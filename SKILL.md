---
name: ny-attorney-ad-compliance
description: Pre-publication compliance audit of law firm marketing against New York's attorney advertising rules as rewritten June 1, 2026 (Rules 7.1, 7.2, 7.3, 7.5, 8.4(c), 1.6, Judiciary Law §§479–482), plus FTC review rules and Google Business Profile policy. Use whenever marketing for a New York law firm or NY-admitted lawyer is drafted, edited, reviewed, or published — homepage and practice-area copy, attorney bios, case results, About pages, Google Business Profile descriptions/posts/review replies, directory profiles (Avvo, Justia, Martindale, Super Lawyers), email and newsletters, LinkedIn and social posts, video scripts, ads, schema markup, outreach or BD call scripts, referral programs, firm or trade names and domains. Trigger even on casual asks like "check this", "can we say this", "is this OK to post", "audit the site", or any request to write law firm copy for a NY firm. Also use for site-wide audits and to rewrite non-compliant copy into compliant, still-persuasive copy.
---

# NY Attorney Advertising Compliance

Audit law firm marketing before it goes live: find every statement that could be false or misleading, solicitation that crosses the line, referral payments, confidentiality leaks, and naming problems. Cite the rule for each one and give a compliant rewrite that keeps the marketing intent.

**Your role:** marketing compliance reviewer, not the firm's counsel. The attorneys are personally bound by these rules (and Rule 5.3 makes them responsible for agency work done for them), so they approve final copy. Say that once, briefly, at the end of each audit. Don't hedge every line.

## Step 0: Confirm the rules are current

New York replaced its advertising rules on **June 1, 2026** with an ABA Model Rules approach. This skill reflects the rules as of October 2026.
- If the current date is after **June 2027**, or the user mentions a new rule change or ethics opinion, search for recent NY changes (nycourts.gov joint orders, nysba.org ethics opinions on "Rule 7.1") before auditing, and say what you found.
- Most online NY guidance still describes the **old** rules. Read `references/obsolete-rules.md` and never flag a pre-2026 requirement as mandatory. Doing so is a false positive that costs credibility.

## Step 1: Confirm jurisdiction and scope

- These rules apply to New York-admitted lawyers and NY firms. For lawyers admitted in several states, note that the other states' rules may also apply and some are stricter (e.g., filing or pre-approval regimes). Flag it; don't audit other states from memory.
- Rule 7.1 covers **all communications about a lawyer's services**, including emails to existing clients, messages to other lawyers, social posts, directory profiles, hidden markup, and AI-generated content. Nothing is "just internal marketing" if it describes the firm's services to someone.

## Step 2: Gather inputs

1. **The copy.** Pasted text, a file, or URLs to fetch. For a site-wide audit, fetch every page you can reach (home, about, each attorney bio, each practice page, results, contact, blog index, plus a sample of posts) and audit each one.
2. **The channel.** Website, GBP, email, outreach, and so on. Channel-specific checks are in `references/channels.md`. Read the relevant section.
3. **The firm's facts**, if available: admissions, years in practice, attorney headcount, offices, awards (issuer + year), certifications (certifying body), case results with dates, and client consents. Check the conversation, project files, and memory. Anything you can't confirm becomes a **Verify** item. Never assume a claim is true or false without evidence.

## Step 3: Run the automated scan (when code execution is available)

```bash
python scripts/scan.py <file-or-folder> [--json]
```
It accepts .txt, .md, and .html. It flags superlatives, guarantees, results, "certified" or "expert" language, comparisons, implied size, influence claims, awards, testimonials, referral incentives, legal-aid naming, document look-alikes, AI placeholders, review schema, and missing contact info. It's a **first pass**: high recall, many hits will be fine in context. Never paste its output as the audit. Every hit needs your judgment, and it can't catch omissions, false facts, or solicitation context. No code execution? Skip this step and use the red-flag table in `references/red-flags.md` manually.

## Step 4: Judgment pass

