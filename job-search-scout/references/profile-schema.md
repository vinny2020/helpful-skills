# Profile schema

The profile is a YAML file holding everything specific to one candidate. Only the fields marked **required** must be present; everything else has the default shown.

Keep the profile out of public repositories — it contains a resume and salary expectations. The repo's `.gitignore` excludes `profile.yaml` for this reason.

```yaml
candidate:
  name: "Sam Okafor"               # used in the briefing greeting only
  home_metro: "Chicago, IL"         # REQUIRED — anchors hybrid/on-site searches
  country_code: "US"                # default "US"

resume:                             # REQUIRED — at least one of the three
  text: |                           # preferred: works in cloud/scheduled runs
    ...paste the resume...
  path: "~/Documents/resume.md"     # works only where that file is reachable
  url: "https://example.com/cv"     # fetched with web_fetch

summary:                            # optional — overrides resume extraction
  current_title: "Senior Data Engineer"
  core_skills: [Python, SQL, dbt, Airflow, Spark]
  domains: [healthcare, logistics]
  past_employers: [Northwind Health, Contoso Freight]   # get the YOUR CALL reputation label
  not_experienced_in: [pre-sales]           # informs the role-disguise screen

targets:                            # REQUIRED — one entry per briefing section
  - group: "Data Engineering Leadership"
    titles: ["Data Engineering Manager", "Manager, Analytics Engineering"]
  - group: "Staff / Lead Data Engineer"
    titles: ["Staff Data Engineer", "Lead Data Engineer", "Senior Analytics Engineer"]
    search_phrases: ["staff data engineer dbt"]   # optional explicit queries

workplace:
  priority: [remote, hybrid, onsite]        # order = ranking preference
  hybrid_metros: ["Chicago, IL", "Evanston, IL"]   # default: [home_metro]
  onsite_metros: ["Chicago, IL"]                 # default: [home_metro]
  relocation:
    willing: false
    min_base: 200000                # relocate only when base max ≥ this

compensation:                       # REQUIRED: base_floor
  currency: "USD"
  base_floor: 150000                # compared against BASE max, never OTE
  show_ote: true                    # show "$X base / $Y OTE" when they differ

filters:
  dealbreakers:                     # each maps to a check in screens.md
    - pre_sales                     # sales/solutions roles under engineering titles
    - security_clearance            # roles requiring a clearance the candidate lacks
    - staffing_funnel               # recruiter posts with no identifiable employer
  exclude_specializations: [embedded, mainframe, RF]
  exclude_companies: []
  max_travel_pct: 30                # down-rank above this; don't exclude
  custom_disguise_terms: []         # extra regex terms for the disguise screen

boosts:
  skills: [dbt, Airflow, Spark]            # added to resume-derived skills
  domains: [cybersecurity, fintech]
  preferred_companies: []

reputation:
  enabled: true
  hard_flag:                        # any one of these → DEPRIORITIZED
    layoff_pct_12mo: 10
    declining_revenue_guidance: true
    quiet_layoffs: true             # cuts deliberately kept under WARN thresholds
    comp_band_cuts: true
  caution:                          # labelled CAUTION, ranked lower, not dimmed
    rating_below: 3.5               # Glassdoor-style 5-point rating
    recommend_below: 60             # % who'd recommend to a friend
  reverify_after_days: 30
  verify_top_n_per_section: 2       # minimum real reads per section
  known:                            # carried-forward findings
    - employer: "Example Corp"
      finding: "Rating 4.4 / 210 reviews, 86% recommend"
      label: "VERIFIED — GOOD"
      as_of: "2026-09-14"

sources:
  enabled: [indeed, dice, builtin, web]     # default: all available
  disabled: []
  builtin_urls: []                  # optional explicit Built In search URLs
  limits:                           # optional per-source call caps
    indeed: 2                       # Indeed is slow (1 call/min) and thin for senior tech

output:
  max_per_section: 12
  top_picks: 2
  delivery:
    chat: true
    email:
      enabled: false
      to: "you@example.com"
      subject: "🔍 Job Search – {date}"     # literal emoji, not an escape
      max_per_section: 6            # email is a digest; the chat briefing stays full

ledger:                             # grows run over run; see SKILL.md §9
  auto_update: false
  adjudications:
    - employer: "Example Corp"
      title: "Staff Engineer, Platform"
      id: "dice:00000000-example"         # source-prefixed id when available
      verdict: EXCLUDE              # KEEP | EXCLUDE
      reason: "Body requires 5 years pre-sales; OTE comp"
      as_of: "2026-09-28"
  staffing_funnels: []              # poster names the candidate has seen funnel
```

## Defaults when a field is absent

| Field | Default |
|---|---|
| `workplace.priority` | `[remote, hybrid, onsite]` |
| `workplace.hybrid_metros`, `onsite_metros` | `[candidate.home_metro]` |
| `workplace.relocation.willing` | `false` |
| `filters.dealbreakers` | `[staffing_funnel]` |
| `reputation.enabled` | `true` |
| `reputation.hard_flag.layoff_pct_12mo` | `10` |
| `output.max_per_section` | `12` |
| `output.top_picks` | `2` |
| `output.delivery.email.enabled` | `false` |
| `output.delivery.email.max_per_section` | `6` |
| `sources.limits.indeed` | remote queries + one metro query |

## Validation

Before searching, confirm the required fields exist and are sane: a floor that is a number, at least one target group with at least one title, and a resume source. If `resume.text` is empty and the only other source is a local `path`, warn — in an unattended cloud run it will be unreachable, and the run will fall back to `summary`. That fallback works, but the briefing's why-it-fits lines get less specific, so the warning should tell the candidate to paste the text in.
