#!/usr/bin/env python3
"""Render a job-search briefing JSON into email HTML, plain text, and a subject line.

Usage:
    python render_email.py briefing.json [--out-dir DIR] [--max-per-section N]

Writes DIR/email.html, DIR/email.txt and DIR/subject.txt (UTF-8). Standard library only.

--max-per-section N turns the email into a digest: each section keeps its first N roles
(the briefing JSON should already be in rank order) and the rest are named in one line.
Email tools take the body as a string, so a smaller email is a smaller, safer tool call.

Input shape (fields marked ? are optional):

{
  "subject": "🔍 Job Search – Monday, March 2, 2026",   # literal emoji
  "coverage_note"?: "Indeed unavailable today; Dice and Built In ran.",
  "bottom_line": {
    "top_picks": ["Example Robotics — Staff Data Engineer (Remote, $190K–$240K). Why…"],
    "dropped"?: "Sample Analytics Co (reported 12% layoff) …"   # text only: the script adds
                                                      # the "Moved down on reputation:" prefix
  },
  "sections": [
    {
      "name": "Principal / Staff Engineer Roles",
      "roles": [
        {
          "title": "Staff Data Engineer",
          "url": "https://…",
          "company": "Example Robotics",
          "location": "Remote, US",
          "salary"?: "$190K–$240K",
          "source": "Built In",
          "posted"?: "~Sep 14",
          "why": "Top Skills are Python, dbt, Airflow …",
          "reputation": {
            "label": "VERIFIED — GOOD",       # shown verbatim
            "tone"?: "good",                  # good | caution | neutral | plain;
                                              # inferred from the label when omitted
            "note": "Reviews describe …"
          },
          "badge"?: "TOP PICK"                # TOP PICK | DEPRIORITIZED | null
        }
      ],
      "overflow"?: "Also qualifying but not listed: …"
    }
  ],
  "footer": {
    "summary": "31 roles surfaced across 15 searches (Dice + Built In).",
    "filters"?: "Filtered out: 3 disguised sales roles, 12 staffing funnels.",
    "label_legend"?: "VERIFIED means …",
    "disclosure"?: "Job listings were retrieved using AI-powered search — verify …",
    "notes"?: ["Two previously adjudicated reqs reappeared and were skipped."]
  }
}
"""

import argparse
import html
import json
import sys
from pathlib import Path

GREEN, RED, AMBER = "#1a7f37", "#b42318", "#8a6100"
GREY = "#444444"
TONE_COLOR = {"good": GREEN, "caution": RED, "neutral": AMBER, "plain": GREY}


def infer_tone(label):
    """Map a reputation label to a colour tone when the JSON doesn't set one."""
    up = (label or "").upper()
    if any(w in up for w in ("DIRECTIONAL", "UNKNOWN", "YOUR CALL")):
        return "neutral"
    if "GOOD" in up:
        return "good"
    if any(w in up for w in ("CAUTION", "AVOID", "MIXED")):
        return "caution"
    return "plain"   # bare VERIFIED: confirmed, but neither good nor bad
BADGE_COLOR = {"TOP PICK": GREEN, "DEPRIORITIZED": RED}

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif")


def e(text):
    """Escape text for HTML element content."""
    return html.escape(str(text or ""), quote=False)


def attr(text):
    """Escape text for an HTML attribute value (keeps & in URLs valid as &amp;)."""
    return html.escape(str(text or ""), quote=True)


def check_subject(subject):
    # Catch the bug this script exists to prevent: Python-style escapes that a
    # JSON-taking email connector would deliver verbatim.
    if "\\U0" in subject or "\\u" in subject:
        sys.exit(
            "subject contains a literal backslash escape (e.g. \\U0001F50D). "
            "Use the actual emoji character instead."
        )


def role_html(r):
    badge = r.get("badge")
    dim = badge == "DEPRIORITIZED"
    rep = r.get("reputation") or {}
    color = TONE_COLOR.get(rep.get("tone") or infer_tone(rep.get("label")), AMBER)

    pill = ""
    if badge in BADGE_COLOR:
        pill = (
            f' <span style="background:{BADGE_COLOR[badge]};color:#fff;font-size:11px;'
            f'padding:2px 7px;border-radius:9px;font-weight:600">{e(badge)}</span>'
        )

    meta = " &middot; ".join(
        e(x) for x in [
            r.get("company"), r.get("location"),
            r.get("salary") or "Salary not listed",
            r.get("source"), r.get("posted") and f"Posted {r['posted']}",
        ] if x
    )

    style = "margin:0 0 20px" + (";opacity:0.72" if dim else "")
    return (
        f'<div style="{style}">'
        f'<div><a href="{attr(r.get("url"))}" style="font-size:16px;font-weight:600;'
        f'color:#0a58ca;text-decoration:none">{e(r.get("title"))}</a>{pill}</div>'
        f"<div>{meta}</div>"
        f'<div><em>Why it fits:</em> {e(r.get("why"))}</div>'
        f'<div><strong>Reputation (<span style="color:{color}">{e(rep.get("label", "UNKNOWN"))}'
        f"</span>):</strong> {e(rep.get('note'))}</div>"
        "</div>"
    )


