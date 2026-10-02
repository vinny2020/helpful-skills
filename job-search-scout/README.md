# job-search-scout

An agent skill that runs a personalized job search and returns a ranked, *screened* briefing — the kind of list you'd get from a friend who read every posting, checked the pay was real, and looked up whether the company just had layoffs.

It works with Claude (Claude Code, the Claude apps, Cowork) and any agent runtime that supports the `SKILL.md` format.

## Why screening, not searching

Job boards return titles, companies and a salary string. They never return requirements. So the best-looking matches are often traps:

- **Sales roles under engineering titles.** "Staff Software Engineer" postings whose bodies demand five years of pre-sales experience and pay on commission.
- **Inflated pay.** On-target earnings shown as base; a CAD range labelled USD.
- **Employer risk.** A perfect stack match at a company that cut 14% of staff last quarter.

This skill reads the bodies of the roles it's about to recommend, applies your floor to base pay only, and researches each employer's last 12 months before ranking. Roles at flagged employers are dimmed and moved down — not hidden — so you can disagree.

## What you provide

One `profile.yaml` (see `profile.example.yaml` and `references/profile-schema.md`):

- **Resume** — pasted text, a file path, or a URL
- **Target titles**, grouped into the sections you want
- **Workplace preferences** — remote / hybrid / on-site in priority order, metros, and whether you'd relocate and at what pay
- **Compensation** — base floor and currency
- **Dealbreakers** — e.g. no pre-sales background, no clearance, no staffing agencies
- **Reputation thresholds** — the layoff percentage, rating and recommend-rate lines that should demote an employer, plus any findings you already know

## What you get

A briefing with a short bottom line naming the one or two best picks, then a section per target group. Each role has a link, location, base pay (and OTE when different), source, posted date, a specific why-it-fits line, and a reputation note labelled `VERIFIED`, `DIRECTIONAL`, `UNKNOWN`, or `YOUR CALL` (for your past employers). Optionally emailed.

Each run ends with a **ledger** block — reqs it adjudicated and employer findings it verified — to paste back into your profile. The next run starts from those verdicts instead of re-checking them, so the skill gets faster and sharper the longer you run it.

## Install

**Claude Code:** copy the folder to `~/.claude/skills/job-search-scout/`.
**Claude apps:** upload the packaged `job-search-scout.skill` in Settings → Capabilities → Skills (if your plan or organization allows custom skills).

Then copy `profile.example.yaml` to `profile.yaml`, fill it in, and ask: *"Run my job search."* With no profile, the skill will interview you and write one.

## Sources

The skill detects what's available and uses it:

| Source | Needs |
|---|---|
| Indeed | the Indeed connector |
| Dice | the Dice connector |
| Built In | web fetch (no connector) |
| Greenhouse / Lever / Ashby job pages | web search (fallback for anything) |

Missing a connector degrades coverage; it doesn't stop the run. The briefing says which sources ran.

## Why not LinkedIn?

LinkedIn is the biggest job board, and this skill deliberately doesn't search it.

- **There is no public job-search API.** LinkedIn's Jobs API is for *posting* jobs and managing applications, and it is limited to approved applicant-tracking-system and enterprise HR partners. Individual developers can get access only to their own profile data. Data-extraction use cases are not approved.
- **Its terms prohibit automated access.** Section 8.2 of the LinkedIn User Agreement forbids using "software, devices, scripts, robots or any other means or processes (such as crawlers, browser plugins and add-ons…) to scrape or copy the Services." An agent fetching LinkedIn job pages on your behalf is exactly that.
- **It enforces this.** LinkedIn has sued scrapers repeatedly: hiQ Labs (2017–2022, ending in a settlement and a permanent ban), Mantheos (2022), Proxycurl (2025, shut down under an injunction) and ProAPIs (settled 2026). Accounts tied to automated access are routinely restricted or banned, and the account at risk would be yours.

What you *can* do: when you find a role on LinkedIn yourself, paste the posting text into the conversation. The skill will run the same screens on it — disguised sales roles, base-vs-OTE, employer reputation — without anything touching LinkedIn.

## Running it on a schedule

Scheduled runs usually execute in a cloud environment with no access to your laptop. Two consequences:

1. Put your resume in `resume.text`, not `resume.path`.
2. The profile must reach the run. Either paste the profile into the scheduled task's prompt, or keep it somewhere the run can read (a connected folder, a private gist via URL).

## Privacy

Two kinds of file this skill produces should never be published:

- **Your profile** (`profile.yaml`): your resume and pay expectations.
- **Run outputs** (`briefing.md`, `ledger.md`, the rendered email, run logs). These name real employers next to reputation notes — layoff figures, review scores, verdicts like "AVOID". They're dated, attributed notes for your own decision-making, not published claims, and an employer seeing its name labelled that way in a public repo could reasonably object.

The `.gitignore` excludes all of these. Your ledger and reputation findings belong in your private `profile.yaml` (or a private gist), never in a fork of this repo. If you want to share what the skill does, share the method; if you want to share an example briefing, use fictional employers like the example profile does.

## Limitations

- Job-board coverage is uneven outside tech; the web-search fallback helps but is slower.
- Reputation research reflects what's findable publicly and can lag. Labels tell you how confident each note is.
- Dice's terms require an AI-retrieval disclosure, which the briefing includes.
- Respect each site's terms. The skill uses only the fetch and search tools the agent runtime provides.

## License

MIT — see `LICENSE`.
