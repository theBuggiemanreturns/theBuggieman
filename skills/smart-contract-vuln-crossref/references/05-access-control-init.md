# 05 — Access control, initialization & privilege escalation

## ACC-01 — Frontrunnable `initialize()` on a proxy/implementation
**Root cause.** A clone or proxy is deployed, then `initialize()` is
called in a *separate* transaction (rather than atomically at deploy), and
anyone can call it first with malicious parameters — e.g. becoming the
owner, or minting to themselves before the real owner sets `implementation`
back to a safe value.
**Precedents.** `SpiritToken::initialize()` H-1 (Spirit Protocol, Critical)
— frontrunnable init let an attacker mint free tokens then reset the
implementation to `address(0)`. `BoldToken::initialize()` M-1 (Nerite) —
same shape, rated Medium because the practical blast radius (mitigable via
same-tx deployment scripts) was smaller. **Wormhole — $10M (February
2022):** the Solana bridge's implementation account was never properly
locked down; an attacker called the guardian-set initialization function
directly on the implementation, became the guardian-set owner, then
forged a message minting 120,000 wETH with no backing collateral. This is
the field's canonical example of this exact bug class — cite it when the
severity needs a concrete, undisputed real-money anchor.
**Detection.** Deploy script / factory pattern review: is `initialize()`
guaranteed to be called in the *same transaction* as deployment (e.g. via
a factory that deploys-then-initializes atomically), or can a clone exist
on-chain, uninitialized, for even one block?

