#!/usr/bin/env python3
"""Build the static GitHub Pages site into docs/ from scripts/data.py.

    python3 scripts/build_site.py

Standard library only. Every number on the site comes from data.py, which only holds values
taken from official pages or PDFs opened during this session. Estimates are labelled.
"""
import datetime as dt
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "docs")
AS_OF = D.AS_OF


# ---------- helpers ----------
def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def money(n):
    return "" if n is None else f"${n:,.0f}"


def a(url, label=None):
    label = label or url
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'


def badge(text, kind="x"):
    return f'<span class="badge {kind}">{esc(text)}</span>'


UNVER = badge("Unverified", "x")
EST = badge("Estimate", "warn")


def sheet_link(n):
    return a(D.sheet(n), f"Sheet {n}")


def table(headers, rows, tid, cls="wide", search=True):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    box = f'<div class="tools"><input type="search" placeholder="Filter rows…" data-filter="{tid}" aria-label="Filter table"></div>' if search else ""
    return f'{box}<div class="tablewrap"><table id="{tid}" class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def kpi(value, label):
    return f'<div class="kpi"><div class="kv">{esc(value)}</div><div class="kl">{esc(label)}</div></div>'


def section(title, body, cls="panel"):
    return f'<section class="{cls}"><h2>{esc(title)}</h2>{body}</section>'


def intro(title, lead):
    return f'<section class="intro"><h1>{esc(title)}</h1><p class="lead">{lead}</p></section>'


# ---------- derived numbers (only arithmetic on official numbers) ----------
def multiple(e):
    return round(e["gtd"] / e["buyin"], 2) if e["gtd"] else None


def pool_from_buyin(e):
    return None  # not computed: pool split is taken from the sheet (see SHEETS_READ)


def ranked_single():
    rows = []
    for e in D.SINGLE_ENTRY:
        rows.append(dict(e, mult=multiple(e)))
    ranked = sorted([r for r in rows if r["mult"] is not None], key=lambda r: (-r["mult"], -r["gtd"], r["date"], r["event"]))
    unranked = sorted([r for r in rows if r["mult"] is None], key=lambda r: (r["date"], r["event"]))
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    for r in unranked:
        r["rank"] = None
    return ranked + unranked


SINGLE = ranked_single()
N_SINGLE = len(D.SINGLE_ENTRY)
N_NO_GTD = sum(1 for e in D.SINGLE_ENTRY if e["gtd"] is None)
N_UNVER = len(D.UNVERIFIED_VENETIAN)
N_MULTI = len(D.MULTI_ENTRY)
N_HOTELS = len(D.HOTELS)


def time_key(t):
    return dt.datetime.strptime(t, "%I:%M %p").time()


EARLIEST = min((e for e in D.SINGLE_ENTRY), key=lambda e: time_key(e["start"]))
EARLIEST_START = EARLIEST["start"]

# ---------- navigation ----------
NAV = [
    ("index.html", "Home"),
    ("single-entry.html", "Single-entry (ranked)"),
    ("multi-entry.html", "Rebuys & paid chips"),
    ("schedule.html", "Day schedule"),
    ("hotels.html", "Hotels"),
    ("questions.html", "Questions & info"),
    ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged for Review"),
    ("repo-review.html", "Repo review"),
    ("sources.html", "Sources"),
]


