# Contract Audit Pipeline

Agent skills for authorized smart-contract security reviews and bug bounty work.

## Pipeline
1. **onchain-recon** — trace deployments, extract candidate addresses, sweep view functions, check canonical templates.
2. **contract-mapping** — build `protocol-map.md` for the target, validate it, find coverage gaps.
3. **smart-contract-auditing** — systematic review passes over the mapped protocol, hypothesis/test ledgers, fork PoCs, triage and reports.
4. **smart-contract-vuln-crossref** — cross-reference independent findings against a pattern index of known vulnerability classes.

## Layout
```
skills/
  onchain-recon/
  contract-mapping/
  smart-contract-auditing/
  smart-contract-vuln-crossref/
```
Each skill has a `SKILL.md`, `references/`, and `scripts/`.

Only use against targets you are authorized to test.
