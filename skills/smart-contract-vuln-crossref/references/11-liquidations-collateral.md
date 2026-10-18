# 11 — Liquidations & collateral / CDP accounting

## LIQ-01 — Liquidation math ignores the bonus/fee, missing the target health factor
**Root cause.** A "maximum liquidatable amount" formula solves for a
target post-liquidation health factor but omits the liquidation
bonus/incentive from the equation, so the actual resulting health factor
overshoots or undershoots the target — sometimes leaving the position
liquidatable again immediately.
**Precedents.** `ViewLogic::maxLiquidatable()` M-10 (Cap) — computed debt
to liquidate for an exact target health but didn't account for the bonus,
which affects the final health, leaving the agent liquidatable again right
after. `ManagedLeveragedVault::executeWithdrawalEpoch()` M-8 (Beraborrow
Managed Dens) — similar family, applied fees to the wrong side of a
repay/withdraw calculation.
**Detection.** Any liquidation-sizing formula: write out the full
post-liquidation balance sheet by hand including every fee/bonus/incentive
term the code applies elsewhere, and check the sizing formula includes all
of them.

## LIQ-02 — Seized collateral or liquidation proceeds routed to the wrong party
**Root cause.** A liquidation function correctly identifies the amount to
seize but sends it to the wrong address — the lender/pool instead of the
liquidator, or vice versa.
**Precedents.** `liquidateDefaultedLoanWithIncentive()` H-4 (Teller
Finance, Critical) — sent collateral to the `LenderCommitmentGroup`
instead of the actual liquidator, removing the liquidator's incentive to
liquidate at all (a protocol-health issue, not just a one-off loss).
**Detection.** Trace the exact recipient variable in every liquidation
transfer against who the liquidation mechanism is *supposed* to reward.

## LIQ-03 — Bad debt is never socialized/cleared and silently accrues
**Root cause.** The protocol has no mechanism (or a broken one) for
handling debt that exceeds recoverable collateral value; it just sits on
the books, understating insolvency risk until a crisis makes it visible
all at once.
**Precedents.** BendDAO H-05 (Code4rena, Critical) — bad debt never
handled, placing insolvency risk on the whole protocol whenever collateral
crashes or debt spikes. Exactly Protocol Update M-9 — earnings accumulator
not triggered before liquidating, causing accumulation of unaddressed bad
debt over repeated liquidations.
**Detection.** Ask explicitly: "what happens when collateral value < debt
value at liquidation time?" — if the answer is "the liquidation reverts"
or "nothing, the position just sits there," that's this finding.

## LIQ-04 — Borrower can indefinitely delay liquidation by refreshing a timeout
**Root cause.** A liquidation-avoidance mechanism intended to be temporary
(e.g. "give the trader a grace window after updating their stop-loss") can
be re-triggered by the trader themselves faster than the window expires,
making liquidation permanently avoidable.
**Precedents.** Ostium H-01 (Critical) — traders who continually update
their stop-loss just before the SL timeout expires never face liquidation,
turning a grace-period feature into an indefinite liquidation-immunity
switch.
**Detection.** Any "grace period after user action X" pattern: check
whether the user can trigger action X again, cheaply, before the grace
period expires, to reset the clock forever.

## LIQ-05 — Worst-of price selection logic is inverted
**Root cause.** A protocol intends to always use the *worse* of two price
sources (e.g. spot vs. TWAP) against the user, to prevent the user from
choosing a favorable moment to act — but the comparison operator or branch
selection is backwards, picking the *better* price for the user instead.
**Precedents.** `LenderCommitmentGroup_Smart` H-7 (Teller Finance,
Critical) — calculates spot and TWAP prices intending to pick the worse
one for the borrower, but the logic is inverted, letting borrowers time a
swap right before withdrawing to borrow at a discount.
**Detection.** Any "worst-of"/"min of"/"conservative price" comparison:
write out both branches concretely with sample numbers and confirm the
selected branch is actually the one that disadvantages the user, not the
protocol.

## Cross-references
`ORC-06` (spot price used where TWAP intended) frequently sits upstream of
`LIQ-05` — check both together whenever a liquidation path touches an AMM
price directly.
