# 18 — Already-mitigated signatures (Step 5 positive-control checklist)

`SKILL.md`'s Step 5 says to check a highest-stakes disproved hypothesis
against the KB and cite it as a confirmed, checked defense rather than
staying silent. This file is the concrete checklist that step points to.
Each row names the exact condition that has to hold — verify the
condition actually holds against the real source (read the code; don't
take a comment, a variable name, or a natspec claim's word for it),
then cite the pattern ID in your report as a checked-and-defended item.

## DeFi protocol

| If you see... | ...then this closed pattern | Cite as |
|---|---|---|
| `nonReentrant` (or equivalent) on **every** external-facing function that moves value — not just some of them | Reentrancy | `MIT-01`, closes `REN-01`–`REN-04` |
| Staleness check **AND** circuit breaker **AND** multi-source/TWAP agreement, all three present together | Oracle manipulation | `MIT-02`, closes `ORC-01`, `ORC-03`, `ORC-06` |
| `_disableInitializers()` present in **every** upgradeable implementation's constructor, not just the main one | Uninitialized-proxy takeover | `MIT-03`, closes `ACC-01`, `ACC-02` |
| Nonce **AND** `chainid` **AND** contract address all bound into the signed hash (not just one or two of the three) | Signature replay | `MIT-04`, closes `SIG-02` |
| A decimals offset / virtual-shares mechanism (e.g. OpenZeppelin 4.9+'s `_decimalsOffset()`) actually present and non-zero | ERC4626 first-depositor/inflation attack | `MIT-05`, closes `VLT-01` |

**Partial credit doesn't count.** Two out of three oracle controls, or a
`_disableInitializers()` on the proxy but not on a second implementation
contract used elsewhere in the same system, is *not* a closed finding —
it's a weaker version of the open one. Don't round up.

## Governance / centralization — a policy note, not a technical-mitigation note
`MIT-06`: a large multisig (>5 signers) with a long timelock (>48h) is
frequently treated by bounty programs (Immunefi's centralization-risk
policy is the cited example) as **out of scope for payout** when a
finding requires admin malice to exploit. That is a program-scope fact,
not a claim that the centralization risk doesn't exist. Don't let it
substitute for the `13-centralization-trust.md` writeup — a large
multisig+timelock is real risk mitigation against a *rushed unilateral*
admin action, but `TRU-01`–`TRU-04` (fee redirection, renounce foot-guns,
un-timelocked config, pending-tx not bound to reviewed terms) still apply
and still belong in a thorough report regardless of whether a specific
bounty program will pay for them. Read the actual program brief before
deciding whether to report a centralization finding *for a bounty*; keep
reporting it *in an audit*.

## Token / meme-coin

| If you see... | ...then this closed | Cite as |
|---|---|---|
| All authorities (mint, freeze, update/metadata, close) verifiably null on-chain — not just "the code has a renounce function," actually check the current on-chain value | No rug authority on this axis | `RUG-01`, `RUG-06`, `RUG-07` (LP concentration and holder concentration are separate axes — still check those) |
| LP locked in a verified locker contract, >6 months remaining, and the locker has no shortening/extension permission | LP-drain path | `RUG-04` |
| Honeypot checkers (honeypot.is, rugcheck.xyz) show clean **AND** a manual transfer simulation (buy → transfer to a second wallet → sell) has actually been run, not just the automated check alone | Honeypot on basic checks | `RUG-02` — still worth deeper testing before fully clearing, automated checkers miss novel restriction mechanisms |
| Token is established (>2 years), has an active ecosystem, and none of the above red flags are present | Rug-pull risk is de minimis on the classic axes | shift framing to a protocol-level audit (files 01–17) instead of a rug screen |

## Cross-references
Files 01–17 describe the open/vulnerable version of each pattern in this
checklist; this file only exists to name the closed version concretely
enough to cite. If a target only partially satisfies a row here, go read
the corresponding pattern file(s) and write it up as (still) open, not as
a weaker positive control.
