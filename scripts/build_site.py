#!/usr/bin/env python3
"""Build the static GitHub Pages site in docs/ from the verified data files in data/.

Inputs (all copied from official sources; see docs/sources.html):
  data/venetian_dse_iv.txt   Venetian DeepStack Extravaganza IV schedule (official page + structure sheets)
  data/other_rooms.txt       Wynn / MGM Grand / Bellagio official listings
Outputs:
  docs/*.html, docs/assets/style.css, docs/data/*.json, docs/.nojekyll

Run:  python3 scripts/build_site.py
"""
import html
import json
import os
import re
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(ROOT, "data")

VENETIAN_PAGE = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
VENETIAN_STRUCT = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf"
WYNN_WPT_PDF = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WYNN_POKER_PAGE = "https://www.wynnlasvegas.com/casino/poker"
WYNN_DAILY_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"
WYNN_DAILY_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"
MGM_PAGE = "https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html"
MGM_SCHEDULE_PDF = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf"
MGM_STRUCT_PDF = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf"
BELLAGIO_PAGE = "https://bellagio.mgmresorts.com/en/casino/poker.html"
WYNN_TC = "https://www.visitwynn.com/tc/index.cfm?term_id=850250"
RWLV_OFFER = "https://www.rwlasvegas.com/offers/all-resort-no-fees/"
RWLV_EBLAST = "https://www.rwlasvegas.com/eblast/poker-invite/"
WSOP_NEWS = "https://www.wsop.com/news/2026-world-series-of-poker/"
PA_VENETIAN = "https://www.pokeratlas.com/poker-room/venetian-las-vegas/tournaments"

# Official house-fee / prize-pool wording taken from the structure sheets that were read.
STRUCT_FEES = {
    1: "House $40 of $200 buy-in (official); prize pool $160; guarantee includes bounties",
    7: "House $90 of $600 buy-in (official); prize pool $510; pays 12.5% of field",
    11: "House $90 of $600 buy-in (official); prize pool $510; guarantee includes bounties",
    15: "House $50 of $300 buy-in (official); prize pool $250; guarantee includes bounties",
    16: "House $100 of $800 buy-in (official); prize pool $700; guarantee includes bounties",
    33: "House $80 + $10 flat LIPS fee of $600 (official); prize pool $510; guarantee includes bounties",
    34: "House $130 of $1,100 buy-in (official); prize pool $970; guarantee includes bounty prize money",
}
STRUCT_READ = sorted(STRUCT_FEES.keys()) + [10]  # 10 read (multi-flight sheet)

STATUS_LABEL = {
    "S": ("Single-entry (verified)", "ok"),
    "M": ("Multi-flight / multi-entry", "warn"),
    "X": ("Excluded: re-entry, rebuy or paid chips", "bad"),
    "U": ("Unverified format", "unk"),
    "SAT": ("Satellite (seat prize)", "info"),
    "T": ("Team event (excluded)", "bad"),
    "R": ("Restart / final table (same event)", "info"),
}


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def money(v):
    if v in (None, "", "None"):
        return ""
    try:
        f = float(v)
    except ValueError:
        return esc(v)
    if f.is_integer():
        return "${:,.0f}".format(f)
    return "${:,.2f}".format(f)


def link(url, text=None):
    if not url:
        return ""
    return '<a href="{u}" target="_blank" rel="noopener">{t}</a>'.format(u=esc(url), t=esc(text or url))


def parse_venetian():
    rows = []
    path = os.path.join(DATA, "venetian_dse_iv.txt")
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        f = line.split("|")
        d, start, num, name, buyin, gtd, struct, status, note = f
        n = int(struct)
        rows.append({
            "venue": "Venetian Las Vegas",
            "event_group": "DeepStack Extravaganza IV",
            "date": d,
            "start": start,
            "event_no": int(num),
            "name": name,
            "buyin": float(buyin) if buyin else None,
            "guarantee": float(gtd) if gtd else None,
            "structure_no": n,
            "structure_url": VENETIAN_STRUCT.format(n=n),
            "source_url": VENETIAN_PAGE,
            "status": status,
            "note": note,
            "house_fee": STRUCT_FEES.get(n, ""),
            "structure_read": n in STRUCT_READ,
        })
    return rows


def parse_other():
    rows = []
    path = os.path.join(DATA, "other_rooms.txt")
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        f = line.split("|")
        venue, d, start, name, buyin, gtd, status, src, note = f
        rows.append({
            "venue": venue,
            "event_group": "",
            "date": d,
            "start": start,
            "event_no": None,
            "name": name,
            "buyin": float(buyin) if buyin else None,
            "guarantee_raw": gtd,
            "guarantee": float(gtd) if gtd and gtd.replace('.', '').isdigit() else None,
            "structure_no": None,
            "structure_url": "",
            "source_url": src,
            "status": status,
            "note": note,
            "house_fee": "",
            "structure_read": False,
        })
    return rows


def ratio(r):
    if r.get("buyin") and r.get("guarantee"):
        return r["guarantee"] / r["buyin"]
    return None


def sort_key_date(r):
    return (r["date"], r["start"])


