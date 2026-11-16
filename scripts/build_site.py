#!/usr/bin/env python3
"""Build the GitHub Pages site and markdown mirrors from data/*.json.

Only values present in data/*.json are rendered. Blank cells stay blank.
Run from the repository root:  python3 scripts/build_site.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

TOURNEY = json.loads((DATA / "tournaments.json").read_text(encoding="utf-8"))
HOTELS = json.loads((DATA / "hotels.json").read_text(encoding="utf-8"))

E = html.escape


def money(s):
    """Parse the first dollar amount in a string, supporting K and M suffixes."""
    if not s:
        return None
    m = re.search(r"\$([\d,]+(?:\.\d+)?)\s*([KkMm]?)", s)
    if not m:
        return None
    v = float(m.group(1).replace(",", ""))
    suffix = m.group(2).lower()
    if suffix == "k":
        v *= 1_000
    elif suffix == "m":
        v *= 1_000_000
    return v


def ratio(row):
    g = money(row.get("guarantee", ""))
    b = money(row.get("buy_in", ""))
    if g and b:
        return g / b
    return None


def fmt_ratio(r):
    return "" if r is None else f"{r:,.1f}x"


def link(url, label):
    if not url:
        return E(label) if label else ""
    return f'<a href="{E(url)}" rel="noopener">{E(label or "Official source")}</a>'


def flags_html(flags):
    if not flags:
        return ""
    items = "".join(f"<li>{E(f)}</li>" for f in flags)
    return f'<ul class="flags">{items}</ul>'


def page(title, body, active):
    nav_items = [
        ("index.html", "Home"),
        ("tournaments.html", "Tournaments"),
        ("hotels.html", "Hotels"),
        ("schedule.html", "Daily schedule"),
        ("dashboard.html", "Dashboard"),
        ("summary.html", "Summary"),
        ("flagged.html", "Flagged for Review"),
    ]
    nav = "".join(
        f'<a href="{href}"{" class=active" if href == active else ""}>{E(lbl)}</a>'
        for href, lbl in nav_items
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} · Poker5 Las Vegas</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="brand"><a href="index.html">Poker5 · Las Vegas Strip</a></div>
  <nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer>
  <p>Data as of 2026-11-16 (America/Los_Angeles). Every value is sourced to an official page or left blank and flagged. Built from <code>data/*.json</code> by <code>scripts/build_site.py</code>.</p>
</footer>
</body>
</html>
"""


def tourney_table(rows, show_category=False, show_ratio=True):
    head = ["Venue", "Event", "Name", "Date", "Start", "Buy-in", "Guarantee"]
    if show_category:
        head.insert(3, "Category")
    if show_ratio:
        head.append("Guarantee ÷ buy-in")
    head += ["Pool / rules", "Source", "Flags"]
    th = "".join(f"<th>{E(h)}</th>" for h in head)
    trs = []
    for r in rows:
        cells = [
            E(r.get("venue", "")),
            E(r.get("event", "")),
            E(r.get("name", "")),
        ]
        if show_category:
            cells.append(E(r.get("category", "")))
        cells += [
            E(r.get("date", "")),
            E(r.get("start", "")),
            E(r.get("buy_in", "")),
            E(r.get("guarantee", "")),
        ]
        if show_ratio:
            cells.append(E(fmt_ratio(ratio(r))))
        cells += [
            E(" ".join(x for x in [r.get("pool_note", ""), r.get("entry_rule", "")] if x)),
            link(r.get("source_url", ""), r.get("source_label", "")),
            flags_html(r.get("flags", [])),
        ]
        tds = "".join(f"<td>{c}</td>" for c in cells)
        trs.append(f"<tr>{tds}</tr>")
    return f'<div class="table-wrap"><table class="data"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def ranked(rows):
    """Sort by guarantee ÷ buy-in (descending). Rows without the ratio go last, in file order."""
    with_r = [(ratio(r), i, r) for i, r in enumerate(rows) if ratio(r) is not None]
    without = [r for r in rows if ratio(r) is None]
    with_r.sort(key=lambda t: (-t[0], t[1]))
    return [t[2] for t in with_r] + without


