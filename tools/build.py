#!/usr/bin/env python3
"""Builds the static GitHub Pages site in ../docs from tools/data.py.

Run:  python3 tools/build.py
Checks: every internal link resolves; every single-entry and excluded row has an
official source link; exits non-zero on any failure.
"""
import datetime as dt
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "docs")
VERIFIED = "2026-11-16"

NAV = [
    ("index.html", "Home"),
    ("summary.html", "Executive summary"),
    ("single-entry.html", "Single-entry (Venetian)"),
    ("daily-schedule.html", "Daily schedule"),
    ("excluded.html", "Excluded (multi-entry, satellites)"),
    ("wpt-wynn.html", "WPT / Wynn festival"),
    ("hotels.html", "Hotels"),
    ("analysis.html", "Analysis"),
    ("questions.html", "Questions to answer"),
    ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources & repo review"),
]

CSS = """
:root{--ink:#1d2433;--muted:#5b6474;--line:#e3e7ee;--bg:#f7f8fb;--card:#fff;--accent:#1f6feb;--warn:#b26a00;--ok:#1a7f37;--bad:#b42318}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--bg)}
header{background:#0f172a;color:#fff;padding:14px 22px}header a{color:#fff;text-decoration:none;font-weight:700;font-size:17px}
nav{background:#fff;border-bottom:1px solid var(--line);padding:8px 22px;display:flex;flex-wrap:wrap;gap:6px 14px}
nav a{color:var(--accent);text-decoration:none;font-size:14px}nav a.on{font-weight:700;color:var(--ink)}
main{max-width:1280px;margin:0 auto;padding:22px}
h1{font-size:26px;margin:4px 0 6px}h2{font-size:20px;margin:28px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}h3{font-size:16px;margin:18px 0 6px}
p.lead{color:var(--muted);margin-top:0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.card b{font-size:24px;display:block}.card span{color:var(--muted);font-size:13px}
.card a{color:var(--accent);text-decoration:none;font-weight:600}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden;font-size:13.5px}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#eef2f8;position:sticky;top:0;font-weight:700}
tr:nth-child(even) td{background:#fbfcfe}
td.num{text-align:right;white-space:nowrap}
.tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:12px;font-weight:600;background:#eef2f8;color:var(--muted)}
.tag.ok{background:#e6f4ea;color:var(--ok)}.tag.warn{background:#fff4e0;color:var(--warn)}.tag.bad{background:#fde8e6;color:var(--bad)}
.note{background:#fff8e6;border:1px solid #f5d98a;border-radius:8px;padding:10px 12px;margin:10px 0}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:10px 0}
input.filter{width:100%;max-width:420px;padding:8px 10px;border:1px solid #c9d1de;border-radius:8px;margin:8px 0 10px;font-size:14px}
.wrap{overflow-x:auto}
ul{padding-left:20px}li{margin:3px 0}
footer{color:var(--muted);font-size:12.5px;padding:24px 22px;text-align:center}
"""

JS = """
document.querySelectorAll('input.filter').forEach(function(inp){
  inp.addEventListener('input',function(){
    var t=document.getElementById(inp.dataset.target);
    var q=inp.value.toLowerCase();
    t.querySelectorAll('tbody tr').forEach(function(r){
      r.style.display=r.textContent.toLowerCase().indexOf(q)>-1?'':'none';
    });
  });
});
"""

LINKS_SEEN = []  # (page, href) internal links for checking


def e(x):
    return html.escape("" if x is None else str(x))


def money(x):
    if x is None:
        return '<span class="tag warn">unverified</span>'
    return "${:,.0f}".format(x)


def link(url, label="source"):
    if not url:
        return '<span class="tag warn">no official source</span>'
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (e(url), e(label))


def wd(d):
    return dt.datetime.strptime(d, "%Y-%m-%d").strftime("%a %b %d, %Y")


def struct_url(n):
    return D.VEN_STRUCT.format(n)


def page(fname, title, body, active=None, lead=None):
    navhtml = "".join(
        '<a href="%s"%s>%s</a>' % (href, ' class="on"' if href == active else "", e(label))
        for href, label in NAV
    )
    html_out = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s | Las Vegas Strip Poker Research</title><style>%s</style></head><body>
