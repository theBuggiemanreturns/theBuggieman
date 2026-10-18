# 12 — Governance, staking & rewards accounting

## GOV-01 — Changing reward rate/duration mid-stream leaks or strands rewards
**Root cause.** Reward-per-second style distributors recompute a rate
whenever the admin calls a "set duration"/"notify reward amount" function;
if the recomputation doesn't correctly fold in whatever was left over from
the previous, still-active period, value is either double-counted (leaked
to whoever claims first) or permanently stranded.
**Precedents.** `StakedEXA::notifyRewardAmount()` M-13 (Exactly Protocol) —
precision loss in the reward-rate calculation locks some rewards as
permanently unclaimable. `StakedExa::update()` M-2 — resets `avgStart`
whenever elapsed time exceeds a reference time, making rewards stuck
longer than intended.
**Detection.** For any "restart the reward stream" admin function: work
through the exact sequence "period A active, N seconds in → admin resets
for period B" and check the leftover-from-A accounting explicitly, don't
trust that it "nets out."

## GOV-02 — Auto-voter/delegate can alter a choice after the snapshot window closes
**Root cause.** A voting system snapshots choices at epoch end for reward
distribution, but an "auto-vote" or delegate mechanism isn't frozen at the
same moment, letting a voter change their allocation *after* the window
that was supposed to have locked it, to game the distribution.
**Precedents.** BMX Deli Swap H-4 (Critical) — missing freeze/snapshot of
auto-vote choices at epoch end let attackers manipulate voting results
after the fact.
**Detection.** Any epoch/snapshot-based voting: verify every path that can
change a vote (manual and automated/delegated) is blocked, not just the
manual one, once the snapshot is taken.

## GOV-03 — Vote-power or delegation formula can be reused/abused for outsized reward
**Root cause.** A delegation mechanism doesn't prevent the same underlying
voting power from being counted more than once, or a rewards formula
scales unfairly with vote size (e.g. quadratic-in-the-wrong-direction),
systematically favoring large or repeatedly-delegating holders.
**Precedents.** veRWA H-02 (Code4rena, Critical) — delegate mechanism in
`VotingEscrow` allowed infinite votes in `vote_for_gauge_weights()`. Ajna
Protocol M-02 — delegate reward formula scaled with the *square* of votes,
unfairly disadvantageous to delegates with less voting power and reducing
decentralization as a side effect (a fairness/design finding, not a direct
fund-theft one — still worth logging).
**Detection.** Any delegation feature: check whether delegated power is
deducted from the delegator or merely *added* to the delegate (the latter
enables double-counting); any power-weighted formula: check its
scaling direction against the intended incentive.

## GOV-04 — Points/claim signature can be front-run by a batch keeper call
**Root cause.** A user-facing claim function verifies a signed message and
then calls into a shared points/units-update function; if that shared
function can also be called directly and permissionlessly by anyone
(e.g. a keeper batch job), an attacker can front-run the user's claim,
triggering the update themselves and disrupting the intended attribution.
**Precedents.** `FluidLocker::claim()` M-1 (Superfluid Locker System) —
connects to the pool then calls `EPProgramManager::batchUpdateUserUnits()`
to verify the signature and update points; a frontrunning attacker calling
`batchUpdateUserUnits()` directly can DoS a user's expected balance
increase.
**Detection.** Any two-step "verify signature, then call a shared
state-update function" pattern: check whether step two is independently
callable and, if so, what a front-runner gains by calling it first.

## Cross-references
`SIG-01`/`SIG-02` cover the signature-specific mechanics that often
underlie `GOV-04`.