MAIN = ranked(TOURNEY["rows"])
SEPARATE = ranked(TOURNEY["separate"])
RESTRICTED = TOURNEY["restricted"]
UNVERIFIED = TOURNEY["unverified"]


def build_index():
    body = f"""
<section class="hero">
  <h1>Single-entry poker near the Las Vegas Strip</h1>
  <p>Official-source tournament and hotel data for November–December 2026. Values are filled only when an official page confirms them. Everything else is blank and flagged.</p>
  <div class="cta-row">
    <a class="btn" href="tournaments.html">Tournaments</a>
    <a class="btn" href="hotels.html">Hotels</a>
    <a class="btn" href="schedule.html">Daily schedule</a>
    <a class="btn ghost" href="flagged.html">Flagged for Review</a>
  </div>
</section>
<section class="cards">
  <div class="card"><span class="num">{len(MAIN)}</span><span>Single-entry rows (main list)</span></div>
  <div class="card"><span class="num">{len(SEPARATE)}</span><span>Multi-entry, add-on, or spend-to-gain rows</span></div>
  <div class="card"><span class="num">{len(RESTRICTED)}</span><span>Restricted-eligibility events</span></div>
  <div class="card"><span class="num">{len(HOTELS['rows'])}</span><span>Hotels listed ({sum(1 for h in HOTELS['rows'] if h.get('resort_fee_per_night'))} with official fee)</span></div>
</section>
<section>
  <h2>What this site covers</h2>
  <ul>
    <li><strong>Main list:</strong> events with a single entry on the official sheet. Ranked by guarantee ÷ buy-in.</li>
    <li><strong>Separate list:</strong> double buy-in, re-entry, add-on, or optional paid chips for advantage. Kept apart from the main list.</li>
    <li><strong>Hotels:</strong> only official resort fees are shown. Room rates and walking times were not verified, so true nightly cost and ranking are blank.</li>
    <li><strong>Gaps:</strong> Horseshoe, ARIA, MGM Grand, Planet Hollywood, Golden Nugget, and Resorts World are not verified. See the summary.</li>
  </ul>
  <p>Read the <a href="summary.html">executive summary</a>, including suggestions and open questions. Items that need review are on <a href="flagged.html">Flagged for Review</a>.</p>
</section>
"""
    return page("Home", body, "index.html")


def build_tournaments():
    body = f"""
<section>
  <h1>Tournaments</h1>
  <p>Ranked by guarantee ÷ buy-in. Some guarantees include bounty money, which is noted per row. Blank cells were not verified.</p>
  <h2>Main list: single-entry</h2>
  {tourney_table(MAIN)}
  <h2>Separate list: double buy-in, re-entry, add-on, or spend-to-gain</h2>
  <p>Not single-entry. Read the entry rules before you register. Ratios are shown for comparison only; re-entry makes guarantees misleading as a value measure.</p>
  {tourney_table(SEPARATE, show_category=True)}
  <h2>Restricted eligibility (not ranked)</h2>
  {tourney_table(RESTRICTED, show_ratio=False)}
  <h2>Listed but not verified (no buy-in published, no row)</h2>
  <ul>{"".join(f"<li><strong>{E(r.get('venue',''))} — {E(r.get('name',''))}</strong> ({E(r.get('date',''))}; guarantee {E(r.get('guarantee','') or 'blank')}): {E(r.get('reason',''))}</li>" for r in UNVERIFIED)}</ul>
</section>
"""
    return page("Tournaments", body, "tournaments.html")


