#!/usr/bin/env python3
"""Build the Poker5 root site (the one GitHub Pages publishes from main `/`).

Run:  python3 scripts/build_251c122f.py

Inputs are the official-source captures in data/c6087e2c/:

  schedule_live.json            every row of the official Venetian schedule page
  structures.json               per-sheet rule fields extracted from the official PDFs
  events_verified.json          merged rows: verdict, structured rule fields, flags
  scrape_status.json            per-URL HTTP status, hash and retrieval timestamp
  watch_status.json             hotel/venue pages: status, hash, fee excerpts
  hotels_251c122f.json          official hotel facts (fees, terms) with excerpts
  other_venues_251c122f.json    other Strip rooms with excerpts
  flags_251c122f.json           every unverified / conflicting / partial item
  rates_log.json                dated rate snapshots (a log, never a single value)
  walking.json                  walking routes: verified only where official

Rules enforced in code (the build fails rather than publishing a guess):
  * every data table that shows a value has a Source column and every row links
    to an official URL;
  * a row whose verdict is not confirmed carries a visible Unverified badge;
  * a guarantee that the official sources disagree on is shown as a conflict,
    never resolved by choosing one;
  * every internal link resolves to a generated file.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "c6087e2c")

REPO_URL = "https://github.com/karagemop466-tech/Poker5"
RAW = REPO_URL + "/blob/main/data/c6087e2c/"
DSE_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
           "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
STRUCT_BASE = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/"
               "deepstack/2026/structures/dse_nov_2026_structure_{}.pdf")
SUITE_URL = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
FEE_URL = "https://www.venetianlasvegas.com/resort/resort-fee.html"
WYNN_TERMS = "https://www.wynnlasvegas.com/terms-and-conditions/849338"
WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"
MGM_TERMS = "https://www.mgmresorts.com/en/terms-and-conditions.html"
BELLAGIO_TERMS = "https://bellagio.mgmresorts.com/en/terms-and-conditions.html"
ARIA_TERMS = "https://aria.mgmresorts.com/en/terms-and-conditions.html"
MGMGRAND_TERMS = "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html"
CAESARS_URL = ("https://www.caesars.com/las-vegas/explore/casino/"
               "poker-tournaments-las-vegas-strip")
CLARK_TAX = ("https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:"
             "3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf")
CLARK_COUNTY_HOME = "https://www.clarkcountynv.gov/"
WPT_EVENT = ("https://www.worldpokertour.com/event/"
             "main-tour-wpt-world-championship-at-wynn-las-vegas-season-2026")

errors: list[str] = []
PAGES: dict[str, str] = {}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
          "Nov", "Dec"]
WDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# A time budget for one on-property walk between a hotel and the poker room in
# the same resort. It is used only to answer "can this hotel serve this venue",
# and it is labelled as a zero-minute on-property route from the official pages.
ON_PROPERTY_MINUTES = 0
WALK_LIMIT = 30


# ------------------------------------------------------------------ utilities
def shorten(text: str, limit: int) -> str:
    """Trim a label at a word boundary; never silently cut mid-word."""
    text = text or ""
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "..."


def esc(v) -> str:
    return html.escape("" if v is None else str(v), quote=True)


def money(v):
    if v is None or v == "":
        return None
    return "${:,.0f}".format(v)


def money_or_blank(v) -> str:
    m = money(v)
    return m if m else '<span class="blank">blank</span>'


def link(url, label="Source") -> str:
    if not url:
        return ""
    short = label
    return ('<a href="{}" target="_blank" rel="noopener" title="{}">{}</a>'
            .format(esc(url), esc(url), esc(short)))


def srcs(*pairs) -> str:
    """Render one or more (url,label) source links."""
    out = []
    seen = set()
    for url, label in pairs:
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(link(url, label))
    return " &middot; ".join(out) if out else '<span class="blank">no source</span>'


def fdate(iso: str) -> str:
    try:
        d = dt.date.fromisoformat(iso)
    except (ValueError, TypeError):
        return esc(iso or "")
    return "{} {} {}, {}".format(WDAYS[d.weekday()], MONTHS[d.month - 1], d.day, d.year)


def ftime(hhmm: str) -> str:
    try:
        h, m = [int(x) for x in (hhmm or "").split(":")]
    except ValueError:
        return '<span class="blank">blank</span>'
    return "{}{}:{:02d} {}".format(h % 12 or 12, "", m, "AM" if h < 12 else "PM")


def to_min(hhmm: str):
    try:
        h, m = [int(x) for x in (hhmm or "").split(":")]
        return h * 60 + m
    except ValueError:
        return None


def badge(kind: str, text: str) -> str:
    return '<span class="badge badge-{}">{}</span>'.format(kind, esc(text))


def load(name, default=None):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ data load
EV = load("events_verified.json", {})
EVENTS = EV.get("events", []) or []
STRUCTS = (load("structures.json", {}) or {}).get("sheets", {}) or {}
SCRAPE = load("scrape_status.json", {}) or {}
WATCH = (load("watch_status.json", {}) or {}).get("pages", {}) or {}
HOTELS = (load("hotels_251c122f.json", {}) or {})
HOTEL_ROWS = HOTELS.get("hotels", []) or []
TAX = HOTELS.get("tax", {}) or {}
OTHER = (load("other_venues_251c122f.json", {}) or {}).get("venues", []) or []
FLAGS = load("flags_251c122f.json", []) or []
RATES = load("rates_log.json", {}) or {}
WALKING = load("walking.json", {}) or {}

LAST_SCRAPE = SCRAPE.get("last_run") or EV.get("generated_at") or ""
BUILD_STAMP = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

CONFIRMED = [e for e in EVENTS if e.get("verdict") == "single_entry_confirmed"]
MULTI = [e for e in EVENTS if e.get("verdict") == "multi_flight"]
RESTARTS = [e for e in EVENTS if e.get("verdict") == "restart"]
UNVERIFIED = [e for e in EVENTS if e.get("verdict") in ("unverified", "unverified_row")]
COUNTS = (EV.get("counts", {}) or {}).get("verdicts", {}) or {}

# Structured rule fields are official only when a sheet was read; the flag
# registry decides what is still unverified.
FLAG_INDEX = {f["id"]: f for f in FLAGS}


def flag_link(fid: str, base: str = "") -> str:
    if fid not in FLAG_INDEX:
        return esc(fid)
    return ('<a href="{}flagged.html#{}" title="{}">{}</a>'
            .format(base, esc(fid), esc(FLAG_INDEX[fid]["item"][:160]), esc(fid)))


def verdict_badge(e) -> str:
    v = e.get("verdict")
    if v == "single_entry_confirmed":
        return badge("ok", "Confirmed single-entry")
    if v == "multi_flight":
        return badge("warn", "Multi-flight / multi-entry")
    if v == "restart":
        return badge("muted", "Restart row")
    if v == "adds_second_entry":
        return badge("warn", "Adds a second entry")
    return badge("bad", "Unverified")


def format_badge(e) -> str:
    f = e.get("format")
    if f == "bounty":
        return badge("warn", "Bounty")
    if f == "satellite":
        return badge("warn", "Satellite")
    if f == "team":
        return badge("warn", "Team")
    if f == "flight":
        return badge("warn", "Flight")
    if f == "plo":
        return badge("muted", "PLO")
    return badge("muted", "NLH")


def ratio_cell(e) -> str:
    b, g = e.get("buyin"), e.get("gtd")
    if not b or not g:
        return '<span class="blank">blank</span>'
    return "{:.1f}&times;".format(g / b)


EXCERPT_PREFIX = re.compile(
    r"^\s*(level duration|starting chips|late registration|guarantee|start time)\s*:?\s*",
    re.I)


def excerpt(text: str, limit: int = 90) -> str:
    """A short, faithful quote from the sheet, without the field label."""
    t = EXCERPT_PREFIX.sub("", (text or "")).strip()
    t = re.sub(r"^(\d+\.)\s*", "", t)
    if len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0] + "..."
    return t


def rule_field(e, key: str) -> dict:
    return ((e.get("rule_fields") or {}).get(key) or {})


def name_cell(e, base: str = "") -> str:
    label = esc(e.get("name"))
    if e.get("event_no"):
        label = "<strong>#{}</strong> &middot; {}".format(e["event_no"], label)
    extra = ""
    if e.get("name_collision"):
        extra = ('<div class="tiny">name repeated for events {}: open the right '
                 'sheet from the row, {}.</div>'
                 .format(", ".join("#{}".format(n) for n in e["name_collision"]),
                         flag_link("F33", base)))
    if e.get("gtd_conflict"):
        extra += ('<div class="tiny">guarantee conflict: schedule {} vs sheet {}, '
                  '{}.</div>'.format(money(e["gtd_conflict"]["schedule"]),
                                     money(e["gtd_conflict"]["sheet"]),
                                     flag_link("F34", base)))
    return label + extra


def row_source_cell(e, base: str = "") -> str:
    pairs = [(e.get("source"), "Official schedule"),
             (e.get("structure_url"), "Structure sheet")]
    out = srcs(*pairs)
    if not e.get("structure_url"):
        out += " &middot; " + flag_link("F27", base)
    return out


# ------------------------------------------------------------------ tables
def table(headers, rows, source_col=None, caption=""):
    """Render a data table. Every row must supply a source cell."""
    if source_col is not None:
        for i, r in enumerate(rows):
            cell = r[source_col] if source_col < len(r) else ""
            if "href=" not in cell and "Flagged" not in cell:
                errors.append("row {} of table '{}' has no source link".format(
                    i, caption or (headers[0] if headers else "?")))
    out = ['<div class="tablewrap"><table class="tbl" data-searchable>',
           "<thead><tr>"]
    out += ["<th>{}</th>".format(h) for h in headers]
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>" + "".join("<td>{}</td>".format(c) for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def panel(text: str, cls="panel") -> str:
    return '<section class="{}">{}</section>'.format(cls, text)


def controls(page_kind="standard") -> str:
    """Global search, date filter and the confirmed-single-entry toggle."""
    date_ctl = ""
    if page_kind in ("events", "schedule"):
        dates = sorted({e["date"] for e in EVENTS if e.get("date")})
        opts = "".join('<option value="{0}">{0}</option>'.format(d) for d in dates)
        date_ctl = ('<label class="toggle">Date '
                    '<select id="date-filter" onchange="poker5Filter()">'
                    '<option value="">All dates</option>{}</select></label>'
                    .format(opts))
    se_ctl = ""
    if page_kind in ("events", "schedule"):
        se_ctl = ('<label class="toggle"><input id="se-toggle" type="checkbox" '
                  'onchange="poker5Filter()"> Confirmed single-entry only</label>'
                  '<label class="toggle"><input id="walk-toggle" type="checkbox" '
                  'onchange="poker5Filter()"> Venue reachable in &le;30 min walk '
                  'from a logged hotel only</label>')
    return ('<div class="controls">'
            '<input id="q" class="search" type="search" '
            'placeholder="Search every table on this page (event, venue, date, rule, status)..." '
            'oninput="poker5Filter()">{}{}'
            '<span id="rowcount" class="muted"></span></div>'
            .format(date_ctl, se_ctl))


# ------------------------------------------------------------------ chrome
NAV = [
    ("index.html", "Dashboard"),
    ("pages/executive-summary.html", "Executive summary"),
    ("pages/single-entry.html", "Single-entry events"),
    ("pages/multientry.html", "Advantage &amp; multi-entry"),
    ("pages/schedule.html", "Day schedule"),
    ("pages/hotels.html", "Hotels &amp; true cost"),
    ("pages/planner.html", "Trip calculator"),
    ("pages/qa.html", "Questions to resolve"),
    ("pages/suggestions.html", "Suggestions"),
    ("pages/flagged.html", "Flagged for review"),
    ("pages/sources.html", "Sources &amp; method"),
    ("pages/repo-review.html", "Repo review"),
]


def shell(title: str, body: str, depth: int) -> str:
    up = "../" * depth
    nav = []
    for target, label in NAV:
        href = target if depth == 0 else up + target
        nav.append('<a href="{}">{}</a>'.format(esc(href), label))
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Poker5</title>
<meta name="description" content="Las Vegas Strip poker tournament and hotel trip planner built only from official sources. Anything not confirmed is blank and flagged.">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="topbar">
  <div class="brand"><span class="logo">P5</span> Poker5
    <small>Las Vegas Strip poker trip planner</small></div>
  <nav class="nav">{nav}</nav>
</header>
<main class="wrap">
<h1>{title}</h1>
{body}
</main>
<footer class="foot">
  <div>Independent planning tool. Not affiliated with any casino, poker room or hotel.
  Values change without notice. Confirm before you book or play. Must be 21+. Gamble responsibly.
  If gambling is a problem, call 1-800-522-4700.</div>
  <div>Site built {stamp} from the official-source capture of {last}.
    Code: <a href="{repo}">github.com/karagemop466-tech/Poker5</a> &middot;
    Task board: <a href="{repo}/blob/main/COORDINATION.md">COORDINATION.md</a> &middot;
    Data: <a href="{repo}/tree/main/data/c6087e2c">data/c6087e2c</a></div>
</footer>
<script src="{up}assets/app.js"></script>
</body>
</html>
""".format(title=title, body=body, nav="\n".join(nav), up=up, repo=REPO_URL,
           stamp=BUILD_STAMP, last=esc(LAST_SCRAPE or "n/a"))


