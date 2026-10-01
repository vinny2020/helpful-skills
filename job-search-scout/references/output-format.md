# Output format

## Chat briefing

Title: **🔍 Job Search – <weekday, month day, year>** (or the profile's subject pattern).

Directly under the title:
1. **Coverage note** (one line, grey in email): only when a source was skipped, or failed and recovered. Name the sources.
2. **Bottom line** box: the `TOP PICK` roles (one or two — roles combining strong fit, pay above floor, and clean reputation), one sentence each on why; then which employers moved down on reputation grounds and why, briefly.

Then one section per `targets[].group`, in profile order. Within a section:

- Order by **fit and reputation together**, not stack fit alone. Deprioritized roles go last.
- Cap at `output.max_per_section`. Name the overflow in a single trailing line ("Also qualifying but not listed: …") rather than listing everything.
- Collapse near-duplicate reqs from one employer into the best one, with "N more near-identical reqs at the same band".

Per role:
- **Title** linked to the apply URL, exactly as the source returned it — query parameters included.
- Company · Location/workplace (`Remote`, `Hybrid, <metro>`, `On-site, <metro>`) · Salary (base; `$X–$Y base / $A–$B OTE` when they differ; "not listed" when absent) · Source(s) · Posted date (approximate is fine; say "~").
- **Why it fits** — one sentence, specific to the candidate. Name the overlapping skills from the listing's skills field, tie the scope to something on their resume, and call out relocation, travel or a pay tier explicitly.
- **Reputation (LABEL)** — one or two sentences per `reputation.md`.
- Badge: `TOP PICK` or `DEPRIORITIZED` where applicable.

Close with:
- "N roles surfaced across M searches (<sources>)."
- Filter tally: how many excluded by the disguise screen, how many as staffing funnels, plus any previously adjudicated reqs that reappeared and were skipped.
- One sentence on what VERIFIED vs DIRECTIONAL means.
- The Dice disclosure line, when Dice results are included.
- The ledger block (SKILL.md §9).

Tone: professional and conversational. Don't pad with roles that clearly don't match.

## Email

Use `scripts/render_email.py` rather than hand-writing HTML, so escaping and colour rules stay consistent between runs. Its input is a JSON file; the expected shape is documented at the top of the script.

Colour rules the script applies (keep them if you ever render by hand):
- Reputation labels: green `#1a7f37` for VERIFIED good, red `#b42318` for VERIFIED caution/mixed/avoid, amber `#8a6100` for DIRECTIONAL, UNKNOWN and YOUR CALL.
- `TOP PICK` gets a green pill; `DEPRIORITIZED` gets a red pill and `opacity:0.72` on the whole block.
- System font stack, ~15px, inline styles only, no images, no tracking pixels.

Subject lines and headings carry **literal** emoji. Email connectors take JSON strings, and an escape like `\U0001F50D` arrives as ten literal characters.

If nothing qualified, still send: say so, and list the searches run and the sources that were unavailable.
