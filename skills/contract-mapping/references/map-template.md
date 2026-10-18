# Protocol Map — [Protocol]

**Mapping status:** [READY_FOR_AUDIT | READY_WITH_LIMITATIONS | BLOCKED]
**Map version/date:** [value]
**Prepared from:** [repository/address/bundle paths]

An empty section means incomplete. Use `None found — <evidence>` only after an
explicit check.

## 1. Identity, authorization, and scope

| Field | Value |
|---|---|
| Protocol / version | |
| Audit mode | private audit / readiness / bounty / remediation / diff review |
| Authorization / scope source | |
| Repository and commit | |
| In-scope files/contracts/addresses | |
| Out-of-scope components | |
| Chains and chain IDs | |
| Mapping evidence directory | |

## 2. Source, build, and deployment provenance

Record compiler, optimizer, EVM version, remappings, locked dependencies, build and
test commands/results, explorer/source provider, bytecode/source matching, proxy
resolution, deployment transactions, and fork/reference blocks.

| Component | Source revision | Deployed address | Compiler/config | Verification evidence | Match status |
|---|---|---|---|---|---|
| [required] | | | | | |

## 3. Contract inventory and dependency graph

| Component | Role | Kind | Owns/holds | Upgrade model | Code provenance | Operational controller | Control overlap | Scope verdict | Source status |
|---|---|---|---|---|---|---|---|---|---|
| [required] | | contract/interface/library/external | | immutable/proxy/beacon/clone | in-house/exact upstream/modified upstream/unknown | address/role/evidence block | match/overlap/unrelated/unresolved | in scope/integration-only/out of scope | |

Represent edges explicitly:

```text
[caller/factory/proxy] --[creates/calls/delegates/reads]--> [target]
```

Include inherited contracts, linked libraries, generated contracts, factories,
clones, implementations, beacons, proxy admins, and project-owned off-chain actors.
Do not derive scope from provenance. Exact upstream code may still be self-operated
and in scope; unknown control is unresolved, not unrelated.

## 4. Roles, privileges, and trust boundaries

| Role/actor | Address or derivation | Granted by | Exact powers | Delay/threshold | Can affect existing positions? |
|---|---|---|---|---|---|
| [required] | | | | | |

Include owner/admin, upgrader, pauser, guardian, oracle manager, keeper, signer,
fee recipient, minter/burner, blacklist/freeze authority, bridge relayer, multisig,
timelock, governance, deployer, and permissionless external actors. Normalize every
address and cross-reference it against dependency controllers, constructor
recipients, role-event history, proxy/beacon admins, and mutable integration
settings. Record exact matches and partial governance/role overlap.

## 5. Callable surface and callbacks

| Component::entry point | Caller tier | Phase | Reads | Writes | Value movement | External calls/callbacks | Revert/return paths |
|---|---|---|---|---|---|---|---|
| [required] | permissionless/restricted/privileged | | | | | | |

Include inherited functions, overloads, fallback/receive, hooks, callbacks,
signature/meta-transaction paths, proxy admin surface, and permissionless
maintenance functions. Compare sibling families such as deposit/mint,
withdraw/redeem, create/update/cancel, vote/poke/reset, and pause/emergency paths.

## 6. State, accounting, and coupled variables

| State/invariant group | Writers | Readers | Must change with | Units/decimals | Initialization/default | Failure-path behavior |
|---|---|---|---|---|---|---|
| [required] | | | | | | |

Cover balances, shares, debt, supply, reserves, reward indices, epochs, nonces,
price caches, pending requests, cross-chain mirrors, caps, fees, and transient state.

## 7. Assets, liabilities, and value-flow paths

| Flow ID | Entry → custody/conversion → exit | Assets/shares/debt | Who initiates | Bounds/slippage/fees | Failure/recovery path |
|---|---|---|---|---|---|
| VF-01 | | | | | |

State maximum known value at risk and distinguish protocol assets, user claims,
unrealized accounting, admin-controlled funds, and external liquidity.

## 8. Lifecycle and state machines

| Machine/object | States | Transition entry points | Preconditions | Repetition/order rules | Cancellation/recovery | Terminal state |
|---|---|---|---|---|---|---|
| [required] | | | | | | |

Include initialization, deposits/withdrawals, launch/graduation, epochs, requests
and finalization, liquidation, bridging, governance, pause, upgrade, and shutdown.

## 9. External integrations and assumptions

| Dependency/address | Called from | Interface/function | Code provenance | Operational controller | Control overlap | Scope verdict | Assumption/validation/failure modes |
|---|---|---|---|---|---|---|---|---|
| [required] | | | in-house/exact upstream/modified upstream/unknown | address/role/evidence block | match/overlap/unrelated/unresolved | in scope/integration-only/out of scope | |

Cover tokens, DEXs, pools, routers, oracles, sequencers, bridges, vaults, lending
markets, callbacks, signers, keepers, and off-chain inputs. Record units, decimals,
freshness, ordering, finality, return-value, callback, and upgrade assumptions.
An out-of-scope verdict requires affirmative scope/control evidence; “external,”
“canonical,” or “third-party” alone is not a verdict.

## 10. Invariant register

| ID | Property | Components/entry points | Trust assumptions | Planned test type |
|---|---|---|---|---|
| INV-01 | | | | unit/fuzz/invariant/differential/fork |

At minimum consider solvency, conservation, authorization, coupled-state symmetry,
rounding direction, signature uniqueness/domain binding, lifecycle ordering,
external-state validation, supply/cap bounds, pause/recovery, and upgrade safety.

## 11. Deployment and live configuration

| Setting | Expected | Observed | Evidence block/commit | Security consequence |
|---|---|---|---|---|
| [required] | | | | |

Include implementation/admin/beacon, initialized state, roles, multisig threshold,
timelock, routers/pools/tokens, oracle feeds/decimals/heartbeat, caps, fees, pause
state, authorities, ownership transfers, and chain-specific configuration.

## 12. Unresolved gaps and blind spots

| Gap | Why unresolved | Affected components/invariants/passes | Materiality | Required resolution or accepted limitation |
|---|---|---|---|---|
| [required] | | | | | |

List missing project source, unavailable dependency versions, unverified runtime
code, build failures, inaccessible configuration, unresolved dependency
controllers/control overlap, undocumented actors, and scope exclusions.
`READY_WITH_LIMITATIONS` requires every limitation to appear here.

## 13. Auditor routing notes

List protocol types and applicable specialist routes, then suspicious observations
without declaring findings.

| Route/tag | Why applicable | Highest-risk components/flows/invariants |
|---|---|---|
| general EVM | | |

Do not assign severity or claim exploitability in the map.
