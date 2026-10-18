# 13 — Centralization & trust assumptions

These are not "bugs" in the sense of broken code — the code does exactly
what it says. They're findings about *what power the design hands to
whom*, and they belong in every report because they're what separates "the
code is correct" from "the code is safe to depend on." Rate them
Informational/trust unless the protocol has publicly promised otherwise
(e.g. "fees are immutable once set" — then the same code fact becomes a
real severity finding, see `TRU-01`).

## TRU-01 — Admin can redirect fee/reward recipient for existing, already-earned positions
**Root cause.** A `setRewardRecipient()`-style admin function applies to
positions that already exist and have already accrued value, not just to
future configuration.
**Precedents.** hood.fun-adjacent launchpad review corpus and, generically,
`setRewardRecipient()` (LaunchHood V3 I-01) — factory owner can redirect a
creator's fee share for any already-registered position. Documented in
the code, so a trust/centralization property rather than a hidden
access-control bug — **but flag explicitly if the protocol's marketing or
docs promise immutable/creator-owned fees**, since that turns this into a
real discrepancy between claimed and actual behavior.
**Fix (if immutability is promised).** Remove the power, or gate it behind
the affected creator's consent plus a timelock.

## TRU-02 — `renounceOwnership()` left enabled where it would brick the protocol
**Root cause.** Contracts inheriting `Ownable`/`Ownable2Step` default to
allowing the owner to renounce, setting the owner to `address(0)`. If any
critical function is `onlyOwner`-gated with no other recovery path, an
accidental (or malicious-insider) renounce permanently bricks that
function.
**Precedents.** Recurring across many audits, e.g. Mitosis L-01
(`StrategyExecutor` can remain permanently paused if owner renounces while
paused), Ostium Registry L-10, and others.
**Fix.** Override `renounceOwnership()` to revert if the protocol never
intends to use it.

## TRU-03 — Single-step ownership/config transfer with no timelock on critical params
**Root cause.** `Ownable` (single-step transfer) is used instead of
`Ownable2Step` for a role that controls economically significant
parameters, so a typo'd `transferOwnership()` call permanently loses
control, and/or sensitive parameter changes take effect with no delay for
users to react.
**Precedents.** Recurs constantly across the corpus (see `SMELL-02`) —
material enough to warrant a project-wide finding rather than repeating it
per-contract in a report.

## TRU-04 — Pending user transaction is not bound to the config/price the user reviewed
**Root cause.** A user signs/submits a transaction against currently-
displayed terms (price, fee, supply, limits), but the on-chain function
only takes an opaque config ID, not an expected-value hash or deadline —
so if an admin changes the underlying config between signature and
inclusion, the user's transaction executes against different terms than
they agreed to, with no revert.
**Precedents.** `launchToken()` L-03 (LaunchHood V3) — configs are mutable
in place; the function accepts only a config ID, no `expectedConfigHash`,
`expectedLaunchFee`, or `deadline`. Requires an admin action to trigger, so
not unauthenticated, but a real mainnet transaction-consent problem.
**Fix.** Make economically significant configs append-only (never mutate
in place — publish a new config instead), and/or add
`expectedConfigHash`/`deadline` parameters that the function checks
against live state before executing.

## Cross-references
Always report `TRU-*` findings even when nothing else is found — see
`Cucumberr`'s clean audit in the source corpus, which still explicitly
logged a liveness/incentive centralization note (nobody is paid to call
`graduate()`) despite finding zero exploitable bugs. A "no vulnerabilities
found" report that skips the trust-assumptions section is incomplete.
