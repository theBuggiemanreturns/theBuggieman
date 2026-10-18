# 01 — AMM pool creation / graduation / migration squatting

This is the single best-documented bug family in the source corpus: four
independent write-ups (`hood.fun` [Critical, live-exploitable], `Openfair`
[High], `LaunchHood V3` [Medium residual], `Cucumberr` [not exploitable —
clean design]) all review the *same* moment in a launchpad's lifecycle —
the point where curve/raised funds get deposited into a public AMM pool —
and land at four different points on a maturity ladder. Read this file
whenever an audit target has a bonding curve, fair-launch, IDO, or any
function that creates/seeds/migrates into a Uniswap-style pool.

## The maturity ladder (check every rung, in order)

A launchpad is only as safe as its weakest rung. All four rungs must hold:

| Rung | Question | Failing example |
|---|---|---|
| 1. Can the pool be squatted before the app touches it? | Is pool creation/initialization permissionless, and does the app treat "already initialized" as trusted? | `hood.fun`, `Openfair` — yes, both let `createAndInitializePoolIfNecessary` silently no-op onto an attacker's price |
| 2. If squatted, does minting still protect itself? | Does the mint enforce `amount0Min`/`amount1Min`, or check `slot0()` against the intended price before minting? | `hood.fun`, `Openfair` — `amount0Min: 0, amount1Min: 0`, no equality/tolerance check |
| 3. Can an attacker fund the *token* side of a squatted pool to fake a two-sided price? | Is the token transfer-locked to/from everyone except the launch contract until graduation? | `Cucumberr` — yes, locked, which is why its squat is unprofitable even though pool creation is still permissionless |
| 4. Even with 1–3 fixed, is the *address* of the future pool predictable early enough to grief? | Is the token/pool address deterministic from public inputs (creator + salt) well before the transaction that uses it lands? | `LaunchHood V3` — yes; tick-equality check (rung 2) closes the theft, but a watcher can still win the race and force reverts (liveness DoS, not theft) |

A launchpad that only fixes rung 2 (slippage bounds) but not rung 1 (price
equality/rejection) is *still* vulnerable to loss, because a wrong price
within "acceptable slippage" of nothing is not the same as validating
against the *intended* price — see `AMM-01` vs `AMM-02` below, they are
independent controls and both are required.

## AMM-01 — Permissionless pool pre-initialization sets attacker price

**Root cause.** Uniswap v3's `createAndInitializePoolIfNecessary(...)` only
sets `sqrtPriceX96` if the pool does not yet exist (confirmed against the
deployed `PositionManager`'s `PoolInitializer.sol`: the initialize branch is
skipped once `sqrtPriceX96Existing != 0`). Pool creation and initialization
require no token balance — only gas — so anyone watching the mempool for a
soon-to-launch token address can win the race for one gas fee.

**Detection checklist.**
- Grep for `createAndInitializePoolIfNecessary`, `createPool(`, or any
  factory `getPool` → `createPool` → `initialize` sequence.
- Ask: after that call, does the code ever compare the *actual* resulting
  `slot0().sqrtPriceX96` (or `tick`) against the price the protocol
  intended, and revert/handle a mismatch? If the only check is "pool
  exists, proceed," that's a squat waiting to happen.
- Check both dual-sided *and* single-sided listing code paths separately —
  `Openfair`'s single-sided path read `slot0()` only to pick a tick range,
  which still trusts the attacker's price rather than rejecting it.

**Precedents (paraphrased from the reports).**
- `hood.fun` (Critical, live/verified on fork): migrator skipped its own
  price because the pool was already initialized; minted the full raise
  into the attacker's pool with zero slippage protection. Two PoC variants
  were demonstrated: permanent loss of ~100% of a graduation's ETH (funds
  stranded, no rescue function), and direct theft (attacker pre-buys
  cheap, dumps into the pool the protocol just filled, nets the raise).
