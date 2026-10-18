#!/usr/bin/env python3
"""
find_gaps.py — Given a directory of .sol files, a single .sol file, or a
markdown dump containing fenced ```solidity/```sol code blocks, figure out
what contracts/interfaces/libraries are REFERENCED (via import or
inheritance) but not DEFINED anywhere in the provided source.

The point: resolve this gap BEFORE handing source to an audit model, so the
model spends its time analyzing, not discovering. If you're pasting a .md
bundle assembled from docs, this is what tells you what docs left out.

Usage:
    python3 find_gaps.py <path-to-folder-or-.md-or-.sol> [--json]

Output:
    - Every contract/interface/library actually defined in what you gave it
    - Unresolved imports (import target not present in the bundle)
    - Unresolved inheritance (parent contract/interface never defined)
    - The above two, deduped and split into:
        * third_party_likely   -> OpenZeppelin/Solmate/etc; resolve the exact
                                   version/commit; do not treat it as project-owned
        * project_specific     -> NOT provided, go fetch this before
                                   mapping continues (this is almost always
                                   where the docs undercounted)
"""
import re
import sys
import json
import argparse
from pathlib import Path

STDLIB_HINTS = [
    "openzeppelin", "solmate", "solady", "forge-std", "ds-test",
    "@uniswap", "uniswap", "erc20", "erc721", "erc1155", "ierc20",
    "ierc721", "ierc4626", "safeerc20", "reentrancyguard", "ownable",
    "pausable", "accesscontrol", "initializable", "uupsupgradeable",
    "proxyadmin", "clones", "math.sol", "safecast", "address.sol",
    "context.sol", "multicall.sol",
]

# Cover every Solidity import form:
#   import "path";
#   import "path" as Alias;
#   import * as Alias from "path";
#   import {A, B as C} from "path";
# Keeping the expression semicolon-bounded prevents a malformed import from
# consuming a later statement while still allowing multiline symbol lists.
IMPORT_RE = re.compile(
    r'\bimport\s+(?:[^;]*?\s+from\s+)?["\']([^"\']+)["\']'
    r'(?:\s+as\s+\w+)?\s*;',
    re.MULTILINE,
)
CONTRACT_DEF_RE = re.compile(
    r'\b(?:abstract\s+)?(contract|interface|library)\s+(\w+)'
    r'(?:\s+is\s+([^\{]+))?\s*\{',
    re.MULTILINE,
)
FENCE_RE = re.compile(r'```(?:solidity|sol)\s*\n(.*?)```', re.DOTALL | re.IGNORECASE)
FILENAME_HINT_RE = re.compile(
    r'(?:^|\n)\s*(?:#{1,6}\s*|//\s*File:\s*|///\s*)([A-Za-z0-9_/\.\-]+\.sol)\b'
)


def extract_sol_units_from_md(md_text):
    """Pull fenced solidity blocks out of a markdown dump, trying to recover
    a filename from a preceding header/comment (### Foo.sol or // File: Foo.sol)."""
    units = []
    last_end = 0
    for i, m in enumerate(FENCE_RE.finditer(md_text)):
        preceding = md_text[last_end:m.start()]
        name_matches = FILENAME_HINT_RE.findall(preceding)
        fname = name_matches[-1] if name_matches else f"unnamed_block_{i}.sol"
        units.append((fname, m.group(1)))
        last_end = m.end()
    return units


def load_source_units(path: Path):
    units = []
    if path.is_file() and path.suffix.lower() == ".md":
        units = extract_sol_units_from_md(path.read_text(errors="ignore"))
    elif path.is_file() and path.suffix.lower() == ".sol":
        units = [(path.name, path.read_text(errors="ignore"))]
    elif path.is_dir():
        for f in sorted(path.rglob("*.sol")):
            units.append((str(f.relative_to(path)), f.read_text(errors="ignore")))
        for f in sorted(path.rglob("*.md")):
            units.extend(extract_sol_units_from_md(f.read_text(errors="ignore")))
    else:
        raise SystemExit(f"Don't know how to read: {path}")
    return units


def strip_comments(src):
    src = re.sub(r'//.*', '', src)
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
    return src


def analyze(units):
    defined = {}              # symbol name -> filename that defines it
    imports_by_file = {}      # filename -> [raw import targets]
    inherits_by_symbol = {}   # symbol -> [parent names]

    for fname, src in units:
        clean = strip_comments(src)
        imports_by_file[fname] = IMPORT_RE.findall(clean)
        for kind, name, parents in CONTRACT_DEF_RE.findall(clean):
            defined[name] = fname
            if parents:
                parent_names = [p.strip().split('(')[0].strip() for p in parents.split(',')]
                inherits_by_symbol[name] = [p for p in parent_names if p]

    defined_names = set(defined.keys())
    provided_basenames = {Path(f).name for f, _ in units}

    unresolved_imports = {}
    for fname, targets in imports_by_file.items():
        missing = [t for t in targets if Path(t).name not in provided_basenames]
        if missing:
            unresolved_imports[fname] = missing

    unresolved_parents = {}
    for symbol, parents in inherits_by_symbol.items():
        missing = [p for p in parents if p not in defined_names]
        if missing:
            unresolved_parents[symbol] = missing

    def classify(name_or_path):
        low = name_or_path.lower()
        return "stdlib_likely" if any(h in low for h in STDLIB_HINTS) else "project_specific"

    gaps = {"stdlib_likely": set(), "project_specific": set()}
    for missing in unresolved_imports.values():
        for m in missing:
            gaps[classify(m)].add(m)
    for missing in unresolved_parents.values():
        for m in missing:
            gaps[classify(m)].add(m)

    return {
        "source_units_parsed": len(units),
        "defined_symbols": defined,
        "unresolved_imports_by_file": unresolved_imports,
        "unresolved_inheritance_by_symbol": unresolved_parents,
        "gaps_third_party_likely_NEEDS_VERSION_PIN": sorted(gaps["stdlib_likely"]),
        "gaps_project_specific_NEEDS_FETCHING": sorted(gaps["project_specific"]),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="Folder of .sol files, a single .sol/.md file")
    ap.add_argument("--json", action="store_true", help="Machine-readable output")
    args = ap.parse_args()

    path = Path(args.path)
    units = load_source_units(path)
    if not units:
        print("No Solidity source found (no fenced ```solidity blocks, no .sol files).")
        sys.exit(1)

    result = analyze(units)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Parsed {result['source_units_parsed']} source unit(s).\n")

    print(f"Defined contracts/interfaces/libraries ({len(result['defined_symbols'])}):")
    for name, fname in sorted(result['defined_symbols'].items()):
        print(f"  {name:<30} <- {fname}")

    gaps = result['gaps_project_specific_NEEDS_FETCHING']
    print(f"\nProject-specific gaps — GO FETCH THESE before mapping continues ({len(gaps)}):")
    for g in gaps:
        print(f"  \u26a0 {g}")

    stdlib = result['gaps_third_party_likely_NEEDS_VERSION_PIN']
    print(f"\nLikely third-party libraries — pin exact version/commit ({len(stdlib)}):")
    for g in stdlib:
        print(f"  \u00b7 {g}")

    if not gaps:
        print("\n\u2705 No unresolved project-specific dependencies — source set looks complete.")
    else:
        print(f"\n\u274c {len(gaps)} gap(s) — resolve these before the audit model starts, not during it.")


if __name__ == "__main__":
    main()
