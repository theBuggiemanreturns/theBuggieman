# Known Chains (corpus family)

Chains fuel chains. Each entry is a *generator*, not a signature to match. The
question stays: does this target have a primitive + guard that share a flawed
mechanism? — not "is this the XRPL bug?"

## CHAIN-K001 — Overflow primitive + overflowing invariant (XRPL infinite mint, 2026)
- **Target:** rippled (XRP Ledger payment engine). ~$94B at risk, $250K bounty.
- **Link A (Low):** `BookStep::sum()` aggregates offer inputs into a signed int64 (`savedIns`). A strand of offers whose combined XRP input crosses 2^64 wraps the *aggregate charge* down to a tiny value — but each offer owner is still paid its full, unwrapped amount in `consumeOffer`.
- **Link B (Low / unreachable alone):** the `XRPNotCreated` invariant, meant to reject any tx that creates XRP, accumulates net balance change in a signed int64 (`drops_`). A true gain of ~2^64 wraps back to `-fee`, so the guard reads a normal fee burn and passes.
- **Why it chains — shared mechanism:** both accumulators are signed int64 and wrap by the same 2^64. Choose credits so the total lands on a multiple of 2^64 and *both* wrap together: the charge is tiny, the guard is blind.
- **Construction:** 256 offers of 257 drops → 256·257 = 2^64 + 256; the +1 per offer keeps the total off an exact 2^64 (which would wrap to 0) so it wraps to a usable 256. Per-account 100B cap forces the gain across 256 accounts; strand limit is 1000 offers.
- **End state:** 2^64 + 256 drops ≈ 18.45 trillion XRP minted in one tx, 184× total supply, spendable across 256 accounts, repeatable.
- **Fix:** `checkedAdd`/`checkedStepAdd` in the payment engine (dry the path on overflow) + widen the invariant accumulator to int128 so a real gain can't wrap.
- **Generator lessons:**
  - Audit the invariant/guard with the same overflow lens as the logic.
  - When a primitive and its guard share a type/counter, one break disables both.
  - Per-item settlement can diverge from an aggregate accumulator — track aggregate-vs-per-item as a representation divergence.
  - A Low you can't report alone may be the only reachable path that makes another Low reachable.

<!-- Add new chains as your own hunts confirm them: overflow+invariant, two-oracles,
auth-split + replay, donation + rounding, pause-disable + drain, etc. -->
