# Target Selection & Pre-Dive Triage

**Where this sits:** before `contract-mapping` runs. Auditing assumes a target has
already been chosen and mapped; nothing upstream of it decides *whether* a target
is worth mapping in the first place. This file is that missing decision layer.
Source: `smart-contract-bug-hunting` step 1 + `23-web3-smart-contracts.md` kill-signal
matrix.

## Ground rule, always

This is whitehat work. Every step below assumes: (1) the target has a bug bounty
program or you have a direct legitimate disclosure channel, (2) all testing happens
on a local fork or testnet — never mainnet, never real user funds, and (3) findings
are reported privately first, never disclosed publicly before a fix ships.

## Judgment-based prioritization (from bug-hunting)

- **Disclosure path exists** — check Immunefi, HackerOne, Cantina, or the project's
  own `SECURITY.md`. No formal program doesn't mean no path, but it changes
  expectations around payment.
- **Funds at risk** — higher TVL means higher payout but also more prior scrutiny.
  Freshly launched or recently forked protocols are frequently under-audited
  relative to their TVL.
- **Code maturity** — has it been audited, and by whom? Read the audit report
  first. It tells you what was *already* checked (don't waste time there) and
  often what was flagged "out of scope" or "accepted risk" — assumptions accepted
  at audit time sometimes stop holding later.
- **Forked / composed code is a rich target class.** The bug is rarely in the
  borrowed code — it's in the seams where the team wrote custom logic to connect
  two systems (see: hood.fun's bug wasn't in Uniswap v3, it was in the custom
  migrator that assumed a fresh pool).

## DeFi Protocol — kill signals (skip if any apply)

- TVL < $500K → max payout capped too low for the effort
- 2+ top-tier audits (Halborn, Trail of Bits, Cyfrin, OpenZeppelin) on the
  **current version** → ROI too low unless you have deep protocol expertise and
  can review exactly what they explicitly excluded
- Protocol < 500 lines, single auth/control flow → minimal attack surface
- Payout formula: `max_realistic_payout = min(10% × TVL, program_cap)` → skip if
  this is < $10K

## DeFi Protocol — engagement scoring (engage if ≥ 6/10)

| Signal | Points |
|---|---|
| TVL > $10M | +2 |
| Immunefi Critical tier ≥ $50K | +2 |
| No top-tier audit on current version | +2 |
| < 30 days since deploy | +1 |
| Protocol you've hunted before | +1 |
| Source code + natspec comments available | +1 |
| Upgradeable proxies present | +1 |

## Token / Meme Coin — hard kills (skip immediately)

- Contract not verified on Etherscan/Solscan
- Deployer wallet has history of rug pulls
- Mint authority retained (Solana) with no cap → infinite mint
- Freeze authority retained (Solana) on meme coin → unilateral freeze/honeypot authority remains
- Transfer hook present (Token-2022) with mutable hook program
- Permanent delegate extension (Token-2022) → that delegate can steal all holder tokens

## Token / Meme Coin — soft kills (proceed with extreme caution)

- Top holder > 20% of supply (excluding DEX pools)
- LP not burned or locked in a verified contract
- Contract is upgradeable/proxy with retained admin
- < $5K liquidity in pool

## Token / Meme Coin — 6-question pre-investment fast filter

1. Mint authority null?
2. Freeze authority null?
3. Update authority null (metadata immutability)?
4. LP locked in verified contract for > 6 months?
5. Top 10 holders < 30% (excluding pools/burn addresses)?
6. Bonding curve completed AND post-completion mint authority null?

Five "No"s = walk away. Three "No"s = high risk.

## Handoff

Once a target clears triage, hand off to `contract-mapping` to produce
`protocol-map.md`, then run `smart-contract-auditing` against it.