## ACC-02 — Missing `_disableInitializers()` in the implementation constructor
**Root cause.** The upgradeable *implementation* contract (not the proxy)
can itself be initialized by anyone, since its constructor doesn't call
`_disableInitializers()`. Usually low-impact (the implementation holds no
real funds) but occasionally chains into something worse (self-destruct,
delegatecall abuse) — always check what the implementation *can* do if
initialized standalone before rating this Informational vs Low.
**Precedents (epidemic — appears 10+ times independently).** `PCLBaseSwapInside`
(Clip Finance), `BasicVaultFactory`/vaults (Mitosis), `StandardIDOPool`
(Blast IDO Pools I-3), Vertex (3S-Vertex-M01), `Ostium` (multiple), and
more. Treat this as a mechanical grep-and-check across every upgradeable
contract in scope rather than something to hunt case-by-case.
**Higher-stakes variant — shared library, not just a single implementation:**
Parity — $150M frozen (2017). A shared *library* contract (used by many
wallets via `delegatecall`, not a single proxy's implementation) had no
access control on its own init-equivalent function. An attacker called it
directly, became its owner, then triggered its self-destruct — bricking
every wallet that delegatecalled into that now-empty library address,
permanently. The lesson beyond "add the check": when the uninitialized
contract is a *shared* library rather than one proxy's own implementation,
the blast radius is every consumer of that library, not just one system —
weight severity accordingly, and check whether the codebase under review
has any shared-library-via-delegatecall pattern at all before assuming
this is a single-contract-scoped bug.
**Detection.** `grep -rn "constructor" **/*.sol` on every contract that
inherits an `*Upgradeable` OZ base or uses `Initializable`; confirm
`_disableInitializers()` (or equivalent) is present. Separately, grep for
`delegatecall` and identify every contract reached that way — each one
needs the same check independent of whether it's called a "library," an
"implementation," or a "logic contract" in the codebase's own naming.

## ACC-03 — Sensitive function missing caller authorization entirely
**Root cause.** A function that should be restricted (burn, admin
transfer, payment execution) has no modifier and no internal check at all
— not a subtly wrong check, just absent.
**Precedents.** `deTokenize()` (Critical, MetaZero Omnichain NFTs) — anyone
could burn anyone else's NFT. `send()` (Critical, same report) — no
owner/approval check before moving an NFT cross-chain. `Payment::payWithERC20`
(Critical, Crestal Network) — any address that had approved the
`BlueprintV5` contract for ERC20 spend could be drained by anyone calling
through this path.
**Detection.** This is the "read every public/external function and ask
who is allowed to call it, then check the code actually enforces that"
exercise — the single highest-value, lowest-tech thing to do on new code.
Pay special attention to functions whose name implies internal-only use
but which are `public`/`external`. **Specifically, read every function in
a related family together, not one at a time:** if `vote()` carries
`onlyNewEpoch`, does `reset()`? Does `poke()`? A missing modifier on the
one sibling nobody thought to re-check is a recurring, high-value shape —
attributed by the source material as a very large share of Critical
access-control findings, worth checking explicitly and by name rather
than trusting a per-function read-through to surface it. Precedent:
`poke()` missing an `onlyNewEpoch`-equivalent guard that its siblings
`vote()`/`reset()` both had, leading to uncapped inflation of a reward
token. See `INC-01` (file 17) for the same technique generalized beyond
just authorization checks to any state change or transfer.

## ACC-04 — Counterfactual/precomputed address takeover
**Root cause.** A protocol lets a user's smart-account/wallet address be
computed and referenced (e.g. for gasless onboarding) before it's actually
deployed. If nothing binds "the address" to "control of the eventual
contract," an attacker can claim/use the address for something before the
legitimate owner deploys to it.
**Precedents.** Biconomy H-03 — attacker could gain control of a
counterfactual wallet via `SmartAccountFactory.getAddressForCounterfactualWallet`.
**Detection.** Any "counterfactual"/"precompute address"/"CREATE2 before
deploy" pattern: verify the deployment step itself, not merely knowledge
of the address, is what grants control.

## ACC-05 — Admin can silently override an economic invariant outside its own timelock
**Root cause.** A parameter is nominally protected by a timelock/interval
(e.g. "multiplier only updates every N hours"), but a *different* admin
function can change the same effective value immediately, bypassing the
intended delay.
**Precedents.** `MultiplierContract::proposeMultipleUpdates()` H-1 (Blast
IDO Pools, Critical) — updated `maxLevel` without going through
`UPDATE_INTERVAL`, affecting `getMultiplier()` immediately.
**Detection.** Wherever a report/marketing claim says "parameter X changes
gradually / is timelocked," find *every* code path that can influence X's
effective value and check each one is actually gated the same way.

## ACC-06 — Existence check performed where an ownership/authorization check was required
**Root cause.** A function calls something that confirms a token/account
*exists* (or resolves without reverting) and treats that as proof the
caller is *authorized* to act on it — two different questions that read
similarly at a glance, especially when the existence-check helper's name
doesn't make the distinction obvious.
```solidity
function split(uint256 tokenId, uint256 amount) external {
    _requireOwned(tokenId);       // confirms the token EXISTS — not that msg.sender owns it
    _burn(tokenId);
    _mint(msg.sender, amount);    // attacker burns someone else's token, mints value to themselves
}
```
**Precedent.** ZeroLend — `split()` used an existence check
(`_requireOwned`-style) instead of an ownership/approval check, letting
an attacker burn another user's token and mint themselves the resulting
value. Rated Critical.
**Detection.** For every function gating on a helper whose job is
ambiguous from its name alone (`_requireOwned`, `exists`, `_checkX`),
read what it *actually* checks, not what its name implies — specifically
distinguish "this ID/account exists in storage" from "msg.sender is
authorized to act on this specific ID/account." This is a variant of
`ACC-03` (missing authorization) worth tracking separately because the
fix isn't "add a check," it's "replace the wrong check" — a code reviewer
skimming for the *presence* of a check will miss this every time.

## Cross-references
`SMELL-02` (Ownable vs Ownable2Step) and `SMELL-07` (missing zero-address
checks) are the lower-severity siblings of this category — check those
too since they compound with anything here. `INC-01`/`INC-03` (file 17)
generalize the "read the whole function family together" technique
beyond authorization to any state change. `AMM-09`/`RUG-*` (files 01, 19)
are the token-authority-retention variant of "a privileged lever that
should have been closed wasn't."