def render_html(b):
    out = [
        f'<div style="font-family:{FONT};font-size:15px;line-height:1.55;color:#1a1a1a;max-width:760px">',
        f'<h1 style="font-size:24px;margin:0 0 6px">{e(b["subject"])}</h1>',
    ]
    if b.get("coverage_note"):
        out.append(f'<div style="color:#777;font-size:13px;margin:0 0 16px">{e(b["coverage_note"])}</div>')

    bl = b.get("bottom_line") or {}
    picks = bl.get("top_picks") or []
    if picks or bl.get("dropped"):
        out.append(
            '<div style="border:1px solid #d6d6d6;background:#f7f7f5;border-radius:6px;'
            'padding:14px 16px;margin:0 0 24px">'
            '<div style="font-weight:600;margin-bottom:8px">Bottom line after reputation screening</div>'
        )
        for i, p in enumerate(picks, 1):
            out.append(f'<div style="margin-bottom:6px">{i}. {e(p)}</div>')
        if bl.get("dropped"):
            out.append(f'<div style="margin-top:8px"><strong>Moved down on reputation:</strong> {e(bl["dropped"])}</div>')
        out.append("</div>")

    for s in b.get("sections", []):
        out.append(
            '<h2 style="font-size:19px;border-bottom:2px solid #1a1a1a;padding-bottom:5px;'
            f'margin:0 0 18px">{e(s["name"])}</h2>'
        )
        roles = s.get("roles") or []
        if not roles:
            out.append('<div style="color:#555;margin:0 0 20px">No qualifying roles today.</div>')
        out.extend(role_html(r) for r in roles)
        if s.get("overflow"):
            out.append(
                '<div style="color:#555;font-size:13.5px;margin:0 0 28px;padding-left:12px;'
                f'border-left:3px solid #ddd">{e(s["overflow"])}</div>'
            )

    f = b.get("footer") or {}
    out.append('<hr style="border:0;border-top:1px solid #ddd;margin:0 0 16px">')
    if f.get("summary"):
        out.append(f'<div style="margin-bottom:10px"><strong>{e(f["summary"])}</strong></div>')
    for key in ("filters",):
        if f.get(key):
            out.append(f'<div style="margin-bottom:10px">{e(f[key])}</div>')
    for n in f.get("notes") or []:
        out.append(f'<div style="margin-bottom:10px;color:#444;font-size:13.5px">{e(n)}</div>')
    if f.get("label_legend"):
        out.append(f'<div style="margin-bottom:10px;color:#444;font-size:13.5px">{e(f["label_legend"])}</div>')
    if f.get("disclosure"):
        out.append(f'<div style="color:#777;font-size:12.5px;font-style:italic">{e(f["disclosure"])}</div>')
    out.append("</div>")
    return "\n".join(out)


def render_text(b):
    lines = [b["subject"], ""]
    if b.get("coverage_note"):
        lines += [f"Coverage: {b['coverage_note']}", ""]
    bl = b.get("bottom_line") or {}
    if bl.get("top_picks") or bl.get("dropped"):
        lines.append("BOTTOM LINE AFTER REPUTATION SCREENING")
        lines += [f"{i}. {p}" for i, p in enumerate(bl.get("top_picks") or [], 1)]
        if bl.get("dropped"):
            lines.append(f"Moved down on reputation: {bl['dropped']}")
        lines.append("")
    for s in b.get("sections", []):
        lines += ["=" * 20, s["name"].upper(), "=" * 20, ""]
        for i, r in enumerate(s.get("roles") or [], 1):
            badge = f"[{r['badge']}] " if r.get("badge") else ""
            rep = r.get("reputation") or {}
            meta = " | ".join(x for x in [
                r.get("location"), r.get("salary") or "salary not listed",
                r.get("source"), r.get("posted") and f"Posted {r['posted']}",
            ] if x)
            lines += [
                f"{i}. {badge}{r.get('title')} - {r.get('company')}",
                f"   {meta}",
                f"   Fit: {r.get('why')}",
                f"   Reputation ({rep.get('label', 'UNKNOWN')}): {rep.get('note', '')}",
                f"   {r.get('url')}",
                "",
            ]
        if s.get("overflow"):
            lines += [s["overflow"], ""]
    f = b.get("footer") or {}
    lines.append("=" * 20)
    for key in ("summary", "filters"):
        if f.get(key):
            lines += [f[key], ""]
    for n in f.get("notes") or []:
        lines += [n, ""]
    for key in ("label_legend", "disclosure"):
        if f.get(key):
            lines += [f[key], ""]
    return "\n".join(lines).rstrip() + "\n"


def digest(b, n):
    """Keep the first n roles per section; fold the rest into the overflow line."""
    for s in b.get("sections", []):
        roles = s.get("roles") or []
        if len(roles) <= n:
            continue
        rest = roles[n:]
        named = "; ".join(
            f"{r.get('title')} — {r.get('company')}"
            + (f" ({r['salary']})" if r.get("salary") else "")
            + (" [deprioritized]" if r.get("badge") == "DEPRIORITIZED" else "")
            for r in rest
        )
        line = f"Also in today's full briefing: {named}."
        s["overflow"] = f"{line} {s['overflow']}" if s.get("overflow") else line
        s["roles"] = roles[:n]
    return b


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("briefing", help="briefing JSON file")
    ap.add_argument("--out-dir", default=".", help="where to write email.html / email.txt / subject.txt")
    ap.add_argument("--max-per-section", type=int, default=0,
                    help="digest mode: keep N roles per section (0 = keep all)")
    args = ap.parse_args()

    b = json.loads(Path(args.briefing).read_text(encoding="utf-8"))
    if not b.get("subject"):
        sys.exit("briefing JSON needs a 'subject'")
    check_subject(b["subject"])
    if args.max_per_section > 0:
        b = digest(b, args.max_per_section)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "email.html").write_text(render_html(b), encoding="utf-8")
    (out / "email.txt").write_text(render_text(b), encoding="utf-8")
    (out / "subject.txt").write_text(b["subject"], encoding="utf-8")

    n = sum(len(s.get("roles") or []) for s in b.get("sections", []))
    print(f"rendered {n} roles in {len(b.get('sections', []))} sections -> {out}/email.html, email.txt, subject.txt")


if __name__ == "__main__":
    main()
