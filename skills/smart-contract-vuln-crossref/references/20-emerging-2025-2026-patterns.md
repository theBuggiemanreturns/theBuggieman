# 20 — Emerging 2025–2026 protocol-level patterns

Newer EVM features create new variants of already-known bug shapes rather
than genuinely new bug classes — worth checking explicitly on any recently
deployed contract, since these features are new enough that most audit
checklists (including most of files 01–17) predate them.

## EMG-01 — EIP-1153 transient storage reads stale value across an external call
**Root cause.** `tstore`/`tload` (transient storage, live in Ethereum's
Pectra upgrade) persists only within one transaction, resetting between
transactions — but *within* a transaction, a value cached via `tload`
before an external call can go stale exactly the way a persistent-storage
read can, if the external call re-enters and changes the transient value
in between. This is a reentrancy variant (see file 04), not a new root
cause, but it's easy to miss because transient storage doesn't yet
pattern-match to "storage" in most reviewers' mental model of where
reentrancy risk lives.
**Detection.** `grep -rn "tstore\|tload"`; for every `tload`, check
whether an external call happens between that read and its use, the same
way you would for a persistent-storage read in a `REN-01`-style check.

## EMG-02 — EIP-7702 EOA delegation replay
**Root cause.** EIP-7702 (Pectra) lets an EOA delegate its code to a
contract implementation via a signed authorization. If the delegation
authorization can be replayed — reused across chains, reused after the
user intended to revoke it, or not scoped tightly enough to a specific
implementation/nonce — an attacker can redirect a previously-delegating
EOA's code to an attacker-controlled contract. Structurally this is
`SIG-02` (missing replay protection) applied to a new, higher-stakes
target: successful replay here doesn't just misuse one signed action, it
takes over the account's code.
**Detection.** `grep -rn "setCode\|DELEGATION_MAGIC"`; confirm the
delegation authorization is scoped with the same rigor file 06 requires
of any signed action — nonce, chain ID, and an explicit target
implementation, not just "a signature exists."

## EMG-03 — ERC-4337 paymaster abuse via missing sender allowlist
**Root cause.** A paymaster contract that sponsors gas for user
operations without strictly validating who it will sponsor (or without a
spending cap) can be drained on the first call by anyone submitting a
UserOperation through it — structurally `ACC-03` (missing authorization)
applied to gas sponsorship specifically. Bundler-level griefing (wasting
a bundler's simulation/execution effort without paying) is a related but
distinct DoS-flavored variant.
**Detection.** `grep -rn "validatePaymasterUserOp"`; confirm strict
sender/allowlist validation and a real spending cap, not just a signature
check that anyone with a valid-looking UserOperation can satisfy.

## EMG-04 — LST/LRT depeg breaks a 1:1-peg assumption under loss conditions
**Root cause.** Code that integrates a liquid-staking or liquid-restaking
token (stETH, rETH, wstETH, cbETH, sfrxETH, and their restaking
equivalents) assumes it trades 1:1 with the underlying asset. Under a
genuine depeg (slashing event, market stress, redemption-queue backup),
the oracle or exchange-rate source the protocol relies on may still
assume the peg while the actual tradeable market price has moved,
breaking liquidation and collateral-valuation logic built on the
assumption.
**Detection.** `grep -rn "stETH\|rETH\|wstETH\|cbETH\|sfrxETH"`; for
every integration point, check whether the exchange rate used is the
protocol's own redemption rate (which can lag or ignore market depeg) or
an actual market price, and whether liquidation logic has any explicit
handling for the two diverging. Cross-reference `ORC-01` (instantaneous
rate used as price) — an LST/LRT exchange rate is a specific, currently
very live instance of that general pattern.

## Cross-references
None of these four are new root causes — `EMG-01`→`REN-01`/`REN-03`,
`EMG-02`→`SIG-02`, `EMG-03`→`ACC-03`, `EMG-04`→`ORC-01`. This file exists
because the *surface* is new enough (Pectra-era EVM features, current
account-abstraction adoption) that pattern-matching to the underlying
file 04/06/05/02 entry isn't always obvious on sight — check this file
first on any contract using these features, then go read the underlying
mechanism file for the full detection checklist and fix pattern.