def unverified_table(rows):
    th = "".join(f"<th>{E(h)}</th>" for h in ["Venue", "Name", "Date", "Buy-in", "Guarantee", "Why not verified"])
    trs = []
    for r in rows:
        tds = "".join(
            f"<td>{E(r.get(k, ''))}</td>"
            for k in ["venue", "name", "date", "buy_in", "guarantee", "reason"]
        )
        trs.append(f"<tr>{tds}</tr>")
    return f'<div class="table-wrap"><table class="data"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def build_hotels():
    th = "".join(
        f"<th>{E(h)}</th>"
        for h in ["Hotel", "Area", "Room rate / night", "Resort fee / night", "Parking", "True nightly cost", "Walk to tournament venue", "Source", "Flags"]
    )
    trs = []
    no_source = [r for r in HOTELS["rows"] if not r.get("source_url")]
    for r in [x for x in HOTELS["rows"] if x.get("source_url")]:
        tds = [
            E(r["hotel"]),
            E(r.get("area", "")),
            E(r.get("room_rate_per_night", "")),
            E(r.get("resort_fee_per_night", "")),
            E(r.get("parking", "")),
            E(r.get("true_nightly_cost", "")),
            E(r.get("walk_to_tournament_venue", "")),
            link(r.get("source_url", ""), r.get("source_label", "")),
            flags_html(r.get("flags", [])),
        ]
        trs.append("<tr>" + "".join(f"<td>{c}</td>" for c in tds) + "</tr>")
    body = f"""
<section>
  <h1>Hotels</h1>
  <p>{E(HOTELS['note'])}</p>
  <p><strong>True nightly cost</strong> = {E(HOTELS['cost_formula'])}</p>
  <div class="table-wrap"><table class="data"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>
  <h2>No official source found (not in table)</h2>
  <ul>{"".join(f"<li><strong>{E(r['hotel'])}</strong>: {E(' '.join(r.get('flags', [])))}</li>" for r in no_source)}</ul>
</section>
"""
    return page("Hotels", body, "hotels.html")


def build_schedule():
    # Gather every row with a start time. Each row is a candidate; the user picks one per start window.
    candidates = []
    for r in MAIN + SEPARATE + RESTRICTED:
        st = r.get("start", "")
        if not st:
            continue
        first = re.search(r"(\d{1,2}:\d{2}\s*[AP]M)", st)
        if not first:
            continue
        candidates.append((first.group(1), r))

    def key(item):
        t = item[0]
        h, rest = t.split(":")
        mins = int(h) % 12 * 60 + int(rest[:2]) + (720 if "PM" in t.upper() else 0)
        return mins

    candidates.sort(key=key)
    windows = {}
    for t, r in candidates:
        windows.setdefault(t, []).append(r)

    rows = []
    rows.append(
        '<tr><td>8:00 AM</td><td colspan="4"><em>Planning block (not sourced): breakfast and travel. Travel times are not verified.</em></td></tr>'
    )
    for t in sorted(windows, key=lambda x: key((x, None))):
        items = []
        for r in windows[t]:
            label = f'{r.get("venue", "")} · {r.get("name", "")}'
            cat = r.get("category", "Single-entry" if r in MAIN else ("Restricted" if r in RESTRICTED else ""))
            items.append(f'<li><strong>{E(label)}</strong> <span class="pill">{E(cat or "Single-entry")}</span> · buy-in {E(r.get("buy_in", "blank"))} · date {E(r.get("date", "blank") or "blank")}</li>')
        rows.append(f"<tr><td>{E(t)}</td><td colspan='4'><ul class='plain'>{''.join(items)}</ul></td></tr>")

    body = f"""
<section>
  <h1>Daily schedule (starting 8:00 AM)</h1>
  <p>This is a menu of verified start times, not a booked plan. Each row lists events that start in the same window. <strong>Choose at most one per window.</strong> Event lengths and travel times were not verified, so end times are blank and overlaps are possible. Dates for recurring events depend on the day of the week. Check the source before you play.</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Start</th><th colspan="4">Candidate events (pick one)</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
</section>
"""
    return page("Daily schedule", body, "schedule.html")


