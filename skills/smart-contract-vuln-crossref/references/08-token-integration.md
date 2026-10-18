# 08 — Non-standard token integration assumptions

## TOK-01 — Fee-on-transfer / deflationary token breaks internal accounting
**Root cause.** Code assumes `amountSent == amountReceived` on every
transfer; a fee-on-transfer token violates this, desyncing internal
balance tracking from the real token balance.
**Precedents.** Very common across the corpus: `ERC4626YieldBackend` L-2
(Superfluid), `Clip Finance` M07 (deposit receipts overstate real
balance), `LenderCommitmentGroup` M-9 (Teller Finance) — pool exchange
rate goes wrong whenever a fee-on-transfer token is used because internal
accounting isn't adjusted to the amount actually received.
**Detection.** Every `transferFrom`/`transfer` in a balance-tracking
context: is the internal accounting updated from a *measured*
before/after balance delta, or from the nominal `amount` parameter?

## TOK-02 — Rebasing or slashing-capable token/vault share breaks a 1:1 assumption
**Root cause.** A token's balance can change without a transfer occurring
(rebase) or a vault share's backing can be slashed externally; code that
assumes static conversion ratios breaks.
**Precedents.** `ERC4626YieldBackend` L-2 (Superfluid Yield Backends) — no
support for vaults with slashing mechanisms.
**Detection.** Any integration with a named rebasing token (stETH-style,
ampleforth-style) or any vault whose underlying protocol can slash —
check every place a "1 share = X assets" ratio is cached rather than
recomputed.

## TOK-03 — Blacklistable / pausable stablecoin reverts and blocks a shared path
**Root cause.** USDT/USDC-style tokens can blacklist an address (reverting
any transfer to/from it) or be globally paused. If that transfer sits on a
shared code path (e.g. inside a liquidation or a batch payout), one
blacklisted/paused participant can block the operation for everyone else
on that path.
**Precedents.** `OstiumVault` M-10 — USDC blacklisting a trader's address
prevents that trader's liquidation, since even a zero-value transfer
attempt to a blacklisted address reverts. Nerite L-2 — pausable/
blacklistable collateral tokens (tETH, XVS) could cause liquidations to
fail.
**Detection.** Trace every liquidation/batch/settlement function for a
single `transfer`/`transferFrom` call whose failure reverts the *entire*
batch rather than just skipping the affected party.

## TOK-04 — `approve()`/`transfer()` used instead of SafeERC20, or wrong token approved
**Root cause.** Non-standard ERC20s that don't return a `bool` (or revert
on a nonzero→nonzero approval change) break with raw `approve()`/
`transfer()` calls.
**Precedents.** `WBTCZapper` M-2 (Evro) — approved the *wrong* token
variant entirely (see `RND-03`) — a related but distinct bug from the
missing-SafeERC20 pattern. General missing-`SafeERC20` findings recur
across nearly every audit in the corpus as Low/Informational.
**Fix.** Use `safeApprove`/`forceApprove`/`safeTransfer` throughout;
reset approvals to zero before setting a new nonzero value if not using
`forceApprove`.

## TOK-05 — Wrong wrapped-native-token address assumed across chains
**Root cause.** Code hardcodes or defaults to "WETH" as the native-token
wrapper on every chain, but some chains use a different symbol/address for
their native wrapper.
**Precedents.** `AaveETHYieldBackend` M-1 (Superfluid Yield Backends,
Medium) — used the WETH address on Polygon, where the correct native
wrapper is WPOL, not WETH.
**Detection.** Any multi-chain deployment: verify the native-wrapper
address is chain-configured, not a single hardcoded constant reused
everywhere.

## TOK-06 — `address.transfer()`/`.send()` 2300-gas stipend breaks recipients
**Root cause.** `.transfer()`/`.send()` forward a fixed 2300 gas, which is
insufficient for many smart-contract wallets or any recipient with
non-trivial `receive()`/`fallback()` logic; it also becomes fragile if gas
opcode costs ever change.
**Precedents.** Extremely common Low-severity finding across the corpus —
`PreDepositVault::sweep()` L-4 (GAIB), `OstiumPriceUpKeep::withdrawEth()`
L-16, Trestle wTIA Bridge L-3, Glacier L-01, and many more.
**Fix.** Use `Address.sendValue()` or a raw `.call{value: amount}("")`
with a reentrancy guard already in place.

## Cross-references
`AMM-03`/`AMM-07` cover the launchpad-specific transfer-lock variant of
this category.
