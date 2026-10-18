# 02 — Oracle & price-feed manipulation / staleness

## ORC-01 — Instantaneous vault-rate/`convertToAssets()` used directly as price
**Root cause.** A price feed reads a vault's live `convertToAssets()` (or
similar share-rate) instead of a manipulation-resistant source. Donation
attacks (send underlying directly to the vault) move that rate within one
block.
**Detection.** Any `PriceFeed` contract whose `fetchPrice()` calls into an
ERC4626-like `convertToAssets`/`pricePerShare`/`getRate()` on a vault the
attacker can donate to.
**Precedents.** `SDAIPriceFeed` (Critical, Evro Collateral Onboarding) —
used the instantaneous vault rate, exploitable via donation to drain the
protocol. Same report also had `WSTETHPriceFeed` (`ORC-02` below).
Superfluid Yield Backends M-2: Aave's own rounding on deposit/withdraw let
an attacker drain accumulated yield via many small withdrawals — same
family (an internal rate that drifts predictably in the attacker's favor).
**Fix.** Use a manipulation-resistant rate (TWAP-style accumulator,
external oracle, or a rate that only moves via realized yield, not
instantaneous balance).

## ORC-02 — Fallback oracle path returns the wrong denomination/asset
**Root cause.** A multi-path oracle (primary → fallback) switches sources
on failure but the fallback reports a different quote asset (e.g. USD
instead of EUR) without conversion.
**Precedents.** `WSTETHPriceFeed` (High, Evro Collateral Onboarding): on
stETH-USD oracle failure, fell back to a canonical ETH-USD feed and used
it as if it were EUR-denominated, corrupting every downstream price
calculation.
**Detection.** Any oracle with more than one code path to a final price —
check the denomination/decimals of *every* branch, not just the primary.

## ORC-03 — Future/negative timestamp underflows the staleness check
**Root cause.** `block.timestamp - updatedAt` underflows (wraps to a huge
number, or reverts under checked math) if `updatedAt` is in the future,
which some oracle standards explicitly permit within a tolerance window.
**Precedents.** API3 oracle (Medium, Evro Collateral Onboarding and,
separately, INIT Capital M-11): API3 can return timestamps up to one hour
in the future; the staleness check wasn't written to tolerate that,
causing a temporary DoS of the price feed. Ostium had a related family of
timestamp-decoding issues.
**Fix.** Guard with `updatedAt <= block.timestamp` (or an explicit
tolerance) before subtracting.

## ORC-04 — Unbounded gas forwarded to an external oracle call
**Root cause.** A `try/catch` around an oracle call doesn't check
remaining gas in the `catch` branch, so an attacker forwards just enough
gas to make the external call revert (e.g. OOG inside the oracle) while
leaving enough gas for the caller to keep executing — triggering whatever
"oracle failed" fallback path exists, on demand.
**Precedents.** `RedStonePriceFeedBase::getCurrentRedStoneResponse()`
(Medium, Felix Price Feeds) — missing gas-left check in the catch block
let an attacker trigger a temporary protocol shutdown at will.
**Fix.** Explicitly forward a bounded gas stipend to the external call, or
check `gasleft()` in the catch block before treating the failure as
genuine.

## ORC-05 — Cached "last good price" never initialized in the constructor
**Root cause.** A price feed contract that caches `lastGoodPrice` for
fallback use doesn't seed it at deploy time, so it defaults to zero and
the very first oracle failure returns a price of 0 instead of reverting
safely.
**Precedents.** `SDAIPriceFeed` L-1 (Evro Collateral Onboarding).
**Fix.** Call the primary fetch once in the constructor (or require an
explicit seed value) before the feed is trusted.

## ORC-06 — Spot tick/price used where a manipulation-resistant source was intended
**Root cause.** Strategy/vault code reads `slot0()` (the current, single-
block AMM tick) to make a consequential decision — position range,
liquidation threshold, borrow limit — where a TWAP or a "worst-of
spot-and-twap" comparison was the actual intent.
**Precedents.** Yieldoor H-2/H-4 (Critical): main position ticks set
directly from `slot0`, inaccurate near price borders and exploitable for
loss of funds; a related finding in the same report inverted a leverage
check tied to the same tick source. Vertex H-2 (Critical, `swapAmm`): no
check that `txn.priceX18 > 0` let a negative price flip signs on the
computed quote amount, effectively the same "attacker controls the number
the protocol trusts" pattern applied to an AMM swap price rather than an
oracle read. Mango Markets (historical incident, October 2022) accepted its
thinly traded native token as collateral using a short, single-venue price
window; coordinated spot/perpetual trading moved the reported collateral
value enough to support roughly $117M of borrowing. Treat the amount and
date as incident-source context, not independently verified KB statistics.
**Detection.** Any direct `slot0()`/`getReserves()` read feeding a
liquidation, leverage, or position-sizing decision with no TWAP, no
deviation check against a second source, and no minimum-liquidity/activity
gate.
**Fix.** Use a sufficiently long manipulation-resistant window and independent
sources, require minimum market depth/activity, cap thin collateral, and apply
deviation/circuit-breaker checks before consequential accounting.

## Cross-references
`AMM-01` is the launchpad-specific version of "attacker sets a price the
protocol will trust next." `VLT-01` (ERC4626 inflation attack) is the same
idea at the vault-share level rather than the oracle level.
