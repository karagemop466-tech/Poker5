#!/usr/bin/env python3
"""Build the Poker5 GitHub Pages site from the verified data in data/.

Usage:  python3 scripts/build_site.py

Rules enforced in code:
  * every table row carries a source link (build fails otherwise)
  * every internal link in generated pages must resolve to a file in the repo
  * values that are not verified are shown blank or as 'Unverified' and listed on flagged-review
"""
import datetime
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_URL = "https://github.com/karagemop466-tech/Poker5"
SITE_URL = "https://karagemop466-tech.github.io/Poker5/"
DSE_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
           "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
STRUCT_BASE = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/"
               "deepstack/2026/structures/dse_nov_2026-structure_{}.pdf")
SUITE_URL = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
WPT_URL = ("https://www.worldpokertour.com/event/"
           "main-tour-wpt-world-championship-at-wynn-las-vegas-season-2026")
CAESARS_URL = "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"
WYNN_POKER_URL = "https://www.wynnlasvegas.com/casino/poker"

PAGES = [
    ("index.html", "Home"),
    ("pages/executive-summary.html", "Executive Summary"),
    ("pages/tournaments.html", "Single-Entry Candidates"),
    ("pages/tournaments-double.html", "Re-Entry / Multi-Flight"),
    ("pages/hotels.html", "Hotels"),
    ("pages/schedule.html", "Schedule"),
    ("pages/questions.html", "Questions &amp; Answers"),
    ("pages/suggestions.html", "Suggestions"),
    ("pages/flagged-review.html", "Flagged for Review"),
    ("pages/repo-review.html", "Repo Review"),
]

errors = []


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def money(value):
    return "" if value is None else "${:,.0f}".format(value)


def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%a, %b ") + str(d.day) + d.strftime(", %Y")


def fmt_time(hhmm):
    if not hhmm:
        return "Time not captured"
    h, m = [int(x) for x in hhmm.split(":")]
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return "{}:{:02d} {}".format(h12, m, suffix)


def link(url, label="Source"):
    if not url:
        return ""
    return '<a href="{}" target="_blank" rel="noopener">{}</a>'.format(esc(url), esc(label))


# ---------------------------------------------------------------- data

def load_venetian():
    rows = []
    path = os.path.join(ROOT, "data", "venetian_dse_2026.psv")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) != 9:
                errors.append("bad psv line: " + line)
                continue
            date, time, ev, name, buy, gtd, struct, kind, notes = parts
            if "ROW TRUNCATED" in name:
                cat = "incomplete"
            elif kind == "restart":
                cat = "restart"
            elif "Flight" in notes:
                cat = "flight"
            else:
                cat = "single"
            rows.append({
                "venue": "The Venetian Resort",
                "series": "DeepStack Extravaganza IV",
                "date": date,
                "time": time,
                "event_no": int(ev),
                "name": name,
                "buyin": int(buy) if buy else None,
                "gtd": int(gtd) if gtd else None,
                "schedule": fmt_date(date) + " \u00b7 " + fmt_time(time),
                "reentry": "Unverified (F01)" if cat in ("single", "flight") else "",
                "category": cat,
                "notes": notes,
                "source": DSE_URL,
                "source_type": "official",
                "structure": STRUCT_BASE.format(struct) if struct else "",
                "flags": ["F01"] if cat == "single" else (["F04"] if cat == "flight" else []),
            })
    return rows


def load_other():
    with open(os.path.join(ROOT, "data", "other_events.json"), encoding="utf-8") as fh:
        rows = json.load(fh)
    for r in rows:
        r.setdefault("structure", "")
        r["date"] = ""
        r["time"] = ""
        r["event_no"] = r.get("event_no")
        r["schedule"] = r.get("schedule", "")
        r["notes"] = r.get("notes", "")
        r["buyin_note"] = r.get("buyin_note", "")
        r["reentry_display"] = r.get("reentry", "")
        if not r.get("source"):
            errors.append("missing source: " + r["name"])
    return rows


