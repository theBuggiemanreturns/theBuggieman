# 04 — Reentrancy & checks-effects-interactions violations

## REN-01 — State written after an external call/transfer
**Root cause.** Classic CEI violation: the external call (token transfer,
external protocol call) happens before the contract updates its own
accounting.
**Precedents (representative — this is the single most repeated Low/Med
finding in the corpus, seen 15+ times).** `GovernorTimelock::executeProposals()`
L-2 (Maple Governor Timelock) — proposal info deleted *after* the target
call, letting a malicious executor reenter and re-execute the same
proposal. `LoopedVault::fulfillWithdraw()` L-3 (Yieldoor) — transfers before
state update. `StakingAssetManager` (Singularity, multiple Crit/High
findings) — repeatedly flagged for not following CEI, in a protocol where
it was actually exploitable end-to-end (see `3S-SG-C03`).
**Detection.** For every function that both (a) sends value/tokens/calls
an external contract and (b) mutates the contract's own storage, confirm
the storage mutation happens *first*. Where a `nonReentrant` guard is
present, still flag CEI violations as defense-in-depth (`SMELL-05`) unless
you can show reentrancy is truly impossible (e.g. recipient is a trusted,
non-contract-callback asset).

## REN-02 — Flash-loan / callback caller identity not validated
**Root cause.** A callback function meant to only be invoked by a specific
trusted contract (a lending market completing a flash loan, a router
completing a swap) doesn't check `msg.sender`, so anyone can call it
directly with attacker-chosen parameters.
**Precedents.** `LoopStrategy::onMoreFlashLoan()` (Critical,
3S-MORE-C01, MORE Optimizer) — callable directly by anyone, draining
collateral. This is one of the highest-severity, simplest-to-spot bug
classes in the whole corpus: a single missing `require(msg.sender == market)`.
**Detection.** Grep for every function name that looks like a callback
(`onFlashLoan`, `uniswapV3SwapCallback`, `onMoreFlashLoan`, `receiveXCall`,
etc.) and confirm the first line validates the caller.

## REN-03 — Reentrant call during unlock/withdraw drains beyond entitlement
**Root cause.** A recorded "failed" or "pending" cross-contract action can
be re-triggered by its own callback before the first invocation's state
change is finalized, letting the same entitlement be paid out more than
once.
**Precedents.** `ConnextHandler::executeFailedWithUpdatedArgs()` H-04 (Fuji
Finance) — the `allowedCaller` could reenter and steal all assets by
calling the function again after the inner `xBundle()` call, before the
executed flag was set. `FluidLocker::instantUnlock()` M-3 (Superfluid
Locker System) — missing a check for stakers in the tax pool let a user
unlock all funds instantly with no tax, a design-level reentrancy-adjacent
gap rather than a raw `.call` reentrancy.
**Detection.** Any "retry a previously failed cross-contract action" or
"stake/unstake with a pool-dependent penalty" pattern: verify the
executed/settled flag is set *before* any external call that could loop
back in.

## REN-04 — Missing `nonReentrant` on a state-critical entry point
**Root cause.** Most functions in a contract have the reentrancy guard;
one or two related entry points (often a newer or less-obvious function
like `rebalance()` or a specific withdrawal branch) were missed.
**Precedents.** `LoopedVault::rebalance()` L-1 (Yieldoor) and its
`requestWithdraw()` path when idle funds are insufficient — both missing
the guard that the rest of the contract otherwise applies consistently.
**Detection.** List every state-mutating external/public function in the
contract and diff against which ones carry `nonReentrant` — inconsistency
is the signal, not the guard's mere presence or absence in isolation.

## Cross-references
`AMM-03`/`VLT-01` describe donation-style manipulation that doesn't
require reentrancy at all but is often mentally filed next to it — keep
them distinct in a report.
