# Contract Audit Pipeline — v2

v2 keeps v1's four skills (`onchain-recon → contract-mapping → smart-contract-auditing → smart-contract-vuln-crossref`) and wraps them in an **orchestrator** that gives the agent ways to *think*, not a checklist to tick.

## What changed from v1
- **Two modes.** `hunt` (time-boxed, depth-first, extract-only, Ragnarok-style) and `audit` (v1's full coverage gates, for paid client work). Same skills, different completion bar.
- **Non-negotiables vs defaults.** A short list of hard rules the agent may never break, separated from soft defaults it may skip *if it writes down why*. v1 made everything read as MUST.
- **Generator questions lead.** The audit stage starts from open adversarial questions; the 12 passes become a late completeness sweep.
- **Thin map first.** Component graph + one trace, then invent; the map grows only when a hypothesis names a missing node. The map never shrinks.
- **Primitives ledger.** Every sub-critical observation is recorded as a reusable primitive (what it influences, its precondition, its post-state), not thrown away.
- **Guard-audit pass.** Every invariant, cap, require, and safety check is itself a target.
- **Chaining composition phase.** A dedicated pass that pairs primitives into chains and re-scores severity on the end state. low + low can be critical.
- **Evidence ladder + CLASS.** SOURCE → DEPLOYMENT → RUNTIME → ECONOMICALLY verified; findings tagged EXTRACT / GRIEF / PRIVILEGED against the program's own rubric.
- **Evals.** Known-answer targets so every change to the skill is measured, not guessed.
- **Tracker hook.** CONFIRMED findings open an issue in the bug-hunting repo.

## Files
```
v2/
  ORCHESTRATOR.md                  top-level skill: modes, hard rules, the loop
  passes/guard-audit.md            treat every guard as an attack surface
  phases/composition-chaining.md   build chains from the primitives ledger
  templates/primitives.md          the primitives ledger template
  templates/chain-card.md          a chain finding as a first-class artifact
  knowledge/known-chains.md        chain corpus, seeded with the XRPL infinite mint
  evals/                           known-answer targets, incl. a chaining eval
  scripts/                         helpers (ledger + chain gates)
```

## Run it
```
run the audit pipeline in hunt mode on <target-dir>
run the audit pipeline in audit mode on <target-dir>
```
Start at ORCHESTRATOR.md.
