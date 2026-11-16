#!/usr/bin/env python3
"""Builds the static GitHub Pages site in docs/ from tools/data_source.py.

Every row in the output tables carries a source link. Calculated values are labelled as calculations.
Run:  python3 tools/build.py
"""
import html, json, os, datetime
from collections import OrderedDict
import data_source as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
DATA = os.path.join(OUT, "data")
os.makedirs(DATA, exist_ok=True)

def esc(s):
    return html.escape("" if s is None else str(s))

def money(v):
    if v is None:
        return ""
    return f"${v:,.0f}"

def dt(d):
    return datetime.date.fromisoformat(d).strftime("%a %b %d, %Y")

def link(url, label="Source"):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'

# ---------- Venetian rows ----------
ven_rows = []
for (date, start, ev, name, buyin, gtd, reg, sn, status) in D.VEN:
    pool = D.POOL_PER_ENTRY.get(sn)
    row = OrderedDict(
        date=date, start=start, event_no=ev, name=name, buy_in=buyin,
        guarantee=gtd, reg_close=reg, room="The Venetian / The Palazzo (Poker Room)",
        structure_sheet=D.struct(sn), structure_no=sn,
        status=status,
        source_schedule=D.S_SCHED, source_page=D.S_PAGE,
    )
    if status == "verified":
        row["single_entry"] = "Verified single entry: structure sheet shows no re-entry, rebuy or add-on terms"
    elif status == "unverified":
        row["single_entry"] = "Unverified: structure sheet not reviewed"
    else:
        row["single_entry"] = "Satellite (excluded from ranking)"
    row["prize_pool_per_entry"] = pool[0] if pool else None
    row["pool_source"] = pool[2] if pool else None
    ven_rows.append(row)

# consistency: verified rows must use a structure sheet that was actually read
for r in ven_rows:
    if r["status"] == "verified":
        assert r["structure_no"] in D.STRUCTS_READ, r
    if r["status"] == "unverified":
        assert r["structure_no"] not in D.STRUCTS_READ, r

ranked = []
for r in ven_rows:
    if r["status"] == "verified" and r["guarantee"]:
        ratio = r["guarantee"] / r["buy_in"]
        r["gtd_to_buyin"] = round(ratio, 1)
        if r["prize_pool_per_entry"]:
            r["breakeven_entries"] = round(r["guarantee"] / r["prize_pool_per_entry"])
        ranked.append(r)
ranked_by_ratio = sorted(ranked, key=lambda r: (-r["gtd_to_buyin"], r["buy_in"]))
ranked_by_gtd = sorted(ranked, key=lambda r: (-r["guarantee"], r["buy_in"]))

verified_count = sum(1 for r in ven_rows if r["status"] == "verified")
unverified_count = sum(1 for r in ven_rows if r["status"] == "unverified")
satellite_count = sum(1 for r in ven_rows if r["status"] == "satellite")
earliest_verified = min(r["start"] for r in ven_rows if r["status"] == "verified")

# ---------- WPT (Wynn) rows: all unverified re-entry status ----------
wpt_rows = []
for (date, start, name, buyin, gtd) in D.WPT:
    wpt_rows.append(OrderedDict(
        date=date, start=start, name=name, buy_in=buyin, guarantee=gtd,
        status="unverified", single_entry="Unverified: re-entry terms not reviewed",
        room="Wynn Las Vegas (Poker Room in Encore)",
        source_schedule=D.WPT_SCHED if hasattr(D, "WPT_SCHED") else D.WYNN_WPT_SCHED,
        source_terms=D.WYNN_WPT_STRUCTS))

# ---------- Advantage rows ----------
adv_rows = []
for (days, time, buyin, gtd, atype, note, src) in D.WYNN_DAILY:
    adv_rows.append(OrderedDict(room="Wynn Las Vegas", event=f"NLH daily ({days})", start=time,
                                buy_in=buyin, guarantee=gtd, advantage=atype, note=note, source=src))
for (days, time, buyin, gtd, atype, note, src) in D.CAESARS:
    adv_rows.append(OrderedDict(room="Caesars Palace", event="Daily NLH", start=time,
                                buy_in=buyin, guarantee=gtd, advantage=atype, note=note, source=src))
for (days, time, buyin, note, atype, src, extra) in D.BELLAGIO:
    adv_rows.append(OrderedDict(room="Bellagio", event=f"NLH/HORSE ({days})", start=time,
                                buy_in=buyin, guarantee=None, advantage=atype, note=note, source=src,
                                flag=extra))

# ---------- Hotels ----------
hotel_rows = []
for (prop, room, fee, status, src, stype, note) in D.HOTELS:
    calc = None
    if fee is not None:
        calc = round(fee * (1 + 0.1338), 2)
    hotel_rows.append(OrderedDict(
        property=prop, poker_room=room, resort_fee_before_tax=fee, fee_status=status,
        fee_source=src, fee_source_type=stype, fee_plus_tax_calc=calc,
        room_rate="", room_rate_status="Unverified: no official static rate; dynamic pricing not captured",
        walking_time="", walking_status="Unverified: not measured from an official source",
        notes=note))

