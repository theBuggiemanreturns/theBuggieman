# Source log — provenance for this knowledge base

This skill was built by reading and categorizing:

- **4 standalone, deeply-detailed launchpad reports** (the primary source
  for `references/01-amm-pool-graduation-squatting.md`):
  - `hood.fun` — Critical, fork-verified, unauthenticated theft of
    graduation liquidity via Uniswap v3 pool squatting.
  - `Openfair` — High, statically + locally verified, same root cause
    family across fair-launch graduation and instant-listing paths.
  - `LaunchHood V3` — Medium residual finding (predictable-address DoS)
    after the Critical-class squatting bug was already fixed; used as the
    "partially fixed" rung of the maturity ladder.
  - `Cucumberr` — no vulnerability found; used as the "fixed correctly"
    rung and to document *why* its defenses (transfer-lock + balance-based
    V2 mint + burn-to-DEAD) actually close the gap the other three didn't.

- **A public findings database of ~900 individual findings across 87
  security reviews** (Sherlock, Code4rena, Cantina, Immunefi, Blackthorn,
  Three Sigma, and 0xSimao private audits, spanning Jan 2024–Jul 2026),
  covering lending, CDPs/stablecoins, perpetuals/derivatives, liquid
  staking, vaults/yield aggregators, launchpads, bridges/cross-chain
  messaging, governance/voting-escrow systems, NFT/gaming protocols, and
  L1/L2 infrastructure. Protocols with Critical/High findings that were
  used as named precedents in `references/*.md` include (non-exhaustive):
  Autonomint, hood.fun-analog launchpads, Spirit Protocol, BMX Deli Swap,
  Aegis Staked YUSD, GAIB Pre-Vaults, Evro Collateral Onboarding, MORE
  Optimizer, Superfluid Locker System/Yield Backends, Winnables Raffles,
  Blast IDO Pools, Singularity, Mitosis, Fuji Finance (ConnextRouter),
  Tapioca DAO, BendDAO, Teller Finance, Crestal Network, MetaZero
  (Omnichain NFTs / Staking), Ostium, veRWA, Ajna Protocol, Biconomy,
  Exactly Protocol, Yieldoor (core + LoopedVault + Gauges), Cap,
  Beraborrow (CDP + Managed Dens), M^0 Minter Gateway, TITLES Publishing
  Protocol, INIT Capital, DistrictOne, Morpho (Vault V2 + Midnight),
  Cucumberr.

## What was deliberately left out of the reference files

- Pure gas-optimization findings with no security angle at all (constant
  packing, `unchecked{}` opportunities, redundant storage reads beyond
  what's noted in `SMELL-08`) — the corpus has hundreds of these; they add
  no cross-referencing value for *this* pipeline stage.
- One-off Informational nits that didn't recur anywhere else in the
  corpus and don't fit a named pattern (typos, comment inaccuracies,
  natspec gaps, struct field ordering for readability).
- Findings from reports marked "Report not published," "No findings," or
  "Findings not published" in the source index — nothing to extract.

## Changelog

**v4 — four-skill pipeline integration (2026-08-11).**
Kept the independently generated audit pass ahead of historical lookup, then added
a map-driven completeness pass after that gate. Added the 20-category
`cross-reference.md` template and validator, explicit loopback of new candidates
to the audit proof/kill workflow, JSON search output, and accurate corpus wording:
107 consolidated patterns across 20 families derived from roughly 900 reviewed
findings. Added the supplied Mango Markets incident context to `ORC-06` and
retained its dollar figure as attributed incident context rather than an
independently verified KB statistic.

**v3 — two new source documents, five (then six) new reference files.**
Two documents were provided: a purpose-built seed file explicitly written
"for the cross-reference skill" (a condensed incident corpus plus
already-mitigated signatures), and a much larger sibling skill
(`web3-smart-contracts`) covering stage-1/2 hypothesis generation for
DeFi-protocol and token/meme-coin engagements, with substantial overlap
in the incident corpus and additional named bug-class material this KB
didn't yet have.

Added:
- `references/15-accounting-state-desync.md` (new) — phantom yield,
  fast-path-skips-update, wrong-order dependent calculation. Framed by
  the source as the single highest-frequency Critical class in its
  corpus; nothing in files 01–14 covered this specific two-variables-
  drift-apart mechanism.
- `references/16-boundary-conditions-off-by-one.md` (new) — `>` vs `>=`
  at period/epoch/deadline/array/amount boundaries. Distinct from
  `RND-*` (rounding/precision), which doesn't cover comparison-operator
  boundaries.
- `references/17-incomplete-code-paths.md` (new) — the function-family
  comparison test as an explicit methodology, plus two named instances
  (missing refund in an update sibling, an alternate entry point
  bypassing validation).
- `references/18-already-mitigated-signatures.md` (new) — a single,
  concrete checklist for Step 5 (positive controls), which existed in the
  workflow before this update but had no ready-made artifact to point to.
  Cross-references every row back to the pattern IDs it closes.
- `references/19-token-rugpull-signatures.md` (new) — a genuinely
  different domain (token contracts as adversarial artifacts) that this
  KB didn't cover at all before. EVM + Solana.
- `references/20-emerging-2025-2026-patterns.md` (new) — Pectra-era EVM
  features (EIP-1153 transient storage, EIP-7702 EOA delegation) and
  account abstraction (ERC-4337 paymasters), framed explicitly as new
  surfaces for already-known root causes rather than new root causes,
  plus LST/LRT depeg as a live instance of `ORC-01`.