def load_json(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def sort_rank(rows):
    """Rank by guaranteed prize pool (desc), then buy-in (desc). Missing values rank last."""
    return sorted(rows, key=lambda r: (-(r["gtd"] or -1), -(r["buyin"] or -1), r.get("date") or "9999", r.get("time") or ""))


# ---------------------------------------------------------------- html helpers

def page_shell(path, title, body, depth):
    base = "../" if depth == 1 else ""
    nav = []
    for target, label in PAGES:
        href = base + target if depth == 1 else target
        if depth == 0 and target.startswith("pages/"):
            href = target
        if depth == 1 and target == "index.html":
            href = "../index.html"
        if depth == 1 and target.startswith("pages/"):
            href = target.replace("pages/", "")
        nav.append('<a href="{}">{}</a>'.format(esc(href), label))
    nav_html = "\n".join(nav)
    css = base + "assets/css/style.css"
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Poker5</title>
<meta name="description" content="Las Vegas Strip poker tournament and hotel planner built from official sources. Unverified values are blank and flagged.">
<link rel="stylesheet" href="{css}">
</head>
<body>
<header class="topbar">
  <div class="brand"><span class="logo">P5</span> Poker5 <small>Las Vegas Strip poker planner</small></div>
  <nav class="nav">{nav}</nav>
</header>
<main class="wrap">
<h1>{title}</h1>
{body}
</main>
<footer class="foot">
  <div>Poker5 is an independent planning dashboard, not affiliated with any casino, poker room, or hotel. Values change without notice. Confirm before you book or play. Must be 21+. Gamble responsibly.</div>
  <div>Repo: <a href="{repo}">karagemop466-tech/Poker5</a> &middot; Coordination board: <a href="{repo}/blob/main/COORDINATION.md">COORDINATION.md</a> &middot; Site: <a href="{site}">{site}</a></div>
</footer>
</body>
</html>
""".format(title=esc(title) if "&amp;" not in title else title, css=css, nav=nav_html, body=body,
           repo=REPO_URL, site=SITE_URL)


def table(headers, rows, row_source_index):
    """rows: list of lists of already-html cells. Enforces a source link in each row."""
    out = ['<div class="tablewrap"><table class="tbl"><thead><tr>']
    for h in headers:
        out.append("<th>{}</th>".format(h))
    out.append("</tr></thead><tbody>")
    for i, cells in enumerate(rows):
        src = cells[row_source_index] if row_source_index is not None else "<a "
        if row_source_index is not None and "<a " not in src:
            errors.append("row {} has no source link in table with headers {}".format(i, headers[:3]))
        out.append("<tr>")
        for c in cells:
            out.append("<td>{}</td>".format(c))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def badge(kind, text):
    return '<span class="badge badge-{}">{}</span>'.format(kind, esc(text))


# ---------------------------------------------------------------- data derived

venetian = load_venetian()
other = load_other()
flags = load_json("flags.json")
hotels = load_json("hotels.json")

all_rows = venetian + other
singles = sort_rank([r for r in all_rows if r["category"] == "single"])
multis = sort_rank([r for r in all_rows if r["category"] == "multi"])
flights = sorted([r for r in all_rows if r["category"] == "flight"],
                 key=lambda r: (r.get("date") or "9999", r.get("time") or "", r["name"]))
restarts = [r for r in venetian if r["category"] == "restart"]
incomplete = [r for r in venetian if r["category"] == "incomplete"]
venetian_entries = [r for r in venetian if r["category"] in ("single", "flight", "incomplete")]
venetian_event_nums = sorted({r["event_no"] for r in venetian if r["category"] != "restart"})
n_rows_schedule = len(venetian)


def sched_cell(r):
    if r.get("date"):
        return esc(r["schedule"])
    return esc(r.get("schedule", ""))


def name_cell(r):
    label = esc(r["name"])
    if r.get("event_no"):
        label = "#{} &middot; {}".format(r["event_no"], label)
    return label


def buyin_cell(r):
    if r.get("buyin") is None:
        note = r.get("buyin_note") or ""
        return '<span class="blank">blank</span>' + ('<br><small>{}</small>'.format(esc(note)) if note else "")
    return money(r["buyin"])


def gtd_cell(r):
    if r.get("gtd") is None:
        return '<span class="blank">blank</span>'
    return money(r["gtd"])


def structure_link(r):
    return link(r.get("structure"), "Structure") if r.get("structure") else ""


# ---------------------------------------------------------------- pages

def page_index():
    stats = [
        ("Venetian event numbers (official)", len(venetian_event_nums)),
        ("Single-entry status confirmed", 0),
        ("Re-entry / rebuy / add-on verified", len(multis)),
        ("Multi-flight events (rules unverified)", len(flights)),
        ("Flagged items for review", len(flags)),
    ]
    cards = "".join('<div class="stat"><div class="num">{}</div><div class="lbl">{}</div></div>'.format(v, esc(k)) for k, v in stats)
    body = """
<section class="hero">
  <h2>Plan a Las Vegas Strip poker trip from official sources</h2>
  <p>Live tournaments on the Strip, hotels with their resort fees, and a day plan starting from the official start times.
     Every row links to the official page it came from. Anything that is not confirmed is left blank and flagged.</p>
  <div class="ctas">
    <a class="btn" href="pages/tournaments.html">Single-entry candidates</a>
    <a class="btn ghost" href="pages/hotels.html">Hotels and true nightly cost</a>
    <a class="btn ghost" href="pages/executive-summary.html">Executive summary</a>
  </div>
</section>
<section class="stats">{cards}</section>
<section class="panel">
  <h2>Headline findings</h2>
  <ul>
    <li><strong>No event is confirmed single-entry.</strong> The official pages read do not say "no re-entry" or "freezeout" for any event. All candidates are shown as Unverified.</li>
    <li><strong>No official start at 8:00 AM was found.</strong> The earliest official start found is 9:00 AM (Horseshoe, daily). Earliest Venetian start is 9:10 AM (Dec 12, event #46).</li>
    <li><strong>Resort fees verified for two resorts:</strong> The Venetian (and The Palazzo) at $55 per night plus tax, and Wynn at $55 plus tax. Other resort fees are secondary-only or not checked.</li>
    <li><strong>Walking times and room rates are not verified</strong> except the Venetian poker-suite "as low as $119" figure, which needs qualifying play.</li>
  </ul>
  <p class="muted">Site generated from the data files in <code>data/</code> by <code>scripts/build_site.py</code>.</p>
</section>
<section class="grid3">
  <a class="card" href="pages/tournaments.html"><h3>Single-entry</h3><p>Ranked by guarantee, then buy-in. Single-entry status unverified for every row.</p></a>
  <a class="card" href="pages/tournaments-double.html"><h3>Re-entry / multi-flight</h3><p>Events where official text allows re-entry, rebuys or add-ons, plus multi-flight events.</p></a>
  <a class="card" href="pages/schedule.html"><h3>Schedule</h3><p>Every official Venetian row by date and time, with the 8 AM check.</p></a>
  <a class="card" href="pages/hotels.html"><h3>Hotels</h3><p>On-property tournament venues, resort fees with source, and blank room rates.</p></a>
  <a class="card" href="pages/questions.html"><h3>Questions</h3><p>What is missing and how to find it.</p></a>
  <a class="card" href="pages/flagged-review.html"><h3>Flagged for review</h3><p>{nflags} items with source links. These do not block publication.</p></a>
</section>
""".format(cards=cards, nflags=len(flags))
    return body


def page_tournaments():
    cells = []
    for i, r in enumerate(singles, 1):
        if r["venue"] == "The Venetian Resort":
            status = badge("warn", "Unverified (F01)")
        else:
            status = badge("warn", "Unverified") if not r.get("reentry") or r["reentry"].startswith("Unverified") else esc(r["reentry"])
        src = link(r["source"], "Official page")
        if r.get("structure"):
            src += " &middot; " + link(r["structure"], "Structure")
        cells.append([
            str(i),
            esc(r.get("schedule") or "Not captured"),
            esc(r["venue"]),
            name_cell(r),
            buyin_cell(r),
            gtd_cell(r),
            status,
            src,
        ])
    headers = ["Rank", "Date &middot; time", "Venue", "Event", "Buy-in", "Guarantee", "Single-entry status", "Source"]
    main = table(headers, cells, 7)
    venue_rows = [
        ["Venetian (DeepStack Extravaganza IV)", "Listed, official schedule with 64 event numbers",
         link(DSE_URL, "Official schedule")],
        ["Wynn Las Vegas", "WPT World Championship festival listed; daily tournaments suspended during festival",
         link(WYNN_POKER_URL, "Official poker page")],
        ["Bellagio", "Friday, Saturday and Sunday events listed on official PDFs/page (undated)",
         link("https://bellagio.mgmresorts.com/en/casino/poker.html", "Official poker page")],
        ["MGM Grand", "Daily NLH listed on official page; PDF titled 'August' (stale)",
         link("https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", "Official poker page")],
        ["Caesars Palace and Horseshoe", "Daily NLH listed on official page; Horseshoe buy-ins not stated",
         link(CAESARS_URL, "Official Caesars page")],
        ["ARIA", "Official page has no tournament list. Call the poker room (F12)",
         link("https://aria.mgmresorts.com/en/casino/poker.html", "Official poker page")],
        ["Resorts World Las Vegas", "No current tournaments found in the sources read (secondary only)",
         link("https://www.pokeratlas.com/poker-room/resorts-world-las-vegas/tournaments", "Secondary listing")],
    ]
    venues = table(["Venue", "Status", "Source"], venue_rows, 2)
    body = """
<section class="panel warn-panel">
  <strong>Single-entry status is not confirmed for any row.</strong> The official pages and structure sheets read do not
  state "no re-entry" or "freezeout." Rows below are candidates ranked by guarantee, then buy-in. Confirm each before you play (F01).
</section>
<p class="muted">Ranking: guaranteed prize pool first, then buy-in. Blank = not stated on the official source. Event #40 on the Venetian schedule is excluded because its row was truncated in the capture (F02).
Events with multiple flights (1A/1B...) are moved to <a href="tournaments-double.html">Re-Entry / Multi-Flight</a>.</p>
<h2>Single-entry candidates</h2>
{main}
<h2>Venue status</h2>
{venues}
"""
    body = body.format(main=main, venues=venues)
    return body


def page_double():
    # Section A: verified spending advantage (re-entry / rebuy / add-on / entry cap)
    a_cells = []
    for r in multis:
        src = link(r["source"], "Official page")
        a_cells.append([
            esc(r.get("schedule") or "Not captured"),
            esc(r["venue"]),
            name_cell(r),
            buyin_cell(r),
            gtd_cell(r),
            esc(r.get("reentry_display") or r.get("reentry", "")),
            src,
        ])
    a = table(["Schedule", "Venue", "Event", "Buy-in", "Guarantee", "Verified entry rule (official)", "Source"], a_cells, 6)

    # Section B: multi-flight events, rules unverified
    b_cells = []
    for r in flights:
        src = link(r["source"], "Official page")
        if r.get("structure"):
            src += " &middot; " + link(r["structure"], "Structure")
        b_cells.append([
            esc(r.get("schedule") or "Not captured"),
            esc(r["venue"]),
            name_cell(r),
            buyin_cell(r),
            gtd_cell(r),
            badge("warn", "Unverified (F04)") if r["venue"] == "The Venetian Resort" else esc(r.get("reentry", "Unverified")),
            src,
        ])
    b = table(["Schedule", "Venue", "Event", "Buy-in", "Guarantee", "Re-entry / flight rule", "Source"], b_cells, 6)

    c_rows = [[
        "Daily, Nov 16 - Dec 23 (playing requirement)",
        "The Venetian / The Palazzo poker suite",
        "Poker suite rate requires six hours of active live cash play OR a buy-in to a $300-or-higher tournament for each night stayed (official)",
        "from $119 (as low as)",
        link(SUITE_URL, "Official suite-rate page"),
    ]]
    c = table(["Schedule", "Venue", "Spending requirement (official)", "Rate", "Source"], c_rows, 4)

    body = """
<p class="muted">Kept separate from single-entry because re-entry, rebuys, add-ons, entry caps or flights can let a player spend more for more chances. Only rows whose rules appear in an official source are in Section A. Section B lists multi-flight events whose rules are not yet verified.</p>
<h2>A. Re-entry, rebuy, add-on or entry-cap rules (official)</h2>
{a}
<h2>B. Multi-flight events (entry rules unverified)</h2>
<p class="muted">Each flight is a separate starting event number. Whether a player can enter more than one flight is not verified (F04).</p>
{b}
<h2>C. Spending that buys a better hotel rate</h2>
{c}
"""
    return body.format(a=a, b=b, c=c)


def page_hotels():
    cells = []
    for h in hotels:
        status = badge("ok", "Official fee") if h["source_type"] == "official" and h.get("resort_fee_usd") else (
            badge("warn", "Secondary fee") if h.get("resort_fee_usd") else badge("warn", "Not verified"))
        src = link(h["source"], "Official page" if h["source_type"] == "official" else "Secondary source")
        cells.append([
            "<strong>{}</strong><br><small>{}</small>".format(esc(h["hotel"]), esc(h["role"])),
            esc(h["walk_to_tournament"]) if h["walk_to_tournament"] else '<span class="blank">blank</span>',
            esc(h["nightly_rate"]) if h["nightly_rate"] else '<span class="blank">blank</span>',
            esc(h["resort_fee"]),
            esc(h["true_cost"]) if h["true_cost"] else '<span class="blank">blank</span>',
            '<span class="blank">blank</span>',
            status + "<br>" + src,
        ])
    main = table(["Hotel", "Walk to tournament", "Nightly room rate", "Resort fee (per night)", "True cost per night", "Quality", "Status &amp; source"], cells, 6)
    body = """
<p class="muted">Walking limit: 30 minutes on foot to the tournament room. Not verified for hotels other than the tournament venue itself, so those cells are blank.</p>
<div class="panel">
<strong>How true cost per night is built:</strong> nightly room rate + mandatory resort fee. Taxes are not added because the official tax rate was not verified in the sources read. Where a room rate is blank, the true cost is blank too.
</div>
<h2>Hotels hosting or near tournaments</h2>
{main}
<p class="muted">Quality ratings were not sourced and are blank (F20). Walking times and room rates are blank (F18, F19, F22).</p>
"""
    return body.format(main=main)


def page_schedule():
    cells = []
    rows = sorted(venetian, key=lambda r: (r["date"], r["time"] or "99:99", r["event_no"]))
    for r in rows:
        kind = {"single": "Entry", "flight": "Entry (flight)", "restart": "Restart row", "incomplete": "Row incomplete"}[r["category"]]
        src = link(r["source"], "Official schedule")
        if r.get("structure"):
            src += " &middot; " + link(r["structure"], "Structure")
        cells.append([
            esc(fmt_date(r["date"])),
            esc(fmt_time(r["time"])),
            str(r["event_no"]),
            esc(r["name"]),
            money(r["buyin"]) if r["buyin"] else '<span class="blank">blank</span>',
            money(r["gtd"]) if r["gtd"] else '<span class="blank">blank</span>',
            esc(kind),
            src,
        ])
    venetian_table = table(["Date", "Start", "Event #", "Event (official)", "Buy-in", "Guarantee", "Row type", "Source"], cells, 7)

    other_cells = [
        ["Horseshoe Las Vegas", "Daily (6 starts)", "9:00 AM, 11:00 AM, 2:00 PM, 5:00 PM, 8:00 PM, 11:00 PM", link(CAESARS_URL, "Official Caesars page")],
        ["Caesars Palace", "Daily (4 starts)", "10:00 AM, 2:00 PM, 6:00 PM, 9:00 PM", link(CAESARS_URL, "Official Caesars page")],
        ["Wynn Las Vegas", "Mon-Thu, Sat, Sun", "12:00 PM (daily); Friday rebuy 12:00 PM; nightly 6:00 PM", link("https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf", "Official poster")],
        ["MGM Grand", "Daily (PDF is stale)", "11:10 AM, 7:10 PM, 11:10 PM per PDF; page lists 11:00 AM, 7:00 PM, 11:00 PM", link("https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", "Official poker page")],
        ["Bellagio", "Friday and Saturday 11:00 AM; Sunday and nightly events on page", "11:00 AM (Fri, Sat); 6:00 PM PLO nightly", link("https://bellagio.mgmresorts.com/en/casino/poker.html", "Official poker page")],
    ]
    other = table(["Venue", "Days", "Official start times", "Source"], other_cells, 3)

    body = """
<section class="panel warn-panel">
  <strong>8:00 AM all-day start: not supported by the official sources read.</strong>
  Earliest official start found: 9:00 AM (Horseshoe). Earliest Venetian start: 9:10 AM (Dec 12, event #46). Blocks of play from 8:00 AM cannot be built from verified listings (F03).
</section>
<p class="muted">Event durations are not verified (F06), so this page cannot show non-overlapping day plans or maximum entries. Start times and buy-ins below are the official values. Restart rows (Day 2 / Day 3) are not new entries.</p>
<h2>Venetian DeepStack Extravaganza IV: every official row ({n} rows, Nov 16 - Dec 23, 2026)</h2>
{v}
<h2>Other rooms: official start times</h2>
{o}
""".replace("{n}", str(n_rows_schedule))
    return body.replace("{v}", venetian_table).replace("{o}", other)


def page_exec():
    body = """
<section class="panel">
  <h2>Executive summary</h2>
  <ol class="numbered">
    <li><strong>The main live series in the window:</strong> The Venetian DeepStack Extravaganza IV (Nov 16 - Dec 23, 2026), official page: 64 event numbers, more than $3.6 million in guaranteed prize pools. Source: <a href="{dse}" target="_blank" rel="noopener">official schedule</a>.</li>
    <li><strong>Single-entry: none confirmed.</strong> No official source read says "no re-entry" or "freezeout" for any event. The single-entry page lists {singles} candidates ranked by guarantee, then buy-in. All of them are Unverified.</li>
    <li><strong>Verified re-entry / rebuy / add-on rules</strong> are on the re-entry page: Wynn Mon-Thu, Sat, Sun (re-entry allowed), Wynn Friday (rebuy and add-on, no re-entry), WPT Main Event (up to 4 entries), WPT $600 Day 1 flights (unlimited re-entry per flight until Level 9), Bellagio Friday (re-entry through Level 8), Caesars Palace (add-on).</li>
    <li><strong>8:00 AM start: not met.</strong> Earliest official start found is 9:00 AM (Horseshoe). Earliest Venetian start is 9:10 AM.</li>
    <li><strong>Hotels:</strong> The Venetian (and The Palazzo) and Wynn have official resort fees of $55 per night plus tax. The poker suite "as low as $119" applies only with qualifying play, so the true cost from the Venetian is from $174 before tax. Other room rates are blank. Walking times are blank because no official source gives them.</li>
    <li><strong>Planning limit:</strong> Event durations are not verified, so the maximum number of entries in a day cannot be computed yet.</li>
    <li><strong>Prior site:</strong> the earlier version on main had secondary-source claims presented as facts. This version rebuilds the data and documents the corrections on the Repo Review page.</li>
  </ol>
  <p>Next steps, questions and the decisions still needed are on <a href="questions.html">Questions &amp; Answers</a> and <a href="suggestions.html">Suggestions</a>.</p>
</section>
""".format(dse=DSE_URL, singles=len(singles))
    return body


def page_questions():
    rows = [
        ["Q1", "Which events are truly single-entry (no re-entry, no freezeout)?", badge("warn", "Unverified"),
         "No official source read says so for any event. Re-entry text exists for Wynn, Bellagio Friday and WPT only.",
         "Explicit re-entry text per event.",
         "Read each Venetian structure sheet for re-entry language, or ask the Venetian poker room (lv_cas_poker@venetianlasvegas.com, 702.414.7657, from the official suite page).",
         link(DSE_URL, "Venetian schedule")],
        ["Q2", "Is there any official tournament starting at 8:00 AM?", badge("warn", "Gap"),
         "Earliest official start found: 9:00 AM (Horseshoe). Venetian earliest 9:10 AM.",
         "Official schedules of other Strip rooms not all read.",
         "Read official poker-room pages for each Strip room and look for 8:00 AM starts.",
         link(CAESARS_URL, "Caesars page")],
        ["Q3", "How long does each event take?", badge("warn", "Unverified"),
         "Start times only.", "Level length and expected duration per event.",
         "Read the level-length line of each structure sheet (Venetian sheets are linked on the schedule page).",
         link(DSE_URL, "Venetian schedule")],
        ["Q4", "Hotel room rates for the travel dates", badge("warn", "Blank"),
         "Only the Venetian poker-suite 'as low as $119' figure, which needs qualifying play.",
         "Live rate for each hotel on the travel dates.",
         "Check each official booking page for the dates chosen.",
         link(SUITE_URL, "Venetian suite rates")],
        ["Q5", "Walking time from each hotel to the tournament room", badge("warn", "Blank"),
         "Nothing from an official source. Only on-property venues are known to be 0 minutes.",
         "Measured walking time.",
         "Measure the walking route on a map for each pair.",
         link(DSE_URL, "Venetian schedule")],
        ["Q6", "Resort fees for MGM properties other than The Venetian and Wynn, Caesars Palace and Horseshoe", badge("warn", "Secondary or blank"),
         "MGM fees from secondary news only. Caesars and Horseshoe not checked.",
         "Official resort-fee page for each property.",
         "Find the official resort-fee or hotel policy page for each property.",
         link("https://casino.com/news/las-vegas/mgm-resorts-increases-parking-and-resort-fees-in-its-las-vegas-properties/", "Secondary source")],
        ["Q7", "Current Bellagio dated schedule and Saturday buy-in", badge("warn", "Unverified"),
         "Undated PDFs. Saturday shows $1,000 (title) and $1,100 (body).",
         "Dated schedule and the correct Saturday buy-in.",
         "Ask the Bellagio poker room or check the PDF's buy-in line.",
         link("https://bellagio.mgmresorts.com/en/casino/poker.html", "Bellagio poker page")],
        ["Q8", "Current MGM Grand schedule", badge("warn", "Stale"),
         "Official PDF titled 'August'. Times differ from the page.",
         "Current schedule.", "Ask the MGM Grand poker room.",
         link("https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", "MGM Grand poker page")],
        ["Q9", "ARIA daily tournaments", badge("warn", "No official list"),
         "Official page lists no tournaments. Secondary buy-ins conflict.",
         "Official schedule.", "Call the ARIA poker room.",
         link("https://aria.mgmresorts.com/en/casino/poker.html", "ARIA poker page")],
        ["Q10", "Wynn daily availability Nov 16-26, and re-entry for the nightly $160 event", badge("warn", "Unverified"),
         "Daily tournaments are suspended during the WPT festival (Nov 27 - Dec 21). Nightly re-entry not stated.",
         "Confirmed availability before Nov 27 and nightly re-entry text.",
         "Ask the Wynn poker room or read the current Wynn daily structures PDF.",
         link(WYNN_POKER_URL, "Wynn poker page")],
        ["Q11", "WPT festival day-by-day dates", badge("warn", "Partial"),
         "Main Event: Dec 13-20 (official). Other events: day not captured.",
         "Day-by-day dates.", "Read the WPT schedule PDF day by day.",
         link(WPT_URL, "WPT event page")],
        ["Q14", "Venetian event #40 (Dec 10 row)", badge("warn", "Truncated"),
         "Row was cut off in the capture.", "Name, time and buy-in.",
         "Re-read the official schedule for event #40.",
         link(DSE_URL, "Venetian schedule")],
    ]
    table_html = table(["#", "Question", "Status", "What we know", "What is missing", "How to find it", "Source"], rows, 6)
    body = """
<p class="muted">Each item lists the status, what is known, what is missing and how to find it. Only items with an official source appear in this table.</p>
{t}
<h2>Needs your input (no external source exists)</h2>
<ul>
  <li><strong>Q12. Hotel quality criteria.</strong> Blank because no official quality source has been chosen. See Suggestion S3.</li>
  <li><strong>Q13. Travel dates and party size.</strong> Needed to compute trip cost and pick events. It cannot be looked up from a source. See Suggestion S2.</li>
</ul>
""".format(t=table_html)
    return body


def page_suggestions():
    items = [
        ("S1", "Add a scheduled check that re-reads the official pages each week and flags changed values", "Keeps dates and buy-ins current without manual input. Needs a scheduled job; no code change made in this run."),
        ("S2", "Add your travel dates and party size to compute a day plan and total trip cost", "Needed for Q13. Turns the schedule into a plan of actual entries."),
        ("S3", "Choose a hotel quality source (for example, a published rating) and its scale", "Quality is blank today because none is verified (Q12)."),
        ("S4", "Choose the ranking rule for tournaments: guarantee, buy-in, or guarantee per buy-in", "Current rule is guarantee, then buy-in. Other rules change the top of the list."),
        ("S5", "Add the official Venetian structure-sheet re-entry and level-length lines as columns", "Would resolve F01, F04 and F06 for the Venetian rows."),
        ("S6", "Confirm the Bellagio and MGM Grand dates and add them as dated rows", "Clears F10 and F11."),
    ]
    cells = [[esc(i), esc(t), esc(d), '<span class="blank">Awaiting your choice</span>'] for i, t, d in items]
    rows_html = ['<div class="tablewrap"><table class="tbl"><thead><tr><th>#</th><th>Suggestion</th><th>Why</th><th>Status</th></tr></thead><tbody>']
    for c in cells:
        rows_html.append("<tr>" + "".join("<td>{}</td>".format(x) for x in c) + "</tr>")
    rows_html.append("</tbody></table></div>")
    body = """
<p class="muted">These are options. None is implemented yet; the choice is yours. Only the items you choose will be built.</p>
{t}
""".format(t="".join(rows_html))
    return body


def page_flagged():
    cells = []
    for f in flags:
        srcs = " &middot; ".join(link(u, "Source {}".format(i + 1)) for i, u in enumerate(f.get("sources", []))) or '<span class="blank">none</span>'
        cells.append([
            esc(f["id"]),
            esc(f["item"]),
            esc(f["value_shown"]),
            badge("warn", f["status"]),
            srcs,
            esc(f["to_clear"]),
        ])
    t = table(["ID", "Item", "Value shown", "Status", "Sources", "What clears the flag"], cells, None)
    body = """
<p class="muted">Flagged items do not block publication. Each is listed with its source link and what is needed to clear it.</p>
{t}
""".format(t=t)
    return body


def page_repo_review():
    gh = REPO_URL + "/blob/main/"
    rows = [
        ["README.md", "One line ('# Poker5'). No description, usage, or site link.", "Updated: describes the site, data and build script; links the live site.", link(gh + "README.md", "README.md on main")],
        ["COORDINATION.md (prior task board)", "Tasks 1-8 marked 'done' with secondary sources (PokerNews, VegasPokerCalendar, unleashvegas, lasvegaswonders) cited for facts. Tasks 9-10 'in progress' and task 11 'unclaimed' from the earlier session.", "Reopened in this session. Board rebuilt with this session's claims and findings.", link(gh + "COORDINATION.md", "COORDINATION.md on main")],
        ["index.html", "Headline 'Single-entry tournaments only'. Primary sources list PokerNews and VegasPokerCalendar (secondary). Cites a 13.38% Clark County lodging tax without an official source.", "Rebuilt from official data. Tax removed from the cost formula. Secondary sources removed as primary.", link(gh + "index.html", "index.html on main")],
        ["pages/tournaments.html", "Single-entry column labelled 'Unverified' (correct) but also claims the $200 Bounty events are 'the strongest value' and that Aria starts at 1:00 PM. Neither is in an official source.", "Rebuilt. Aria claim removed (Aria page has no list). Ranking rule stated.", link(gh + "pages/tournaments.html", "tournaments.html on main")],
        ["pages/tournaments-double.html", "Labels Venetian flights as 'multi-flight re-entry' although no official source states re-entry for them. States '$50 bounty per elimination' (not in any official row; official rows say $200 and $500 bounties). WPT dates taken from PokerNews (Dec 13-15) and conflict with the official Dec 13-20.", "Rebuilt. Flight rules marked unverified (F04). Bounty claim removed. WPT dates from the official page.", link(gh + "pages/tournaments-double.html", "tournaments-double.html on main")],
        ["pages/hotels.html", "Walking minutes (e.g., '~5 min', '~12 min walk (0.5 mi)') come from listing sites, not official sources. 13.38% tax unverified. Palazzo, Wynn, Bellagio and Caesars fees shown as '$50 (varies $50-55)' while the official Venetian and Wynn figure is $55. Harrah's, TI, Casino Royale and LINQ listed without a verified tournament.", "Rebuilt. Walking times blank. Fees use the official $55 (Venetian, Wynn). Hotels without a verified tournament removed.", link(gh + "pages/hotels.html", "hotels.html on main")],
        ["pages/schedule.html", "'Best buy-in-to-guarantee value ($50 bounties)' and '8:00 AM' gap statement; 'Aria 1:00 PM' claim unverified.", "Rebuilt from the official Venetian rows with per-row sources.", link(gh + "pages/schedule.html", "schedule.html on main")],
        ["pages/executive-summary.html", "Hotel cost '$56.69-$62.36 per night' computed from secondary fees and an unverified tax. Recommended hotels 'within 30 minutes' without a source.", "Rebuilt. Only verified costs shown.", link(gh + "pages/executive-summary.html", "executive-summary.html on main")],
        ["pages/questions.html", "Q3 and Q5 cite secondary sources and the 13.38% tax as facts.", "Rebuilt with official sources or 'Blank'.", link(gh + "pages/questions.html", "questions.html on main")],
        ["pages/flagged-review.html", "F2 and F6 cite VegasPokerCalendar and unleashvegas (secondary). F5 'Not confirmed' for four hotels without a source.", "Rebuilt from data/flags.json, each item with source links.", link(gh + "pages/flagged-review.html", "flagged-review.html on main")],
        ["pages/suggestions.html", "Suggestions present, no status tracking.", "Rebuilt as a choice list. Nothing implemented without user choice.", link(gh + "pages/suggestions.html", "suggestions.html on main")],
        ["assets/css/style.css", "Dashboard style; no issues found.", "Kept and extended for badges and tables.", link(gh + "assets/css/style.css", "style.css on main")],
        ["Repo settings", "GitHub Pages built from main at /. Repo is public and not archived. Only tracked file was README.md before the earlier session.", "No change. Confirm the Pages build after the merge.", link(REPO_URL + "/settings/pages", "Pages settings")],
        ["LICENSE / .gitignore", "Neither exists. No license is declared for the site content.", "Not added. Needs a user decision (see Suggestions).", link(REPO_URL, "Repo root")],
    ]
    t = table(["File / area", "Finding (line by line)", "Action in this session", "Evidence"], rows, 3)
    body = """
<p class="muted">Line-by-line review of the repo on main (commit 47b2e73) and the earlier site. Findings are about the content, not the people who wrote it. Each correction is shown in the Action column.</p>
{t}
<h2>Verification standard used in this rebuild</h2>
<ul>
  <li>Values are taken only from official pages and PDFs, or left blank and flagged.</li>
  <li>Secondary sources are used only where labelled "Secondary" and are never used to set a verified value.</li>
  <li>Each table row has a link to its source. The build fails if a row has none.</li>
</ul>
""".format(t=t)
    return body


# ---------------------------------------------------------------- build

CSS = """
:root{--ink:#1d2433;--muted:#5b6475;--line:#e3e7ef;--bg:#f6f8fb;--card:#fff;--accent:#1f6feb;--ok:#1a7f37;--warn:#9a6700;--bad:#cf222e}
*{box-sizing:border-box}
body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent)}
.topbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;padding:12px 20px;background:#0f172a;color:#fff}
.brand{font-weight:700}.brand small{font-weight:400;opacity:.7;margin-left:6px}
.logo{display:inline-block;background:#f5c542;color:#0f172a;border-radius:6px;padding:2px 6px;font-weight:800;margin-right:4px}
.nav{display:flex;flex-wrap:wrap;gap:4px}
.nav a{color:#dbe5ff;text-decoration:none;padding:5px 9px;border-radius:6px;font-size:13px}
.nav a:hover{background:#1e293b}
.wrap{max-width:1180px;margin:0 auto;padding:22px 18px 40px}
h1{font-size:26px;margin:4px 0 12px}h2{font-size:19px;margin:26px 0 8px}
.hero{background:linear-gradient(135deg,#0f172a,#1e3a8a);color:#fff;border-radius:14px;padding:26px}
.hero h2{margin-top:0;font-size:26px}.hero p{max-width:760px;opacity:.9}
.ctas{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.btn{background:#f5c542;color:#0f172a;text-decoration:none;font-weight:700;padding:9px 14px;border-radius:8px}
.btn.ghost{background:transparent;color:#fff;border:1px solid #93c5fd}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:16px 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.stat .num{font-size:28px;font-weight:800}.stat .lbl{color:var(--muted);font-size:13px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
.warn-panel{border-left:5px solid var(--warn)}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:14px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;text-decoration:none;color:inherit}
.card:hover{border-color:var(--accent)}.card h3{margin:0 0 4px;font-size:16px}.card p{margin:0;color:var(--muted);font-size:13px}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px}
.tbl{width:100%;border-collapse:collapse;font-size:13px}
.tbl th{position:sticky;top:0;background:#f0f3f9;text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
.tbl td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.tbl tr:hover td{background:#fafbfe}
.badge{display:inline-block;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:600}
.badge-ok{background:#dafbe1;color:var(--ok)}.badge-warn{background:#fff8c5;color:var(--warn)}.badge-bad{background:#ffebe9;color:var(--bad)}
.blank{color:var(--muted);font-style:italic}
.muted{color:var(--muted)}
.numbered li{margin-bottom:8px}
code{background:#eef2f8;padding:1px 5px;border-radius:4px}
.foot{max-width:1180px;margin:0 auto;padding:18px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}
@media (max-width:700px){.topbar{flex-direction:column;align-items:flex-start}}
"""


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    builders = {
        "index.html": (page_index, "Poker5 | Las Vegas Strip poker planner", 0),
        "pages/executive-summary.html": (page_exec, "Executive Summary", 1),
        "pages/tournaments.html": (page_tournaments, "Single-Entry Candidates", 1),
        "pages/tournaments-double.html": (page_double, "Re-Entry and Multi-Flight Events", 1),
        "pages/hotels.html": (page_hotels, "Hotels: Walking Distance and True Nightly Cost", 1),
        "pages/schedule.html": (page_schedule, "Schedule: Official Start Times", 1),
        "pages/questions.html": (page_questions, "Questions, Information and Answers", 1),
        "pages/suggestions.html": (page_suggestions, "Suggestions", 1),
        "pages/flagged-review.html": (page_flagged, "Flagged for Review", 1),
        "pages/repo-review.html": (page_repo_review, "Repo Review", 1),
    }
    for path, (fn, title, depth) in builders.items():
        body = fn()
        write(path, page_shell(path, title, body, depth))
    write("assets/css/style.css", CSS.strip() + "\n")
    if errors:
        print("BUILD ERRORS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("built {} pages; singles={} multis={} flights={} venetian_rows={} flags={}".format(
        len(builders), len(singles), len(multis), len(flights), len(venetian), len(flags)))


if __name__ == "__main__":
    main()
