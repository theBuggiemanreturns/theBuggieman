# 03 — ERC4626 / vault share accounting

## VLT-01 — First-depositor / inflation attack
**Root cause.** Classic ERC4626 inflation: an attacker deposits a trivial
amount first, then donates underlying directly to the vault to inflate the
assets-per-share ratio before a victim's deposit, rounding the victim down
to zero (or near-zero) shares.
**Precedents.** `LoopStrategy` (Medium, MORE Optimizer, 3S-MORE-M02) —
inherits `ERC4626Upgradeable` and is vulnerable via the standard
1e18-deposit-then-donate sequence. Note many modern OZ-based vaults
mitigate this by default via a decimals offset (see the "not every vault
is vulnerable" counter-example in Aegis Staked YUSD L-2 — decimals offset
0 was judged to already dilute attacker donations enough to be low
severity there). **Always check whether a decimals offset / virtual
shares mechanism is actually present before rating this Medium+.**
**Detection.** New vault, `totalSupply() == 0` reachable by a normal user,
and a public/permissionless way to send the underlying asset directly to
the vault's balance without going through `deposit()`.

## VLT-02 — `withdraw()`/`redeem()` missing a slippage parameter
**Root cause.** ERC4626's standard `withdraw`/`redeem` signatures have no
min/max slippage argument, so if the vault's asset conversion can move
between transaction submission and execution (fees, price changes,
oracle updates), the user has no protection.
**Precedents.** `VaultV2` M-1 (Morpho Vault V2) — flagged as worth adding a
slippage-protected variant even though it's spec-compliant behavior, not
a bug per se.
**Detection.** Worth flagging whenever the vault's share price can move
meaningfully within a block or a few blocks (fee accrual, external
strategy rebalances) and there's no protected withdraw path offered.

## VLT-03 — `maxDeposit`/`maxMint`/`maxRedeem` don't reflect real caps
**Root cause.** The vault enforces a cap or limit somewhere in
`deposit`/`withdraw`, but the `maxX()` view functions used by integrators
and off-chain tooling don't reflect it — callers relying on the ERC4626
spec ("call `maxDeposit` then deposit that amount, it must not revert")
get unexpected reverts.
**Precedents.** `PreDepositVault` L-1 (GAIB Pre-Vaults) — `maxDepositLimit`
not reflected in `maxDeposit`/`maxMint`. `LoopedVault` L-6 (Yieldoor) —
`maxMint`/`maxRedeem` not overridden despite a deposit cap existing.
**Fix.** Override every `maxX()` to account for every real-world
constraint (admin caps, paused state, underlying protocol limits).

## VLT-04 — `totalAssets()` counts balances that aren't actually redeemable
**Root cause.** `totalAssets()` sums tracked balances (e.g. an aToken
balance, an idle-strategy balance) that can be independently swept,
donated-away, or are otherwise not truly backing shares 1:1.
**Precedents.** `PreDepositVault` L-2 (GAIB) — `sweep()` could remove
aTokens/USDS that were also counted in `totalAssets()`, directly
decreasing per-share backing. `LoopStrategy` 3S-MORE-L02 (MORE Optimizer)
— tracked a token balance in `totalAssets()` that the vault could never
actually redeem/withdraw, permanently overstating share value.
**Detection.** For every component summed into `totalAssets()`, confirm
there is no admin or external path that can remove that value from the
vault without also burning the corresponding shares.

## VLT-05 — Rounding in withdraw/deposit favors the user, not the protocol
**Root cause.** Fee, interest, or share-conversion math rounds down (or up)
in the direction that benefits the caller rather than the protocol on
every single operation — individually negligible, but exploitable via
volume or repeated round-trips.
**Precedents.** `VaultV2` L-2 (Morpho) — performance/management fee
accrual rounds down, systematically under-collecting for the protocol.
Superfluid M-2 (Aave rounding drain) is the aggressive version of this:
rounding on Aave's own scaled-balance math let an attacker extract real
yield via many small withdrawals, not just under-collect a fee.
**Rule of thumb.** Rounding errors are only "Low/gas" when they cannot be
chained by repetition into meaningful extraction (see `RND-01` for when
they cross into Critical/High) — always check whether the operation is
gated by a fee/cooldown that makes repetition uneconomical, or not.

## VLT-06 — Vesting/interest period reset drops or re-leaks prior yield
**Root cause.** A vault streams interest/yield over a period and resets
period-tracking state, but fails to zero out (or double-counts) the
*previous* period's unvested remainder when a new period starts with zero
new interest.
**Precedents.** `LoopedVaultV11::updateTotalAssets()` M-1 (Yieldoor
LoopedVault) — didn't reset vesting interest to zero when the new period's
`vestingInterestPreFee` was null, so the next period kept vesting stale
interest from the period before.
**Detection.** Any "vesting"/"streaming" accrual pattern: trace what
happens to the *remainder* variable across a period boundary when the new
period's inflow is zero.

## VLT-07 — Vault incompatible with fee-on-transfer / rebasing / slashing underlying
See `TOK-01`/`TOK-02` for the general pattern; `ERC4626YieldBackend` L-2
(Superfluid Yield Backends) is the vault-specific instance: no support for
deposit/withdrawal fees or slashing on the underlying ERC4626 vault, which
can lead to loss of funds or insolvency for other depositors.

## Cross-references
`AMM-03` (balance-based LP mint donation) is the AMM-pool analogue of
`VLT-01`. `RND-01`–`RND-05` cover rounding mechanics in more depth.
