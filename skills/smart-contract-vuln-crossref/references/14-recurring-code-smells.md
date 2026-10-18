# 14 — High-frequency low-severity patterns (grep for these first)

These eight patterns account for a large share of *all* Low/Informational
findings across the ~900-finding corpus — often dozens of near-identical
instances per audit, one per affected contract. They are individually
low-severity, but they're free to check mechanically, with high recall,
before doing any deep manual review.

This is the one file in this knowledge base meant to be run directly
against fresh source rather than against an existing candidate finding —
see **Step 0** in `SKILL.md`'s workflow. Everything else in this skill
(files 01–13) is for cross-referencing something stage 2 already flagged;
this file is the sole, explicitly-scoped exception, precisely because
these 8 checks are cheap and mechanical enough not to need a human
suspicion to justify running them.

Recommended order of operations on a fresh codebase: run this checklist
first as a mechanical pass (grep-able, fast, high recall), log every hit
as a batched Low/Info finding grouped by pattern rather than repeating
the same writeup per contract, *then* move to the deeper pattern files
(01–13) for the manual-review-required classes — those still need a
candidate finding from stage 2 to check against, this file doesn't.

| ID | Pattern | Grep starting point | Typical severity |
|---|---|---|---|
| SMELL-01 | Missing `_disableInitializers()` on upgradeable implementation constructors | `constructor()` in any file importing `*Upgradeable`/`Initializable` | Low–Med (see `ACC-02`) |
| SMELL-02 | `Ownable` used instead of `Ownable2Step` for a critical role | `is Ownable` (not `Ownable2Step`) | Low (see `TRU-03`) |
| SMELL-03 | `address.transfer()`/`.send()` instead of `.call{value}("")` | `.transfer(` / `.send(` on an `address payable` | Low (see `TOK-06`) |
| SMELL-04 | `approve()` instead of `safeApprove`/`forceApprove`, or missing `SafeERC20` | `IERC20(...).approve(` without a `using SafeERC20` nearby | Low–Med (see `TOK-04`) |
| SMELL-05 | CEI ordering violated with no demonstrated reentrancy path | external call followed by a storage write in the same function | Low (see `REN-01`; escalate if a real reentrancy path exists) |
| SMELL-06 | Missing events on state-changing admin functions | any `function set*(...) external onlyOwner` with no `emit` | Informational |
| SMELL-07 | Zero-address / zero-value checks missing on constructor or setter | constructor/setter parameters of type `address` with no `require(x != address(0))` | Low |
| SMELL-08 | Storage variable read repeatedly instead of cached in memory | same `storageVar` read 2+ times in one function/loop | Gas only, not security |

## Why bother listing gas-only findings in a security cross-reference skill

`SMELL-08` (and to a lesser extent `SMELL-06`) are not vulnerabilities.
They're included because (a) the source corpus includes them at high
volume and a completeness pass should account for what was screened out
and why, and (b) `SMELL-06` (missing events) has real forensic value even
though it isn't itself exploitable — its absence is frequently what makes
an actual exploit (from any of files 01–13) harder to detect after the
fact. Note it, but don't let it consume audit time better spent on
files 01–13.

## Redundancy note

Across the corpus, single audits routinely report the *same* SMELL-01
through SMELL-04 pattern 3–8 times in one report (once per affected
contract). When writing up findings from a new target, batch these:
one finding titled e.g. "Missing `_disableInitializers()` across N
upgradeable implementation contracts," with each affected contract listed
as an instance — this mirrors how the better reports in the source corpus
(e.g. Maple, Mitosis, Ostium) structured their own Low/Info sections, and
is much more useful to a development team than N separate near-duplicate
findings.

This also applies *across* files, not just within this one: if
`TRU-02` (self-renounce lockout), `TRU-03`/`SMELL-02` (single-step
transfer, no zero-address check), and something like a stale-role-after-
transfer issue all show up on the *same* ownership/role-transfer function,
that's usually three genuinely distinct root causes (different trigger,
different fix) rather than duplicates — don't merge them into one finding
just because they share a function. But do cross-reference them
explicitly against each other in the write-up, so a reader isn't left
wondering why the same ~10 lines of code produced three separate entries.

## Escalation note

Don't treat every hit here as automatically Informational/Low and move on
— `SMELL-01` (missing `_disableInitializers()`) is normally Informational,
but escalate if the implementation contract can be tricked into
self-destructing or delegatecalling somewhere sensitive once initialized
standalone; `SMELL-05` (CEI ordering) is normally Low, but escalate to
`REN-01`/`REN-02`/`REN-03` severity if a concrete reentrancy path actually
exists rather than being merely theoretical. This checklist is a sweep for
recall, not a severity assignment — sort each hit into the deeper file
(01–13) it maps to before deciding severity.
