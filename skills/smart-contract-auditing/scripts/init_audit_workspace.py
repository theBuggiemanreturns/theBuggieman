#!/usr/bin/env python3
"""Create non-overwriting audit ledgers from a validated protocol map."""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="Validated protocol-map.md")
    parser.add_argument("output", help="New audit output directory")
    args = parser.parse_args()

    map_path = Path(args.map).resolve()
    validator = Path(__file__).with_name("validate_audit_input.py")
    result = subprocess.run([sys.executable, str(validator), str(map_path)])
    if result.returncode != 0:
        return result.returncode

    text = map_path.read_text(encoding="utf-8", errors="replace")
    title = re.search(r"^#\s+Protocol Map\s+[—-]\s+(.+)$", text, re.M)
    protocol = title.group(1).strip() if title else map_path.stem
    status = re.search(r"^\*\*Mapping status:\*\*\s*([A-Z_]+)", text, re.M)
    map_status = status.group(1) if status else "UNKNOWN"

    out = Path(args.output).resolve()
    if out.exists():
        print(f"FAIL: refusing to overwrite existing audit workspace: {out}")
        return 4
    out.mkdir(parents=True)
    (out / "findings").mkdir()

    write_new(out / "coverage.md", f"""# Audit Coverage — {protocol}

**Protocol map:** `{map_path}`
**Map status:** {map_status}

| Pass/route | Components and invariants | Status | Evidence/tests | Limitations |
|---|---|---|---|---|
| 1. Authorization and lifecycle | | pending | | |
| 2. Accounting and coupled state | | pending | | |
| 3. Math, units, and boundaries | | pending | | |
| 4. External calls and reentrancy | | pending | | |
| 5. Oracle and economic manipulation | | pending | | |
| 6. AMM, migration, and MEV | | pending | | |
| 7. Vault/lending/staking/token supply | | pending | | |
| 8. Signatures/governance/account abstraction | | pending | | |
| 9. Proxy/clone/upgrade | | pending | | |
| 10. Cross-chain and asynchronous flows | | pending | | |
| 11. Denial of service and liveness | | pending | | |
| 12. Configuration and deployment | | pending | | |
""")
    write_new(out / "hypotheses.md", f"""# Hypothesis Ledger — {protocol}

| ID | Origin | Status | Source pass | Affected code | Broken invariant | Preconditions | Evidence / resolution |
|---|---|---|---|---|---|---|---|
""")
    write_new(out / "tests.md", f"""# Test Ledger — {protocol}

| Test ID | Hypothesis/invariant | Type | Commit/block | Command | Assertion/result |
|---|---|---|---|---|---|
""")
    write_new(out / "audit-summary.md", f"""# Audit Summary — {protocol}

**Protocol map:** `{map_path}`
**Map status:** {map_status}

## Scope and evidence

## Coverage

## Confirmed findings

## Disproved hypotheses and positive controls

## Cross-reference coverage and loopback

## Limitations and residual risk

## Conclusion
""")
    print(f"Created audit workspace: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
