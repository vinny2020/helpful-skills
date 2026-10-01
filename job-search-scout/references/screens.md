# Screens

Body-level checks that search results can't answer. Run them on finalists, not on everything — see the budget rules at the end.

## Role-disguise screen (`pre_sales` dealbreaker)

Job boards routinely list pre-sales and solution-engineering roles under engineering titles. A real example: a "Staff Software Engineer" listing whose body required "a minimum of 5 years within a pre-sales environment," 25–30% travel, and commission-based pay. Its range looked unusually generous for the title — which is the tell.

Scan the body with this case-insensitive pattern, plus any `filters.custom_disguise_terms` from the profile:

```
(?i)(pre-?sales|solutions? engineer|solutions? consultant|sales engineer|sales cycle|close (business|deals)|quota|on.target earnings|\bOTE\b|commission plan|prospects?\b|discovery calls?|demo(nstration)?s to (executives|customers|prospects)|channel partners|account executive)
```

A hit is a reason to read closely, not a verdict. **Exclude** when the body shows any of:
- An explicit pre-sales / solutions / sales-engineering *experience requirement*.
- A quota, commission plan, or OTE structure asserted *of this role*.
- Core responsibilities framed around a sales cycle: closing business, working prospects with account executives, pre-sales proofs of concept, sales demos.

**Don't exclude** just because a role is customer-facing. Forward-deployed and deployment-engineering roles are legitimately embedded with customers. The test is whether success is measured in **shipped software** or in **closed revenue**. A role that builds tools *for* a sales team is engineering; a role that *is* part of the sales motion isn't.

**Boilerplate scoped to other roles isn't a flag.** Some large employers put "Sales positions generally offer an On Target Earnings (OTE) structure" in every posting, right after a separately stated base range. A conditional sentence about what sales positions get says nothing about this one.

**Corrupt postings.** Occasionally a body contains text belonging to a different company, or a role entirely different from the title. Exclude it and record it in the ledger so later runs skip it.

## Staffing-funnel screen (`staffing_funnel` dealbreaker)

Recruiter posts that hide the employer waste applications and often recycle stale reqs. Signals, roughly in order of strength:

- The body refers to "our client" or "a leading company" without naming it.
- The poster is a known agency (the profile's `ledger.staffing_funnels` list, built up over runs).
- Dice `employerType: "Recruiter"` with no employer named anywhere.
- The same generic title posted many times by one poster across unrelated locations, often with a suffix like "– Work From Home – M".
- Hourly ranges on a role the candidate wants as full-time salaried.
- **Recruiters that look like employers.** Some firms post under their own name with a polished listing and a real band, but describe themselves as a "talent acquisition", "talent partner" or "staffing and consulting" firm in the body or on their own site; on Built In they often carry a "Professional Services, Consulting" industry tag with a thin skills list. Before ranking such a listing, check one source for what the company does.

A recruiter post that **names** the hiring company is fine — evaluate the employer, not the poster. Count funnel exclusions separately from disguise exclusions in the closing tally, so both screens' behaviour stays visible.

## Base vs. OTE

Apply `compensation.base_floor` and `workplace.relocation.min_base` to **base only**.

- When a body gives both, display both: `$165K–$216K base / $220K–$288K OTE`. The candidate wants to see the upside even though the decision is made on base.
- Bonus and equity language ("may include cash bonus and/or long-term incentives") that follows a stated base is ordinary compensation, not OTE. Don't discount the base for it.
- "Total cash compensation inclusive of base salary and annual bonus" means the range includes bonus. If the role is borderline, note that base is lower than shown.
- Unverified single ranges are treated as base — but verify before ranking a role as a finalist.

## Currency

For employers headquartered outside the candidate's country, and for any role clearing the floor by less than ~10%, confirm the currency in the body before including it. Search listings have mislabelled CAD as USD.

## Clearance and travel

- `security_clearance`: exclude when the body requires an active clearance (TS/SCI, polygraph) the candidate doesn't list. "Eligible to obtain" is weaker — include, and note it.
- Travel above `filters.max_travel_pct` is a down-rank, stated in the why-it-fits line, not an exclusion.

## Budget

Verification calls are the scarce resource. In order:

1. **Ledger first.** If `ledger.adjudications` already holds a verdict for this req (match on source id, else employer + title), use it and spend nothing.
2. **Fails on its own? Skip.** A role already below the floor or outside acceptable locations is excluded without opening it.
3. **Then spend on:** roles about to rank near the top of a section; bands generous for the level; titles with Solution(s) / Field / Customer / Partner / Specialist / Forward Deployed; employers with large sales organizations.

Record every verdict you reach — KEEP or EXCLUDE, with a one-line reason — for the ledger block at the end of the run.
