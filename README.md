# ny-attorney-ad-compliance

A Claude skill that audits law firm marketing against New York's attorney advertising rules **as rewritten effective June 1, 2026**, before anything is published.

Most NY attorney-marketing guidance (and most AI training data) still describes the pre-2026 rules. This skill is built on the current text: Rules 7.1 and 7.3 as replaced on June 1, 2026, Rule 7.2 (unchanged), Rule 7.5 (2020 version), Rules 8.4(c), 1.6, and 5.3, and Judiciary Law §§479–482. It also covers the FTC consumer review rule and Google Business Profile policy.

## What it does
- Line-by-line audit with a fixed report: verdict → findings table (excerpt · issue · rule · severity · compliant rewrite) → facts to confirm → required elements → revised copy
- Severity levels: **Block / Revise / Verify / Note**
- Channel-specific checks: website, bios, case results, blog/GEO content, GBP (incl. review replies), directories, email, social, video, paid ads, schema markup, outreach scripts, referral programs, firm names/domains/vanity numbers
- Avoids false positives from obsolete rules (e.g., the "Attorney Advertising" label is no longer required)
- Rewrites keep the marketing intent and never invent facts (`[brackets]` for anything the firm must supply)
- Optional claims ledger for ongoing clients

## Structure
```
SKILL.md                     workflow, severity, report format
references/rules-text.md     verbatim rule & statute text, comment summaries, sources
references/red-flags.md      16 pattern families with why / severity / rewrites
references/channels.md       14 channel checklists + solicitation decision path
references/obsolete-rules.md pre-2026 requirements that are no longer mandatory
scripts/scan.py              stdlib-only first-pass scanner (.txt/.md/.html, stdin; --json)
evals/evals.json             6 test prompts with assertions
```

## Scanner
```
python scripts/scan.py page.html copy.md site-export/ [--json]
```
High recall, low precision by design. It reads visible text, meta titles and descriptions, image alt text, and JSON-LD. It's a first pass that the model then judges in context. It can't detect false facts, omissions, or solicitation context.

## Maintenance
- **Rules as of:** October 2026. Re-verify against nycourts.gov joint orders and NYSBA ethics opinions at least every 6 months, and after any reported amendment. SKILL.md tells the model to check for changes after June 2027.
- Update `references/rules-text.md` first, then `obsolete-rules.md`, then red flags and channels. Log changes in CHANGELOG.md.
- Run the evals after any edit.

## Limits
Marketing compliance review, not legal advice. The responsible attorneys approve final copy. Rule 7.5 paragraphs beyond (a)–(b) and the full NYSBA comment text should be checked in the NYSBA consolidated rules for edge cases.
