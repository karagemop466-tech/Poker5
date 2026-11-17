#!/usr/bin/env python3
"""Build dashboard-6d1e0039/ : a static, source-linked dashboard for session 6d1e0039.

All numbers shown are either copied from data-6d1e0039/events.json (which in turn only
carries values read from official sources) or computed here and labelled "computed".

Run: python3 scripts/build_6d1e0039_site.py
"""
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data-6d1e0039", "events.json")
OUT = os.path.join(ROOT, "dashboard-6d1e0039")

D = json.load(open(DATA))
RET = D["retrieved"]

VEN = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
WYN = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"

# ---------------------------------------------------------------- helpers
def e(x):
    if x is None or x == "":
        return '<span class="blank" title="not published on an official source">blank</span>'
    return html.escape(str(x))


def money(x):
    if x is None or x == "":
        return '<span class="blank">blank</span>'
    try:
        return "$" + format(int(round(float(x))), ",")
    except Exception:
        return e(x)


def src(url, label="source"):
    if not url:
        return '<span class="blank">no link</span>'
    return f'<a class="srclink" href="{html.escape(url)}" target="_blank" rel="noopener">{label}</a>'


def t12(t):
    if not t or ":" not in str(t):
        return e(t)
    hh, mm = str(t).split(":")[:2]
    try:
        h, m = int(hh), int(mm)
    except ValueError:
        return e(t)
    ap = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {ap}"


def dshort(d):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    try:
        y, m, dd = d.split("-")
        return f"{months[int(m) - 1]} {int(dd)}"
    except Exception:
        return e(d)


def num(x):
    try:
        return float(x)
    except Exception:
        return None


# ---------------------------------------------------------------- computed fields
BREAK_EVERY = {20: 4, 25: 4, 30: 4, 40: 3}
BREAK_MIN = {20: 10, 25: 10, 30: 15, 40: 15}
# levels a one-day event typically needs before a winner is declared (assumption, labelled)
LEVELS_TO_FINISH = {15: 26, 20: 22, 25: 20, 30: 18, 40: 14}


def planned_hours(level, levels=None):
    """Computed estimate: levels * level length + scheduled breaks."""
    lv = num(level)
    if not lv or lv not in BREAK_EVERY:
        return None
    n = levels or LEVELS_TO_FINISH.get(int(lv))
    if not n:
        return None
    breaks = n // BREAK_EVERY[int(lv)]
    return round((n * lv + breaks * BREAK_MIN[int(lv)]) / 60, 1)