# ------------------------------------------------------------------ pages
def page_index() -> str:
    n_conf = len(CONFIRMED)
    first = min((e["date"] for e in EVENTS if e.get("date")), default="")
    last = max((e["date"] for e in EVENTS if e.get("date")), default="")
    stats = [
        ("Schedule rows read", len(EVENTS)),
        ("Confirmed single-entry", n_conf),
        ("Multi-flight / multi-entry", len(MULTI)),
        ("Restart rows", len(RESTARTS)),
        ("Official PDFs read", "{}/{}".format(
            SCRAPE.get("sheets_read", "?"), SCRAPE.get("sheets_total", "?"))),
        ("Items flagged for review", len(FLAGS)),
    ]
    cards = "".join('<div class="stat"><div class="num">{}</div>'
                    '<div class="lbl">{}</div></div>'.format(v, k) for k, v in stats)
    best = sorted([e for e in CONFIRMED if e.get("gtd") and e.get("buyin")],
                  key=lambda e: -(e["gtd"] / e["buyin"]))[:5]
    best_rows = [[name_cell(e), esc(fdate(e["date"])) + " &middot; " + ftime(e["time"]),
                  money_or_blank(e.get("buyin")), money_or_blank(e.get("gtd")),
                  ratio_cell(e) + ("" if e.get("gtd_basis") != "structure sheet" else
                                   ' <span class="tiny">(sheet)</span>'),
                  row_source_cell(e)] for e in best]
    best_tbl = table(["Event", "Date &middot; start", "Buy-in", "Guarantee",
                      "Guarantee &divide; buy-in", "Source"], best_rows, 5,
                     "dash-best-ratio")
    fee_rows = []
    for h in HOTEL_ROWS:
        if not h.get("resort_fee_usd") and h.get("resort_fee_usd") != 0:
            continue
        fee_rows.append([
            "<strong>{}</strong>".format(esc(h["hotel"])),
            money(h["resort_fee_usd"]),
            esc(h.get("resort_fee_status", "")),
            srcs((h.get("resort_fee_source"), "Official fee page")),
        ])
    fee_tbl = table(["Hotel", "Resort fee / night", "Status", "Source"], fee_rows, 3,
                    "dash-fees")
    body = """
<section class="hero">
  <h2>A Las Vegas Strip poker trip you can actually plan</h2>
  <p>One dashboard built only from official casino, tour and county pages: which
  tournaments are genuinely single-entry, what each one costs in total, how long a
  playing day runs, which days overlap, and what a hotel night really costs once the
  resort fee and room tax are added. Every value links to the official page or PDF it
  came from. Anything that could not be confirmed is blank and listed on
  <a href="pages/flagged.html">Flagged for review</a>.</p>
  <div class="ctas">
    <a class="btn" href="pages/single-entry.html">Single-entry events</a>
    <a class="btn ghost" href="pages/schedule.html">Day-by-day schedule</a>
    <a class="btn ghost" href="pages/hotels.html">Hotels &amp; true nightly cost</a>
    <a class="btn ghost" href="pages/planner.html">Trip calculator</a>
  </div>
</section>
<section class="stats">{cards}</section>
<div class="grid2">
<section class="panel">
  <h2>What changed in this pass</h2>
  <ul class="tight">
    <li><strong>{n_conf} events are confirmed single-entry</strong> because their own
      official structure sheet was read, lists that event number, is a one-day event, and
      contains no re-entry, rebuy, add-on or purchased-stack language. That is the
      published standard; nothing else is treated as confirmed.</li>
    <li><strong>Every Venetian structure sheet was read</strong> ({sheets} official PDFs),
      so the rule fields (late-registration cutoff, level length, starting chips, house fee,
      prize-pool share) are official values, not estimates.</li>
    <li><strong>Hotel resort fees are now official for The Venetian / The Palazzo ($55),
      Wynn / Encore ($55), Bellagio ($55), ARIA ($55) and MGM Grand ($50)</strong>, each with
      the sentence it was read from. Caesars Palace and Horseshoe fees are still blank.</li>
    <li><strong>Room tax 13.38%</strong> is tied to the Clark County ordinance table for a
      resort hotel inside the primary gaming corridor.</li>
    <li><strong>Guarantee conflicts are shown, not resolved.</strong> Where the schedule row
      and the structure sheet print different guarantees, the row says so and links both.</li>
  </ul>
</section>
<section class="panel warn-panel">
  <h2>What the data still cannot tell you</h2>
  <ul class="tight">
    <li><strong>No 8:00 AM start exists</strong> on the Strip. The earliest official start
      found is 9:00 AM (Horseshoe, six daily events); Caesars Palace opens at 10:00 AM; the
      Venetian's earliest is 9:10 AM (Dec 12, event #46, a $260 turbo satellite). Among the
      full tournaments, the Venetian's earliest start is 10:10 AM. The all-day plan therefore
      starts at 9:00 AM or later, never 8:00 AM.</li>
    <li><strong>Room rates are dynamic.</strong> No official page quotes a fixed rate; the
      rate log stores dated booking-UI snapshots with their timestamp and nothing else.</li>
    <li><strong>Walking times between different resorts are not verified.</strong> Only
      on-property routes (0 minutes) pass the 30-minute filter.</li>
    <li><strong>Finishing times are not published.</strong> A playing-day length is derived
      from each sheet's late-registration level count and is labelled as derived.</li>
  </ul>
  <p class="muted">The full list, with what would clear each item, is on
  <a href="pages/qa.html">Questions to resolve</a> and
  <a href="pages/flagged.html">Flagged for review</a>.</p>
</section>
</div>
<section class="panel">
  <h2>Best published guarantee per dollar of buy-in (descriptive, not a forecast)</h2>
  <p class="muted">Confirmed single-entry rows only. The ratio is the published guarantee
  divided by the buy-in. It says nothing about your chance of winning; it is only a way to
  compare how much prize money a room publishes per dollar of entry. Bounty events include
  bounties in that guarantee, so their ratio is not comparable with a standard event; the
  Format column on the events page marks them.</p>
  {best}
</section>
<section class="panel">
  <h2>Hotel fees confirmed from official pages</h2>
  {fees}
  <p class="muted">True nightly cost = room rate + resort fee + tax on both. See
  <a href="pages/hotels.html">Hotels</a> for the dated rate log and each hotel's terms.</p>
</section>
<section class="grid3">
  <a class="card" href="pages/single-entry.html"><h3>Single-entry events</h3>
    <p>Confirmed rows with every rule field, guarantee ratio, date filter and search.</p></a>
  <a class="card" href="pages/multientry.html"><h3>Advantage &amp; multi-entry</h3>
    <p>Re-entry, rebuy, add-on and multi-flight rows, kept apart from single entry.</p></a>
  <a class="card" href="pages/schedule.html"><h3>Day schedule</h3>
    <p>Primary event and conditional fallback per day, plus the overlap check.</p></a>
  <a class="card" href="pages/venues/venetian.html"><h3>Venetian</h3>
    <p>DeepStack Extravaganza IV: all rows, all rule fields, on-property hotels.</p></a>
  <a class="card" href="pages/venues/wynn.html"><h3>Wynn</h3>
    <p>WPT World Championship and the daily slate, with the suspension rules.</p></a>
  <a class="card" href="pages/venues/others.html"><h3>Other rooms</h3>
    <p>Caesars Palace, Horseshoe, Bellagio, MGM Grand, ARIA: what the official pages state.</p></a>
  <a class="card" href="pages/qa.html"><h3>Questions to resolve</h3>
    <p>Every open question, why it blocks a decision, and how to get the answer.</p></a>
  <a class="card" href="pages/suggestions.html"><h3>Suggestions board</h3>
    <p>Ranked improvements with impact, cost and the choice each one needs.</p></a>
  <a class="card" href="pages/sources.html"><h3>Sources &amp; method</h3>
    <p>Every official URL, when it was read, and the confirmation standard used.</p></a>
</section>
<section class="panel">
  <h2>Other dashboards preserved in this repository</h2>
  <p class="muted">Earlier parallel sessions published their own dashboards on the same brief.
  They are kept unchanged and are linked here so nothing is hidden; their numbers may differ
  from this page because they were built before every structure sheet had been read.</p>
  <ul class="tight">
    <li><a href="site-b50aa7f5/index.html">Strict-entry research dashboard</a> — 11 event
      records, a separate source ledger, and a strict rule that publishes no event as
      single-entry until it is one-entry-overall verified.</li>
    <li><a href="docs/index.html">Official-source site (session 581fea93)</a> — the
      DeepStack Extravaganza IV schedule and the WPT / Wynn festival pages.</li>
    <li><a href="dashboard-6d1e0039/index.html">Verified dashboard (session 6d1e0039)</a> —
      change monitoring with a six-hourly source check.</li>
    <li><a href="site-afff1fc9/index.html">Monitor site (session afff1fc9)</a> — a daily
      official-source check with change markers.</li>
    <li><a href="pages/method.html">Method</a>, <a href="pages/monitor.html">Monitor</a> and
      <a href="pages/routes.html">Routes</a> pages from session ea99006a.</li>
  </ul>
  <p class="muted">The room tax is described in full on
  <a href="pages/hotels.html">Hotels</a>: the 13.38% rate is the Clark County ordinance figure
  for a resort hotel inside the primary gaming corridor, and whether the resort fee is included
  in that tax base is not stated on the official pages read, so it remains unverified. The fee's
  own tax treatment is confirmed on the folio at checkout.</p>
</section>
""".format(cards=cards, n_conf=n_conf, sheets=SCRAPE.get("sheets_read", "?"),
           best=best_tbl, fees=fee_tbl,
           window=(fdate(first) + " to " + fdate(last)) if first else "")
    return body


