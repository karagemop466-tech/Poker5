#!/usr/bin/env python3
"""Build the afff1fc9 Las Vegas poker site (static HTML) from data/ files.

Inputs  : site-afff1fc9/data/events.csv, sources.json, hotels.json, monitor_state.json
Outputs : site-afff1fc9/*.html, site-afff1fc9/assets/*
Nothing is invented: every value comes from a data file that cites an official source.
"""
import csv
import datetime as dt
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site-afff1fc9")
DATA = os.path.join(SITE, "data")

VEN_SCHED = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
WYNN_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WPT_TERMS = "https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf"
VEN_STRUCT = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{}.pdf"

# Structure sheets actually opened and read this session (number -> house fee text, per sheet).
OPENED_SHEETS = {
    1: "$40 of $200 (rake + staff)",
    7: "$90 of $600 (rake + staff)",
    10: "$60 of $300 (rake + staff)",
    15: "$50 of $300 (rake + staff)",
    17: "$90 of $600 (rake + staff)",
    19: "$20 of $100 (rake + staff)",
}

STATUS = {
    "S": "Not confirmed: sheet silent on re-entry / single entry",
    "N": "Not checked: structure sheet not opened",
    "F": "Multi-flight: not single-entry (see sheet)",
    "M": "Multi-entry: unlimited re-entry (WPT terms)",
}

NAV = [
    ("index.html", "Home"),
    ("tournaments.html", "Tournaments"),
    ("venue-venetian.html", "Venetian"),
    ("venue-wynn.html", "Wynn / WPT"),
    ("hotels.html", "Hotels & rates"),
    ("calculator.html", "Trip calculator"),
    ("analysis.html", "Analysis"),
    ("questions.html", "Questions"),
    ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
]


def esc(x):
    return html.escape("" if x is None else str(x), quote=True)


def money(v):
    return "" if v in (None, "") else f"${int(v):,}"


def load_json(name, default):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


SOURCES = load_json("sources.json", {"retrieved": "", "sources": []})
HOTELS = load_json("hotels.json", {"hotels": [], "rate_log": [], "tax_rate_percent": None})
MON = load_json("monitor_state.json", {"checks": {}, "last_run": None})
SRC = {s["id"]: s for s in SOURCES["sources"]}
RETRIEVED = SOURCES.get("retrieved", "")


def last_checked(src_id):
    chk = MON.get("checks", {}).get(src_id, {})
    return chk.get("last_checked") or RETRIEVED