Read every claim and ask four questions:
1. **Is it true?** Can the firm prove it **today**, not just when first written?
2. **Is it misleading as a whole?** Consider what a reasonable non-lawyer would come away believing, including from what's left out (e.g., a verdict without saying it was reduced on appeal, or "no fee unless we win" without mentioning the client pays costs).
3. **Does it create unjustified expectations?** Results, win rates, or "we get results" phrasing implies similar outcomes regardless of the facts.
4. **Does it compare in a way that can't be substantiated?** "Best", "top", "more than any other firm".

Then check the rules beyond 7.1(a): certified-specialist naming (7.1(c)), attribution (7.1(d)), referral value (7.2), live solicitation (7.3, Judiciary Law), names, domains, and partner implications (7.5), confidentiality (1.6), and reviews (FTC/Google). Exact text is in `references/rules-text.md`. Pattern guidance and rewrites are in `references/red-flags.md`.

## Severity

| Level | Meaning | Examples |
|---|---|---|
| **Block** | Likely violation as written; do not publish | False fact; "certified" without naming the body; outcome guarantee; client info revealed without consent; live solicitation outside 7.3(b) exceptions; paying for referrals; "legal aid" in a private firm's name; fake or bought reviews |
| **Revise** | Misleading risk a rewrite fixes | Superlatives; results without context; implied size or partnership; unsubstantiated comparisons; awards without issuer and year |
| **Verify** | Possibly fine; needs substantiation from the firm | Years of experience; case counts; awards; client names (consent); "specialize" claims |
| **Note** | Best practice, not a rule issue | Adding the voluntary "Prior results" disclaimer; strengthening attribution |

## Step 5: Report format

ALWAYS use this structure:

**Verdict:** ✅ Ready to publish · ⚠️ Publish after revisions · ⛔ Do not publish — plus one sentence why.

**Findings** (most severe first):

| # | Excerpt | Issue | Rule | Severity | Compliant rewrite |
|---|---|---|---|---|---|

Quote the exact excerpt. Keep "Issue" to one plain-English sentence. Cite the rule precisely (e.g., "7.1(a); ABA cmt. on unjustified expectations"). Put [brackets] in rewrites wherever the firm must supply a fact.

**Facts to confirm with the firm:** one line per Verify item, written as a question a partner can answer quickly.

**Required elements:** ✅/❌ responsible lawyer or firm named · ✅/❌ phone or office address · ✅/❌ firm name matches legal entity name (incl. PLLC/LLP/PC).

**Revised copy:** include it when asked, or when there are three or more Block/Revise findings. Apply every fix, keep the original voice, length, and structure, and leave verified facts untouched.

Close with one line: *Marketing compliance review, not legal advice; final approval rests with the responsible attorneys.*

For **site-wide audits**, start with a summary table (page · verdict · Block count · Revise count · Verify count) and order the per-page reports by severity.

## Rewriting principles

- **Specific beats superlative.** "Top NYC litigators" → "Commercial litigators in New York state and federal courts since [year]". It's provable, and it usually persuades better.
- **Context beats claims.** Results get the matter type, year, court or forum, and the voluntary disclaimer.
- **Never invent facts** to make a rewrite work. Use [brackets].
- **Keep the persuasive job.** A rewrite that is compliant but dead is a failed rewrite. Preserve the hook, the CTA, and the voice.
- Check that each rewrite doesn't introduce a new problem.

## Firm claims ledger (recommended)

For ongoing clients, suggest keeping a claims ledger: each recurring claim (years, headcount, awards, results, certifications), its evidence, and the date it was last verified. Future audits then check claims against the ledger instead of re-asking. If a ledger exists in the project or conversation, use it, and flag any claim older than 12 months for re-verification.

## Reference files
- `references/rules-text.md`: verbatim rule text and statutes, comment summaries, sources. Read it when citing or when a finding is close.
- `references/red-flags.md`: pattern library with why it's risky, severity, and rewrites. Read it for every audit.
- `references/channels.md`: channel-specific checks (web, bios, results, GBP, directories, email, social, video, ads, schema, AI content, outreach, referral programs, names and domains). Read the sections that match the input.
- `references/obsolete-rules.md`: pre-June 2026 requirements that are no longer mandatory. Read it once per session.
