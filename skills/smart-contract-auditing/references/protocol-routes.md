# Protocol-specific routing

Load only routes supported by the map. Apply the core passes regardless.

## AMM, DEX, and launchpad

- Curves/invariants, token ordering, ticks/ranges, fee tiers, protocol fees, swap
  callbacks, flash paths, and reserve/accounting synchronization.
- Pool creation/initialization, deterministic addresses, launch/graduation,
  migration, liquidity seeding, price validation, min amounts, deadlines, partial
  fills, refunds, LP/NFT custody, lockers, and creator/treasury fee distribution.
- Bonding-curve reserves, buy/sell symmetry, graduation thresholds, anti-snipe
  state, pending-launch configuration binding, and public ordering/griefing.

## Vault and ERC-4626

- Deposit/mint/withdraw/redeem and preview/convert parity.
- First deposit, donation, virtual shares/assets, rounding direction, caps, fees,
  slippage, queued withdrawals, strategy debt, unrealized gains/losses, and
  emergency exit.
- Share transfers versus lock/reward/position state; underlying vault/protocol fees
  and non-1:1 conversions.

## Lending, CDP, and stablecoin

- Collateral/debt accounting, interest indexes, accrual timing, health factor, LTV,
  liquidation thresholds/bonuses/close factor, bad debt, reserves, repayment,
  collateral toggles, isolation/e-mode, caps, and peg mechanisms.
- Oracle composition, stale/closed markets, sequencer state, thin collateral,
  depeg/correlation assumptions, self-liquidation, and socialized losses.

## Staking, gauges, rewards, and governance

- Stake/unstake/claim/checkpoint symmetry, reward-per-share, epoch boundaries,
  emission caps, gauge/controller wiring, missed-update recovery, and dust.
- Vote/poke/reset, delegation, snapshot/checkpoint timing, flash power, quorum,
  proposal state, timelock execution, and re-execution.

## Perpetuals and asynchronous markets

- Margin/PnL/funding/fees, oracle timing, liquidations, ADL/insurance, position
  increase/decrease symmetry, keeper ordering, and collateral conversion.
- Two-phase request/finalize/cancel state, stale snapshots mixed with live values,
  callback authentication, execution fees, and unavailable keepers/oracles.

## Token, launch token, and authority review

- All mint/burn paths and caps; blacklist/freeze/fee/trading/max-wallet/max-tx;
  hidden/secondary admins; renounce behavior; router/pair mutation; LP withdrawal or
  migration; auto-swap slippage; rebasing/reflection; transfer hooks.
- Verify real authority and LP state on-chain. Classify retained owner power as
  trust risk unless an unprivileged exploit path exists.

## Bridge and cross-chain protocol

- Message origin/sender/domain, proof/signature set, nonce/replay, ordering/finality,
  rate limits, duplicate execution, token representation, lock/mint/burn/release,
  refunds/retries, relayer incentives, upgrades, and dual accounting.

## Proxy, factory, clone, and modular account systems

- Creation salt/address predictability, implementation selection, initialization,
  registry validation, module/hook/plugin authorization, caller identity through
  proxies, arbitrary execution, upgrade/storage, and removal/recovery.

## Diff or remediation review

- Pin base and target commits. Build the dependency and behavioral blast radius of
  the diff, including generated code/config/deployment changes.
- Reproduce the original finding, require the patch to make its regression fail,
  then test bypasses, alternate entry points, new DoS, accounting shifts, privilege
  changes, and compatibility/storage consequences.
- Do not claim a full audit when only a diff was reviewed.