def late_reg_close(start, level, lreg):
    """Computed late-registration clock: start + level*levels + breaks inside that span."""
    lv, n = num(level), num(lreg)
    if not start or ":" not in str(start) or not lv or not n or lv not in BREAK_EVERY:
        return None
    mins = n * lv + (int(n) // BREAK_EVERY[int(lv)]) * BREAK_MIN[int(lv)]
    h, m = [int(x) for x in str(start).split(":")[:2]]
    tot = h * 60 + m + int(mins)
    return f"{(tot // 60) % 24:02d}:{tot % 60:02d}"


def add_minutes(start, mins):
    if not start or ":" not in str(start) or mins is None:
        return None
    h, m = [int(x) for x in str(start).split(":")[:2]]
    tot = h * 60 + m + int(mins)
    return f"{(tot // 60) % 24:02d}:{tot % 60:02d}"


def ratio(guarantee, buy):
    g, b = num(guarantee), num(buy)
    if not g or not b:
        return None
    return round(g / b, 1)


def all_events():
    ev = []
    for x in D["venetianSingles"]:
        ev.append(x)
    for x in D["venetianMulti"]:
        ev.append(x)
    for x in D["venetianSatellites"]:
        ev.append(x)
    for x in D["wynn"]:
        ev.append(x)
    for x in D["other"]:
        ev.append(x)
    return ev


EVENTS = all_events()

# ---------------------------------------------------------------- table renderers
HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Strip Poker Dashboard (session 6d1e0039)</title>
<link rel="stylesheet" href="assets/style.css"></head><body>
<header class="top"><div class="brand"><span class="mark">P5</span><div><strong>Strip poker &amp; hotel dashboard</strong>
<small>Verified against official sources · last checked {ret}</small></div></div>
<nav>{nav}</nav></header><main>{body}
<footer><p>Session 6d1e0039 · every row links to the official page or PDF it was read from ·
<code>blank</code> means the official source does not publish the value ·
computed values are labelled. <a href="changes.html">Change log</a> ·
<a href="flagged.html">Flagged for review</a></p></footer>
<script src="assets/app.js"></script></body></html>"""

NAV = [
    ("index.html", "Overview"), ("schedule.html", "All-day plan"), ("venetian.html", "Venetian"),
    ("wynn.html", "Wynn"), ("others.html", "Other rooms"), ("rules.html", "Entry rules"),
    ("hotels.html", "Hotels"), ("routes.html", "Walking"), ("calculator.html", "Trip cost"),
    ("flagged.html", "Flagged"), ("questions.html", "Questions"),
    ("suggestions.html", "Suggestions"), ("changes.html", "Change log"),
]


def nav(cur):
    out = []
    for href, label in NAV:
        cls = ' class="on"' if href == cur else ""
        out.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(out)


def page(path, title, body):
    with open(os.path.join(OUT, path), "w") as f:
        f.write(HEAD.format(title=html.escape(title), ret=RET, nav=nav(path), body=body))


def toolbar(filters=("search", "date", "single")):
    bits = []
    if "search" in filters:
        bits.append('<input id="q" type="search" placeholder="Search events, venues, formats…" aria-label="Search">')
    if "date" in filters:
        bits.append('<select id="dateFilter" aria-label="Filter by date"><option value="">All dates</option></select>')
    if "single" in filters:
        bits.append('<label class="chk"><input id="singleOnly" type="checkbox"> Single-entry confirmed only</label>')
    if "venue" in filters:
        bits.append('<select id="venueFilter" aria-label="Filter by venue"><option value="">All venues</option></select>')
    return ('<div class="toolbar">' + "".join(bits) +
            '<span class="count" id="rowcount"></span></div>')


def event_table(rows, key="ev", show_no=True, show_rules=False):
    th = ["Date", "Start", "Venue", "Event", "Buy-in", "Guarantee", "GTD ÷ buy-in",
          "Stack", "Levels", "Late reg closes", "Single entry", "Sources", "Checked"]
    if show_rules:
        th.insert(11, "Add-on / re-entry")
    if not show_no:
        th.remove("Event")
    head = "".join(f"<th>{h}</th>" for h in th)
    body = []
    for r in rows:
        close = r.get("lateRegClock") or t12(late_reg_close(r.get("start"), r.get("levelMinutes"), r.get("lateRegLevels")))
        se = r.get("singleEntry")
        if se == "no":
            seb = '<span class="pill no">re-entry</span>'
        elif se == "unverified":
            seb = '<span class="pill unv">unverified</span>'
        else:
            seb = f'<span class="pill yes">{e(se)}</span>'
        name = e(r.get("name"))
        if r.get("eventNo"):
            name = f'<span class="evno">#{r["eventNo"]}</span> ' + name
        gtr = ratio(r.get("guarantee"), r.get("buyIn"))
        cells = [
            f'<td data-sort="{e(r.get("date"))}">{e(r.get("date")) if r.get("date") and "-" in str(r.get("date")) else e(r.get("date"))}</td>',
            f'<td>{t12(r.get("start"))}</td>',
            f'<td>{e(r.get("venue"))}</td>',
            f'<td>{name}<div class="sub">{e(r.get("format"))}</div></td>',
            f'<td class="num">{money(r.get("buyIn"))}</td>',
            f'<td class="num">{money(r.get("guarantee"))}</td>',
            f'<td class="num">{("%.1f×" % gtr) if gtr else "<span class=blank>blank</span>"}</td>',
            f'<td class="num">{e(r.get("startingStack"))}</td>',
            f'<td class="num">{e(r.get("levelMinutes"))}</td>',
            f'<td>{e(close)}</td>',
            f'<td>{seb}</td>',
        ]
        if show_rules:
            parts = []
            if r.get("reEntry"):
                parts.append("re-entry: " + e(r["reEntry"]))
            if r.get("addOn"):
                parts.append("add-on: " + e(r["addOn"]))
            cells.append('<td class="rules">' + ("; ".join(parts) if parts else '<span class="blank">no rule published</span>') + "</td>")
        cells += [
            f'<td class="srcs">{src(r.get("scheduleUrl"), "schedule")} {src(r.get("structureUrl"), "structure")}</td>',
            f'<td class="num">{e(r.get("retrieved"))}</td>',
        ]
        body.append(
            f'<tr data-date="{e(r.get("date"))}" data-single="{e(se)}" data-venue="{e(r.get("venueSlug"))}"'
            f' data-text="{html.escape((str(r.get("name")) + " " + str(r.get("venue")) + " " + str(r.get("format")) + " " + str(r.get("date"))).lower(), quote=True)}">'
            + "".join(cells) + "</tr>")
    return (f'<div class="tablewrap"><table class="grid" data-table="{key}"><thead><tr>{head}</tr></thead>'
            f"<tbody>{''.join(body)}</tbody></table></div>")


def stat(label, value, note=""):
    return f'<div class="stat"><div class="v">{value}</div><div class="l">{label}</div><div class="n">{note}</div></div>'


# ---------------------------------------------------------------- derived counts
singles_ven = [x for x in D["venetianSingles"]]
ven_unv = [x for x in singles_ven if x["singleEntry"] == "unverified"]
ven_no = [x for x in singles_ven if x["singleEntry"] == "no"]
wynn_no = [x for x in D["wynn"] if x["singleEntry"] == "no"]
wynn_unv = [x for x in D["wynn"] if x["singleEntry"] == "unverified"]
confirmed_single = [x for x in EVENTS if x["singleEntry"] == "yes"]
with_gtd = [x for x in singles_ven if x.get("guarantee")]
best_ratio = sorted(with_gtd, key=lambda r: -(ratio(r["guarantee"], r["buyIn"]) or 0))[:8]

# ---------------------------------------------------------------- index
tot_rows = len(EVENTS)
index_body = f"""
<h1>Las Vegas Strip poker tournaments and hotels</h1>
<p class="lede">A single-entry-first view of the Strip's published tournament schedules for
16 Nov – 23 Dec 2026, read line by line from official schedule pages, structure-sheet PDFs and
posted hotel terms on {RET}. Every row carries its source link and a <em>last checked</em> date.
Nothing is filled in when the official source does not publish it.</p>

<section class="stats">
{stat("Rows captured", tot_rows, "3 venues + daily rooms")}
{stat("Single-entry <b>confirmed</b>", 0, "no official page says &quot;no re-entry&quot;")}
{stat("Re-entry priced (excluded)", len(ven_no) + len(wynn_no), "Venetian #18/#58, Wynn terms sheets")}
{stat("Guarantee + buy-in verified", len(with_gtd), "Venetian one-day slate")}
{stat("Flagged for review", len(D["flags"]), "see Flagged page")}
{stat("Hotels with a dated quote", 2, "Venetian checkout total, Wynn average")}
</section>

<section class="panel">
<h2>Executive summary</h2>
<ul class="tight">
<li><b>The strict list is empty on purpose.</b> All 37 Venetian structure sheets and every Wynn
terms sheet the WPT posted were read. Not one event says “no re-entry” or “freezeout”. Two
Venetian events publish a re-entry price (#18 and #58, “All subsequent buy in's after the initial
buy in will be $200”) and every Wynn event with a posted terms sheet states unlimited re-entry.
So no Strip event can be certified single-entry today — the candidates stay marked
<span class="pill unv">unverified</span> instead of being promoted.</li>
<li><b>Best published value among the one-day Venetian events</b> (guarantee ÷ buy-in, descriptive
only, not a forecast): {", ".join(f'#{r["eventNo"]} {money(r["buyIn"])} → {money(r["guarantee"])} ({ratio(r["guarantee"], r["buyIn"])}×)' for r in best_ratio[:4])}.
These are the rows where the house is guaranteeing the most money per dollar of entry.</li>
<li><b>Dates matter more than buy-in.</b> The Venetian's own booking engine prices the same
Luxury King suite at $231.75 on Sun Dec 6 and $779.25 on Sat Dec 5. A seven-night Dec 2–9 stay is
<b>$6,927.21 all-in</b> (room $5,837.25 + resort fees $385.00 + tax $817.46), an $872.82 nightly
average including the resort fee but excluding tax.</li>
<li><b>There is no 8:00 a.m. start on the Strip.</b> The earliest verified start is 9:10 a.m.
(Venetian #46, Dec 12); regular slates begin 10:10 a.m. (Venetian), 10:00 a.m. (Wynn Super Gold
Million), 9:00 a.m. (Horseshoe). An all-day plan therefore runs roughly 9:10 a.m. → midnight.</li>
<li><b>Two Strip rooms cannot be used under the brief.</b> Bellagio sells a $40 “voluntary staff
gratuity” that adds 20,000 chips and Caesars Palace sells a $50 add-on for 15,000 chips — both are
pay-for-advantage. They are documented separately, not ranked.</li>
</ul>
</section>

<section class="panel">
<h2>Start here</h2>
<div class="cards">
<a class="card" href="schedule.html"><h3>All-day plan</h3><p>Day-by-day primary event plus a
conditional fallback, with an overlap check built from start time, late-reg close and a labelled
duration estimate.</p></a>
<a class="card" href="venetian.html"><h3>Venetian</h3><p>48 one-day events, 9 multi-flight events
and 7 satellites, each with its structure sheet.</p></a>
<a class="card" href="wynn.html"><h3>Wynn</h3><p>113 scheduled rows for the WPT World
Championship series, with the entry rule shown wherever Wynn publishes one.</p></a>
<a class="card" href="hotels.html"><h3>Hotels &amp; true cost</h3><p>Dated rate log, resort fee,
13.38% Clark County tax, parking and cancellation terms.</p></a>
<a class="card" href="calculator.html"><h3>Trip cost calculator</h3><p>Entries × buy-ins + nights ×
true nightly cost, computed from the quotes on this site.</p></a>
<a class="card" href="flagged.html"><h3>Flagged for review</h3><p>Twelve irregularities, each with
the official source that shows it.</p></a>
</div>
</section>

<section class="panel">
<h2>How verification works here</h2>
<table class="kv">
<tr><th>Read directly from an official source</th><td>Dates, start times, buy-ins, guarantees,
starting stacks, level lengths, late-registration levels and clocks, payout percentages, bounty
amounts, fee splits, hotel rates, resort fees, tax rate, walking times. Each row links the page
and records {RET}.</td></tr>
<tr><th>Computed (labelled)</th><td>Guarantee ÷ buy-in, house fee (buy-in − prize-pool portion),
late-registration clock when only levels are published, estimated event length, trip totals.</td></tr>
<tr><th>Left blank</th><td>Anything the official source does not state: entry rules for most Wynn
events, cancellation deadlines for both hotels, parking at the Venetian, Bellagio's real Saturday
buy-in, Resorts World's rates.</td></tr>
</table>
</section>
"""
page("index.html", "Overview", index_body)

# ---------------------------------------------------------------- venue pages
def venue_page(slug, title, intro, rows, hotel_slugs, extra=""):
    hotels = [h for h in D["hotels"] if h["slug"] in hotel_slugs]
    hrows = "".join(
        f'<tr><td>{e(h["venue"])}</td><td class="num">{e(h["room"])}</td>'
        f'<td class="num">{(("$%s" % format(round(h["checkoutTotal"], 2), ",.2f")) if h["checkoutTotal"] else "<span class=blank>blank</span>")}</td>'
        f'<td class="num">{(("$%.2f" % (h["checkoutTotal"] / h["nights"])) if h["checkoutTotal"] else "<span class=blank>blank</span>")}</td>'
        f'<td class="num">{(("$%.0f" % h["resortFeePerNight"]) if h["resortFeePerNight"] else "<span class=blank>blank</span>")}</td>'
        f'<td>{src(h["rateSource"], "rate")}</td></tr>' for h in hotels)
    body = f"""
<h1>{title}</h1>
<p class="lede">{intro}</p>
{toolbar()}
<section class="panel">{extra}
<h2>Events</h2>
{event_table(rows, key=slug, show_rules=True)}
</section>
<section class="panel">
<h2>Hotels within a 30-minute walk, cheapest dated quote first</h2>
<div class="tablewrap"><table class="grid"><thead><tr><th>Hotel</th><th>Room</th>
<th>7-night total</th><th>Per night all-in</th><th>Resort fee / night</th><th>Source</th></tr></thead>
<tbody>{hrows}</tbody></table></div>
<p class="muted">Only quotes that were actually read are listed. Airbnb-style or unbundled rates are
not compared because they lack the resort fee and tax basis the brief asks for.</p>
</section>
"""
    page(f"{slug}.html", title, body)


ven_extra = """
<div class="note"><b>Venetian entry-rule finding.</b> 48 one-day events were read line by line
(sheets #1–#37). Two events publish a re-entry price and are excluded from the single-entry list.
The remaining 46 sheets contain no re-entry, rebuy or add-on sentence at all — which is not the
same as a freezeout, so they stay <span class="pill unv">unverified</span>.
Multi-flight events (1, 7, 19, 26, 39, 47, 49, 56, 59) are listed separately because a player may
buy a new entry in each starting flight.</div>
<h3>Multi-flight events (multi-entry by design)</h3>
""" + event_table(D["venetianMulti"], key="venmulti", show_rules=True) + """
<h3>Satellites (buy a seat, not a prize pool)</h3>
""" + event_table(D["venetianSatellites"], key="vensat", show_rules=True)

venue_page("venetian", "The Venetian Resort Las Vegas",
           f"Poker room on Palazzo level 2. DeepStack Extravaganza IV runs 16 Nov – 23 Dec 2026. "
           f"48 one-day events with a published guarantee, stack, level length and late-registration "
           f"cut-off: {len(ven_unv)} carry no entry rule, {len(ven_no)} publish a re-entry price. "
           f"Schedule page and all 37 structure sheets read {RET}.",
           singles_ven, ["venetian", "wynn", "bellagio"], ven_extra)

# Wynn page: mark which events have a rule, group by week
wynn_by_date = {}
for r in D["wynn"]:
    wynn_by_date.setdefault(r["date"], []).append(r)
week_blocks = []
for d in sorted(wynn_by_date):
    rows = sorted(wynn_by_date[d], key=lambda r: (r.get("start") or ""))
    week_blocks.append(f"<h3>{e(d)}</h3>" + event_table(rows, key="w" + d, show_rules=True))

wynn_extra = f"""
<div class="note"><b>Wynn entry-rule finding.</b> Wynn posts one structures PDF for the whole
series. It contains terms sheets only up to the $1,600 PLO Mystery Bounty ($500,000 GTD). Every
terms sheet inside it states <em>unlimited re-entry</em> (until level 9, or level 10 for the
$1,600 NLH and the PLO Mystery Bounty); the $1,100 WPT Prime Championship allows “one (1) entry and
one (1) re-entry for each starting flight”. So no Wynn event qualifies as single-entry, and the
{len(wynn_unv)} rows without a published terms sheet stay unverified rather than assumed.
</div>
"""

venue_page("wynn", "Wynn Las Vegas (Encore poker room)",
           "WPT World Championship series, 27 Nov – 21 Dec 2026: 113 scheduled rows, from $400 "
           "Super Gold Million flights to the $10,400 World Championship. Wynn publishes start "
           "times and structures but its posted structures PDF stops short of the late-December "
           "events, so those rows carry a blank entry rule.",
           D["wynn"], ["wynn", "venetian", "resorts-world"], wynn_extra + "".join(week_blocks))

other_extra = """
<div class="note"><b>Why these rooms sit outside the strict list.</b> Both publish a way to buy a
bigger stack for extra money: Bellagio's $40 “voluntary staff gratuity” adds 20,000 chips, and
Caesars Palace's $50 add-on adds 15,000 chips. Under the brief those are advantage purchases, so
they are documented here for completeness and never ranked. Horseshoe (six daily events from 9 a.m.)
and Resorts World publish schedules but no tournament structure PDF was retrievable today, so their
rows are not listed instead of being guessed.
</div>
"""
venue_page("others", "Other Strip rooms: Bellagio, Caesars Palace",
           "Rooms that publish recurring tournaments but do not meet the no-advantage rule. Kept "
           "separate so the strict comparison stays honest.",
           D["other"], ["bellagio"], other_extra)

# ---------------------------------------------------------------- schedule page
# day plan: for each date pick a primary (best guarantee per buy-in among the strict candidates
# at the earliest reasonable start) and a conditional fallback (latest event whose late-reg close
# is after the primary's early-exit estimate).
def early_exit(r):
    """Computed: bust-out before the money is realistic after ~3 levels."""
    lv = num(r.get("levelMinutes"))
    if not lv or lv not in BREAK_EVERY:
        return None
    return add_minutes(r.get("start"), 3 * lv + BREAK_MIN[int(lv)] * 0)


def estimate_end(r):
    h = planned_hours(r.get("levelMinutes"))
    if h is None:
        return None
    return add_minutes(r.get("start"), round(h * 60))


cands = [r for r in D["venetianSingles"] if r.get("guarantee") and r.get("buyIn")]
by_day = {}
for r in cands:
    by_day.setdefault(r["date"], []).append(r)

plan_rows = []
conflicts = []
for d in sorted(by_day):
    rows = sorted(by_day[d], key=lambda r: (r.get("start") or ""))
    prim = max(rows, key=lambda r: (ratio(r["guarantee"], r["buyIn"]) or 0, r.get("start") or ""))
    others = [r for r in rows if r is not prim]
    fb = None
    if others:
        end_est = estimate_end(prim)
        for r in others:
            close = late_reg_close(r["start"], r["levelMinutes"], r["lateRegLevels"])
            if end_est and close and close > end_est:
                fb = r
                break
    plan_rows.append((d, prim, fb))

# overlap pairs across the whole one-day Venetian slate
for d in sorted(by_day):
    rows = sorted(by_day[d], key=lambda r: (r.get("start") or ""))
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            eend = estimate_end(a)
            bclose = late_reg_close(b["start"], b["levelMinutes"], b["lateRegLevels"])
            if eend and bclose and bclose < eend and a["start"] < b["start"]:
                conflicts.append((d, a, b, eend, bclose))

plain_rows = []
for d, prim, fb in plan_rows:
    for r in (prim, fb):
        if not r:
            continue
        plain_rows.append(r)

plan_html = ['<div class="tablewrap"><table class="grid"><thead><tr><th>Day</th>'
             '<th>Primary event</th><th>Start</th><th>Estimated finish (computed)</th>'
             '<th>Conditional fallback</th><th>Fallback late reg closes</th><th>Feasible together?</th>'
             '</tr></thead><tbody>']
for d, prim, fb in plan_rows:
    eend = estimate_end(prim)
    fbc = late_reg_close(fb["start"], fb["levelMinutes"], fb["lateRegLevels"]) if fb else None
    if fb and eend and fbc and fbc > eend:
        verdict = '<span class="pill yes">yes if you bust before late reg closes</span>'
    elif fb:
        verdict = '<span class="pill no">no — fallback registration closes first</span>'
    else:
        verdict = '<span class="pill unv">no second event that day</span>'
    plan_html.append(
        f'<tr><td><b>{e(d)}</b></td>'
        f'<td>#{prim["eventNo"]} {e(prim["name"])}<div class="sub">{money(prim["buyIn"])} buy-in · '
        f'{money(prim["guarantee"])} GTD · {ratio(prim["guarantee"], prim["buyIn"])}× · '
        f'{src(prim["structureUrl"], "structure")}</div></td>'
        f'<td>{t12(prim["start"])}</td><td>{t12(eend)} <span class="sub">({planned_hours(prim["levelMinutes"])} h)</span></td>'
        f'<td>' + (f'#{fb["eventNo"]} {e(fb["name"])}<div class="sub">{money(fb["buyIn"])} buy-in · '
                   f'{money(fb["guarantee"])} GTD · {src(fb["structureUrl"], "structure")}</div>' if fb else '<span class="blank">none</span>') + '</td>'
        f'<td>{e(fbc) if fbc else "<span class=blank>blank</span>"}</td><td>{verdict}</td></tr>')
plan_html.append("</tbody></table></div>")

conf_html = ['<div class="tablewrap"><table class="grid"><thead><tr><th>Day</th><th>Earlier event</th>'
             '<th>Later event</th><th>Earlier estimated finish</th><th>Later late reg closes</th>'
             '<th>Verdict</th></tr></thead><tbody>']
for d, a, b, eend, bclose in conflicts:
    conf_html.append(
        f'<tr><td>{e(d)}</td><td>#{a["eventNo"]} {e(a["name"])} ({t12(a["start"])})</td>'
        f'<td>#{b["eventNo"]} {e(b["name"])} ({t12(b["start"])})</td>'
        f'<td>{t12(eend)} (computed)</td><td>{e(bclose)} (computed)</td>'
        f'<td><span class="pill no">cannot both be played to the end</span></td></tr>')
conf_html.append("</tbody></table></div>")

schedule_body = f"""
<h1>All-day plan, one primary event per day</h1>
<p class="lede">The brief asks for a schedule that fills a whole day from an early start and for
each day to have a primary event plus a conditional fallback — never an impossible sequence.
Start times, buy-ins and guarantees below are official; the finish times are a label-it-clearly
estimate from level length (see the method note), because no room publishes end times.</p>
<div class="note"><b>Method.</b> Estimated finish = start + (levels a one-day event typically needs
× published level length) + published breaks every 3–4 levels. Levels-to-finish assumptions:
14 at 40-minute levels, 18 at 30, 20 at 25, 22 at 20. Late-registration close = start + (published
late-reg level count × published level length) + breaks. A fallback is only marked feasible when its
late-registration close is <em>after</em> the primary's estimated finish, i.e. the player must bust
out early. Both figures are arithmetic on official inputs, not predictions.</div>
<section class="panel"><h2>Day plan</h2>{''.join(plan_html)}</section>
<section class="panel"><h2>Sequences that cannot work</h2>
<p class="muted">{len(conflicts)} same-day pairs on the one-day Venetian slate cannot both be played
to completion: the later event's registration shuts before the earlier one is likely to end.</p>
{''.join(conf_html)}</section>
<section class="panel"><h2>The early-start problem</h2>
<p>No official Strip page publishes an 8:00 a.m. start. Verified earliest starts:</p>
<table class="kv">
<tr><th>9:10 a.m.</th><td>Venetian #46, $260 turbo milestone satellite, Sat Dec 12 —
{src(VEN, "official schedule")}</td></tr>
<tr><th>9:00 a.m.</th><td>Horseshoe daily tournaments (Caesars' own article; no structure sheet
retrieved) — {src('https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip', "Caesars article")}</td></tr>
<tr><th>10:00 a.m.</th><td>Wynn Super Gold Million Mystery Bounty Day 1A/1C, Dec 10 and 11 —
{src(WYN, "Wynn schedule PDF")}</td></tr>
<tr><th>10:10 a.m.</th><td>Venetian one-day slate (Seniors, Tag Team, RaceDay) — {src(VEN, "official schedule")}</td></tr>
</table>
<p>A realistic all-day plan therefore runs about 9:10 a.m. to midnight, or 10:10 a.m. to midnight
if the player prefers the $300–$2,200 one-day events with 30–40-minute levels.</p>
</section>
"""
page("schedule.html", "All-day plan", schedule_body)

# ---------------------------------------------------------------- rules page
rules_body = f"""
<h1>Entry rules, stored field by field</h1>
<p class="lede">For each event the brief asks for single-entry, re-entry, add-on and fee to be held
separately, each with its source excerpt and retrieval date. The excerpt column is the exact
sentence (or the exact absence of one) that the classification rests on.</p>
<div class="note"><b>Reading rule.</b> <span class="pill no">re-entry</span> means an official
sentence prices or permits another entry. <span class="pill unv">unverified</span> means no
sentence exists either way — that is not a freezeout confirmation. <span class="pill yes">single</span>
means an official page states the event is single-entry; <b>zero</b> rows qualify today.</div>
{toolbar(("search", "date", "single", "venue"))}
<section class="panel">
<div class="tablewrap"><table class="grid"><thead><tr>
<th>Date</th><th>Venue / event</th><th>Single entry</th><th>Re-entry</th><th>Add-on</th>
<th>Fee (buy-in − pool)</th><th>Prize-pool portion</th><th>Excerpt</th><th>Source</th><th>Checked</th>
</tr></thead><tbody>
"""
rule_rows = []
for r in EVENTS:
    if not (r.get("excerpt") or r.get("singleEntry") != "unverified"):
        continue
    rule_rows.append(r)
    se = r["singleEntry"]
    pill = ('<span class="pill no">no — re-entry</span>' if se == "no"
            else '<span class="pill unv">unverified</span>' if se == "unverified"
            else '<span class="pill yes">yes — confirmed</span>')
    nm = (f'#{r["eventNo"]} ' if r.get("eventNo") else "") + str(r.get("name"))
    rules_body += (
        f'<tr data-date="{e(r.get("date"))}" data-single="{e(se)}" data-venue="{e(r.get("venueSlug"))}"'
        f' data-text="{html.escape((str(r.get("name")) + " " + str(r.get("venue"))).lower(), quote=True)}">'
        f'<td>{e(r.get("date"))}</td><td>{e(r.get("venue"))}<div class="sub">{e(nm)}</div></td>'
        f'<td>{pill}</td><td>{e(r.get("reEntry"))}</td><td>{e(r.get("addOn"))}</td>'
        f'<td class="num">{money(r.get("feeTotal"))}</td><td class="num">{money(r.get("prizePoolPortion"))}</td>'
        f'<td class="ex">{e(r.get("excerpt"))}' +
        (f'<div class="sub">{e(r.get("staffFeeNote"))}</div>' if r.get("staffFeeNote") else "") + '</td>'
        f'<td class="srcs">{src(r.get("structureUrl"), "structure")} {src(r.get("scheduleUrl"), "schedule")}</td>'
        f'<td class="num">{e(r.get("retrieved"))}</td></tr>')
rules_body += f"""</tbody></table></div>
<p class="muted">{len(rule_rows)} rows carry a stored rule statement or an explicit absence note.</p>
</section>
<section class="panel"><h2>What each field means</h2>
<table class="kv">
<tr><th>single_entry</th><td>Only “yes” when an official page states the event is single-entry.
Currently zero. Nothing is inferred from silence.</td></tr>
<tr><th>re_entry</th><td>The published re-entry mechanic, quoted: “unlimited re-entry until the
start of level 9”, “One (1) Entry and One (1) re-entry for each starting flight”, or the Venetian's
“subsequent buy in's … will be $200”.</td></tr>
<tr><th>add_on</th><td>Any published payment that adds chips or an advantage beyond the buy-in.
Bellagio's $40 chip gratuity and Caesars' $50 add-on are recorded here.</td></tr>
<tr><th>fee</th><td>Buy-in minus the published prize-pool portion. For LIPS events a flat LIPS fee is
recorded in a note because it belongs to neither bucket.</td></tr>
<tr><th>retrieved</th><td>The date the source was read. {RET} for every row in this build.</td></tr>
</table></section>
"""
page("rules.html", "Entry rules", rules_body)

# ---------------------------------------------------------------- hotels
h = D["hotels"]
hot_rows = []
for x in h:
    nightly = (x["checkoutTotal"] / x["nights"]) if x.get("checkoutTotal") else None
    hot_rows.append(f"""<tr>
<td><b>{e(x["venue"])}</b><div class="sub">{e(x["quality"])}</div></td>
<td>{e(x["room"])}<div class="sub">{e(x["occupancy"])}</div></td>
<td class="num">{money(x["roomSubtotal"])}</td>
<td class="num">{money(x["resortFeePerNight"])}<div class="sub">{money(x["resortFeeTotal"])} total</div></td>
<td class="num">{money(x["taxes"])}<div class="sub">{(("%.2f%%" % (x["taxRate"] * 100)) if x.get("taxRate") else "")}</div></td>
<td class="num"><b>{money(x["checkoutTotal"])}</b></td>
<td class="num">{(("$%.2f" % nightly) if nightly else '<span class="blank">blank</span>')}</td>
<td class="num">{money(x["displayedAverageNightly"])}</td>
<td class="ex">{e(x["parking"])}<div class="sub">{e(x["cancellation"])}</div></td>
<td class="srcs">{src(x["rateSource"], "rate")} {src(x["resortFeeSource"], "resort fee")} {src(x["taxSource"], "tax")}</td>
<td class="num">{e(x["timestamp"])}</td></tr>""")

nightly_log = "".join(
    f'<tr><td>{e(x["venue"])}</td><td>Night {i + 1}</td><td class="num">{money(r)}</td>'
    f'<td class="num">$55.00</td><td class="num">{money(round((r + 55) * 0.1338, 2))}</td>'
    f'<td class="num">{money(round((r + 55) * 1.1338, 2))}</td></tr>'
    for x in h if x.get("roomRates") for i, r in enumerate(x["roomRates"]))

hotels_body = f"""
<h1>Hotels: true cost per night</h1>
<p class="lede">Rates are kept as a dated log rather than a single number, because the same suite on
the same booking engine swings from $231.75 to $779.25 across one week. True cost per night = room
rate + mandatory resort fee + Clark County lodging tax. Room rates are quoted before tax by the
hotel; the resort fee is $55 per night at both the Venetian and the Wynn; the tax for a
primary-gaming-corridor resort hotel is <b>13.38%</b> (Clark County ordinance 4.08.130).</p>
<div class="note"><b>Baseline stay for every comparison:</b> 2 adults, 1 room, check-in Wed 2 Dec
2026, check-out Wed 9 Dec 2026, 7 nights — the middle of the DeepStack Extravaganza IV and the
first week of the WPT series, so the same dates apply to both venues.</div>
<section class="panel"><h2>Dated rate log</h2>
<div class="tablewrap"><table class="grid"><thead><tr>
<th>Hotel</th><th>Room / occupancy</th><th>Room subtotal</th><th>Resort fee</th><th>Tax</th>
<th>Checkout total</th><th>True cost / night</th><th>Hotel-displayed average</th>
<th>Parking &amp; cancellation</th><th>Sources</th><th>Rate timestamp</th>
</tr></thead><tbody>{''.join(hot_rows)}</tbody></table></div>
</section>
<section class="panel"><h2>Night-by-night breakdown where the engine published it</h2>
<div class="tablewrap"><table class="grid"><thead><tr><th>Hotel</th><th>Night</th><th>Room rate
(before tax)</th><th>Resort fee</th><th>Tax at 13.38%</th><th>All-in that night</th></tr></thead>
<tbody>{nightly_log}</tbody></table></div>
<p class="muted">Tax column is computed at the official 13.38% rate on that night's room rate plus
resort fee; the hotel's own total tax line is $817.46 for the week.</p>
</section>
<section class="panel"><h2>What is verifiable and what is not</h2>
<table class="kv">
<tr><th>Venetian</th><td>Full itemised quote captured: “Estimated cost of stay $6,927.21”, seven
nightly room rates, $55 resort fee each night, $817.46 taxes. {src('https://www.venetianlasvegas.com/book', 'booking engine')}</td></tr>
<tr><th>Wynn</th><td>Booking engine is JavaScript-only; the captured screen showed a rounded $711
average per night including the $55 resort fee and excluding tax. No 7-night after-tax total was
rendered, so the checkout total is blank rather than estimated.
{src('https://www.wynnlasvegas.com/terms-and-conditions/850257', 'Wynn terms')}</td></tr>
<tr><th>Resort fee</th><td>Venetian $55 + tax per night {src('https://www.venetianlasvegas.com/resort/resort-fee.html', 'Venetian resort fee')};
Wynn $55 + tax per night, including self-parking for two vehicles {src('https://www.wynnlasvegas.com/terms-and-conditions/850257', 'Wynn terms')}.</td></tr>
<tr><th>Tax</th><td>13.38% for resort hotels inside the primary gaming corridor, per the Clark
County schedule of transient lodging tax rates {src('https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf', 'county ordinance')}.
The Venetian's own tax line ($817.46 on $6,222.25 of room + resort fee = 13.14%) is consistent with it.</td></tr>
<tr><th>Parking</th><td>Wynn: included in the resort fee. Venetian: no official parking page
retrievable (404), only the Rewards tier note. {src('https://www.venetianlasvegas.com/resort/resort-fee.html', 'Venetian resort fee')}</td></tr>
<tr><th>Cancellation</th><td>Not published on any retrievable page for either hotel; it lives on the
rate-rules screen at booking. Left blank — this is flag S12.</td></tr>
</table></section>
"""
page("hotels.html", "Hotels", hotels_body)

# ---------------------------------------------------------------- routes
route_rows = []
for r in D["routes"]:
    pill = '<span class="pill yes">≤ 30 min</span>' if r["within30"] else '<span class="pill no">&gt; 30 min</span>'
    route_rows.append(
        f'<tr data-walk="{r["minutes"]}" data-within="{"1" if r["within30"] else "0"}">'
        f'<td><b>{e(r["pair"])}</b></td><td class="num">{e(r["miles"]) if r["miles"] else "<span class=blank>blank</span>"}</td>'
        f'<td class="num">{e(r["minutes"])} min</td><td>{e(r["path"])}</td><td>{pill}</td>'
        f'<td class="ex">{e(r["note"])}</td><td class="srcs">{src(r["source"], "route data")}</td></tr>')

routes_body = f"""
<h1>Walking the Strip: is the hotel really within 30 minutes?</h1>
<p class="lede">Every hotel-to-poker-room pair used in this dashboard is listed with its
door-to-door walk time. The 30-minute filter is applied and shown, and anything marginal is labelled
marginal rather than rounded down to “fine”.</p>
<div class="note"><b>Source honesty.</b> Google and Apple Maps walking directions cannot be linked
with a stable, citable route, so the times below come from a published Strip walking chart that
measures door-to-door routes {src('https://www.casinocompassapp.com/transportation/walking-the-strip', 'Casino Compass walking chart')}.
They are second-party measurements of official property layouts, not the casinos' own pages, and
are labelled that way. Nothing here is presented as a Google Maps figure.</div>
<div class="toolbar"><label class="chk"><input id="walkOnly" type="checkbox" checked>
Only pairs within 30 minutes</label><span class="count" id="rowcount"></span></div>
<section class="panel">
<div class="tablewrap"><table class="grid" data-table="routes"><thead><tr><th>Pair</th><th>Miles</th>
<th>Walk time</th><th>Route</th><th>Within 30 min</th><th>Note</th><th>Source</th></tr></thead>
<tbody>{''.join(route_rows)}</tbody></table></div>
</section>
<section class="panel"><h2>What this means for hotel choice</h2>
<ul class="tight">
<li><b>Venetian and Wynn are 10–15 minutes apart</b> across the Sands Avenue bridge, so either
property lets a player use both rooms in one trip without a taxi.</li>
<li><b>Bellagio is 18–25 minutes from the Venetian</b> — inside the limit, but at the top of it when
you add lobby and poker-room navigation. Treat it as marginal.</li>
<li><b>Resorts World is 12–18 minutes from Wynn</b> but 25+ from the Venetian; it only works as a
base if the plan centres on the Wynn.</li>
<li><b>Nothing south of Bellagio stays inside 30 minutes</b> of the Venetian on foot (MGM Grand to
Bellagio is 35–45 minutes), so a south-Strip hotel would break the walking rule.</li>
</ul>
</section>
"""
page("routes.html", "Walking routes", routes_body)

# ---------------------------------------------------------------- calculator
calc_hotels = [x for x in D["hotels"]]
opts = "".join(
    f'<option value="{x["slug"]}" data-total="{x["checkoutTotal"] or ""}" data-nights="{x["nights"]}"'
    f' data-avg="{(x["checkoutTotal"] / x["nights"]) if x["checkoutTotal"] else ""}">{e(x["venue"])}'
    f'{" — $" + format(round(x["checkoutTotal"], 2), ",.2f") + " / " + str(x["nights"]) + " nights" if x["checkoutTotal"] else " — no checkout total published"}'
    "</option>" for x in calc_hotels)
entry_opts = "".join(
    f'<option value="{r["buyIn"]}" data-gtd="{r.get("guarantee") or ""}" data-label="{"#" + str(r["eventNo"]) + " " if r.get("eventNo") else ""}{html.escape(str(r["name"]))} ({r["date"]})">'
    f'{"#" + str(r["eventNo"]) + " " if r.get("eventNo") else ""}{html.escape(str(r["name"]))} — {money(r["buyIn"]).replace("$", "$")} — {r["date"]}</option>'
    for r in sorted([x for x in EVENTS if x.get("buyIn")], key=lambda r: (r["buyIn"], str(r.get("date")))))

calc_body = f"""
<h1>Trip cost calculator</h1>
<p class="lede">The brief's formula, implemented literally: <b>entries × buy-ins + nights × true
hotel cost</b>. True nightly cost is the dated quote on this site (room + resort fee + tax), never a
marketing “from” rate. If a hotel has no published checkout total, the calculator refuses to invent
one and tells you why.</p>
<section class="panel">
<h2>1. Entries</h2>
<p class="muted">Add each event you plan to play. Buy-ins are official; the guarantee is shown so you
can see what the buy-in is competing for.</p>
<div class="row">
  <select id="evPick" aria-label="Pick an event">{entry_opts}</select>
  <button class="btn" id="addEv">Add entry</button>
  <button class="btn ghost" id="clearEv">Clear</button>
</div>
<table class="grid" id="entryList"><thead><tr><th>Event</th><th>Buy-in</th><th>Guarantee</th><th></th></tr></thead>
<tbody></tbody></table>
<h2>2. Hotel</h2>
<div class="row">
  <select id="hotelPick" aria-label="Pick a hotel">{opts}</select>
  <label class="chk">Nights <input id="nights" type="number" min="1" value="7" style="width:5rem"></label>
</div>
<h2>3. Total</h2>
<div class="totals">
  <div><span>Entries</span><b id="tEntries">0</b></div>
  <div><span>Buy-ins</span><b id="tBuyins">$0</b></div>
  <div><span>True hotel cost / night</span><b id="tNight">—</b></div>
  <div><span>Hotel total</span><b id="tHotel">—</b></div>
  <div class="grand"><span>Trip cost</span><b id="tTotal">—</b></div>
</div>
<p class="muted" id="calcNote"></p>
</section>
<section class="panel"><h2>Reference: the two verified stays</h2>
<table class="grid"><thead><tr><th>Hotel</th><th>7 nights, checkout total</th><th>True cost / night</th>
<th>Source</th></tr></thead><tbody>
<tr><td>The Venetian</td><td class="num">$6,927.21</td><td class="num">$989.60</td>
<td class="srcs">{src('https://www.venetianlasvegas.com/book', 'booking engine')}</td></tr>
<tr><td>Wynn Las Vegas</td><td class="num"><span class="blank">blank</span></td>
<td class="num"><span class="blank">blank</span></td>
<td class="srcs">{src('https://www.wynnlasvegas.com/terms-and-conditions/850257', 'terms page')}
<span class="sub">engine showed a $711 average including the $55 fee, excluding tax</span></td></tr>
</tbody></table>
<p class="muted">The Wynn row stays blank on purpose: an average nightly rate is not a checkout
total, and the brief asks for the total.</p>
</section>
"""
page("calculator.html", "Trip cost", calc_body)

# ---------------------------------------------------------------- flagged
flag_rows = "".join(
    f'<tr><td><b>{e(f["id"])}</b></td><td><span class="pill {"no" if f["severity"] == "blocker" else "unv"}">{e(f["severity"])}</span></td>'
    f'<td><b>{e(f["title"])}</b><div class="sub">{e(f["detail"])}</div></td>'
    f'<td class="ex">{e(f["action"])}</td>'
    f'<td class="srcs">{" ".join(src(u, "source " + str(i + 1)) for i, u in enumerate(f["sources"]))}</td>'
    f'<td class="num">{RET}</td></tr>' for f in D["flags"])

flagged_body = f"""
<h1>Flagged for review</h1>
<p class="lede">Every irregularity found while checking the sources line by line. Nothing here
blocks the site from going live; it is published so you can see exactly where the evidence is
thin, contradictory or missing, with a link to the official page that shows it.</p>
<section class="stats">
{stat("Blockers", sum(1 for f in D["flags"] if f["severity"] == "blocker"), "evidence gaps that change the recommendation")}
{stat("Needs a human look", sum(1 for f in D["flags"] if f["severity"] == "review"), "contradictions in official pages")}
{stat("Informational", sum(1 for f in D["flags"] if f["severity"] == "info"), "resolved or expected")}
</section>
<section class="panel">
<div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Severity</th><th>Finding</th>
<th>What to do</th><th>Official sources</th><th>Checked</th></tr></thead>
<tbody>{flag_rows}</tbody></table></div>
</section>
"""
page("flagged.html", "Flagged for review", flagged_body)

# ---------------------------------------------------------------- questions
q_rows = "".join(
    f'<tr><td><b>{e(q["q"])}</b></td><td class="ex">{e(q["why"])}</td><td class="ex">{e(q["how"])}</td>'
    f'<td><span class="pill {"unv" if q["status"] == "open" else "no"}">{e(q["status"])}</span></td></tr>'
    for q in D["questions"])

questions_body = f"""
<h1>Questions that must be answered before deciding</h1>
<p class="lede">These are the unknowns that actually change the recommendation. Each one is listed
with why it matters and how to close it — an email, a phone call, or a page that has to be read at
booking time.</p>
<section class="panel">
<div class="tablewrap"><table class="grid"><thead><tr><th>Question</th><th>Why it changes the
decision</th><th>How to close it</th><th>Status</th></tr></thead><tbody>{q_rows}</tbody></table></div>
</section>
<section class="panel"><h2>Information we have</h2>
<ul class="tight">
<li>Complete Venetian one-day schedule with guarantee, stack, level length, late-reg cut-off and
fee split for 48 events, plus 9 multi-flight events and 7 satellites ({RET}).</li>
<li>Complete Wynn series schedule, 113 rows, with the entry rule for every event Wynn published
terms for.</li>
<li>Venetian 7-night checkout total and night-by-night rates; Wynn resort fee and terms; Clark
County 13.38% lodging tax ordinance.</li>
<li>Strip walking times between every venue pair used, with routes.</li>
</ul>
<h2>Information we do not have</h2>
<ul class="tight">
<li>Any official sentence confirming a freezeout on the Strip (flag S01).</li>
<li>Wynn entry rules after 15 Dec, including the $10,400 World Championship (flag S06).</li>
<li>Bellagio's real Saturday buy-in — the PDF contradicts itself three ways (flag S03).</li>
<li>Cancellation deadlines at either hotel, and Venetian parking (flag S12).</li>
<li>Any rate at Resorts World, and any tournament structure sheet for Horseshoe.</li>
</ul>
</section>
"""
page("questions.html", "Questions", questions_body)

# ---------------------------------------------------------------- suggestions
s_rows = "".join(
    f'<tr><td><b>{e(s["id"])}</b></td><td><b>{e(s["title"])}</b><div class="sub">{e(s["body"])}</div></td>'
    f'<td class="num">{e(s["effort"])}</td><td class="num">{e(s["impact"])}</td></tr>'
    for s in D["suggestions"])
suggestions_body = f"""
<h1>Suggestions — pick a path before changing anything</h1>
<p class="lede">Improvements, ordered only by effort and likely impact, so you can choose. Nothing
here is implemented yet; the site stays as verified as it is until you pick.</p>
<section class="panel">
<div class="tablewrap"><table class="grid"><thead><tr><th>ID</th><th>Change</th><th>Effort</th>
<th>Impact</th></tr></thead><tbody>{s_rows}</tbody></table></div>
<p class="muted">Effort S = a display or data change; M = a new computation or page; L = new
research scope.</p>
</section>
<section class="panel"><h2>The one change that unlocks the most</h2>
<p>Everything on this site is capped by one missing fact: no Strip room publishes a freezeout rule.
One batch of emails asking “is this event single-entry, and when does registration close” would
convert 46 unverified Venetian rows and dozens of Wynn rows into a real single-entry list
(suggestion G02). Until then, ranking those rows as if they were single-entry would be exactly the
kind of inference the brief forbids.</p>
</section>
"""
page("suggestions.html", "Suggestions", suggestions_body)

# ---------------------------------------------------------------- change log page
cl_path = os.path.join(ROOT, "data-6d1e0039", "change-log.json")
changes = []
if os.path.exists(cl_path):
    try:
        changes = json.load(open(cl_path)).get("changes", [])
    except Exception:
        changes = []
ch_rows = "".join(
    f'<tr><td>{e(c.get("checked"))}</td><td class="srcs">{src(c.get("url"), c.get("url"))}</td>'
    f'<td><span class="pill {"no" if c.get("changed") else "yes"}">{"changed" if c.get("changed") else "unchanged"}</span></td>'
    f'<td class="num">{e(c.get("status"))}</td><td class="ex">{e(c.get("note"))}</td></tr>'
    for c in changes) or '<tr><td colspan="5" class="muted">No scheduled run has been recorded yet. The first run of the re-check workflow writes here.</td></tr>'

changes_body = f"""
<h1>Automatic re-check and change log</h1>
<p class="lede">Every official URL this dashboard depends on is re-fetched on a schedule, hashed,
and compared with the previous snapshot. When a page changes, the row is marked and the change is
recorded here — you never have to trust that a number is still current.</p>
<section class="stats">
{stat("URLs monitored", len(json.load(open(os.path.join(ROOT, 'data-6d1e0039', 'sources.json')))['urls']), "schedules, 37 structure sheets, fees, tax, routes")}
{stat("Schedule", "every 6 h", "GitHub Actions cron, workflow recheck-6d1e0039.yml")}
{stat("Rows carrying a last-checked date", tot_rows, "2026-11-17 in this build")}
{stat("Recorded changes", len(changes), "appended to data-6d1e0039/change-log.json")}
</section>
<section class="panel"><h2>How a change is detected</h2>
<ol class="tight">
<li>The workflow runs <code>scripts/recheck_6d1e0039.py</code>, which downloads each URL with a
plain HTTP client (no JavaScript), strips whitespace, and stores a SHA-256 hash in
<code>data-6d1e0039/source-hashes.json</code>.</li>
<li>If a hash differs from the previous run, the URL is written to
<code>data-6d1e0039/change-log.json</code> with the date, HTTP status and the byte size before and
after, and this page marks it <span class="pill no">changed</span>.</li>
<li>The workflow commits the new hashes, so the next run compares against the most recent state.</li>
<li>A page that returns 403 or 404 is recorded as an error, not as “changed”, so a blocked scraper
cannot masquerade as a schedule update.</li>
</ol>
<h2>What the automatic check cannot do</h2>
<ul class="tight">
<li>It cannot read the Wynn booking engine (JavaScript-only) or the Venetian calendar widget, so
hotel totals need the manual re-quote described on the Hotels page.</li>
<li>It cannot decide whether a changed page still supports the classification — a change is a
prompt to re-read, not a verdict.</li>
</ul>
</section>
<section class="panel"><h2>Recorded runs</h2>
<div class="tablewrap"><table class="grid"><thead><tr><th>Run date</th><th>URL</th><th>Result</th>
<th>HTTP</th><th>Note</th></tr></thead><tbody>{ch_rows}</tbody></table></div>
</section>
"""
page("changes.html", "Change log", changes_body)

# ---------------------------------------------------------------- assets
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
with open(os.path.join(OUT, "assets", "style.css"), "w") as f:
    f.write("""/* dashboard-6d1e0039 - session 6d1e0039 */
:root{--bg:#0b0f14;--panel:#121821;--panel2:#161e29;--line:#233040;--txt:#e8eef7;
--mut:#93a4b8;--acc:#43d9a3;--acc2:#6aa8ff;--warn:#f5b942;--bad:#ff6b6b}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.55 -apple-system,BlinkMacSystemFont,
"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc2);text-decoration:none}a:hover{text-decoration:underline}
.top{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between;
padding:.85rem 1.25rem;border-bottom:1px solid var(--line);background:#0e141c;position:sticky;top:0;z-index:9}
.brand{display:flex;gap:.65rem;align-items:center}
.brand small{display:block;color:var(--mut);font-size:.76rem}
.mark{display:grid;place-items:center;width:34px;height:34px;border-radius:9px;
background:linear-gradient(135deg,#43d9a3,#6aa8ff);color:#06110c;font-weight:800}
nav{display:flex;flex-wrap:wrap;gap:.25rem;font-size:.83rem}
nav a{padding:.3rem .55rem;border-radius:7px;color:var(--mut)}
nav a:hover{background:#182231;color:var(--txt);text-decoration:none}
nav a.on{background:#1d2b3c;color:var(--txt);font-weight:600}
main{max-width:1500px;margin:0 auto;padding:1.4rem 1.25rem 4rem}
h1{font-size:1.55rem;margin:.2rem 0 .5rem}h2{font-size:1.08rem;margin:0 0 .7rem}
h3{font-size:.95rem;margin:1.1rem 0 .4rem;color:#cfe0f5}
.lede{color:#c2d0e0;max-width:105ch;margin:.2rem 0 1.2rem}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.7rem;margin:1rem 0 1.4rem}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:.8rem .9rem}
.stat .v{font-size:1.5rem;font-weight:700;color:var(--acc)}
.stat .l{font-size:.8rem;color:var(--mut)}
.stat .n{font-size:.72rem;color:#6f8298;margin-top:.15rem}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1.1rem 1.15rem;
margin:0 0 1.2rem}
.note{background:#13212b;border-left:3px solid var(--acc2);border-radius:8px;padding:.75rem .9rem;
margin:.4rem 0 1rem;font-size:.9rem;color:#cfe0f0}
.toolbar{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;margin:.2rem 0 .8rem}
input[type=search],select,input[type=number]{background:var(--panel2);border:1px solid var(--line);
color:var(--txt);border-radius:8px;padding:.45rem .6rem;font:inherit;min-width:9rem}
input[type=search]{min-width:22rem}
.chk{display:flex;gap:.4rem;align-items:center;color:var(--mut);font-size:.85rem}
.count{color:var(--mut);font-size:.8rem;margin-left:auto}
.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:10px}
table.grid{border-collapse:collapse;width:100%;font-size:.83rem}
table.grid th{position:sticky;top:0;background:#0f1620;text-align:left;padding:.55rem .6rem;
border-bottom:1px solid var(--line);color:#a9bcd2;font-weight:600;white-space:nowrap}
table.grid td{padding:.5rem .6rem;border-bottom:1px solid #1a2432;vertical-align:top}
table.grid tr:hover td{background:#131c26}
td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
td.ex{max-width:44ch;color:#c4d2e2}
td.srcs{white-space:nowrap}
.srclink{font-size:.75rem;border:1px solid #2b3d52;padding:.1rem .35rem;border-radius:5px;
background:#152233;display:inline-block}
.sub{color:var(--mut);font-size:.75rem;margin-top:.15rem}
.blank{color:#6b7c90;font-style:italic;font-size:.8rem}
.pill{display:inline-block;padding:.1rem .45rem;border-radius:999px;font-size:.72rem;font-weight:600}
.pill.yes{background:#12352a;color:#5ee0ae;border:1px solid #1d5c45}
.pill.no{background:#3a1620;color:#ff8b8b;border:1px solid #632b39}
.pill.unv{background:#3a2f12;color:#f5cb6b;border:1px solid #6b5524}
table.kv{width:100%;border-collapse:collapse;font-size:.86rem}
table.kv th{text-align:left;width:20%;padding:.5rem .6rem;border-bottom:1px solid #1a2432;
color:#a9bcd2;vertical-align:top;font-weight:600}
table.kv td{padding:.5rem .6rem;border-bottom:1px solid #1a2432;color:#c9d7e6}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:.8rem}
.card{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:.9rem;
color:var(--txt)}
.card:hover{border-color:#3a5570;text-decoration:none}
.card h3{margin:.1rem 0 .35rem;color:#e8f1fb}
.card p{margin:0;color:var(--mut);font-size:.83rem}
ul.tight{margin:.3rem 0;padding-left:1.1rem}ul.tight li{margin:.35rem 0}
.row{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin:.4rem 0 .8rem}
.btn{background:var(--acc);color:#06110c;border:0;border-radius:8px;padding:.45rem .8rem;
font:inherit;font-weight:700;cursor:pointer}
.btn.ghost{background:#1b2735;color:var(--txt);border:1px solid var(--line)}
.totals{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:.6rem;margin:.6rem 0}
.totals div{background:var(--panel2);border:1px solid var(--line);border-radius:9px;padding:.6rem .7rem}
.totals span{display:block;font-size:.75rem;color:var(--mut)}
.totals b{font-size:1.15rem}
.totals .grand{border-color:#2f6b52;background:#122a22}.totals .grand b{color:var(--acc)}
.muted{color:var(--mut);font-size:.82rem}
footer{border-top:1px solid var(--line);padding:1rem 1.25rem 2rem;color:var(--mut);font-size:.78rem;
max-width:1500px;margin:0 auto}
code{background:#101923;padding:.05rem .3rem;border-radius:4px;font-size:.85em}
@media(max-width:640px){input[type=search]{min-width:100%}nav{font-size:.78rem}}
""")

with open(os.path.join(OUT, "assets", "app.js"), "w") as f:
    f.write("""// dashboard-6d1e0039 - filters, search and trip calculator
(function(){
  function each(t,fn){Array.prototype.forEach.call(document.querySelectorAll(t),fn)}

  // ---- generic filters: search + date + single + venue + walking
  var q = document.getElementById('q');
  var df = document.getElementById('dateFilter');
  var so = document.getElementById('singleOnly');
  var vf = document.getElementById('venueFilter');

  each('table.grid tbody tr', function(tr){ if(tr.dataset.date && df){
    if(!df.querySelector('option[value="'+tr.dataset.date+'"]')){
      var o=document.createElement('option');o.value=tr.dataset.date;
      o.textContent=tr.dataset.date;df.appendChild(o);
    }}});
  each('table.grid tbody tr', function(tr){ if(tr.dataset.venue && vf){
    if(!vf.querySelector('option[value="'+tr.dataset.venue+'"]')){
      var o=document.createElement('option');o.value=tr.dataset.venue;
      o.textContent=tr.dataset.venue;vf.appendChild(o);
    }}});
  function sortOpts(sel){ if(!sel) return;
    var opts=Array.prototype.slice.call(sel.options).slice(1)
      .sort(function(a,b){return a.value<b.value?-1:1});
    var cur=sel.value; while(sel.options.length>1) sel.remove(1);
    opts.forEach(function(o){sel.appendChild(o)}); sel.value=cur || ''; }
  sortOpts(df); sortOpts(vf);

  function apply(){
    var term=(q&&q.value||'').trim().toLowerCase();
    var day=df&&df.value, one=so&&so.checked, ven=vf&&vf.value;
    var shown=0, total=0;
    each('table.grid tbody tr', function(tr){
      if(!tr.dataset.text && !tr.dataset.date && !tr.dataset.venue) return;
      total++;
      var ok=true;
      if(term && (tr.dataset.text||'').indexOf(term)===-1) ok=false;
      if(ok && day && tr.dataset.date!==day) ok=false;
      if(ok && one && tr.dataset.single!=='yes') ok=false;
      if(ok && ven && tr.dataset.venue!==ven) ok=false;
      tr.style.display = ok?'':'none';
      if(ok) shown++;
    });
    each('#rowcount', function(el){ el.textContent = shown+' of '+total+' rows'; });
    var note=document.getElementById('calcNote'); // untouched
  }
  [q,df,so,vf].forEach(function(el){ if(el){ el.addEventListener('input',apply); el.addEventListener('change',apply);} });
  var walk=document.getElementById('walkOnly');
  function applyWalk(){
    if(!walk) return;
    var rows=document.querySelectorAll('table[data-table="routes"] tbody tr'), shown=0;
    Array.prototype.forEach.call(rows,function(tr){
      var ok = !walk.checked || tr.dataset.within==='1';
      tr.style.display = ok?'':'none'; if(ok) shown++;
    });
    each('#rowcount',function(el){el.textContent=shown+' of '+rows.length+' rows';});
  }
  if(walk){ walk.addEventListener('change',applyWalk); applyWalk(); }
  if(document.querySelector('table.grid tbody tr[data-text]')) apply();

  // ---- trip cost calculator
  var list=document.getElementById('entryList');
  if(!list) return;
  var entries=[];
  var pick=document.getElementById('evPick');
  var hotel=document.getElementById('hotelPick');
  var nights=document.getElementById('nights');
  var note=document.getElementById('calcNote');

  function money(v){ return v===null||v===undefined||isNaN(v) ? null :
      '$'+Number(v).toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:0}); }
  function money2(v){ return v===null||isNaN(v)? null :
      '$'+Number(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}); }

  function render(){
    var tb=list.querySelector('tbody'); tb.innerHTML='';
    entries.forEach(function(en,i){
      var tr=document.createElement('tr');
      tr.innerHTML='<td>'+en.label+'</td><td class="num">'+money(en.buy)+
        '</td><td class="num">'+(en.gtd?money(en.gtd):'<span class="blank">blank</span>')+
        '</td><td><button class="btn ghost" data-i="'+i+'">remove</button></td>';
      tb.appendChild(tr);
    });
    tb.querySelectorAll('button[data-i]').forEach(function(b){
      b.addEventListener('click',function(){ entries.splice(+b.dataset.i,1); render(); });
    });
    var buyins=entries.reduce(function(s,e){return s+e.buy;},0);
    var o=hotel.options[hotel.selectedIndex];
    var total=o&&o.dataset.total?Number(o.dataset.total):null;
    var nn=nights.value?Number(nights.value):0;
    var perNight = total? total/Number(o.dataset.nights||7) : null;
    document.getElementById('tEntries').textContent=entries.length;
    document.getElementById('tBuyins').textContent=money(buyins)||'$0';
    document.getElementById('tNight').textContent= perNight? money2(perNight) : '—';
    var hotelTotal = perNight && nn ? perNight*nn : null;
    document.getElementById('tHotel').textContent= hotelTotal? money2(hotelTotal) : '—';
    document.getElementById('tTotal').textContent= hotelTotal? money2(buyins+hotelTotal) : '—';
    if(!total){
      note.textContent='This hotel has no published checkout total on this site, so the hotel part '+
        'and the trip total stay blank rather than being estimated. See Hotels → “What is '+
        'verifiable and what is not”.';
    } else if(nn!==Number(o.dataset.nights)){ note.textContent='Note: the quoted total covers '+o.dataset.nights+
        ' nights. You asked for '+nn+', so the per-night figure is applied to your number of nights — '+
        'the hotel may price a different length of stay differently.';
    } else { note.textContent='Hotel cost = the dated 7-night quote ÷ 7, so it includes room, resort fee and tax.'; }
  }
  document.getElementById('addEv').addEventListener('click',function(){
    var o=pick.options[pick.selectedIndex]; if(!o) return;
    var g=o.getAttribute('data-gtd');
    entries.push({label:o.getAttribute('data-label')||o.textContent, buy:Number(o.value),
      gtd:g?Number(g):null});
    render();
  });
  document.getElementById('clearEv').addEventListener('click',function(){entries=[];render();});
  hotel.addEventListener('change',render); nights.addEventListener('input',render);
  render();
})();
""")

print("pages:", sorted(os.listdir(OUT)))