- New sub-patterns folded into existing files rather than spun out
  separately, because they're genuinely the same category: `AMM-09`
  (privileged authority retained past graduation — pump.fun) in file 01;
  `ACC-06` (existence check used where an ownership check was needed —
  ZeroLend `split()`) in file 05; Wormhole ($10M, uninitialized proxy) and
  Parity ($150M frozen, uninitialized *shared library* — a higher-blast-
  radius variant worth calling out on its own) added as precedents to
  `ACC-01`/`ACC-02`; the "read every sibling function together" checklist
  (`vote()`/`poke()`/`reset()`) added to `ACC-03`.

Deliberately **not** adopted, because it belongs to a different pipeline
stage than this skill covers:
- The kill-signal / target-scoring matrix (TVL thresholds, "engage if
  ≥6/10," bounty-ROI formulas) — that's stage-1 target triage (should I
  even look at this target), not stage-3 cross-referencing.
- Tooling installation commands (Foundry, Slither, Echidna, Mythril,
  Semgrep, etc.) and Foundry PoC/exploit templates — stage-2 bug-hunting
  and exploit-development tooling.
- The Immunefi report-template scaffold — a deliverable format, not a
  precedent library.
- The "Learning Resources" list (Damn Vulnerable DeFi, Cyfrin Updraft,
  etc.) — training material, not something to cross-reference against.

Both left-out categories are legitimate and useful — just for the
sibling skill that already covers that stage, not for this one. Pulling
them in here would blur the boundary this skill exists to keep clean (see
`SKILL.md`'s "this skill mainly contextualizes findings you already
have" framing, and the Step 0/file-14 discussion above it).

**v3 addendum — scoring refinement found while testing the new patterns.**
Testing the new sub-patterns (`ACC-06`, `RUG-06`) against representative
queries surfaced a side effect of v2's keyword-count normalization: a
single excellent, specific hit (e.g. an exact match on `_requireOwned`)
was getting diluted to a "weak" band purely because the pattern had other
keyword phrases that didn't match — correct ranking, misleadingly low
confidence label. Fixed with a `single_hit_floor` in `search_patterns.py`:
an exact match on a multi-word phrase, or on a single word that looks
like a code identifier (`snake_case`/`camelCase`/dotted), sets a floor
under the combined score regardless of dilution from other keywords.
Plain single-word matches (no identifier shape — "graduate," "pool,"
"seed") don't get a floor, specifically so this fix can't reopen the v2
bug it was built next to. Re-ran the full v2 regression suite plus the
two newly-broken cases after the change; all pass — see the queries
tested inline in that session if reproducing.

**v2 — fixes driven by a real usage report.** An agent ran
this skill against a live target ("Sheriff") and reported back concrete
process and code issues. Three were confirmed and fixed:

1. **Scoring bug in `scripts/search_patterns.py`:** raw per-keyword scores
   were summed with no normalization for how many keywords a pattern has,
   so a pattern with many generic keywords (e.g. `AMM-01`, 9 keywords)
   could structurally out-rank a pattern with few specific keywords (e.g.
   `RND-04`, 3 keywords) on partial-overlap noise alone, independent of
   which was the better conceptual match. Reproduced directly: a
   dust-leftover-token query scored `AMM-01` (pool squatting — unrelated)
   above `RND-04` (truncation-locked dust — the right family) purely on
   generic word overlap ("seed," "liquidity," "migrate"). Fixed by
   normalizing each pattern's score by its own keyword count, and by
   surfacing a `weak`/`moderate`/`strong` band instead of an opaque raw
   number, so a `weak` top match now visibly tells the reader not to
   anchor on it instead of looking authoritative.
2. **Workflow contradiction:** `SKILL.md` said cross-referencing is
   stage 3 and runs on stage-2 output; file 14 separately said to run its
   checklist first, before manual review — i.e. earlier than stage 2.
   Resolved by adding an explicit **Step 0** to `SKILL.md`'s workflow that
   names file 14 as the sole, narrowly-scoped exception allowed to run
   directly against fresh source, and rewriting file 14's intro to point
   back at Step 0 instead of independently contradicting the ordering.
3. **Added a "positive control" step (Step 5)** to the workflow: for the
   highest-stakes patterns stage 2 considered and ruled out (especially
   `REN-02`-class callback checks and `ACC-01`-class initializer checks),
   explicitly check the matching reference file's detection checklist
   against source and cite the pattern ID as a confirmed, checked defense
   in the report — not just a silent non-finding. Scoped deliberately to
   "highest-stakes disproved hypotheses only," not every pattern, to avoid
   turning a cheap cross-reference pass into an unbounded re-audit.

One suggestion from the same report was *not* adopted as literally
proposed: deleting the "this skill will not find new bugs for you" line
entirely. That caution is still correct and worth keeping for files
01–13 — the fix was to scope the Step 0 exception narrowly to file 14
rather than remove the caution altogether, so a future run doesn't read
the exception as a general license to go bug-hunting with this skill
instead of doing stage 2 properly.

## How to extend this knowledge base

When a new audit surfaces a finding that doesn't match anything in
`pattern_index.json` (i.e. `scripts/search_patterns.py` returns no
matches, or a poor match):

1. Decide if it's a genuinely new pattern or a variant of an existing one
   (check the "Cross-references" section at the bottom of each relevant
   `references/*.md` file first).
2. If new: add a pattern entry to the appropriate category in
   `pattern_index.json` (or create a new category file + index entry if it
   doesn't fit any of the 20 existing categories), with `keywords` chosen
   from the vocabulary a *future* auditor would actually type or see in
   code (function names, error-message text, root-cause verbs).
3. Add the full write-up to the matching `references/*.md` file using the
   existing template: Root cause / Detection checklist / Precedents /
   Fix, citing protocol + finding ID + one-line paraphrase — never verbatim
   quotes from the source report.
4. Update this source log with the new protocol name.

This keeps the skill a living document instead of a one-time snapshot.
