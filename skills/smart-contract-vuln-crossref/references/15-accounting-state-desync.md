# 15 — Accounting state desynchronization

Two state variables are supposed to move together (`totalSupply` and a
token balance, `totalShares` and `totalAssets`, `totalDebt` and a
per-period tracker). One code path updates variable A but not variable B.
Later code reads both and makes a decision — pays out yield, mints
shares, releases collateral — based on the gap. No reentrancy, no
external manipulation, and often no oracle is involved at all: the bug is
purely in the bookkeeping.

*Source note:* this file was seeded from an external corpus that
describes this as the single highest-frequency Critical bug class in its
dataset ("28% of all Criticals"). That percentage is the source's own
claim, not independently verified here — treat it as a signal that this
category is worth checking early and thoroughly, not as a verified
statistic to cite as fact in your own report.

## ACD-01 — Phantom yield/balance via a premature (decrement-before-transfer) update
**Root cause.** A "yield" or "surplus" figure is computed as
`externalBalance - internalCounter` (e.g. `aToken.balanceOf(this) -
totalSupply`). If `internalCounter` is decremented *before* the
corresponding transfer actually reduces `externalBalance`, the formula
briefly (or, if multiple callers interleave, repeatedly) reports value
that hasn't actually accrued — and if the yield figure feeds a claim
function, multiple simultaneous callers can each be paid from the same
phantom surplus.
```solidity
function startUnstake(uint256 amount) external {
    totalSupply -= amount;              // decremented BEFORE the transfer
    // aToken.balanceOf(this) still reflects the OLD value here
    // yieldAmount = aToken.balanceOf(this) - totalSupply  <- inflated
}
```
**Precedent.** Alchemix V2's `startUnstake()` — exactly this shape, Medium
severity, fixed in V2.1. A related, higher-volume instance in the same
source material: a yield-bearing vault whose duplicate-report count (35
independent submitters found the same bug) is a good illustration of how
mechanically discoverable this class is once you know the shape — this is
one of the highest-value single checks for a code review, not an exotic
one.
**Detection.** Grep for every variable that looks like an aggregate
counter (`totalSupply`, `totalShares`, `totalAssets`, `totalDebt`,
`cumulativeReward`, `rewardPerShare`); for each one, find every function
that both mutates it and performs a token transfer, and check the order.

## ACD-02 — Fast-path early return skips state updates the slow path performs
**Root cause.** A function has two branches for the same logical
operation — a cheap "fast path" (funds already available, serve
immediately) and an expensive "slow path" (funds not available, go fetch
them first). The slow path correctly updates every accounting variable;
the fast path `return`s early after moving funds but *before* reaching
the same updates, because the updates were written assuming the slow
path's control flow.
```solidity
function claimRedemption(uint256 tokenId) external {
    if (transmuter.balance >= amount) {
        transmuter.transfer(user, amount);
        _burn(tokenId);
        return;   // cumulativeEarmarked, _redemptionWeight, totalDebt never touched
    }
    // slow path below updates all of the above correctly
    alchemist.redeem(...);
}
```
**Detection.** For every early `return` inside a function that also has a
longer "normal" path below it, diff the two paths' full list of state
writes. Any state variable the slow path updates that the fast path
skips is this bug, full stop — it doesn't require deep reasoning to spot
once you're actually doing the diff, which is exactly why it's worth
doing mechanically rather than trusting a read-through.

## ACD-03 — Dependent value calculated before the state it depends on is updated
**Root cause.** A rate/ratio (shares-per-asset, price-per-unit) is
computed using `totalAssets`/`totalSupply`-style variables, but the
function computes the rate *before* applying the deposit that's
supposed to be priced at the pre-deposit rate — or, symmetrically,
applies the state change before computing a rate that was meant to use
the pre-change value. Either direction is a real bug; check which order
the design actually intends and confirm the code matches it.
```solidity
function deposit(uint256 amount) external {
    _shares = (amount * totalShares) / totalAssets;  // computed first
    totalAssets += amount;   // but assets added after — wrong effective rate
}
```
**Detection.** For every share/rate calculation involving a running
total: identify which side of the calculation should reflect
"before this operation" state and which should reflect "after," and
check the actual write order against that intent, not just against
"does it compile and pass a happy-path test."

## Cross-references
`VLT-06` (vesting/interest period reset) is a specific instance of this
same family scoped to vault yield-streaming. `REN-01` (CEI violation) is
adjacent but mechanically distinct: CEI is about ordering relative to an
*external call*; this file's patterns require no external call at all —
the desync is purely between two of the contract's own storage variables.
Don't conflate the two in a report; cite whichever actually matches.
