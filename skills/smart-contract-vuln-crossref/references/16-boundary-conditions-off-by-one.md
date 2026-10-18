# 16 — Off-by-one and boundary-condition errors

A single wrong comparison operator (`>` where `>=` was needed, `<=` where
`<` was needed) at a period, timestamp, index, or amount boundary. Often
a one-character fix once found, but frequently a real economic bug, not
merely cosmetic — a boundary error at a reward-period edge can pay out
(or withhold) an entire period's rewards.

## The core heuristic
> For every `if (A > B)` (or any strict comparison): what happens when
> `A == B`? Is that the intended outcome?

This single question, asked explicitly rather than skimmed past, is the
entire technique. It's cheap enough to apply to every comparison touching
a period, epoch, deadline, index, or amount in the contracts under
review.

## BND-01 — Strict vs. inclusive comparison at a period/epoch boundary
**Root cause.** A function decides "is this period claimable" using a
strict inequality where the boundary case (exactly at period end) should
have been inclusive, or vice versa.
```solidity
function _claimableDelegationPeriods(address delegator) internal view returns (uint256) {
    if (endPeriod > nextClaimablePeriod) {   // should be >=
        return 0;                             // users who exit exactly at period end get nothing here...
    }
    return nextClaimablePeriod - lastClaimedPeriod;  // ...but this branch pays them for a period after exit
}
```
**Precedent.** VeChain Stargate — the `>`/`>=` swap let users who exited
at the exact end of a delegation period claim rewards for the period
*after* their exit, a period they had no stake in. High severity; the fix
was a single-character operator change, which is the point — boundary
bugs are cheap to introduce and cheap to fix, but not cheap to leave in
production.
**Detection.** Grep every comparison near `Period`/`Epoch`/`Round`/
`Deadline` identifiers for a bare `<`/`>` (not `<=`/`>=`), and for each
one, work out both branches at the exact boundary value by hand.

## BND-02 — Ambiguous exact-deadline behavior for a time-lock
**Root cause.** Code compares `block.timestamp` against a deadline/unlock
time without being explicit about whether the boundary instant itself is
locked or unlocked, and the answer differs from what the rest of the
contract assumes elsewhere.
**Detection.** For every `block.timestamp < deadline` / `<= deadline` /
`> deadline` / `>= deadline` check gating a lock/unlock, confirm the
chosen operator matches the intended semantics ("locked *through* the
deadline" vs "locked *until* the deadline") and that every other place in
the contract touching the same deadline uses the same convention.

## BND-03 — Loop break / array-index off-by-one
**Root cause.** `for (uint i = 0; i <= array.length; i++)` (should be
`<`) or a `break` condition that fires one iteration early/late.
**Detection.** Grep for `<=` immediately preceding `.length`, and for
every `break` inside a loop, confirm the break condition's comparison
operator against what should terminate the loop.

## BND-04 — Amount/balance boundary mishandled at exact full withdrawal or a zero-output edge
**Root cause.** A withdrawal/redemption check written as `amount >
balance` (should be `>=`, or vice versa) either wrongly blocks an exact
full withdrawal or wrongly allows withdrawing more than available; or, on
the calculation side, some input value causes a rounding/division result
of exactly zero where a non-zero result was expected (e.g. redeeming a
tiny share amount that rounds down to zero assets, but the redeem still
proceeds and burns the shares).
**Detection.** For every withdraw/redeem amount check: test the exact
boundary value (amount == balance) explicitly. Separately, for every
division in a payout calculation: ask what the smallest non-zero input
produces, and whether "produces zero" is handled (reverted, or
intentionally allowed) rather than silently accepted.

## Cross-references
`RND-01`–`RND-05` cover rounding/precision errors specifically — a
zero-output edge case (`BND-04`'s second half) sits at the intersection
of both files; check whichever framing fits the specific bug better, or
cite both if genuinely both apply. `DOS-04`/`DOS-05` cover loop-related
DoS at scale, which is a different failure mode from `BND-03`'s single-
iteration correctness error.