- `Openfair` (High, verified statically + local PoC): identical root cause
  in `OpenLaunch.graduate()` and `LaunchFactory._seedAndLockPool`, plus a
  single-sided listing path that inherits the same trust gap. Rated High
  rather than Critical because each squat only threatens one launch's
  raise (bounded to that token's ~5 ETH curve target), not the whole
  protocol in one transaction.
- Related, different mechanism, same family: `AMM-06` below (Uniswap v4
  single-sided range init frontrun) and `ORC-01` (donation attacks on
  vault/rate-based price oracles) are the same "attacker sets the number
  the protocol will trust next" idea applied to a mint tick and a share
  rate respectively.

**Fix pattern (from the reports' recommendations, converge on all of):**
1. After creation, require `slot0().sqrtPriceX96` (not just `tick`) equals
   the intended price within a tight tolerance; revert otherwise.
2. Reject-and-halt is not enough on its own — pair it with a way forward
   (see `AMM-08`), or the fix just converts theft into permanent DoS.
3. Prefer deriving the pool's price from real reserves computed at
   execution time, not a value computed earlier and now stale.

## AMM-02 — Zero-slippage LP mint

**Root cause.** `nfpm.mint(... amount0Min: 0, amount1Min: 0 ...)` means no
on-chain price, however wrong, can make the mint itself revert.

**Detection checklist.** Grep every `mint(`/`addLiquidity(` call against a
position manager or router; confirm `amount0Min`/`amount1Min` (or
`amountAMin`/`amountBMin` on v2-style routers) are non-zero and derived
from the *desired* amounts with a real tolerance (e.g. 99%), not `0` or a
placeholder.

**Precedents.** `hood.fun`, `Openfair` — both. `Cucumberr`'s Uniswap v2
`mint()` is balance-based rather than min-out based, and is protected by
`AMM-03`'s token transfer-lock (rung 3) instead — a legitimate alternative
control, but only because rung 3 holds; don't assume "V2 uses a different
formula" is itself a fix.

## AMM-03 — Balance-based first-mint donation/inflation

**Root cause.** Uniswap v2 style `mint()` computes
`liquidity = sqrt(balance0 * balance1) - MINIMUM_LIQUIDITY` on the first
mint. If an attacker can get token balance into the pair before the
protocol's own liquidity add, they can manipulate this ratio.

**Detection checklist.** For V2-style graduation/seeding, check whether the
*launch token* itself can reach the pair contract before the protocol's
own add-liquidity call — via direct transfer, via any public mint/claim
path, or via the token's own transfer function if it isn't gated.

**Precedents.** `Cucumberr` (verified clean): the launch token's
`_update()` reverts any transfer where neither party is the launchpad
contract itself, for as long as `isUnlocked[token] == false`. A WETH-only
donation still skews the pair's *price* once the protocol mints (because
the pair ends up over-collateralized in WETH relative to the intended
curve price), but produces `sqrt(0 * balanceWETH) = 0` liquidity to the
attacker and the resulting LP goes to a burn address, not the attacker —
so the donation is pure economic self-harm for the attacker, not a theft
vector. **Still flag the WETH-only griefing as a low/informational
finding** — it can visibly mis-set a launch's opening price even though it
can't be profitably exploited.

## AMM-04 — Predictable pre-deploy address enables squat/DoS even after price checks are fixed

**Root cause.** If the token (and therefore the pool) address is
deterministically computable from public inputs (creator address + a
user- or sequentially-chosen salt) before the launch transaction lands, a
watcher can win the initialization race even when `AMM-01`'s price-equality
check is correctly implemented. The theft is closed, but the watcher can
now force the legitimate transaction to revert every single time, forever,
for the cost of gas — a repeatable liveness/DoS + gas-griefing issue
against the actual creator.

**Precedents.** `LaunchHood V3` (Medium, confirmed by code reachability):
this is exactly the state the protocol was in — the theft class from
`hood.fun`/`Openfair` was fixed via an intended-tick equality check, but
because `predictTokenAddress()` is public and deterministic, an attacker
can still pre-initialize the future pool at the "wrong" price and force
`PoolAlreadyInitializedAtWrongPrice()` reverts indefinitely. Recommended
mitigations (use more than one): make the final salt depend on
execution-time entropy so it isn't known pre-inclusion; fall back to
another un-squatted address in the same transaction instead of reverting;
check pool existence before doing the expensive clone/init work, to at
least cut the creator's wasted gas; route mainnet launches through private
order flow so the salt isn't exposed pre-inclusion.

**Why this still matters even after AMM-01/AMM-02 are fixed:** treat
"predictable address + permissionless pool creation" as its own finding
independent of whether the price-validation and slippage controls are
present. Grading rule of thumb used across these reports: if rung 1/2 are
broken → Critical/High (theft or full loss); if only rung 4 is broken →
Medium (liveness/gas-griefing, no fund loss).

## AMM-05 / AMM-06 — Single-sided listings and v4-style range squats

**AMM-05.** A single-sided listing path that reads the *existing* pool's
tick to decide its own liquidity range inherits whatever price an attacker
already set — reading `slot0()` for tick math is not the same as
validating it. Treat any code that says "align to current tick" as needing
the exact same price-equality check as `AMM-01`, not an exemption from it.

**AMM-06.** A related but mechanically different variant found in the
findings corpus (not from the four reports): a factory mints a
single-sided Uniswap v4 position "from the current tick to the max tick,"
meaning the effective floor price is whatever tick a frontrunner leaves
the pool at immediately before the mint — buyers can then acquire the
child token for as little as that tick's price. Same family: attacker
controls a number (here, a tick boundary) the protocol trusts without
independently deriving or bounding it.

## AMM-07 — Transfer-lock is necessary but not sufficient

Don't credit a transfer-lock (`isUnlocked` / "no transfers except to/from
the launch contract") as closing `AMM-01` — it only closes `AMM-03` (the
attacker can't fake the *token* side of the pool). It does nothing against
pool *price* squatting, because Uniswap v3 pool initialization requires no
token balance at all (`hood.fun`'s report calls this out explicitly: the
transfer-lock exists specifically to stop the four.meme-style "park tokens
in a pre-made pool" attack, and is irrelevant to a pure price-initialize
squat). Always evaluate transfer-lock and price-validation as two
independent controls.

## AMM-08 — No rescue/re-migration path once funds are stuck

**Root cause.** Once a squat causes a revert-on-mismatch design, or once a
naive design deposits into a mispriced pool, is there *any* function that
lets an owner or the affected creator recover stranded value? `hood.fun`'s
migrator had none — flagged explicitly as defense-in-depth even in the fix
recommendations, since a revert-based fix (from `AMM-01`) introduces a new
DoS surface that a rescue path can mitigate.

**Detection checklist.** After adding a price-equality revert, check
whether the contract that received partial funds before reverting can
strand them (call ordering matters: does the revert unwind the whole
transaction, or can prior steps already have moved funds out
irreversibly?), and whether an owner-guarded sweep/rescue function exists
for genuinely stuck balances.

## AMM-09 — Privileged authority retained past the graduation/finalization event

**Root cause.** Distinct from `AMM-01`–`AMM-08`, which are all about price/
liquidity manipulation *at* graduation: this pattern is about a privileged
lever (most commonly token mint authority) that should be irrevocably
closed *at* graduation but is left open, letting an insider dilute or
dump against the pool the graduation event just seeded — after the price/
liquidity controls all did their job correctly.

**Precedent.** Multiple pump.fun-launched tokens retained Solana mint
authority after their bonding curve completed and graduated to a public
AMM. Legitimate launches null the mint authority immediately at
graduation; retaining it lets the deployer mint additional supply
post-graduation and dump it against the liquidity that just formed.
Common enough that automated checkers (rugcheck.xyz) now flag retained
post-graduation mint authority as a rug signal on its own.

**Detection.** For any bonding-curve/launchpad review, treat "what
happens to every privileged authority on the token at the exact moment of
graduation" as its own checklist item, separate from the pool-price
checks in `AMM-01`–`AMM-06`. See `references/19-token-rugpull-signatures.md`
(`RUG-05`, `RUG-06`) for the token-authority-specific detection
checklist, including the on-chain (source-independent) verification
command for Solana mint/freeze authorities.

## Cross-references
- `ORC-01`, `ORC-06` — same "attacker sets a number the protocol trusts"
  shape, applied to price oracles instead of pool initialization.
- `VLT-01` — ERC4626 inflation attack is the vault-share analogue of
  `AMM-03`.
- `TRU-04` — pending launch not bound to the config a user reviewed is a
  related but distinct issue seen in the same `LaunchHood V3` report
  (L-03): an admin changing launch parameters mid-flight, not an external
  attacker squatting a pool.
- `RUG-01`/`RUG-05`/`RUG-06` (file 19) — the token-authority side of
  `AMM-09`.
