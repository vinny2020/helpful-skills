# Reputation screen

A role that passes every other filter can still be a bad move if the employer is mid-restructure. None of that shows in a listing. This screen runs before the briefing is written, because applying it after the fact means the candidate reads a ranking that's about to change.

## Method

1. **Start from what's known.** Load `reputation.known` from the profile. A `VERIFIED` finding newer than `reputation.reverify_after_days` (default 30) counts as verified for this run — including for a `TOP PICK` — and needs no new fetch. Older findings, and anything labelled `DIRECTIONAL` or `UNKNOWN`, are a starting point to re-check.

   **Stored labels are evidence, not verdicts.** Re-apply this run's thresholds to every stored finding. If a finding stored as `CAUTION` meets a hard-flag rule (e.g. "rolling sub-WARN layoffs" meets `quiet_layoffs`), the employer is `DEPRIORITIZED` — the rules win — and the ledger block should correct the stored label.
2. **Batch the research.** Issue 3–5 searches that each name several employers, targeting the last 12 months: layoffs, restructuring, leadership changes, revenue guidance, review-site ratings. For example: `tech layoffs 2026 CompanyA CompanyB CompanyC` and `CompanyD CompanyE employee reviews rating 2026`.
3. **Read the pages that matter.** A search result list is titles and links — weak evidence. For any employer you're about to call a `TOP PICK` *without a fresh stored finding*, any new candidate for a hard flag, and at least `reputation.verify_top_n_per_section` employers per section, fetch the actual page (a review-site summary, a layoff tracker, an earnings report) and get the number.
4. **Prefer pages that allow fetching.** Some news sites refuse automated fetches. Layoff trackers and aggregators usually carry the same figures.

A near-perfect stack match at an employer you've never heard of is the case where this matters most. It's also the case most tempting to wave through.

## Labels

Every employer with a full role entry in the briefing gets a one-line note carrying one label. Employers named only in an overflow line are exempt — researching forty of them buys little. The label is what stops a stale impression from being read as fact.

| Label | Meaning |
|---|---|
| `VERIFIED` | Found by a search or fetch during this run. State the specific finding: percentage cut and date, rating and review count, guidance change. Add `— GOOD`, `— CAUTION`, `— MIXED` or `— AVOID` as the evidence warrants. |
| `DIRECTIONAL` | General knowledge or a weak signal not confirmed today. Say so, and suggest the candidate check review sites themselves. |
| `UNKNOWN` | No meaningful public footprint. Write the line anyway and flag it as unknown-risk; a small company with a suspiciously perfect match deserves scrutiny on size, funding and whether the band is real. |
| `YOUR CALL` | The employer is the same company or business unit as an entry in `summary.past_employers`. Don't lecture someone about a company they know firsthand — their read beats yours. For a parent, sibling or acquirer (worked at a subsidiary; the listing is its parent company), label it normally on the evidence and add the relationship in the note: their inside knowledge is partial, not absent. |

## Thresholds

From `reputation.hard_flag` — any one confirmed within the last 12 months marks every role at that employer `DEPRIORITIZED`:
- A layoff at or above `layoff_pct_12mo` percent of staff.
- Declining revenue guidance.
- Documented layoffs deliberately kept below WARN-notice thresholds.
- Documented downward revisions to pay bands.

From `reputation.caution` — a rating below `rating_below` or a recommend rate below `recommend_below` earns a `CAUTION` label and a lower rank, without dimming.

A layoff below the hard-flag percentage is still worth stating, with the number and date. Whether 8% three months ago matters is the candidate's call; the briefing's job is to put the fact in front of them.

## Deprioritized is not deleted

Hard-flagged roles stay in the briefing, dimmed and moved to the bottom of their section with the finding stated. The candidate may know something you don't — a specific team that was protected, a friend who works there — and the decision is theirs.

## Writing the note

- Attribute every claim: "reviews describe…", "reported cutting ~300 roles in June 2026…". Never state a reputation claim as bare fact.
- One or two sentences. Lead with the most decision-relevant number.
- When a finding cuts across roles (cuts concentrated in sales while engineering was protected), say which side the role sits on.
- Note dissent briefly: a 4.9 rating with one detailed "toxic management" review is worth one clause, because it's a good interview question.

## Recording

Add each new finding to the end-of-run ledger block with employer, finding, label and today's date, so the next run starts from it.