# ---------- Serialise data ----------
payload = dict(as_of=D.AS_OF, venetian=ven_rows, wpt=wpt_rows, advantage=adv_rows, hotels=hotel_rows,
               tax_note=D.TAX_NOTE, tax_sources=D.TAX_SOURCES,
               counts=dict(venetian_verified=verified_count, venetian_unverified=unverified_count,
                           venetian_satellites=satellite_count, wpt_rows=len(wpt_rows),
                           advantage_rows=len(adv_rows)))
with open(os.path.join(DATA, "tournaments.json"), "w") as f:
    json.dump(dict(as_of=D.AS_OF, venetian=ven_rows, wynn_wpt=wpt_rows), f, indent=1)
with open(os.path.join(DATA, "advantage.json"), "w") as f:
    json.dump(dict(as_of=D.AS_OF, rows=adv_rows), f, indent=1)
with open(os.path.join(DATA, "hotels.json"), "w") as f:
    json.dump(dict(as_of=D.AS_OF, rows=hotel_rows, tax_note=D.TAX_NOTE, tax_sources=D.TAX_SOURCES), f, indent=1)
with open(os.path.join(DATA, "summary.json"), "w") as f:
    json.dump(payload["counts"] | {"as_of": D.AS_OF, "earliest_verified_start": earliest_verified}, f, indent=1)

