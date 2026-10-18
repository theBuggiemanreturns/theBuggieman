# Proof, triage, and reporting standard

## Hypothesis record

```text
ID:
STATUS: open | testing | confirmed | disproved | duplicate | accepted-risk | blocked
SOURCE PASS / ROUTE:
AFFECTED CODE AND ENTRY POINTS:
BROKEN INVARIANT:
ATTACKER PREREQUISITES:
FULL CALL AND STATE PATH:
EXPECTED IMPACT / BOUND:
STRONGEST DEFENSE OR KILL TEST:
EVIDENCE / TEST:
RESOLUTION:
```

## Proof selection

- Use a unit test for isolated deterministic behavior.
- Use fuzzing for boundary and input interactions.
- Use stateful invariants for accounting, solvency, supply, permissions, and
  lifecycle sequences.
- Use differential tests for formulas, solvers, curves, or fork modifications.
- Use a local fork pinned to an exact block for deployed integrations/configuration.
- Prefer exact real source and addresses. Use a reduced harness only when it
  faithfully reproduces load-bearing logic and live magnitudes are separately
  evidenced.

Every proof must name source commit/compiler, chain and block when applicable,
one reproduction command, assertions, and actual result. Demonstrate attacker net
gain or victim/protocol loss after costs, assets frozen, violated authorization,
or the exact non-economic safety/liveness property.

## Adversarial quality gate

Try to refute every candidate:

1. Is the external trigger reachable by the claimed actor?
2. Which modifier, upstream validation, or sibling state update could stop it?
3. Does deployed configuration match the tested path?
4. Is it owner/role power by design rather than permissionless exploitation?
5. Are required capital, liquidity, ordering, timing, and victim actions realistic?
6. Does profit remain after fees and price impact? Is griefing economically repeatable?
7. Is impact permanent, recoverable, bounded, or only theoretical?
8. Is it excluded, documented, accepted, previously audited, or already known?
9. Does the proposed fix close alternate paths, and what new DoS/accounting/privilege
   risk does it introduce?

## Severity

Use the engagement's published rubric where available. Otherwise rate impact and
likelihood conservatively:

- Critical: permissionless systemic theft/loss/freeze or equivalent safety failure;
- High: serious unauthenticated loss or control with a material stated bound or
  common condition;
- Medium: conditional/limited loss, repeatable griefing, or material availability;
- Low: minor edge case or low-impact correctness/security weakness;
- Informational/trust: hardening, operational risk, or intended privileged power.

Never derive severity from a historical label. State authorization, capital,
frequency, victims, recoverability, and maximum magnitude.

## Finding report

```markdown
# [ID] [Severity] — [root cause and consequence]

**Scope:** [commit, files/addresses, chain/block]
**Status:** [proof type and result]

## Summary
[One wrong assumption, broken invariant, and consequence in plain language.]

## Affected components
| Component | File:line / address | Role |
|---|---|---|

## Root cause
[Exact code and mechanical explanation.]

## Preconditions and reachability
1. [Condition, actor control, and evidence.]

## Attack or failure sequence
1. [Complete ordered path.]

## Impact and bound
[Authorization, capital, frequency, victims, recoverability, magnitude.]

## Proof
`[one command]`

[Assertions and actual output.]

## Recommended remediation
1. [Root-cause fix.]
2. [Alternate-path/defense-in-depth fix.]
3. [Second-order risk and test.]

## Limitations and assumptions
[Relevant map/audit limitations.]

## Fix and retest
[Patch commit, regression, full-suite result when available.]
```

For bounty disclosure, add private-channel and compensation language only when
requested. Do not hard-code a researcher identity into the auditing skill.

## Completion artifacts

- Coverage links every in-scope component and invariant to passes and tests.
- Disproved candidates remain in the hypothesis ledger with reasons.
- Tests record commands and results, not just intended PoCs.
- The summary states unresolved items and residual risk.
- A readiness decision is explicitly tied to the reviewed commit/configuration.