def layout(title, active, body):
    nav = "".join(f'<a href="{h}" class="{"active" if h == active else ""}">{esc(l)}</a>' for h, l in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Las Vegas Strip Poker Planner</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="brand"><a href="index.html">Las Vegas Strip Poker Planner</a><span class="asof">Data as of {AS_OF}</span></div>
  <nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer>
  <p>Every value on this site comes from an official casino page or PDF, linked on its row. Values that no official source stated are left blank and marked {UNVER}. Walk times are {EST}s. Nothing here is booking, gambling, or financial advice. Confirm every detail with the casino before you travel.</p>
  <p class="small">Problem Gambling HelpLine (Wynn's official documents): 1-800-522-4700.</p>
</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""


# ---------- PAGE: home ----------
def page_index():
    top = [e for e in SINGLE if e["rank"] and e["rank"] <= 5]
    top_rows = [
        [str(e["rank"]), f'{esc(e["date"])} · {esc(e["start"])}', f'#{e["event"]} {esc(e["name"])}',
         money(e["buyin"]), money(e["gtd"]), f'{e["mult"]}×', a(D.SRC["dse_pdf"], "Schedule") + " · " + sheet_link(e["sheet"])]
        for e in top
    ]
    summary = f"""
<ol class="summary">
  <li><strong>Verified single-entry events: {N_SINGLE}.</strong> All are in the Venetian's DeepStack Extravaganza IV (Nov 16 – Dec 23, 2026). Each date, buy-in, and guarantee comes from the official schedule PDF. Each event's structure sheet was read for re-entry, rebuy, add-on, paid-chip, and later-flight rules; none has any of them.</li>
  <li><strong>{N_NO_GTD} of them have no official guarantee</strong> (#3, #4, #5, #6). Their guarantee cells are blank.</li>
  <li><strong>{N_UNVER} more Venetian events are unverified.</strong> They are flights, satellites, tag-team, two-day, or PLO/Big O events whose structure sheets I did not read. They are listed on the Flagged page, not ranked.</li>
  <li><strong>Re-entry and paid-chip events are in their own section</strong> ({N_MULTI} rows): Wynn daily tournaments (re-entry and rebuys) and Bellagio Friday, Saturday, and Sunday (re-entry or optional chip purchases).</li>
  <li><strong>Earliest single-entry start: {esc(EARLIEST_START)}.</strong> Nothing verified starts between 8 AM and 10:10 AM, so a full-day plan from 8 AM cannot be built from verified single-entry events. See the Day schedule page.</li>
  <li><strong>Hotels: only partly verified.</strong> The Venetian's resort fee is $55 a night (official). Wynn's is $55 plus tax (official terms, but for an expired promotion). Base room rates are not verified for any hotel, so no true nightly cost is shown. Walk times are unverified estimates.</li>
  <li><strong>Decisions blocked:</strong> your travel dates, party size, and budget; room rates for those dates; Clark County tax rate; Bellagio's resort-fee terms; and Bellagio Saturday's buy-in conflict. See <a href="questions.html">Questions &amp; info</a>.</li>
</ol>"""
    kp = (
        kpi(N_SINGLE, "verified single-entry events")
        + kpi(N_NO_GTD, "single-entry events with no official guarantee")
        + kpi(N_UNVER, "Venetian events, format unverified")
        + kpi(N_MULTI, "re-entry / rebuy / paid-chip rows")
        + kpi(N_HOTELS, "hotels listed (4 within 30 min by unverified estimate)")
    )
    cards = """
<div class="cards">
  <a class="card" href="single-entry.html"><h3>Single-entry (ranked)</h3><p>Verified single-entry events, ranked by guarantee ÷ buy-in.</p></a>
  <a class="card" href="multi-entry.html"><h3>Rebuys &amp; paid chips</h3><p>Re-entry, rebuy, add-on, or optional chip purchase events. Kept separate.</p></a>
  <a class="card" href="schedule.html"><h3>Day schedule</h3><p>Every day Nov 16 – Dec 23, with official start and registration-close times.</p></a>
  <a class="card" href="hotels.html"><h3>Hotels</h3><p>Official resort fees, walk-time estimates, and what is still missing for a true nightly cost.</p></a>
  <a class="card" href="questions.html"><h3>Questions &amp; info</h3><p>What is answered (with sources) and what you must supply before booking.</p></a>
  <a class="card" href="suggestions.html"><h3>Suggestions</h3><p>Site improvements for review. Nothing is implemented until you approve it.</p></a>
  <a class="card warnc" href="flagged.html"><h3>Flagged for Review</h3><p>Irregularities, unverified rows, and conflicting official figures, each with a source link.</p></a>
  <a class="card" href="repo-review.html"><h3>Repo review</h3><p>What was checked in the repository, and what was flagged.</p></a>
</div>"""
    body = (
        intro("Las Vegas Strip poker: verified tournaments, rules, and hotels",
              "Built only from official casino pages and PDFs, linked on every row. Anything an official source did not state is blank and flagged.")
        + f'<section class="kpis">{kp}</section>'
        + section("Executive summary", summary)
        + section("Top 5 verified single-entry events (guarantee ÷ buy-in)",
                  '<p class="small">Multiple = official guarantee ÷ official buy-in (computed here). Bounty guarantees include bounty money, as stated on each sheet.</p>'
                  + table(["Rank", "Date · start", "Event", "Buy-in", "Guarantee", "×", "Sources"], top_rows, "top5", search=False))
        + "<h2>Browse</h2>"
        + cards
    )
    return layout("Home", "index.html", body)


# ---------- PAGE: single-entry ----------
def page_single():
    rows = []
    for e in SINGLE:
        tags = []
        if e["gtd"] is None:
            tags.append(badge("No official guarantee", "x"))
        if "50+" in e["name"]:
            tags.append(badge("50+ only", "warn"))
        if "Valuetown" in e["name"]:
            tags.append(badge("PokerAtlas PRO $20 off first entry", "warn"))
        if "Bounty" in e["name"] or "Knock-Out" in e["name"]:
            tags.append(badge("Bounty: guarantee includes bounties", "ok"))
        s = D.SHEETS_READ[e["sheet"]]
        pool_cell = f'{money(s["pool"])} <span class="small">of {money(e["buyin"])} (house {money(s["house"])})</span>'
        rows.append([
            str(e["rank"]) if e["rank"] else "—",
            f'{esc(e["date"])}<br><span class="small">{esc(e["start"])} · reg. closes {esc(e["reg_close"])}</span>',
            f'#{e["event"]}',
            f'{esc(e["name"])}<br>' + " ".join(tags),
            money(e["buyin"]),
            money(e["gtd"]) if e["gtd"] else UNVER,
            f'{e["mult"]}×' if e["mult"] else "—",
            pool_cell,
            money(e["chips"]) if e["chips"] else "—",
            a(D.SRC["dse_pdf"], "Schedule") + " · " + sheet_link(e["sheet"]),
        ])
    body = (
        intro("Single-entry tournaments (verified)",
              "Venetian DeepStack Extravaganza IV, Nov 16 – Dec 23, 2026. Ranked by official guarantee ÷ buy-in. Events with no official guarantee are listed but not ranked.")
        + section("How the rules were applied", """<ul>
<li><strong>Single-entry</strong> means the official structure sheet describes one entry. The sheet has no re-entry, rebuy, add-on, paid-chip, or later-flight language. Late registration is allowed.</li>
<li><strong>Ranking:</strong> guarantee ÷ buy-in, highest first, then guarantee. The guarantee is the official figure; bounty events include bounty money in it.</li>
<li><strong>Prize pool / house:</strong> taken from the structure sheet's buy-in breakdown. Sheet 5 (#2, #12) and sheet 6 (#10) are read from the same official sheets.</li>
<li><strong>Not ranked:</strong> events with no official guarantee, and all unverified-format events (see Flagged).</li>
</ul>""")
        + f'<section class="panel">{table(["Rank", "Date · start", "Event", "Tournament", "Buy-in", "Guarantee", "Guarantee ÷ buy-in", "Prize pool from buy-in (sheet)", "Chips", "Sources"], rows, "single")}</section>'
    )
    return layout("Single-entry", "single-entry.html", body)


# ---------- PAGE: multi-entry ----------
def page_multi():
    rows = []
    for m in D.MULTI_ENTRY:
        rows.append([
            esc(m["venue"]),
            f'<strong>{esc(m["name"])}</strong><br><span class="small">{esc(m["start"])}</span>',
            money(m["buyin"]) if m["buyin"] else UNVER,
            money(m["gtd"]) if m["gtd"] else UNVER,
            badge(m["kind"], "warn"),
            esc(m["rule"]),
            a(D.SRC[m["src"]], "Official sheet") + " · " + a(D.SRC[m["src2"]], "Official page"),
        ])
    body = (
        intro("Rebuys, re-entry, add-ons, and paid chips (not single-entry)",
              "Shown separately, as requested. Each row lets you buy in again, add chips, or pay extra for chips. Read each rule before you decide.")
        + section("What counts here", """<ul>
<li><strong>Re-entry / rebuy:</strong> an official rule lets you buy in again after busting.</li>
<li><strong>Add-on / paid chips:</strong> an official rule lets you buy extra chips, including an optional staff gratuity that buys chips.</li>
<li><strong>Buy-in conflict:</strong> the official sheet states two different buy-ins, so the buy-in cell is left blank.</li>
</ul>""")
        + f'<section class="panel">{table(["Venue", "Tournament", "Buy-in", "Guarantee", "Type", "Official rule", "Sources"], rows, "multi")}</section>'
        + section("Notes", """<p>Wynn's Friday sheet says "Re-entry is NOT allowed", but its rules allow unlimited $200 rebuys and a $100 add-on. The Wynn sheets for Monday–Thursday, Saturday, Sunday and the nightly event all allow re-entry until the start of level 9.</p>
<p>Bellagio's Saturday sheet is inconsistent: header "$1100 BUY-IN", rule 07 "$600 Buy-in". Its buy-in is blank until Bellagio confirms it (see Flagged).</p>""")
    )
    return layout("Rebuys & paid chips", "multi-entry.html", body)


# ---------- PAGE: schedule ----------
def page_schedule():
    single_by_day = {}
    for e in D.SINGLE_ENTRY:
        single_by_day.setdefault(e["date"], []).append(e)
    unver_by_day = {}
    for u in D.UNVERIFIED_VENETIAN:
        first = u["date"][:10]
        unver_by_day.setdefault(first, []).append(u)
    rows = []
    d = dt.date(2026, 11, 16)
    end = dt.date(2026, 12, 23)
    while d <= end:
        key = d.isoformat()
        singles = sorted(single_by_day.get(key, []), key=lambda e: time_key(e["start"]))
        unv = unver_by_day.get(key, [])
        s_cell = "<br>".join(
            f'<strong>{esc(e["start"])}</strong> · #{e["event"]} {esc(e["name"])} · {money(e["buyin"])} · '
            + (f'GTD {money(e["gtd"])}' if e["gtd"] else 'GTD ' + UNVER)
            + f' · reg. closes {esc(e["reg_close"])}'
            for e in singles
        ) or '<span class="small">No verified single-entry start</span>'
        u_cell = "<br>".join(f'{esc(u["start"])} · #{u["event"]} {esc(u["name"])} ({esc(u["kind"])})' for u in unv) or ""
        rows.append([f"{d.strftime('%a %b')} {d.day}", s_cell, str(len(singles)), u_cell])
        d += dt.timedelta(days=1)
    body = (
        intro("Day schedule, Nov 16 – Dec 23, 2026",
              "Official start times and registration-close times from the Venetian schedule PDF. The official schedule gives no event lengths, so this page does not claim you can play two events in one day.")
        + section("Can you play all day from 8 AM?", f"""
<p><strong>Not with verified single-entry events.</strong> The earliest single-entry start is {esc(EARLIEST_START)} (RaceDay, Nov 19–21; Seniors, Dec 2 and Dec 8). Nothing in the verified list starts between 8 AM and 10:10 AM.</p>
<p>Days with two single-entry starts (for example Nov 28: 11:10 AM, 12:10 PM, 5:10 PM) let you enter both. Whether you can play both to the end depends on how long each event runs, which the official schedule does not state.</p>
<p>The unverified column lists flights, satellites, and other formats. They are not single-entry in this planner until their sheets are read.</p>""")
        + f'<section class="panel">{table(["Date (2026)", "Verified single-entry starts (official)", "Count", "Unverified formats (not in ranking)"], rows, "sched")}</section>'
    )
    return layout("Day schedule", "schedule.html", body)


# ---------- PAGE: hotels ----------
def page_hotels():
    rows = []
    for h in D.HOTELS:
        if h["walk_min"] is not None:
            walk = f'{h["walk_min"]} min <span class="small">({h["walk_km"]:.2f} km)</span> {EST}'
            within = "Yes (estimate)" if h["walk_min"] <= 30 else "No (estimate)"
            within_cell = badge(within, "ok" if h["walk_min"] <= 30 else "x")
        else:
            walk = "On site" if "On site" in h["walk_note"] else UNVER
            within_cell = badge("Yes (on site)", "ok")
        fee = esc(h["resort_fee"]) if h["resort_fee"] else UNVER
        rate = esc(h["base_rate"]) if h["base_rate"] else UNVER
        src = []
        if h.get("fee_src"):
            src.append(a(D.SRC[h["fee_src"]], "Official fee source"))
        if h.get("src_price") and h["src_price"] != h.get("fee_src"):
            src.append(a(D.SRC[h["src_price"]], "Official rate source"))
        rows.append([
            f'<strong>{esc(h["name"])}</strong>',
            walk,
            within_cell,
            fee,
            rate,
            esc(h["parking"]) if h.get("parking") else UNVER,
            esc(h["notes"]) + ("<br>" + " · ".join(src) if src else ""),
        ])
    body = (
        intro("Hotels near the Venetian poker room",
              "Priority: cost and quality, then walk distance (30 minutes is the limit). Walk times are estimates, not official values. Nightly base rates are not verified for any hotel, so no true nightly cost is shown.")
        + section("Why there is no nightly total yet", """
<ul>
<li><strong>Room rates:</strong> the Venetian publishes "as low as $119 and $209", but only with a poker-play requirement and subject to availability. Neither the Venetian nor Wynn gives a date-specific price in the sources read.</li>
<li><strong>Taxes:</strong> the Clark County lodging-tax rate was not read from an official page, so no fee-plus-tax totals are computed.</li>
<li><strong>Quality:</strong> no official quality source was read, so no hotel is scored. Quality cells are not filled in.</li>
</ul>""")
        + f'<section class="panel">{table(["Hotel", "Walk to Venetian poker room", "≤ 30 min?", "Resort fee (official)", "Base room rate", "Parking", "Notes & sources"], rows, "hotels")}</section>'
        + section("Walk-time method", f'<p>{esc(D.WALK_NOTE)}</p><p class="small">Routes: ' + " · ".join(a(u, k) for k, (u, _) in D.OSRM_ROUTES.items()) + "</p>")
    )
    return layout("Hotels", "hotels.html", body)


# ---------- PAGE: questions ----------
ANSWERED = [
    ("Which official schedules were read in full?",
     "Venetian DeepStack Extravaganza IV schedule PDF (both pages) and event page (all 4 pages). Wynn daily tournament structures PDF (all 3 pages), Wynn daily poster. Bellagio Friday, Saturday, and Sunday PDFs. Venetian structure sheets are listed on Sources.",
     [("Venetian schedule", D.SRC["dse_pdf"]), ("Venetian event page", D.SRC["dse_page"]), ("Wynn daily structures", D.SRC["wynn_daily_structs"]), ("Bellagio Saturday", D.SRC["bellagio_sat"])]),
    ("How many Venetian events are verified single-entry?",
     f"{N_SINGLE} of the 64 numbered Venetian events (structure sheet read; no re-entry, rebuy, add-on, paid-chip, or later-flight language). {N_UNVER} are unverified and are not ranked. Wynn and Bellagio re-entry rows are on their own page.",
     [("Venetian event page", D.SRC["dse_page"])]),
    ("What is the Venetian resort fee?", "$55 per night stayed.", [("Venetian poker suite rates", D.SRC["venetian_suite"])]),
    ("What must you do for the Venetian's poker suite rate?",
     "Play six hours of live cash or buy into a $300-or-higher tournament each night stayed. Rates start as low as $119 and $209. Blackout dates and availability apply.",
     [("Venetian poker suite rates", D.SRC["venetian_suite"])]),
    ("What is the Wynn resort fee?", "$55 plus tax per room night (Wynn Resort King and Two Queens). The source is an expired 2026 promotion page, so re-confirm it.",
     [("Wynn terms (expired promo)", D.SRC["wynn_terms"])]),
    ("Are Wynn's daily tournaments single-entry?", "No. Mon–Thu, Sat, and Sun allow re-entry until level 9; Friday allows unlimited $200 rebuys plus a $100 add-on; the nightly $160 allows re-entry and a $100 add-on until level 9.",
     [("Wynn daily structures", D.SRC["wynn_daily_structs"])]),
    ("Are Bellagio's Friday and Sunday events single-entry?", "No. Both allow re-entry through level 8. Each also has an optional staff gratuity that buys extra chips (Friday $40 / 15,000 chips; Sunday $25 / 15,000 chips).",
     [("Bellagio Friday", D.SRC["bellagio_fri"]), ("Bellagio Sunday", D.SRC["bellagio_sun"])]),
    ("When is the earliest single-entry start?", f"{EARLIEST_START} (verified).", [("Venetian schedule", D.SRC["dse_pdf"])]),
    ("Which Venetian events have no official guarantee?", "#3, #4, #5 (RaceDay Stack) and #6. Their guarantee cells are blank.", [("Venetian schedule", D.SRC["dse_pdf"])]),
    ("Is the MGM Grand poker page available?", "No. The official URL returned 'Page not found' when opened.", [("MGM Grand poker page", D.SRC["mgmgrand_404"])]),
    ("Does ARIA publish a tournament schedule on its poker page?", "No. The page says to call the poker room.", [("ARIA poker page", D.SRC["aria_poker"])]),
]

OPEN = [
    ("Q1", "Travel dates and number of nights", "Decides which events are open and which room rates apply.", "You"),
    ("Q2", "Party size and room type", "Changes room rates, the Wynn extra-guest charge, and Venetian suite pricing.", "You"),
    ("Q3", "Room rate for each hotel on your dates", "Needed for true nightly cost. No date-specific official rate was read.", "You: check each official booking page and record the total"),
    ("Q4", "Clark County / Strip lodging tax rate", "Needed for fee-plus-tax totals. No official tax page was read.", "Agent next pass (official Clark County page)"),
    ("Q5", "Bellagio resort fee and parking", "No official MGM terms page was read.", "Agent next pass (official MGM page)"),
    ("Q6", "Resort fees for Encore, ARIA, Resorts World", "No official fee page was read for these.", "Agent next pass, or you"),
    ("Q7", "Walk-time origin points", "The Venetian and Wynn origin coordinates are not from an official source.", "Agent next pass (official addresses + geocoder)"),
    ("Q8", "Bellagio Saturday buy-in", "Header says $1100, rule text says $600, file name says $1000.", "Bellagio poker room, 702.693.7291 (official)"),
    ("Q9", "Venetian guarantees for #3–#6", "Not stated on the official schedule or sheets.", "Venetian poker room, 702.414.7657 (official)"),
    ("Q10", "Single-entry status of the 21 unverified Venetian events", "Their structure sheets were not read. Flight events may allow later-flight entry.", "Agent next pass (read the remaining sheets)"),
    ("Q11", "Wynn WPT formats and Nevada eligibility of the added $1,000,000", "The WPT footnote says ClubWPT Gold is not available in Nevada.", "Wynn poker room (official number on the Wynn poster)"),
    ("Q12", "Your budget ceiling per event", "Filters the ranking and the 8 AM plan.", "You"),
    ("Q13", "Are you 50 or older?", "Seniors events (#24, #32) are 50+ only. Players who are not 50+ forfeit the buy-in and prize money.", "You"),
    ("Q14", "Are bounty and PKO events acceptable?", "They are single-entry on their sheets, but their guarantees include bounties.", "You"),
    ("Q15", "Should off-Strip rooms (Red Rock, Downtown) be included?", "Excluded for now, since you asked for Strip events.", "You"),
    ("Q16", "How fast do you walk, and is 30 minutes a hard limit?", "Changes which hotels pass.", "You"),
    ("Q17", "Which quality measure should count?", "Quality has no official source yet.", "You (choose a source and rule)"),
    ("Q18", "Is the PokerAtlas PRO discount relevant?", "It takes $20 off the first entry only (Valuetown #18 and #58); you must be a PRO member and claim it at the cage.", "You"),
    ("Q19", "Events starting today (Nov 16, 11:10 AM) may already be under way", "The official schedule does not show live status.", "You: check the poker room"),
    ("Q20", "Other Strip rooms: Caesars Palace, Planet Hollywood, MGM Grand, Resorts World", "Their official schedules were not found or not read.", "Agent next pass, or you"),
]


def page_questions():
    ans = "".join(
        f"<tr><td><strong>{esc(q)}</strong></td><td>{esc(a_)}</td><td>" + " · ".join(a(u, l) for l, u in srcs) + "</td></tr>"
        for q, a_, srcs in ANSWERED
    )
    open_t = table(["ID", "Missing information", "Why it matters", "How to resolve it"], [[esc(i), esc(q), esc(w), esc(h)] for i, q, w, h in OPEN], "open")
    body = (
        intro("Questions, information, and answers",
              "Answered items cite official sources. Open items list what I cannot finish without you or a further check. Nothing here is a guess.")
        + f'<section class="panel"><h2>Known (with official sources)</h2><div class="tablewrap"><table class="wide"><thead><tr><th>Question</th><th>Answer</th><th>Sources</th></tr></thead><tbody>{ans}</tbody></table></div></section>'
        + section("Missing or needs a decision", open_t)
    )
    return layout("Questions", "questions.html", body)


# ---------- PAGE: suggestions ----------
SUGGESTIONS = [
    ("S1", "Add a trip filter: dates, party size, and budget narrow every table.", "Only events you can attend are shown.", "M", "A) Client-side filter (static site). B) Export and filter in a spreadsheet.", "A; keeps the site static."),
    ("S2", "Store one machine-readable row per event: re-entry, rebuy, add-on, paid chips, flight, eligibility, bounty type.", "Filters and checks become reliable instead of reading prose.", "S", "A) Add the fields to the data file. B) Keep prose only.", "A."),
    ("S3", "Record the date each source was checked and a hash of each official file.", "Shows when a value was last verified and catches changed files.", "S", "A) Dates and hashes only. B) Also keep copies of the PDFs.", "A. Copies would bloat the repo."),
    ("S4", "Capture the official booking total for your exact dates.", "Closes the biggest gap: real nightly cost.", "M", "A) You capture it. B) Agent captures it if the booking pages allow.", "A and B: you give dates; agent tries; you confirm."),
    ("S5", "Replace the public OSRM walk estimate with a documented walking-route source.", "Walk times become reviewable.", "M", "A) Keep distance estimate and a map link. B) Routes API (needs a key).", "A for now."),
    ("S6", "Define a quality rubric with cited sources.", "Quality is priority 2 and is not scored yet.", "M", "A) Official ratings only. B) Official ratings plus reviews.", "Needs your choice (Q17)."),
    ("S7", "Export a chosen day plan as a calendar file.", "Adds the starts to your phone.", "S", "A) ICS file per plan.", "After dates are known."),
    ("S8", "Add a check that every internal link resolves before the site is published.", "Prevents broken pages on Pages.", "S", "A) Script in scripts/check_links.py (added). B) Full CI workflow.", "A now; B later."),
    ("S9", "Track each Flagged item with an owner, status, and resolution date.", "Makes review traceable.", "S", "A) Table on the Flagged page. B) Issue tracker.", "A."),
    ("S10", "Move data out of Python into a validated JSON file.", "Safer edits.", "S", "A) JSON + schema test. B) Keep Python.", "A."),
    ("S11", "Extend coverage to other Strip rooms once their official schedules are read.", "Coverage is Venetian-only now, with Wynn and Bellagio re-entry rows.", "L", "A) Phase 2 after your approval. B) Stop here.", "A, after Q20."),
]


def page_suggestions():
    rows = [[esc(i), esc(s), esc(b), esc(e), esc(o), esc(r), badge("Awaiting your choice", "warn")] for i, s, b, e, o, r in SUGGESTIONS]
    body = intro("Suggestions for review", "Nothing here is implemented yet. Choose the options you want. Each lists the trade-off.") + f'<section class="panel">{table(["ID", "Suggestion", "Benefit", "Effort", "Options", "Recommendation", "Decision"], rows, "sugg")}</section>'
    return layout("Suggestions", "suggestions.html", body)


# ---------- PAGE: flagged ----------
FLAGS = [
    ("F-01", "Bellagio Saturday buy-in conflict: header '$1100 BUY-IN', rule 07 '$600 Buy-in', file name '$1000'. Buy-in left blank.", D.SRC["bellagio_sat"], "Needs review (Bellagio)."),
    ("F-02", "Bellagio Saturday rule 04 names 'Combined Final Day 2 (9/13/26)', a date before this site's as-of date (2026-11-16). Probably stale text.", D.SRC["bellagio_sat"], "Needs review."),
    ("F-03", "Bellagio Saturday blinds table shows '200-4300' at level 3 (typo).", D.SRC["bellagio_sat"], "Minor."),
    ("F-04", "Bellagio poker page notice: 'Tournament play will resume on Saturday, July 26'. That date is in the past.", D.SRC["bellagio_poker"], "Needs review."),
    ("F-05", "Wynn daily sheet says 'Re-entry is NOT allowed' for Friday, yet it allows unlimited $200 rebuys and a $100 add-on.", D.SRC["wynn_daily_structs"], "Classified as rebuy/add-on."),
    ("F-06", "Wynn WPT schedule footnote: $1,000,000 added via ClubWPT Gold, which 'is not available in Nevada'.", D.SRC["wynn_wpt_sched"], "Needs review (Wynn)."),
    ("F-07", "Wynn WPT: Ladies NLH Championship lists $1,100 buy-in, but its footnote says $11,100.", D.SRC["wynn_wpt_sched"], "Conflict; $1,100 shown with the flag."),
    ("F-08", "Venetian: no official guarantee for #3, #4, #5 (RaceDay Stack) and #6. Blank, not filled.", D.SRC["dse_pdf"], "Unverified value."),
    ("F-09", "Venetian: event numbers repeat for flights and Day 2 restarts (#1, #7, #19, #26, #47, #49, #56, #59). Restarts reuse the event number.", D.SRC["dse_pdf"], "Needs review."),
    ("F-10", "Venetian: 21 numbered events have no sheet read in this session (flights, satellites, tag-team, two-day, PLO/Big O).", D.SRC["dse_page"], "Unverified format; not ranked."),
    ("F-11", "Venetian: #35 tag-team requires female/female or female/male teams.", D.SRC["dse_pdf"], "Eligibility; not ranked."),
    ("F-12", "Venetian eligibility: #39 is a women's event (LIPS Ladies); #24, #32 and #49 are 50+ only, and non-50+ players forfeit the buy-in on #24 and #32.", D.SRC["dse_pdf"], "Eligibility."),
    ("F-13", "Venetian PDF and page typos: '(IDAY)' for '(1DAY)', 'LIPS CHAMPIES', 'No LImit'. Cosmetic.", D.SRC["dse_pdf"], "Minor."),
    ("F-14", "Venetian suite rate: 'as low as $119 and $209' does not say which tower each applies to. Conditional on six hours of play or a $300+ buy-in per night.", D.SRC["venetian_suite"], "Needs review."),
    ("F-15", "Wynn resort-fee terms come from an expired 2026 Concours promotion page.", D.SRC["wynn_terms"], "Re-confirm on the live booking page."),
    ("F-16", "Walk-time estimates use an unsourced reference point near the Venetian and an unsourced Wynn origin. Estimates only.", D.SRC["venetian_poker"], "Estimate; not official."),
    ("F-17", "No official MGM Grand poker schedule: official URL returned 'Page not found'.", D.SRC["mgmgrand_404"], "Cannot verify."),
    ("F-18", "ARIA poker page has no schedule; it says to call the room.", D.SRC["aria_poker"], "Cannot verify."),
    ("F-19", "Resorts World: no official poker schedule could be read. The pages opened returned an email template.", "https://www.rwlasvegas.com/poker", "Cannot verify."),
    ("F-20", "Bellagio resort fee and parking: no official page read in this session.", D.SRC["bellagio_poker"], "Unverified; blank."),
    ("F-21", "Lodging tax (13.38%) was not confirmed on an official page, so no fee-plus-tax totals are shown.", D.SRC["venetian_suite"], "Unverified."),
    ("F-22", "Venetian poker page says the room is open 24 hours. Events starting Nov 16 may already have started.", D.SRC["venetian_poker"], "Check live status."),
]

PAGE_LEVEL_UNVERIFIED = [
    ("Bellagio Saturday NLH buy-in", "Conflicting on its own sheet ($1100 / $600 / $1000).", D.SRC["bellagio_sat"]),
    ("Walk time, all hotels", "Estimate only; origin points are not official.", D.OSRM_ROUTES["Wynn"][0]),
    ("Base room rate, all hotels", "No date-specific official rate was read.", D.SRC["venetian_suite"]),
    ("Hotel quality, all hotels", "No official quality source was read.", None),
]


def page_flagged():
    irr = table(["ID", "Irregularity / caveat", "Source link", "Status"],
                [[esc(i), esc(t), a(u, "Source"), badge(s, "warn")] for i, t, u, s in FLAGS], "irr", cls="wide")
    unv_rows = []
    for u in D.UNVERIFIED_VENETIAN:
        unv_rows.append([f'#{u["event"]}', esc(u["date"]), esc(u["start"]), esc(u["name"]), money(u["buyin"]), money(u["gtd"]) if u["gtd"] else UNVER,
                         esc(u["reg_close"]), esc(u["kind"]), esc(u["sheets"]), a(D.SRC["dse_pdf"], "Schedule")])
    unv = table(["Event #", "Date(s)", "Start", "Event (official schedule)", "Buy-in", "Guarantee", "Reg. closes", "Why not ranked", "Sheet(s) not read", "Source"], unv_rows, "unv")
    wpt_rows = [[esc(w["name"]), money(w["buyin"]), money(w["gtd"]) if w["gtd"] else UNVER, esc(w["note"]), a(D.SRC["wynn_wpt_sched"], "Official WPT schedule")] for w in D.WYNN_WPT_UNVERIFIED]
    wpt = table(["Event", "Buy-in", "Guarantee", "Note", "Source"], wpt_rows, "wpt", search=False)
    pl = table(["Item", "Why it is unverified", "Source"], [[esc(a_), esc(b), a(u, "Link") if u else "—"] for a_, b, u in PAGE_LEVEL_UNVERIFIED], "pl", search=False)
    body = (
        intro("Flagged for Review",
              "Irregularities and unverified items, each with a source link so you can check it yourself. Flags do not block the merge.")
        + section("Irregularities and caveats", irr)
        + section("Unverified Venetian events (not ranked)", '<p class="small">These are on the official schedule. Their structure sheets were not read in this session, so their entry rules are not verified.</p>' + unv)
        + section("Wynn WPT World Championship events (formats not read)", '<p class="small">Only the first page of the official WPT schedule was read. Entry formats (flights, re-entry) were not read.</p>' + wpt)
        + section("Unverified across the site", pl)
    )
    return layout("Flagged for Review", "flagged.html", body)


# ---------- PAGE: repo review ----------
REPO = [
    ("Branch", "arena/bafafd7c-poker5 (session branch). Base commit 0ba2e55 'Initial commit' on main.", "git log, git branch"),
    ("Files at start", "Only README.md, which is 8 bytes: '# Poker5' with no trailing newline. No LICENSE, no .gitignore, no docs folder, no Pages config, no build tooling.", "git ls-files; od -c README.md"),
    ("Remote branch", "origin/arena/bafafd7c-poker5 exists after the claim push (verified with git ls-remote).", "git ls-remote origin"),
    ("Coordination board", "COORDINATION.md added in this session with claims for tasks T1–T8 under arena-bafafd7c.", "file check"),
    ("Branch naming", "The coordination text asks for session-<id>/<task> branches. Session rules fix this session to arena/bafafd7c-poker5, so that rule was followed.", "task rules vs. session rules"),
    ("Parallel sessions", "No other session claims exist in COORDINATION.md at the start.", "git show main:COORDINATION.md (not present on main)"),
    ("README quality", "Placeholder only: no description, setup, or build steps.", "README.md"),
    ("Build tooling", "Added scripts/data.py, scripts/build_site.py, scripts/check_links.py. Standard library only; no packages installed.", "git status"),
]


def page_repo():
    rows = [[esc(a_), esc(b), esc(c)] for a_, b, c in REPO]
    body = (
        intro("Repo review", "Checked at the start of the session with local git commands. Items to review manually are listed below, with links.")
        + f'<section class="panel">{table(["Check", "Result", "How checked"], rows, "repo")}</section>'
        + section("Irregularities to review", """<ul>
<li>README is a placeholder and has no trailing newline.</li>
<li>No license file. Decide whether the data may be reused.</li>
<li>GitHub Pages was not configured before this session. It is set up as part of the merge.</li>
<li>The coordination rules are for parallel sessions; this repo had none, so they were applied to this one session.</li>
</ul>""")
    )
    return layout("Repo review", "repo-review.html", body)


# ---------- PAGE: sources ----------
OFFICIAL = [
    ("Venetian DeepStack Extravaganza IV: event page", D.SRC["dse_page"], "Event numbers, dates, start times, structure links (4 pages read)."),
    ("Venetian DeepStack Extravaganza IV: schedule PDF", D.SRC["dse_pdf"], "Buy-ins, guarantees, registration close, chips (both pages read)."),
    ("Venetian structure sheet 1 ($200 Bounty)", D.sheet(1), "House $40, pool $160, $50 bounty, late reg. 8 levels + break; no re-entry language."),
    ("Venetian structure sheet 5 ($300 NLH)", D.sheet(5), "House $58, pool $242 (from earlier read); no re-entry language."),
    ("Venetian structure sheet 6 ($400 NLH)", D.sheet(6), "House $65, pool $335 (from earlier read)."),
    ("Venetian structure sheet 7 ($600 NLH)", D.sheet(7), "House $90, pool $510 (from earlier read)."),
    ("Venetian structure sheet 8 ($200 Valuetown Bounty)", D.sheet(8), "House $40, pool $160, $50 bounty, PokerAtlas PRO $20 off first entry (claim at cage), 21+."),
    ("Venetian structure sheet 11 ($600 Bounty)", D.sheet(11), "House $90, pool $510, $200/$500 bounties; guarantees by event in sheet."),
    ("Venetian structure sheet 15 ($300 Bounty)", D.sheet(15), "House $50, pool $250, $100 bounty, $15K guarantee."),
    ("Venetian structure sheet 16 ($800 Bounty)", D.sheet(16), "House $100, pool $700, $75K guarantee."),
    ("Venetian structure sheet 17 ($600 Seniors)", D.sheet(17), "House $90, pool $510, 50+ only, $40K guarantee, forfeit rule."),
    ("Venetian structure sheet 18 ($200 RaceDay Stack)", D.sheet(18), "House $35, pool $165 (from earlier read)."),
    ("Venetian structure sheet 26 ($400 PLO Bounty)", D.sheet(26), "House $60, pool $340, $100 bounty, $15K guarantee."),
    ("Venetian structure sheet 28 ($600 Big O)", D.sheet(28), "House $90, pool $510, 8-handed, late reg. 8 levels + break."),
    ("Venetian structure sheet 29 ($200 NLH)", D.sheet(29), "House $40, pool $160 (from earlier read)."),
    ("Venetian structure sheet 30 ($200 PKO)", D.sheet(30), "House $40, pool $160, $50 starting bounty, $8K guarantee."),
    ("Venetian structure sheet 34 ($1,100 PKO)", D.sheet(34), "House $130, pool $970, $200 starting bounty, $75K guarantee."),
    ("Venetian poker room page", D.SRC["venetian_poker"], "Location (Palazzo level 2), open 24 hours, self-parking for 3+ hour players."),
    ("Venetian poker suite rates", D.SRC["venetian_suite"], "$55 resort fee per night; rates as low as $119 and $209; play requirement."),
    ("Wynn poker room page", D.SRC["wynn_poker"], "Series dates; daily event summary."),
    ("Wynn daily tournament poster (PDF)", D.SRC["wynn_poster"], "Daily schedule and guarantees."),
    ("Wynn daily tournament structures (PDF, 3 pages)", D.SRC["wynn_daily_structs"], "Re-entry, rebuy, add-on rules; nightly $160 structure (page 3)."),
    ("Wynn WPT World Championship schedule (PDF, page 1 of 2)", D.SRC["wynn_wpt_sched"], "Dates, buy-ins, guarantees; ClubWPT Gold footnote."),
    ("Wynn terms: resort fee (expired 2026 promotion)", D.SRC["wynn_terms"], "$55 plus tax resort fee for Wynn Resort King and Two Queens."),
    ("Bellagio poker page", D.SRC["bellagio_poker"], "Room phone (702.693.7291); links to Friday, Saturday, Sunday PDFs."),
    ("Bellagio Friday NLH $600 (PDF)", D.SRC["bellagio_fri"], "Re-entry through level 8; $40 gratuity buys 15,000 chips."),
    ("Bellagio Saturday NLH (PDF)", D.SRC["bellagio_sat"], "Flights; header and rule text conflict; $40 gratuity buys 20,000 chips."),
    ("Bellagio Sunday H.O.R.S.E. $400 (PDF)", D.SRC["bellagio_sun"], "$340 pool, $35 house, $25 gratuity buys 15,000 chips; re-entry through level 8."),
    ("ARIA poker page", D.SRC["aria_poker"], "No schedule; call the room."),
    ("MGM Grand poker URL", D.SRC["mgmgrand_404"], "'Page not found' (checked)."),
    ("WSOP official schedule", D.SRC["wsop_schedule"], "No WSOP Strip events Nov–Dec 2026 (checked earlier in session)."),
]
THIRD = [
    ("OpenStreetMap Nominatim (geocoding)", "https://nominatim.openstreetmap.org/", "Coordinates for hotels; not official."),
    ("OSRM public demo router (foot profile)", "https://router.project-osrm.org/", "Walk-distance estimates; durations not used."),
]



def page_sources():
    off = table(["Official source", "Link", "Used for"], [[esc(x), a(y, y), esc(z)] for x, y, z in OFFICIAL], "src-off")
    third = table(["Non-official (estimates only)", "Link", "Used for"], [[esc(x), a(y, y), esc(z)] for x, y, z in THIRD], "src-3p", search=False)
    body = intro("Sources", "Every official source was opened on 2026-11-16. Non-official sources are used only for walk-time estimates.") + section("Official sources", off) + section("Non-official sources (estimates only)", third)
    return layout("Sources", "sources.html", body)


CSS = """
:root{--ink:#14202b;--mut:#5b6b78;--line:#dfe6ec;--bg:#f7f9fb;--card:#fff;--brand:#1f5f8b;--ok:#1b7f4b;--warn:#8a5a00;--x:#8a2c2c}
*{box-sizing:border-box}
body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--brand)}
.top{background:#fff;border-bottom:1px solid var(--line);padding:12px 20px;position:sticky;top:0;z-index:5}
.brand{display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
.brand a{font-weight:700;color:var(--ink);text-decoration:none;font-size:17px}
.asof{color:var(--mut);font-size:13px}
nav{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
nav a{padding:5px 9px;border-radius:6px;text-decoration:none;color:var(--ink);background:#eef3f7;font-size:13px}
nav a.active{background:var(--brand);color:#fff}
main{max-width:1280px;margin:0 auto;padding:18px 20px}
.intro h1{font-size:24px;margin:6px 0 4px}
.lead{color:var(--mut);margin:0 0 14px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.panel h2,h2{font-size:18px;margin:14px 0 8px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:12px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.kv{font-size:26px;font-weight:700;color:var(--brand)}
.kl{color:var(--mut);font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:12px 0 30px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;text-decoration:none;color:var(--ink)}
.card:hover{border-color:var(--brand)}
.card h3{margin:0 0 6px;font-size:16px;color:var(--brand)}
.card p{margin:0;color:var(--mut);font-size:14px}
.card.warnc{border-left:5px solid var(--warn)}
.tools{margin:6px 0 8px}
input[type=search]{padding:7px 10px;border:1px solid var(--line);border-radius:6px;min-width:260px;font:inherit}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#f1f5f8;white-space:nowrap}
tbody tr:nth-child(even){background:#fbfcfd}
table.wide td{min-width:110px}
.badge{display:inline-block;padding:1px 7px;border-radius:999px;font-size:12px;font-weight:600;margin:1px 2px;white-space:nowrap}
.badge.ok{background:#e4f5ec;color:var(--ok)}
.badge.warn{background:#fdf1dc;color:var(--warn)}
.badge.x{background:#f8e4e4;color:var(--x)}
.small{color:var(--mut);font-size:12.5px}
.summary li{margin:0 0 10px}
footer{max-width:1280px;margin:20px auto;padding:0 20px 40px;color:var(--mut);font-size:13px}
ul{padding-left:20px}
"""

JS = """
(function(){
  document.querySelectorAll('input[data-filter]').forEach(function(inp){
    var t=document.getElementById(inp.getAttribute('data-filter'));
    if(!t) return;
    inp.addEventListener('input',function(){
      var q=inp.value.toLowerCase();
      t.querySelectorAll('tbody tr').forEach(function(r){
        r.style.display = r.textContent.toLowerCase().indexOf(q)>-1 ? '' : 'none';
      });
    });
  });
})();
"""


def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    with open(os.path.join(OUT, "assets", "app.js"), "w", encoding="utf-8") as f:
        f.write(JS)
    with open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")
    pages = {
        "index.html": page_index(),
        "single-entry.html": page_single(),
        "multi-entry.html": page_multi(),
        "schedule.html": page_schedule(),
        "hotels.html": page_hotels(),
        "questions.html": page_questions(),
        "suggestions.html": page_suggestions(),
        "flagged.html": page_flagged(),
        "repo-review.html": page_repo(),
        "sources.html": page_sources(),
    }
    for name, content in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"wrote {len(pages)} pages to {OUT}")


if __name__ == "__main__":
    main()