def build_dashboard():
    total_main = len(MAIN)
    total_sep = len(SEPARATE)
    total_res = len(RESTRICTED)
    total_unv = len(UNVERIFIED)
    fees_verified = sum(1 for h in HOTELS["rows"] if h.get("resort_fee_per_night") and h.get("source_url"))
    flagged_count = sum(len(r.get("flags", [])) for r in MAIN + SEPARATE + RESTRICTED + HOTELS["rows"])
    rows_html = tourney_table(MAIN).replace('class="data"', 'class="data" id="main-table"')
    body = f"""
<section>
  <h1>Dashboard</h1>
  <div class="cards">
    <div class="card"><span class="num">{total_main}</span><span>Single-entry rows</span></div>
    <div class="card"><span class="num">{total_sep}</span><span>Multi-entry / add-on rows</span></div>
    <div class="card"><span class="num">{total_res}</span><span>Restricted rows</span></div>
    <div class="card"><span class="num">{total_unv}</span><span>Unverified listings</span></div>
    <div class="card"><span class="num">{fees_verified}</span><span>Hotels with official fee</span></div>
    <div class="card"><span class="num">{flagged_count}</span><span>Open flags (tournaments + hotels)</span></div>
  </div>
  <p><label for="filter">Filter main list:</label> <input id="filter" type="search" placeholder="Type venue, event, or buy-in" aria-label="Filter main list"></p>
  {rows_html}
</section>
<script>
(function () {{
  var input = document.getElementById('filter');
  var table = document.getElementById('main-table');
  if (!input || !table) return;
  input.addEventListener('input', function () {{
    var q = input.value.toLowerCase();
    var rows = table.tBodies[0].rows;
    for (var i = 0; i < rows.length; i++) {{
      rows[i].style.display = rows[i].textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
    }}
  }});
}})();
</script>
"""
    return page("Dashboard", body, "dashboard.html")


def build_summary():
    body = """
<section>
  <h1>Executive summary</h1>
  <p><strong>Scope:</strong> single-entry poker tournaments on or after 2026-11-16 near the Las Vegas Strip, with hotels within walking distance and a daily schedule starting 8 AM. Only official sources were used for values.</p>
  <p><strong>Result, honestly stated:</strong> this is a partial verification. Confirmed rows come mainly from The Venetian DeepStack Extravaganza IV, which publishes structure sheets, plus Bellagio, Wynn, and Caesars Palace official PDFs. Several venues have no usable official schedule (Horseshoe, ARIA, MGM Grand, Planet Hollywood, Golden Nugget, Resorts World). Those gaps are left blank.</p>
  <ul>
    <li><strong>Best single-entry value by guarantee ÷ buy-in (verified):</strong> Wynn daily $200 NLH Sat/Sun ($25K GTD, 125x; validity flagged), then Venetian $200 ValueTown Bounty ($20K GTD, 100x, event 58, Dec 19), then Wynn daily $200 Mon–Thu (50x; validity flagged), then Venetian $600 Big O ($25K GTD, 41.7x, Dec 3).</li>
    <li><strong>Re-entry and add-on events</strong> are listed separately. Their guarantees are large, but the buy-in is not the total cost, so they are not comparable with single-entry events.</li>
    <li><strong>Hotels:</strong> only the Venetian ($55 plus tax) and Wynn/Encore ($55 plus tax) resort fees are verified from official pages. Room rates and walking times were not verified, so nightly cost and ranking are blank. Do not use the hotel table to choose a hotel yet.</li>
    <li><strong>Schedule:</strong> the 8 AM menu uses verified start times only. Durations and travel are not verified, so it does not yet show a route that fits the most events.</li>
  </ul>
  <h2>Suggestions (for review, not implemented)</h2>
  <ol>
    <li>Add official hotel room rates: pull them from each property's booking engine for a fixed test date so nightly cost can be computed.</li>
    <li>Verify the remaining Venetian DSE IV structure sheets (events 02, 19, 20, 36, 42, 43, 47, 52, 56, 59, 63) and add rows only after line-by-line reading.</li>
    <li>Confirm Wynn's 2026 daily structures on a current page, since the poster in use is a 2025 asset.</li>
    <li>Obtain official Caesars Palace, Horseshoe, and Bellagio resort-fee pages and add them to the hotel table.</li>
    <li>Add a schedule builder that tests overlapping start windows against verified durations, once those durations are available.</li>
    <li>Add a "last verified" date to each row and a stale-data warning after 14 days.</li>
  </ol>
  <h2>Questions, missing information, and how to find it</h2>
  <table class="data">
    <thead><tr><th>Question</th><th>Why it matters</th><th>Suggested way to find out</th></tr></thead>
    <tbody>
      <tr><td>What is the 2026 schedule for Horseshoe, ARIA, MGM Grand, Planet Hollywood, Golden Nugget?</td><td>No official schedule was found, so these venues are blank.</td><td>Call each poker room. Ask for the current tournament calendar. Check each property's poker page for a PDF.</td></tr>
    <tr><td>Is Resorts World's poker room still open?</td><td>A third-party source reports it closed in March 2026. The official page shows dining only.</td><td>Call the property poker desk. Check the official poker page for a closure notice.</td></tr>
    <tr><td>Which Venetian event numbers are correct for the PKO and Day 1 events?</td><td>Sheets and the schedule disagree on event numbers.</td><td>Ask the Venetian Poker Room for the official event list. Check the event page for changes.</td></tr>
    <tr><td>What is the Bellagio Saturday buy-in?</td><td>The PDF says both $1,100 and $600.</td><td>Ask the Bellagio poker room, or check the poker page for a newer PDF.</td></tr>
    <tr><td>Which Wynn daily structures apply after Nov 16, 2026?</td><td>The poster is a 2025 asset. Daily tournaments are suspended during the WPT series.</td><td>Call the Wynn poker room. Check the Wynn poker page.</td></tr>
    <tr><td>What does a room rate cost for your dates?</td><td>Without a rate, true nightly cost cannot be computed.</td><td>Give your check-in and check-out dates. A dated rate search on each official booking page would fill this.</td></tr>
    <tr><td>How far is each hotel from each event room on foot?</td><td>Walk time is required for the 30-minute filter.</td><td>Use a walking route tool on each official address. Record the source and the date.</td></tr>
    <tr><td>Do you want to include events that are not single-entry in the main ranking?</td><td>The current rule keeps them separate, as requested.</td><td>No action needed unless your preference changes.</td></tr>
  </table>
</section>
"""
    body = body.replace("</table>", "</tbody></table>", 1) if "</tbody></table>" not in body and "</tbody>\n  </table>" not in body else body
    body = body.replace('<table class="data">', '<div class="table-wrap"><table class="data">').replace("</table>", "</table></div>")
    return page("Summary", body, "summary.html")


