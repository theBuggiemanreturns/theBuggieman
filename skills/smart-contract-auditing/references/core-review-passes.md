# Core smart-contract review passes

Read this file for every audit. Apply each pass across the full call graph and all
mapped invariants. Record `not applicable` only with protocol-specific evidence.

## 1. Authorization and lifecycle

- Compare modifiers and caller checks across sibling functions.
- Distinguish existence checks from ownership/approval checks.
- Test custom modifiers that silently skip the body rather than revert.
- Inspect initializer/reinitializer exposure, implementation initialization,
  deployment races, role grants/revocations, pause bypass, renounce behavior, and
  phase-transition authorization.
- Probe admin/keeper functions read-only from an unprivileged caller, then inspect
  why calls revert or succeed; an apparently successful `eth_call` is a hypothesis,
  not proof of usable privilege.
- Check permissionless maintenance such as `poke`, `sync`, `snapshot`, `crank`,
  `finalize`, `liquidate`, and `distribute` for caller-controlled targets/timing.

## 2. Accounting, coupled state, and path symmetry

- For every balance/share/debt/supply/reward/reserve pair that must move together,
  enumerate all writers and failure paths.
- Inspect early returns, partial completion, wrong update order, stale caches,
  deletion before success, missing reversal/refund, double claim, and emergency
  paths that skip normal accounting.
- Compare deposit/mint/withdraw/redeem and create/update/cancel state changes.
- Reconcile actual token balances with internal credits, liabilities, shares,
  pending claims, cross-chain mirrors, and accumulated fees.
- Test direct donations, forced ETH, unsolicited tokens, and sync/reconcile calls.
- Treat state updates performed before a failed low-level send or ignored return as
  possible accounting corruption.

## 3. Math, units, precision, and boundaries

- Test zero, one, exact thresholds, one below/above, maximum values, empty/full
  collections, first/last user, first/last epoch, and exact deadline timestamps.
- Check rounding direction for every division and whether repetition compounds dust.
- Check decimals and base units across tokens, shares, feeds, ratios, percentages,
  basis points, ticks, fixed-point formats, and chain-specific constants.
- Inspect signed/unsigned conversions, narrowing casts, unchecked arithmetic,
  multiplication-before-division overflow, saturating math, and fraction comparison.
- Differentially test custom solvers, curves, interest, reward, liquidation, swap,
  tick, and share math against a reference implementation or high-precision model.
- Ensure minimum output is nonzero where zero would mint/burn/credit value unfairly.

## 4. External calls, token behavior, and reentrancy

- Trace every call, delegatecall, staticcall, transfer, hook, callback, fallback, and
  user-controlled target/data.
- Test classic, cross-function, cross-contract, callback, and read-only reentrancy.
- Inspect state-update-after-external-call on queued/timelocked actions even when it
  does not look like a token callback.
- Model fee-on-transfer, rebasing, ERC-777/hooks, false/no return, codeless token
  addresses, reverting receivers, unusual decimals, blacklist/freeze, and tokens
  whose pool transfers differ from wallet transfers.
- Check approval zero-reset/infinite approval behavior and stale approvals after
  integration changes.
- For transient storage (`TSTORE`/`TLOAD`), test stale transaction-local values and
  nested/cross-contract calls against persistent state.

## 5. Oracle and economic manipulation

- Identify every value used for collateral, liquidation, minting, redemption,
  solvency, fee, reward, or eligibility.
- Check spot versus real TWAP behavior, observation history/cardinality, multi-source
  validation, heartbeat/staleness, answer sign, round completeness, Pyth confidence,
  sequencer downtime/grace periods, fallback units, and closed-market calendars.
- Test flash liquidity, self-trading, thin markets, donated liquidity, depegs, and
  LST/LRT assumptions instead of treating wrapped assets as permanently 1:1.
- Analyze incentives: can a caller worsen their own health, trigger a bonus, choose
  victims, socialize losses, externalize slippage, or profit from griefing?
- Quantify capital requirements and profitability after fees, liquidity depth,
  price impact, and protocol limits.

## 6. AMM, migration, MEV, and shared-state seams

- Check permissionless pool/state creation or initialization before protocol action.
- After create-if-needed calls, verify existing state matches intended price,
  tokens, fee tier, hooks, and ownership rather than trusting a silent no-op.
- Require meaningful min/max amounts and deadlines; check partial fills, token order,
  ticks/ranges, refund paths, LP/NFT custody, lockers, and recovery.
- Model public-mempool ordering, sandwiching, back-running, deterministic future
  addresses, repeated DoS/griefing, and chain/sequencer realities.
