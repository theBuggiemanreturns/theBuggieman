---
name: smart-contract-vuln-crossref
description: Cross-reference independently generated smart-contract audit artifacts, findings, code behavior, or disproved high-risk hypotheses against a curated index of 107 consolidated patterns across 20 families derived from ~900 public audit findings, detailed disclosures, and named incidents. Use after smart-contract-auditing has stabilized its independent hypotheses, before finalizing audit coverage; also use for “has this happened before,” “known bug class,” precedent, positive-control, rug-pull/honeypot, or missed-pattern checks involving AMMs, oracles, ERC4626, reentrancy, access control, signatures, rounding, accounting desync, boundaries, incomplete paths, token behavior, DoS, cross-chain, liquidation, staking, governance, centralization, EIP-1153/7702/4337, or LST/LRT risk. Consume protocol-map.md plus audit ledgers, route newly surfaced candidates back through auditing proof/kill gates, and never treat similarity as proof or historical severity as the current severity.
---

# Smart-contract vulnerability cross-referencer

Use this skill as the fourth skill in the audit pipeline:

1. `onchain-recon` batches deployment/runtime evidence when needed.
2. `contract-mapping` produces `protocol-map.md`.
3. `smart-contract-auditing` generates and resolves hypotheses independently.
4. **This skill cross-references results and runs a map-driven completeness pass.**

The index contains 107 consolidated signatures, not 900 distinct patterns; its
source corpus reviewed roughly 900 findings. A match is a routing clue. It never
proves reachability, impact, exploitability, or severity.

Do not load this corpus before the auditor's independent hypothesis ledger is
stable. After that gate, use it both to contextualize existing candidates and to
check applicable high-risk families the map says should have been considered.
Any newly surfaced candidate returns to the auditing workflow for proof and
adversarial refutation.

## Contents

```
smart-contract-vuln-crossref/
├── SKILL.md                              <- you are here
├── pattern_index.json                    <- machine-readable index (20 categories, 107 patterns)
├── scripts/
│   └── search_patterns.py                <- keyword pre-filter over pattern_index.json
└── references/
    ├── 01-amm-pool-graduation-squatting.md  <- flagship deep dive (4 full disclosure reports)
    ├── 02-oracle-price-feeds.md
    ├── 03-erc4626-vaults.md
    ├── 04-reentrancy-cei.md
    ├── 05-access-control-init.md
    ├── 06-signatures-replay.md
    ├── 07-rounding-precision.md
    ├── 08-token-integration.md
    ├── 09-dos-griefing.md
    ├── 10-cross-chain-bridging.md
    ├── 11-liquidations-collateral.md
    ├── 12-governance-staking-rewards.md
    ├── 13-centralization-trust.md
    ├── 14-recurring-code-smells.md
    ├── 15-accounting-state-desync.md        <- phantom yield / fast-path skip / wrong-order update
    ├── 16-boundary-conditions-off-by-one.md
    ├── 17-incomplete-code-paths.md          <- function-family comparison test
    ├── 18-already-mitigated-signatures.md   <- the checklist Step 5 (below) points to
    ├── 19-token-rugpull-signatures.md       <- EVM + Solana meme-coin/rug-pull domain
    ├── 20-emerging-2025-2026-patterns.md    <- Pectra/EIP-1153/7702/4337/LST-depeg
    └── source-log.md                     <- provenance + how to extend the KB
```

## Required inputs

For a full pipeline run, require:

1. `protocol-map.md`;
2. `coverage.md`, `hypotheses.md`, and `tests.md`;
3. every draft confirmed finding;
4. exact source/evidence paths referenced by those artifacts.

For a one-off precedent check, accept a single finding or behavior description but
state that category completeness was not assessed.

Copy `references/crossref-template.md` to `cross-reference.md` and keep it
updated throughout the workflow.

## Workflow

### 1. Freeze the independent audit state

Record hashes/paths for the map and audit artifacts. Confirm the hypothesis ledger
already contains independently generated, disproved, confirmed, blocked, and open
candidates. Do not rewrite root causes to fit historical wording.

### 2. Cross-reference every audit candidate

For each confirmed, open, blocked, and materially disproved hypothesis, run:

```bash
python3 scripts/search_patterns.py "<root cause, broken invariant, entry point, and impact>"
python3 scripts/search_patterns.py --file path/to/finding.md
```

Read every strong/moderate matched reference in full and inspect adjacent families
named by its cross-references. For weak/no matches, choose the closest category
manually and record either a reasoned match or `NO_CLOSE_PRECEDENT`.

Record candidate ID, pattern ID(s), match strength, common mechanism, material
differences, precedent, fix guidance, and disposition. Preserve the auditor's own
severity analysis; historical labels are context only.

### 3. Run map-driven category coverage

Use the map's route tags, components, value flows, trust boundaries, and deployment
model to mark all 20 categories `applicable`, `not applicable` with evidence, or
`blocked`. Read the full reference for every applicable category.

Run `references/14-recurring-code-smells.md` as the cheap mechanical pass. Then
use each applicable reference's detection checklist against the mapped high-risk
components and invariants. This is a completeness check after independent review,
not permission to promote pattern resemblance into a finding.

Examples:

- AMM/launch/migration routes: CAT-01, CAT-02, CAT-06, CAT-07, CAT-15–17.
- Vault/lending routes: CAT-02–04, CAT-07–09, CAT-11, CAT-15–17.
- Proxy/role/signature routes: CAT-05–06, CAT-09, CAT-12–13, CAT-18.
- Bridge routes: CAT-04–10, CAT-15–17.
- Token/rug screening: CAT-05, CAT-07–08, CAT-13–14, CAT-18–20.

These are seeds, not exhaustive routing. Mark categories from actual map evidence.

### 4. Check positive controls

Spend source-level positive-control effort on disproved Critical/High-precedent
hypotheses and other load-bearing defenses. Read
`references/18-already-mitigated-signatures.md`, verify the exact defense in
source and deployed configuration, and cite the pattern ID plus evidence. A
modifier name or comment is not a positive control.

### 5. Loop new candidates back to auditing

Create a new hypothesis for every plausible missed pattern, set origin to
`crossref`, and return it to `smart-contract-auditing` for reachability,
preconditions, proof, kill tests, impact bounds, remediation, and severity. Record
the resulting audit hypothesis/finding ID in `cross-reference.md`.

Do not close cross-reference while a new candidate is merely “similar.” It must be
confirmed, disproved, accepted-risk, duplicate, or explicitly blocked.

### 6. Validate the handoff

Run:

```bash
python3 scripts/validate_crossref.py cross-reference.md
```

A complete result requires all 20 category rows, every audit candidate disposition,
positive controls for selected high-stakes defenses, all new candidates resolved
or bounded as limitations, and explicit no-match entries where the corpus has no
close precedent.

## Output contract

Return:

1. `cross-reference.md` and validator result;
2. candidate-to-pattern and category-coverage matrices;
3. positive-control evidence;
4. new audit hypothesis/finding IDs created by loopback;
5. corpus gaps and limitations.

## Category index