def build_flagged():
    items = [
        ("Venetian", "Event 01 appears on two structure sheets. One says Day A+C at 11:10 AM (Day 2 at 12 PM, $75K). The other says Day B+D at 5:10 PM (Day 2 at 12 PM, $75K). Both are listed in the separate section, with no date. Source: dse_nov_2026-structure_10.pdf and structure_9.pdf."),
        ("Venetian", "Structure sheet event 08 (PKO $200) does not match schedule summary numbering (#09, #11, #13, etc.). Date left blank. Source: dse_nov_2026-structure_30.pdf."),
        ("Venetian", "Event 39 (LIPS Ladies $800): schedule summary says Dec 9; structure sheet says Day 1 Dec 10, Day 2 Dec 11. Sheet used. Source: dse_nov_2026-structure_32.pdf."),
        ("Venetian", "Event 18 and event 58 share one sheet ($200 ValueTown Bounty). Date is verified only for event 58. PokerAtlas PRO discount applies to the first buy-in only. Source: dse_nov_2026-structure_8.pdf."),
        ("Venetian", "Schedule-only events not verified line-by-line in this pass (e.g., #02 $300 1-Day, #20 $300 PLO double-board bomb, #36 $800 bounty, #42 $300 bounty, #47 $2,200 title, #52 $1,100 PKO, #56 $1,100 NLH, #59 $600 NLH). Not published as rows."),
        ("Venetian", "Structure sheet file names do not always match event numbers printed inside them (e.g., structure_29 is event 06; structure_26 is event 17). Mapping was taken from the printed event number."),
        ("Bellagio", "Saturday $1,000 NLH PDF: heading says $1,100 buy-in, rule 07 says $600. Rule 04 names Day 2 as 9/13/26 (past date). Level 3 blind shows '200-4300' (typo). Buy-in left blank. Source: mgm-bellagio-poker-saturdays-$1000-nlh.pdf."),
        ("Bellagio", "Poker page notice mentions a tournament resuming on Saturday, July 26 at 2 PM, which is past. Notice may be stale. Source: bellagio.mgmresorts.com/en/casino/poker.html."),
        ("Bellagio", "Friday and Sunday PDFs do not print a guarantee. Left blank."),
        ("Wynn", "Daily tournament poster is a 2025 asset (v1752011166). Validity for 2026 not confirmed. Daily tournaments are suspended during the WPT World Championship (Nov 27–Dec 21, 2026) per the Wynn poker page."),
        ("Wynn", "WPT World Championship: Dec 9 $1,600 2-day event is on the schedule but not verified. Dec 13 Day 1A $10,400 (+$1M added) is not verified. Super Gold Million Mystery Bounty $400 (bounty rules and re-entry not confirmed)."),
        ("Wynn", "Resort fee language comes from a Feb 2026 promotion terms page, which has expired. Confirm on the live booking page before relying on it."),
        ("Caesars Palace", "Daily NLH flyer is a 2026 asset with no date range printed in the chunk read. Second chunk unread. Caesars Palace resort fee not found on official pages; third-party values conflict ($49.95, $55, $62.30 incl. tax)."),
        ("Caesars Horseshoe", "Official pages list no poker buy-ins or resort fee. Third-party fees conflict ($50, $56.63). Blank."),
        ("Resorts World", "Third-party source reports the poker room closed March 30, 2026. Official page shows dining only. Not confirmed; not used as a tournament venue."),
        ("MGM Grand", "Official poker page returned 404. No values published."),
        ("Planet Hollywood", "Official poker page returned HTTP 500. Third-party data is from 2025. No values published."),
        ("ARIA", "Official poker page has no schedule; directs guests to call or @ARIAPoker. Third-party $200 daily is not used."),
        ("Repository", "Repository contained only README.md at start. There was no existing data to review line-by-line. Sibling branches (arena/2ed7df1a, 3dfaf2a5, 66cdf731, 9c91bba7, aa83f1e1, b50aa7f5, cd5ab298) claim overlapping research and site tasks. Not edited."),
        ("Process", "Branch name is fixed by Arena (arena/053f694f-poker5) and does not follow the session-<id>/<task> pattern in COORDINATION.md. Logged here."),
    ]
    lis = "".join(f"<li><strong>{E(k)}:</strong> {E(v)}</li>" for k, v in items)
    body = f"""
<section>
  <h1>Flagged for Review</h1>
  <p>These items do not block publication. Each one is a value that is blank, a conflict between sources, or a sign of a stale source. Please review before relying on the data.</p>
  <ol class="flag-list">{lis}</ol>
</section>
"""
    return page("Flagged for Review", body, "flagged.html")