- Diff forked protocol code and focus on custom glue, migration, settlement, and
  integration seams rather than assuming audited upstream behavior transfers.

## 7. Vaults, lending, staking, and token supply

- Test first-depositor/share inflation, direct donation, virtual/dead shares,
  preview/convert parity, fee/slippage-aware conversions, and underlying-protocol
  rounding.
- Test health factor, LTV, liquidation close factors/bonuses, bad debt, interest
  indexes, repayment, collateral enable/disable, and insolvent edge states.
- Check reward/emission accounting, missed epochs, checkpoint ordering, vote refresh,
  stake/unstake/claim symmetry, and stranded rewards.
- Enumerate every mint/burn path and cap; retained mint/freeze/blacklist/fee/pair/
  router/LP authorities are trust or rug vectors whose actual bounds matter.
- Verify supply and authority behavior on-chain; a renounced owner does not prove
  secondary roles or upgrade paths are gone.

## 8. Signatures, governance, and account abstraction

- Compare every function parameter with every field in the signed digest.
- Require nonce, deadline, signer/action/amount/destination binding, chain ID, and
  verifying-contract/domain separation; inspect invalidation and replay across
  upgrades, deployments, forks, and signature types.
- Check malleability, ERC-1271 behavior, permit variants, batch signatures, and
  caller-selected targets/data.
- Test flash-inflated governance/snapshot power, delegation/checkpoint timing,
  proposal execution ordering, quorum boundaries, and timelock re-execution.
- For ERC-4337, inspect EntryPoint trust, paymaster sender/sponsorship bounds,
  validation/execution state, prefund griefing, and signature aggregation.
- For EIP-7702/delegated EOAs, inspect delegation authorization, domain binding,
  revocation, implementation changes, replay, and assumptions that `tx.origin` or
  an EOA cannot execute code.

## 9. Proxy, clone, and upgrade safety

- Resolve the live proxy, implementation, beacon, admin, clone target, and storage
  layout; do not audit only the shell.
- Check implementation initialization, initializer ordering, reinitializers,
  `_authorizeUpgrade`, selector collisions, delegatecall/self-call, rollback,
  immutable values, constructors, and library links.
- Compare storage layouts across every upgrade and test migration from actual prior
  state. Check removed/retyped/reordered fields and inheritance changes.
- Verify upgrade authority, multisig/timelock, emergency upgrades, implementation
  allowlists, and whether changes retroactively alter existing user positions.
- Diff deployed code against the version previously audited; prioritize post-audit
  changes and components excluded from earlier scope.

## 10. Cross-chain and asynchronous flows

- Verify origin chain/domain, sender, destination, message type, nonce, replay,
  finality, proof/signature set, and default/zero-value semantics.
- Model delayed, dropped, duplicated, reordered, and conflicting messages.
- Identify the single source of truth for mirrored balances, debt, supply, rewards,
  price, and pending state; test dual-accounting desynchronization.
- Inspect request/finalize/cancel flows that mix stale snapshots with live state.
- Check rate limits, refund/retry, partial execution, failure recovery, migration,
  and upgrades spanning chains.
- For bridges, distinguish message validity from token/accounting solvency.

## 11. Denial of service and liveness

- Find permissionless growth followed by unbounded iteration; require caps,
  pagination, pull patterns, or bounded batches.
- Model malicious tokens/receivers, revert-on-push payments, storage growth, gas
  limits, block stuffing, oracle/keeper/relayer failure, unavailable dependencies,
  and stuck phases.
- Check whether anyone can initialize/synchronize empty canonical state, consume a
  one-time slot, precreate deterministic resources, or repeatedly force retries.
- Verify pause/unpause, cancellation, rescue, timeout, fallback, and shutdown paths
  remain reachable in adverse states.
- Distinguish temporary delay, economically repeatable griefing, and permanent loss
  of availability; severity follows demonstrated impact.

## 12. Configuration, centralization, and deployment

- Validate zero addresses, token/router/oracle/pool wiring, units/decimals, caps,
  fee bounds, delay bounds, role recipients, ownership transfer, chain IDs, and
  initialization order.
- Verify actual live values at a pinned block rather than relying on defaults or docs.
- Map compromised-role blast radius and label trusted-role power separately from a
  permissionless vulnerability.
- Check multisig owners/threshold, timelock coverage, pause guardian, upgrade path,
  monitoring, incident response, and recovery/rollback.
- Simulate exact deployment and initialization; ensure no hijack window and match
  source, bytecode, metadata, compiler, libraries, and storage layout.
- A launch/readiness conclusion is tied to one commit and configuration, never a
  universal claim of safety.
