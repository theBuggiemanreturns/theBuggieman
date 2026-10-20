# Evals

Known-answer targets. A run passes only if the agent reaches the asserted witness
and the finding matches `EXPECTED.md`. Measures changes to the skill instead of
guessing. Grief is not EXTRACT; a theoretical state violation is not a pass.

- `chain-overflow-invariant/` — a deliberately broken vault whose *only* critical
  is a chain of two individually-low primitives (an aggregate overflow + an
  overflowing supply guard). Tests the primitives ledger, the guard-audit pass,
  and the composition phase together. Modeled on the XRPL infinite-mint shape.
