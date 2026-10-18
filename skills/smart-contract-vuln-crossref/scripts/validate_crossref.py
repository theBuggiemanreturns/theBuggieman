#!/usr/bin/env python3
"""Validate the cross-reference handoff and its 20-category coverage table."""

import re
import sys
from pathlib import Path

VALID_STATUSES = {"CROSSREF_COMPLETE", "CROSSREF_WITH_LIMITATIONS", "BLOCKED"}
VALID_CATEGORY_STATUSES = {"applicable", "not applicable", "blocked"}
REQUIRED_HEADINGS = [
    "Input provenance",
    "Category coverage",
    "Audit candidate cross-reference",
    "Positive controls",
    "Cross-reference-origin candidates and loopback",
    "Corpus gaps and no-close-precedent items",
    "Limitations and residual uncertainty",
]
PLACEHOLDERS = re.compile(
    r"\[(?:Protocol|value|CROSSREF_COMPLETE[^\]]*)\]", re.IGNORECASE
)


def section_body(text: str, heading: str) -> str:
    match = re.search(
        rf"^##\s+\d+\.\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+\d+\.|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""

def table_rows(body: str):
    rows = []
    header_seen = False
    for line in body.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        if re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", stripped):
            continue
        cells = [cell.strip() for cell in stripped[1:-1].split("|")]
        if not header_seen:
            header_seen = True
            continue
        rows.append(cells)
    return rows


def complete_row_count(body: str, width: int) -> int:
    return sum(
        1
        for row in table_rows(body)
        if len(row) >= width and all(row[:width])
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_crossref.py <cross-reference.md>")
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"FAIL: cross-reference file not found: {path}")
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    failures = []

    match = re.search(
        r"^\*\*Cross-reference status:\*\*\s*([A-Z_]+)\s*$",
        text,
        re.MULTILINE,
    )
    status = match.group(1) if match else ""
    if status not in VALID_STATUSES:
        failures.append("missing or invalid Cross-reference status")

    for heading in REQUIRED_HEADINGS:
        if not section_body(text, heading):
            failures.append(f"missing or empty section: {heading}")

    if PLACEHOLDERS.search(text):
        failures.append("template placeholders remain")

    evidence_requirements = [
        ("Input provenance", 2, 6, False),
        ("Audit candidate cross-reference", 8, 1, False),
        ("Positive controls", 5, 1, True),
        ("Cross-reference-origin candidates and loopback", 6, 1, True),
        ("Corpus gaps and no-close-precedent items", 4, 1, True),
    ]
    for heading, width, minimum, allow_none in evidence_requirements:
        body = section_body(text, heading)
        complete = complete_row_count(body, width)
        explicit_none = bool(
            re.search(r"^None\b[^\n]*[—-]\s*\S+", body, re.MULTILINE | re.IGNORECASE)
        )
        if complete < minimum and not (allow_none and explicit_none):
            suffix = " or an explicit 'None — evidence' statement" if allow_none else ""
            failures.append(
                f"{heading} requires {minimum} complete evidence row(s){suffix}"
            )

    category_body = section_body(text, "Category coverage")
    found_values = [
        int(value)
        for value in re.findall(r"\|\s*CAT-(\d{2})\s*\|", category_body)
    ]
    found = set(found_values)
    if len(found_values) != len(found):
        failures.append("duplicate category rows are not allowed")
    expected = set(range(1, 21))
    if found != expected:
        missing = ", ".join(f"CAT-{value:02d}" for value in sorted(expected - found))
        extra = ", ".join(f"CAT-{value:02d}" for value in sorted(found - expected))
        if missing:
            failures.append(f"missing category rows: {missing}")
        if extra:
            failures.append(f"unexpected category rows: {extra}")

    for line in category_body.splitlines():
        if not re.match(r"^\|\s*CAT-\d{2}\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) < 7:
            category = cells[1] if len(cells) > 1 else "unknown category"
            failures.append(f"{category} has a malformed category row")
            continue
        category = cells[1]
        category_status = cells[3].lower()
        map_evidence = cells[4]
        result = cells[5]
        if category_status not in VALID_CATEGORY_STATUSES:
            failures.append(f"{category} has invalid/empty category status")
        if not map_evidence:
            failures.append(f"{category} is missing map/route evidence")
        if not result:
            failures.append(f"{category} is missing checklist result or hypothesis link")

    if status == "CROSSREF_COMPLETE":
        blocked_rows = re.findall(
            r"^\|\s*CAT-\d{2}\s*\|[^\n]*\|\s*blocked\s*\|",
            category_body,
            re.MULTILINE | re.IGNORECASE,
        )
        if blocked_rows:
            failures.append("CROSSREF_COMPLETE contains blocked category rows")

    limitations = section_body(text, "Limitations and residual uncertainty")
    if status == "CROSSREF_WITH_LIMITATIONS" and not re.search(
        r"\b(blocked|missing|unavailable|unresolved|limitation)\b",
        limitations,
        re.IGNORECASE,
    ):
        failures.append("CROSSREF_WITH_LIMITATIONS does not state a limitation")

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1

    print(f"PASS: structurally valid cross-reference ({status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