# ---------------------------------------------------------------- layout
NAV = [
    ("index.html", "Dashboard"),
    ("tournaments.html", "Single-entry tournaments"),
    ("excluded.html", "Multi-entry, excluded & satellites"),
    ("unverified.html", "Unverified (needs review)"),
    ("schedule.html", "Schedule"),
    ("hotels.html", "Hotels"),
    ("analysis.html", "Analysis"),
    ("questions.html", "Questions to answer"),
    ("suggestions.html", "Suggestions (for review)"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
]


def page(active, title, body, lead=""):
    nav = "\n".join(
        '<a class="{c}" href="{h}">{t}</a>'.format(
            c="active" if h == active else "", h=h, t=esc(t))
        for h, t in NAV)
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Las Vegas Strip Poker Dashboard</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="brand"><a href="index.html">Strip Poker Dashboard</a></div>
  <div class="sub">Live tournaments near the Las Vegas Strip · data as of 2026-11-16 · all values from official sources unless flagged</div>
</header>
<div class="layout">
<nav class="side">{nav}</nav>
<main>
<h1>{title}</h1>
{lead}
{body}
<footer>Built from files in <code>data/</code> by <code>scripts/build_site.py</code>. Blank cells = not verified from an official source (see <a href="flagged.html">Flagged for Review</a>).</footer>
</main>
</div>
</body>
</html>
""".format(title=esc(title), nav=nav, lead=lead, body=body)


def table(headers, rows, cls="data"):
    th = "".join("<th>{}</th>".format(esc(h)) for h in headers)
    trs = []
    for r in rows:
        tds = "".join("<td>{}</td>".format(c) for c in r)
        trs.append("<tr>{}</tr>".format(tds))
    return '<div class="scroll"><table class="{c}"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'.format(
        c=cls, th=th, tb="\n".join(trs))


def badge(status):
    label, kind = STATUS_LABEL.get(status, (status, "unk"))
    return '<span class="badge {k}">{l}</span>'.format(k=kind, l=esc(label))


def pretty_date(iso):
    try:
        y, m, d = map(int, iso.split("-"))
        return date(y, m, d).strftime("%a %b %-d, %Y")
    except Exception:
        return esc(iso)


def pretty_time(t):
    try:
        h, m = map(int, t.split(":"))
        ap = "AM" if h < 12 else "PM"
        hh = h % 12 or 12
        return "{}:{:02d} {}".format(hh, m, ap)
    except Exception:
        return esc(t)


def build():
    os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()

    ven = parse_venetian()
    oth = parse_other()
    all_rows = ven + oth

    singles = [r for r in ven if r["status"] == "S"]
    for r in singles:
        r["ratio"] = ratio(r)
    singles.sort(key=lambda r: (-(r["ratio"] or 0), r["date"], r["start"]))

    # ---- machine-readable copies
    json.dump(ven, open(os.path.join(DOCS, "data", "venetian_dse_iv.json"), "w"), indent=1)
    json.dump(oth, open(os.path.join(DOCS, "data", "other_rooms.json"), "w"), indent=1)
    json.dump(singles, open(os.path.join(DOCS, "data", "single_entry.json"), "w"), indent=1)

    counts = defaultdict(int)
    for r in ven:
        counts[r["status"]] += 1
    other_counts = defaultdict(int)
    for r in oth:
        other_counts[r["status"]] += 1

    S_n = len(singles)
    max_gtd = max(singles, key=lambda r: r["guarantee"] or 0)
    best_ratio = singles[0]
    cheapest = min(singles, key=lambda r: r["buyin"] or 9e9)

    # ================================================================ index
    lead_index = """
<div class="banner warn"><b>Status:</b> Only one verified Strip series is live right now: the Venetian's
<i>DeepStack Extravaganza IV</i> (Nov 16 – Dec 23, 2026). The WSOP runs May–July, so it is not upcoming.
Wynn's WPT World Championship runs Nov 27 – Dec 21 (official). Hotel rates and walking distances could not be verified from official sources.</div>
"""
    cards = """
<div class="cards">
  <a class="card" href="tournaments.html"><div class="num">{s}</div><div>Single-entry Venetian events (verified structure)</div></a>
  <a class="card" href="excluded.html"><div class="num">{m}</div><div>Multi-flight, re-entry, paid-chip and satellite rows (separate)</div></a>
  <a class="card" href="unverified.html"><div class="num">{u}</div><div>Events whose entry format is not yet verified</div></a>
  <a class="card" href="hotels.html"><div class="num">2 of 5</div><div>Hotels with an official resort-fee figure</div></a>
</div>
""".format(s=S_n, m=counts["M"] + other_counts["M"] + other_counts["X"] + counts["X"] + counts["SAT"] + other_counts["SAT"], u=counts["U"] + other_counts["U"])

    exec_summary = """
<h2>Executive summary</h2>
<ol class="summary">
<li><b>What is live now.</b> Official Venetian schedule: 94 rows = 64 numbered events plus flights, restarts and satellites, Nov 16 – Dec 23, 2026. Wynn's daily tournaments are listed through Nov 26 and pause during the WPT (Nov 27 – Dec 21).</li>
<li><b>Single-entry definition used.</b> An event counts as single-entry only if (a) it is one day, (b) it has no flight suffix (1A–1F) or multi-day format, (c) its official structure sheet was read and contains no re-entry, rebuy, add-on or optional paid-chip text. This leaves <b>{s} Venetian events</b> verified.</li>
<li><b>Best value (guarantee ÷ buy-in).</b> #{bv_no} — {bv_date}, {bv_time}, {bv_name} ({bv_ratio:.1f}×). Largest guarantee among verified singles: #{mg_no} — {mg_date}, {mg_time}, {mg_name} ({mg_gtd}). Cheapest verified singles: $200 bounty events, $8,000 guarantee each.</li>
<li><b>Caution on bounty events.</b> Official structure sheets say the headline guarantee <i>includes</i> bounty money, so the cash prize pool is smaller than the headline figure.</li>
<li><b>Excluded from "single entry".</b> Wynn $200 dailies Mon–Thu, Sat and Sun (re-entry allowed), Wynn Friday $240 rebuy &amp; add-on, MGM Grand $120 (voluntary $11 gratuity buys 10,000 chips), Bellagio Friday $600 (re-entry to level 8 and a $40 gratuity for 15,000 chips), Bellagio Saturday $1,100 (flights + gratuity). These are listed separately.</li>
<li><b>8 AM start.</b> No verified single-entry event starts before 11:10 AM. The earliest verified tournament start is 9:10 AM (a satellite). Wynn daily events are re-entry, so they are not in the single-entry plan.</li>
<li><b>Hotels.</b> Official resort fees found only for Wynn ($55 + tax) and Resorts World ($55 + tax). Venetian, MGM Grand and Bellagio fees conflict across non-official sources and are flagged. No nightly rate or walking distance could be confirmed, so the true per-night cost is <b>not yet computable</b> and those cells are blank.</li>
<li><b>Verification status.</b> {nu} Venetian and {nou} other-room listings are not verified for entry format; {nflag} items are on the <a href="flagged.html">Flagged for Review</a> page with links.</li>
</ol>
""".format(
        s=S_n,
        bv_no=best_ratio["event_no"], bv_date=pretty_date(best_ratio["date"]), bv_time=pretty_time(best_ratio["start"]),
        bv_name=esc(best_ratio["name"].split(" - ")[0]), bv_ratio=best_ratio["ratio"],
        mg_no=max_gtd["event_no"], mg_date=pretty_date(max_gtd["date"]), mg_time=pretty_time(max_gtd["start"]),
        mg_name=esc(max_gtd["name"].split(" - ")[0]), mg_gtd=money(max_gtd["guarantee"]),
        nu=counts["U"], nou=other_counts["U"],
        nflag=len(FLAGS),
    )

    quick = """
<h2>Top single-entry picks (verified)</h2>
{tbl}
<p class="small">Ranked by guarantee ÷ buy-in. Full list on <a href="tournaments.html">Single-entry tournaments</a>.</p>
""".format(tbl=table(
        ["Date", "Start", "Event", "Buy-in", "Guarantee", "Guarantee ÷ buy-in", "Source"],
        [[pretty_date(r["date"]), pretty_time(r["start"]), "#{} {}".format(r["event_no"], esc(r["name"].split(" - ")[0])),
          money(r["buyin"]), money(r["guarantee"]), "{:.1f}×".format(r["ratio"]),
          link(r["source_url"], "Venetian schedule") + " · " + link(r["structure_url"], "structure")]
         for r in singles[:6]]))

    body_index = cards + exec_summary + quick + """
<h2>Where to go next</h2>
<ul>
<li><a href="schedule.html">Schedule</a> — the verified day-by-day timeline and what the 8 AM goal does and does not allow.</li>
<li><a href="hotels.html">Hotels</a> — official resort fees only; blanks where the value is unverified.</li>
<li><a href="questions.html">Questions to answer</a> — what must be known before a booking decision can be made.</li>
<li><a href="suggestions.html">Suggestions</a> — ways to improve this site. Nothing has been implemented; choose a path first.</li>
</ul>
"""
    write("index.html", page("index.html", "Dashboard", body_index, lead_index))

    # ================================================================ tournaments (single-entry)
    rows = []
    for i, r in enumerate(singles, 1):
        fee = r["house_fee"]
        rows.append([
            str(i),
            pretty_date(r["date"]),
            pretty_time(r["start"]),
            "#{}".format(r["event_no"]),
            esc(r["name"]),
            money(r["buyin"]),
            money(r["guarantee"]),
            "{:.1f}×".format(r["ratio"]),
            esc(fee),
            link(r["source_url"], "Official schedule") + "<br>" + link(r["structure_url"], "Structure #{}".format(r["structure_no"])),
        ])
    lead_t = """
<p>Criteria: one-day events with no flight suffix, no re-entry/rebuy/add-on and no paid optional chips in the official structure sheet read for that event.
Sorted by guarantee ÷ buy-in (highest first). Guarantees for bounty events include bounty money (per the official sheet).
Venue: The Venetian Las Vegas. Age 21+ and a Venetian Rewards card are required (official structure sheets).</p>
<p class="small">{n} events verified out of 30 single-entry rows. Events not listed here are on <a href="excluded.html">Multi-entry &amp; excluded</a> or <a href="unverified.html">Unverified</a>.</p>
""".format(n=S_n)
    body_t = table(
        ["#", "Date", "Start", "Event", "Event name (official)", "Buy-in", "Guarantee", "Guarantee ÷ buy-in", "Official house fee / prize pool", "Sources"],
        rows)
    write("tournaments.html", page("tournaments.html", "Single-entry tournaments (verified)", body_t, lead_t))

    # ================================================================ excluded / multi / satellite / team / restart
    ex_rows = [r for r in ven if r["status"] in ("M", "SAT", "T", "R")] + [r for r in oth if r["status"] in ("M", "X", "SAT", "R")]
    ex_rows.sort(key=lambda r: (r["venue"], r["date"], r["start"]))
    rows = []
    for r in ex_rows:
        note = esc(r["note"])
        rows.append([
            esc(r["venue"]),
            pretty_date(r["date"]) if r["date"][:2] == "20" else esc(r["date"]),
            pretty_time(r["start"]) if re.match(r"^\d", r["start"]) and ":" in r["start"] and len(r["start"]) <= 5 else esc(r["start"]),
            esc(r["name"]),
            money(r["buyin"]),
            money(r["guarantee"]) if r.get("guarantee") else esc(r.get("guarantee_raw", "")),
            badge(r["status"]),
            note,
            link(r["source_url"], "Source") + (" · " + link(r["structure_url"], "Structure #{}".format(r["structure_no"])) if r.get("structure_no") else ""),
        ])
    lead_x = """
<p>These events are <b>not</b> single-entry. They are kept here so they can be reviewed separately, as requested.
Statuses come from the official text: re-entry or rebuy language, flight suffixes (1A–1F), multi-day formats, voluntary gratuities that buy extra chips, satellites, and team formats.</p>
<p class="small">Counts: Venetian — {vm} multi-flight, {vr} restart rows, {vs} satellites, {vt} team. Other rooms — {xm} multi-flight/multi-day, {xx} excluded (re-entry or paid chips), {xs} satellites.</p>
""".format(vm=counts["M"], vr=counts["R"] + other_counts["R"], vs=counts["SAT"] + other_counts["SAT"], vt=counts["T"], xm=other_counts["M"], xx=other_counts["X"], xs=other_counts["SAT"])
    write("excluded.html", page("excluded.html", "Multi-entry, excluded & satellites (separate section)", table(
        ["Venue", "Date", "Start", "Event (official)", "Buy-in", "Guarantee", "Status", "Why", "Sources"], rows), lead_x))

    # ================================================================ unverified
    un_rows = [r for r in ven if r["status"] == "U"] + [r for r in oth if r["status"] == "U"]
    un_rows.sort(key=lambda r: (r["venue"], r["date"], r["start"]))
    rows = []
    for r in un_rows:
        rows.append([
            esc(r["venue"]),
            pretty_date(r["date"]) if r["date"][:2] == "20" else esc(r["date"]),
            pretty_time(r["start"]) if re.match(r"^\d", r["start"]) and ":" in r["start"] and len(r["start"]) <= 5 else esc(r["start"]),
            esc(r["name"]),
            money(r["buyin"]),
            money(r["guarantee"]) if r.get("guarantee") else esc(r.get("guarantee_raw", "")),
            esc(r["note"]) or "Structure sheet not read",
            link(r["source_url"], "Source") + (" · " + link(r["structure_url"], "Structure #{}".format(r["structure_no"])) if r.get("structure_no") else ""),
        ])
    lead_u = """
<p>These rows are on official pages, but the entry rules (single vs. re-entry) were <b>not confirmed</b>, so they are not in the single-entry list.
To move a row into the single-entry list, its structure sheet must be read and contain no re-entry, rebuy, add-on or paid-chip text.</p>
<p class="small">Unverified: {v} Venetian and {o} other-room rows. Blank guarantee = not stated on the official listing.</p>
""".format(v=counts["U"], o=other_counts["U"])
    write("unverified.html", page("unverified.html", "Unverified entry format (needs review)", table(
        ["Venue", "Date", "Start", "Event (official)", "Buy-in", "Guarantee", "Missing check", "Sources"], rows), lead_u))

    # ================================================================ schedule
    by_day = defaultdict(list)
    for r in ven:
        if r["status"] == "S":
            by_day[r["date"]].append(r)
    days = sorted({r["date"] for r in ven})
    rows = []
    for d in days:
        singles_d = sorted(by_day.get(d, []), key=lambda r: r["start"])
        all_d = sorted([r for r in ven if r["date"] == d], key=lambda r: r["start"])
        if singles_d:
            cell = "<br>".join("{} · #{} {} {}".format(pretty_time(r["start"]), r["event_no"], money(r["buyin"]), money(r["guarantee"]) and "(" + money(r["guarantee"]) + " GTD)")
                               for r in singles_d)
            note = "Two or more single-entry starts this day: overlap depends on how long each event runs (not verified)." if len(singles_d) > 1 else ""
        else:
            cell = "<i>No verified single-entry Venetian start</i>"
            note = ""
        other_items = [r for r in all_d if r["status"] != "S"]
        other = ", ".join("{} #{}".format(pretty_time(r["start"]), r["event_no"]) for r in other_items if r["status"] != "R")
        rows.append([pretty_date(d), cell, note, esc(other) if other else ""])
    wynn_note = """<p><b>Logistics (official, not a single-entry event):</b> Wynn daily events allow re-entries, so they are excluded from the single-entry plan. Registration-open times for single-entry events are not verified. <a href="{tc}" target="_blank" rel="noopener">source</a>.</p>""".format(tc=WYNN_DAILY_STRUCT)
    lead_s = """
<p>Verified single-entry Venetian starts by day (official start times). Earliest verified single-entry start: <b>11:10 AM</b>. The 8 AM goal therefore cannot be met with single-entry events.</p>
<p class="small">Event durations and registration-open times are not verified, so no end times or travel times are shown. Walking times between venues are not verified.</p>
"""
    body_s = wynn_note + table(["Date", "Single-entry starts (Venetian)", "Overlap note", "Other Venetian rows that day (not single-entry)"], rows)
    write("schedule.html", page("schedule.html", "Schedule — verified start times", body_s, lead_s))

    # ================================================================ hotels
    hotel_rows = [
        ["Wynn Las Vegas", "WPT / Wynn dailies (re-entry events; see schedule)",
         "<b>$55 + tax per room night</b> (official T&amp;C)", link(WYNN_TC, "Wynn official T&C"),
         "not verified",
         "", "", "", ""],
        ["Resorts World Las Vegas", "No official tournament listing found (see flags)",
         "<b>$55 + tax per room night</b> (official offer T&amp;C); waived only on the 'All Resort, No Fees' offer, valid through Dec 28, 2026 on select dates",
         link(RWLV_OFFER, "RWLV official offer") + " · " + link(RWLV_EBLAST, "RWLV poker eblast"),
         "not verified",
         "", "", "", ""],
        ["Venetian Resort", "DeepStack Extravaganza IV (host)",
         "<b>Not verified</b> — aggregators say $55; no official Venetian fee page could be read",
         link(VENETIAN_PAGE, "Venetian event page (no fee found)"), "", "", "", "", ""],
        ["MGM Grand", "Daily $120 NLH (excluded); weekly schedule",
         "<b>Not verified</b> — a non-MGM listing says $50; another says $56.69", link(MGM_PAGE, "MGM official poker page (no fee found)"), "", "", "", "", ""],
        ["Bellagio", "Fri/Sat/Sun events (excluded or unverified)",
         "<b>Not verified</b> — an aggregator says $51", link(BELLAGIO_PAGE, "Bellagio official poker page (no fee found)"), "", "", "", "", ""],
    ]
    hotel_rows = [r[:5] + [r[5], r[6], r[7], r[8]] for r in hotel_rows]
    tbl_h = table(
        ["Hotel", "Tournament link", "Official resort fee (per night, before tax)", "Source", "Parking (official)",
         "Nightly room rate", "Walking distance to venue", "Quality rating", "True nightly cost"],
        [[esc(r[0]), esc(r[1]), r[2], r[3], r[4], "<i>blank — unverified</i>", "<i>blank — unverified</i>", "<i>blank — no official source</i>", "<i>blank — needs rate</i>"]
         for r in hotel_rows])
    lead_h = """
<p>Goal per brief: lowest <i>true</i> nightly cost (room rate + resort fee + tax), then quality, with walking distance at most 30 minutes to the tournament.
This session could only confirm <b>two</b> resort fees from official sources. Nightly rates, walking distances and quality ratings are <b>blank</b> because no official source for them was retrieved.</p>
<p><b>Formula for when rates are supplied:</b> true nightly cost = (room rate + resort fee) × (1 + lodging tax rate) + parking/day. The lodging-tax rate is not verified here and is not applied.</p>
"""
    write("hotels.html", page("hotels.html", "Hotels near the Strip venues", tbl_h, lead_h))

    # ================================================================ analysis
    top10 = singles[:10]
    rows = [[str(i), pretty_date(r["date"]), pretty_time(r["start"]), "#{} {}".format(r["event_no"], esc(r["name"].split(" - ")[0])),
             money(r["buyin"]), money(r["guarantee"]), "{:.1f}×".format(r["ratio"]), link(r["source_url"], "Source")]
            for i, r in enumerate(top10, 1)]
    prize_share = []
    for r in singles:
        if r["structure_no"] in STRUCT_FEES:
            pass
    nb = sum(1 for r in singles if re.search(r"Bounty|PKO", r["name"]))
    fees = []
    for r in singles:
        m = re.search(r"House \$([\d,]+)(?: \+ \$(\d+))? of \$([\d,]+)", r["house_fee"])
        if m:
            h = float(m.group(1).replace(",", "")) + float(m.group(2) or 0)
            fees.append(100 * h / float(m.group(3).replace(",", "")))
    fmin, fmax = (min(fees), max(fees)) if fees else (0, 0)
    body_a = """
<h2>Counts</h2>
{counts_tbl}
<h2>Top 10 single-entry events by guarantee ÷ buy-in</h2>
{top}
<h2>Findings</h2>
<ul>
<li><b>Bounties inflate the headline.</b> {nb} of the {s} single-entry events are bounty or PKO formats; their guarantees include bounty money per the official sheets. Read the cash prize pool, not the headline, when comparing.</li>
<li><b>House fees on the sheets read are {fmin:.1f}%–{fmax:.1f}% of buy-in</b> (e.g., $40 of $200, $90 of $600, $130 of $1,100). The 12.5% figure on the sheets is the share of the field paid, not a fee.</li>
<li><b>Largest verified guarantee:</b> #{mg_no} ({mg_gtd}) on {mg_date}; the $1,100 PKO at #52 has the same $75,000 guarantee. The $800 bounty #36 has the highest guarantee ÷ buy-in among verified singles.</li>
<li><b>Multi-flight is where the money is, but it is not single-entry.</b> Venetian's 1A–1F events (e.g., #26 $800 with $500K guarantee; #56 $1,100 with $500K; #47 $2,200 with $1M) are excluded here because the structure sheets say players can play later flights.</li>
<li><b>Wynn's dailies are cheap but re-entry.</b> $200 NLH, $10K–$25K guarantees, re-entries to about 4:30 PM. The Friday $240 event is a rebuy and add-on event.</li>
<li><b>No verified tournament starts before 11:10 AM.</b> The 9:10 AM Venetian event (#46) is a satellite, not a cash entry.</li>
</ul>
<h2>Limits of this analysis</h2>
<ul>
<li>Only the official pages listed on the <a href="sources.html">Sources</a> page were used. Resorts World, Caesars/Planet Hollywood and Horseshoe/Paris tournament schedules were not confirmed from official pages.</li>
<li>Venetian structure sheets read: {read}. Every single-entry event maps to one of these sheets ({unread} single-entry events use a sheet not read).</li>
<li>WSOP (official wsop.com: May 26 – July 15, 2026) is outside the Nov–Dec window and is excluded.</li>
</ul>
""".format(
        counts_tbl=table(["Status", "Venetian rows", "Other-room rows"], [
            [badge(k), str(counts[k]), str(other_counts[k])] for k in ["S", "M", "X", "U", "SAT", "T", "R"]]),
        top=table(["Rank", "Date", "Start", "Event", "Buy-in", "Guarantee", "Guarantee ÷ buy-in", "Source"], rows),
        s=S_n, nb=nb, fmin=fmin, fmax=fmax,
        mg_no=max_gtd["event_no"], mg_gtd=money(max_gtd["guarantee"]), mg_date=pretty_date(max_gtd["date"]),
        read=", ".join(str(x) for x in sorted(set(STRUCT_READ))),
        unread=len([r for r in singles if not r["structure_read"]]),
    )
    write("analysis.html", page("analysis.html", "Analysis & findings", body_a))

    # ================================================================ questions
    questions = [
        ("Travel", "What are the exact arrival and departure dates?", "Determines which events and hotel nights apply. Currently all dates are open."),
        ("Budget", "What is the total budget per day (buy-ins + food + hotel + parking)?", "Single-entry buy-ins range $200–$1,100 on verified events."),
        ("Goal", "Is the goal maximum number of events, or best value per dollar?", "Changes ranking: value favours #36/#54; volume favours $200–$300 events."),
        ("Definition", "Do you accept re-entry or flight-based events, or only strict single entry?", "Currently strict single entry; the excluded list would change the plan."),
        ("Definition", "Are optional chip gratuities (MGM $11, Bellagio $40) acceptable?", "Currently excluded because they buy extra chips."),
        ("Eligibility", "Can you meet the age and rewards-card requirements (21+, Venetian Rewards card; Wynn Rewards membership)?", "Official rules; membership cost not verified."),
        ("8 AM goal", "Is an 11:10 AM start acceptable given that no verified single-entry event starts before then?", "Only satellites or re-entry events start earlier."),
        ("Verify", "Can the 29 unread Venetian structure sheets and the Wynn WPT structure sheets be read to confirm entry format?", "18 Venetian rows and most WPT rows remain unverified."),
        ("Verify", "What are the official nightly rates for each candidate hotel on the candidate dates?", "Rates are dynamic; none could be confirmed from official pages."),
        ("Verify", "What are the official resort fees for the Venetian, MGM Grand and Bellagio?", "Conflicting non-official figures; official pages not located."),
        ("Verify", "Is the MGM Grand weekly schedule current? It is labeled 'August' and shows 11:10 AM vs the page's 11:00 AM.", "Times and buy-ins may be out of date."),
        ("Verify", "What is the Bellagio Saturday buy-in: $1,000 (link text) or $1,100 (PDF text)?", "Affects value ranking only if it is ever considered."),
        ("Verify", "Where are the official Resorts World, Caesars/Planet Hollywood and Horseshoe/Paris tournament pages?", "Those schedules are not verified and are excluded."),
        ("Distance", "Should walking distances be measured with a mapping source (not on the allowed-host list) or supplied manually?", "The brief requires ≤30 minutes walking; no distance is verified yet."),
        ("Quality", "What quality measure should be used for hotels (official AAA/awards, your own rating, review scores)?", "No quality value is filled in because none is verified."),
        ("Stay", "Would you like the Wynn Signature Series (Jan 11–24, 2027, official) or the WSOP added to a later plan?", "Both are official and upcoming but outside the Nov–Dec window."),
    ]
    rows = [[esc(a), esc(b), esc(c)] for a, b, c in questions]
    lead_q = "<p>Answers needed before a reasonable decision can be made. Items marked <i>Verify</i> are data gaps that can be closed with official sources or your input.</p>"
    write("questions.html", page("questions.html", "Questions and information still needed", table(["Area", "Question", "Why it matters"], rows), lead_q))

    # ================================================================ suggestions
    sugg = [
        ("S1", "Auto-classify entry format", "Parse each official structure sheet for re-entry/rebuy/add-on/paid-chip text instead of reading each by hand.", "Faster, repeatable; still needs human review of edge cases."),
        ("S2", "Scheduled re-verification", "Re-fetch official pages on a schedule and flag any changed time, buy-in or guarantee.", "Keeps data current; needs a scheduled job or a manual run."),
        ("S3", "Link checker in build", "Fail the build if any internal page or source link breaks.", "Protects the site from broken links; adds a build step."),
        ("S4", "Hotel rate quotes table", "Add a dated table where official booking-engine rates are pasted for chosen nights, with the quote time recorded.", "Makes true cost possible; rates expire, so each quote needs a date."),
        ("S5", "Walking-distance source", "Use a mapping API or manual distances with the source recorded per row.", "Needed for the 30-minute rule; a mapping host is not on the current allowed list."),
        ("S6", "Trip planner page", "Enter arrival/departure dates and buy-in cap; the site builds a non-overlapping plan with overlap warnings.", "Directly answers 'play all day'; more work and needs the answers on the Questions page."),
        ("S7", "Filters and sorting", "Add client-side filters (date, venue, buy-in, guarantee) to each table.", "Easier to use; a small JavaScript addition."),
        ("S8", "Last-verified column", "Show the date each row was last checked against its official source.", "Improves trust; needs a verification log per row."),
        ("S9", "CSV download", "Offer each table as CSV for offline comparison.", "Useful for sharing; small effort."),
        ("S10", "Keep the current static design", "Leave the site as it is; only fix data as gaps are closed.", "Lowest effort; no new features."),
    ]
    rows = [[esc(a), esc(b), esc(c), esc(d)] for a, b, c, d in sugg]
    lead_sg = """
<div class="banner unk"><b>For review only.</b> No suggestion below has been implemented. Choose one or more (for example "S1, S3, S6") before any change is made.</div>
"""
    write("suggestions.html", page("suggestions.html", "Suggestions to improve the site (for review)", table(["ID", "Suggestion", "What it does", "Trade-off"], rows), lead_sg))

    # ================================================================ flagged
    flags_html = []
    for i, (sev, title, detail, links) in enumerate(FLAGS, 1):
        l = " · ".join(link(u, t) for t, u in links)
        flags_html.append([str(i), badge_sev(sev), esc(title), esc(detail), l])
    lead_f = """
<div class="banner warn"><b>Flagged for Review.</b> These items do not block publication. Each has source links for manual review.
Please review these after the site is live and request changes if needed.</div>
"""
    write("flagged.html", page("flagged.html", "Flagged for Review", table(["#", "Severity", "Item", "Detail", "Sources"], flags_html), lead_f))

    # ================================================================ sources
    srcs = [
        ("Venetian DeepStack Extravaganza IV — official schedule page", VENETIAN_PAGE, "All 94 rows (dates, times, event numbers, names, buy-ins, guarantees, structure numbers)"),
        ("Venetian structure sheet — #1 ($200 bounty)", VENETIAN_STRUCT.format(n=1), "Single-day; house fee $40; events 9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64"),
        ("Venetian structure sheet — #7 ($600 1Day, $30K/$40K)", VENETIAN_STRUCT.format(n=7), "Single-day; events 14, 28, 63; house fee $90"),
        ("Venetian structure sheet — #10 ($300 1A–1D flights)", VENETIAN_STRUCT.format(n=10), "Multi-flight; 'may not play a subsequent flight' wording"),
        ("Venetian structure sheet — #11 ($600 bounty)", VENETIAN_STRUCT.format(n=11), "Events 16, 30, 54"),
        ("Venetian structure sheet — #15 ($300 bounty)", VENETIAN_STRUCT.format(n=15), "Events 29, 31, 34, 38, 42, 50, 51, 53, 55"),
        ("Venetian structure sheet — #16 ($800 bounty, $75K)", VENETIAN_STRUCT.format(n=16), "Event 36"),
        ("Venetian structure sheet — #33 ($600 LIPS, $30K)", VENETIAN_STRUCT.format(n=33), "Event 43"),
        ("Venetian structure sheet — #34 ($1,100 PKO, $75K)", VENETIAN_STRUCT.format(n=34), "Event 52"),
        ("Wynn Las Vegas poker page", WYNN_POKER_PAGE, "Daily tournaments suspended during WPT; WPT dates Nov 27–Dec 21; Friday $40K rebuy"),
        ("Wynn WPT World Championship schedule (PDF)", WYNN_WPT_PDF, "All WPT rows (dates, times, buy-ins, guarantees)"),
        ("Wynn daily tournament poster (PDF)", WYNN_DAILY_POSTER, "Daily $200 NLH $10K (Mon–Thu, 12 PM); $200 $25K (Sat/Sun); nightly $160 $10K (6 PM); Friday $240 rebuy $40K"),
        ("Wynn daily tournament structures (PDF)", WYNN_DAILY_STRUCT, "Re-entry until level 9 for $200 events; Friday rebuy & add-on"),
        ("MGM Grand poker page", MGM_PAGE, "Daily tournament times 11:00 AM, 7:00 PM, 11:00 PM"),
        ("MGM Grand weekly tournament schedule (PDF)", MGM_SCHEDULE_PDF, "$120 NLH at 11:10 AM / 7:10 PM / 11:10 PM; Saturday $150 NLH $2,000 guarantee; titled 'August'"),
        ("MGM Grand $120 NLH structure (PDF)", MGM_STRUCT_PDF, "Voluntary $11 gratuity grants 10,000 extra chips; registration until level 8"),
        ("Bellagio poker page", BELLAGIO_PAGE, "Friday $600, Saturday $1,000 (link text), Sunday $400 HORSE; stale 'resume July 26' notice"),
        ("Bellagio Friday $600 NLH structure (PDF)", "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf", "Re-entry through level 8; $40 gratuity grants 15,000 chips"),
        ("Bellagio Saturday NLH structure (PDF)", "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf", "PDF says NLH $1100 buy-in; flights 1A–1D; $40 gratuity grants 20,000 chips"),
        ("Wynn Las Vegas terms (resort fee)", WYNN_TC, "$55 + tax daily resort fee"),
        ("Resorts World 'All Resort, No Fees' offer (official)", RWLV_OFFER, "$55 resort fee per room per night waived only under offer; valid through Dec 28, 2026"),
        ("Resorts World poker eblast (official)", RWLV_EBLAST, "Address 3000 S Las Vegas Blvd; no tournament schedule found"),
        ("WSOP 2026 news (official wsop.com)", WSOP_NEWS, "May 26 – July 15, 2026 (outside the window)"),
        ("PokerAtlas Venetian page (non-official, lead only)", PA_VENETIAN, "Used only to locate the Venetian series; no values taken from it"),
    ]
    rows = [[esc(a), link(b, b), esc(c)] for a, b, c in srcs]
    lead_src = "<p>All sources were retrieved on 2026-11-16. Items marked non-official were used only to find official pages; no value was taken from them.</p>"
    write("sources.html", page("sources.html", "Sources (official unless marked)", table(["Source", "URL", "Used for"], rows), lead_src))


def badge_sev(sev):
    kind = {"High": "bad", "Medium": "warn", "Low": "info", "Unverified": "unk"}.get(sev, "unk")
    return '<span class="badge {k}">{s}</span>'.format(k=kind, s=esc(sev))


def write(name, content):
    with open(os.path.join(DOCS, name), "w", encoding="utf-8") as f:
        f.write(content)


# (severity, title, detail, [(link text, url), ...])
FLAGS = [
    ("High", "Bellagio Saturday buy-in mismatch",
     "The Bellagio page links the Saturday event as '$1,000 NLH', but the PDF it links to says 'NLH $1100 BUY-IN' (and 'Combined Final Day 2 ... at Bellagio').",
     [("Bellagio page", BELLAGIO_PAGE), ("Saturday PDF", "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf")]),
    ("High", "MGM Grand schedule may be outdated",
     "The weekly schedule PDF is titled 'August Tournament Schedule' and gives 11:10 AM / 7:10 PM / 11:10 PM; the official poker page gives 11:00 AM / 7:00 PM / 11:00 PM. No dates are printed.",
     [("MGM poker page", MGM_PAGE), ("Weekly schedule PDF", MGM_SCHEDULE_PDF)]),
    ("High", "Hotel resort fees not confirmed for Venetian, MGM Grand, Bellagio",
     "Only the Wynn and Resorts World fees are on official pages. Non-official sources conflict for MGM Grand ($50 vs $56.69) and state $55 (Venetian) and $51 (Bellagio). Values left blank.",
     [("Wynn T&C", WYNN_TC), ("RWLV offer T&C", RWLV_OFFER), ("Venetian event page", VENETIAN_PAGE)]),
    ("High", "No nightly room rates verified",
     "Rates are dynamic and no official rate page for the candidate dates was retrieved. The true cost per night cannot be computed; all rate cells are blank.",
     [("Hotels page", "hotels.html")]),
    ("High", "Walking distances not verified",
     "No official source for walking time between hotels and venues was retrieved, so the 30-minute rule cannot be confirmed for any hotel. Cells are blank.",
     [("Hotels page", "hotels.html")]),
    ("High", "Bounty guarantees include bounty money",
     "Venetian structure sheets state that the guarantee is 'prize pool + total bounties'. The cash prize pool is therefore lower than the headline guarantee. This is an official statement, flagged because it changes how value is read.",
     [("Structure #1", VENETIAN_STRUCT.format(n=1)), ("Structure #11", VENETIAN_STRUCT.format(n=11)), ("Structure #34", VENETIAN_STRUCT.format(n=34))]),
    ("Medium", "Venetian Race-format events not understood",
     "Events 3–5 are listed as '$200 NLH RaceDay Stack (1Day) - Race to finish before the Race'. The format is not explained on the schedule and the structure sheet was not read.",
     [("Venetian event page", VENETIAN_PAGE), ("Structure #18", VENETIAN_STRUCT.format(n=18))]),
    ("Medium", "PokerAtlas Pro membership discount (Events 18 and 58)",
     "Event listed with a '$20 rake discount' for PokerAtlas Pro members. The membership cost and eligibility were not verified.",
     [("Venetian event page", VENETIAN_PAGE), ("Structure #8", VENETIAN_STRUCT.format(n=8))]),
    ("Medium", "Tag-team and age-restricted events",
     "Event 35 is a female/female or female/male tag team (excluded). Events 24, 32, 49 are 50+ only. Event 39 is a two-day event whose structure was not read.",
     [("Venetian event page", VENETIAN_PAGE)]),
    ("Medium", "Wynn WPT PDF lists Dec 17 after Dec 18",
     "In the official WPT schedule PDF the Thursday Dec 17 rows appear after the Friday Dec 18 rows. The dates were transcribed as printed; possible typo on the official sheet.",
     [("WPT schedule PDF", WYNN_WPT_PDF)]),
    ("Medium", "Wynn daily tournaments paused during the WPT",
     "The official Wynn page says daily tournaments are suspended during the WPT series (Nov 27 – Dec 21). Daily dates are therefore listed only through Nov 26. Dates after Dec 21 were not verified.",
     [("Wynn poker page", WYNN_POKER_PAGE)]),
    ("Medium", "Wynn nightly $160 event: structure not read",
     "Listed on the official daily poster, but the nightly structure was not located in the sheets read.",
     [("Daily poster", WYNN_DAILY_POSTER), ("Daily structures", WYNN_DAILY_STRUCT)]),
    ("Medium", "Resorts World tournaments: no official page found",
     "Official rwlasvegas.com pages retrieved contain no tournament schedule (the poker eblast has none). Third-party sites (2024–2025) describe $200 NLH at noon and 7 PM, but those are not used.",
     [("RWLV poker eblast", RWLV_EBLAST), ("RWLV offer", RWLV_OFFER)]),
    ("Medium", "Caesars / Planet Hollywood tournaments: no official page retrieved",
     "The official Caesars page did not show poker schedules. Third-party reports from 2025 describe four $100 NLH events a day; those are old and not used.",
     [("Caesars home (official)", "https://www.caesars.com/planet-hollywood-las-vegas/casino/poker")]),
    ("Medium", "Bellagio: stale and undated notice",
     "The official Bellagio page says 'Tournament play will resume on Saturday, July 26' with no year. The Friday, Saturday and Sunday schedule has no printed dates.",
     [("Bellagio page", BELLAGIO_PAGE)]),
    ("Medium", "Bellagio Sunday $400 HORSE: PDF not read",
     "Listed on the official page; the PDF was not read, so the format and start time are not verified.",
     [("Bellagio page", BELLAGIO_PAGE)]),
    ("Medium", "Venetian single-entry status rests on 7 structure sheets",
     "All 30 single-entry events map to structure sheets #1, #7, #11, #15, #16, #33 and #34, which were read in full. Sheet #10 (1A–1D flights) was also read. The other 29 sheets were not read; they cover only rows classified U or M.",
     [("Venetian event page", VENETIAN_PAGE)]),
    ("Low", "WSOP end date conflicts across sources",
     "The official wsop.com news page says May 26 – July 15, 2026. Some third-party pages say July 25. The WSOP is outside the planned window either way.",
     [("WSOP news (official)", WSOP_NEWS)]),
    ("Low", "Venetian claim of '$3.6 Million' guaranteed prize pools",
     "Stated on the official page; the sum of guarantees was not checked against individual rows.",
     [("Venetian event page", VENETIAN_PAGE)]),
    ("Low", "Venetian satellites listed in the cash schedule",
     "Rows 33, 37, 41, 44, 45, 46, 48 are satellites (seat prizes, not cash). They are shown separately.",
     [("Venetian event page", VENETIAN_PAGE)]),
    ("Low", "Repo review: no code, tests or CI in the repository",
     "Repository contains only README.md ('# Poker5') and one commit (0ba2e55 Initial commit). No .gitignore, license, or CI config was present.",
     [("Repository", "https://github.com/karagemop466-tech/Poker5")]),
    ("Low", "Repo review: brief's branch naming differs from the assigned branch",
     "The brief asks for session-<id>/<task> branches; the platform assigned arena/de0bebd4-poker5. The assigned branch is used.",
     [("COORDINATION.md", "https://github.com/karagemop466-tech/Poker5/blob/arena/de0bebd4-poker5/COORDINATION.md")]),
    ("Low", "Repo review: COORDINATION.md did not exist",
     "Created by this session as the shared task board. Only one session worked on the repository.",
     [("COORDINATION.md", "https://github.com/karagemop466-tech/Poker5/blob/arena/de0bebd4-poker5/COORDINATION.md")]),
]


if __name__ == "__main__":
    build()
    print("built", len(os.listdir(DOCS)), "entries in docs/")
