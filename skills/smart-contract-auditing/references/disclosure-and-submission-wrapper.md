# Disclosure & Submission Wrapper

**Where this sits:** applied *after* `smart-contract-auditing` has produced a
confirmed finding using `references/proof-triage-report.md`'s report schema.
This wrapper only applies to whitehat bug-bounty / direct-disclosure engagements —
not paid client audits, which have their own contractual reporting terms.

Auditing intentionally left this out. Quoting `references/proof-triage-report.md`:
*"For bounty disclosure, add private-channel and compensation language only when
requested. Do not hard-code a researcher identity into the auditing skill."*
This file is that optional addition, kept separate so it never contaminates the
core audit report for non-bounty engagements. Source: `smart-contract-bug-hunting`
step 8 + ground rules.

## Ground rules (restate before every disclosure)

- All testing happens on a local fork or testnet — never mainnet, never real user
  funds.
- Findings are reported privately first. Never disclose publicly before a fix
  ships, and never hold an unpatched 0-day for leverage.

## Channel selection

- **Formal program exists** (Immunefi, HackerOne, Cantina, or the project's own
  `SECURITY.md`) → submit through the program's official intake. These have
  structured triage and hold periods — use them, don't go around them.
- **No formal program** → disclose directly to the team. Be explicit that the fix
  is not conditioned on payment, then separately ask for a bounty. This is both
  the ethical move and, pragmatically, the one that gets taken seriously fastest —
  teams are far more receptive to a report that isn't implicitly "pay me or I sit
  on this."

## Compensation ask language (template)

Append to the end of a finding report when disclosing directly:

> This is a good-faith private disclosure. [One sentence on effort/value delivered
> — e.g. number of working PoCs, or the fact this was found without a formal
> bounty program in place.] I would appreciate being considered for a bounty
> commensurate with a [severity]-severity finding.
>
> To be explicit: I am **not** conditioning this disclosure or the fix on payment
> — the details above are yours to act on immediately regardless of whether we
> agree on a number. I'm simply asking that responsible disclosure be recognized
> fairly, and I'm happy to discuss compensation once you've confirmed the issue.

## Don't hold the fix hostage

Never gate remediation details behind a bounty agreement. State the fix
unconditionally, ask for consideration separately. Aside from being the right
call, teams patch faster and trust the report more when there's no perceived
leverage play.