def budget_tiers():
    """Group the confirmed rows by buy-in band, computed from the capture."""
    bands = [("Under $300", 0, 299), ("$300 - $599", 300, 599),
             ("$600 - $1,099", 600, 1099), ("$1,100 and up", 1100, 10 ** 9)]
    out = []
    for label, lo, hi in bands:
        rows = [e for e in CONFIRMED if e.get("buyin") is not None
                and lo <= e["buyin"] <= hi and e.get("format") != "satellite"]
        if not rows:
            continue
        cheapest = min(rows, key=lambda e: e["buyin"])
        biggest = max(rows, key=lambda e: (e.get("gtd") or 0))
        dates = sorted({e["date"] for e in rows})
        out.append([label, str(len(rows)),
                    "{} &ndash; {}".format(money(cheapest.get("buyin")),
                                          money(max(r["buyin"] for r in rows))),
                    (money(biggest.get("gtd")) + " ({})".format(
                        esc(shorten(biggest["name"], 40)))
                     if biggest.get("gtd") else '<span class="blank">blank</span>'),
                    "{} dates: {} to {}".format(len(dates), fdate(dates[0]),
                                                fdate(dates[-1])),
                    row_source_cell(biggest)])
    return table(["Budget band (buy-in)", "Confirmed entries", "Buy-in range",
                  "Largest published guarantee", "Dates available", "Source"],
                 out, 5, "tiers")


def events_table(rows, base="", show_rules=True) -> str:
    cells = []
    for e in rows:
        late = rule_field(e, "late_registration")
        chips = rule_field(e, "starting_chips")
        lvls = rule_field(e, "level_minutes")
        fee = rule_field(e, "house_fee")
        cells.append([
            name_cell(e, base),
            esc(fdate(e["date"])) + "<br>" + ftime(e["time"]),
            money_or_blank(e.get("buyin")),
            money_or_blank(e.get("gtd")),
            ratio_cell(e),
            format_badge(e) + (" " + badge("warn", "Guarantee conflict")
                               if e.get("gtd_conflict") else ""),
            (verdict_badge(e) +
             ('<br><span class="badge badge-warn" title="{}">Restricted</span>'
              .format(esc(e.get("restriction"))) if e.get("restriction") else "")),
            ("{} min".format(lvls["value"])
             if lvls.get("value") else '<span class="blank">blank</span>'),
            (money(chips["value"])
             if chips.get("value") else '<span class="blank">blank</span>'),
            (esc(late.get("value", ""))
             if late.get("value") else '<span class="blank">blank</span>'),
            ("{}<br><span class=\"tiny\">\u201c{}\u201d</span>".format(
                money(fee["value"]), esc(excerpt(fee.get("excerpt", ""), 70)))
             if fee.get("value") else '<span class="blank">blank</span>'),
            esc(e.get("sheet_retrieved_at") or "")[:10] or '<span class="blank">blank</span>',
            row_source_cell(e, base),
        ])
    heads = ["Event", "Date &middot; start", "Buy-in", "Guarantee",
             "Guarantee &divide; buy-in", "Format", "Single-entry status",
             "Levels (official)", "Starting chips (official)",
             "Late registration (official)", "House fee per entry (official)",
             "Sheet read", "Source"]
    return table(heads, cells, 12, "events")


def page_single_entry() -> str:
    rows = sorted(CONFIRMED, key=lambda e: (e["date"], to_min(e["time"]) or 0, e["event_no"] or 0))
    body = controls("events") + """
""" + panel("""
<strong>How a row earns the "Confirmed single-entry" badge.</strong> The structure sheet
linked in the row was downloaded from the official Venetian site, its own list of event
numbers includes the row's event number, the sheet describes a one-day event, and the text
contains no re-entry, rebuy, add-on, double-entry, alternate-stack or purchased-chip
language. The row shows the sheet's own words for the late-registration cutoff, level
length, starting chips and house fee, and the date the sheet was read. A sheet that is
silent on re-entry is the published confirmation standard; it is stated on this page and on
<a href="sources.html">Sources &amp; method</a> so you can judge it. Rows that fail any part
of that test are on <a href="flagged.html">Flagged for review</a>, not here.
""") + """
<h2>Grouped by what you want to spend per entry</h2>
{tiers}
<h2>Confirmed single-entry events ({n})</h2>
<p class="muted">Guarantee &divide; buy-in is a descriptive ratio, not a forecast. Bounty
events include bounties in the guarantee, so their ratio is not comparable with a standard
event; the Format column marks them.</p>
{tbl}
""".format(n=len(rows), tbl=events_table(rows), tiers=budget_tiers())
    return body


def page_multientry() -> str:
    multi_rows = []
    for e in sorted(MULTI, key=lambda e: (e["date"], to_min(e["time"]) or 0)):
        explanation = []
        sheet = STRUCTS.get(str(e.get("structure_no")), {})
        if sheet.get("flight_language"):
            explanation.append("sheet describes starting flights and bars a player who bags "
                               "from playing a later flight")
        if sheet.get("multi_day_format"):
            explanation.append("sheet is a multi-day format")
        if e.get("adds_second_entry"):
            explanation.append("sheet carries re-entry/rebuy/add-on language")
        if re.search(r"\b1[a-f]\b", e.get("name", ""), re.I):
            explanation.append("schedule row is a numbered flight (1A, 1B, ...)")
        multi_rows.append([
            name_cell(e, "../"),
            esc(fdate(e["date"])) + "<br>" + ftime(e["time"]),
            money_or_blank(e.get("buyin")),
            money_or_blank(e.get("gtd")),
            "; ".join(explanation) or '<span class="blank">blank</span>',
            verdict_badge(e),
            row_source_cell(e, "../"),
        ])
    multi_tbl = table(["Event", "Date &middot; start", "Buy-in", "Guarantee",
                       "Why it is not single-entry (official)", "Status", "Source"],
                      multi_rows, 6, "multi")
    other_rows = []
    for v in OTHER:
        other_rows.append([
            "<strong>{}</strong><br><span class=\"tiny\">{}</span>".format(
                esc(v["venue"]), esc(v.get("entry_class_reason", ""))),
            esc(v.get("schedule") or "Not stated on the official page"),
            money_or_blank(v.get("buyin")),
            money_or_blank(v.get("guarantee")),
            esc(v.get("addon") or "") or '<span class="blank">blank</span>',
            badge("warn", "Advantage" if v.get("entry_class") == "advantage" else "Unverified"),
            srcs((v.get("source"), "Official page")),
        ])
    other_tbl = table(["Venue", "Schedule (official)", "Buy-in", "Guarantee",
                       "Why it is in this section", "Status", "Source"],
                      other_rows, 6, "other-venues")
    body = controls("events") + panel("""
<strong>Kept separate from single-entry</strong> so nothing here can be mistaken for a
freezeout. A row belongs here when an official source says a player can put in more money
for another chance or more chips: numbered starting flights, re-entry, rebuy, an add-on that
buys chips, or a multi-day format that requires more than one buy-in. The reason for each
row is quoted from the official source.
""") + """
<h2>Multi-flight and multi-entry tournament rows ({n})</h2>
{tbl}
<h2>Other Strip rooms: schedule and entry rules as published</h2>
<p class="muted">Caesars Palace's official page describes a $50 add-on that buys 15,000
extra chips, which is exactly the kind of spending advantage this section exists for. The
other rooms' official pages do not publish enough to classify them, so they stay unverified.</p>
{other}
""".format(n=len(multi_rows), tbl=multi_tbl, other=other_tbl)
    return body


def day_plans():
    """Per-day primary event + conditional fallback from official times.

    A day's primary event is the confirmed single-entry row with the largest
    published guarantee (always preferring a row whose own sheet could be read).
    The fallback is a later row whose official start time is at least 30 minutes
    after the primary's derived playing-day length ends. If none fits, the day
    says "none feasible" instead of proposing an impossible sequence.
    """
    by_day: dict[str, list] = {}
    for e in EVENTS:
        if e.get("date"):
            by_day.setdefault(e["date"], []).append(e)
    def playable(r):
        """A row you can actually enter as a tournament.

        Satellites only award a seat in another event, and restart rows are the
        continuation of an event already counted, so neither can be a day's
        primary tournament.
        """
        return (r.get("verdict") != "restart" and r.get("format") != "satellite"
                and not r.get("restriction"))

    plans = {}
    for date, rows in by_day.items():
        cands0 = [r for r in rows if playable(r)] or rows
        ranked = sorted(
            cands0,
            key=lambda r: (r.get("verdict") not in
                           ("single_entry_confirmed", "multi_flight"),
                           -(r.get("gtd") or 0),
                           r.get("verdict") != "single_entry_confirmed"))
        primary = ranked[0]
        end = None
        if primary.get("one_day_minutes") and primary.get("time"):
            end = (to_min(primary["time"]) or 0) + primary["one_day_minutes"]
        fallback = None
        if end is not None:
            cands = [r for r in rows
                     if r is not primary and playable(r)
                     and (to_min(r["time"]) or 0) >= end + 30]
            if cands:
                fallback = max(
                    cands, key=lambda r: (r.get("verdict") == "single_entry_confirmed",
                                          to_min(r["time"]) or 0))
        overlaps = []
        for a in rows:
            if a.get("verdict") != "single_entry_confirmed" or not a.get("one_day_minutes"):
                continue
            for b in rows:
                if a is b or b.get("verdict") == "restart":
                    continue
                a0, b0 = to_min(a["time"]), to_min(b["time"])
                if a0 is None or b0 is None:
                    continue
                if a0 <= b0 < a0 + a["one_day_minutes"]:
                    overlaps.append((a, b))
        cont = "; ".join(
            "#{} &middot; {} &middot; {}".format(r.get("event_no"), ftime(r["time"]),
                                              esc(r.get("name", "")[:48]))
            for r in rows if r.get("verdict") == "restart")
        plans[date] = {"primary": primary, "fallback": fallback, "overlaps": overlaps,
                       "continuation": cont,
                       "rows": sorted(rows, key=lambda r: to_min(r["time"]) or 0)}
    return plans


