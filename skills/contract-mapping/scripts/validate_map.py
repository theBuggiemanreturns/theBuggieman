#!/usr/bin/env python3
"""Validate the structural handoff from contract-mapping to auditing."""

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "Identity, authorization, and scope",
    "Source, build, and deployment provenance",
    "Contract inventory and dependency graph",
    "Roles, privileges, and trust boundaries",
    "Callable surface and callbacks",
    "State, accounting, and coupled variables",
    "Assets, liabilities, and value-flow paths",
    "Lifecycle and state machines",
    "External integrations and assumptions",
    "Invariant register",
    "Deployment and live configuration",
    "Unresolved gaps and blind spots",
    "Auditor routing notes",
]

VALID_STATUSES = {"READY_FOR_AUDIT", "READY_WITH_LIMITATIONS", "BLOCKED"}
REQUIRED_CONTROL_MARKERS = {
    "Code provenance",
    "Operational controller",
    "Control overlap",
    "Scope verdict",
}
PLACEHOLDERS = re.compile(
    r"\[(?:required|value|Protocol|repository/address/bundle paths|READY_FOR_AUDIT[^\]]*)\]",
    re.I,
)

TABLE_REQUIREMENTS = {
    "Identity, authorization, and scope": ((0, 1), 6),
    "Source, build, and deployment provenance": ((0, 1, 3, 4, 5), 1),
    "Contract inventory and dependency graph": ((0, 1, 2, 5, 6, 7, 8, 9), 1),
    "Roles, privileges, and trust boundaries": ((0, 1, 2, 3, 4, 5), 1),
    "Callable surface and callbacks": (tuple(range(8)), 1),
    "State, accounting, and coupled variables": (tuple(range(7)), 1),
    "Assets, liabilities, and value-flow paths": (tuple(range(6)), 1),
    "Lifecycle and state machines": (tuple(range(7)), 1),
    "External integrations and assumptions": (tuple(range(8)), 1),
    "Invariant register": (tuple(range(5)), 1),
    "Deployment and live configuration": (tuple(range(5)), 1),
    "Unresolved gaps and blind spots": (tuple(range(5)), 1),
    "Auditor routing notes": (tuple(range(3)), 1),
}


def section_body(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+\d+\.\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+\d+\.|\Z)",
        re.M | re.S,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def table_data_rows(body: str) -> str:
    rows = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", stripped):
            continue
        if not rows:
            rows.append("__HEADER__")
            continue
        rows.append(stripped)
    return "\n".join(row for row in rows if row != "__HEADER__")

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="Path to protocol-map.md")
    args = parser.parse_args()
    path = Path(args.map)

    if not path.is_file():
        print(f"FAIL: map not found: {path}")
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    failures = []
    warnings = []

    status_match = re.search(r"^\*\*Mapping status:\*\*\s*([A-Z_]+)\s*$", text, re.M)
    status = status_match.group(1) if status_match else None
    if status not in VALID_STATUSES:
        failures.append("missing or invalid Mapping status")

    for heading in REQUIRED_HEADINGS:
        body = section_body(text, heading)
        if not body:
            failures.append(f"missing or empty section: {heading}")

    for heading, (required_columns, min_rows) in TABLE_REQUIREMENTS.items():
        rows = table_rows(section_body(text, heading))
        complete = [
            row for row in rows
            if all(index < len(row) and row[index] for index in required_columns)
        ]
        if len(complete) < min_rows:
            failures.append(
                f"{heading} requires at least {min_rows} complete evidence row(s)"

            )
    if PLACEHOLDERS.search(text):
        failures.append("template placeholders remain")

    for marker in sorted(REQUIRED_CONTROL_MARKERS):
        if marker.lower() not in text.lower():
            failures.append(f"missing provenance/control schema marker: {marker}")

    unresolved = table_data_rows(
        section_body(text, "Unresolved gaps and blind spots")
    )
    if status == "READY_FOR_AUDIT" and re.search(
        r"\b(unresolved|unknown|missing|unverified|blocked|tbd)\b",
        unresolved,
        re.I,
    ):
        warnings.append(
            "READY_FOR_AUDIT map contains possible unresolved data rows; review section 12"
        )
    if status == "READY_WITH_LIMITATIONS" and not re.search(
        r"\b(limitation|unresolved|unknown|missing|unverified)\b",
        unresolved,
        re.I,
    ):
        failures.append(
            "READY_WITH_LIMITATIONS does not describe a limitation in section 12"
        )

    for message in warnings:
        print(f"WARN: {message}")
    for message in failures:
        print(f"FAIL: {message}")

    if failures:
        return 1

    print(f"PASS: structurally valid protocol map ({status})")
    if status == "BLOCKED":
        print("HANDOFF: mapping is valid but auditing must not claim complete coverage")
    else:
        print("HANDOFF: map may enter smart-contract-auditing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
