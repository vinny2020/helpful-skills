---
name: job-search-scout
description: Run a personalized, screened job search across job boards (Indeed, Dice, Built In, or plain web search) and produce a ranked briefing driven by a candidate profile — resume, target titles, workplace preferences (remote/hybrid/on-site), salary floor, relocation rules, and reputation thresholds. Screens out sales roles disguised under engineering titles, staffing-agency funnels and commission-inflated pay bands, and checks each employer's recent layoffs and reviews before ranking. Use this whenever someone wants to find jobs that fit their background, set up a daily or recurring job search, triage listings against their resume, or vet employers they're considering — even if they only say "find me roles like my current one" or "what's out there for a staff engineer in my city".
---

# Job Search Scout

Job boards answer the wrong question. A search returns titles, companies and a salary string — never the requirements — so a title match tells you almost nothing about whether a role is winnable or worth taking. Three failure modes recur often enough that this skill exists to catch them:

- **Disguised roles.** Pre-sales and solution-engineering reqs posted under engineering titles. They look like the best matches in the list because they're paid like it.
- **Misleading pay.** Ranges that are on-target earnings (base + commission), or in a different currency, presented as base.
- **Invisible employer risk.** A role can match perfectly at a company that cut 14% of staff three months ago. Nothing in the listing says so.

The skill's value is the screening, not the searching. Spend effort accordingly.

Everything person-specific comes from a **profile** file. Nothing about the candidate belongs in this skill.

## 1. Load the profile

Look for the profile in this order: a path the user gave you → `profile.yaml` in the working directory → `~/.job-search-scout/profile.yaml`. The schema is in `references/profile-schema.md`; `profile.example.yaml` is a filled-in example.

If there is no profile and someone is present, build one with them (see *First run* below). If there is no profile and the run is unattended, stop and report that — guessing someone's salary floor or titles produces a briefing that's confidently wrong.

**Resume.** The profile can carry the resume as inline `text`, a `path`, or a `url`. Prefer `text` for scheduled runs: those often execute in a cloud environment that can't reach the candidate's laptop, so a local path silently fails. If a path is unreachable, don't treat that as a run failure — fall back to the profile's `summary` fields and say so in one line.

From the resume, extract: recent titles and level, core skills, domains, and past employers. Explicit profile fields override anything you extract, because the candidate knows better than a parse of their resume.

## 2. Plan the searches

Detect which sources are available by **tool signature**, not server name — connector IDs vary between installs:

| Source | How to recognize it | Notes |
|---|---|---|
| Indeed | `search_jobs(search, location, country_code, job_type)` | Strict rate limit — serial calls only |
| Dice | `search_jobs(keyword, location, workplace_types, employment_types, jobs_per_page, …)` | Highest yield for tech roles |
| Built In | no connector — fetched pages | Rich salary and skills data for tech roles |
| Web search | `WebSearch` / `web_fetch` | Fallback; covers ATS pages (Greenhouse, Lever, Ashby) |

Build the query plan from the profile: each target group's titles × each acceptable workplace mode (remote, plus the home metro for hybrid/on-site). Merge near-synonyms into one query rather than running both. Aim for roughly 15–20 searches total; past that, yield drops and duplicates climb. Respect `sources.disabled` and `sources.limits`.

Never search or fetch LinkedIn: it has no public job-search API and its terms prohibit automated access (details in `references/sources.md`). If the candidate pastes a LinkedIn posting's text, screen that text normally.

Read `references/sources.md` before issuing calls — it has the rate-limit rules, response-parsing quirks and the URL patterns that work for Built In.

## 3. Collect

Run every planned search before filtering anything.

Keep a **tally file** (e.g. `tally.md`) from the first call, and update it as you go rather than reconstructing it at the end: one line per search (source, query, result count, errors), then a count per exclusion reason as you filter (below floor, location, specialization, clearance, disguise, funnel, ledger-skipped). The closing summary is computed from this file. Disguise, funnel and ledger counts should be exact; floor and specialization counts may be approximate if marked with `~`. Without the file, a run of ~300 rows produces miscounts that end up in the email.

Keep a coverage record too: which sources ran, which failed, which recovered.

A connector that fails at the start of a run sometimes reconnects a minute later. Before reporting a source as skipped, re-check for its tools once the other sources are done. A degraded run is fine — never abort because one source is down — but say plainly which sources ran, and distinguish "failed and recovered" from "skipped".

## 4. Filter and score