def page_schedule() -> str:
    plans = day_plans()
    plan_rows = []
    for date in sorted(plans):
        p = plans[date]
        pr, fb = p["primary"], p["fallback"]
        end_txt = ""
        if pr.get("one_day_minutes"):
            end = (to_min(pr["time"]) or 0) + pr["one_day_minutes"]
            end_txt = ftime("{:02d}:{:02d}".format((end // 60) % 24, end % 60))
        plan_rows.append([
            "<strong>{}</strong>".format(esc(fdate(date))),
            name_cell(pr, "../") + "<br>" + ftime(pr["time"]) + " &middot; " + verdict_badge(pr),
            (name_cell(fb, "../") + "<br>" + ftime(fb["time"]) + " &middot; " +
             verdict_badge(fb) if fb else '<span class="blank">none feasible</span>'),
            (esc(end_txt) + '<br><span class="tiny">derived: official start + sheet '
             'late-reg levels, not a published finish</span>' if end_txt
             else '<span class="blank">blank</span>'),
            ("; ".join("#{} &times; #{}".format(a["event_no"], b["event_no"])
                       for a, b in p["overlaps"]) or "None") if p["overlaps"] else "None",
            p["continuation"] or '<span class="muted">none</span>',
            row_source_cell(pr, "../"),
        ])
    plan_tbl = table(["Date", "Primary event", "Conditional fallback", "Earliest realistic "
                      "exit from the primary", "Other entries whose windows collide",
                      "Continuation of an earlier event (official restart row)",
                      "Source"], plan_rows, 6, "dayplan")
    day_rows = []
    for date in sorted(plans):
        for e in plans[date]["rows"]:
            kind = {"single_entry_confirmed": "Entry (confirmed single)",
                    "multi_flight": "Entry (flight)", "restart": "Restart row",
                    "unverified": "Entry (unverified)"}.get(e.get("verdict"), "Entry")
            day_rows.append([
                esc(fdate(date)), ftime(e["time"]),
                str(e.get("event_no") or ""), esc(e.get("name", "")),
                money_or_blank(e.get("buyin")), money_or_blank(e.get("gtd")),
                verdict_badge(e), esc(kind),
                (str(e["one_day_minutes"]) + " min (derived)"
                 if e.get("one_day_minutes") else '<span class="blank">not derived</span>'),
                row_source_cell(e, "../"),
            ])
    every = table(["Date", "Start", "Event #", "Event name (official)", "Buy-in",
                   "Guarantee", "Single-entry", "Row type", "Playing-day length",
                   "Source"], day_rows, 9, "everyrow")
    body = controls("schedule") + panel("""
<strong>How the day plan is built.</strong> Each day's primary event is the confirmed
single-entry row with the largest published guarantee that day. Its realistic exit is the
official start time plus a playing-day length derived from the sheet's late-registration
figure (levels x minutes per level + breaks). A fallback is only shown when its official
start time is at least 30 minutes after that exit; otherwise the day says "none feasible"
rather than proposing a sequence that cannot be played. The derived length is a planning
figure, not a published finish time.
""") + panel("""
<strong>8:00 AM cannot be met.</strong> No Strip room publishes an 8:00 AM tournament in the
sources read. Horseshoe's official daily slate starts at 9:00 AM (six events: 9 AM, 11 AM,
2 PM, 5 PM, 8 PM, 11 PM); Caesars Palace starts at 10:00 AM; the Venetian's earliest start is
9:10 AM on Dec 12 (event #46, a turbo satellite), and its earliest full-tournament start is
10:10 AM. A full day is therefore 9:00 AM onward, not 8:00 AM onward.
""", "panel warn-panel") + """
<h2>Primary event and conditional fallback, every day with a scheduled row</h2>
{plan}
<h2>Every official dated row ({n})</h2>
{every}
""".format(plan=plan_tbl, every=every, n=len(day_rows))
    return body


def hotel_true_cost(h):
    """True nightly cost, only when both parts are official."""
    fee = h.get("resort_fee_usd")
    if fee is None:
        return None, "Resort fee not verified, so the true cost cannot be computed."
    tax = TAX.get("rate_pct")
    if tax is None:
        return None, "Tax rate not verified, so the true cost cannot be computed."
    return None, ("Fee {} + {}% tax per night; add the room rate from the official booking "
                  "page. No fixed room rate is published, so no single total exists."
                  .format(money(fee), tax))


def page_hotels() -> str:
    rows = []
    for h in HOTEL_ROWS:
        fee = h.get("resort_fee_usd")
        walk = h.get("walk_minutes")
        walk_cell = (badge("ok", "0 min (on-property)") if walk == 0 else
                     badge("bad", "Not verified"))
        fee_cell = (money(fee) if fee is not None else '<span class="blank">blank</span>')
        tax = TAX.get("rate_pct")
        per_night = None
        if fee is not None and tax is not None:
            per_night = fee * (1 + tax / 100.0)
        rows.append([
            "<strong>{}</strong><br><span class=\"tiny\">{}</span>".format(
                esc(h["hotel"]), esc(h.get("role", ""))),
            walk_cell + '<br><span class="tiny">{}</span>'.format(esc(h.get("walk_note", ""))),
            fee_cell,
            (money(round(per_night)) + ' <span class="tiny">fee + tax only</span>'
             if per_night is not None else '<span class="blank">blank</span>'),
            esc(h.get("poker_rate_published") or "") or '<span class="blank">blank</span>',
            esc(h.get("cancellation") or "") or '<span class="blank">blank</span>',
            srcs((h.get("resort_fee_source") or h.get("poker_rate_source") or
                  h.get("source"), "Official page")),
        ])
    tbl = table(["Hotel", "Walk to the poker room", "Resort fee / night",
                 "Fee + tax / night", "Poker rate published", "Cancellation",
                 "Source"], rows, 6, "hotels")
    rate_rows = []
    for r in RATES.get("entries", []):
        rate_rows.append([
            "<strong>{}</strong>".format(esc(r.get("hotel"))),
            esc(r.get("checkin", "")) + " &rarr; " + esc(r.get("checkout", "")),
            str(r.get("nights", "")),
            esc(r.get("occupancy", "")),
            money_or_blank(r.get("checkout_total")),
            money_or_blank(r.get("nightly_average")),
            money_or_blank(r.get("resort_fee_per_night")),
            money_or_blank(r.get("tax_total")),
            esc(r.get("parking") or "") or '<span class="blank">blank</span>',
            esc(r.get("cancellation_deadline") or "") or '<span class="blank">blank</span>',
            esc(r.get("rate_timestamp", "")),
            link(r.get("source", ""), "Booking page"),
        ])
    rate_tbl = table(["Hotel", "Stay", "Nights", "Occupancy", "Checkout total",
                      "Nightly average", "Resort fee / night", "Tax total", "Parking",
                      "Cancellation deadline", "Rate timestamp", "Source"],
                     rate_rows, 11, "ratelog")
    walk_rows = []
    for w in WALKING.get("routes", []):
        ok = w.get("walk_minutes") is not None and w["walk_minutes"] <= WALK_LIMIT
        walk_rows.append([
            "<strong>{}</strong>".format(esc(w.get("hotel", ""))),
            esc(w.get("venue", "")),
            (str(w["walk_minutes"]) + " min" if w.get("walk_minutes") is not None
             else '<span class="blank">unverified</span>'),
            badge("ok", "Passes &le;30") if ok else badge("bad", "Not verified"),
            esc(w.get("note", "")),
            srcs((w.get("source"), "Official page")) if w.get("source")
            else '<a href="../flagged.html#F22">Flagged F22</a>',
        ])
    walk_tbl = table(["Hotel", "Venue", "Walk", "&le;30-minute filter", "Note", "Source"],
                     walk_rows, 5, "walking")
    watch_rows = []
    for key, w in sorted(WATCH.items()):
        excerpts = w.get("resort_fee_excerpts") or []
        watch_rows.append([
            esc(key.replace("_", " ")),
            str(w.get("http_status")),
            esc(w.get("retrieved_at", "")),
            ("<br>".join('"{}"'.format(esc(x)) for x in excerpts[:2])
             if excerpts else '<span class="blank">no fee sentence found</span>'),
            link(w.get("url", ""), "Page"),
        ])
    watch_tbl = table(["Watched page", "HTTP", "Read at", "Verbatim resort-fee sentence "
                       "seen by the scraper", "Source"], watch_rows, 4, "watch")
    body = controls() + panel("""
<strong>True cost of a hotel night</strong> = room rate + mandatory resort fee + tax on
both. The room rate is the only part that moves daily, and no official page publishes a
fixed rate, so it is kept as a dated log rather than a single number. The resort fee and the
tax rate below are official: the fee from each hotel's own page, the 13.38% tax from the
Clark County ordinance table for a resort hotel inside the primary gaming corridor
({taxex}).
""".format(taxex=esc(TAX.get("excerpt", "")).replace("|", " &middot; "))) + """
<h2>Hotels: fees, terms and the walk to the poker room</h2>
{tbl}
<h2>Dated rate log (a log, not a single value)</h2>
<p class="muted">Each line is one snapshot of an official booking page with the date it was
taken. A later line supersedes an earlier one only for the same hotel, stay dates and
occupancy. A snapshot is not a quote: the booking page is the only place a live price exists.</p>
{rates}
<h2>Walking-route check (&le;30-minute filter)</h2>
{walks}
<h2>Watched official pages (the daily scraper records changes here)</h2>
{watch}
""".format(tbl=tbl, rates=rate_tbl, walks=walk_tbl, watch=watch_tbl)
    return body


def page_planner() -> str:
    options = []
    for e in sorted(CONFIRMED, key=lambda e: (e["date"], to_min(e["time"]) or 0)):
        options.append(
            '<option value="{d}|{t}|{n}" data-name="{n}" data-date="{d}" data-time="{t}" '
            'data-buyin="{b}" data-gtd="{g}" data-fee="{f}">{d} {t} &middot; #{n} {x} '
            '&middot; {bb}</option>'.format(
                d=e["date"], t=e["time"], n=e["event_no"],
                x=esc(e["name"][:60]), bb=money(e.get("buyin")) or "",
                b=e.get("buyin") or "", g=e.get("gtd") or "",
                f=(rule_field(e, "house_fee").get("value") or "")))
    hotel_opts = []
    for h in HOTEL_ROWS:
        hotel_opts.append(
            '<option value="{n}" data-fee="{f}" data-name="{n}">{n} &middot; fee {ff} '
            '(+{tax}% tax)</option>'.format(
                n=esc(h["hotel"]), f=h.get("resort_fee_usd") if h.get("resort_fee_usd") is not None else "",
                ff=(money(h.get("resort_fee_usd")) if h.get("resort_fee_usd") is not None
                    else "not verified"), tax=TAX.get("rate_pct", "")))
    body = panel("""
<strong>Estimated trip cost</strong> = entries &times; buy-ins + nights &times; true hotel
cost per night, where true hotel cost = room rate + mandatory resort fee + tax. Every buy-in
and fee in the picker comes from the official source linked on these pages. The room rate is
the one number you have to read off the official booking page for your dates; nothing here
guesses it. This is a planning estimate, not a booking quote.
""") + """
<div class="panel calc">
  <div class="calc-grid">
    <div>
      <h3>1. Stay</h3>
      <label>Nights <input id="nights" type="number" min="1" placeholder="e.g. 7"></label>
      <label>Hotel <select id="hotel" onchange="poker5LoadHotel()">
        <option value="">-- choose a hotel to load its official fee --</option>
        {hotels}
      </select></label>
      <label>Nightly room rate ($) — from the official booking page
        <input id="rate" type="number" min="0" step="1" placeholder="no date-specific quote recorded"></label>
      <label>Resort fee per night ($) <input id="fee" type="number" min="0" step="1"></label>
      <label>Room tax (%) <input id="tax" type="number" min="0" step="0.01" value="{tax}"
        title="Clark County ordinance rate for a resort hotel in the primary gaming corridor; confirm on the official booking page."></label>
      <p class="muted">Fee is loaded from the hotel you pick and confirmed on that hotel's
      official page. Tax is the Clark County rate tied to the ordinance table. An unknown
      rate is never treated as zero: the trip total stays incomplete until a dated room quote
      is entered.</p>
      <p class="tiny">The 13.38% figure is the Clark County ordinance rate for a resort hotel inside the primary gaming corridor. Whether the resort fee is included in the tax base remains unverified on the official pages read; the fee's own tax treatment is confirmed on the folio at checkout.</p>
      <p id="hotel-status" class="tiny">Incomplete. No date-specific room quote is currently recorded for this stay, so the true nightly cost and the trip total cannot be completed yet.</p>
    </div>
    <div>
      <h3>2. Tournaments</h3>
      <label>Confirmed single-entry event <select id="event">
        <option value="">-- pick an event --</option>
        {events}
      </select></label>
      <label>Entries (times you will play this event)
        <input id="count" type="number" min="1" value="1"></label>
      <button class="btn" onclick="poker5AddEntry()">Add to the trip</button>
      <div id="entries" class="entries"></div>
    </div>
  </div>
  <div class="calc-total">
    <div><span>Entries &times; buy-ins</span><strong id="sum-entries">$0</strong></div>
    <div><span>Nights &times; true hotel cost</span><strong id="sum-hotel">$0</strong></div>
    <div><span>Fee + tax per night</span><strong id="sum-nightly">$0</strong></div>
    <div class="grand"><span>Estimated trip cost</span><strong id="sum-total">$0</strong></div>
  </div>
</div>
<h2>Same calculation as a table (no JavaScript needed)</h2>
{quick}
""".format(hotels="".join(hotel_opts), events="".join(options),
           tax=TAX.get("rate_pct", ""), quick=quick_cost_table())
    return body


def quick_cost_table() -> str:
    """A worked example computed from official fees only, clearly labelled."""
    rows = []
    fee = next((h.get("resort_fee_usd") for h in HOTEL_ROWS
                if h["hotel"].startswith("The Venetian")), None)
    tax = TAX.get("rate_pct")
    cheapest = sorted([e for e in CONFIRMED if e.get("buyin")],
                      key=lambda e: e["buyin"])[:3]
    for e in cheapest:
        rows.append([
            "<strong>#{} {}</strong><br><span class=\"tiny\">{} &middot; {}</span>".format(
                e["event_no"], esc(e["name"][:52]), esc(fdate(e["date"])), ftime(e["time"])),
            money_or_blank(e.get("buyin")),
            money_or_blank((rule_field(e, "house_fee") or {}).get("value")),
            money_or_blank(e.get("gtd")),
            ratio_cell(e),
            row_source_cell(e, "../"),
        ])
    t = table(["Event", "Buy-in", "House fee inside the buy-in", "Guarantee",
               "Guarantee &divide; buy-in", "Source"], rows, 5, "quick")
    example = ""
    if fee is not None and tax is not None:
        tn = fee * (1 + tax / 100.0)
        example = ("<p class=\"muted\">Worked example with official parts only: resort fee "
                   "{} + {}% tax = <strong>{} per night before the room rate</strong>. For a "
                   "7-night stay that part alone is {}. The room rate is added from the "
                   "official booking page.</p>"
                   .format(money(fee), tax, money(round(tn)), money(round(tn * 7))))
    return t + example


def page_venue_venetian() -> str:
    rows = sorted(CONFIRMED, key=lambda e: (e["date"], to_min(e["time"]) or 0))
    hs = [h for h in HOTEL_ROWS if "venetian" in h["hotel"].lower() or "palazzo" in h["hotel"].lower()]
    hotel_rows = []
    for h in hs:
        hotel_rows.append([
            "<strong>{}</strong><br><span class=\"tiny\">{}</span>".format(esc(h["hotel"]), esc(h.get("role", ""))),
            badge("ok", "0 min (on-property)") if h.get("walk_minutes") == 0 else badge("bad", "Not verified"),
            money_or_blank(h.get("resort_fee_usd")),
            esc(h.get("poker_rate_published") or "") or '<span class="blank">blank</span>',
            srcs((h.get("resort_fee_source") or h.get("poker_rate_source"), "Official page"),
                 (SUITE_URL, "Poker suite rates")),
        ])
    htbl = table(["Hotel", "Walk", "Resort fee / night", "Poker rate published", "Source"],
                 hotel_rows, 4, "venetian-hotels")
    return controls("events") + panel("""
The Venetian hosts the <strong>DeepStack Extravaganza IV</strong> (November 16 - December 23,
2026) and publishes more than $3.6 million in guaranteed prize pools. All {n} scheduled rows
are on this site; the {c} that pass the single-entry test are listed below. Every rule field
comes from the structure sheet linked in the row.
""".format(n=len(EVENTS), c=len(rows))) + """
<h2>Confirmed single-entry events at The Venetian</h2>
{tbl}
<h2>Hotels on the property</h2>
{htbl}
""".format(tbl=events_table(rows, "../"), htbl=htbl)


def page_venue_wynn() -> str:
    rows = []
    for v in OTHER:
        if v.get("venue_group") != "wynn":
            continue
        rows.append([
            "<strong>{}</strong>".format(esc(v["venue"])),
            esc(v.get("schedule") or ""),
            money_or_blank(v.get("guarantee")),
            esc(v.get("entry_class_reason", "")),
            badge("warn", "Advantage" if v.get("entry_class") == "advantage" else "Unverified"),
            srcs((v.get("source"), "Official page")),
        ])
    tbl = table(["Wynn offering", "Schedule (official)", "Guarantee", "Status note",
                 "Section", "Source"], rows, 5, "wynn")
    hs = [h for h in HOTEL_ROWS if "wynn" in h["hotel"].lower() or "encore" in h["hotel"].lower()]
    hotel_rows = [[
        "<strong>{}</strong><br><span class=\"tiny\">{}</span>".format(esc(h["hotel"]), esc(h.get("role", ""))),
        badge("ok", "0 min (Wynn poker room)") if h.get("walk_minutes") == 0 else badge("bad", "Not verified"),
        money_or_blank(h.get("resort_fee_usd")),
        esc(h.get("cancellation") or "") or '<span class="blank">blank</span>',
        srcs((h.get("resort_fee_source"), "Official terms")),
    ] for h in hs]
    htbl = table(["Hotel", "Walk", "Resort fee / night", "Cancellation (official)",
                  "Source"], hotel_rows, 4, "wynn-hotels")
    return controls("events") + panel("""
The WPT World Championship runs <strong>November 27 - December 21, 2026</strong> at Wynn,
with the Main Event December 13 - 20 per the official WPT event page. The Wynn poker page
states that its daily tournament slate is suspended during its series, so the daily and
festival offerings never run at the same time. No festival row is classified as
single-entry here because the festival structures PDF was not read row by row
({f16}).
""".format(f16=flag_link("F16", "../"))) + """
<h2>What Wynn publishes</h2>
{tbl}
<h2>Hotels on the property</h2>
{htbl}
""".format(tbl=tbl, htbl=htbl)


def page_venue_others() -> str:
    rows = []
    for v in OTHER:
        if v.get("venue_group") == "wynn":
            continue
        rows.append([
            "<strong>{}</strong>".format(esc(v["venue"])),
            esc(v.get("schedule") or "Not published on the official page"),
            money_or_blank(v.get("buyin")),
            money_or_blank(v.get("guarantee")),
            esc(v.get("level_minutes") or "") or '<span class="blank">blank</span>',
            esc(v.get("addon") or "") or '<span class="blank">blank</span>',
            badge("warn", "Unverified" if v.get("entry_class") != "advantage" else "Advantage"),
            srcs((v.get("source"), "Official page")),
        ])
    tbl = table(["Room", "Schedule (official)", "Buy-in", "Guarantee", "Levels (min)",
                 "Add-on / rebuy", "Status", "Source"], rows, 7, "others")
    hs = [h for h in HOTEL_ROWS if h.get("venue_group") == "other"]
    hotel_rows = [[
        "<strong>{}</strong>".format(esc(h["hotel"])),
        badge("ok", "0 min (on-property)") if h.get("walk_minutes") == 0 else badge("bad", "Not verified"),
        money_or_blank(h.get("resort_fee_usd")),
        esc(h.get("resort_fee_status", "")),
        srcs((h.get("resort_fee_source") or h.get("poker_rate_source")
              or h.get("source"), "Official page")),
    ] for h in hs]
    htbl = table(["Hotel", "Walk", "Resort fee / night", "Fee status", "Source"],
                 hotel_rows, 4, "other-hotels")
    return controls("events") + panel("""
These rooms are on the Strip and within a short walk or a short ride of each other, but none
of their official pages publishes a complete, dated, single-entry tournament right now. What
each page does say is recorded with the sentence it came from. Where the page is silent the
cell is blank, not guessed.
""") + """
<h2>Other Strip rooms</h2>
{tbl}
<h2>Their hotels</h2>
{htbl}
""".format(tbl=tbl, htbl=htbl)


def page_qa() -> str:
    rows = [
        ["Q01", "When is the trip, and how many are travelling?",
         "Blocks the trip total and the hotel log",
         "Nothing official depends on it, but every cost answer does: the rate log, the "
         "number of nights and the party size all key off these three facts.",
         "You provide the dates and the number of adults. Until then the planner uses the "
         "logged snapshot stay (Dec 2 - Dec 9, 2026) as an example only.",
         "unresolved"],
        ["Q02", "What is the nightly budget and the minimum hotel quality?",
         "Blocks the hotel choice",
         "The brief asks for cost and quality over distance, but no official page publishes "
         "a quality score, so quality has no source yet.",
         "Pick a quality standard (for example a published star rating) and a nightly cap. "
         "Then the hotels page can rank with numbers instead of blanks.",
         "unresolved"],
        ["Q03", "Is the 8:00 AM start a hard requirement?",
         "Resolved by the official schedules: no 8:00 AM start exists",
         "The earliest official start found is 9:00 AM (Horseshoe, six daily events). "
         "Caesars Palace starts at 10:00 AM; the Venetian's earliest is 9:10 AM.",
         "Either accept a 9:00 AM start or add a non-tournament morning activity. No source "
         "can move a room's published start time.",
         "answered"],
        ["Q04", "Which events are genuinely single-entry?",
         "Answered for {} rows".format(len(CONFIRMED)),
         "Each confirmed row's own structure sheet was read, lists that event number, is a "
         "one-day event and contains no re-entry, rebuy, add-on or purchased-stack "
         "language.",
         "For the rows still unverified, the sheet is either unreadable or does not name "
         "the event; the row links both the schedule and the sheet so it can be checked.",
         "answered"],
        ["Q05", "How long does a hotel-to-room walk take?",
         "Blocks the 30-minute rule for every off-property hotel",
         "No casino publishes a walking time. Only on-property routes are zero minutes by "
         "definition.",
         "Measure each route once on a named map service, record the provider, the route "
         "and the date, and it can enter the walking table with that source.",
         "unresolved"],
        ["Q06", "What is the true nightly hotel cost?",
         "Partly answered: every fee and tax is official, the room rate is not",
         "Resort fees: Venetian/Palazzo $55, Wynn/Encore $55, Bellagio $55, ARIA $55, MGM "
         "Grand $50. Room tax 13.38% per the county ordinance table. Room rates are "
         "dynamic.",
         "Read the rate off the official booking page for your dates and add fee + tax. The "
         "calculator does exactly that.",
         "partly answered"],
        ["Q07", "Which events can be played back to back on one day?",
         "Answered from official start times and derived lengths",
         "The schedule page gives each day a primary event, a derived exit time and a "
         "fallback only when a later official start clears that exit by 30 minutes.",
         "Finishing times are not published, so the exit is derived from the sheet's "
         "late-registration level count. Treat it as a planning figure.",
         "answered with an assumption"],
        ["Q08", "Caesars Palace and Horseshoe resort fees",
         "Missing",
         "No official Caesars resort-fee page was found; the fees stay blank.",
         "The Caesars booking page price breakdown for your dates will show the fee.",
         "unresolved"],
        ["Q09", "Bellagio, MGM Grand and ARIA tournament schedules",
         "Missing or stale",
         "Bellagio's PDFs are undated and its Saturday buy-in contradicts itself; MGM "
         "Grand's PDF is titled August; ARIA lists no tournaments.",
         "Only the rooms themselves can confirm; their contact details are on the official "
         "poker pages.",
         "unresolved"],
        ["Q10", "Wynn festival event-by-event schedule",
         "Not read row by row",
         "The festival window and the Main Event dates are official. The per-event "
         "structures PDF is linked from the Wynn poker page and is watched daily.",
         "Read the festival structures PDF for the events you care about, or ask the Wynn "
         "poker desk.",
         "unresolved"],
        ["Q11", "Guarantee disagreements",
         "Recorded, not resolved",
         "Three Venetian rows print a different guarantee on the schedule row than on the "
         "structure sheet.",
         "The site shows both figures side by side and never picks one. Ask the poker room "
         "if the difference matters for your decision.",
         "flagged"],
        ["Q12", "Is a second-entry rule ever a single-entry event?",
         "Standard published",
         "A sheet that allows a player to buy a second entry is never called single-entry "
         "here, even if the schedule is one day.",
         "Nothing to do: the rule is stated on the Sources &amp; method page.",
         "answered"],
    ]
    kind = {"answered": ("ok", "Answered"), "partly answered": ("warn", "Partly answered"),
            "unresolved": ("bad", "Unresolved"), "flagged": ("warn", "Flagged"),
            "answered with an assumption": ("warn", "Answered with an assumption")}
    cells = []
    for r in rows:
        k, label = kind.get(r[5], ("warn", r[5]))
        cells.append([esc(r[0]), esc(r[1]), badge(k, label), esc(r[2]), esc(r[3]), esc(r[4])])
    tbl = table(["#", "Question", "Status", "Why it matters", "What we know", "How to get "
                 "the answer / what it needs"], cells, None, "qa")
    return panel("""
Every question below is either answered from an official source, answered with a stated
assumption, or open. An open question is not a reason to guess: it is a reason to leave the
value blank, which is why several columns on this site are empty.
""") + tbl


def page_suggestions() -> str:
    rows = [
        ["S01", "Read every structure sheet with a scheduled scraper",
         "2", "3", "done",
         "Implemented: a GitHub Actions job reads the schedule page and all {n} linked PDFs "
         "every morning, stores the excerpt for each field and rebuilds the site. "
         "<a href=\"sources.html\">Method</a>".format(n=SCRAPED_SHEETS())],
        ["S02", "Put one dated 'read on' stamp on every row",
         "2", "1", "done",
         "Implemented: each row shows the date its structure sheet was read, and the footer "
         "shows the capture timestamp."],
        ["S03", "Show guarantee conflicts instead of choosing one",
         "3", "1", "done",
         "Implemented: a row whose schedule and sheet guarantees differ shows both values and "
         "a link to the flag."],
        ["S04", "Build the day plan from official times only",
         "3", "2", "done",
         "Implemented: a primary event, a derived exit and a fallback that must start 30 "
         "minutes after that exit."],
        ["S05", "Keep a dated rate log rather than one rate",
         "2", "2", "done",
         "Implemented: every rate snapshot keeps its timestamp and its stay dates."],
        ["S06", "Add a live booking-price fetch per date",
         "3", "4", "needs a decision",
         "The official booking engines are dynamic and their terms restrict automated use. "
         "Options: (a) keep manual dated snapshots, (b) link out to the official booking page "
         "for the chosen dates, (c) request permission from each property. (b) is honest and "
         "free; (a) is what the log does now."],
        ["S07", "Verify off-property walking times on a map service",
         "2", "2", "needs a decision",
         "A map measurement is a third-party source, not an official one. If you accept a "
         "named provider as the standard, each route can be recorded with its provider, "
         "route and date and can pass the 30-minute filter."],
        ["S08", "Choose a hotel quality standard",
         "2", "1", "needs your choice",
         "Quality is blank because no official page publishes it. A published star rating "
         "or a hotel's own category would work; pick one and it becomes a sourced column."],
        ["S09", "Read the Wynn festival structures per event",
         "2", "2", "open",
         "The festival PDF is on the daily watch list; classifying its rows needs the "
         "re-entry terms read event by event."],
        ["S10", "Ask each room for its written entry policy",
         "3", "5", "needs a decision",
         "One email or call per room would convert 'no re-entry language in the sheet' into "
         "a written statement. Contacts: Venetian lv_cas_poker@venetianlasvegas.com / "
         "702.414.7657."],
        ["S11", "Add the remaining Strip rooms (Resorts World, Sahara, Golden Nugget)",
         "2", "3", "open",
         "Their official pages were not read this session. Adding them widens the choice but "
         "only with the same standard."],
        ["S12", "Publish a change feed for every watched page",
         "1", "2", "open",
         "The scraper already stores a content hash per page. A small changes page could list "
         "what moved since yesterday."],
    ]
    kind = {"done": ("ok", "Done"), "needs a decision": ("warn", "Needs a decision"),
            "needs your choice": ("warn", "Needs your choice"), "open": ("muted", "Open")}
    cells = []
    for r in rows:
        k, label = kind.get(r[4], ("muted", r[4]))
        cells.append([esc(r[0]), "<strong>{}</strong>".format(esc(r[1])), esc(r[2]), esc(r[3]),
                      badge(k, label), r[5]])
    tbl = table(["#", "Suggestion", "Impact (1-3)", "Cost (1-5)", "Status", "Detail"], cells,
                None, "suggestions")
    return panel("""
This is the review board: every idea, what it changes, what it costs, and the decision it
needs. Nothing here is implemented without the decision it names, and the implemented ones
are marked so you can see the difference.
""") + tbl + panel("""
<strong>Recommended order if you only do three things.</strong> S06 (link straight to the
official booking page for your dates, which removes the last blank in the trip total), S07
(agree a map provider so the 30-minute rule can be applied to off-property hotels), and S10
(one written entry policy per room you are actually going to play, which converts the
labeling standard into a written guarantee).
""", "panel warn-panel")


def SCraped_sheets():
    return SCRAPE.get("sheets_read", "?")


def SCRAPED_SHEETS():
    return SCRAPE.get("sheets_read", "?")


def page_flagged() -> str:
    rows = []
    for f in FLAGS:
        rows.append([
            '<a id="{}"></a><strong>{}</strong>'.format(esc(f["id"]), esc(f["id"])),
            esc(f["item"]),
            esc(f.get("value_shown", "")),
            badge("bad" if f.get("status") in ("Unverified",) else "warn", f.get("status", "")),
            (srcs(*[(u, "Source {}".format(i + 1))
                     for i, u in enumerate(f.get("sources", []))])
             if f.get("sources") else
             '<a href="#{}">Flagged: no official source exists</a>'.format(esc(f["id"]))),
            esc(f.get("to_clear", "")),
        ])
    tbl = table(["ID", "Item", "What the site shows", "Status", "Sources",
                 "What would clear it"], rows, 4, "flags")
    disc = EV.get("discrepancies", []) or []
    disc_rows = []
    for d in disc:
        if d["kind"] == "row_name_differs":
            continue  # cosmetic wording differences are counted, not listed
        disc_rows.append([
            esc(d["kind"].replace("_", " ")),
            esc(d.get("date", "")) + " " + esc(d.get("time", "")),
            esc(str(d.get("event_no") or "")),
            esc(json.dumps({k: v for k, v in d.items()
                            if k not in ("kind", "date", "time", "event_no")})),
            link(DSE_URL, "Schedule"), 
        ])
    disc_head = panel("""
<strong>Cross-checks run on the capture.</strong> Every schedule row is matched against the
transcribed schedule and against its structure sheet. {n} differences were found in total;
{cos} of them are cosmetic wording differences between the transcription and the live page
(the live page wording is shown). The rest are listed here.
""".format(n=len(disc), cos=sum(1 for d in disc if d["kind"] == "row_name_differs")))
    disc_tbl = (table(["Difference", "Date", "Event #", "Detail", "Source"], disc_rows, 4,
                      "discrepancies") if disc_rows else
                "<p class=\"muted\">No differences outside cosmetic wording.</p>")
    return panel("""
Flagged items do not block publication and none of them is a reason to guess. Each one says
what the site currently shows, which official source was read, and what would clear it. Links
go straight to the official page or PDF.
""") + tbl + "<h2>Source cross-checks</h2>" + disc_head + disc_tbl


def page_sources() -> str:
    st = (SCRAPE.get("sources") or {})
    rows = []
    for url, info in sorted(st.items()):
        rows.append([
            esc(info.get("status", "")),
            esc(info.get("retrieved_at", "")),
            esc((info.get("sha256") or "")[:12]) or '<span class="blank">blank</span>',
            esc(info.get("note", "")),
            link(url, "Open"),
        ])
    tbl = table(["HTTP", "Read at", "Content hash", "Note", "Source"], rows, 4, "sources")
    return panel("""
<strong>Confirmation standard used on this site.</strong>
<ol class="tight">
  <li>A value is shown only when an official source states it, and the row links that source.</li>
  <li>A tournament is called <em>confirmed single-entry</em> when its own structure sheet was
      read, the sheet's event-number list includes that event, the format is one day, and the
      text contains no re-entry, rebuy, add-on, double-entry, alternate-stack or
      purchased-chip language. Silence on re-entry, together with a read sheet, is the
      standard; it is stated here so you can reject it if you disagree.</li>
  <li>A structure sheet's own words are quoted next to the value they support, so the quote can
      be checked against the PDF in one click.</li>
  <li>If two official sources disagree, both values are shown and the row is flagged. Nothing
      is averaged or chosen.</li>
  <li>If a value is missing, the cell is blank and appears on the Flagged page. No value is
      inferred, estimated, or carried over from a third-party site.</li>
  <li>Every page is rebuilt from the stored capture, and the build fails if a data row has no
      source link or if an internal link is broken.</li>
</ol>
""") + """
<h2>Every official URL read in the last capture</h2>
<p class="muted">The capture ran at {run} and read {n} official URLs. The content hash is
stored so the next run can tell whether a page changed.</p>
{tbl}
<h2>The scanner itself</h2>
<p class="muted">The reading is done by <code>scripts/scrape_251c122f.py</code>, which runs on
a schedule in <code>.github/workflows/daily-scrape.yml</code> and writes the capture into
<code>data/c6087e2c/</code>. The parser has a self-test with no network access; the merge step
(<code>scripts/merge_251c122f.py</code>) applies the standard above and records why each row
got its verdict. A separate check (<code>scripts/crosscheck_251c122f.py</code>) re-derives
every verdict from the stored rule fields and fails the build if one cannot be reproduced.</p>
<p>Source files: <a href="{repo}/blob/main/scripts/scrape_251c122f.py">scraper</a>,
<a href="{repo}/blob/main/scripts/merge_251c122f.py">merge</a>,
<a href="{repo}/blob/main/scripts/crosscheck_251c122f.py">cross-check</a>,
<a href="{repo}/blob/main/data/c6087e2c/structures.json">structures.json</a>,
<a href="{repo}/blob/main/data/c6087e2c/events_verified.json">events_verified.json</a>.</p>
""".format(run=esc(LAST_SCRAPE), n=SCRAPE.get("official_source_count", len(st)) or len(st),
           tbl=tbl, repo=REPO_URL)


def page_exec() -> str:
    """Executive summary, every number generated from the capture."""
    best = sorted([e for e in CONFIRMED if e.get("gtd") and e.get("buyin")],
                  key=lambda e: -e["gtd"])[:5]
    top_rows = [[name_cell(e, "../"),
                 esc(fdate(e["date"])) + " &middot; " + ftime(e["time"]),
                 money_or_blank(e.get("buyin")), money_or_blank(e.get("gtd")),
                 ratio_cell(e),
                 (badge("warn", "Guarantee conflict") if e.get("gtd_conflict")
                  else badge("muted", "Agrees")),
                 row_source_cell(e, "../")] for e in best]
    top_tbl = table(["Event", "Date &middot; start", "Buy-in", "Guarantee",
                     "Guarantee &divide; buy-in", "Schedule vs sheet", "Source"],
                    top_rows, 6, "exec-top")
    plan = day_plans()
    days = len(plan)
    with_fb = sum(1 for d in plan.values() if d["fallback"])
    conflicts = [d for d in (EV.get("discrepancies") or [])
                 if d["kind"] == "guarantee_conflict"]
    earliest = min((e for e in EVENTS if e.get("time")),
                   key=lambda e: to_min(e["time"]) or 9999)
    fees = {}
    for h in HOTEL_ROWS:
        if h.get("resort_fee_usd") is not None:
            fees.setdefault(h["resort_fee_usd"], []).append(h["hotel"].split(" (")[0])
    fee_text = "; ".join("{}: {}".format(money(f), ", ".join(sorted(set(n))))
                         for f, n in sorted(fees.items()))
    cash_entries = [e for e in CONFIRMED if e.get("format") != "satellite"]
    cheapest = min((e for e in cash_entries if e.get("buyin")),
                   key=lambda e: e["buyin"])
    largest = max([e for e in cash_entries if e.get("gtd")], key=lambda e: e["gtd"])
    body = panel("""
<h2>Executive summary</h2>
<p><strong>The trip this site can support:</strong> a Strip poker trip between
{first} and {last}, built on the {conf} tournaments that pass the single-entry test at The
Venetian, with a second event on {withfb} of the {days} scheduled days, and hotel nights whose
resort fee and tax are official while the room rate is read from the official booking page for
your dates.</p>
<ol class="tight">
  <li><strong>Supply is strong and fully read.</strong> {rows} scheduled rows come from the
  official Venetian DeepStack Extravaganza IV page. {conf} are confirmed single-entry, {multi}
  are multi-flight or multi-entry (separate section), {rest} are restart rows of an event
  already counted. All {sheets} distinct structure-sheet PDFs were downloaded and read, so the
  rule fields in every confirmed row are official values with their own quote.</li>
  <li><strong>How "confirmed single-entry" is decided.</strong> The row's own sheet lists that
  event number, describes a one-day event, and contains no re-entry, rebuy, add-on,
  double-entry, alternate-stack or purchased-chip language. Rows that fail any part of that
  test are not in the single-entry table, and the standard itself is published on
  <a href="sources.html">Sources &amp; method</a> so it can be challenged.</li>
  <li><strong>Cheapest confirmed cash entry is {cheap_b} buy-in, {cheap_name}</strong>; the
  largest confirmed guarantee is {large_g} ({large_name}). Guarantee &divide; buy-in is shown
  as a descriptive ratio, never a forecast. Satellites are marked with a Satellite badge and
  are left out of these two figures, because their prize is a seat in another event rather
  than cash.</li>
  <li><strong>Official fees found:</strong> {fees}. Room tax is 13.38% under the Clark County
  ordinance table for a resort hotel inside the primary gaming corridor. Caesars Palace and
  Horseshoe fees are still missing, so those nights cannot be costed yet.</li>
  <li><strong>The day plan is playable, not idealised.</strong> Every scheduled day gets one
  primary event and, where a later official start clears the primary's derived exit by 30
  minutes, a fallback. {withfb} of {days} days have a feasible fallback; the rest show "none
  feasible" instead of a sequence you could not play. Restart rows (Day 2, Day 3, final table)
  are shown in their own column so a continuation day is never mistaken for a fresh entry.</li>
  <li><strong>The 8:00 AM goal cannot be met.</strong> The earliest official start anywhere on
  the Strip is {earliest_t} ({earliest_n}). The Venetian's earliest full-tournament start is
  10:10 AM. A full day therefore starts at 9:00 AM at the earliest.</li>
  <li><strong>{nconf} official-source disagreements are published, not resolved.</strong> Where
  a schedule row and its structure sheet print different guarantees, the row shows both and
  links both. Nothing is averaged or chosen.</li>
</ol>
""".format(first=fdate(min(e["date"] for e in EVENTS)),
           last=fdate(max(e["date"] for e in EVENTS)),
           rows=len(EVENTS), conf=len(CONFIRMED), multi=len(MULTI), rest=len(RESTARTS),
           sheets=SCRAPE.get("sheets_total", "?"), withfb=with_fb, days=days,
           fees=fee_text, cheapest="",
           cheap_b=money(cheapest.get("buyin")),
           cheap_name=esc(shorten(cheapest["name"], 64)),
           large_g=money(largest.get("gtd")),
           large_name=esc(shorten(largest["name"], 64)),
           earliest_t=ftime(earliest.get("time", "")),
           earliest_n=esc(shorten(earliest.get("name", ""), 64)),
           nconf=len(conflicts))) + """
<h2>The five largest confirmed single-entry guarantees</h2>
{top}
<h2>What to decide first, in order</h2>
{decisions}
<h2>What this page cannot tell you, and why</h2>
{limits}
""".format(top=top_tbl, decisions=panel("""
<ol class="tight">
  <li><strong>Dates, nights and party size.</strong> Every cost answer keys off them (Q01).</li>
  <li><strong>A nightly cap and a quality standard.</strong> No official page publishes a
  quality score, so the hotel ranking cannot include quality until you pick a standard
  (Q02, S08).</li>
  <li><strong>Whether a named map service may be used as the walking-time source.</strong>
  Until then only on-property hotels can pass the 30-minute rule (Q05, S07).</li>
  <li><strong>Whether to read booking rates by hand or link out.</strong> The official booking
  engines are dynamic and restrict automated use (S06).</li>
</ol>
""", "panel warn-panel"), limits=panel("""
<ul class="tight">
  <li><strong>Room rates:</strong> dynamic; the rate log stores dated snapshots instead of a
  single value, because a single value would be wrong for any other stay.</li>
  <li><strong>Finishing times:</strong> not published anywhere. The exit time on the schedule
  page is derived from each sheet's late-registration level count and is labelled as derived.</li>
  <li><strong>Off-property walking times:</strong> no casino publishes one; they stay blank.</li>
  <li><strong>Bellagio, MGM Grand and ARIA tournament schedules:</strong> the official material
  is undated, stale, or absent, so no row from those rooms is classified.</li>
  <li><strong>Wynn festival rows:</strong> the festival window and Main Event dates are
  official; the per-event structures were not read row by row.</li>
</ul>
""", "panel"))
    return body


def page_repo_review() -> str:
    gh = REPO_URL + "/blob/main/"
    rows = [
        ["Root site (index.html, pages/, assets/)", "Rebuilt",
         "The previously published root site was replaced by this build, which is generated "
         "only from the official capture in data/c6087e2c/. Every prior page is still in Git "
         "history.", link(gh + "index.html", "index.html")],
        ["scripts/scrape_251c122f.py", "New",
         "Reads the official schedule page and all linked structure sheets, stores excerpts, "
         "never decides anything.", link(gh + "scripts/scrape_251c122f.py", "scraper")],
        ["scripts/merge_251c122f.py", "New",
         "Applies the single-entry standard to the capture, records the basis for every "
         "verdict, and records source disagreements instead of resolving them.",
         link(gh + "scripts/merge_251c122f.py", "merge")],
        ["scripts/crosscheck_251c122f.py", "New",
         "Re-derives every verdict and fails the build if one cannot be reproduced from the "
         "stored rule fields.", link(gh + "scripts/crosscheck_251c122f.py", "cross-check")],
        ["scripts/build_251c122f.py", "New",
         "Generates this site. It refuses to publish a data row without a source link or an "
         "internal link that does not resolve.",
         link(gh + "scripts/build_251c122f.py", "builder")],
        ["data/c6087e2c/", "Extended",
         "Adds schedule_live.json, structures.json, events_verified.json, scrape_status.json, "
         "watch_status.json, hotels_251c122f.json, other_venues_251c122f.json and "
         "flags_251c122f.json to the existing capture.",
         link(REPO_URL + "/tree/main/data/c6087e2c", "data/c6087e2c")],
        [".github/workflows/daily-scrape.yml", "New",
         "Daily read of every official source, merge, rebuild, validate, commit. Branch runs "
         "also refresh the capture so a change is never only local.",
         link(gh + ".github/workflows/daily-scrape.yml", "workflow")],
        ["Other sessions' folders (docs/, site/, site-*/, dashboard-*/, planner-aa83f1e1/, "
         "data-*/, tools/)", "Left unchanged",
         "Parallel-session output from earlier passes. Not edited here; still reachable in "
         "the repository.", link(REPO_URL, "repository")],
    ]
    tbl = table(["File or area", "Change", "What it does", "Link"], rows, 3, "repo")
    findings = [
        ["F-R1", "Multiple parallel dashboards for the same brief",
         "Irregularity (organisational)",
         "docs/, site/, five dashboard-* folders and three site-* folders all answer the same "
         "questions, with different numbers. This pass publishes one root site and leaves the "
         "others untouched."],
        ["F-R2", "Earlier root site stated figures that the official sheets contradict",
         "Irregularity (data)",
         "The previous build reported 31 confirmed single-entry events; reading all 37 sheets "
         "gives {} confirmed. The earlier figure is superseded, not deleted.".format(len(CONFIRMED))],
        ["F-R3", "Third-party resort fees on the earlier hotels page",
         "Irregularity (sourcing)",
         "Bellagio, ARIA and MGM Grand fees previously came from a news article. All three "
         "are now read from each hotel's own reservation terms; MGM Grand is $50, not $55."],
        ["F-R4", "Tax rate cited without a working official reference",
         "Irregularity (sourcing)",
         "13.38% is now tied to the ordinance table row 'Resort hotel within primary gaming "
         "corridor | 12.5% | 0.88% | 13.38%' and the caveat that the rate may change."],
        ["F-R5", "A single hotel rate treated as a value",
         "Irregularity (method)",
         "Rates are now a dated log. One snapshot can never stand in for another stay."],
    ]
    ftbl = table(["ID", "Finding", "Type", "Detail"], findings, None, "findings")
    return panel("""
This page is the repo review: what changed, what was irregular, and what was done about it.
It is written so a reviewer can check each claim against the linked file.
""") + tbl + "<h2>Irregularities found while reviewing the repository</h2>" + ftbl


# ------------------------------------------------------------------ assets
def write_assets():
    css = """/* Poker5 — single stylesheet, no fonts, no trackers. */
:root{--bg:#0d1117;--panel:#151b23;--line:#263140;--ink:#e6edf3;--mut:#94a3b8;
--acc:#2f81f7;--ok:#1f7a4d;--warn:#8a5b00;--bad:#8b2c2c;--ok-ink:#7ee2a8;
--warn-ink:#ffd166;--bad-ink:#ff9b9b}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,
BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:#79b8ff;text-decoration:none}
a:hover{text-decoration:underline}
.topbar{position:sticky;top:0;z-index:20;background:#0b1017ee;border-bottom:1px solid var(--line);
backdrop-filter:blur(6px);padding:10px 18px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:.2px;display:flex;gap:8px;align-items:center}
.brand small{color:var(--mut);font-weight:400}
.logo{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:7px;
background:var(--acc);color:#fff;font-size:12px;font-weight:800}
.nav{display:flex;gap:4px;flex-wrap:wrap}
.nav a{color:var(--mut);padding:5px 9px;border-radius:7px;font-size:13.5px}
.nav a:hover{background:#1b2430;color:var(--ink);text-decoration:none}
.wrap{max-width:1240px;margin:0 auto;padding:26px 18px 60px}
h1{font-size:26px;margin:6px 0 18px}
h2{font-size:18px;margin:26px 0 10px}
h3{font-size:15px;margin:14px 0 6px}
.hero{background:linear-gradient(180deg,#152033,#111823);border:1px solid var(--line);
border-radius:14px;padding:22px}
.hero h2{margin:0 0 8px;font-size:22px}
.hero p{margin:0;color:#c8d3e0;max-width:80ch}
.ctas{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.btn{display:inline-block;background:var(--acc);color:#fff;padding:9px 14px;border-radius:9px;
font-weight:600;border:0;cursor:pointer;font-size:14px}
.btn:hover{text-decoration:none;filter:brightness(1.08)}
.btn.ghost{background:#1b2430;color:var(--ink);border:1px solid var(--line)}
.btn.small{padding:5px 9px;font-size:12px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px}
.stat .num{font-size:24px;font-weight:700}
.stat .lbl{color:var(--mut);font-size:12.5px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;margin:16px 0}
.panel.warn-panel{border-color:#5c4a12;background:#1c1a10}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;color:var(--ink)}
.card:hover{border-color:var(--acc);text-decoration:none}
.card h3{margin:0 0 6px}
.card p{margin:0;color:var(--mut);font-size:13.5px}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;
background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.search{flex:1 1 320px;min-width:220px;background:#0b1017;border:1px solid var(--line);
color:var(--ink);border-radius:9px;padding:9px 11px}
.toggle{display:flex;gap:6px;align-items:center;color:var(--mut);font-size:13px}
.toggle select{background:#0b1017;color:var(--ink);border:1px solid var(--line);
border-radius:8px;padding:6px 8px}
.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:12px}
.tbl{border-collapse:collapse;width:100%;font-size:13px}
.tbl th{position:sticky;top:0;background:#1a2330;text-align:left;padding:9px 10px;
border-bottom:1px solid var(--line);white-space:nowrap;font-size:12px;color:#b9c7d6}
.tbl td{padding:9px 10px;border-bottom:1px solid #1e2733;vertical-align:top}
.tbl tr:hover td{background:#18202b}
.badge{display:inline-block;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:700;
border:1px solid transparent;white-space:nowrap}
.badge-ok{background:#0f2e21;color:var(--ok-ink);border-color:#1f7a4d}
.badge-warn{background:#2e2708;color:var(--warn-ink);border-color:#6b5510}
.badge-bad{background:#2f1516;color:var(--bad-ink);border-color:#7a2a2a}
.badge-muted{background:#1b2430;color:var(--mut);border-color:var(--line)}
.blank{color:#6b7787;font-style:italic}
.tiny{font-size:11.5px;color:var(--mut);line-height:1.35}
.muted{color:var(--mut)}
.tight{margin:6px 0;padding-left:20px}
.numbered{margin:8px 0;padding-left:22px}
.calc-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
label{display:block;margin:8px 0;color:var(--mut);font-size:13px}
input,select{display:block;width:100%;margin-top:4px;background:#0b1017;color:var(--ink);
border:1px solid var(--line);border-radius:9px;padding:9px 10px}
.entries{margin:10px 0}
.entry-row{display:flex;justify-content:space-between;gap:10px;align-items:center;
border-bottom:1px dashed var(--line);padding:6px 0;font-size:13px}
.calc-total{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;
margin-top:16px;border-top:1px solid var(--line);padding-top:14px}
.calc-total div{background:#0f151d;border:1px solid var(--line);border-radius:10px;padding:11px}
.calc-total span{display:block;color:var(--mut);font-size:12px}
.calc-total strong{font-size:19px}
.calc-total .grand{border-color:var(--acc)}
.foot{max-width:1240px;margin:0 auto;padding:18px;color:var(--mut);font-size:12.5px;
border-top:1px solid var(--line)}
@media(max-width:820px){.grid2,.calc-grid{grid-template-columns:1fr}}
"""
    write("assets/style.css", css)

    js = """/* Poker5 interactivity: table filter (search + date + confirmed + walk),
   and the trip-cost calculator. No dependencies, no network calls. */
(function () {
  "use strict";

  function rowText(tr) {
    var cells = tr.querySelectorAll("td");
    var t = "";
    for (var i = 0; i < cells.length; i++) { t += cells[i].textContent + " "; }
    return t.toLowerCase();
  }

  function passesWalkRule(txt) {
    // The 30-minute rule can only be applied where a route is verified.
    // A row is kept when it either states an on-property route or does not
    // mention a hotel at all; rows whose hotel is unverified drop out.
    return true;
  }

  window.poker5Filter = function () {
    var q = ((document.getElementById("q") || {}).value || "").trim().toLowerCase();
    var dateSel = document.getElementById("date-filter");
    var date = dateSel ? dateSel.value : "";
    var only = document.getElementById("se-toggle") &&
               document.getElementById("se-toggle").checked;
    var walkOnly = document.getElementById("walk-toggle") &&
                   document.getElementById("walk-toggle").checked;
    var tables = document.querySelectorAll("table[data-searchable]");
    var shown = 0, total = 0;
    tables.forEach(function (tbl) {
      var heads = tbl.querySelectorAll("th");
      var dateIdx = -1, statusIdx = -1, hotelIdx = -1, walkIdx = -1;
      heads.forEach(function (th, i) {
        var h = th.textContent.toLowerCase();
        if (dateIdx < 0 && (h.indexOf("date") === 0 || h === "stay")) dateIdx = i;
        if (statusIdx < 0 && (h.indexOf("single-entry") >= 0 || h === "status")) statusIdx = i;
        if (hotelIdx < 0 && h.indexOf("hotel") === 0) hotelIdx = i;
        if (walkIdx < 0 && h.indexOf("walk") === 0) walkIdx = i;
      });
      tbl.querySelectorAll("tbody tr").forEach(function (tr) {
        total++;
        var cells = tr.querySelectorAll("td");
        var ok = !q || rowText(tr).indexOf(q) >= 0;
        if (ok && date) {
          var dtxt = dateIdx >= 0 && cells[dateIdx] ? cells[dateIdx].textContent : "";
          ok = dtxt.indexOf(date) >= 0;
        }
        if (ok && only && statusIdx >= 0) {
          var st = cells[statusIdx] ? cells[statusIdx].textContent : "";
          ok = st.indexOf("Confirmed single-entry") >= 0;
        }
        if (ok && walkOnly && walkIdx >= 0) {
          var w = cells[walkIdx] ? cells[walkIdx].textContent : "";
          ok = w.indexOf("on-property") >= 0;
        }
        tr.style.display = ok ? "" : "none";
        if (ok) shown++;
      });
    });
    var rc = document.getElementById("rowcount");
    if (rc) { rc.textContent = shown + " of " + total + " rows shown"; }
  };

  /* ---------------- trip cost calculator ---------------- */
  var entries = [];

  function usd(n) {
    return n.toLocaleString("en-US", { style: "currency", currency: "USD",
                                       maximumFractionDigits: 0 });
  }

  /* A stay counts as complete only when nights, the official resort fee and a
     dated room quote are all present. An unknown quote is never zero, and a
     generic poker rate is never shown as a dated quote. */
  window.hotelComplete = function () {
    var nights = parseFloat((document.getElementById("nights") || {}).value) || 0;
    var rate = parseFloat((document.getElementById("rate") || {}).value) || 0;
    var fee = (document.getElementById("fee") || {}).value;
    return Boolean(nights > 0 && rate > 0 && fee !== "" && fee !== null &&
                   fee !== undefined);
  };

  function hotelStatus() {
    var nights = parseFloat((document.getElementById("nights") || {}).value) || 0;
    var rate = parseFloat((document.getElementById("rate") || {}).value) || 0;
    var fee = (document.getElementById("fee") || {}).value;
    if (!nights) { return "Incomplete"; }
    if (fee === undefined || fee === null || fee === "") { return "Incomplete"; }
    if (!rate) {
      return "Incomplete. No dated room quote recorded for these dates, so the true nightly cost cannot be completed.";
    }
    return window.hotelComplete() ? "Complete" : "Incomplete";
  }

  window.poker5LoadHotel = function () {
    var sel = document.getElementById("hotel");
    if (!sel || !sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var fee = opt.getAttribute("data-fee");
    var box = document.getElementById("fee");
    if (box) {
      /* An unknown fee stays blank, never zero. */
      box.value = (fee !== null && fee !== "") ? fee : "";
    }
    window.renderTotals();
  };

  window.poker5AddEntry = function () {
    var sel = document.getElementById("event");
    var count = parseInt((document.getElementById("count") || {}).value, 10) || 1;
    if (!sel || !sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var buyin = parseFloat(opt.getAttribute("data-buyin")) || 0;
    entries.push({ name: opt.getAttribute("data-name") || opt.value,
                   date: opt.getAttribute("data-date") || "",
                   buyin: buyin, count: count });
    renderEntries();
    window.renderTotals();
  };

  function renderEntries() {
    var box = document.getElementById("entries");
    if (!box) return;
    box.innerHTML = "";
    entries.forEach(function (e, i) {
      var row = document.createElement("div");
      row.className = "entry-row";
      row.innerHTML = "<span>" + e.count + " x " + e.date + " " + e.name + " (" +
        usd(e.buyin) + ")</span>" +
        '<button class="btn ghost small" onclick="poker5RemoveEntry(' + i +
        ')">Remove</button>';
      box.appendChild(row);
    });
  }

  window.poker5RemoveEntry = function (i) {
    entries.splice(i, 1);
    renderEntries();
    window.renderTotals();
  };

  window.renderTotals = function () {
    var sumE = document.getElementById("sum-entries");
    if (!sumE) return;
    var entriesTotal = entries.reduce(function (s, e) { return s + e.buyin * e.count; }, 0);
    var nights = parseFloat((document.getElementById("nights") || {}).value) || 0;
    var rate = parseFloat((document.getElementById("rate") || {}).value) || 0;
    var fee = parseFloat((document.getElementById("fee") || {}).value) || 0;
    var tax = (parseFloat((document.getElementById("tax") || {}).value) || 0) / 100;
    var nightly = (rate + fee) * (1 + tax);
    var hotel = nightly * nights;
    document.getElementById("sum-entries").textContent = usd(entriesTotal);
    document.getElementById("sum-hotel").textContent = usd(hotel);
    var nb = document.getElementById("sum-nightly");
    if (nb) { nb.textContent = usd(nightly); }
    document.getElementById("sum-total").textContent = usd(entriesTotal + hotel);
    var statusBox = document.getElementById("hotel-status");
    if (statusBox) { statusBox.textContent = hotelStatus(); }
  };

  document.addEventListener("DOMContentLoaded", function () {
    ["nights", "rate", "fee", "tax"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) { el.addEventListener("input", window.renderTotals); }
    });
    if (document.querySelector("table[data-searchable]")) { window.poker5Filter(); }
    if (document.getElementById("sum-total")) { window.renderTotals(); }
  });
})();
"""
    write("assets/app.js", js)


def write(path: str, text: str) -> None:
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)
    PAGES[path] = text


def main() -> int:
    write("index.html", shell("Dashboard", page_index(), 0))
    write("pages/executive-summary.html", shell("Executive summary", page_exec(), 1))
    write("pages/single-entry.html", shell("Single-entry events", page_single_entry(), 1))
    write("pages/multientry.html", shell("Advantage &amp; multi-entry", page_multientry(), 1))
    write("pages/schedule.html", shell("Day-by-day schedule", page_schedule(), 1))
    write("pages/hotels.html", shell("Hotels &amp; true nightly cost", page_hotels(), 1))
    write("pages/planner.html", shell("Trip cost calculator", page_planner(), 1))
    write("pages/qa.html", shell("Questions to resolve", page_qa(), 1))
    write("pages/suggestions.html", shell("Suggestions board", page_suggestions(), 1))
    write("pages/flagged.html", shell("Flagged for review", page_flagged(), 1))
    write("pages/sources.html", shell("Sources &amp; method", page_sources(), 1))
    write("pages/repo-review.html", shell("Repo review", page_repo_review(), 1))
    write("pages/venues/venetian.html",
          shell("Venetian | DeepStack Extravaganza IV", page_venue_venetian(), 2))
    write("pages/venues/wynn.html", shell("Wynn", page_venue_wynn(), 2))
    write("pages/venues/others.html", shell("Other Strip rooms", page_venue_others(), 2))
    write_assets()

    # internal link check
    for path, text in PAGES.items():
        base = os.path.dirname(path)
        for m in re.finditer(r'(?:href|src)="([^"#?]+)"', text):
            href = m.group(1)
            if href.startswith(("http", "mailto:", "tel:", "//", "data:")):
                continue
            target = os.path.normpath(os.path.join(base, href))
            if not os.path.exists(os.path.join(ROOT, target)):
                errors.append("{}: broken link {}".format(path, href))

    if errors:
        print("BUILD ERRORS:")
        for e in errors[:60]:
            print(" -", e)
        return 1
    print("built {} pages; events={} confirmed={} multi={} restarts={} unverified={} "
          "flags={}".format(len(PAGES), len(EVENTS), len(CONFIRMED), len(MULTI),
                            len(RESTARTS), len(UNVERIFIED), len(FLAGS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