# ---------- HTML helpers ----------
NAV = [
    ("index.html", "Dashboard"),
    ("tournaments.html", "Single-entry tournaments"),
    ("advantage.html", "Advantage / not single-entry"),
    ("hotels.html", "Hotels"),
    ("schedule.html", "Schedule"),
    ("analysis.html", "Analysis"),
    ("questions.html", "Questions & open items"),
    ("suggestions.html", "Suggestions (decide)"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
]

def page(filename, title, body, active):
    nav = "".join(
        f'<a href="{href}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for href, label in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | Poker5 Las Vegas Strip</title>
<link rel="stylesheet" href="assets/style.css"></head>
<body>
<header class="top"><div class="brand">Poker5 <span>Las Vegas Strip poker research</span></div>
<div class="asof">Data as of {D.AS_OF} (America/Los_Angeles)</div></header>
<div class="layout">
<nav class="side">{nav}</nav>
<main>
<h1>{esc(title)}</h1>
{body}
</main></div>
<footer>Every value links to an official source unless marked <span class="pill unv">Unverified</span>. Blank = not verified; nothing was inferred.</footer>
<script src="assets/app.js"></script>
</body></html>"""

def table(headers, rows, cls="data", filter_id=None):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    f = f'<input class="filter" data-target="{filter_id}" placeholder="Filter rows (e.g. Bounty, 12/..., $600)">' if filter_id else ""
    return f'{f}<div class="scroll"><table class="{cls}" id="{filter_id or ""}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def pill(kind, text):
    cls = {"ver": "ver", "unv": "unv", "adv": "adv", "sat": "sat", "flag": "flag"}[kind]
    return f'<span class="pill {cls}">{esc(text)}</span>'

def sdate(d):
    return datetime.date.fromisoformat(d).strftime("%a %b %-d")

def stat(label, value, note=""):
    return f'<div class="stat"><div class="v">{esc(value)}</div><div class="l">{esc(label)}</div><div class="n">{esc(note)}</div></div>'

# ---------- Page: tournaments ----------
ven_tbl_rows = []
for r in ven_rows:
    if r["status"] == "verified":
        st = pill("ver", "Verified single entry")
    elif r["status"] == "unverified":
        st = pill("unv", "Unverified")
    else:
        st = pill("sat", "Satellite")
    ven_tbl_rows.append([
        sdate(r["date"]), esc(r["start"]), esc(r["event_no"]), esc(r["name"]),
        money(r["buy_in"]), money(r["guarantee"]) or pill("unv", "none listed"),
        esc(r["reg_close"] or ""), esc(f"#{r['structure_no']}"),
        st,
        link(r["source_schedule"], "Schedule PDF") + " · " + link(r["structure_sheet"], "Structure sheet"),
    ])
tourney_body = f"""
<p class="lede">Venetian DeepStack Extravaganza IV, Nov 16 to Dec 23, 2026. Single entry means one buy-in, with no re-entry, rebuy or add-on terms on the structure sheet. Rows are entry-level only; restarts and final-table rows are in the official PDF and are excluded here.</p>
<div class="grid4">
{stat("Verified single-entry events", verified_count, "structure sheet read")}
{stat("Unverified events", unverified_count, "listed on official schedule; structure not read")}
{stat("Satellites", satellite_count, "excluded from ranking")}
{stat("Wynn WPT rows (unverified)", len(wpt_rows), "re-entry not reviewed")}
</div>
<h2>All Venetian entry-level events</h2>
<p class="note">Status key: <span class="pill ver">Verified single entry</span> = structure sheet read, no re-entry/add-on language. <span class="pill unv">Unverified</span> = official schedule row, structure not read, so single-entry is not confirmed. Blank guarantee = none listed on the official schedule.</p>
{table(["Date","Start","Event #","Event","Buy-in","Guarantee","Reg. closes","Structure","Status","Sources"], ven_tbl_rows, filter_id="ven")}
<h2>Wynn WPT World Championship (Nov 27 to Dec 13 rows read)</h2>
<p class="note">These events are listed on the official WPT schedule. Their re-entry and rebuy terms were not reviewed, so they are <span class="pill unv">Unverified</span> and not ranked. The official structures document (<a href="{esc(D.WYNN_WPT_STRUCTS)}" target="_blank" rel="noopener">WPT structures PDF</a>) should be read for each event before any of them is treated as single entry.</p>
{table(["Date","Start","Event","Buy-in","Guarantee","Status","Sources"], [[sdate(r["date"]), esc(r["start"]), esc(r["name"]), money(r["buy_in"]), money(r["guarantee"]) or pill("unv","none listed"), pill("unv","Unverified"), link(D.WYNN_WPT_SCHED,"WPT schedule PDF")+" · "+link(D.WYNN_WPT_STRUCTS,"WPT structures PDF")] for r in wpt_rows], filter_id="wpt")}
"""
open(os.path.join(OUT, "tournaments.html"), "w").write(page("tournaments.html", "Single-entry tournaments", tourney_body, "tournaments.html"))

# ---------- Page: advantage ----------
adv_tbl = []
for r in adv_rows:
    atype = r["advantage"]
    kind = "unv" if atype == "unverified" else "adv"
    adv_tbl.append([esc(r["room"]), esc(r["event"]), esc(r["start"]), money(r["buy_in"]), money(r["guarantee"]) or pill("unv","none listed") if r["guarantee"] is not None else "", pill(kind, atype), esc(r["note"]) + (f' <em>{esc(r.get("flag"))}</em>' if r.get("flag") else ""), link(r["source"], "Official source")])
adv_body = f"""
<p class="lede">Not single entry, or the extra spending buys an advantage. These are listed separately as you asked. Re-entry, rebuys, add-ons and purchased chips are all counted here.</p>
<div class="grid4">
{stat("Entries in this section", len(adv_rows), "from official sources")}
{stat("Unverified", sum(1 for r in adv_rows if r["advantage"]=="unverified"), "re-entry not reviewed")}
</div>
{table(["Room","Event","Start","Buy-in","Guarantee","Type","Terms (from official text)","Source"], adv_tbl, filter_id="adv")}
<h2>Verification notes</h2>
<ul>
<li>Wynn's Monday-Thursday, Saturday and Sunday events allow re-entry at the entry fee, so they are kept out of the single-entry list.</li>
<li>Bellagio's Saturday heading says $1,100, the file name says $1,000, and the rules allocate $600. The buy-in is recorded as $600 from the rules text; this conflict is in Flagged for Review.</li>
<li>Caesars' $50 add-on and re-entry terms come from the official daily NLH flyer.</li>
</ul>
"""
open(os.path.join(OUT, "advantage.html"), "w").write(page("advantage.html", "Advantage / not single-entry", adv_body, "advantage.html"))

# ---------- Page: hotels ----------
hot_tbl = []
for r in hotel_rows:
    fee_txt = money(r["resort_fee_before_tax"]) if r["resort_fee_before_tax"] is not None else pill("unv", "unverified")
    hot_tbl.append([
        esc(r["property"]), esc(r["poker_room"]), fee_txt,
        pill("ver","Official") if r["fee_source_type"]=="official" else pill("unv","Third-party only"),
        money(r["fee_plus_tax_calc"]) if r["fee_plus_tax_calc"] else "",
        pill("unv", "Blank: unverified"), pill("unv", "Blank: unverified"),
        esc(r["notes"]), link(r["fee_source"], "Fee source"),
    ])
hotel_body = f"""
<p class="lede">The true nightly cost is room rate plus resort fee plus tax. Only Wynn's resort fee is confirmed from an official page. Room rates and walking times cannot be verified from official static sources, so those columns are blank.</p>
<div class="grid4">
{stat("Resort fee confirmed (official)", "1 of 6", "Wynn Las Vegas")}
{stat("Room rates verified", "0", "dynamic pricing")}
{stat("Walking times verified", "0", "not measured")}
{stat("Tax rate", "13.38%", "third-party; official page not retrieved")}
</div>
<p class="note"><strong>Tax:</strong> {esc(D.TAX_NOTE)} Tax sources: {' · '.join(link(u, 'third-party') for u in D.TAX_SOURCES)}.</p>
<p class="note"><strong>Fee + tax (calc)</strong> = resort fee × (1 + 13.38%). It is a calculation, not a quote, and it excludes the room rate.</p>
{table(["Property","Poker room (official location)","Resort fee / night (before tax)","Fee status","Fee + tax (calc)","Room rate / night","Walk to poker room","Notes","Source"], hot_tbl, filter_id="hot")}
"""
open(os.path.join(OUT, "hotels.html"), "w").write(page("hotels.html", "Hotels", hotel_body, "hotels.html"))

# ---------- Page: schedule ----------
sched_rows = []
for r in sorted([r for r in ven_rows if r["status"] in ("verified","unverified")], key=lambda r:(r["date"], r["start"])):
    sched_rows.append([sdate(r["date"]), esc(r["start"]), esc(r["name"]), money(r["buy_in"]),
                       esc(r["reg_close"] or ""), pill("ver","Single entry") if r["status"]=="verified" else pill("unv","Unverified"),
                       link(r["source_schedule"], "Schedule PDF")])
schedule_body = f"""
<p class="lede">Start times are from the official schedule. The earliest verified single-entry start is <strong>{esc(earliest_verified)}</strong>. No verified single-entry event starts at 8:00 AM, so a plan that begins at 8:00 AM cannot be built from verified data.</p>
<h2>Plan logic</h2>
<ul>
<li><strong>Morning anchor:</strong> the 10:10 or 11:10 AM events are the earliest single-entry starts in the verified data. Official pages do not publish finish times, so the length of each day depends on how long you last.</li>
<li><strong>Evening option:</strong> the 5:10 PM bounty events ($200 to $300, verified single entry) are a lower-cost option on the same day. Whether you can play both depends on how long the morning event runs; the official sources do not give that time.</li>
<li><strong>Not included:</strong> Caesars' 10:00 AM and Wynn's 12:00 PM daily events start earlier than most single-entry events, but they allow re-entry, add-ons or rebuys, so they sit in the advantage section.</li>
</ul>
<h2>Single-entry and unverified starts, by date</h2>
{table(["Date","Start","Event","Buy-in","Reg. closes","Status","Source"], sched_rows, filter_id="sch")}
"""
open(os.path.join(OUT, "schedule.html"), "w").write(page("schedule.html", "Schedule", schedule_body, "schedule.html"))

# ---------- Page: analysis ----------
def rrow(r):
    return [sdate(r["date"]), esc(r["start"]), esc(r["name"]), money(r["buy_in"]), money(r["guarantee"]),
            f'{r["gtd_to_buyin"]:,.1f}x', money(r["prize_pool_per_entry"]) if r["prize_pool_per_entry"] else pill("unv","unverified"),
            f'{r["breakeven_entries"]:,}' if r.get("breakeven_entries") else "", link(r["structure_sheet"], f'Structure #{r["structure_no"]}')]
top_ratio = [rrow(r) for r in ranked_by_ratio[:10]]
top_gtd = [rrow(r) for r in ranked_by_gtd[:10]]
analysis_body = f"""
<p class="lede">Analysis uses only verified single-entry Venetian events. The guarantee-to-buy-in ratio is a calculation: guarantee ÷ buy-in. Breakeven entries is also a calculation: guarantee ÷ prize pool per entry from the structure sheet. A guarantee is paid even if the field is small, so a higher breakeven count means more risk that the event runs as an overlay.</p>
<h2>Top 10 by guarantee-to-buy-in ratio (calc)</h2>
{table(["Date","Start","Event","Buy-in","Guarantee","GTD ÷ buy-in (calc)","Prize pool / entry","Breakeven entries (calc)","Structure"], top_ratio)}
<h2>Top 10 by guarantee (verified single-entry)</h2>
{table(["Date","Start","Event","Buy-in","Guarantee","GTD ÷ buy-in (calc)","Prize pool / entry","Breakeven entries (calc)","Structure"], top_gtd)}
<h2>Findings</h2>
<ul>
<li>The highest prize pools are at the Venetian: $1,000,000 for the $2,200 PokerAtlas event (1A on Dec 12, 10:10 AM) and $500,000 for the $800 event (#26) and $1,100 event (#56). The 1A flights are verified single entry.</li>
<li>The best value per dollar is the $800 event (#26, GTD ÷ buy-in 625x) and the $300 event #1 (250x). These are verified single entry and also have large field-size risk; check the breakeven counts.</li>
<li>Verified bounty events ($200 to $300) have $8,000 to $15,000 guarantees. Their GTD ÷ buy-in is 40x to 50x, below the $75,000-guarantee events, but their buy-ins are much lower.</li>
<li>Wynn's cheapest daily events ($200 with $10,000 to $25,000 guarantees) and Caesars' $100 daily events all allow re-entry or add-ons, so they cannot be ranked as single entry.</li>
<li>Bellagio's Friday and Sunday events allow re-entry and sell extra chips for a staff gratuity, so they are excluded from single entry.</li>
</ul>
<h2>Method and limits</h2>
<ul>
<li>Single-entry status is checked only from each event's official structure sheet. Events whose sheets were not read are shown as unverified.</li>
<li>Prize pool per entry is taken from the structure sheet. Two sheets conflict on house fees for the same buy-in: the $300 sheets say $242 and $240 per entry, and the $400 sheets say $330 and $335. Both figures are shown in Flagged for Review.</li>
<li>Room rates, walking distance and nightly hotel costs are not verified and are not used in the rankings.</li>
</ul>
"""
open(os.path.join(OUT, "analysis.html"), "w").write(page("analysis.html", "Analysis", analysis_body, "analysis.html"))


# ---------- Flagged for review ----------
FLAGS = [
 # id, category, item, detail, sources
 ("F01","Irregularity","Bellagio Saturday buy-in conflicts",
  "PDF heading reads $1100 buy-in; the file name reads $1000; the rules allocate a $600 buy-in. Recorded as $600 from the rules text.",
  [D.BEL_SAT]),
 ("F02","Irregularity","Bellagio Saturday PDF lists a past Day 2 date",
  "Rules say 'Combined Final Day 2 (9/13/26)'. That date is before today (2026-11-16) and the PDF may be an old template.",
  [D.BEL_SAT]),
 ("F03","Irregularity","Bellagio poker page weekday does not match the date",
  "Page says tournament play 'will resume on Saturday, July 26'. July 26, 2026 is a Sunday (July 26, 2025 was a Saturday). The page looks stale; the date was not used.",
  [D.BEL_POKER]),
  ("F05","Irregularity","Venetian $300 house fee differs between two structure sheets",
  "Structure #5 withholds $58 (prize pool $242). Structure #10 withholds $60 (prize pool $240). Both are $300 1-Day or Day 1 events. The prize-pool figure used in the breakeven math comes from each event's own sheet.",
  [D.struct(5), D.struct(10)]),
 ("F06","Irregularity","Venetian $400 house fee differs between two structure sheets",
  "Structure #2/#3 withholds $70 (prize pool $330). Structure #6 withholds $65 (prize pool $335).",
  [D.struct(2), D.struct(3), D.struct(6)]),
 ("F07","Irregularity","Venetian series page still shows a finished series",
  "The DeepStack page still references the WPT Fall Festival, which ended Nov 15, 2026, before the as-of date (2026-11-16).",
  [D.S_SERIES]),
 ("F08","Irregularity","Wynn 'Single Day' label conflicts with re-entry terms",
  "Wynn's Mon-Thu and Sat/Sun daily events allow re-entry at the entry fee, so they are excluded from the single-entry list.",
  [D.WYNN_DAILY_STRUCTS]),
 ("F09","Irregularity","Official Wynn links return a 'checked out' page",
  "https://www.wynnlasvegas.com/Casino/Poker was removed, and https://www.wynnlasvegas.com/hotel shows a 'checked out' page. Neither is used as a source.",
  ["https://www.wynnlasvegas.com/Casino/Poker", "https://www.wynnlasvegas.com/hotel"]),
 ("F10","Irregularity","Official Venetian tournaments page returns 404",
  "https://www.venetianlasvegas.com/resort/casino/poker/tournaments.html returns a 404. The working schedule is the DeepStack series page.",
  ["https://www.venetianlasvegas.com/resort/casino/poker/tournaments.html", D.S_SERIES]),
 ("F11","Irregularity","WSOP Las Vegas 2026 has ended; no Las Vegas events on the WSOP schedule for Nov-Dec 2026",
  "The official WSOP.com schedule was checked for Nov 16 to Dec 23, 2026 and lists no Las Vegas events in that window. It was not used as a tournament source.",
  [D.WSOP_SCHED]),
 ("F12","Irregularity","Venetian 'Single Day' events may still include bounties and late registration",
  "Structure sheets list late-registration windows. Late registration was not treated as a re-entry. Confirm with the room if it counts as a second entry.",
  [D.struct(1), D.struct(11)]),
 ("F13","Unverified","Resort fees: Bellagio, ARIA, Venetian, Palazzo, Caesars Palace",
  "No official resort-fee page was retrieved for these properties. Third-party sites conflict: Bellagio and ARIA appear at $50 on one list and $55 on others.",
  [ "https://www.applevacations.com/hotels/bellagio/", "https://www.virginatlantic.com/holidays/holiday-types/city-breaks/hotels/aria-resort-and-casino",
    "https://www.resortfeechecker.com/1443-resort_fee_venetian_resort_las_vegas.html", "https://www.resortfeechecker.com/41245-resort_fee_caesars_palace.html", "https://unleashvegas.com/guides/vegas-basics/resort-fees"]),
 ("F14","Confirmed","Wynn resort fee: official terms used",
  "Official Wynn terms state a $55 resort fee plus tax. The official figure is used; third-party figures are not used for Wynn.",
  [D.WYNN_TERMS]),
 ("F15","Unverified","Clark County lodging tax (13.38%) not confirmed from an official page",
  "The rate is reported by third-party sites that cite Clark County. The official Clark County tax page was not retrieved.",
  D.TAX_SOURCES),
 ("F16","Unverified","Aria has no official daily tournament schedule on its poker page",
  "The official ARIA poker page says daily tournaments must be confirmed by phone at 702.590.7232, and it has no tournament list. Third-party listings were not used.",
  [D.ARIA_POKER]),
 ("F17","Unverified","Resorts World poker page has no tournament schedule",
  "The official Resorts World poker-room page covers dining only. No official tournament schedule was found.",
  [D.RW_POKER]),
 ("F18","Unverified","MGM Grand schedule not confirmed from an official source",
  "Only a PokerAtlas calendar, dated 2025, was found. It is treated as stale and was not used.",
  ["https://www.pokeratlas.com/poker-room/mgm-grand-las-vegas/tournaments"]),
 ("F19","Unverified","Wynn WPT events: re-entry terms not reviewed",
  "46 rows from the official WPT schedule (Nov 27 to Dec 13) are listed, but none was checked against the terms for re-entry. The Dec 13 'Day 1A' row reads '$1,000,000 added*' with no guarantee given in the row; the asterisk was not resolved.",
  [D.WYNN_WPT_SCHED, D.WYNN_WPT_STRUCTS]),
 ("F20","Unverified","Wynn nightly $160 event: structure not reviewed",
  "Listed on the official daily poster. Re-entry terms are unknown, so the event is not placed in either section.",
  [D.WYNN_DAILY_POSTER]),
 ("F21","Unverified","31 Venetian entry-level events have unread structure sheets",
  "These events are on the official schedule (dates, times, buy-ins, guarantees confirmed) but their single-entry status is not confirmed. The status column in Single-entry tournaments shows which ones.",
  [D.S_SCHED]),
 ("F22","Unverified","Room rates and walking times are not verified for any hotel",
  "Official static pages do not publish nightly rates for the dates in question. Walking distances were not measured from an official source. Both columns are blank.",
  [D.BEL_POKER, D.ARIA_POKER, D.CAE_PAGE]),
]

flag_rows = []
for fid, cat, item, detail, srcs in FLAGS:
    cls = {"Irregularity": "flag", "Conflict": "flag", "Unverified": "unv", "Confirmed": "ver"}[cat]
    flag_rows.append([esc(fid), pill(cls, cat), esc(item), esc(detail),
                      " · ".join(link(u, f"Link {i+1}") for i, u in enumerate(srcs))])
flagged_body = f"""
<p class="lede"><strong>Flagged for Review.</strong> These items did not block the site. Each one lists its source links so you can check them. Irregularities are things that look wrong in the source itself. Unverified items are values that could not be confirmed from an official source; they are left blank or marked.</p>
<div class="grid4">
{stat("Irregularities", sum(1 for f in FLAGS if f[1]=="Irregularity"), "in official or third-party sources")}
{stat("Conflicts", sum(1 for f in FLAGS if f[1]=="Conflict"), "two sources disagree")}
{stat("Unverified items", sum(1 for f in FLAGS if f[1]=="Unverified"), "blank or marked")}
{stat("Repo review items", "see REPO_REVIEW.md", "repository-level findings")}
</div>
{table(["ID","Type","Item","What was found","Sources"], flag_rows, filter_id="flags")}
"""
open(os.path.join(OUT, "flagged.html"), "w").write(page("flagged.html", "Flagged for Review", flagged_body, "flagged.html"))
with open(os.path.join(DATA, "flagged.json"), "w") as f:
    json.dump([dict(id=a, type=b, item=c, detail=d, sources=e) for a,b,c,d,e in FLAGS], f, indent=1)

# ---------- Questions & open items ----------
QUESTIONS = [
 ("Q01","Trip dates and number of nights","Unanswered","Needed to price rooms and build a day-by-day plan. Nothing in the official sources depends on your dates; the schedule covers Nov 16 to Dec 23, 2026.","You provide dates."),
 ("Q02","Buy-in budget per day and bankroll","Unanswered","Determines which events fit. The site shows buy-ins but has no budget filter yet.","You provide a budget."),
 ("Q03","Maximum walking time","Answered","You set 30 minutes as the limit.","None needed."),
 ("Q04","How walking time is measured","Unanswered","Official pages publish addresses, not walking times. A measured source is needed (for example a maps service), and that service is not an allowed host in this environment.","Decide a method; see Suggestions S5."),
 ("Q05","Does re-entry or an add-on count as 'spending more for advantage'?","Answered","Yes. You said these go in a separate section, so re-entry, rebuy, add-on and purchased chips are all in the advantage section.","None needed."),
 ("Q06","Is late registration allowed?","Partly answered","Late registration is not a second entry, so it is treated as single entry. Confirm with the room if you disagree.","Confirm with the room."),
 ("Q07","Are satellites in scope?","Assumed","They award seats rather than prize money, so they are excluded from ranking. Confirm if you want them listed.","You confirm."),
 ("Q08","Single-entry status for 31 Venetian events and 46 WPT rows","Open","Requires reading each remaining structure sheet. Doable, but it is a research step to be scheduled.","Next research pass."),
 ("Q09","Single-entry status for Wynn's nightly 6 PM event","Open","Structure sheet not reviewed.","Next research pass."),
 ("Q10","Official resort fees for Bellagio, ARIA, Venetian, Palazzo and Caesars Palace","Open","Only third-party figures found, and some conflict.","Locate official pages."),
 ("Q11","Official Clark County lodging tax","Open","Only third-party sources found.","Locate the official Clark County page."),
 ("Q12","Nightly room rates for your dates","Open","Rates are dynamic and not in static official pages. They need a dated capture from each official booking engine.","Needs your dates (Q01)."),
 ("Q13","Loyalty status that waives resort fees","Open","MGM, Caesars and Wynn tiers can change the fee. Your status is not known.","You provide your rewards tiers."),
 ("Q14","Is an 8:00 AM start a hard requirement?","Answered","No verified single-entry event starts before 10:10 AM. The closest earlier starts (Caesars 10:00 AM and Wynn 12:00 PM) are not single entry.","Confirm or relax the 8:00 AM goal."),
 ("Q15","Are Aria, MGM Grand and Resorts World events wanted if they cannot be verified?","Open","They are listed as unverified in Flagged for Review but not in the tables.","Decide whether to keep them."),
]
q_rows = [[esc(a), esc(b), pill("ver" if c=="Answered" else "unv", c), esc(d), esc(e)] for a,b,c,d,e in QUESTIONS]
questions_body = f"""
<p class="lede">What must be answered before a decision can be made. It lists what we have, what we don't, and what would close each gap.</p>
{table(["ID","Question / information","Status","Notes","Next step"], q_rows, filter_id="qs")}
"""
open(os.path.join(OUT, "questions.html"), "w").write(page("questions.html", "Questions & open items", questions_body, "questions.html"))

# ---------- Suggestions ----------
SUGGESTIONS = [
 ("S1","Add a 'last checked' date and structure-sheet link to every row","Recommended","Makes it obvious how old each value is and where to check it."),
 ("S2","Read the 31 unread Venetian structure sheets and 46 WPT rows, then convert them to verified or excluded","Recommended","Largest gain in accuracy; it is research, not a design change."),
 ("S3","Refresh official schedule PDFs on a schedule (for example weekly) through a GitHub Action, with a diff report","Needs your decision","Keeps the site current but needs a scheduled job."),
 ("S4","Capture nightly room rates for your chosen dates from each official booking engine, with a timestamp","Needs your decision","The only way to get a verified room rate; needs your dates."),
 ("S5","Add a walking-time column measured from a maps service","Needs your decision","Walking times are not on official sites. Requires a maps service that is outside the current allowed hosts."),
 ("S6","Add a trip planner: dates and budget in, a day plan out","Needs your decision","Useful for the goal of playing as many events as possible; adds a page and some logic."),
 ("S7","Add a single-entry filter toggle and CSV download on every table","Recommended","Simple to implement and makes review easier."),
 ("S8","Split satellites into their own page instead of mixing them in the tournament table","Recommended","Keeps the main table clean."),
 ("S9","Run an automated check before every publish (JSON valid, every row has an official source, no broken links)","Recommended","tools/validate.py covers part of this; a CI step would make it automatic."),
 ("S10","Add a 'Changes since last check' log","Needs your decision","Helps you see what moved between checks."),
]
s_rows = [[esc(a), esc(b), pill("ver" if c=="Recommended" else "unv", c), esc(d)] for a,b,c,d in SUGGESTIONS]
suggestions_body = f"""
<p class="lede">These are proposed changes to the site. Nothing here has been implemented. Choose which ones to approve, change or reject.</p>
{table(["ID","Suggestion","Status","Why"], s_rows, filter_id="sug")}
"""
open(os.path.join(OUT, "suggestions.html"), "w").write(page("suggestions.html", "Suggestions (decide)", suggestions_body, "suggestions.html"))

# ---------- Sources ----------
OFFICIAL = [
 (D.S_SCHED, "Venetian DeepStack Extravaganza IV schedule (Nov 16 to Dec 23, 2026)"),
 (D.S_PAGE, "Venetian DeepStack Extravaganza IV page (structure index)"),
 (D.S_SERIES, "Venetian DeepStack series page"),
 (D.S_POKER, "Venetian poker room page"),
 (D.struct(1), "Venetian structure #1 ($200 bounty events)"),
 (D.struct(2), "Venetian structure #2 ($400 1A/1B)"),
 (D.struct(3), "Venetian structure #3 ($400 1A/1B/1C)"),
 (D.struct(5), "Venetian structure #5 ($300 1-Day)"),
 (D.struct(6), "Venetian structure #6 ($400 1-Day)"),
 (D.struct(7), "Venetian structure #7 ($600 1-Day)"),
 (D.struct(10), "Venetian structure #10 ($300 1A/1C)"),
 (D.struct(11), "Venetian structure #11 ($600 bounty)"),
 (D.struct(12), "Venetian structure #12 ($800 1A/1C/1E)"),
 (D.struct(15), "Venetian structure #15 ($300 bounty)"),
 (D.struct(21), "Venetian structure #21 ($2,200 1A)"),
 (D.struct(29), "Venetian structure #29 ($200 1-Day)"),
 (D.struct(35), "Venetian structure #35 ($1,100 1A/1C/1E)"),
 (D.WYNN_DAILY_POSTER, "Wynn daily tournaments poster"),
 (D.WYNN_DAILY_STRUCTS, "Wynn daily tournament terms and structures"),
 (D.WYNN_WPT_SCHED, "Wynn WPT World Championship schedule"),
 (D.WYNN_WPT_STRUCTS, "Wynn WPT World Championship terms"),
 (D.WYNN_TERMS, "Wynn Las Vegas terms page (resort fee $55 plus tax)"),
 (D.BEL_POKER, "Bellagio poker room page"),
 (D.BEL_FRI, "Bellagio Friday $600 NLH PDF"),
 (D.BEL_SAT, "Bellagio Saturday NLH PDF"),
 (D.BEL_SUN, "Bellagio Sunday $400 HORSE PDF"),
 (D.CAE_FLYER, "Caesars Palace daily NLH tournament flyer"),
 (D.CAE_PAGE, "Caesars Palace casino page"),
 (D.ARIA_POKER, "ARIA poker page"),
 (D.RW_POKER, "Resorts World poker room page"),
 (D.WSOP_SCHED, "WSOP official schedule"),
]
THIRD = [
 ("https://www.resortfeechecker.com/1443-resort_fee_venetian_resort_las_vegas.html","Third-party: resort fee for The Venetian (not official)"),
 ("https://www.resortfeechecker.com/1769973-resort_fee_palazzo_venetian.html","Third-party: resort fee for The Palazzo (not official)"),
 ("https://www.resortfeechecker.com/41245-resort_fee_caesars_palace.html","Third-party: resort fee for Caesars Palace (not official)"),
 ("https://www.applevacations.com/hotels/bellagio/","Third-party: Bellagio resort-fee text quoted (not official)"),
 ("https://www.virginatlantic.com/holidays/holiday-types/city-breaks/hotels/aria-resort-and-casino","Third-party: ARIA resort-fee text quoted (not official)"),
 ("https://unleashvegas.com/guides/vegas-basics/resort-fees","Third-party: resort fee list and Clark County tax reference (not official)"),
 ("https://www.roommaster.com/hotel-tax/nevada","Third-party: Nevada hotel tax summary (not official)"),
 ("https://www.pokeratlas.com/poker-room/mgm-grand-las-vegas/tournaments","Third-party: MGM Grand calendar, dated Jan 2025 (not used)"),
]
src_rows = [[link(u, "Open"), esc(desc), pill("ver","Official")] for u, desc in OFFICIAL] + \
           [[link(u, "Open"), esc(desc), pill("unv","Third-party")] for u, desc in THIRD]
sources_body = f"""
<p class="lede">Every official source the site relies on, and the third-party sites that were consulted only for flagged items. Third-party sites are never used as the source for a verified value.</p>
{table(["Link","Description","Type"], src_rows, filter_id="src")}
"""
open(os.path.join(OUT, "sources.html"), "w").write(page("sources.html", "Sources", sources_body, "sources.html"))
with open(os.path.join(DATA, "sources.json"), "w") as f:
    json.dump(dict(official=[dict(url=u, description=d) for u,d in OFFICIAL], third_party=[dict(url=u, description=d) for u,d in THIRD]), f, indent=1)

# ---------- Dashboard ----------
index_body = f"""
<p class="lede">Live single-entry poker tournaments on and near the Las Vegas Strip, with a hotel cost check for each venue. Built from official schedules and structure sheets. Anything that could not be confirmed from an official source is blank or marked Unverified.</p>
<div class="grid4">
{stat("Verified single-entry Venetian events", verified_count, "Nov 16 to Dec 23, 2026")}
{stat("Earliest verified single-entry start", earliest_verified, "no verified event starts at 8:00 AM")}
{stat("Advantage events (not single entry)", len(adv_rows), "re-entry, rebuy, add-on or purchased chips")}
{stat("Hotel resort fees verified", "1 of 6", "Wynn only, from an official page")}
</div>
<h2>Key findings</h2>
<ul>
<li><strong>Best verified single-entry value:</strong> the $800 Venetian event (#26) has a $500,000 guarantee on a $800 buy-in (GTD ÷ buy-in 625x, calc). The $300 event #1 has a $75,000 guarantee (250x, calc).</li>
<li><strong>Biggest prize pool:</strong> the $2,200 PokerAtlas Championship event (#47, 1A on Dec 12 at 10:10 AM) has a $1,000,000 guarantee and is verified single entry.</li>
<li><strong>Most daily events are not single entry:</strong> Wynn's daily events and Caesars' daily events allow re-entry or add-ons. Bellagio's Friday and Sunday events allow re-entry and sell extra chips for a staff gratuity.</li>
<li><strong>8:00 AM:</strong> no verified single-entry event starts before 10:10 AM, so an 8:00 AM all-day plan cannot be built from verified data.</li>
<li><strong>Hotels:</strong> only Wynn's $55 resort fee is confirmed from an official page. Room rates and walking times are not verified and are blank.</li>
</ul>
<h2>Pages</h2>
<div class="cards">
<a class="card" href="tournaments.html"><b>Single-entry tournaments</b><span>{verified_count} verified rows plus unverified rows</span></a>
<a class="card" href="advantage.html"><b>Advantage / not single entry</b><span>Re-entry, rebuys, add-ons, purchased chips</span></a>
<a class="card" href="hotels.html"><b>Hotels</b><span>Resort fees, tax and what is still missing</span></a>
<a class="card" href="schedule.html"><b>Schedule</b><span>Start times and the plan logic</span></a>
<a class="card" href="analysis.html"><b>Analysis</b><span>Ranking, breakeven entries, method</span></a>
<a class="card" href="questions.html"><b>Questions &amp; open items</b><span>What we know and what we still need</span></a>
<a class="card" href="suggestions.html"><b>Suggestions</b><span>Site improvements awaiting your decision</span></a>
<a class="card" href="flagged.html"><b>Flagged for Review</b><span>Irregularities and unverified items with links</span></a>
</div>
<h2>Recommended path</h2>
<ol>
<li>Confirm your trip dates, budget and loyalty tiers (Questions Q01, Q02, Q13).</li>
<li>Read the remaining Venetian structure sheets (Q08) so the single-entry list covers the whole series.</li>
<li>Pick a hotel once official resort fees and dated room rates are captured (Q10, Q12).</li>
</ol>
"""
open(os.path.join(OUT, "index.html"), "w").write(page("index.html", "Las Vegas Strip poker dashboard", index_body, "index.html"))

# ---------- static assets ----------
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print("built all pages")
print("counts", payload["counts"], "earliest verified", earliest_verified)
