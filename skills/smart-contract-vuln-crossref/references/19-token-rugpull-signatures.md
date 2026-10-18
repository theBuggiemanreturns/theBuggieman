# 19 — Token / meme-coin rug-pull patterns (EVM + Solana)

Different domain from files 01–17: those cover *protocol logic* bugs in
contracts the team is trying to get right. This file covers *token
contracts as adversarial artifacts* — the question isn't "did the
developer make a mistake," it's "does the developer retain a privileged
lever, and will they pull it." Every pattern below reduces to: find the
privileged operation (mint, freeze, fee-set, LP-move, authority), then
check whether it's actually gone, not just claimed to be gone.

*Source note:* the same caveat as file 15 applies — frequency claims
below ("35% of meme coin rugs," "confirmed rug signal") are attributed to
the source material, not independently verified here.

## RUG-01 — Hidden mint / unlimited supply retained post-launch
**Root cause.** A mint function (or an unprotected internal `_mint`
call reachable from an external one) survives past launch, letting the
deployer inflate supply and dump on liquidity later.
**Detection.** EVM: `grep -rn "function mint\|_mint(" src/` and confirm
either the function is removed entirely post-launch or every path enforces
a genuine, already-reached `MAX_SUPPLY`. Solana: check `mint_authority`
on-chain (not just in source) via `spl-token display <MINT>` — should
read "(not set)".
**Closes as:** `MIT`-checklist row 1 in file 18, when authority is
verifiably null on-chain.

## RUG-02 — Honeypot / asymmetric transfer restriction
**Root cause.** Buys succeed (they have to, or the token gets no
traction); sells from ordinary holders fail or are taxed at a
crippling rate, while the deployer's own wallet can still sell freely.
**Detection matrix (do all four, the asymmetry is the signal):**
| Test | Honeypot signal |
|---|---|
| Buy from a random wallet | Succeeds |
| Transfer to a second random wallet | Often fails |
| Sell from the original wallet | Fails, or >50% effective tax |
| Sell from a team-controlled wallet | Succeeds |
Solana-specific: a `TransferHook` extension with a mutable authority, or
a `PermanentDelegate` extension, are structural honeypot/theft primitives
regardless of what the visible transfer function does — check Token-2022
extensions directly (`spl-token display <MINT> --program-id
TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`), not just the SPL base
token behavior.

## RUG-03 — Fee manipulation (sell fee raised sharply after initial buys)
**Root cause.** A fee setter has no enforced ceiling, or the ceiling is
high enough to be economically equivalent to none (e.g. 99%).
**Detection.** `grep -rn "function set.*Fee"` and check for a
`require(fee <= MAX_FEE)` with a genuinely low `MAX_FEE` (single digits
percent, not "under 100%").

## RUG-04 — Liquidity pool drain via migration/removal/pair-reset function
**Root cause.** An owner-callable function can pull LP, redirect the
trading pair, or otherwise separate holders from the liquidity backing
their tokens.
**Detection.** `grep -rn "migrateLP\|emergencyWithdraw\|setPair\|setRouter"`.
Verify LP lock claims on-chain, not from a badge: actual unlock
timestamp, actual lock-contract owner, and whether the locker contract
itself permits shortening the lock — some forked locker contracts add a
shortening/extension backdoor the UI never surfaces.

## RUG-05 — Bonding curve parameters or graduation not immutable/permissionless
**Root cause.** Curve parameters can be changed by an admin after launch,
or "graduation" to a public AMM requires a privileged call rather than
being automatic once a target is hit — either gives an insider a lever
ordinary participants don't have.
**Cross-reference.** This is the token-authority framing of the same
lifecycle-boundary idea as `AMM-09` (privileged authority retained past a
graduation event) in file 01 — `AMM-09` is scoped to the *launchpad
contract's* behavior at graduation; `RUG-05`/`RUG-06` are scoped to the
*token's own* authority state at the same moment. Check both when
reviewing a bonding-curve launch.

## RUG-06 — Solana authority retention (mint / freeze / update / close / transfer-hook / permanent-delegate)
**Root cause.** Any of a Solana SPL/Token-2022 mint's authorities left
set instead of nulled is a retained privileged lever specific to that
authority: mint → inflate supply, freeze → honeypot any holder, update →
rewrite metadata/mutate extensions, close → reclaim the account,
transfer-hook/permanent-delegate → intercept or directly move any
holder's tokens.
**Precedent.** pump.fun-launched tokens that retain mint authority past
bonding-curve graduation are a named, recurring instance of this — common
enough that automated checkers (rugcheck.xyz, per the source material)
now flag retained post-graduation mint authority as a confirmed signal on
its own.
**Detection (on-chain, no source needed):**
```bash
solana account <MINT> --output json | python3 -c "
import json,sys
d=json.load(sys.stdin)
info=d.get('account',{}).get('data',{}).get('parsed',{}).get('info',{})
print('mint_authority:', info.get('mintAuthority'))
print('freeze_authority:', info.get('freezeAuthority'))
"
```
Both should print `None`/null for a token with this axis closed.

## RUG-07 — Fake renounce / hidden ownership
**Root cause.** `owner()` reads as null or a burn address, but a second,
undocumented privileged role (a "shadow admin," a hardcoded backup
address, or a `selfdestruct`-and-redeploy path) retains equivalent
control.
**Detection.** `grep -rn "renounceOwnership.*override\|_shadowAdmin\|_backupOwner\|selfdestruct"`.
A renounce that's genuinely complete has *no* override that reintroduces
privilege and no second role with equivalent power — verify by reading
every function gated by *any* role, not just the one named `owner`.

## RUG-08 — Contract designed to be maximally sandwichable
**Root cause.** An auto-swap/rebase mechanism triggers trades with zero
slippage protection by construction (not by oversight — e.g. a
`swapExactTokensForETH(..., 0, ...)` call baked into every transfer),
making every holder's transaction a predictable MEV target the deployer
(or an affiliated searcher) can extract from systematically.
**Detection.** `grep -rn "swapExactTokensForETH" -A5` and check the
`amountOutMin` argument is a literal `0`; separately check for
rebase/mandatory-pool mechanics that force trades on every transfer
regardless of the holder's intent.

## Cross-references
File 18's "Token / meme-coin" table is the closed-signature version of
every pattern in this file — use it for Step 5 positive controls once
you've checked an axis and found it genuinely closed.
