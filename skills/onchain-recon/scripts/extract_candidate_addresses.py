#!/usr/bin/env python3
"""
extract_candidate_addresses.py — Given raw hex (calldata from `cast tx <hash>
--json`'s "input" field, or a decoded parameter blob), pull out every 32-byte
word that LOOKS like an address (top 12 bytes zero, meaningful data in the
low 20 bytes) without needing to know the function's ABI first.

Why this exists: addresses passed as function/constructor arguments are
always ABI-encoded as a 32-byte word with 12 leading zero bytes. You can spot
them mechanically before you've decoded anything, which is exactly the kind
of legwork that shouldn't cost an LLM a reasoning step or a human an approval
click per candidate.

This is a HEURISTIC SHORTLIST, not a decode. It will occasionally flag a
non-address (a huge uint) or miss an address embedded in a dynamic/nested
struct your calldata slicing didn't align on a 32-byte boundary. Always
verify each candidate with `cast code <addr>` before trusting it — this
script's job is to hand you a short list to check, not a final answer.

Usage:
    python3 extract_candidate_addresses.py <hex-string> [--skip-selector]
    python3 extract_candidate_addresses.py --file calldata.txt

    --skip-selector   drop the leading 4-byte function selector before
                       splitting into 32-byte words (use this for top-level
                       calldata; omit it for an already-unwrapped param blob)
"""
import sys
import argparse
import json
import re

MIN_NONZERO_TAIL_BYTES = 4  # heuristic threshold, see module docstring


def clean_hex(s: str) -> str:
    s = s.strip()
    if s.lower().startswith("0x"):
        s = s[2:]
    data = "".join(s.split())  # drop any stray whitespace/newlines
    if not re.fullmatch(r"[0-9a-fA-F]*", data):
        raise ValueError("input contains non-hex characters")
    return data.lower()


def find_candidates(hex_str: str, skip_selector: bool):
    data = clean_hex(hex_str)
    if skip_selector:
        if len(data) < 8:
            raise ValueError("cannot skip selector: input is shorter than 4 bytes")
        data = data[8:]  # drop 4-byte / 8-hex-char selector

    words = [data[i:i + 64] for i in range(0, len(data), 64)]
    candidates = []
    for idx, word in enumerate(words):
        if len(word) != 64:
            continue  # trailing partial word, not a clean 32-byte slot
        top12 = word[:24]
        tail20 = word[24:]
        if top12 != "0" * 24:
            continue
        nonzero_tail_bytes = sum(
            1 for i in range(0, 40, 2) if tail20[i:i + 2] != "00"
        )
        if nonzero_tail_bytes >= MIN_NONZERO_TAIL_BYTES:
            candidates.append({
                "word_index": idx,
                "address_candidate": "0x" + tail20,
                "nonzero_tail_bytes": nonzero_tail_bytes,
            })
    return candidates


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("hex", nargs="?", help="Raw hex calldata/blob")
    ap.add_argument("--file", help="Read hex from a file instead")
    ap.add_argument("--skip-selector", action="store_true",
                     help="Drop the leading 4-byte function selector first")
    ap.add_argument("--json", action="store_true",
                     help="Emit a JSON array for downstream scripts")
    args = ap.parse_args()

    if args.file:
        with open(args.file) as f:
            hex_str = f.read()
    elif args.hex:
        hex_str = args.hex
    else:
        ap.error("Provide hex as an argument or via --file")

    try:
        candidates = find_candidates(hex_str, args.skip_selector)
    except ValueError as exc:
        ap.error(str(exc))

    if args.json:
        print(json.dumps(candidates, indent=2))
        return

    if not candidates:
        print("No address-shaped words found.")
        return

    print(f"{len(candidates)} candidate address(es) — verify each with `cast code <addr>`:\n")
    for c in candidates:
        print(f"  word #{c['word_index']:<3} {c['address_candidate']}  "
              f"({c['nonzero_tail_bytes']}/20 tail bytes nonzero)")


if __name__ == "__main__":
    main()
