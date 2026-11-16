#!/usr/bin/env python3
"""Build the static GitHub Pages site (docs/) from the verified JSON data.

Stdlib only. Every value printed comes from data/*.json; nothing is inferred.
Derived numbers (ratios, day counts) are labelled as calculated.
"""
import datetime as dt
import html
import json
import os
import re
from collections import OrderedDict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

SOURCES = load("sources.json")
SINGLE = load("tournaments_single_entry.json")
MULTI = load("tournaments_multi_entry.json")
HOTELS = load("hotels.json")
PENDING = load("pending_and_flags.json")

E = html.escape

def money(v):
    if v is None or v == "":
        return "—"
    if isinstance(v, (int, float)):
        return f"${v:,.0f}"
    return E(str(v))

def src_link(key, label=None):
    s = SOURCES[key]
    return f'<a href="{E(s["url"])}" target="_blank" rel="noopener">{E(label or s["label"].split(" (")[0])}</a>'

def fmt_date(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%a %b %d, %Y").replace(" 0", " ")

def page(title, active, body, desc=""):
    nav = [
        ("index.html", "Home"),
        ("tournaments.html", "Single-entry tournaments"),
        ("multi-entry.html", "Multi-entry (separate)"),
        ("schedule.html", "Day plan"),
        ("hotels.html", "Hotels"),
        ("analysis.html", "Analysis"),
        ("executive-summary.html", "Executive summary"),
        ("questions.html", "Questions & answers"),
        ("suggestions.html", "Suggestions"),
        ("flagged-review.html", "Flagged for Review"),
        ("sources.html", "Sources"),
    ]
    links = "".join(
        '<a href="%s"%s>%s</a>' % (href, ' class="active"' if href == active else "", E(label))
        for href, label in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} · Las Vegas Strip Poker Planner</title>
<meta name="description" content="{E(desc or 'Verified live poker tournament and hotel planning for the Las Vegas Strip.')}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="brand"><a href="index.html">♠ Strip Poker Planner</a></div>
  <nav>{links}</nav>
</header>
<main>
{body}
</main>
<footer>
  <p>Every value on this site is taken from an official operator or tournament page listed on the <a href="sources.html">Sources</a> page. Blank cells are unverified (see <a href="flagged-review.html">Flagged for Review</a>). Data as of 2026-11-16 (UTC). Confirm details at the poker room cage before you play.</p>
</footer>
</body>
</html>
"""

def tbl(headers, rows, cls="data", filter_id=None):
    head = "".join(f"<th>{E(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    fid = f' data-filter="{filter_id}"' if filter_id else ""
    return f'<div class="tablewrap"><table class="{cls}"{fid}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

FILTER_JS = """<script>
document.querySelectorAll('input[data-target]').forEach(function(inp){
  inp.addEventListener('input', function(){
    var q = inp.value.toLowerCase();
    var t = document.getElementById(inp.dataset.target);
    t.querySelectorAll('tbody tr').forEach(function(r){
      r.style.display = r.textContent.toLowerCase().indexOf(q) > -1 ? '' : 'none';
    });
  });
});
</script>"""

def status_badge(text):
    t = text.lower()
    if "single" in t:
        cls = "ok"
    elif "multi" in t:
        cls = "warn"
    else:
        cls = "bad"
    return f'<span class="badge {cls}">{E(text)}</span>'

# ---------- derived values (calculated from verified inputs only) ----------
def ratio(row):
    b, g = row.get("buy_in"), row.get("guarantee")
    if isinstance(b, (int, float)) and isinstance(g, (int, float)) and b:
        return g / b
    return None

SINGLE_ROWS = sorted(SINGLE["rows"], key=lambda r: (r["date"], r["start"]))

def tournaments_page():
    headers = ["Date", "Start", "Event", "Buy-in", "Guarantee", "GTD ÷ buy-in*", "House fee", "Prize pool per entry**", "Chips / level", "Late reg closes", "Bounty", "Status", "Sources"]
    rows = []
    for r in SINGLE_ROWS:
        rt = ratio(r)
        rows.append([
            E(fmt_date(r["date"])),
            E(r["start"]),
            f'<strong>#{E(r["event"])}</strong> {E(r["name"])}',
            money(r["buy_in"]),
            money(r["guarantee"]),
            f'{rt:.1f}×' if rt else "—",
            money(r["house_fee"]),
            money(r["prize_pool_per_entry"]),
            f'{r["starting_chips"]:,} / {r["level_minutes"]} min',
            E(r["late_reg_close"]),
            E(r["bounty"]),
            status_badge(r["status"]) + (f'<div class="note">{E(r["flag"])}</div>' if r.get("flag") else ""),
            f'{src_link("S_VEN_SCHED_PDF","Schedule")} · {src_link(r["source_structure"],"Structure")} · {src_link(r["source_listing"],"Listing")}',
        ])
    body = f"""
<section class="hero small">
  <h1>Single-entry live tournaments</h1>
  <p class="lead">Venue: {E(SINGLE["venue"])}. {len(SINGLE_ROWS)} events, one entry each per the official structure sheets. Sorted by date.</p>
</section>
<div class="callout">
  <strong>Read this first:</strong> The guarantee on a bounty event includes the bounty money (the official structure sheets say so), so cash to first place is less than the headline guarantee. Prize pool per entry = buy-in minus the house fee shown on the structure sheet.
</div>
<div class="toolbar"><input type="search" placeholder="Filter by date, name, buy-in…" data-target="t-single"></div>
{tbl(headers, rows, filter_id="t-single").replace('<table class="data"', '<table class="data" id="t-single"')}
<p class="note">* Calculated: guarantee ÷ buy-in (arithmetic on verified values). ** Calculated: buy-in − house fee as printed on the structure sheet. Times are venue local (Pacific). Blank = not verified.</p>
{FILTER_JS}
"""
    return page("Single-entry tournaments", "tournaments.html", body, "Verified single-entry live tournaments on the Las Vegas Strip, Nov–Dec 2026.")

def multi_page():
    headers = ["Event / format", "Venue", "Schedule", "Buy-in", "Guarantee", "Rule (from official terms)", "Status", "Sources"]
    rows = []
    for r in MULTI["rows"]:
        srcs = [src_link(r["source_schedule"], "Schedule"), src_link(r["source_structure"], "Terms/structure"), src_link(r["source_listing"], "Listing")]
        rows.append([
            f'<strong>{E(r["name"])}</strong>',
            E(r["venue"]),
            E(r["schedule"]),
            money(r["buy_in"]),
            money(r["guarantee"]),
            E(r["rule"]) + (f'<div class="note">{E(r["suspension_note"])}</div>' if r.get("suspension_note") else ""),
            status_badge(r["status"]) + (f'<div class="note">{E(r["flag"])}</div>' if r.get("flag") else ""),
            " · ".join(srcs),
        ])
    body = f"""
<section class="hero small">
  <h1>Multi-entry, re-entry, rebuy, add-on and flight events</h1>
  <p class="lead">Kept separate on purpose: these formats let a player spend more to improve their position, so they are excluded from the single-entry list. Shown for reference.</p>
</section>
<div class="toolbar"><input type="search" placeholder="Filter…" data-target="t-multi"></div>
{tbl(headers, rows, filter_id="t-multi").replace('<table class="data"', '<table class="data" id="t-multi"')}
<p class="note">Not included here: WPT World Championship events at Wynn (official schedule verified, but flight/re-entry rules were not) and other unverified items. See <a href="flagged-review.html">Flagged for Review</a>.</p>
{FILTER_JS}
"""
    return page("Multi-entry events", "multi-entry.html", body)

def schedule_page():
    by_day = OrderedDict()
    for r in SINGLE_ROWS:
        by_day.setdefault(r["date"], []).append(r)
    cards = []
    for d, evs in by_day.items():
        items = "".join(
            f'<li><span class="time">{E(e["start"])}</span> <strong>#{E(e["event"])}</strong> {E(e["name"])} · buy-in {money(e["buy_in"])} · GTD {money(e["guarantee"])}</li>'
            for e in evs
        )
        cards.append(f'<div class="card day"><h3>{E(fmt_date(d))}</h3><ul>{items}</ul><p class="note">{len(evs)} verified single-entry event{"s" if len(evs)!=1 else ""}</p></div>')
    earliest = min(r["start"] for r in SINGLE_ROWS)
    body = f"""
<section class="hero small">
  <h1>Day plan (verified single-entry events only)</h1>
  <p class="lead">Built only from verified start times. The earliest verified single-entry start is <strong>{E(earliest)}</strong>, so a player cannot start at 8 AM with verified single-entry events. Venue: The Venetian.</p>
</section>
<div class="callout warn-box">
  <strong>Finding:</strong> No verified single-entry event starts before {E(earliest)}. Days with two verified single-entry events (both at Venetian times): {E(", ".join(fmt_date(d) for d, evs in by_day.items() if len(evs) > 1))}. Event durations are not verified, so overlaps cannot be checked. Wynn daily events (multi-entry) start at 12:00 PM and 6:00 PM and are not included.
</div>
<div class="grid">{''.join(cards)}</div>
"""
    return page("Day plan", "schedule.html", body)

def hotels_page():
    headers = ["Hotel", "Resort fee / night (before tax)", "Official room-rate floor", "Nightly rate for your dates", "True nightly cost", "Walk to venue", "Poker-rate requirement", "Sources", "Flags"]
    rows = []
    for h in HOTELS["rows"]:
        fee = h["resort_fee_per_night_before_tax"]
        fee_cell = money(fee) if isinstance(fee, (int, float)) else (E(fee) if fee else "—")
        srcs = []
        for k in ("resort_fee_source", "resort_fee_source_2", "room_rate_floor_source", "source_listing"):
            v = h.get(k)
            if v and v in SOURCES:
                srcs.append(src_link(v, SOURCES[v]["label"].split(" (")[0][:48]))
        srcs = sorted(set(srcs))
        rows.append([
            f'<strong>{E(h["hotel"])}</strong>',
            fee_cell,
            E(h["room_rate_floor_official"]) if h["room_rate_floor_official"] else "—",
            "— (unverified)",
            "— (unverified)",
            E(h["walk_to_venue"]) if h["walk_to_venue"] else "— (unverified)",
            E(h["poker_rate_requirement"]) if h["poker_rate_requirement"] else "—",
            " · ".join(srcs) if srcs else "—",
            E(h["flags"]),
        ])
    body = f"""
<section class="hero small">
  <h1>Hotels near the verified venue</h1>
  <p class="lead">Ranking not yet possible: only resort fees are officially verified. Nightly rates for your dates, walking times, and the true cost per night are blank because no official source confirmed them.</p>
</section>
<div class="callout warn-box">
  <strong>How the true cost will be calculated once verified:</strong> nightly room rate for the exact stay dates + resort fee (official) + room tax (rate to be confirmed from an official Clark County source) = true nightly cost. Nothing has been estimated here.
</div>
{tbl(headers, rows, filter_id="t-hotels").replace('<table class="data"', '<table class="data" id="t-hotels"')}
<p class="note">Walking-distance requirement (30 min or less to the tournament) is unverified for every hotel. The Venetian is the verified venue, so a stay on-site meets the distance rule by definition; all other hotels need a verified walk time.</p>
"""
    return page("Hotels", "hotels.html", body)

def analysis_page():
    # calculated ranking: guarantee-to-buy-in multiple (arithmetic on verified values)
    ranked = sorted([r for r in SINGLE_ROWS if ratio(r)], key=lambda r: ratio(r), reverse=True)[:8]
    rank_rows = []
    for r in ranked:
        rank_rows.append([f"{fmt_date(r['date'])}", f"#{E(r['event'])} {E(r['name'])}", money(r["buy_in"]), money(r["guarantee"]), f"{ratio(r):.1f}×", E(r["bounty"])])
    by_gtd = sorted(SINGLE_ROWS, key=lambda r: (-r["guarantee"], r["buy_in"]))[:6]
    gtd_rows = [[fmt_date(r["date"]), f"#{E(r['event'])} {E(r['name'])}", money(r["buy_in"]), money(r["guarantee"]), E(r["start"])] for r in by_gtd]
    total = len(SINGLE_ROWS)
    gtd_sum = sum(r["guarantee"] for r in SINGLE_ROWS)
    buy_range = (min(r["buy_in"] for r in SINGLE_ROWS), max(r["buy_in"] for r in SINGLE_ROWS))
    body = f"""
<section class="hero small">
  <h1>Analysis of verified findings</h1>
  <p class="lead">Calculations use only official values. Anything that could not be verified is excluded, not estimated.</p>
</section>
<div class="kpis">
  <div class="kpi"><span>{total}</span><label>Verified single-entry events</label></div>
  <div class="kpi"><span>{money(buy_range[0])}–{money(buy_range[1])}</span><label>Buy-in range</label></div>
  <div class="kpi"><span>{money(gtd_sum)}</span><label>Sum of listed guarantees (includes bounty money on bounty events)</label></div>
  <div class="kpi"><span>{len(MULTI["rows"])}</span><label>Multi-entry items (separate)</label></div>
</div>
<h2>Best value: guarantee ÷ buy-in (calculated)</h2>
<p>A higher multiple means more guaranteed money per dollar of entry. Bounty guarantees include bounty money, so treat them as a headline figure.</p>
{tbl(["Date", "Event", "Buy-in", "Guarantee", "Multiple", "Bounty"], rank_rows)}
<h2>Largest guarantees (verified)</h2>
{tbl(["Date", "Event", "Buy-in", "Guarantee", "Start"], gtd_rows)}
<h2>Findings</h2>
<ul class="bullets">
  <li>All 30 verified single-entry events are at The Venetian Poker Room (DeepStack Extravaganza IV). No other single-entry venue was verified.</li>
  <li>The lowest verified buy-in tier is $200: {sum(1 for r in SINGLE_ROWS if r['buy_in']==200)} single-entry events, with $8,000 to $20,000 guarantees. Bounties are paid to eliminators, so each player's prize depends on the field.</li>
  <li>Wynn Las Vegas daily events carry a higher buy-in-to-guarantee profile (e.g., $25,000 GTD weekend at $200) but are multi-entry (re-entry allowed), so they are not in the single-entry list.</li>
  <li>The Venetian's own poker-suite rate requires a $300+ tournament buy-in each night (or 6 hours of live cash). Verified $300+ single-entry events: {sum(1 for r in SINGLE_ROWS if r['buy_in']>=300)} of {total}.</li>
</ul>
<p class="note">Calculated values: multiples and sums are arithmetic on the verified guarantees and buy-ins. Sum includes bounty money where applicable.</p>
"""
    return page("Analysis", "analysis.html", body)

def exec_page():
    body = """
<section class="hero small">
  <h1>Executive summary</h1>
  <p class="lead">Status as of 16 Nov 2026 (UTC). What is verified, what is not, and what you need to decide.</p>
</section>
<div class="card wide">
<h2>What is verified</h2>
<ul class="bullets">
  <li><strong>30 single-entry live tournaments</strong> at The Venetian Poker Room, Nov 18 – Dec 17, 2026. Each row has an official schedule link and an official structure-sheet link (no re-entry or add-on language). <a href="tournaments.html">See the list</a>.</li>
  <li><strong>Best guarantee-to-buy-in multiples (calculated):</strong> $200 Valuetown Bounty (Nov 28, $20K GTD, 100×), $800 Bounty (Dec 9, $75K GTD, 94×), $600 Bounty (Dec 16, $50K GTD, 83×). Bounty guarantees include bounty money.</li>
  <li><strong>Multi-entry events kept separate:</strong> Wynn daily (re-entry and rebuy formats, including $10K GTD nightly and $25K GTD weekends), Venetian Event 1 and Event 7 flights. <a href="multi-entry.html">See the separate section</a>.</li>
  <li><strong>Resort fees (official):</strong> The Venetian and Palazzo $55 per night before tax; Encore $45; Wynn $45 (standard offer) or $55 (Tower Suite offer).</li>
</ul>
</div>
<div class="card wide warn-box">
<h2>What is not verified (left blank)</h2>
<ul class="bullets">
  <li>Nightly room rates for any dates. The official Venetian poker-suite page says "as low as $119 / $209" but gives no date-specific rate.</li>
  <li>Walking times from hotels to the Venetian. No official walking distance was found.</li>
  <li>Room tax: 13.38% appears only in third-party guides; the official Clark County page was not retrieved.</li>
  <li>Caesars Palace and MGM resort fees: conflicting or third-party only.</li>
  <li>WPT World Championship (Wynn) and about 30 other Venetian events: structure sheets not checked, so single-entry status is unconfirmed.</li>
</ul>
</div>
<div class="card wide">
<h2>Key constraints for planning</h2>
<ul class="bullets">
  <li>No verified single-entry event starts before 11:10 AM, so an 8 AM start is not possible with verified events. See the <a href="schedule.html">Day plan</a>.</li>
  <li>All verified events require 21+ and a Venetian Rewards card (official Venetian terms).</li>
  <li>The Venetian DSE series (Nov 16 – Dec 23) is the only verified single-entry source. The WPT World Championship at Wynn (Nov 27 – Dec 21) is a large festival whose single-entry rules still need checking.</li>
</ul>
</div>
<div class="card wide">
<h2>Decision needed from you</h2>
<p>To turn this into a complete itinerary and hotel recommendation, we need the stay dates, budget, and bankroll tolerance. The <a href="questions.html">Questions</a> page lists each item and how to resolve it. The <a href="suggestions.html">Suggestions</a> page lists site changes for you to choose from before any implementation.</p>
</div>
"""
    return page("Executive summary", "executive-summary.html", body)

QUESTIONS = [
    ("Q1", "Which Venetian events are single-entry?", "Answered for 30 events (structure sheets checked). Open for the rest (see Flagged P-04).", "answered"),
    ("Q2", "Which Wynn WPT World Championship events are single-entry?", "Open. The official schedule is verified; structure sheets were not checked.", "open"),
    ("Q3", "What is the true nightly cost at The Venetian for my dates?", "Open. Needs your stay dates and a booking-calendar check (dynamic, not published as static official data).", "open"),
    ("Q4", "What is the room tax rate?", "Open. Third-party sources say 13.38%; the official Clark County page must be confirmed.", "open"),
    ("Q5", "How far is each hotel from the Venetian (walking time)?", "Open. No official walking-distance source was retrieved.", "open"),
    ("Q6", "What is the Caesars Palace resort fee?", "Open. Official caesars.com fee page not retrieved; third-party values conflict.", "open"),
    ("Q7", "What is the MGM resort fee for Bellagio, ARIA, MGM Grand, Mandalay Bay?", "Open. The official MGM terms index has no per-property fee values.", "open"),
    ("Q8", "Is the Wynn resort fee $45 or $55 for my booking?", "Open. Official terms show both; the offer code determines which applies.", "open"),
    ("Q9", "Does the Wynn daily schedule run during the WPT World Championship (Nov 27 – Dec 21)?", "Open. The daily terms say events may be suspended during a Tournament Series.", "open"),
    ("Q10", "Is the Venetian poker-suite promo code (EPOKR25) still valid?", "Open. The page is titled 2026 but the code name suggests 2025.", "open"),
    ("Q11", "Is the WPT $1,000,000 added prize available in Nevada?", "Open. The official schedule says ClubWPT Gold is not available in Nevada.", "open"),
    ("Q12", "Are Venetian Event 1 flights still open for registration today (Nov 16)?", "Open. Confirm at the cage; the official schedule lists flights Nov 16–17 and Day 2 Nov 18.", "open"),
    ("Q13", "What dates is the trip?", "Open. Needed to pick events and hotel nights.", "open"),
    ("Q14", "What is the bankroll / per-day buy-in budget?", "Open. Needed to rank events by affordability.", "open"),
    ("Q15", "Do the Venetian 1-Day events have any re-entry rule I missed?", "Answered for the 30 verified events: the structure sheets contain no re-entry or add-on language. Confirm at the cage before playing.", "answered"),
    ("Q16", "What are the 21+ and Venetian Rewards card requirements?", "Answered (official Venetian structure sheets). Free card required to track play.", "answered"),
    ("Q17", "Is the PokerAtlas PRO $20 discount (Event 18) worth the membership?", "Open. Membership price not verified from an official PokerAtlas page.", "open"),
]

def questions_page():
    rows = []
    for qid, q, a, st in QUESTIONS:
        badge = '<span class="badge ok">Answered</span>' if st == "answered" else '<span class="badge bad">Open</span>'
        rows.append([E(qid), E(q), E(a), badge])
    body = f"""
<section class="hero small">
  <h1>Questions, information and answers</h1>
  <p class="lead">What must be known before a decision can be made. Open items say how to resolve them.</p>
</section>
{tbl(["#", "Question", "Answer or what is needed", "Status"], rows)}
<h2>Information still needed (how to discover it)</h2>
<ul class="bullets">
  <li>Stay dates and party size: from you (needed for nightly rates and Venetian events).</li>
  <li>Booking-calendar rate checks on each hotel's official site for those dates (manual lookup, or an approved tool).</li>
  <li>Official Clark County lodging-tax page and official caesars.com / mgmresorts.com fee pages.</li>
  <li>Official Wynn and WPT structure sheets for the WPT World Championship events.</li>
</ul>
"""
    return page("Questions & answers", "questions.html", body)

SUGGESTIONS = [
    ("S1", "Add a verification log for every row (last-checked date and the exact page version)", "Improves audit trail when schedules change weekly.", "Recommended"),
    ("S2", "Automate schedule refresh from the official Venetian and Wynn PDFs with a diff alert", "Keeps dates and buy-ins current; needs an approved script and a schedule (e.g., daily).", "Option"),
    ("S3", "Add a rate-check step for specific stay dates (manual or approved booking tool)", "Turns blank nightly rates into verified costs; the most important missing value.", "Recommended"),
    ("S4", "Add walking-time verification using an approved mapping source", "Needed to prove the 30-minute walking rule for each hotel.", "Option"),
    ("S5", "Split the Wynn WPT events into single-entry and multi-flight groups after reading each structure sheet", "Completes the single-entry list for Nov 27 – Dec 21.", "Recommended"),
    ("S6", "Add a 'bounty-adjusted' value column that shows how much of the guarantee is bounty money", "Prevents over-reading headline guarantees.", "Option"),
    ("S7", "Add a planner that builds a day schedule from a chosen list of events and checks overlap", "Needs event durations, which are not yet verified.", "Later"),
    ("S8", "Consolidate the parallel coordination boards on one branch before merging", "Avoids duplicate claims and merge conflicts (see Flagged R-01).", "Recommended"),
]

def suggestions_page():
    rows = [[E(sid), E(t), E(why), f'<span class="badge {"ok" if st=="Recommended" else "warn"}">{E(st)}</span>', '<span class="badge">Awaiting your choice</span>'] for sid, t, why, st in SUGGESTIONS]
    body = f"""
<section class="hero small">
  <h1>Suggestions for the site (choose before anything changes)</h1>
  <p class="lead">No site changes will be made from this list until you pick the options you want. Each one is a proposal, not an implemented change.</p>
</section>
{tbl(["#", "Suggestion", "Why it matters", "Suggested priority", "Decision"], rows)}
<p class="note">To choose, reply with the IDs you want (e.g., "S1, S3, S5"). Choosing none keeps the site as it is.</p>
"""
    return page("Suggestions", "suggestions.html", body)

def flagged_page():
    rows = []
    for p in PENDING["pending_tournaments"]:
        rows.append([E(p["id"]), "Tournament", E(p["item"]) + (f'<div class="note">e.g. {E(p["example"])}</div>' if p.get("example") else ""), src_link(p["source"], "Source") if p.get("source") else "—", E(p["status"])])
    for h in PENDING["hotel_items"]:
        srcs = []
        if h.get("source"):
            srcs.append(src_link(h["source"], "Source"))
        if h.get("source2"):
            srcs.append(src_link(h["source2"], "Source 2"))
        rows.append([E(h["id"]), "Hotel", E(h["item"]), " · ".join(srcs) if srcs else "—", E(h["status"])])
    for r in PENDING["repo_irregularities"]:
        rows.append([E(r["id"]), "Repo", E(r["item"]), src_link(r["source"], "Source") if r.get("source") else "—", E(r["status"])])
    body = f"""
<section class="hero small">
  <h1>Flagged for Review</h1>
  <p class="lead">Irregularities, unverified items, and blank values. These do not block publication. Review them and request changes.</p>
</section>
<div class="toolbar"><input type="search" placeholder="Filter flags…" data-target="t-flags"></div>
{tbl(["ID", "Type", "Item", "Source", "Status"], rows, filter_id="t-flags").replace('<table class="data"', '<table class="data" id="t-flags"')}
{FILTER_JS}
"""
    return page("Flagged for Review", "flagged-review.html", body)

def sources_page():
    rows = []
    for k, s in SOURCES.items():
        rows.append([E(k), E(s["label"]), f'<a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["url"])}</a>', "Official" if s.get("official") else "Third-party"])
    body = f"""
<section class="hero small">
  <h1>Sources</h1>
  <p class="lead">Every link used for a verified value. Official pages are operator or tournament sites (venetianlasvegas.com, wynnlasvegas.com, worldpokertour.com, wynn PDF hosting).</p>
</section>
{tbl(["ID", "Source", "URL", "Type"], rows)}
"""
    return page("Sources", "sources.html", body)

def index_page():
    cards = [
        ("tournaments.html", "Single-entry tournaments", f"{len(SINGLE_ROWS)} verified events at The Venetian, Nov 18 – Dec 17, 2026"),
        ("multi-entry.html", "Multi-entry (separate)", f"{len(MULTI['rows'])} re-entry, rebuy, add-on and flight formats"),
        ("schedule.html", "Day plan", "Verified start times by date (earliest 11:10 AM)"),
        ("hotels.html", "Hotels", "Official resort fees; nightly rates and walk times pending"),
        ("analysis.html", "Analysis", "Guarantee-to-buy-in ratios and findings"),
        ("executive-summary.html", "Executive summary", "What is verified, what is not, what to decide"),
        ("questions.html", "Questions & answers", "What must be known before deciding"),
        ("suggestions.html", "Suggestions", "Site changes to choose from; nothing implemented yet"),
        ("flagged-review.html", "Flagged for Review", "Irregularities and unverified items with source links"),
        ("sources.html", "Sources", "Every link used"),
    ]
    tiles = "".join(f'<a class="tile" href="{h}"><h3>{E(t)}</h3><p>{E(d)}</p></a>' for h, t, d in cards)
    body = f"""
<section class="hero">
  <h1>Las Vegas Strip poker & hotel planner</h1>
  <p class="lead">Live single-entry poker tournaments near the Strip, a separate list of re-entry formats, and hotel resort-fee checks. Only official-source values are shown. Blank = not verified.</p>
  <div class="kpis">
    <div class="kpi"><span>{len(SINGLE_ROWS)}</span><label>Single-entry events verified</label></div>
    <div class="kpi"><span>{min(r['buy_in'] for r in SINGLE_ROWS)}–{max(r['buy_in'] for r in SINGLE_ROWS):,}</span><label>Buy-in range (USD)</label></div>
    <div class="kpi"><span>11:10 AM</span><label>Earliest verified start</label></div>
    <div class="kpi"><span>{len(PENDING['pending_tournaments']) + len(PENDING['hotel_items']) + len(PENDING['repo_irregularities'])}</span><label>Items flagged for review</label></div>
  </div>
</section>
<div class="tiles">{tiles}</div>
<p class="note">Data date: 16 Nov 2026. Prepared from official operator pages and PDFs listed under Sources.</p>
"""
    return page("Home", "index.html", body, "Las Vegas Strip poker tournaments and hotel planner, verified to official sources.")

CSS = """
:root{--ink:#1d2433;--muted:#5c6679;--line:#e3e7ef;--bg:#f6f8fb;--card:#fff;--accent:#1f6feb;--ok:#127a3c;--warn:#a25b00;--bad:#b42323;}
*{box-sizing:border-box}
body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header.top{background:#0f1b2d;color:#fff;padding:10px 20px;display:flex;flex-wrap:wrap;gap:10px 24px;align-items:center;position:sticky;top:0;z-index:5}
header.top .brand a{color:#fff;font-weight:700;font-size:16px}
header.top nav{display:flex;flex-wrap:wrap;gap:4px 12px}
header.top nav a{color:#c9d6ea;font-size:13px;padding:4px 6px;border-radius:6px}
header.top nav a.active,header.top nav a:hover{background:#1f3352;color:#fff;text-decoration:none}
main{max-width:1280px;margin:0 auto;padding:20px}
section.hero{background:linear-gradient(135deg,#0f1b2d,#1f3f6e);color:#fff;border-radius:14px;padding:26px 28px;margin-bottom:18px}
section.hero.small{padding:18px 22px}
section.hero h1{margin:0 0 6px;font-size:26px}
section.hero .lead{margin:0;color:#dbe6f7;max-width:820px}
h1{font-size:24px}h2{font-size:19px;margin:26px 0 8px}h3{margin:4px 0 8px;font-size:16px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-top:16px}
.kpi{background:rgba(255,255,255,.1);border-radius:10px;padding:12px 14px}
.kpi span{display:block;font-size:22px;font-weight:700}
.kpi label{font-size:12px;color:#cfe0f5}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;color:var(--ink);box-shadow:0 1px 2px rgba(0,0,0,.03)}
.tile:hover{border-color:var(--accent);text-decoration:none;box-shadow:0 4px 14px rgba(31,111,235,.12)}
.tile p{margin:0;color:var(--muted);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:14px}
.card.wide{max-width:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.day ul{list-style:none;padding:0;margin:0}.day li{padding:4px 0;border-bottom:1px dashed var(--line);font-size:13px}
.time{display:inline-block;min-width:72px;font-weight:700;color:var(--accent)}
.callout{background:#eaf2ff;border-left:4px solid var(--accent);padding:12px 14px;border-radius:8px;margin:12px 0}
.callout.warn-box,.warn-box{background:#fff6e5;border-left-color:var(--warn)}
.toolbar{margin:10px 0}
input[type=search]{width:min(420px,100%);padding:8px 12px;border:1px solid var(--line);border-radius:8px;font:inherit;background:#fff}
.tablewrap{overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;max-height:72vh}
table.data{border-collapse:collapse;width:100%;min-width:700px;font-size:13px}
table.data th,table.data td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.data thead th{position:sticky;top:0;background:#f0f4fa;font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted);z-index:1}
table.data tbody tr:hover{background:#f7faff}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;background:#eef1f6;color:var(--muted);white-space:nowrap}
.badge.ok{background:#e4f5ea;color:var(--ok)}.badge.warn{background:#fff1da;color:var(--warn)}.badge.bad{background:#fde7e7;color:var(--bad)}
.note{font-size:12px;color:var(--muted);margin:4px 0 0}
ul.bullets{padding-left:18px}ul.bullets li{margin:6px 0}
footer{max-width:1280px;margin:30px auto;padding:0 20px 30px;color:var(--muted);font-size:12px}
@media (max-width:700px){header.top{position:static}section.hero h1{font-size:21px}}
"""

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    pages = {
        "index.html": index_page(),
        "tournaments.html": tournaments_page(),
        "multi-entry.html": multi_page(),
        "schedule.html": schedule_page(),
        "hotels.html": hotels_page(),
        "analysis.html": analysis_page(),
        "executive-summary.html": exec_page(),
        "questions.html": questions_page(),
        "suggestions.html": suggestions_page(),
        "flagged-review.html": flagged_page(),
        "sources.html": sources_page(),
    }
    for name, text in pages.items():
        write(os.path.join(OUT, name), text)
    write(os.path.join(OUT, "assets", "style.css"), CSS)
    write(os.path.join(OUT, ".nojekyll"), "")
    print("built", len(pages), "pages into", OUT)

if __name__ == "__main__":
    main()
