#!/usr/bin/env python3
"""Validate protocol-map.md as an input to smart-contract-auditing."""

import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_audit_input.py <protocol-map.md>")
        return 2

    map_path = Path(sys.argv[1]).resolve()
    mapper_validator = Path(__file__).resolve().parents[2] / "contract-mapping" / "scripts" / "validate_map.py"
    result = subprocess.run([sys.executable, str(mapper_validator), str(map_path)])
    if result.returncode != 0:
        return result.returncode

    text = map_path.read_text(encoding="utf-8", errors="replace")
    status_match = re.search(r"^\*\*Mapping status:\*\*\s*([A-Z_]+)\s*$", text, re.M)
    status = status_match.group(1) if status_match else ""
    if status == "BLOCKED":
        print("REFUSE COMPLETE AUDIT: return material gaps to contract-mapping")
        return 3
    if status == "READY_WITH_LIMITATIONS":
        print("ACCEPT WITH LIMITATIONS: propagate section 12 into coverage and findings")
    else:
        print("ACCEPT: validated map is ready for auditing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
