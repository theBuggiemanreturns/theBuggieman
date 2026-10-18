---
name: smart-contract-auditing
description: Systematically audit a previously mapped smart-contract protocol for authorization, accounting, lifecycle, math, external-call, economic, integration, token, signature, upgrade, cross-chain, denial-of-service, and configuration vulnerabilities. Use after contract-mapping has produced protocol-map.md, or for an explicitly bounded remediation/diff review with equivalent mapping evidence; also use its optional wrappers when selecting an authorized whitehat target or privately disclosing an already-proven bounty finding. Validate the map, route only applicable references, use mechanical checks only to seed hypotheses, maintain coverage/hypothesis/test ledgers, prove and try to disprove every candidate, quantify impact, hand independent results to smart-contract-vuln-crossref, and produce reproducible reports.
---

# Smart Contract Auditing

Audit behavior using the mapper's evidence. Do not rebuild the protocol from
memory, treat scanner output as a finding, or load historical cases before the
independent hypothesis pass.

For a requested whitehat target-selection decision before mapping, read
`references/target-selection-triage.md`, verify an authorized disclosure path,
and stop at a triage decision. Do not call triage an audit.

## Required input

Require:

1. `protocol-map.md` produced by `contract-mapping`;
2. the exact source, commit, deployment, and evidence paths named by the map.

Run the preflight:

```bash
python3 scripts/validate_audit_input.py path/to/protocol-map.md
```

- Refuse a complete-audit claim when status is `BLOCKED`.
- With `READY_WITH_LIMITATIONS`, propagate each limitation into affected coverage
  rows, hypotheses, findings, and the final summary.
- If source tracing contradicts the map, return the discrepancy to mapping and
  rerun affected passes after correction.

For an intentionally narrow diff/remediation review, record the bounded scope and
the pre-existing architecture evidence that substitutes for a fresh full map.

## Initialize outputs

```bash
python3 scripts/init_audit_workspace.py \
  path/to/protocol-map.md path/to/engagement/audit
```

Maintain these throughout the audit:

- `coverage.md`: every required pass, component, invariant, reviewer/result;
- `hypotheses.md`: open, testing, confirmed, disproved, duplicate, accepted risk;
- `tests.md`: commands, commits/blocks, assertions, and results;
- `findings/`: one self-contained report per confirmed issue;
- `audit-summary.md`: scope, evidence, findings, limitations, residual risk.

## Workflow

### 1. Confirm the map against source

Read the map first, then verify its load-bearing facts while tracing source:
entry points, roles, proxy/clone implementations, state writers, value flows,
external calls, lifecycle, and invariants. Do not spend the audit reconstructing
already-mapped facts unless evidence is inconsistent.

### 2. Build the coverage matrix

Read `references/core-review-passes.md` completely. Add all twelve passes to
`coverage.md` and mark each `required`, `not applicable` with reason, or `blocked`
with the exact missing evidence. Review each pass across the entire call graph,
not one contract at a time.

Read `references/protocol-routes.md` and load only the applicable protocol routes.
For example, a vault should not consume validator-consensus guidance; a launchpad
should not skip AMM migration, token, MEV, and lifecycle routes.

For Solana programs, Token-2022, Rust consensus, or validator code, read
`references/non-evm-and-consensus.md`. Do not claim the EVM `contract-info` and
Solidity gap finder cover those platforms.

### 3. Trace invariants and sibling paths

For every map invariant, identify all writers, readers, entry points, early
returns, failure/recovery paths, and external callbacks. Compare sibling families:

- deposit/mint and withdraw/redeem;
- create/update/cancel and request/finalize/cancel;
- vote/poke/reset and claim/harvest/emergency;
- pause/unpause/recovery and upgrade/migrate/rollback.

The most valuable questions are often: which two values must change together,
which path updates only one, and what external state does the code assume rather
than verify?

### 4. Generate hypotheses independently

Use source reasoning, static analysis, fuzz/invariant failures, diffs, and deployed
read-only state to create hypotheses. Read
`references/mechanical-discovery-checks.md` and run only applicable grouped
checks. Each hit is a hypothesis seed, never coverage or a finding.

Each hypothesis must name:

- affected entry points and code locations;
- broken invariant;
- attacker prerequisites and controllable inputs;
- full call/state sequence;
- expected impact and preliminary bound;
- strongest known defense or kill test.

Do not consult `historical-corpus/` or vulnerability-pattern references in this
phase. The cross-reference stage consumes the independently generated map,
coverage, candidates, and findings only after this pass is stable.

### 5. Verify reachability and preconditions

Trace modifiers, internal calls, inherited behavior, lifecycle, configuration,
token/oracle behavior, and real deployed state. Use only read-only live-chain
calls. Record disproved candidates with the exact guard or economic constraint;
do not delete them from the ledger.

### 6. Prove surviving candidates

Read `references/proof-triage-report.md`. Choose the smallest faithful proof:

- unit test for local logic;
- fuzz test for input boundaries;
- stateful invariant test for accounting/lifecycle;
- differential test for formulas or modified upstream code;
- pinned local fork for deployed configuration and integrations.

Quantify attacker cost/profit, victim/protocol loss, assets frozen, scope,
repeatability, and maximum bound. For non-economic safety/liveness findings,
demonstrate the exact violated property under the allowed fault model.

### 7. Try to kill every finding

Before confirmation, attempt to refute it using authorization, reachability,
phase/order, upstream guards, source/deployment mismatch, liquidity/capital,
profitability, sequencer/MEV assumptions, known scope exclusions, and duplicate or
accepted-risk status. Distinguish owner power from a permissionless exploit.

A passing call is not an impact proof. A scanner warning is not reachability.
Similarity to a historical bug is not proof.

### 8. Report, fix, and retest

Use the report schema in `references/proof-triage-report.md`. Align severity to the
engagement's rubric, state the bound, and provide concrete remediation plus risks
introduced by the fix. Add a regression test that fails before and passes after
the patch. Rerun affected passes and the full suite.

For a readiness review, also verify exact deployment/initialization ordering,
roles, multisig/timelock, oracles, caps, fees, source/bytecode, monitoring, and
incident controls before a commit/configuration-specific go/no-go decision.

### 9. Cross-reference and loop back

After independent hypotheses are resolved, invoke `smart-contract-vuln-crossref`
with `protocol-map.md`, `coverage.md`, `hypotheses.md`, `tests.md`, and the
draft findings. Require its category coverage and candidate-to-pattern ledger.

Any new candidate found by the map-driven completeness pass returns to steps 5–8
and must receive reachability, proof, kill-test, impact, and severity analysis.
Historical similarity never confirms a bug or determines severity. Update
`audit-summary.md` only after all cross-reference-origin candidates are resolved.

For a confirmed whitehat bounty finding, read
`references/disclosure-and-submission-wrapper.md` only when the user asks to
prepare the private submission. Paid client reports keep their contractual format.

## Completion gate

Do not call an audit complete until:

1. every in-scope component and map invariant has coverage;
2. all twelve core passes have a result or justified non-applicability;
3. applicable protocol routes are complete;
4. every hypothesis is resolved or explicitly open/blocked;
5. confirmed findings have reproducible tests and bounded impact;
6. limitations and residual risks are stated;
7. fixes, when in scope, have regression/retest evidence;
8. cross-reference coverage is complete and every new candidate has looped through
   the independent proof/kill workflow;
9. any bounty disclosure uses the authorized private channel and remains
   unconditional on payment.

This pipeline reduces missed work; it does not prove a protocol is safe.