<header><a href="index.html">Las Vegas Strip Poker Research</a> <span style="opacity:.7;font-size:13px">&middot; data verified %s &middot; all values from official sources unless flagged</span></header>
<nav>%s</nav><main><h1>%s</h1>%s%s</main>
<footer>Figures are as published by the named official source on %s. Unverified values are left blank and flagged. Not financial advice.</footer>
<script>%s</script></body></html>""" % (
        e(title), CSS, VERIFIED, navhtml, e(title),
        ('<p class="lead">%s</p>' % e(lead)) if lead else "", body, VERIFIED, JS)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html_out)


def table(tid, headers, rows, filt=True):
    head = "".join("<th>%s</th>" % e(h) for h in headers)
    body = "".join("<tr>%s</tr>" % "".join(c for c in r) for r in rows)
    box = ""
    if filt:
        box = '<input class="filter" data-target="%s" placeholder="Filter rows (type to search)">' % tid
    return '%s<div class="wrap"><table id="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        box, tid, head, body)


def td(x, cls=""):
    return '<td class="%s">%s</td>' % (cls, x)


# ---------------------------------------------------------------------------
# Derived numbers
# ---------------------------------------------------------------------------
single = D.VEN_SINGLE
single_n = len(single)
single_reviewed = sum(1 for r in single if r[7])
multi_rows = D.VEN_MULTI_FLIGHT
sat_rows = D.VEN_SATELLITES
other_rows = D.VEN_OTHER_EXCLUDED
cont_rows = D.VEN_CONTINUATIONS
events_all = set(r[2] for r in single) | set(r[2] for r in multi_rows) | set(r[2] for r in sat_rows) | set(r[2] for r in other_rows)
events_total = len(events_all)
ratio = lambda r: (r[5] / r[4]) if r[5] else None  # GTD / buy-in (computed)
wpt_counts = {}
for r in D.WYNN_ROWS:
    wpt_counts[r[5]] = wpt_counts.get(r[5], 0) + 1
wpt_total = len(D.WYNN_ROWS)
ranked = sorted([r for r in single if ratio(r)], key=lambda r: -ratio(r))
top_ratio = ranked[:6]
cheapest = sorted(single, key=lambda r: (r[4], -(r[5] or 0)))[:5]
events_with_gtd = sum(1 for r in single if r[5])
excluded_events = len(set(r[2] for r in multi_rows) | set(r[2] for r in sat_rows) | set(r[2] for r in other_rows))

# Days with 2+ single-entry options
by_day = {}
for r in single:
    by_day.setdefault(r[0], []).append(r)
multi_day = {d: v for d, v in by_day.items() if len(v) >= 2}
earliest = min(single, key=lambda r: dt.datetime.strptime(r[1], "%I:%M %p").time())
earliest_time = earliest[1]

# ---------------------------------------------------------------------------
# PAGE: index
# ---------------------------------------------------------------------------
cards = """
<div class="cards">
<div class="card"><b>%d</b><span>Venetian single-entry events (official schedule)</span><br><a href="single-entry.html">View table &rarr;</a></div>
<div class="card"><b>%d</b><span>Events excluded: multi-flight, satellites, team, restricted</span><br><a href="excluded.html">View &rarr;</a></div>
<div class="card"><b>%d</b><span>WPT / Wynn festival schedule rows (official)</span><br><a href="wpt-wynn.html">View &rarr;</a></div>
<div class="card"><b>%d</b><span>Items flagged for review (unverified or irregular)</span><br><a href="flagged.html">Review &rarr;</a></div>
</div>""" % (single_n, len(multi_rows) + len(sat_rows) + len(other_rows), wpt_total, len(D.FLAGS))

index_body = cards + """
<h2>What this site covers</h2>
<p>Live, upcoming poker tournaments on or near the Las Vegas Strip, filtered to <b>single-entry</b> events. Events that allow a second or later starting-flight entry, a re-entry, a rebuy or an add-on are kept in a separate section, as requested. Every table row links to the official source it came from.</p>
<h2>Pages</h2>
<ul>
<li><a href="summary.html">Executive summary</a> - the short version: what is verified, what is not, and the answer to the 8:00 AM all-day question.</li>
<li><a href="single-entry.html">Single-entry tournaments</a> - all %d Venetian single-entry events, ranked by guarantee-to-buy-in ratio.</li>
<li><a href="daily-schedule.html">Daily schedule</a> - single-entry options by day, with the days that have two or more shots.</li>
<li><a href="excluded.html">Excluded</a> - multi-flight, satellites, the team event, and Day-2 continuation rows.</li>
<li><a href="wpt-wynn.html">WPT / Wynn festival</a> - the full official Wynn schedule. Almost all of it is multi-entry.</li>
<li><a href="hotels.html">Hotels</a> - official resort fees only; nightly rates and walking times are not verified yet.</li>
<li><a href="analysis.html">Analysis</a> - method, findings, and what the data does and does not support.</li>
<li><a href="questions.html">Questions to answer</a> - what must be known before a decision can be made, and where to get it.</li>
<li><a href="suggestions.html">Suggestions</a> - site improvements for review before anything is changed.</li>
<li><a href="flagged.html">Flagged for Review</a> - irregularities and unverified items, with source links.</li>
<li><a href="sources.html">Sources &amp; repo review</a> - every source URL used, and the repository review.</li>
</ul>
<div class="note"><b>Important:</b> No hotel can yet be recommended on verified numbers. Nightly rates and walking times are not available from official sources in this session. See <a href="hotels.html">Hotels</a> and <a href="questions.html">Questions</a>.</div>
""" % single_n
page("index.html", "Las Vegas Strip Poker Research", index_body, active="index.html",
     lead="A simple dashboard of verified live poker tournaments near the Strip, single-entry first.")

# ---------------------------------------------------------------------------
# PAGE: executive summary
# ---------------------------------------------------------------------------
top_names = "; ".join("%s (%s, %s)" % (r[3].split(" - ")[0], wd(r[0]), r[1]) for r in top_ratio[:3])
summary_body = """
<h2>Bottom line</h2>
<ul>
<li><b>%d single-entry events</b> are listed at the Venetian DeepStack Extravaganza IV (Nov 16 - Dec 23, 2026) on the official Venetian schedule. Of these, <b>%d</b> have a structure sheet reviewed in this session; the rest are flagged for line-by-line confirmation.</li>
<li><b>%d events</b> are excluded from the single-entry list: multi-flight events (%d rows), satellites (%d rows), one team event, and one restricted-eligibility event. Day-2 restarts are listed separately as continuations.</li>
<li><b>The WPT World Championship festival at Wynn</b> (%d official schedule rows) is treated as multi-entry: every Wynn structure sheet reviewed states unlimited re-entry or one re-entry. The $10,400 WPT World Championship structure was not found, so it is marked unverified.</li>
<li><b>Best single-entry value by guarantee per buy-in (computed from official figures):</b> %s.</li>
<li><b>8:00 AM start:</b> not achievable from verified data. The earliest single-entry start found is <b>%s</b>. No official 8:00 AM single-entry event was found.</li>
<li><b>Hotels:</b> only resort fees are verified. The Venetian and Wynn both list a <b>$55 plus tax</b> resort fee on official pages. Nightly rates, the Clark County tax rate and walking times are <b>not verified</b>, so no hotel ranking is possible yet.</li>
<li><b>Coverage gap:</b> other Strip rooms (Bellagio, MGM Grand, Caesars, Resorts World, Horseshoe/Paris, etc.) and the ARIA Poker Open have not been verified from official schedules.</li>
</ul>
<h2>Key numbers</h2>
<div class="cards">
<div class="card"><b>%d</b><span>Venetian events in the official schedule (64 numbered events)</span></div>
<div class="card"><b>%d</b><span>Single-entry events with a published guarantee</span></div>
<div class="card"><b>%d</b><span>Single-entry events with a structure sheet reviewed</span></div>
<div class="card"><b>%d</b><span>Single-entry days with two or more shots</span></div>
<div class="card"><b>%d</b><span>Items flagged for review</span></div>
</div>
<h2>Verified facts used</h2>
<ul>
<li>Venetian schedule and structure sheets: <a href="%s" target="_blank">official schedule</a>; example structure: <a href="%s" target="_blank">structure sheet for Events #9, #11, #13 and others</a>.</li>
<li>Venetian resort fee: <a href="%s" target="_blank">official page</a> ($55 plus tax per night).</li>
<li>WPT / Wynn: <a href="%s" target="_blank">official Wynn schedule PDF</a>, <a href="%s" target="_blank">official Wynn structures PDF</a> (re-entry rules), <a href="%s" target="_blank">official WPT event page</a> (Dec 13-20 dates).</li>
<li>Wynn resort fee: <a href="%s" target="_blank">official terms page</a> ($55 plus tax per room night).</li>
</ul>
<div class="note"><b>Decision readiness:</b> the single-entry list is ready for a shortlist. A hotel decision is <b>not</b> ready, and a daily all-day plan cannot be confirmed until run-times and the remaining structure sheets are checked. See <a href="questions.html">Questions to answer</a>.</div>
""" % (single_n, single_reviewed, excluded_events,
       len(multi_rows), len(sat_rows), wpt_total, top_names, earliest_time,
       64, events_with_gtd, single_reviewed, len(multi_day), len(D.FLAGS),
       D.VEN_SCHED, D.VEN_STRUCT.format(1), D.VEN_RESORT_FEE, D.WYNN_SCHED_PDF, D.WYNN_STRUCT_PDF, D.WPT_EVENT_PAGE, D.WYNN_TERMS)
page("summary.html", "Executive summary", summary_body, active="summary.html",
     lead="Important details first: what is verified, what is excluded, and what is still missing.")

# ---------------------------------------------------------------------------
# PAGE: single-entry table
# ---------------------------------------------------------------------------
rows = []
for r in sorted(single, key=lambda x: (x[0], dt.datetime.strptime(x[1], "%I:%M %p").time())):
    date, time_, ev, name, buy, gtd, sn, rev, pool, note = r
    rat = "%.1fx" % ratio(r) if ratio(r) else '<span class="tag warn">n/a</span>'
    rows.append([
        td(e(wd(date))), td(e(time_)), td(e(ev), "num"), td(e(name)),
        td(money(buy), "num"), td(money(gtd), "num"), td(rat, "num"),
        td(money(pool) if pool else '<span class="tag">not reviewed</span>', "num"),
        td(('<span class="tag ok">reviewed</span>' if rev else '<span class="tag warn">confirm</span>')),
        td('%s &middot; %s' % (link(D.VEN_SCHED, "schedule"), link(struct_url(sn), "structure #%d" % sn))),
        td(e(note)),
    ])
single_body = """
<div class="note"><b>Single-entry rule used:</b> single day, one starting flight, no re-entry, rebuy or add-on named on the official schedule, not a satellite, not a team event, not a Day-2 restart. Structure sheets confirm the event number and guarantee for the rows marked <i>reviewed</i>. <b>Confirm</b> rows are provisional until their structure sheet is read.</div>
<h2>Top value (guarantee per buy-in, computed)</h2>
<p>Computed as guarantee &divide; buy-in from official figures. Bounty events include bounty money inside the guarantee, so they are not directly comparable with plain guarantees.</p>
%s
<h2>All single-entry events (%d)</h2>
%s
""" % (
    table("top", ["Date", "Time", "Event #", "Event", "Buy-in", "GTD", "GTD / buy-in", "Prize pool per buy-in (structure)", "Structure", "Sources", "Notes"],
          [[td(e(wd(r[0]))), td(e(r[1])), td(e(r[2]), "num"), td(e(r[3].split(' - ')[0])), td(money(r[4]), "num"),
            td(money(r[5]), "num"), td("%.1fx" % ratio(r), "num"),
            td(money(r[8]) if r[8] else '<span class="tag">not reviewed</span>', "num"),
            td('<span class="tag ok">reviewed</span>' if r[7] else '<span class="tag warn">confirm</span>'),
            td('%s &middot; %s' % (link(D.VEN_SCHED, "schedule"), link(struct_url(r[6]), "structure #%d" % r[6]))),
            td(e(r[9]))] for r in top_ratio], filt=False),
    single_n, table("single", ["Date", "Time", "Event #", "Event", "Buy-in", "GTD", "GTD / buy-in", "Prize pool per buy-in (structure)", "Structure status", "Sources", "Notes"], rows)
)
page("single-entry.html", "Single-entry tournaments (Venetian DeepStack Extravaganza IV)", single_body, active="single-entry.html",
     lead="All single-entry events from the official Venetian schedule, Nov 16 - Dec 23, 2026. Times are venue times (Las Vegas).")

# ---------------------------------------------------------------------------
# PAGE: daily schedule
# ---------------------------------------------------------------------------
day_sections = []
for d in sorted(by_day):
    items = sorted(by_day[d], key=lambda x: dt.datetime.strptime(x[1], "%I:%M %p").time())
    lis = "".join("<li><b>%s</b> &middot; Event #%d &middot; %s &middot; %s <span class='tag'>%s</span></li>" % (
        e(t), r_ev, e(name.split(' - ')[0]), money(b), "bounty" if "Bounty" in name or "PKO" in name else "no bounty")
        for (dd, t, r_ev, name, b, g, sn, rv, pl, nt) in items)
    flag = ' <span class="tag bad">2+ shots</span>' if len(items) >= 2 else ""
    day_sections.append("<div class='box'><h3>%s%s</h3><ul>%s</ul></div>" % (e(wd(d)), flag, lis))
sched_body = """
<div class="note"><b>8:00 AM start: not possible from verified data.</b> The earliest single-entry start found on the official Venetian schedule is <b>%s</b>. Run-times are not published, so a day with two events can overlap. Check overlap with the structure sheets before planning.</div>
<h2>Days with two or more single-entry options</h2>
<p>These days allow two or more single-entry starts. Count: <b>%d</b>.</p>
<h2>All single-entry days</h2>
%s
""" % (earliest_time, len(multi_day), "".join(day_sections))
page("daily-schedule.html", "Daily schedule (single-entry options)", sched_body, active="daily-schedule.html",
     lead="Single-entry options by day, in time order. Use this to build a plan; run-times still need confirming.")

# ---------------------------------------------------------------------------
# PAGE: excluded
# ---------------------------------------------------------------------------
ex_rows = []
for r in sorted(multi_rows, key=lambda x: (x[0], dt.datetime.strptime(x[1], "%I:%M %p").time())):
    date, time_, ev, name, buy, gtd, sn, rev, note = r
    ex_rows.append([td(e(wd(date))), td(e(time_)), td(e(ev), "num"), td(e(name)), td(money(buy), "num"), td(money(gtd), "num"),
                    td('<span class="tag bad">multi-flight</span>'),
                    td('%s &middot; %s' % (link(D.VEN_SCHED, "schedule"), link(struct_url(sn), "structure #%d" % sn))),
                    td(e(note))])
for r in sat_rows:
    date, time_, ev, name, buy, gtd, sn, rev = r
    ex_rows.append([td(e(wd(date))), td(e(time_)), td(e(ev), "num"), td(e(name)), td(money(buy), "num"), td(money(gtd), "num"),
                    td('<span class="tag">satellite</span>'),
                    td('%s &middot; %s' % (link(D.VEN_SCHED, "schedule"), link(struct_url(sn), "structure #%d" % sn))),
                    td("Award is a seat in a later event, not cash")])
for r in other_rows:
    date, time_, ev, name, buy, gtd, sn, rev, note = r
    ex_rows.append([td(e(wd(date))), td(e(time_)), td(e(ev), "num"), td(e(name)), td(money(buy), "num"), td(money(gtd), "num"),
                    td('<span class="tag warn">team / restricted</span>'),
                    td('%s &middot; %s' % (link(D.VEN_SCHED, "schedule"), link(struct_url(sn), "structure #%d" % sn))),
                    td(e(note))])
cont_table_rows = [[td(e(wd(d))), td(e(t)), td(e(ev), "num"), td(e(n)), td('<span class="tag">continuation</span>'),
                    td(link(D.VEN_SCHED, "schedule")), td("Not a new entry")] for (d, t, ev, n) in cont_rows]
ex_body = """
<div class="note"><b>Why these are excluded:</b> players may enter more than one starting flight (multi-flight), or the event is a satellite, a team event, or has restricted eligibility. Under the brief, anything that lets you spend more to gain an advantage belongs in this separate section.</div>
<h2>Excluded entries (%d rows)</h2>
%s
<h2>Day-2 / Day-3 / final-table continuations (%d rows, not new entries)</h2>
%s
""" % (len(ex_rows), table("excl", ["Date", "Time", "Event #", "Event", "Buy-in", "GTD", "Reason", "Sources", "Notes"], ex_rows),
       len(cont_table_rows), table("cont", ["Date", "Time", "Event #", "Event", "Type", "Source", "Notes"], cont_table_rows))
page("excluded.html", "Excluded from single-entry (multi-entry, satellites, team, restricted)", ex_body, active="excluded.html",
     lead="Kept separate as requested. Multi-flight and re-entry events can be entered more than once.")

# ---------------------------------------------------------------------------
# PAGE: WPT / Wynn
# ---------------------------------------------------------------------------
STATUS_TXT = {
    "RE": ('<span class="tag bad">re-entry (structure reviewed)</span>', "Multi-entry"),
    "RE1": ('<span class="tag bad">1 entry + 1 re-entry</span>', "Multi-entry"),
    "NR": ('<span class="tag warn">not reviewed - provisionally excluded</span>', "Provisional"),
    "UV": ('<span class="tag warn">unverified (structure not found)</span>', "Unverified"),
    "SAT": ('<span class="tag">satellite</span>', "Satellite"),
    "CONT": ('<span class="tag">continuation</span>', "Continuation"),
    "IRR": ('<span class="tag bad">irregular (flagged)</span>', "Flagged"),
}
w_rows = []
for r in D.WYNN_ROWS:
    date, time_, name, buy, gtd, st = r
    w_rows.append([td(e(wd(date))), td(e(time_)), td(e(name)), td(money(buy), "num"), td(money(gtd), "num"),
                   td(STATUS_TXT[st][0]), td('%s &middot; %s' % (link(D.WYNN_SCHED_PDF, "schedule PDF"), link(D.WPT_EVENT_PAGE, "WPT page")))])
rev_st = sum(1 for r in D.WYNN_ROWS if r[5] in ("RE", "RE1"))
wpt_body = """
<div class="note"><b>Finding:</b> the official Wynn structure sheets reviewed (13 formats) state <b>unlimited re-entry</b> (or one entry plus one re-entry for the WPT Prime Championship). The festival is therefore kept out of the single-entry list.<br>
<b>Date conflict:</b> the official WPT page says the World Championship runs Dec 13-20; a third-party site says Dec 14-22. Official dates are used. See <a href="flagged.html">Flagged</a>.</div>
<h2>Full official Wynn / WPT schedule (%d rows)</h2>
<p>Re-entry confirmed on structure sheet: %d rows. Provisional or unverified: the rest. Status is explained per row.</p>
%s
""" % (wpt_total, rev_st, table("wpt", ["Date", "Time", "Event", "Buy-in", "GTD", "Status", "Sources"], w_rows))
page("wpt-wynn.html", "WPT World Championship at Wynn Las Vegas (festival schedule)", wpt_body, active="wpt-wynn.html",
     lead="Official schedule, Nov 27 - Dec 21, 2026, with entry status for every row.")

# ---------------------------------------------------------------------------
# PAGE: hotels
# ---------------------------------------------------------------------------
h_rows = []
for h in D.HOTELS:
    fee = ("$%d plus tax" % h["resort_fee_pre_tax"]) if h["resort_fee_pre_tax"] else '<span class="tag warn">unverified</span>'
    h_rows.append([
        td(e(h["name"])),
        td(fee, "num"),
        td(e(h["resort_fee_status"])),
        td(link(h["resort_fee_source"], "official page") if h["resort_fee_source"] else '<span class="tag warn">no official source</span>'),
        td(money(h["base_rate"]), "num"),
        td(e(h["base_rate_status"])),
        td(e(h["walk_status"])),
        td(e(h["tourneys"])),
        td(e(h["other"])),
    ])
hotel_body = """
<div class="note"><b>Result: no hotel recommendation can be made on verified data yet.</b> Only the resort fees are confirmed from official pages. Nightly rates, tax, and walking times are blank because they could not be confirmed from an official source in this session.</div>
<h2>True cost per night (formula)</h2>
<div class="box">
<p><b>True nightly cost</b> = (base room rate for your dates + resort fee + room tax + any mandatory extra-guest or deposit fees) &divide; nights.</p>
<p>Inputs: base room rate - <span class="tag warn">unverified</span> &middot; resort fee - verified for Venetian and Wynn ($55 plus tax) &middot; room tax - <span class="tag warn">unverified</span>. No number is filled in.</p>
</div>
<h2>Candidate hotels (official data only)</h2>
%s
<h2>Distance rule</h2>
<p>Requirement: within at least 30 minutes' walk of each tournament. Walk times are not verified, so no hotel is confirmed to meet it. The Venetian hosts the DeepStack single-entry events; the Wynn hosts the WPT festival (multi-entry, excluded).</p>
""" % table("hotels", ["Hotel", "Resort fee (pre-tax)", "Fee status", "Fee source", "Base rate / night", "Rate status", "Walking to tournaments", "Tournaments here", "Other requirements"], h_rows)
page("hotels.html", "Hotels near the Strip tournaments", hotel_body, active="hotels.html",
     lead="Resort fees from official pages. Rates and walking times are pending.")

# ---------------------------------------------------------------------------
# PAGE: analysis
# ---------------------------------------------------------------------------
analysis_body = """
<h2>Method</h2>
<ul>
<li><b>Single-entry filter:</b> single day, one starting flight, no re-entry/rebuy/add-on on the official schedule, not a satellite, team, or Day-2 restart.</li>
<li><b>Value metric:</b> guarantee &divide; buy-in (computed). It is a simple proxy for how much the organiser promises per dollar. It ignores field size and the house fee. The prize pool per buy-in (from structure sheets) is shown where reviewed (e.g., 80%% of a $200 buy-in goes to the prize pool; 85%% of $600).</li>
<li><b>Cost:</b> buy-in only. Hotel cost is not included because no nightly rate is verified.</li>
</ul>
<h2>Findings</h2>
<ul>
<li><b>Best guarantee per buy-in (single-entry):</b> %s.</li>
<li><b>Lowest-cost single-entry events:</b> %s.</li>
<li><b>Bounty events:</b> many single-entry events are bounty tournaments. The bounty money is part of the guarantee, so the cash prize pool for those events is smaller than the headline number. Treat bounty GTDs with care.</li>
<li><b>Age limit:</b> the Seniors events are 50+ only; they are included but flagged.</li>
<li><b>Schedule shape:</b> single-entry events cluster at 11:10 AM, 12:10 PM, 10:10 AM and 5:10 PM. %d days have two or more single-entry starts.</li>
<li><b>WPT:</b> none of the reviewed WPT formats is single-entry, so the WPT festival (the largest guarantees) is outside the single-entry list.</li>
</ul>
<h2>What the data does not yet support</h2>
<ul>
<li>A ranking by expected value (field size and payout structure per event are not verified).</li>
<li>An all-day plan starting at 8:00 AM (no official 8:00 AM single-entry start found).</li>
<li>A hotel ranking (no verified nightly rate or walking time).</li>
</ul>
""" % (", ".join("%s (%.1fx, %s)" % (r[3].split(' - ')[0], ratio(r), wd(r[0])) for r in top_ratio[:4]),
       ", ".join("%s on %s" % (r[3].split(' - ')[0], wd(r[0])) for r in cheapest[:3]), len(multi_day))
page("analysis.html", "Analysis and findings", analysis_body, active="analysis.html",
     lead="What the verified data says, and what it cannot say yet.")

# ---------------------------------------------------------------------------
# PAGE: questions
# ---------------------------------------------------------------------------
q_rows = [[td(e(c)), td(e(q)), td(e(s))] for (c, q, s) in D.QUESTIONS]
q_body = """
<p>These must be answered before a decision is reasonably possible. The left column shows the area; the right column shows where the answer comes from.</p>
%s
""" % table("qs", ["Area", "Question", "Where the answer comes from"], q_rows)
page("questions.html", "Questions and information still needed", q_body, active="questions.html",
     lead="The information we have, and the information we still need.")

# ---------------------------------------------------------------------------
# PAGE: suggestions
# ---------------------------------------------------------------------------
s_rows = [[td('<span class="tag">%s</span>' % e(a)), td(e(b)), td('<span class="tag warn">awaiting your choice</span>')] for (a, b) in D.SUGGESTIONS]
sug_body = """
<div class="note"><b>Nothing here has been implemented.</b> Review each suggestion, then choose which to adopt before any change is made.</div>
%s
""" % table("sug", ["Area", "Suggestion", "Status"], s_rows)
page("suggestions.html", "Suggestions for improving the site (for review)", sug_body, active="suggestions.html",
     lead="Choose the path before implementation.")

# ---------------------------------------------------------------------------
# PAGE: flagged
# ---------------------------------------------------------------------------
f_rows = []
for i, (area, text, src1, src2) in enumerate(D.FLAGS, 1):
    def _src(x, n):
        if not x:
            return None
        if x.startswith("http"):
            return link(x, "source %d" % n)
        return "<i>%s</i>" % e(x)
    links = " &middot; ".join(x for x in [_src(src1, 1), _src(src2, 2)] if x) or '<span class="tag warn">no source</span>'
    f_rows.append([td(str(i), "num"), td('<span class="tag warn">%s</span>' % e(area)), td(e(text)), td(links)])
flag_body = """
<div class="note"><b>Flagged for Review.</b> These items do not block the merge. They are listed here with their sources so you can review them after the site is live and request changes.</div>
%s
""" % table("flags", ["#", "Area", "Item", "Sources"], f_rows)
page("flagged.html", "Flagged for Review", flag_body, active="flagged.html",
     lead="Irregularities and unverified items, with links for manual review.")

# ---------------------------------------------------------------------------
# PAGE: sources & repo review
# ---------------------------------------------------------------------------
src_list = [
    (D.VEN_SCHED, "Venetian DeepStack Extravaganza IV full schedule (64 events, dates, times, buy-ins, guarantees)"),
    (D.VEN_STRUCT.format(1), "Venetian structure: $200 Bounty $8K (1Day) - events 9,11,13,15,21,22,23,25,60,61,62,64; house fee $40; guarantee includes bounties"),
    (D.VEN_STRUCT.format(7), "Venetian structure: $600 NLH (1Day) - events 14,28,63; house fee $90; guarantees $30K/$40K"),
    (D.VEN_STRUCT.format(10), "Venetian structure: $300 NLH flights 1A/1C - multi-flight wording; house fee $60"),
    (D.VEN_STRUCT.format(12), "Venetian structure: $800 NLH flights 1A/1C/1E - multi-flight wording; house fee $110"),
    (D.VEN_STRUCT.format(15), "Venetian structure: $300 NLH Bounty $15K (1Day) - events 29,31,34,38,42,50,51,53,55; house fee $50"),
    (D.VEN_STRUCT.format(21), "Venetian structure: $2,200 NLH Title Event 1A - multi-flight; house fee $225"),
    (D.VEN_RESORT_FEE, "Venetian resort fee - $55 plus tax per night"),
    (D.WPT_EVENT_PAGE, "WPT official event page - World Championship dates Dec 13-20 and schedule rows"),
    (D.WYNN_SCHED_PDF, "Wynn official WPT World Championship schedule PDF (all rows)"),
    (D.WYNN_STRUCT_PDF, "Wynn official WPT structures PDF - re-entry terms (chunks 0-7 reviewed)"),
    (D.WYNN_POKER, "Wynn poker room page - WPT dates, daily tournaments reference"),
    (D.WYNN_TERMS, "Wynn terms page - $55 plus tax resort fee"),
    (D.WSOP_SCHED, "WSOP official schedule - no Las Vegas events Nov-Dec 2026"),
    ("https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html", "(duplicate of schedule, cross-check)"),
]
src_rows = [[td(link(u, u.split('//')[1][:60])), td(e(t))] for (u, t) in src_list[:-1]]
secondary = [
    "https://pokergods.com/series/wpt/ - third-party: WPT dates Dec 14-22 (conflict, flagged)",
    "https://pokerfuse.com/live-poker/world-poker-tour/ - third-party: WPT schedule summary (not used for values)",
    "https://www.lifeofpoker.com/news/2026/09/wpt-world-championship-returns-to-wynn-las-vegas-with-85-events-and-20m-in-guarantees - third-party: Super Gold Million re-entry (flagged)",
    "https://vegascasinoinsider.com/casino/the-venetian-hotel-and-casino-las-vegas - third-party: Venetian fee $62.36 total (flagged)",
    "https://www.resortfeechecker.com/2565776-resort_fee_ariresort_casino.html - third-party: ARIA fee (flagged)",
    "https://www.pokeratlas.com/poker-room/aria-las-vegas/tournaments - third-party: ARIA Poker Open dates (flagged)",
    "https://poker.betmgm.com/en/blog/poker-news/win-your-way-to-betmgm-events-at-aria-poker-open-in-las-vegas/ - third-party, 2025 post (flagged)",
    "https://www.pokeratlas.com/poker-tournament-series - third-party: Las Vegas festival listings (not used for values)",
    "https://pokerdb.thehendonmob.com/festival.php?a=l&y=2026&m=all&c=USA - third-party: festival listings (not used for values)",
]
repo_review = """
<h2>Repository review (line by line)</h2>
<table><thead><tr><th>Item</th><th>Finding</th><th>Evidence</th></tr></thead><tbody>
<tr><td>Branch</td><td>arena/581fea93-poker5, branched from 0ba2e55 (main). Working tree clean at start.</td><td>git status / git log</td></tr>
<tr><td>Files</td><td>Only README.md ("# Poker5", no trailing newline). No code, data, tests, CI or site existed.</td><td>git ls-files</td></tr>
<tr><td>Remote</td><td>origin = github.com/karagemop466-tech/Poker5; main is 0ba2e55.</td><td>git ls-remote</td></tr>
<tr><td>Coordination</td><td>No COORDINATION.md existed; created with this session's claims and log.</td><td>COORDINATION.md</td></tr>
<tr><td>Irregularity</td><td>README is a title-only stub. Session branch rule and the task text disagree on branch naming (session-&lt;id&gt;/&lt;task&gt;). Followed the session branch rule.</td><td>See flagged page</td></tr>
</tbody></table>
<h2>Official sources used (checked 2026-11-16)</h2>
%s
<h2>Third-party sources (cross-check only; flagged where used)</h2>
<ul>%s</ul>
""" % (table("src", ["Official source", "What it supports"], src_rows, filt=False),
       "".join("<li>%s</li>" % e(x) for x in secondary))
page("sources.html", "Sources and repository review", repo_review, active="sources.html",
     lead="Every source URL, what it supports, and what was reviewed.")

# Root redirect: the live GitHub Pages source is main / (root) (token cannot change it to /docs).
ROOT_INDEX = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=docs/index.html">
<link rel="canonical" href="docs/index.html"><title>Las Vegas Strip Poker Research</title></head>
<body><p>Opening the site: <a href="docs/index.html">docs/index.html</a></p>
<script>location.replace('docs/index.html');</script></body></html>
"""
with open(os.path.join(os.path.dirname(HERE), "index.html"), "w", encoding="utf-8") as f:
    f.write(ROOT_INDEX)

# ---------------------------------------------------------------------------
# Link + completeness checks
# ---------------------------------------------------------------------------
errors = []
pages = [n for n, _ in NAV]
for fname in os.listdir(OUT):
    if fname.endswith(".html"):
        with open(os.path.join(OUT, fname), encoding="utf-8") as f:
            text = f.read()
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith("http") or href.startswith("#") or href.startswith("mailto:"):
                continue
            if href not in pages and not os.path.exists(os.path.join(OUT, href)):
                errors.append("%s -> broken internal link %s" % (fname, href))
for r in single:
    if not r[6] or not D.VEN_SCHED:
        errors.append("single row missing source: %s" % r[3])
for r in multi_rows + other_rows:
    if not D.VEN_SCHED:
        errors.append("excluded row missing source: %s" % r[3])
if single_n != 47:
    errors.append("unexpected single-entry count %d" % single_n)
for n in pages:
    if not os.path.exists(os.path.join(OUT, n)):
        errors.append("missing page %s" % n)

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK: %d pages; single=%d; excluded=%d; WPT rows=%d; flags=%d; events accounted=%d" % (
    len(pages), single_n, len(multi_rows) + len(sat_rows) + len(other_rows), wpt_total, len(D.FLAGS), events_total))
