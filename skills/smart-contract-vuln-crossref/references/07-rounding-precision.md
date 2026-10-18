# 07 — Rounding, precision & decimals

## RND-01 — Rounding direction favors the caller and is abusable by repetition
**Root cause.** A single operation's rounding error is individually
negligible, but the caller can invoke the operation many times cheaply,
each time capturing the rounding in their favor, compounding to a real
drain.
**Precedents.** `StakingPool::unstake()` H-3 (Spirit Protocol, Critical) —
reduces a staker's units pro-rata to the unstaked amount, rounding units
*down* each time; repeated partial unstaking lets a staker withdraw more
than their fair share over many calls. Superfluid Yield Backends M-2 —
Aave's own scaled-balance rounding let an attacker drain accumulated yield
via many small withdrawals, each burning more scaled balance than the
actual value withdrawn.
**This is the line between "Low/gas rounding nit" and "Critical/High
exploit":** always check whether the rounding-favorable operation (a) is
cheap/uncapped to repeat, and (b) has no minimum-size or cooldown that
makes repetition uneconomical. If both hold, escalate severity
accordingly — this exact reasoning is why the two precedents above were
rated Critical/High rather than Low.

## RND-02 — Division before multiplication
**Root cause.** `a / b * c` truncates before the multiplication has a
chance to preserve precision, versus `a * c / b`.
**Precedents.** `FluidLocker::_getUnlockingPercentage()` M-2 (Superfluid
Locker System) — divided before multiplying, causing a significant
precision error in the unlock percentage calculation.
**Detection.** Grep for `/ ... *` sequences in financial math; almost
always reorderable to `* ... /` with an intermediate-overflow check if
needed (or use a full-precision `mulDiv`).

## RND-03 — Decimal mismatch between wrapped/native representations of the same asset
**Root cause.** A protocol handles both a token and its wrapped
counterpart (e.g. 8-decimal WBTC vs. an 18-decimal wrapped wWBTC) and
mixes the two decimal bases in one calculation, or approves/uses the
wrong one entirely.
**Precedents.** `WBTCZapper` (Evro Collateral Onboarding): M-1 mixed
18-decimal wWBTC with 8-decimal WBTC in `closeTroveFromCollateral()`,
causing reverts or bypassed slippage protection; M-2 approved the wrong
token variant for the exchange, breaking swaps; M-3 hit precision loss on
amounts not evenly divisible by the `1e10` conversion factor, causing
reverts.
**Detection.** Anywhere two representations of "the same" asset coexist —
diff every arithmetic operation and every `approve()`/`transferFrom()`
call against which variant is actually expected.

## RND-04 — Integer truncation permanently strands dust/rewards
**Root cause.** `total / period` (or similar) truncates a remainder that
is never distributed anywhere and accumulates as permanently unclaimable
dust — usually Low/Medium, but check whether the "dust" can grow into
something non-trivial across many periods or many users.
**Precedents.** `upsertIncentive` M-3 (BMX Deli Swap) — every remainder
from `total / WEEK` is truncated and unstreamable. `ShadowStrategyGauge::collectGaugeRewards()`
L-5 (Yieldoor Gauges) — worse variant: when the swap-in-half balance
equals 1, `swapAmount / 2` reverts, actually DoSing reward collection
rather than just losing dust — check whether a truncation bug can also
trigger a revert at small balances, not only a value loss.
**Detection.** Every `/` in a rewards/incentive distribution loop; check
what happens to the remainder, and what happens at the smallest possible
non-zero input.

## RND-05 — Hardcoded `1e18` scaling regardless of actual token decimals
**Root cause.** Code assumes 18-decimal precision throughout, breaking
silently for any 6- or 8-decimal token routed through the same path.
**Precedents.** `MellowPriceFeed` 3S-Ojo-L01 (Ojo Mellow Price Feed) —
hardcoded `1e18` ratio calculation regardless of the actual underlying
decimals.
**Detection.** Grep for literal `1e18`/`10**18`/`WAD` constants used on a
value whose token/decimals aren't already known-fixed at 18.

## Cross-references
`VLT-05` covers the vault-share-specific instance of favorable rounding;
`RND-01` is the general, protocol-agnostic version.
