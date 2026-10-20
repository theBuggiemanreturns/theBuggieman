# Primitives Ledger — <target>

Every sub-critical observation goes here, even Low/Info. These are the raw
material for chains. Do not discard a Low because it is not reportable alone.

CLASS legend: INFLUENCE (you can move a value/state), GUARD (a check/invariant/cap),
ORDERING (you can affect sequencing), INFO (a fact worth keeping).

| ID | CLASS | What it influences / protects | Precondition | Post-state | Mechanism (type/counter/oracle/rounding/assumption) | Severity alone | In chains |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| P-001 | INFLUENCE | e.g. aggregate charge in sum() | strand of N offers | charge wraps to small value | savedIns sum, int64 | Low | C-001 |
| P-002 | GUARD | e.g. XRPNotCreated invariant | tx modifies many accounts | net gain wraps to -fee, passes | drops_ accumulator, int64 | Low | C-001 |

## How to add a row
- Give it an ID (P-###).
- CLASS it.
- State what you can **make it do**, not just that it looks odd.
- Name the **mechanism** precisely — this is how the composition pass finds shared-mechanism chains.
- Leave `In chains` blank until the composition pass links it.
