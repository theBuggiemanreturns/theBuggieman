# Phase: Composition & Chaining

A chain turns sub-critical primitives into a critical finding. The XRPL mint was
`low (aggregate-charge overflow) + low (invariant-accumulator overflow)` → infinite
mint, because both accumulators were the same signed int64 and wrapped by the same
2^64. Neither alone was reportable; together they were the largest whitehat bug on
record.

Run this phase after independent hypotheses are stable, over the full
`research/primitives.md` ledger — including every Low/Info/GUARD row.

## 1. Normalize primitives

Each primitive in the ledger has: what it **influences**, its **precondition**,
its **post-state**, and the **mechanism** it relies on (type, counter, oracle,
rounding mode, assumption). Make these explicit — chains are matched on them.

## 2. Pair systematically

For every ordered pair (A, B) of primitives, ask:
- **Precondition unlock:** does A's post-state satisfy B's precondition?
- **Guard disable:** does A break, bypass, or disable the guard that would catch B? *(primitive + its own guard is the first pair to try — always.)*
- **Shared mechanism:** do A and B depend on the *same* flawed thing (same int type, same accumulator, same oracle, same rounding)? Breaking it once breaks both.
- **Representation divergence:** can A make two components disagree about one fact, so B redeems against the stale one?
- **Entitlement/payment split:** does A grant a right or credit that B redeems in a different state?

Record every plausible pair as a candidate chain even if one link is Low.

## 3. Re-score on the end state

A chain's severity = the impact of its final state, scored on the program's
rubric — not the max of the links. Re-run the evidence ladder and CLASS on the
chain as a whole.

## 4. Prove the whole chain on one fork

A chain is CONFIRMED only when a single PoC executes A then B (then C…) and
reaches the asserted impossible end state, with extract economics and a kill
attempt. One harness, the full sequence. (XRPL: 256 offers → BookStep overflow →
XRPNotCreated overflow → committed mint, in one transaction.)

## 5. Reopen on map growth

When the map grows, re-run pairing: a new node may be the missing link between two
primitives you had already shelved. Killed chains carry a `Revisit if` trigger.

## The chaining checklist (bake into every hunt)
1. Keep a primitives ledger, not just a findings list. Never discard a Low.
2. Audit the guard as a target (`passes/guard-audit.md`).
3. Look for a shared flawed mechanism between a primitive and its guard.
4. Pair primitives: precondition-unlock, guard-disable, shared-mechanism, representation-divergence, entitlement/payment-split.
5. Severity is emergent — score the end state.
6. Prove the whole chain on one fork.