def load_events():
    rows = []
    with open(os.path.join(DATA, "events.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        for i, r in enumerate(reader, 1):
            r["_i"] = i
            rows.append(r)
    # Repeated Venetian event numbers across dates = multi-flight / restart structure.
    dates_by_event = {}
    for r in rows:
        if r["venue"] == "venetian" and r["event_no"]:
            dates_by_event.setdefault(r["event_no"], set()).add(r["date"])
    out = []
    for r in rows:
        code = r["code"]
        if r["venue"] == "venetian" and r["event_no"] and len(dates_by_event[r["event_no"]]) > 1:
            code = "F"
        d = dt.date.fromisoformat(r["date"])
        name = r["name"]
        note = r["note"]
        fmt = "Standard"
        if "Bounty" in name or "Bounty" in note or "PKO" in name or "Knock-Out" in name:
            fmt = "Bounty (labelled separately)"
        elif "Satellite" in name or "Satellite" in note:
            fmt = "Satellite (seat prize, labelled separately)"
        buy = int(r["buy_in"]) if r["buy_in"] else None
        gtd = int(r["guarantee"]) if r["guarantee"] else None
        ratio = f"{gtd / buy:,.1f}" if (gtd and buy) else ""
        sources = []
        if r["venue"] == "venetian":
            sources.append(("Schedule", VEN_SCHED, "ven-dse-schedule"))
            if r["structure"]:
                sn = int(r["structure"])
                sources.append((f"Structure sheet #{sn}", VEN_STRUCT.format(sn), None))
            fee = OPENED_SHEETS.get(int(r["structure"])) if r["structure"] else None
        else:
            sources.append(("Schedule (PDF)", WYNN_SCHED, "wynn-wpt-schedule"))
            if code == "M":
                sources.append(("WPT terms (PDF)", WPT_TERMS, "wpt-terms"))
            fee = None
            if code == "M" and buy == 600:
                fee = "$90 of $600 ($65 fee + $25 staff; prize $510)"
            elif code == "M" and buy == 400:
                fee = "$63 of $400 ($45 fee + $18 staff; prize $337)"
        src_id = "ven-dse-schedule" if r["venue"] == "venetian" else "wynn-wpt-schedule"
        out.append({
            "id": f"{r['venue']}-{r['_i']:03d}",
            "venue": r["venue"],
            "venue_label": "The Venetian" if r["venue"] == "venetian" else "Wynn / WPT",
            "date": r["date"],
            "date_label": d.strftime("%a %b %d"),
            "time": r["time"],
            "event_no": r["event_no"],
            "name": name,
            "format": fmt,
            "buy_in": buy,
            "guarantee": gtd,
            "ratio": ratio,
            "code": code,
            "status": STATUS[code],
            "confirmed": "No",
            "group": "separate" if code in ("F", "M") else "candidate",
            "house_fee": fee or "",
            "sources": sources,
            "last_checked": last_checked(src_id),
            "note": note,
        })
    return out


EVENTS = load_events()
DATES = sorted({e["date"] for e in EVENTS})


def fmt_date_opts(rows):
    dates = sorted({e["date"] for e in rows})
    opts = ['<option value="">All dates</option>']
    for d in dates:
        lab = dt.date.fromisoformat(d).strftime("%a %b %d, %Y")
        opts.append(f'<option value="{d}">{lab}</option>')
    return "".join(opts)


def event_table(rows, table_id, show_venue=True):
    if not rows:
        return '<p class="muted">No rows.</p>'
    head = ["Date", "Time", "Event #", "Event", "Format", "Buy-in", "Guarantee",
            "Guarantee ÷ buy-in (descriptive, not a forecast)", "Entry-rule status",
            "Confirmed single-entry", "House fee (per sheet)", "Official source(s)", "Last checked"]
    if show_venue:
        head.insert(0, "Venue")
    th = "".join(f"<th>{esc(h)}</th>" for h in head)
    body = []
    for e in rows:
        links = " · ".join(f'<a href="{esc(u)}" rel="noopener" target="_blank">{esc(lab)}</a>' for lab, u, _ in e["sources"])
        cells = []
        if show_venue:
            cells.append(f"<td>{esc(e['venue_label'])}</td>")
        cells += [
            f"<td>{esc(e['date_label'])}, 2026</td>",
            f"<td>{esc(e['time'])}</td>",
            f"<td>{esc(e['event_no'])}</td>",
            f"<td>{esc(e['name'])}</td>",
            f"<td>{esc(e['format'])}</td>",
            f"<td class='num'>{money(e['buy_in'])}</td>",
            f"<td class='num'>{money(e['guarantee'])}</td>",
            f"<td class='num'>{esc(e['ratio'])}</td>",
            f"<td><span class='tag tag-{e['code'].lower()}'>{esc(e['status'])}</span></td>",
            f"<td><span class='tag tag-no'>No</span></td>",
            f"<td>{esc(e['house_fee'])}</td>",
            f"<td class='links'>{links}</td>",
            f"<td>{esc(e['last_checked'])}</td>",
        ]
        body.append(f'<tr data-date="{e["date"]}" data-confirmed="0" data-search="{esc((e["venue_label"]+" "+e["name"]+" "+e["event_no"]+" "+e["format"]).lower())}">' + "".join(cells) + "</tr>")
    return (f'<div class="table-wrap"><table class="data" id="{table_id}"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def controls(table_id, rows, toggle=True):
    t = ""
    if toggle:
        t = (f'<label class="toggle"><input type="checkbox" data-toggle-confirmed="{table_id}"> '
             f'Show only confirmed single-entry events (currently 0 of {len(rows)} rows)</label>')
    return (f'<div class="controls">'
            f'<input type="search" class="search" placeholder="Search this table…" data-search-target="{table_id}" aria-label="Search table">'
            f'<select data-date-target="{table_id}" aria-label="Filter by date">{fmt_date_opts(rows)}</select>'
            f'{t}</div>')


def layout(title, active, body, extra_head=""):
    nav = "".join(
        f'<a href="{href}" class="{"on" if href == active else ""}">{esc(label)}</a>' for href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Strip poker planner</title>
<link rel="stylesheet" href="assets/style.css">
{extra_head}
</head>
<body>
<header class="top">
  <div class="brand"><a href="index.html">Strip Poker Planner</a><span class="snap">Snapshot 2026-11-17 · official sources only</span></div>
  <nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer>
  <p>Every table row links to an official source. Blank cells are unverified and are never filled in.
  Data: <code>site-afff1fc9/data/</code>. Build: <code>scripts/build_afff1fc9.py</code>. Not financial, legal or booking advice.</p>
</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""


def write(name, content):
    with open(os.path.join(SITE, name), "w", encoding="utf-8") as f:
        f.write(content)


def counts():
    c = {"all": len(EVENTS), "venetian": 0, "wynn": 0, "S": 0, "N": 0, "F": 0, "M": 0, "confirmed": 0,
         "priced": 0}
    for e in EVENTS:
        c[e["venue"]] += 1
        c[e["code"]] += 1
        if e["buy_in"] and e["guarantee"]:
            c["priced"] += 1
    c["sheets"] = len(OPENED_SHEETS) + 1  # plus WPT terms (opened); see sources
    c["unique_sheets_venetian"] = len({e["sources"][1][1] for e in EVENTS if e["venue"] == "venetian" and len(e["sources"]) > 1})
    return c


C = counts()
TAX = HOTELS.get("tax_rate_percent") or 13.38
VEN_HOTEL = next((h for h in HOTELS["hotels"] if h["id"] == "venetian"), None)
WYNN_HOTEL = next((h for h in HOTELS["hotels"] if h["id"] == "wynn"), None)
CHECKED_MON = MON.get("last_run") or "not yet run (scheduled daily)"


# ---------- pages ----------

def page_index():
    cards = [
        ("tournaments.html", "Tournaments", f"{C['all']} official schedule rows across both venues, with single-entry status."),
        ("venue-venetian.html", "The Venetian", f"{C['venetian']} DeepStack Extravaganza IV rows; 6 structure sheets read."),
        ("venue-wynn.html", "Wynn / WPT", f"{C['wynn']} WPT World Championship schedule rows; re-entry terms checked for 3 event types."),
        ("hotels.html", "Hotels & rates", "Resort fee verified for the Venetian ($55 + tax). Rates and walking times: none verified."),
        ("calculator.html", "Trip calculator", "Entries × buy-ins + nights × true hotel cost (rate + fee + 13.38% tax)."),
        ("analysis.html", "Analysis", "Ranking gates, same-day start counts and why no ranking is shown yet."),
        ("questions.html", "Questions", "What must be answered before a decision can be made."),
        ("suggestions.html", "Suggestions", "Options for you to choose from. Nothing here is implemented yet."),
        ("flagged.html", "Flagged for Review", "Irregularities and unverified items, with source links."),
        ("sources.html", "Sources", "Every official URL used, the date it was read, and the monitoring state."),
    ]
    card_html = "".join(
        f'<a class="card" href="{h}"><h3>{esc(t)}</h3><p>{esc(d)}</p></a>' for h, t, d in cards)
    body = f"""
<section class="hero">
  <h1>Las Vegas Strip poker: verified schedule and trip planner</h1>
  <p class="lede">Single-entry tournaments, true hotel cost, and a trip calculator. Every value comes from an official source
  or is left blank and flagged. <strong>No event is confirmed single-entry yet</strong>, so no ranking is shown.</p>
  <p class="status">Snapshot read {esc(RETRIEVED)} · Last monitor run: {esc(CHECKED_MON)}</p>
</section>

<section class="kpis">
  <div class="kpi"><span>{C['all']}</span>official schedule rows</div>
  <div class="kpi"><span>{C['S'] + C['N']}</span>candidate rows (rule not confirmed multi-entry)</div>
  <div class="kpi"><span>{C['F'] + C['M']}</span>multi-entry / multi-flight rows (kept separate)</div>
  <div class="kpi warn"><span>0</span>confirmed single-entry events</div>
  <div class="kpi"><span>{C['priced']}</span>rows with buy-in and guarantee (official)</div>
  <div class="kpi warn"><span>1 of 2</span>hotels with resort fee verified</div>
</section>

<section>
  <h2>Executive summary</h2>
  <ol class="findings">
    <li><strong>Single-entry gate: nothing passes.</strong> The official Venetian schedule repeats event numbers across flights (multi-flight, {C['F']} rows). The rest of the Venetian rows read by us are silent on re-entry, which is not the same as single-entry. WPT Wynn terms for the $600 NLH ($400K), $600 TORSE and $400 PLO allow unlimited re-entry until level 9.</li>
    <li><strong>Ranking is withheld.</strong> The brief ranks only after the total entry fee and guarantee are confirmed and the event passes single-entry. Guarantee ÷ buy-in is shown as a descriptive ratio only.</li>
    <li><strong>Hotels.</strong> The Venetian resort fee is verified: $55 plus tax per night (official page). The Wynn fee could not be verified. Nightly rates and walking times were not retrieved from official sources, so they are blank.</li>
    <li><strong>Tax.</strong> The Clark County schedule sets 13.38% for a resort hotel in the primary gaming corridor. That text is the 2017 ordinance and must be reconfirmed. Whether the Venetian lies inside the corridor is not checked against the map.</li>
    <li><strong>Calculator.</strong> Enter entries, buy-ins, nights and your own rates. It applies tax to rate + mandatory resort fee, which the ordinance's 'rent' definition supports (see Flagged F7).</li>
    <li><strong>Monitoring.</strong> A scheduled job re-reads the official URLs each morning, stores a hash, and flags any change. It has not yet run on GitHub.</li>
  </ol>
</section>

<section>
  <h2>Pages</h2>
  <div class="cards">{card_html}</div>
</section>
"""
    return layout("Home", "index.html", body)


def page_tournaments():
    cand = [e for e in EVENTS if e["group"] == "candidate"]
    sep = [e for e in EVENTS if e["group"] == "separate"]
    body = f"""
<section>
  <h1>Tournaments</h1>
  <p class="lede">Official schedule rows for The Venetian (DeepStack Extravaganza IV) and Wynn (WPT World Championship).
  Table A holds events whose re-entry rule is not confirmed as multi-entry. Table B holds multi-entry and multi-flight events,
  which are kept separate as the brief requires. <strong>No row is confirmed single-entry</strong>, so the toggle shows none.</p>
  <div class="legend">
    <span class="tag tag-s">S: {esc(STATUS['S'])}</span>
    <span class="tag tag-n">N: {esc(STATUS['N'])}</span>
    <span class="tag tag-f">F: {esc(STATUS['F'])}</span>
    <span class="tag tag-m">M: {esc(STATUS['M'])}</span>
  </div>
</section>
<section>
  <h2>Table A: single-entry candidates (not confirmed)</h2>
  {controls('tblA', cand)}
  {event_table(cand, 'tblA')}
</section>
<section>
  <h2>Table B: multi-entry or multi-flight (separate, not single-entry)</h2>
  {controls('tblB', sep)}
  {event_table(sep, 'tblB')}
</section>
"""
    return layout("Tournaments", "tournaments.html", body)


def venue_page(venue):
    rows = [e for e in EVENTS if e["venue"] == venue]
    cand = [e for e in rows if e["group"] == "candidate"]
    sep = [e for e in rows if e["group"] == "separate"]
    if venue == "venetian":
        title, active = "The Venetian", "venue-venetian.html"
        intro = ("DeepStack Extravaganza IV, Nov 16 – Dec 23, 2026, per the official Venetian schedule. "
                 "The Venetian poker room is on the Palazzo level 2 per the source; walking time to it is not verified.")
        hotel = VEN_HOTEL
        vid = "venetian"
    else:
        title, active = "Wynn / WPT", "venue-wynn.html"
        intro = ("WPT World Championship series, Nov 27 – Dec 21, 2026, per the official Wynn schedule PDF. "
                 "Continuation rows (Day 2/3/4 and final tables) are omitted because they carry no entry fee.")
        hotel = WYNN_HOTEL
        vid = "wynn"
    hot = ""
    if hotel:
        hot = f"""<div class="card-static"><h3>Hotel on this venue page: {esc(hotel['name'])}</h3>
        <p>Resort fee: {esc(hotel['resort_fee_status'])}</p>
        <p>Walking time to poker room: {esc(hotel['walk_status'])}</p>
        <p>Rate: {esc(hotel['rate_status'])}</p>
        <p><a href="hotels.html">Full hotel and rate page →</a></p></div>"""
    body = f"""
<section>
  <h1>{esc(title)}</h1>
  <p class="lede">{esc(intro)}</p>
  {hot}
</section>
<section>
  <h2>Candidates (single-entry not confirmed)</h2>
  {controls(vid+'A', cand)}
  {event_table(cand, vid+'A', show_venue=False)}
</section>
<section>
  <h2>Multi-entry / multi-flight (separate)</h2>
  {controls(vid+'B', sep)}
  {event_table(sep, vid+'B', show_venue=False)}
</section>
"""
    return layout(title, active, body)


def page_hotels():
    rows = []
    for h in HOTELS["hotels"]:
        fee = h.get("resort_fee_per_night")
        fee_txt = f"${fee} plus tax per night" if fee is not None else "Not verified"
        src = SRC.get(h.get("resort_fee_source"), {})
        link = f'<a href="{esc(src.get("url"))}" target="_blank" rel="noopener">{esc(src.get("publisher", "source"))}</a>' if src else ""
        rows.append(f"""<tr>
<td>{esc(h['name'])}</td>
<td class="num">{esc(fee_txt)}</td>
<td>{esc(h['resort_fee_status'])}</td>
<td class="num">{TAX:.2f}%</td>
<td class="num">blank: needs official rate</td>
<td>{esc(h['walk_status'])}</td>
<td>{link}</td>
<td>{esc(last_checked(h.get('resort_fee_source', '')) if h.get('resort_fee_source') else RETRIEVED)}</td>
</tr>""")
    log_head = ("<tr><th>Captured</th><th>Hotel</th><th>Check-in / out</th><th>Occupancy</th><th>Nightly average</th>"
                "<th>Checkout total</th><th>Resort fee</th><th>Tax</th><th>Parking</th><th>Cancellation deadline</th>"
                "<th>Rate timestamp</th><th>Source</th></tr>")
    body = f"""
<section>
  <h1>Hotels &amp; rates</h1>
  <p class="lede">Only official values are shown. The Venetian resort fee is verified. Rates, walking times and the Wynn fee
  are blank because no official value was retrieved in this session. Tax {TAX:.2f}% comes from the Clark County ordinance
  (see Flagged F6).</p>
  <h2>Resort fee and tax</h2>
  <div class="table-wrap"><table class="data" id="tblHotels"><thead><tr>
    <th>Hotel</th><th>Resort fee</th><th>Status</th><th>Tax rate</th><th>True cost / night</th>
    <th>Walking time to poker room (30-min limit)</th><th>Source</th><th>Last checked</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table></div>
  <p class="muted">True cost / night = (nightly rate + resort fee) × (1 + {TAX:.2f}%). Shown blank until an official nightly rate is entered in the calculator or captured below.</p>
</section>
<section>
  <h2>Dated rate log</h2>
  <p>Rates are kept as a dated log, not a single value. The log is empty: no official rate was captured in this session.
  Each future entry must record check-in/out, occupancy, nightly average, checkout total, resort fee, tax, parking,
  cancellation deadline, rate timestamp and the official booking page.</p>
  <div class="table-wrap"><table class="data"><thead>{log_head}</thead>
  <tbody><tr><td colspan="12" class="muted">No rows. Nothing has been captured from an official booking page.</td></tr></tbody></table></div>
</section>
"""
    return layout("Hotels & rates", "hotels.html", body)


def page_calculator():
    ev = [{"id": e["id"], "label": f"{e['venue_label']} · {e['date_label']} {e['time']} · {e['name']}",
           "buy_in": e["buy_in"], "code": e["code"], "venue": e["venue"]} for e in EVENTS if e["buy_in"]]
    ev_json = json.dumps(ev).replace("</", "<\\/")
    fee_default = VEN_HOTEL["resort_fee_per_night"] if VEN_HOTEL else 55
    body = f"""
<section>
  <h1>Trip cost calculator</h1>
  <p class="lede">Estimated cost = entries × buy-ins + nights × true hotel cost. Enter your own numbers.
  Nothing is pre-filled as a trip plan: trip dates and budget have not been provided.</p>
  <p class="muted">True hotel cost per night = (nightly rate + resort fee) × (1 + tax). The Clark County ordinance defines
  'rent' to include mandatory charges, so the fee is taxed too (Flagged F7). The 13.38% rate is from a 2017 ordinance (Flagged F6).</p>
</section>
<section class="calc">
  <div class="calc-grid">
    <fieldset>
      <legend>1. Tournament entries</legend>
      <label>Event <select id="evSel">{''.join(f'<option value="{esc(x["id"])}">{esc(x["label"])} · ${x["buy_in"]:,}</option>' for x in ev)}</select></label>
      <label>Number of entries <input type="number" id="evQty" min="0" step="1" value="1"></label>
      <button type="button" id="evAdd">Add entry line</button>
      <table class="data small" id="evList"><thead><tr><th>Event</th><th>Entries</th><th>Buy-in</th><th>Subtotal</th><th></th></tr></thead><tbody></tbody></table>
      <p>Entry total: <strong id="entryTotal">$0</strong></p>
      <p class="muted">Buy-ins shown are the schedule buy-ins. House fees are included in the buy-in per the structure sheets.</p>
    </fieldset>
    <fieldset>
      <legend>2. Hotel (your official quote)</legend>
      <label>Nights <input type="number" id="nights" min="0" step="1" placeholder="enter nights"></label>
      <label>Nightly room rate, pre-tax, pre-fee ($) <input type="number" id="rate" min="0" step="0.01" placeholder="from official booking page"></label>
      <label>Resort fee per night ($) <input type="number" id="fee" min="0" step="0.01" value="{fee_default}"></label>
      <p class="muted">Default $55 is the Venetian's verified fee. For Wynn, enter the fee from the booking page (not verified here).</p>
      <label>Tax rate (%) <input type="number" id="tax" min="0" step="0.01" value="{TAX}"></label>
      <p>True cost per night: <strong id="trueNight">enter rate</strong></p>
      <p>Hotel total: <strong id="hotelTotal">enter nights and rate</strong></p>
    </fieldset>
  </div>
  <div class="result">
    <h2>Estimated trip total</h2>
    <p><span id="grand">$0</span> = entries <span id="entryTotal2">$0</span> + hotel <span id="hotelTotal2">$0</span></p>
    <p class="muted">Excludes flights, parking, meals, cancellation charges and any tax the hotel charges outside the rate schedule.
    Parking and cancellation deadline are not verified (see Questions).</p>
  </div>
</section>
<script type="application/json" id="events-data">{ev_json}</script>
"""
    return layout("Trip cost calculator", "calculator.html", body)


def page_analysis():
    per_day = {}
    for e in EVENTS:
        per_day.setdefault(e["date"], {"venetian": 0, "wynn": 0})
        per_day[e["date"]][e["venue"]] += 1
    rows = "".join(
        f"<tr><td>{esc(dt.date.fromisoformat(d).strftime('%a %b %d, %Y'))}</td><td class='num'>{v['venetian']}</td>"
        f"<td class='num'>{v['wynn']}</td><td>Primary event and fallback: <em>not set</em>. Finish times unverified.</td></tr>"
        for d, v in sorted(per_day.items()))
    body = f"""
<section>
  <h1>Analysis</h1>
  <p class="lede">The brief asks for a ranking only after three gates are passed. Gate status is shown below. Nothing is ranked.</p>
  <table class="data"><thead><tr><th>Gate</th><th>Requirement</th><th>Status</th><th>Result</th></tr></thead><tbody>
    <tr><td>1</td><td>Single-entry confirmed from official text (explicit single entry, or 'no re-entry' in the official rule)</td>
        <td><span class="tag tag-s">0 of {len(EVENTS)} pass</span></td><td>Silent sheets and multi-entry terms do not pass.</td></tr>
    <tr><td>2</td><td>Total entry fee and guarantee confirmed from official source</td>
        <td><span class="tag tag-n">{C['priced']} rows have both</span></td><td>Applies only to rows that also pass gate 1.</td></tr>
    <tr><td>3</td><td>Start time, late-registration cutoff and finish time (duration) verified, so overlap can be checked</td>
        <td><span class="tag tag-n">not run</span></td><td>Finish times are not published. Late-reg cutoffs appear only on 6 opened sheets.</td></tr>
  </tbody></table>
  <h2>Ranking</h2>
  <p>0 events have passed all gates, so the ranking table is empty by design.</p>
  <h2>Ratio definition (descriptive only)</h2>
  <p>Guarantee ÷ buy-in is a descriptive ratio of advertised money to entry price. It is not a forecast of prize value,
  of field size, or of expected return. Bounty and satellite formats are labelled separately in the tables and should not be
  compared with standard events on this ratio.</p>
  <h2>Same-day starts (for planning; overlap not checked)</h2>
  <div class="table-wrap"><table class="data"><thead><tr><th>Date</th><th>Venetian starts</th><th>Wynn starts</th><th>Plan</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
  <h2>Hotel walking route</h2>
  <p>No official walking time was retrieved. Walking times are blank, so the 30-minute limit cannot be applied yet.</p>
</section>
"""
    return layout("Analysis", "analysis.html", body)


QUESTIONS = [
    ("Q1", "Which dates is the trip? Number of nights?", "Open", "Needed before any hotel or event combination can be costed. Not provided by user."),
    ("Q2", "What is the nightly budget and the quality floor (star rating, room type)?", "Open", "Needed to filter hotels. Not provided."),
    ("Q3", "Do the official structure sheets for the remaining Venetian events state single entry or no re-entry?", "Open", "This session read 6 of the unique Venetian sheets. Silence is not a confirmation."),
    ("Q4", "Does the Venetian's 'bag for Day 2 may not play a subsequent flight' rule mean a player can enter multiple flights before bagging?", "Answered for Event 01 (multi-flight text)", "Structure sheet #10, rule 08."),
    ("Q5", "What re-entry rule applies to the WPT World Championship events ($10,400) and the other Wynn events not reviewed?", "Open", "WPT terms were read only up to the $600 NLH, TORSE and $400 PLO sections."),
    ("Q6", "What is the Wynn resort fee?", "Open", "Official Wynn resort-fee URL returned an error page on 2026-11-17."),
    ("Q7", "What is the official nightly rate for the chosen dates at each hotel? Is the rate timestamp captured?", "Open", "No official booking page was retrieved. Rates must be captured with timestamp."),
    ("Q8", "What is the official walking time from each hotel to the poker room?", "Open", "No official source found for walking time. Google/Apple Maps are not official sources for this purpose."),
    ("Q9", "What are the finish times and late-registration cutoffs for each candidate event?", "Partly answered", "Late-reg cutoffs appear on 6 opened sheets. Finish times are not published."),
    ("Q10", "Is 13.38% the current 2026 rate for the Venetian? Is the Venetian inside the primary gaming corridor on the official map?", "Open", "Source is the 2017 ordinance text."),
    ("Q11", "Is the resort fee taxed? Confirm with the hotel's folio or Clark County.", "Open", "Ordinance 4.08.005(17)(a)(viii) includes mandatory charges in 'rent'. Calculator follows that reading."),
    ("Q12", "Parking charges and cancellation deadline for each hotel?", "Open", "Not retrieved."),
    ("Q13", "Which other Strip poker rooms are in scope (Golden Nugget, Caesars, Bellagio, MGM Grand, ARIA, Planet Hollywood, Resorts World, South Point)?", "Open", "Only Venetian and Wynn were researched on this site."),
]

SUGGESTIONS = [
    ("S1", "Scope: Venetian + Wynn only (now) vs add all Strip rooms", "Recommend: decide scope first; each room adds its own schedule and sheets."),
    ("S2", "Single-entry rule: strict (explicit official text only) vs inferred (silence = single entry)", "Recommend strict. Silence is not confirmation, so the strict rule keeps the toggle honest."),
    ("S3", "Read every official structure sheet (about 50 unique Venetian sheets, plus WPT event terms)", "Recommend: finish the reading in a follow-up task; the monitor can then flag sheet changes."),
    ("S4", "Rates: capture official booking-page rates each morning with timestamps (rate log) vs manual entry", "Recommend: scheduled capture, with a log, to keep the like-for-like comparison."),
    ("S5", "Walking times: official address-based routing (not verified) vs use of Google/Apple Maps (third-party)", "Decision needed: the brief says official sources only. Maps values can be shown but must be flagged as third-party."),
    ("S6", "Tax basis in calculator: tax on rate + mandatory fee (current) vs tax on rate only", "Recommend current setting pending confirmation (Q11)."),
    ("S7", "Repo clean-up: several overlapping dashboards and planners on main (dashboard-*, site-*, planner-*, docs/, pages/)", "Decision needed: which one is the public site. Not changed here."),
    ("S8", "Link this site from the root landing page", "Not changed here (root index.html belongs to another session)."),
]

FLAGS = [
    ("F1", "Multi-flight events", "The Venetian schedule lists one event number across several dates (for example Event 01 on Nov 16–18 and Event 26 on Dec 3–6). Structure sheet #10 says a player who bags for Day 2 may not play a subsequent flight, which implies earlier flights can be entered. These rows are classed as multi-flight, not single-entry.", "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    ("F2", "Silence is not single-entry", "The structure sheets read (#1, #7, #15, #17, #19) state no re-entry rule and no single-entry rule. They are classed as 'not confirmed', not as single-entry.", VEN_STRUCT.format(1)),
    ("F3", "Only 6 of the unique Venetian sheets read", "Sheets #1, #7, #10, #15, #17 and #19 were read. The other sheets are listed as 'not checked'.", VEN_SCHED),
    ("F4", "WPT re-entry: unlimited", "WPT terms state unlimited re-entry for the $600 NLH ($400K guarantee), $600 TORSE and $400 PLO events, until level 9. Those rows are excluded from single-entry.", WPT_TERMS),
    ("F5", "Schedule order irregularity (Wynn)", "On the official Wynn PDF, the Dec 17 rows are printed after the Dec 18 rows. Rows here are sorted by date. The Ladies NLH row shows $1,100 while its footnote says the Ladies Championship entry is $11,100 with a discounted ladies entry. The row is kept as published and needs the structure sheet.", WYNN_SCHED),
    ("F6", "Tax rate source is a 2017 ordinance", "13.38% is the combined rate in the 2017 Clark County ordinance text for a resort hotel within the primary gaming corridor. The current rate was not re-confirmed. Whether the Venetian is inside the corridor is not checked against the ordinance map.", SRC["clark-tax"]["url"]),
    ("F7", "Resort-fee tax basis", "The ordinance's definition of 'rent' (4.08.005(17)(a)) includes charges that are mandatory. The calculator taxes rate + resort fee on that basis. Confirm with the hotel.", SRC["clark-tax"]["url"]),
    ("F8", "Wynn resort fee unverified", "https://www.wynnlasvegas.com/resort-fee returned a 'checked out' error page. No Wynn fee value is shown.", "https://www.wynnlasvegas.com/resort-fee"),
    ("F9", "No rates captured", "No official nightly rate or booking-page total was retrieved, so the rate log is empty and the true cost per night is blank.", VEN_SCHED),
    ("F10", "Walking times unverified", "No official source for hotel-to-poker-room walking time was retrieved. The 30-minute filter cannot be applied.", VEN_SCHED),
    ("F11", "Bounty and satellite formats", "Bounty events (for example $200 bounty, $8K guarantee, where the guarantee includes bounties) and satellites (which award seats, not cash) are labelled separately and should not be compared on the ratio alone.", VEN_STRUCT.format(1)),
    ("F12", "Prior sessions disagree on counts", "Other sessions on this repo record different Venetian single-entry counts (20, 30, 64) and different Bellagio fees. This site does not use those numbers. They are unreconciled and out of scope here.", "https://github.com/karagemop466-tech/Poker5/blob/main/COORDINATION.md"),
    ("F13", "Continuation rows omitted (Wynn)", "Day 2 / Day 3 / final-table rows on the Wynn PDF carry no entry fee and are omitted. One row ('Dec 5 No Limit Hold'em Day 2, $1,100, $5M') shows a buy-in on the continuation line and was not included.", WYNN_SCHED),
        ("F14", "Earlier note about committed bytecode not reproduced", "Another session (359e3f96) recorded a committed tools/__pycache__/*.pyc on main. On this branch (base f203df6) `git ls-files` finds no __pycache__ files, so the note is not reproduced. Not changed here.", "https://github.com/karagemop466-tech/Poker5/tree/main"),
]


def page_questions():
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(q)}</td><td><span class='tag tag-n'>{esc(s)}</span></td><td>{esc(n)}</td></tr>" for a, q, s, n in QUESTIONS)
    body = f"""
<section>
  <h1>Questions to answer before a decision</h1>
  <p class="lede">What is known and what is missing. Each open item needs an answer before a booking, a ranking or a
  payment is reasonable. Suggestions for finding the answers are on the Suggestions page.</p>
  <div class="table-wrap"><table class="data" id="tblQ"><thead><tr><th>#</th><th>Question</th><th>Status</th><th>Notes</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
</section>
"""
    return layout("Questions", "questions.html", body)


def page_suggestions():
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td><td><span class='tag tag-n'>Awaiting your choice</span></td></tr>" for a, b, c in SUGGESTIONS)
    body = f"""
<section>
  <h1>Suggestions for review</h1>
  <p class="lede">Choose a path before any change is made. Nothing on this list has been implemented.
  Reply with the ID(s) you want (for example "S2 strict, S4 scheduled capture").</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>#</th><th>Option</th><th>Recommendation</th><th>Decision</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
</section>
"""
    return layout("Suggestions", "suggestions.html", body)


def page_flagged():
    rows = "".join(
        f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td><td><a href='{esc(d)}' target='_blank' rel='noopener'>official link</a></td></tr>"
        for a, b, c, d in FLAGS)
    changed = [k for k, v in MON.get("checks", {}).items() if v.get("changed")]
    chg = ("<p>Changed since the last check: " + (", ".join(esc(x) for x in changed) if changed else "none recorded") + ".</p>")
    body = f"""
<section>
  <h1>Flagged for Review</h1>
  <p class="lede">Irregularities and unverified items, for your review after go-live. These do not block publication.
  Each item has the official link to check.</p>
  {chg}
  <div class="table-wrap"><table class="data"><thead><tr><th>#</th><th>Item</th><th>Detail</th><th>Source</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
</section>
"""
    return layout("Flagged for Review", "flagged.html", body)


def page_sources():
    rows = []
    for s in SOURCES["sources"]:
        chk = MON.get("checks", {}).get(s["id"], {})
        rows.append(f"""<tr><td>{esc(s['label'])}</td><td>{esc(s['publisher'])}</td>
<td><a href="{esc(s['url'])}" target="_blank" rel="noopener">{esc(s['url'])}</a></td>
<td>{esc(SOURCES['retrieved'])}</td><td>{'yes' if s.get('monitored') else 'no'}</td>
<td>{esc(chk.get('last_checked', 'not yet'))}</td><td>{'CHANGED' if chk.get('changed') else ('ok' if chk else 'pending')}</td>
<td>{esc(s.get('used_for', ''))}</td></tr>""")
    body = f"""
<section>
  <h1>Sources</h1>
  <p class="lede">Every URL used on this site, with the date it was read. Monitoring runs daily via GitHub Actions
  (<code>.github/workflows/afff1fc9-monitor.yml</code>). Last run: {esc(CHECKED_MON)}.</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Source</th><th>Publisher</th><th>URL</th><th>Read</th>
  <th>Monitored</th><th>Last checked</th><th>Monitor</th><th>Used for</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table></div>
</section>
"""
    return layout("Sources", "sources.html", body)


def main():
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    pages = {
        "index.html": page_index(),
        "tournaments.html": page_tournaments(),
        "venue-venetian.html": venue_page("venetian"),
        "venue-wynn.html": venue_page("wynn"),
        "hotels.html": page_hotels(),
        "calculator.html": page_calculator(),
        "analysis.html": page_analysis(),
        "questions.html": page_questions(),
        "suggestions.html": page_suggestions(),
        "flagged.html": page_flagged(),
        "sources.html": page_sources(),
    }
    for name, content in pages.items():
        write(name, content)
    print(f"built {len(pages)} pages; events={len(EVENTS)} "
          f"venetian={C['venetian']} wynn={C['wynn']} S={C['S']} N={C['N']} F={C['F']} M={C['M']}")


if __name__ == "__main__":
    main()