CSS = """
:root { --bg:#0f1514; --panel:#172120; --ink:#e8efee; --muted:#9db3af; --accent:#45c1a0; --warn:#f2b84b; --line:#2a3a38; }
@media (prefers-color-scheme: light) {
  :root { --bg:#f6f8f7; --panel:#ffffff; --ink:#172120; --muted:#4c6461; --accent:#127c63; --warn:#8a5a00; --line:#d6e0de; }
}
* { box-sizing: border-box; }
body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:var(--bg); color:var(--ink); line-height:1.5; }
a { color:var(--accent); }
.site-header { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px; padding:16px 24px; border-bottom:1px solid var(--line); }
.brand a { font-weight:700; text-decoration:none; color:var(--ink); }
nav { display:flex; flex-wrap:wrap; gap:14px; }
nav a { text-decoration:none; color:var(--muted); font-size:14px; }
nav a.active, nav a:hover { color:var(--accent); }
main { max-width:1200px; margin:0 auto; padding:24px; }
h1 { font-size:28px; margin:8px 0 12px; }
h2 { font-size:20px; margin:28px 0 10px; }
.hero { padding:24px 0 8px; }
.hero p { color:var(--muted); max-width:720px; }
.cta-row { display:flex; flex-wrap:wrap; gap:10px; margin-top:12px; }
.btn { display:inline-block; padding:9px 16px; border-radius:6px; background:var(--accent); color:#06120f; text-decoration:none; font-weight:600; }
.btn.ghost { background:transparent; color:var(--accent); border:1px solid var(--accent); }
.cards { display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:12px; margin:18px 0; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px; display:flex; flex-direction:column; gap:4px; }
.card .num { font-size:28px; font-weight:700; color:var(--accent); }
.card span:last-child { color:var(--muted); font-size:14px; }
.table-wrap { overflow-x:auto; border:1px solid var(--line); border-radius:8px; background:var(--panel); margin:10px 0 20px; }
table.data { border-collapse:collapse; width:100%; font-size:14px; }
table.data th, table.data td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }
table.data th { background:rgba(127,127,127,0.12); font-weight:600; white-space:nowrap; }
ul.flags { margin:0; padding-left:18px; color:var(--warn); font-size:13px; }
ul.plain { margin:0; padding-left:18px; }
.pill { font-size:12px; padding:1px 6px; border-radius:10px; border:1px solid var(--line); color:var(--muted); }
input[type=search] { padding:8px 10px; border-radius:6px; border:1px solid var(--line); background:var(--panel); color:var(--ink); min-width:280px; }
footer { max-width:1200px; margin:0 auto; padding:16px 24px 40px; color:var(--muted); font-size:13px; }
ol.flag-list li { margin-bottom:10px; }
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md_tourney(rows, title):
    lines = [f"## {title}", "", "| Venue | Event | Name | Category | Date | Start | Buy-in | Guarantee | Guarantee ÷ buy-in | Rules | Source | Flags |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        src = f"[{r.get('source_label', 'source')}]({r['source_url']})" if r.get("source_url") else ""
        flags = "; ".join(r.get("flags", []))
        rules = " ".join(x for x in [r.get("pool_note", ""), r.get("entry_rule", "")] if x).replace("|", "/")
        cells = [
            r.get("venue", ""), r.get("event", ""), r.get("name", ""), r.get("category", "Single-entry" if title.startswith("Main") else ""),
            r.get("date", ""), r.get("start", ""), r.get("buy_in", ""), r.get("guarantee", ""),
            fmt_ratio(ratio(r)), rules, src, flags,
        ]
        lines.append("| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |")
    lines.append("")
    return lines


def build_md_tournaments():
    out = ["# Tournaments (generated from data/tournaments.json)", "", f"As of {TOURNEY['as_of']}. {TOURNEY['note']}", ""]
    out += md_tourney(MAIN, "Main list: single-entry")
    out += md_tourney(SEPARATE, "Separate list: double buy-in, re-entry, add-on, or spend-to-gain")
    out += md_tourney(RESTRICTED, "Restricted eligibility")
    out += ["## Listed but not verified", "", "| Venue | Name | Date | Buy-in | Guarantee | Reason |", "|---|---|---|---|---|---|"]
    for r in UNVERIFIED:
        out.append("| " + " | ".join(str(r.get(k, "")).replace("|", "/") for k in ["venue", "name", "date", "buy_in", "guarantee", "reason"]) + " |")
    out.append("")
    return "\n".join(out)


def build_md_hotels():
    out = ["# Hotels (generated from data/hotels.json)", "", f"As of {HOTELS['as_of']}. {HOTELS['note']}", "", f"True nightly cost = {HOTELS['cost_formula']}", "",
           "| Hotel | Area | Room rate/night | Resort fee/night | Parking | True nightly cost | Walk to venue | Source | Flags |", "|---|---|---|---|---|---|---|---|---|"]
    for r in HOTELS["rows"]:
        src = f"[{r.get('source_label', 'source')}]({r['source_url']})" if r.get("source_url") else ""
        flags = "; ".join(r.get("flags", []))
        cells = [r["hotel"], r.get("area", ""), r.get("room_rate_per_night", ""), r.get("resort_fee_per_night", ""), r.get("parking", ""), r.get("true_nightly_cost", ""), r.get("walk_to_tournament_venue", ""), src, flags]
        out.append("| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |")
    out.append("")
    return "\n".join(out)


def main():
    write(ROOT / "index.html", build_index())
    write(ROOT / "tournaments.html", build_tournaments())
    write(ROOT / "hotels.html", build_hotels())
    write(ROOT / "schedule.html", build_schedule())
    write(ROOT / "dashboard.html", build_dashboard())
    write(ROOT / "summary.html", build_summary())
    write(ROOT / "flagged.html", build_flagged())
    write(ROOT / "assets" / "style.css", CSS)
    write(ROOT / ".nojekyll", "")
    write(DATA / "tournaments.md", build_md_tournaments())
    write(DATA / "hotels.md", build_md_hotels())
    print("built")


if __name__ == "__main__":
    main()