| # | File | Covers | Flagship severity range |
|---|---|---|---|
| 01 | `01-amm-pool-graduation-squatting.md` | Pool creation/graduation/migration squatting, zero-slippage LP mints, donation/inflation at first mint, predictable pre-deploy addresses | Critical → Medium |
| 02 | `02-oracle-price-feeds.md` | Manipulable/instantaneous rates used as price, wrong-denomination fallbacks, stale/future timestamps, spot-vs-TWAP misuse | Critical → Low |
| 03 | `03-erc4626-vaults.md` | Inflation attacks, missing withdraw slippage, max*() spec gaps, totalAssets() overstatement, favorable rounding | High → Low |
| 04 | `04-reentrancy-cei.md` | CEI violations, unvalidated flash-loan/callback callers, reentrant unlock/withdraw drains | Critical → Low |
| 05 | `05-access-control-init.md` | Frontrunnable initializers, missing `disableInitializers`, absent authorization checks, timelock bypasses | Critical → Informational |
| 06 | `06-signatures-replay.md` | Unsigned economically-relevant fields, missing nonce/replay protection, signature malleability, zero-address signer | High → Medium |
| 07 | `07-rounding-precision.md` | Exploitable favorable rounding, division-before-multiplication, decimal mismatches, truncation-locked dust | Critical → Low |
| 08 | `08-token-integration.md` | Fee-on-transfer/rebasing tokens, blacklistable stablecoins, missing SafeERC20, wrong native-wrapper per chain | High → Low |
| 09 | `09-dos-griefing.md` | Unbounded arrays, spammable queues, front-run-to-revert griefing, unbatched settlement | Critical → Low |
| 10 | `10-cross-chain-bridging.md` | Chain-fork replay, caller-controlled bridge payloads, non-atomic cross-chain state desync, LayerZero/CCIP gas griefing | Critical → Medium |
| 11 | `11-liquidations-collateral.md` | Liquidation math omitting bonus/fees, misrouted proceeds, unsocialized bad debt, inverted worst-of pricing | Critical → Medium |
| 12 | `12-governance-staking-rewards.md` | Reward-rate reset leaks, post-snapshot vote changes, delegation double-counting, claim front-running | Critical → Medium |
| 13 | `13-centralization-trust.md` | Admin fee redirection, renounceOwnership foot-guns, unbound-to-signed-terms transactions | Informational/trust |
| 14 | `14-recurring-code-smells.md` | The 8 highest-frequency Low/Info patterns — grep these first, batch the results | Low → Gas |
| 15 | `15-accounting-state-desync.md` | Phantom yield, fast-path-skips-update, wrong-order dependent calculations — two variables that must track together and don't | Critical → Medium |
| 16 | `16-boundary-conditions-off-by-one.md` | `>` vs `>=` at period/epoch/deadline/array/amount boundaries | High → Medium |
| 17 | `17-incomplete-code-paths.md` | Function-family comparison test; missing refund in an update/cancel sibling; alternate entry point bypasses validation | High → methodology |
| 18 | `18-already-mitigated-signatures.md` | Ready checklist for Step 5 — the exact condition that must hold for each closed DeFi and token/rug-pull pattern | verification-checklist |
| 19 | `19-token-rugpull-signatures.md` | **Different domain — token contracts as adversarial artifacts, not protocol logic.** Hidden mint, honeypot, fee manipulation, LP drain, bonding-curve authority retention, Solana Token-2022 extensions, fake renounce, sandwich-by-design | Critical → Medium |
| 20 | `20-emerging-2025-2026-patterns.md` | Pectra-era EVM features (transient storage, EIP-7702) and account abstraction (ERC-4337) — new surfaces for already-known root causes, plus LST/LRT depeg | Critical → High |

Files 01–17 assume the team is trying to get the logic right and you're
checking whether they did; file 19 assumes the token deployer may be
adversarial and you're checking what privileged levers they still hold.
Different mental model — don't reach for file 19's patterns on a protocol
audit, or file 01–17's on a rug screen, without first confirming which
kind of target you actually have.

## Notes on how this KB was built (read `references/source-log.md` for full detail)

- Every pattern is grounded in named, real precedents — protocol,
  approximate severity, and a one-line paraphrase — not invented examples.
  Findings are paraphrased, never quoted verbatim from source reports.
- Redundant near-duplicate findings (the same "missing `disableInitializers`"
  or "use `Ownable2Step`" nit appearing 5–15 times across different audits)
  were consolidated into single pattern entries in file 14, with frequency
  noted, instead of being repeated per source report.
- `01-amm-pool-graduation-squatting.md` is unusually deep because 4 full
  disclosure reports on the same bug family were available, at 4 different
  points on the same "maturity ladder" (live-exploited Critical → High →
  partially-fixed Medium → correctly fixed / no finding). Use it as the
  template for how to reason about a bug family when you have more than
  one precedent to compare, not just a single write-up.
- Files 15, 16, 17, and 19 were seeded from a second, external source
  document that makes quantitative claims (e.g. "28% of Criticals," "$953M
  lost in 2024") about its own corpus. Those numbers are attributed to
  that source in the relevant files, not independently verified here —
  treat them as a claimed prior worth taking seriously, not a citable fact.
  See `references/source-log.md`'s changelog for exactly what was added,
  from where, and why a couple of things from that source were deliberately
  left out.
- This is a living document. See `references/source-log.md` for how to add
  new patterns as future audits surface them.