Deduplicate first: the same role from several sources becomes one listing (prefer the richest source's record, note all sources).

**Hard-exclude** when any of these hold — each comes from the profile:
- Base salary max is below `compensation.base_floor`.
- The role requires on-site presence outside the candidate's acceptable metros and doesn't clear `workplace.relocation.min_base`. (On-site *in* the home metro is not a relocation.)
- It hits a `filters.dealbreakers` entry (e.g. a clearance the candidate lacks).
- It requires a specialization in `filters.exclude_specializations`.
- It's a staffing funnel with no identifiable employer, or the employer is in `filters.exclude_companies`.

**Score** what's left on stack overlap (resume skills and `boosts.skills`), domain match, level match, workplace priority order, and pay upside. A listing whose skills field names several of the candidate's core skills outranks one whose title merely matches.

## 5. Verify the bodies

Read `references/screens.md`. It covers the role-disguise screen, staffing-funnel signals, base-vs-OTE, and currency checks.

You can't afford to open every listing. Check the profile's `ledger.adjudications` first — a req already settled in an earlier run doesn't need a second look. Skip anything that already fails the salary or location bar on its own. Then spend verification calls on: the roles you're about to rank near the top, pay bands that look generous for the level, titles containing words like Solution(s), Field, Customer, Partner or Specialist, and companies with large sales organizations.

## 6. Reputation screen

Read `references/reputation.md`. This step runs inside the main search, before the briefing is written — not as an optional follow-up. In practice it regularly moves the best stack match out of the top picks, which is exactly what it's for.

Start from `reputation.known` in the profile, re-verify anything older than about a month, and research the rest in batched searches. Every employer in the briefing gets a one-line note with a confidence label (`VERIFIED`, `DIRECTIONAL`, `UNKNOWN`, or `YOUR CALL` for the candidate's past employers). Employers that cross the profile's hard-flag thresholds are marked `DEPRIORITIZED` and moved down — not deleted. The candidate may disagree, and they should get to.

## 7. Rank and write the briefing

Read `references/output-format.md`. In short: a short bottom-line box naming one or two `TOP PICK`s (strong fit, good pay, clean reputation) and anything that dropped on reputation; one section per target group, ordered by **fit and reputation together**; per-role why-it-fits and reputation lines; an overflow line instead of an endless list; and a closing tally of what was filtered and why.

## 8. Deliver

Always present the briefing in chat. If `output.delivery.email.enabled`, also email it:

1. Write the briefing as JSON in the shape `scripts/render_email.py` expects (documented at the top of the script).
2. Run `python scripts/render_email.py briefing.json --out-dir . --max-per-section N`, with N from `output.delivery.email.max_per_section` (default 6). This produces `email.html`, `email.txt` and `subject.txt`. The script handles escaping and colour-coding so they can't drift between runs, and trims each section to a digest — the email links back to nothing, so it carries the top of each section and folds the rest into the overflow line.
3. Read the rendered files and pass their **contents** to the email connector (HTML body, plain-text body, subject). Email tools take strings, not file paths. The digest limit is what keeps this copy small; a full 35-role email is ~60 KB of text to carry through a tool call, which is slow and error-prone.

Put emoji in subjects as **literal characters**. Email connectors take JSON parameters, and JSON has no `\U0001F50D`-style escape, so the escape text arrives verbatim in the subject line.

A send counts as delivered only when the tool returns a message id. Retry once on failure; if it fails again, report the error plainly rather than looping.

## 9. Propose ledger updates

End every run with a short block the candidate can paste into the profile's `ledger` and `reputation.known` sections: newly adjudicated reqs (with verdict and one-line reason) and new reputation findings (with date and label). This is how the skill gets cheaper and sharper over time — each run inherits the previous runs' judgment instead of re-deriving it. If `ledger.auto_update` is true and the profile file is writable, append the entries directly and say that you did.

## First run: building a profile

When someone has no profile, ask for — or extract from their resume — the minimum needed to run:

1. Resume (pasted text is best).
2. Target titles, grouped the way they'd want the briefing sectioned.
3. Workplace: remote / hybrid / on-site in priority order, home metro, and whether they'd relocate and at what pay.
4. Pay: base floor and currency.
5. Dealbreakers: things that make a role unwinnable or unwanted (e.g. no sales background, no clearance, no heavy travel).
6. Past employers (these get the `YOUR CALL` reputation label).
7. Delivery: chat only, or email too.

Write the result to `profile.yaml` using the schema, show it to them, and run once interactively before they schedule it. Everything else in the schema has sensible defaults.

## Unattended runs

When running on a schedule, nobody can answer questions. Make the reasonable call, note the assumption in one line, and keep going. Always deliver something — including a "nothing qualified today" briefing that lists the searches run — because silence is indistinguishable from failure.
