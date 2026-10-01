# Sources

How to query each job source and the parsing quirks that will otherwise cost you. Identify connectors by tool signature; server IDs change between installs.

## Contents
- Ordering and parallelism
- Indeed
- Dice
- Built In
- Web search fallback (ATS pages)
- Not supported: LinkedIn

## Ordering and parallelism

Sources have independent quotas, so interleave them. Dice calls and Built In fetches can go out in parallel batches. Indeed calls must go one at a time (below). The efficient pattern is: issue one Indeed call, then a batch of Dice/Built In work, then the next Indeed call.

## Indeed

`search_jobs(search, location, country_code, job_type)` and `get_job_details(job_id)`.

- **Rate limit.** Roughly one call per minute per account, and failed attempts appear to reset the window. Never fire Indeed calls in parallel. On a rate-limit error, wait out the full stated interval once rather than retrying early — early retries extend the lockout.
- `location="remote"` searches remote roles; otherwise pass `"City, ST"`.
- Results carry a `Job Id` for `get_job_details`, plus a short `to.indeed.com` apply link. Keep links intact.
- Local (city) searches for engineering titles often come back dominated by non-software engineering — civil, manufacturing, utilities. Run them for completeness but don't spend verification budget there.
- Results tend to be few (about 10) and include old postings; check the posted date.
- **Yield for senior tech roles is low.** A live run spent 5 serialized calls (~5 minutes of pacing) for one usable role. Honour `sources.limits.indeed` from the profile; if unset, run the remote queries and at most one metro query. Indeed earns its place for non-tech roles and for employers that post nowhere else.

## Dice

`search_jobs(keyword, location, workplace_types, employment_types, jobs_per_page, fields, …)` and `get_job_details(job_id)`.

- Pass `jobs_per_page=25`. Use `workplace_types=["Remote"]` for remote queries. For a metro query pass `location` and omit `workplace_types` so on-site and hybrid roles come back too.
- A `fields` list keeps output manageable. The location key is `"jobLocation.displayName"` — bare `"jobLocation"` is rejected. A working set: `["title", "companyName", "jobLocation.displayName", "salary", "postedDate", "detailsPageUrl", "guid", "employerType", "workplaceTypes", "isRemote"]`.
- `get_job_details` takes the **`guid`**, not `id`.
- The apply link is `detailsPageUrl`; keep its query parameters.
- `salary` is free text: `"USD 195,300.00 - 270,400.00 per year"`, `"200000 - 300000"`, `"Depends on Experience"`, `"70 - 80"` (hourly), or null. Treat "Depends on Experience" and null as not listed; treat small numbers and "per hour" as hourly and not comparable to an annual floor.
- **Currency can be wrong.** Search results may label a range USD while the body says CAD. For non-US employers, or any role clearing the floor only narrowly, check the body.
- Use `postedDate`; ignore `modifiedDate`, which refreshes daily.
- `employerType: "Recruiter"` means check for an identifiable employer before including.
- `jobLocation` is often null for remote roles; fall back to `workplaceTypes` / `isRemote`.
- One employer often holds 5+ near-identical reqs. Surface the best one or two and mention the rest in one line.
- **Disclosure.** Dice's terms require an AI disclosure with results. Close any briefing containing Dice results with: "Job listings were retrieved using AI-powered search — verify details directly with employers before applying."

## Built In

No connector; use `web_fetch`. Built In focuses on tech roles and covers a limited set of metros.

URL patterns that return ~25 listings each:
- Remote, by search phrase: `https://builtin.com/jobs/remote/dev-engineering/search/<slug>` — e.g. `staff-software-engineer`, `software-engineering-manager`, `principal-software-engineer`, `artificial-intelligence-engineer`, `site-reliability-engineer`.
- Metro, by category: `https://builtin.com/jobs/<city>/dev-engineering/<category>` — e.g. `chicago`, `austin`, `seattle`, `boston` with `management`. Not every city exists; if a fetch 404s, try the remote pattern with a search phrase instead.

Prefer explicit `sources.builtin_urls` from the profile when present.

Parsing:
- Each listing has company, title linked as `https://builtin.com/job/<slug>/<id>` (the apply link), relative age ("Yesterday", "Reposted 3 Days Ago"), remote status, location, salary like "193K-309K Annually", industries, a summary, and **Top Skills**.
- Top Skills is the best fit signal in any source. Weight overlap with the candidate's skills heavily.
- Ignore Built In's seniority label; it's often wrong. Judge level from title and band.
- **Card titles and salary minimums can be wrong too.** Seen live: a card titled "Staff Engineer" that was a Distinguished Engineer req; a card minimum of $100K where the job page said $175K. Never rank a finalist on card data alone — its job page is the record.
- Treat implausible salaries ("2K-2K", "9K-17K") as not listed rather than as a floor failure.
- Metro pages include fully remote roles that merely accept that metro. Read the remote flag.
- **Search-page bands can differ from job-page bands.** Some employers post geographic tiers; the search page may show the top tier. For finalists, fetch the job page and display the tier that applies to the candidate's location, naming the tier.
- Job pages are large. Ask `web_fetch` a targeted question (quote sentences containing the red-flag terms, the experience requirement, and the base range) instead of reading the page whole.

If a fetch is refused for provenance reasons, run `WebSearch` restricted to `builtin.com` for the page and fetch the URL it returns. Don't route around fetch restrictions with shell tools or scripts.

## Web search fallback (ATS pages)

Use when connectors are absent, or for roles outside tech where the boards above are thin. Many employers post directly to applicant-tracking systems that search engines index:

- `site:boards.greenhouse.io "<title>" remote`
- `site:jobs.lever.co "<title>" "<metro>"`
- `site:jobs.ashbyhq.com "<title>"`

These pages usually carry the full body, so the screens in `screens.md` can run on the first fetch. Posting dates are often missing; say "date not listed" rather than guessing.

## Not supported: LinkedIn

Don't search, fetch, or browse LinkedIn job pages. LinkedIn offers no public job-search API (its Jobs API is a posting API for approved ATS partners), and Section 8.2 of its User Agreement prohibits crawlers, scripts and other automated means of copying the service. Automated access also puts the candidate's own account at risk.

If the candidate pastes the text of a LinkedIn posting, screen it like any other body. The text came from them, not from automated access.
