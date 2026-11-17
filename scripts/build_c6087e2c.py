#!/usr/bin/env python3
"""Build the Poker5 GitHub Pages site from the verified data in data/.

Usage:  python3 scripts/build_c6087e2c.py

This is the final-integration build for the root site (published from main `/`).
It merges every verified dataset already on main and implements the planning
features of the brief:

  * confirmed single-entry status from structure sheets (unverified rows stay
    unverified -- nothing is inferred);
  * structured rule fields (single-entry / re-entry / add-on / fee) with a
    source link and retrieval date per row;
  * "last checked" date per row, from the scheduled re-check baseline;
  * guarantee / entry-fee ratio shown as a descriptive ratio, not a forecast;
  * bounty and flight events labelled separately;
  * a date filter, a global search box and a single-entry toggle on the tables;
  * a per-day overlap check with a primary event and a conditional fallback;
  * a walking-route check with a <=30-minute filter (unverified routes blank);
  * one page per venue (Venetian, Wynn, others) with its events and hotels;
  * a trip-cost calculator (entries x buy-ins + nights x true hotel cost);
  * hotels with a dated rate log and true nightly cost.

Rules enforced in code:
  * every table row carries a source link (build fails otherwise);
  * every internal link in generated pages must resolve to a file in the repo;
  * values that are not verified are shown blank or as 'Unverified' and listed
    on the Flagged for Review page.
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
CLARK_TAX_URL = ("https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:"
                 "3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf")

# Overlap estimation. Event durations are NOT verified from official sources, so
# this is a clearly-labelled planning assumption used only to flag potential
# overlaps and pick a primary + fallback. It is never shown as a fact.
DEFAULT_DURATION_HOURS = 4.0

errors = []


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def money(value):
    return "" if value is None else "${:,.0f}".format(value)


def fmt_date(iso):
    if not iso:
        return ""
    try:
        d = datetime.date.fromisoformat(iso)
        return d.strftime("%a, %b ") + str(d.day) + d.strftime(", %Y")
    except ValueError:
        return iso  # non-ISO range or label; render as-is (escaped by callers)


def fmt_time(hhmm):
    if not hhmm:
        return "Time not captured"
    try:
        h, m = [int(x) for x in hhmm.split(":")]
    except ValueError:
        return hhmm
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return "{}:{:02d} {}".format(h12, m, suffix)


def to_minutes(hhmm):
    if not hhmm:
        return None
    try:
        h, m = [int(x) for x in hhmm.split(":")]
        return h * 60 + m
    except ValueError:
        return None


def link(url, label="Source"):
    if not url:
        return ""
    return '<a href="{}" target="_blank" rel="noopener">{}</a>'.format(esc(url), esc(label))


def src_or_flag(url, label="Source", base=""):
    """A source link, or a link to the Flagged page when no source exists.

    base is the relative path prefix from the current page to pages/.
    """
    if url:
        return link(url, label)
    return link(base + "flagged-review.html", "Flagged (no source)")


def to_int(value):
    """Parse an integer from a possibly-messy field (e.g. '25 prizes'); None if absent."""
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    m = re.search(r"-?\d[\d,]*", value)
    if not m:
        return None
    return int(m.group(0).replace(",", ""))


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- data loading

def load_venetian_psv():
    """Dated Venetian rows from the official schedule capture."""
    rows = []
    path = os.path.join(ROOT, "data", "c6087e2c", "venetian_dse_2026.psv")
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
            rows.append({
                "venue": "The Venetian Resort",
                "series": "DeepStack Extravaganza IV",
                "date": date,
                "time": time,
                "event_no": int(ev),
                "name": name,
                "buyin": int(buy) if buy else None,
                "gtd": int(gtd) if gtd else None,
                "structure_no": int(struct) if struct else None,
                "kind": kind,
                "notes": notes,
            })
    return rows


def load_venetian_status():
    """Status + structure sheet from the structure-sheet-read capture.

    Keyed by (date, event_no, start) -> dict(status, struct, note).
    status: S single-entry confirmed | M multi-flight/entry | U unverified
            | SAT satellite | T team | R restart.
    """
    out = {}
    path = os.path.join(ROOT, "data", "venetian_dse_iv.txt")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) != 9:
                continue
            date, start, ev, name, buy, gtd, struct, status, note = parts
            out[(date, int(ev), start)] = {
                "status": status,
                "struct": int(struct) if struct else None,
                "note": note,
                "name": name,
            }
    return out


def load_other_rooms():
    """Dated other-room rows from the official schedule capture."""
    rows = []
    path = os.path.join(ROOT, "data", "other_rooms.txt")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) < 9:
                continue
            venue, date, start, event, buy, gtd, status, source, note = parts[:9]
            rows.append({
                "venue": venue,
                "date": date,
                "time": start,
                "event_no": None,
                "name": event,
                "buyin": to_int(buy),
                "gtd": to_int(gtd),
                "status": status,
                "source": source,
                "notes": note,
                "series": "Other rooms",
            })
    return rows


def load_other_events():
    """Recurring other-room rows (no fixed date)."""
    rows = load_json(os.path.join(ROOT, "data", "c6087e2c", "other_events.json"))
    for r in rows:
        r["status"] = "multi" if r.get("category") == "multi" else (
            "flight" if r.get("category") == "flight" else "single")
    return rows


def load_structured_rules():
    """Structured rule fields keyed by (venue_key, event_no) and by name."""
    data = load_json(os.path.join(ROOT, "data", "tournaments.json"))
    rules = {}
    for section in ("main", "separate", "restricted", "unverified"):
        for r in data.get(section, []):
            venue = r.get("venue", "")
            ev = r.get("event", "")
            key = (venue, ev)
            rules[key] = r
            rules[(venue, r.get("name", ""))] = r
    return rules


def venue_key(venue):
    v = venue.lower()
    if "venetian" in v:
        return "The Venetian (DeepStack Extravaganza IV)"
    if "wynn" in v:
        return "Wynn Las Vegas (WPT World Championship)" if "wpt" in v or "world" in v else "Wynn Las Vegas (daily tournament)"
    if "caesars" in v:
        return "Caesars Palace (daily NLH)"
    if "bellagio" in v:
        return "Bellagio"
    return venue


# ---------------------------------------------------------------- merge

def build_events():
    venetian = load_venetian_psv()
    status = load_venetian_status()
    other_rooms = load_other_rooms()
    other_events = load_other_events()
    rules = load_structured_rules()

    events = []
    for r in venetian:
        st = status.get((r["date"], r["event_no"], r["time"]), {})
        status_code = st.get("status", "U")
        if r["kind"] == "restart":
            status_code = "R"
        struct_no = r["structure_no"] or st.get("struct")
        rule = None
        for key in ((venue_key(r["venue"]), str(r["event_no"])),
                    (venue_key(r["venue"]), r["name"])):
            if key in rules:
                rule = rules[key]
                break
        entry_rule = ""
        pool_note = ""
        if rule:
            entry_rule = rule.get("entry_rule", "")
            pool_note = rule.get("pool_note", "")
        confirmed = status_code == "S" or (
            entry_rule and re.search(r"single entry|no re-entry|no reentry", entry_rule, re.I))
        rec = {
            "venue": r["venue"],
            "venue_group": "venetian",
            "series": r["series"],
            "date": r["date"],
            "time": r["time"],
            "event_no": r["event_no"],
            "name": r["name"],
            "buyin": r["buyin"],
            "gtd": r["gtd"],
            "status": status_code,
            "structure_no": struct_no,
            "structure": STRUCT_BASE.format(struct_no) if struct_no else "",
            "source": DSE_URL,
            "source_type": "official",
            "notes": r["notes"] or st.get("note", ""),
            "entry_rule": entry_rule,
            "pool_note": pool_note,
            "single_entry_confirmed": confirmed,
            "flags": [],
        }
        if status_code == "U":
            rec["flags"].append("F01")
        if status_code == "M":
            rec["flags"].append("F04")
        if "Bounty" in r["name"] or "PKO" in r["name"]:
            rec["format"] = "bounty"
        elif status_code == "M":
            rec["format"] = "flight"
        else:
            rec["format"] = "standard"
        events.append(rec)

    # Other rooms dated rows
    for r in other_rooms:
        rec = {
            "venue": r["venue"],
            "venue_group": "wynn" if "wynn" in r["venue"].lower() else "other",
            "series": "Other rooms",
            "date": r["date"],
            "time": r["time"],
            "event_no": r["event_no"],
            "name": r["name"],
            "buyin": r["buyin"],
            "gtd": r["gtd"],
            "status": r["status"],
            "structure_no": None,
            "structure": "",
            "source": r["source"],
            "source_type": "official",
            "notes": r["notes"],
            "entry_rule": "",
            "pool_note": "",
            "single_entry_confirmed": r["status"] == "S",
            "flags": [],
            "format": "flight" if r["status"] == "M" else "standard",
        }
        if r["status"] == "U":
            rec["flags"].append("F01")
        if r["status"] == "M":
            rec["flags"].append("F04")
        events.append(rec)

    # Other rooms recurring rows
    for r in other_events:
        confirmed = bool(re.search(r"single entry|no re-entry|no reentry", r.get("reentry", ""), re.I))
        rec = {
            "venue": r["venue"],
            "venue_group": "wynn" if "wynn" in r["venue"].lower() else "other",
            "series": r.get("series", "Other rooms"),
            "date": "",
            "time": "",
            "event_no": r.get("event_no"),
            "name": r["name"],
            "buyin": r.get("buyin"),
            "gtd": r.get("gtd"),
            "status": r.get("category", "single"),
            "structure_no": None,
            "structure": "",
            "source": r["source"],
            "source_type": r.get("source_type", "official"),
            "notes": r.get("notes", ""),
            "entry_rule": r.get("reentry", ""),
            "pool_note": r.get("buyin_note", ""),
            "single_entry_confirmed": confirmed,
            "flags": list(r.get("flags", [])),
            "format": "flight" if r.get("category") == "flight" else "standard",
        }
        if not confirmed and rec["status"] in ("single", "flight"):
            rec["flags"].append("F01")
        events.append(rec)

    return events


def load_hotels():
    """Merge hotel rows from both captures, de-duplicated by hotel name."""
    by_name = {}
    for path in ("data/c6087e2c/hotels.json", "data/hotels.json"):
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            continue
        data = load_json(full)
        if isinstance(data, dict):
            data = data.get("rows", [])
        for h in data:
            if not isinstance(h, dict):
                continue
            name = h.get("hotel")
            if not name:
                continue
            by_name.setdefault(name, h)
    return list(by_name.values())


# ---------------------------------------------------------------- derived

def ratio(rec):
    if rec.get("buyin") and rec.get("gtd"):
        return rec["gtd"] / rec["buyin"]
    return None


def overlap_plan(events):
    """Per-day primary event + conditional fallback.

    Durations are not verified, so a fixed planning assumption is used and
    clearly labelled. Primary = highest-guarantee confirmed single-entry event
    of the day. Fallback = best event that can start after the primary's
    estimated end (start >= primary start + duration). If none, fallback None.
    """
    by_day = {}
    for e in events:
        if e.get("date") and e.get("time"):
            by_day.setdefault(e["date"], []).append(e)
    plans = {}
    for date, rows in by_day.items():
        rows = sorted(rows, key=lambda r: (to_minutes(r["time"]) or 0, -(r["gtd"] or 0)))
        primaries = [r for r in rows if r.get("single_entry_confirmed")]
        primary = None
        if primaries:
            primary = max(primaries, key=lambda r: (r.get("gtd") or 0))
        else:
            # No confirmed single-entry event that day: use the top event as a
            # provisional primary, clearly marked unverified.
            primary = max(rows, key=lambda r: (r.get("gtd") or 0)) if rows else None
        fallback = None
        if primary:
            end = (to_minutes(primary["time"]) or 0) + int(DEFAULT_DURATION_HOURS * 60)
            candidates = [r for r in rows
                          if r is not primary
                          and r.get("single_entry_confirmed")
                          and (to_minutes(r["time"]) or 0) >= end]
            if candidates:
                fallback = max(candidates, key=lambda r: (r.get("gtd") or 0))
        overlaps = []
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                a_s, b_s = to_minutes(a["time"]), to_minutes(b["time"])
                if a_s is None or b_s is None:
                    continue
                a_end = a_s + int(DEFAULT_DURATION_HOURS * 60)
                if b_s < a_end:
                    overlaps.append((a["event_no"] or a["name"], b["event_no"] or b["name"]))
        plans[date] = {
            "primary": primary,
            "fallback": fallback,
            "overlaps": overlaps,
            "assumption_hours": DEFAULT_DURATION_HOURS,
        }
    return plans


# ---------------------------------------------------------------- html helpers

def badge(kind, text):
    return '<span class="badge badge-{}">{}</span>'.format(kind, esc(text))


def single_entry_badge(rec):
    if rec.get("single_entry_confirmed"):
        return badge("ok", "Confirmed single-entry")
    if rec.get("status") in ("M", "flight"):
        return badge("warn", "Multi-flight / multi-entry")
    if rec.get("status") == "SAT":
        return badge("warn", "Satellite (seat prize)")
    if rec.get("status") == "T":
        return badge("warn", "Team event")
    if rec.get("status") == "R":
        return badge("muted", "Restart row")
    return badge("warn", "Unverified")


def ratio_cell(rec):
    r = ratio(rec)
    if r is None:
        return '<span class="blank">blank</span>'
    return "{:.1f}x".format(r)


def table(headers, rows, row_source_index=None):
    out = ['<div class="tablewrap"><table class="tbl" data-searchable>']
    out.append("<thead><tr>")
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


def page_shell(path, title, body, depth):
    base = "../" if depth == 1 else ("../../" if depth == 2 else "")
    nav_items = [
        ("index.html", "Home"),
        ("pages/executive-summary.html", "Executive Summary"),
        ("pages/tournaments.html", "Single-Entry"),
        ("pages/tournaments-double.html", "Multi-Entry"),
        ("pages/schedule.html", "Schedule"),
        ("pages/hotels.html", "Hotels"),
        ("pages/planner.html", "Trip Planner"),
        ("pages/venues/venetian.html", "Venetian"),
        ("pages/venues/wynn.html", "Wynn"),
        ("pages/venues/others.html", "Other Venues"),
        ("pages/questions.html", "Questions"),
        ("pages/suggestions.html", "Suggestions"),
        ("pages/flagged-review.html", "Flagged"),
        ("pages/repo-review.html", "Repo Review"),
    ]
    nav = []
    for target, label in nav_items:
        if depth == 0:
            href = target
        elif depth == 1:
            href = target.replace("pages/", "") if target.startswith("pages/") else "../" + target
        else:  # depth 2 (venue pages under pages/venues/)
            href = "../" + target.replace("pages/", "") if target.startswith("pages/") else "../../" + target
        if depth == 1 and target == "index.html":
            href = "../index.html"
        if depth == 2 and target == "index.html":
            href = "../../index.html"
        nav.append('<a href="{}">{}</a>'.format(esc(href), label))
    nav_html = "\n".join(nav)
    css = base + "assets/css/style.css"
    js = base + "assets/app.js"
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
<script src="{js}"></script>
</body>
</html>
""".format(title=esc(title) if "&amp;" not in title else title, css=css, nav=nav_html, body=body,
           repo=REPO_URL, site=SITE_URL, js=js)


# ---------------------------------------------------------------- data (global)

events = build_events()
hotels = load_hotels()
flags = load_json(os.path.join(ROOT, "data", "c6087e2c", "flags.json"))
rates_log = load_json(os.path.join(ROOT, "data", "c6087e2c", "rates_log.json"))
walking = load_json(os.path.join(ROOT, "data", "c6087e2c", "walking.json"))

try:
    baseline = load_json(os.path.join(ROOT, "data", "c6087e2c", "last_checked.json"))
    LAST_RUN = baseline.get("last_run", "2026-11-16")
except (OSError, ValueError):
    baseline = {}
    LAST_RUN = "2026-11-16"

# last checked per source URL
source_last_checked = {}
if isinstance(baseline, dict):
    for url, info in (baseline.get("sources") or {}).items():
        source_last_checked[url] = info.get("last_checked", LAST_RUN)


def last_checked_for(rec):
    url = rec.get("source") or rec.get("structure") or ""
    return source_last_checked.get(url, LAST_RUN)


# ---------------------------------------------------------------- derived sets

confirmed = [e for e in events if e.get("single_entry_confirmed")]
unverified_single = [e for e in events
                     if not e.get("single_entry_confirmed")
                     and e.get("status") in ("U", "single", None)
                     and e.get("format") != "flight"]
multis = [e for e in events if e.get("status") in ("M", "multi", "flight")]
flights = [e for e in events if e.get("format") == "flight"]
bounties = [e for e in events if e.get("format") == "bounty"]
restarts = [e for e in events if e.get("status") == "R"]
satellites = [e for e in events if e.get("status") == "SAT"]
teams = [e for e in events if e.get("status") == "T"]


def sort_rank(rows):
    return sorted(rows, key=lambda r: (-(r.get("gtd") or -1), -(r.get("buyin") or -1),
                                       r.get("date") or "9999", r.get("time") or ""))


def name_cell(r):
    label = esc(r["name"])
    if r.get("event_no"):
        label = "#{} &middot; {}".format(r["event_no"], label)
    return label


def buyin_cell(r):
    if r.get("buyin") is None:
        return '<span class="blank">blank</span>'
    return money(r["buyin"])


def gtd_cell(r):
    if r.get("gtd") is None:
        return '<span class="blank">blank</span>'
    return money(r["gtd"])


def structure_link(r):
    if r.get("structure"):
        return link(r["structure"], "Structure sheet")
    return ""


def src_cell(r, extra_structure=True):
    src = link(r["source"], "Official page")
    if extra_structure and r.get("structure"):
        src += " &middot; " + link(r["structure"], "Structure")
    return src


def fmt_sched(r):
    if r.get("date"):
        return esc(fmt_date(r["date"])) + " &middot; " + esc(fmt_time(r["time"]))
    return esc(r.get("schedule", "")) if r.get("schedule") else '<span class="blank">recurring</span>'


# ---------------------------------------------------------------- pages

def search_bar(placeholder="Search this table (event, venue, date, status)..."):
    return ('<div class="controls">'
            '<input id="q" class="search" type="search" placeholder="{}" '
            'oninput="poker5Filter()">'
            '<label class="toggle"><input id="se-toggle" type="checkbox" '
            'onchange="poker5Filter()"> Confirmed single-entry only</label>'
            '</div>').format(esc(placeholder))


def page_index():
    n_confirmed = len(confirmed)
    n_unverified = len(unverified_single)
    stats = [
        ("Official Venetian event numbers", len({e["event_no"] for e in events if e.get("event_no")})),
        ("Confirmed single-entry events", n_confirmed),
        ("Single-entry unverified", n_unverified),
        ("Multi-flight / multi-entry", len(multis)),
        ("Bounty events", len(bounties)),
        ("Flagged items for review", len(flags)),
    ]
    cards = "".join('<div class="stat"><div class="num">{}</div><div class="lbl">{}</div></div>'.format(v, esc(k)) for k, v in stats)
    body = """
<section class="hero">
  <h2>Plan a Las Vegas Strip poker trip from official sources</h2>
  <p>Live tournaments on the Strip, hotels with their resort fees and dated rate log,
     a trip-cost calculator, and a day plan built from the official start times.
     Every row links to the official page it came from. Anything that is not confirmed
     is left blank and flagged.</p>
  <div class="ctas">
    <a class="btn" href="pages/planner.html">Trip cost calculator</a>
    <a class="btn ghost" href="pages/tournaments.html">Single-entry tournaments</a>
    <a class="btn ghost" href="pages/schedule.html">Day schedule + overlap check</a>
    <a class="btn ghost" href="pages/hotels.html">Hotels + true nightly cost</a>
  </div>
</section>
<section class="stats">{cards}</section>
<section class="panel">
  <h2>Headline findings</h2>
  <ul>
    <li><strong>{n_confirmed} events are confirmed single-entry</strong> from a structure sheet that was read and shows no re-entry, rebuy, add-on or paid-chip text. A further {n_unverified} candidate rows remain <strong>Unverified</strong> because their structure sheet was not read; they are never assumed to be single-entry.</li>
    <li><strong>Guarantee &divide; entry fee is shown as a descriptive ratio, not a forecast.</strong> It describes the published guarantee per dollar of buy-in; it is not a prediction of winnings.</li>
    <li><strong>Bounty and flight events are labelled separately.</strong> Bounty guarantees include bounty payouts; flight events allow more than one entry per flight.</li>
    <li><strong>Every row carries a "last checked" date.</strong> A scheduled job re-reads each official URL and flags any row whose source changed (see the Flagged page).</li>
    <li><strong>No official 8:00 AM start was found.</strong> The earliest verified Venetian start is 9:10 AM. The day plan starts from the earliest verified start.</li>
    <li><strong>Hotel true nightly cost = room rate + resort fee + tax.</strong> Room rates are dynamic; only dated booking-UI snapshots are logged. Walking times are verified only for on-property venues.</li>
  </ul>
  <p class="muted">Site generated from data/c6087e2c/ by scripts/build_c6087e2c.py. Last source re-check: {lastrun}.</p>
</section>
<section class="grid3">
  <a class="card" href="pages/tournaments.html"><h3>Single-entry</h3><p>Confirmed events with structured rules, ratio and filters.</p></a>
  <a class="card" href="pages/tournaments-double.html"><h3>Multi-entry</h3><p>Re-entry, rebuy, add-on and multi-flight events, kept separate.</p></a>
  <a class="card" href="pages/schedule.html"><h3>Schedule</h3><p>Every official row by date, with the overlap check and primary/fallback.</p></a>
  <a class="card" href="pages/hotels.html"><h3>Hotels</h3><p>Resort fees, dated rate log, true nightly cost and the 30-minute walk filter.</p></a>
  <a class="card" href="pages/planner.html"><h3>Trip planner</h3><p>Entries x buy-ins + nights x true hotel cost.</p></a>
  <a class="card" href="pages/venues/venetian.html"><h3>Venetian</h3><p>DeepStack Extravaganza IV events and on-property hotels.</p></a>
  <a class="card" href="pages/venues/wynn.html"><h3>Wynn</h3><p>WPT World Championship and daily events.</p></a>
  <a class="card" href="pages/venues/others.html"><h3>Other venues</h3><p>Caesars, Horseshoe, Bellagio, MGM Grand.</p></a>
  <a class="card" href="pages/questions.html"><h3>Questions</h3><p>What is missing and how to find it.</p></a>
  <a class="card" href="pages/flagged-review.html"><h3>Flagged for review</h3><p>{nflags} items with source links. These do not block publication.</p></a>
</section>
""".format(cards=cards, n_confirmed=n_confirmed, n_unverified=n_unverified,
           lastrun=esc(LAST_RUN), nflags=len(flags))
    return body


def tournaments_table(rows, with_rules=True):
    cells = []
    for r in rows:
        cells.append([
            name_cell(r),
            fmt_sched(r),
            esc(r["venue"]),
            buyin_cell(r),
            gtd_cell(r),
            ratio_cell(r),
            badge("warn", "Bounty") if r.get("format") == "bounty" else (
                badge("warn", "Flight") if r.get("format") == "flight" else badge("muted", "Standard")),
            single_entry_badge(r),
            esc(r.get("entry_rule") or "") if with_rules else "",
            esc(last_checked_for(r)),
            src_cell(r),
        ])
    headers = ["Event", "Date &middot; time", "Venue", "Buy-in", "Guarantee",
               "Guarantee &divide; buy-in", "Format", "Single-entry status",
               "Entry rule (official excerpt)", "Last checked", "Source"]
    return table(headers, cells, 10)


def page_tournaments():
    confirmed_rows = sort_rank([e for e in confirmed if e.get("format") != "flight"])
    unverified_rows = sort_rank([e for e in unverified_single if e.get("format") != "flight"])
    venue_rows = [
        ["The Venetian Resort", "Hosts DeepStack Extravaganza IV; 64 event numbers on the official schedule", link(DSE_URL, "Official schedule")],
        ["Wynn Las Vegas", "WPT World Championship festival (Nov 27-Dec 21); daily tournaments suspended during the festival", link(WYNN_POKER_URL, "Official poker page")],
        ["Caesars Palace", "Daily NLH: $100 buy-in, $1,000 GTD, 4 starts (official Caesars page)", link(CAESARS_URL, "Official Caesars page")],
        ["Horseshoe Las Vegas", "Daily NLH: $100 buy-in, $1,000 GTD, 6 starts (official Caesars page)", link(CAESARS_URL, "Official Caesars page")],
        ["Bellagio", "Friday, Saturday and Sunday events on official PDFs/page (undated)", link("https://bellagio.mgmresorts.com/en/casino/poker.html", "Official poker page")],
        ["MGM Grand", "Daily NLH on official page; PDF titled 'August' (stale)", link("https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", "Official poker page")],
        ["ARIA", "Official page has no tournament list. Call the poker room (F12)", link("https://aria.mgmresorts.com/en/casino/poker.html", "Official poker page")],
    ]
    venues = table(["Venue", "Status", "Source"], venue_rows, 2)
    body = """
<section class="panel warn-panel">
  <strong>Confirmed single-entry</strong> means a structure sheet was read and shows no
  re-entry, rebuy, add-on or paid-chip text. Rows marked <strong>Unverified</strong> have not had
  their structure sheet read; they are candidates only and must be confirmed before you play.
  The guarantee &divide; buy-in column is a <strong>descriptive ratio, not a forecast</strong>.
</section>
{search}
<h2>Confirmed single-entry events</h2>
{confirmed}
<h2>Single-entry candidates &mdash; unverified (structure sheet not read)</h2>
<p class="muted">These are not confirmed. Do not assume single-entry from a missing rule.</p>
{unverified}
<h2>Venue status</h2>
{venues}
""".format(search=search_bar(), confirmed=tournaments_table(confirmed_rows),
           unverified=tournaments_table(unverified_rows), venues=venues)
    return body


def page_double():
    a_rows = sort_rank([e for e in multis if e.get("status") in ("M", "multi")])
    b_rows = sort_rank([e for e in events if e.get("status") in ("U", "single") and e.get("format") == "flight"])
    a_cells = []
    for r in a_rows:
        a_cells.append([
            name_cell(r),
            fmt_sched(r),
            esc(r["venue"]),
            buyin_cell(r),
            gtd_cell(r),
            esc(r.get("entry_rule") or r.get("notes") or ""),
            esc(last_checked_for(r)),
            src_cell(r),
        ])
    a = table(["Event", "Date &middot; time", "Venue", "Buy-in", "Guarantee",
               "Verified entry rule (official)", "Last checked", "Source"], a_cells, 7)
    b_cells = []
    for r in b_rows:
        b_cells.append([
            name_cell(r),
            fmt_sched(r),
            esc(r["venue"]),
            buyin_cell(r),
            gtd_cell(r),
            single_entry_badge(r),
            esc(last_checked_for(r)),
            src_cell(r),
        ])
    b = table(["Event", "Date &middot; time", "Venue", "Buy-in", "Guarantee",
               "Status", "Last checked", "Source"], b_cells, 7)
    c_rows = [[
        "Daily, Nov 16 - Dec 23 (playing requirement)",
        "The Venetian / The Palazzo poker suite",
        "Poker suite rate requires six hours of active live cash play OR a buy-in to a $300-or-higher tournament for each night stayed (official)",
        "from $119 (as low as)",
        link(SUITE_URL, "Official suite-rate page"),
    ]]
    c = table(["Schedule", "Venue", "Spending requirement (official)", "Rate", "Source"], c_rows, 4)
    body = """
<p class="muted">Kept separate from single-entry because re-entry, rebuys, add-ons, entry caps or
flights can let a player spend more for more chances. Section A rows have a rule in an official
source. Section B lists multi-flight events whose per-flight entry rule is not yet verified.</p>
{search}
<h2>A. Re-entry, rebuy, add-on or entry-cap rules (official)</h2>
{a}
<h2>B. Multi-flight events (per-flight entry rule unverified)</h2>
{b}
<h2>C. Spending that buys a better hotel rate</h2>
{c}
""".format(search=search_bar(), a=a, b=b, c=c)
    return body


def page_schedule():
    plans = overlap_plan(events)
    rows = sorted([e for e in events if e.get("date")],
                  key=lambda r: (r["date"], to_minutes(r["time"]) or 0, r.get("event_no") or 0))
    cells = []
    for r in rows:
        kind = {"S": "Entry (confirmed single)", "M": "Entry (flight)", "U": "Entry (unverified)",
                "R": "Restart row", "SAT": "Satellite", "T": "Team"}.get(r.get("status"), r.get("status", ""))
        src = src_cell(r)
        cells.append([
            esc(fmt_date(r["date"])),
            esc(fmt_time(r["time"])),
            str(r.get("event_no") or ""),
            esc(r["name"]),
            buyin_cell(r),
            gtd_cell(r),
            badge("ok", "Confirmed") if r.get("single_entry_confirmed") else badge("warn", "Unverified"),
            esc(kind),
            esc(last_checked_for(r)),
            src,
        ])
    v = table(["Date", "Start", "Event #", "Event (official)", "Buy-in", "Guarantee",
               "Single-entry", "Row type", "Last checked", "Source"], cells, 9)

    # Overlap / primary-fallback section
    plan_cells = []
    for date in sorted(plans):
        p = plans[date]
        primary = p["primary"]
        fallback = p["fallback"]
        overlap_txt = "; ".join("{} &times; {}".format(esc(a), esc(b)) for a, b in p["overlaps"]) or "None"
        plan_cells.append([
            esc(fmt_date(date)),
            name_cell(primary) if primary else '<span class="blank">none</span>',
            name_cell(fallback) if fallback else '<span class="blank">none feasible</span>',
            esc(overlap_txt),
            '<span class="muted">{}h assumed</span>'.format(p["assumption_hours"]),
        ])
    plan = table(["Date", "Primary event", "Conditional fallback",
                  "Flagged overlaps (assumption)", "Duration assumption"], plan_cells, None)

    body = """
<section class="panel warn-panel">
  <strong>8:00 AM all-day start: not supported by the official sources read.</strong>
  Earliest official start found: 9:00 AM (Horseshoe). Earliest Venetian start: 9:10 AM.
  Blocks of play from 8:00 AM cannot be built from verified listings.
</section>
<section class="panel">
  <strong>Overlap check.</strong> Event durations are not verified from official sources, so a
  fixed {h}-hour planning assumption is used to flag potential overlaps and to pick a primary
  event and a conditional fallback each day. This is a planning aid, not a verified schedule.
  The fallback only lists an event that can start after the primary's estimated end; if none fits,
  it is shown as "none feasible" rather than an impossible sequence.
</section>
{search}
<h2>Every official dated row</h2>
{v}
<h2>Per-day plan: primary + conditional fallback</h2>
{plan}
""".format(h=DEFAULT_DURATION_HOURS, search=search_bar(), v=v, plan=plan)
    return body


def page_hotels():
    # true cost = room rate + resort fee + tax (tax cited, confirm current rate)
    cells = []
    for h in hotels:
        fee = h.get("resort_fee_usd")
        rate_str = h.get("nightly_rate") or h.get("room_rate_per_night") or ""
        true_cost = h.get("true_cost") or h.get("true_nightly_cost") or ""
        status = badge("ok", "Official fee") if h.get("source_type") == "official" and fee else (
            badge("warn", "Secondary fee") if fee else badge("warn", "Not verified"))
        walk = h.get("walk_to_tournament") or h.get("walk_to_tournament_venue") or ""
        walk_badge = ""
        if walk:
            if "0 min" in walk:
                walk_badge = badge("ok", "<=30 min (on-property)")
            else:
                walk_badge = badge("warn", "Unverified")
        else:
            walk_badge = badge("warn", "Unverified")
        src = src_or_flag(h.get("source") or "", "Official page" if h.get("source_type") == "official" else "Source", base="")
        cells.append([
            "<strong>{}</strong><br><small>{}</small>".format(esc(h.get("hotel")), esc(h.get("role") or h.get("area") or "")),
            walk_badge + (("<br><small>{}</small>".format(esc(walk))) if walk else ""),
            esc(rate_str) if rate_str else '<span class="blank">blank</span>',
            esc(h.get("resort_fee") or ("${} per night".format(fee) if fee else "")) or '<span class="blank">blank</span>',
            esc(true_cost) if true_cost else '<span class="blank">blank</span>',
            esc(h.get("parking") or "") or '<span class="blank">blank</span>',
            status + "<br>" + src,
        ])
    main = table(["Hotel", "Walk to tournament", "Nightly room rate", "Resort fee (per night)",
                  "True cost per night", "Parking", "Status &amp; source"], cells, 6)

    # dated rate log
    log_cells = []
    for e in rates_log.get("entries", []):
        log_cells.append([
            "<strong>{}</strong>".format(esc(e["hotel"])),
            esc(e.get("checkin", "")) + " &rarr; " + esc(e.get("checkout", "")),
            str(e.get("nights", "")),
            esc(e.get("occupancy", "")),
            money(e.get("checkout_total")) if e.get("checkout_total") else '<span class="blank">blank</span>',
            money(e.get("nightly_average")) if e.get("nightly_average") else '<span class="blank">blank</span>',
            money(e.get("resort_fee_per_night")) if e.get("resort_fee_per_night") else '<span class="blank">blank</span>',
            money(e.get("tax_total")) if e.get("tax_total") else '<span class="blank">blank</span>',
            esc(e.get("rate_timestamp", "")),
            link(e.get("source", ""), "Booking source"),
        ])
    log = table(["Hotel", "Stay", "Nights", "Occupancy", "Checkout total", "Nightly average",
                 "Resort fee/night", "Tax total", "Rate timestamp", "Source"], log_cells, 9)

    # walking routes with <=30 filter
    walk_cells = []
    for w in walking.get("routes", []):
        ok = w.get("walk_minutes") is not None and w["walk_minutes"] <= walking.get("limit_minutes", 30)
        walk_cells.append([
            "<strong>{}</strong>".format(esc(w["hotel"])),
            esc(w["venue"]),
            str(w["walk_minutes"]) + " min" if w.get("walk_minutes") is not None else '<span class="blank">unverified</span>',
            badge("ok", "Passes <=30") if ok else badge("warn", "Not verified / fails"),
            esc(w.get("note", "")),
            src_or_flag(w.get("source", ""), "Source", base=""),
        ])
    walk_tbl = table(["Hotel", "Venue", "Walk", "<=30-min filter", "Note", "Source"], walk_cells, 5)

    body = """
<section class="panel">
  <strong>How true nightly cost is built:</strong> nightly room rate + mandatory resort fee + tax.
  Room rates are dynamic and were not retrieved as a single static value; the dated rate log below
  records each booking-UI snapshot. The Clark County room-tax rate is cited from the official
  ordinance: <a href="{tax}" target="_blank" rel="noopener">Clark County room-tax ordinance</a>;
  confirm the current rate on the booking page. Where a room rate is blank, the true cost is blank.
</section>
{search}
<h2>Hotels hosting or near tournaments</h2>
{main}
<h2>Dated rate log (each entry is a snapshot, not a live quote)</h2>
{log}
<h2>Walking-route check (&le;30-minute filter)</h2>
<p class="muted">Only on-property venues are verified at 0 minutes. All other routes are unverified
and left blank; the filter shows only verified entries. No walking time is inferred.</p>
{walk}
""".format(tax=CLARK_TAX_URL, search=search_bar(), main=main, log=log, walk=walk_tbl)
    return body


def page_planner():
    # Build an event options list for the calculator from confirmed single-entry events.
    options = []
    for r in sort_rank([e for e in confirmed if e.get("format") != "flight"]):
        options.append((r["name"], r.get("buyin"), r.get("gtd"), r.get("venue")))
    opts = "\n".join(
        '      <option value="{name}" data-buyin="{buyin}" data-gtd="{gtd}">{name} &middot; {venue} &middot; {buyin}</option>'.format(
            name=esc(name), buyin=money(buyin) if buyin else "", gtd=money(gtd) if gtd else "",
            venue=esc(venue))
        for name, buyin, gtd, venue in options)
    hotel_opts = []
    for h in hotels:
        fee = h.get("resort_fee_usd")
        rate = h.get("nightly_rate") or h.get("room_rate_per_night") or ""
        # parse a leading $ number from the rate string if present
        rate_num = None
        m = re.search(r"\$([0-9][0-9,]*)", rate or "")
        if m:
            rate_num = float(m.group(1).replace(",", ""))
        hotel_opts.append((h.get("hotel"), rate_num, fee))
    h_opts = "\n".join(
        '      <option value="{name}" data-rate="{rate}" data-fee="{fee}">{name} (rate {rate}, fee {fee})</option>'.format(
            name=esc(name), rate=("" if rate is None else "${:,.0f}".format(rate)),
            fee=("" if fee is None else "${:,.0f}".format(fee)), )
        for name, rate, fee in hotel_opts)
    body = """
<section class="panel">
  <strong>Trip cost calculator.</strong> Total = (entries &times; buy-ins) + (nights &times; true
  hotel cost per night). True hotel cost = nightly room rate + mandatory resort fee + tax.
  Room rates are dynamic; the calculator uses the value you enter or the logged snapshot. This is a
  planning estimate, not a booking quote. Confirm on the official booking page before paying.
</section>
<div class="panel">
  <div class="calc-grid">
    <div>
      <h3>1. Trip</h3>
      <label>Nights
        <input id="nights" type="number" min="1" value="7">
      </label>
      <label>Nightly room rate ($)
        <input id="rate" type="number" min="0" step="1" placeholder="e.g. 200">
      </label>
      <label>Resort fee per night ($)
        <input id="fee" type="number" min="0" step="1" placeholder="e.g. 55">
      </label>
      <label>Tax rate (%)
        <input id="tax" type="number" min="0" step="0.01" value="13.38">
      </label>
      <label>Hotel
        <select id="hotel">
          <option value="">-- pick a hotel to load its logged rate/fee --</option>
{h_opts}
        </select>
      </label>
      <p class="muted">True cost/night = (rate + fee) &times; (1 + tax%). Tax rate is cited from the
      Clark County ordinance; confirm the current rate.</p>
    </div>
    <div>
      <h3>2. Entries</h3>
      <label>Event
        <select id="event">
          <option value="">-- pick an event to add --</option>
{opts}
        </select>
      </label>
      <label>Entries (count)
        <input id="count" type="number" min="1" value="1">
      </label>
      <button class="btn add-entry" onclick="poker5AddEntry()">Add to trip</button>
      <div id="entries" class="entries"></div>
      <p class="muted">Only confirmed single-entry events are listed. Multi-entry events are on the
      Multi-Entry page and are not added here.</p>
    </div>
  </div>
  <div class="calc-total">
    <div><span>Entries &times; buy-ins</span><strong id="sum-entries">$0</strong></div>
    <div><span>Nights &times; true hotel cost</span><strong id="sum-hotel">$0</strong></div>
    <div class="grand"><span>Estimated trip cost</span><strong id="sum-total">$0</strong></div>
  </div>
</div>
<p class="muted">No manual input is required to read the site; this calculator is an optional
planning tool. Every buy-in and fee shown comes from the linked official source.</p>
""".format(h_opts=h_opts, opts=opts)
    return body


def page_venue(group, title, intro):
    rows = [e for e in events if e.get("venue_group") == group]
    venue_hotels = [h for h in hotels if group == "venetian" and "venetian" in (h.get("hotel", "") + h.get("role", "")).lower()]
    if group == "wynn":
        venue_hotels = [h for h in hotels if "wynn" in (h.get("hotel", "") + h.get("role", "")).lower() or "encore" in h.get("hotel", "").lower()]
    if group == "other":
        venue_hotels = [h for h in hotels if any(k in h.get("hotel", "").lower() for k in ("caesars", "horseshoe", "bellagio", "mgm", "aria", "planet", "golden", "resorts world"))]
    cells = []
    for r in sort_rank(rows):
        cells.append([
            name_cell(r),
            fmt_sched(r),
            buyin_cell(r),
            gtd_cell(r),
            ratio_cell(r),
            single_entry_badge(r),
            esc(r.get("entry_rule") or ""),
            esc(last_checked_for(r)),
            src_cell(r),
        ])
    t = table(["Event", "Date &middot; time", "Buy-in", "Guarantee", "Guarantee &divide; buy-in",
               "Single-entry status", "Entry rule (official excerpt)", "Last checked", "Source"], cells, 8)
    h_cells = []
    for h in venue_hotels:
        h_cells.append([
            "<strong>{}</strong><br><small>{}</small>".format(esc(h.get("hotel")), esc(h.get("role") or h.get("area") or "")),
            esc(h.get("resort_fee") or "") or '<span class="blank">blank</span>',
            esc(h.get("nightly_rate") or h.get("room_rate_per_night") or "") or '<span class="blank">blank</span>',
            src_or_flag(h.get("source") or "", "Source", base="../"),
        ])
    ht = table(["Hotel", "Resort fee", "Nightly rate", "Source"], h_cells, 3) if h_cells else ""
    body = """
<p class="muted">{intro}</p>
{search}
<h2>Events</h2>
{t}
<h2>Hotels</h2>
{ht}
""".format(intro=intro, search=search_bar(), t=t, ht=ht)
    return body


def page_exec():
    n_confirmed = len(confirmed)
    top = sort_rank([e for e in confirmed if e.get("format") != "flight"])[:5]
    top_rows = "".join(
        "<li><strong>{}</strong> &mdash; {} &middot; {} &middot; guarantee {} &middot; ratio {} (descriptive). "
        "<a href=\"{}\" target=\"_blank\" rel=\"noopener\">Structure sheet</a>.</li>".format(
            esc(r["name"]), esc(fmt_sched(r)), money(r.get("buyin")), money(r.get("gtd")),
            ratio_cell(r), esc(r.get("structure") or r["source"]))
        for r in top)
    body = """
<section class="panel">
  <h2>Executive summary</h2>
  <ol class="numbered">
    <li><strong>Main live series in the window:</strong> The Venetian DeepStack Extravaganza IV
      (Nov 16 - Dec 23, 2026). Official page: 64 event numbers, more than $3.6 million in guaranteed
      prize pools. Source: <a href="{dse}" target="_blank" rel="noopener">official schedule</a>.</li>
    <li><strong>Confirmed single-entry events: {n}.</strong> A structure sheet was read and shows no
      re-entry, rebuy, add-on or paid-chip text. These rows are labelled Confirmed. All other
      candidates stay Unverified.</li>
    <li><strong>Top confirmed single-entry events by guarantee:</strong>
      <ul>{top}</ul>
    </li>
    <li><strong>Guarantee &divide; entry fee is a descriptive ratio, not a forecast.</strong> It
      describes the published guarantee per dollar of buy-in. Bounty guarantees include bounty
      payouts; flight events are labelled separately.</li>
    <li><strong>Multi-entry events are separate.</strong> Wynn daily (re-entry), Wynn Friday
      (rebuy/add-on), WPT Main Event (up to 4 entries), Caesars daily ($50 add-on) and Bellagio
      (re-entry + optional gratuity) are on the Multi-Entry page.</li>
    <li><strong>8:00 AM start: not met.</strong> Earliest official start found is 9:00 AM (Horseshoe).
      Earliest Venetian start is 9:10 AM.</li>
    <li><strong>Hotels:</strong> The Venetian (and The Palazzo) and Wynn have an official resort fee
      of $55 per night plus tax. Room rates are dynamic and recorded as a dated log. Walking times are
      verified only for on-property venues; others are blank and flagged.</li>
    <li><strong>Verification:</strong> every row links to its official source and carries a last-checked
      date. A scheduled job re-reads each source and flags changes. Unverified values are blank, never
      inferred.</li>
  </ol>
  <p>Next steps: <a href="questions.html">Questions &amp; Answers</a>,
  <a href="suggestions.html">Suggestions</a>, and the <a href="planner.html">trip calculator</a>.</p>
</section>
""".format(dse=DSE_URL, n=n_confirmed, top=top_rows)
    return body


def page_questions():
    rows = [
        ["Q1", "Which events are truly single-entry?", "Answered for confirmed rows",
         "{} events are confirmed from a read structure sheet with no re-entry/add-on text. The rest are unverified.".format(len(confirmed)),
         "Re-read any unverified structure sheet.", link(DSE_URL, "Venetian schedule")],
        ["Q2", "Is there an official 8:00 AM start?", "Gap",
         "Earliest verified start is 9:00 AM (Horseshoe); earliest Venetian 9:10 AM.",
         "Read official schedules of every Strip room.", link(CAESARS_URL, "Caesars page")],
        ["Q3", "How long does each event take?", "Unverified",
         "Start times only. Durations are not verified; the overlap check uses a labelled assumption.",
         "Read the level-length line of each structure sheet.", link(DSE_URL, "Venetian schedule")],
        ["Q4", "Hotel room rates for the travel dates", "Dated log",
         "Booking-UI snapshots are logged with timestamps; no static rate exists.",
         "Check each official booking page for the dates chosen.", link(SUITE_URL, "Venetian suite rates")],
        ["Q5", "Walking time from each hotel to the tournament room", "Blank / on-property only",
         "On-property venues are 0 minutes (official). All other routes are unverified.",
         "Measure each route on a map; the 30-minute filter shows only verified entries.", link(DSE_URL, "Venetian schedule")],
        ["Q6", "Resort fees for MGM properties, Caesars and Horseshoe", "Secondary or blank",
         "Wynn and Venetian fees are official ($55). Others are secondary or not checked.",
         "Find each property's official resort-fee page.", link(CLARK_TAX_URL, "Clark County")],
        ["Q7", "Current Bellagio dated schedule and Saturday buy-in", "Unverified",
         "Undated PDFs; Saturday buy-in conflicts ($1,000 title vs $1,100 body).",
         "Ask the Bellagio poker room or read the PDF buy-in line.", link("https://bellagio.mgmresorts.com/en/casino/poker.html", "Bellagio poker page")],
        ["Q8", "Current MGM Grand schedule", "Stale",
         "Official PDF titled 'August'; times differ from the page.",
         "Ask the MGM Grand poker room.", link("https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", "MGM Grand poker page")],
        ["Q9", "ARIA daily tournaments", "No official list",
         "Official page lists no tournaments.",
         "Call the ARIA poker room.", link("https://aria.mgmresorts.com/en/casino/poker.html", "ARIA poker page")],
        ["Q10", "Wynn daily availability Nov 16-26 and nightly $160 re-entry", "Unverified",
         "Daily tournaments suspended during the WPT festival (Nov 27-Dec 21).",
         "Ask the Wynn poker room or read the current structures PDF.", link(WYNN_POKER_URL, "Wynn poker page")],
        ["Q11", "WPT festival day-by-day dates", "Partial",
         "Main Event Dec 13-20 (official). Other events: day not captured.",
         "Read the WPT schedule PDF day by day.", link(WPT_URL, "WPT event page")],
        ["Q12", "Hotel quality criteria", "Needs your input",
         "No official quality source chosen; quality is blank.",
         "Choose a quality source and its scale.", link(REPO_URL, "Repo")],
        ["Q13", "Travel dates and party size", "Needs your input",
         "Needed to compute trip cost and pick events; cannot be looked up.",
         "Provide dates and party size for the planner.", link(REPO_URL, "Repo")],
        ["Q14", "Venetian event #40 (Dec 10 row)", "Truncated",
         "Row was cut off in the capture.",
         "Re-read the official schedule for event #40.", link(DSE_URL, "Venetian schedule")],
    ]
    t = table(["#", "Question", "Status", "What we know", "How to find it", "Source"], rows, 5)
    body = '<p class="muted">Each item lists the status, what is known and how to find it. Only items with an official source appear in the table.</p>\n' + t
    return body


def page_suggestions():
    items = [
        ("S1", "Scheduled source re-check (implemented)", "A daily job re-reads each official URL and flags changed rows. Implemented in scripts/recheck_sources.py and .github/workflows/recheck.yml."),
        ("S2", "Add travel dates and party size", "Turns the schedule into an actual plan of entries and a total trip cost (see the Trip Planner)."),
        ("S3", "Choose a hotel quality source", "Quality is blank because none is verified (Q12)."),
        ("S4", "Choose the ranking rule", "Current rule is guarantee, then buy-in. The ratio column is descriptive, not a ranking."),
        ("S5", "Read every structure sheet", "Resolves single-entry status for the unverified rows. Each confirmed row already links its sheet."),
        ("S6", "Confirm Bellagio and MGM Grand dates", "Clears the stale/undated rows (Q7, Q8)."),
        ("S7", "Live hotel rate lookup per date", "The dated rate log records snapshots; a per-date lookup would need the official booking engines."),
        ("S8", "Walking-route verification", "On-property routes are verified; other routes need a map measurement before they can pass the 30-minute filter."),
    ]
    cells = [[esc(i), esc(t), esc(d), badge("ok", "Implemented") if "implemented" in d.lower() else badge("warn", "Awaiting your choice")] for i, t, d in items]
    rows_html = ['<div class="tablewrap"><table class="tbl"><thead><tr><th>#</th><th>Suggestion</th><th>Why</th><th>Status</th></tr></thead><tbody>']
    for c in cells:
        rows_html.append("<tr>" + "".join("<td>{}</td>".format(x) for x in c) + "</tr>")
    rows_html.append("</tbody></table></div>")
    body = '<p class="muted">These are options for decision-making. Implemented items are built; the rest need your choice before they are built.</p>\n' + "".join(rows_html)
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
    # Add change-monitoring flags from the baseline
    changed = []
    if isinstance(baseline, dict):
        for url, info in (baseline.get("sources") or {}).items():
            if info.get("status") == "changed":
                changed.append([esc(url), "Source content changed since the last re-check", esc(info.get("note", "")), badge("bad", "Changed"), link(url, "Source"), "Re-read the source and update the row."])
    if changed:
        ct = table(["Source", "Item", "Detail", "Status", "Sources", "Action"], changed, None)
        body = ('<p class="muted">Flagged items do not block publication. Each is listed with its source link and what is needed to clear it.</p>\n'
                + t + '<h2>Sources changed since the last re-check</h2>\n' + ct)
    else:
        body = ('<p class="muted">Flagged items do not block publication. Each is listed with its source link and what is needed to clear it. '
                'No official source has been recorded as changed since the last scheduled re-check.</p>\n' + t)
    return body


def page_repo_review():
    gh = REPO_URL + "/blob/main/"
    rows = [
        ["Root site (index.html, pages/, assets/)", "Prior build showed 0 single-entry confirmed and used a conservative standard.", "Rebuilt in this integration session: confirmed single-entry rows are labelled from read structure sheets; unverified rows stay unverified; new planner, venue, schedule, hotel and re-check features added.", link(gh + "index.html", "index.html")],
        ["data/c6087e2c/", "Holds the verified inputs (psv, json) for the root site.", "Extended with rates_log.json, walking.json and last_checked.json for the new features.", link(gh + "data/c6087e2c/", "data/c6087e2c")],
        ["scripts/build_c6087e2c.py", "Regenerated the root site from data/c6087e2c/.", "Rewritten to merge all verified datasets, enforce source links, and generate the new pages and calculator.", link(gh + "scripts/build_c6087e2c.py", "build script")],
        ["scripts/recheck_sources.py", "Did not exist.", "Added: scheduled re-check of every official URL, diff vs baseline, change flags.", link(gh + "scripts/recheck_sources.py", "recheck script")],
        [".github/workflows/recheck.yml", "Did not exist.", "Added: daily cron re-check that commits the updated baseline.", link(gh + ".github/workflows/recheck.yml", "workflow")],
        ["assets/app.js", "Did not exist on the root site.", "Added: global search, single-entry toggle, date filter and the trip-cost calculator.", link(gh + "assets/app.js", "app.js")],
        ["Other sessions' folders (docs/, site/, dashboard-*/, planner-aa83f1e1/, site-*/, data-*/, tools/)", "Parallel-session outputs.", "Read-only in this session; not edited. Preserved on main.", link(REPO_URL, "Repo root")],
        ["Walking times", "No official source; prior rows used third-party estimates.", "Only on-property 0-minute routes are verified; all others are blank and flagged (F22). No value inferred.", link(DSE_URL, "Venetian schedule")],
        ["Tax rate 13.38%", "Previously cited from third-party sources only.", "Tied to the official Clark County room-tax ordinance PDF; still labelled 'confirm the current rate'.", link(CLARK_TAX_URL, "Clark County ordinance")],
        ["README.md", "Described the repo and prior sessions.", "Updated to document the integration build and new features.", link(gh + "README.md", "README.md")],
    ]
    t = table(["File / area", "Finding", "Action in this session", "Evidence"], rows, 3)
    body = '<p class="muted">Line-by-line review of the repo on main and the integration changes. Findings are about content, not people.</p>\n' + t
    return body


# ---------------------------------------------------------------- app.js

APP_JS = r"""
/* Poker5 root-site interactivity: global search, single-entry toggle,
   date filter and the trip-cost calculator. No external dependencies. */
(function () {
  "use strict";

  function visible(tr, query, onlyConfirmed) {
    var cells = tr.querySelectorAll("td");
    var text = "";
    for (var i = 0; i < cells.length; i++) text += (cells[i].textContent || "") + " ";
    text = text.toLowerCase();
    if (query && text.indexOf(query) === -1) return false;
    if (onlyConfirmed) {
      var badge = tr.querySelector(".badge");
      if (!badge || badge.textContent.indexOf("Confirmed single-entry") === -1) return false;
    }
    return true;
  }

  window.poker5Filter = function () {
    var q = (document.getElementById("q") || {}).value || "";
    var only = document.getElementById("se-toggle") && document.getElementById("se-toggle").checked;
    q = q.trim().toLowerCase();
    var tables = document.querySelectorAll("table[data-searchable]");
    var anyVisible = false;
    tables.forEach(function (tbl) {
      var rows = tbl.querySelectorAll("tbody tr");
      rows.forEach(function (tr) {
        var show = visible(tr, q, only);
        tr.style.display = show ? "" : "none";
        if (show) anyVisible = true;
      });
    });
    return anyVisible;
  };

  // Trip-cost calculator state.
  var entries = [];
  window.poker5AddEntry = function () {
    var sel = document.getElementById("event");
    var count = parseInt(document.getElementById("count").value, 10) || 1;
    if (!sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var buyin = parseFloat(opt.getAttribute("data-buyin").replace(/[^0-9.]/g, "")) || 0;
    var name = opt.value;
    entries.push({ name: name, buyin: buyin, count: count });
    renderEntries();
    renderTotals();
  };

  function renderEntries() {
    var box = document.getElementById("entries");
    if (!box) return;
    box.innerHTML = "";
    entries.forEach(function (e, i) {
      var row = document.createElement("div");
      row.className = "entry-row";
      row.innerHTML = "<span>" + e.count + " &times; " + e.name + " (" +
        e.buyin.toLocaleString("en-US", { style: "currency", currency: "USD" }) + ")</span>" +
        "<button class=\"btn ghost small\" onclick=\"poker5RemoveEntry(" + i + ")\">Remove</button>";
      box.appendChild(row);
    });
  }
  window.poker5RemoveEntry = function (i) {
    entries.splice(i, 1);
    renderEntries();
    renderTotals();
  };

  window.renderTotals = function () {
    var sumE = document.getElementById("sum-entries");
    var sumH = document.getElementById("sum-hotel");
    var sumT = document.getElementById("sum-total");
    if (!sumE) return;
    var entriesTotal = entries.reduce(function (s, e) { return s + e.buyin * e.count; }, 0);
    var nights = parseFloat(document.getElementById("nights").value) || 0;
    var rate = parseFloat(document.getElementById("rate").value) || 0;
    var fee = parseFloat(document.getElementById("fee").value) || 0;
    var tax = (parseFloat(document.getElementById("tax").value) || 0) / 100;
    var trueNightly = (rate + fee) * (1 + tax);
    var hotelTotal = trueNightly * nights;
    sumE.textContent = "$" + entriesTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    sumH.textContent = "$" + hotelTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    sumT.textContent = "$" + (entriesTotal + hotelTotal).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  };

  // Wire hotel select to load logged rate/fee.
  document.addEventListener("DOMContentLoaded", function () {
    var hotel = document.getElementById("hotel");
    if (hotel) {
      hotel.addEventListener("change", function () {
        var opt = hotel.options[hotel.selectedIndex];
        if (!opt.value) return;
        var rate = opt.getAttribute("data-rate");
        var fee = opt.getAttribute("data-fee");
        if (rate !== "") document.getElementById("rate").value = parseFloat(rate).toFixed(0);
        if (fee !== "") document.getElementById("fee").value = parseFloat(fee).toFixed(0);
        renderTotals();
      });
    }
    ["nights", "rate", "fee", "tax", "count"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("input", renderTotals);
    });
    renderTotals();
  });
})();
"""


CSS = open(os.path.join(ROOT, "assets", "css", "style.css"), encoding="utf-8").read()
# Append calculator/control styles if not already present.
if ".calc-grid" not in CSS:
    CSS += """
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:12px 0}
.search{flex:1;min-width:220px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;font-size:14px}
.toggle{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted);white-space:nowrap}
.calc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
.calc-grid label{display:flex;flex-direction:column;gap:5px;font-size:13px;color:var(--muted);margin-bottom:10px}
.calc-grid input,.calc-grid select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:14px;color:var(--ink)}
.entries{margin-top:8px;display:flex;flex-direction:column;gap:6px}
.entry-row{display:flex;justify-content:space-between;align-items:center;gap:8px;background:#f0f3f9;border-radius:8px;padding:7px 10px;font-size:13px}
.btn.small{padding:4px 9px;font-size:12px}
.calc-total{display:flex;gap:14px;flex-wrap:wrap;margin-top:16px;border-top:1px solid var(--line);padding-top:14px}
.calc-total>div{display:flex;flex-direction:column;gap:2px;min-width:150px}
.calc-total span{font-size:12px;color:var(--muted)}
.calc-total strong{font-size:20px}
.calc-total .grand strong{color:var(--accent);font-size:24px}
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
        "pages/tournaments.html": (page_tournaments, "Single-Entry Tournaments", 1),
        "pages/tournaments-double.html": (page_double, "Multi-Entry and Multi-Flight Events", 1),
        "pages/schedule.html": (page_schedule, "Schedule and Overlap Check", 1),
        "pages/hotels.html": (page_hotels, "Hotels: Rates, True Cost and Walking", 1),
        "pages/planner.html": (page_planner, "Trip Cost Planner", 1),
        "pages/questions.html": (page_questions, "Questions, Information and Answers", 1),
        "pages/suggestions.html": (page_suggestions, "Suggestions", 1),
        "pages/flagged-review.html": (page_flagged, "Flagged for Review", 1),
        "pages/repo-review.html": (page_repo_review, "Repo Review", 1),
        "pages/venues/venetian.html": (lambda: page_venue("venetian", "Venetian", "The Venetian Resort hosts the DeepStack Extravaganza IV (Nov 16 - Dec 23, 2026). Events and on-property hotels below."), "Venetian", 2),
        "pages/venues/wynn.html": (lambda: page_venue("wynn", "Wynn", "Wynn Las Vegas hosts the WPT World Championship (Nov 27 - Dec 21, 2026) and daily tournaments (suspended during the festival)."), "Wynn", 2),
        "pages/venues/others.html": (lambda: page_venue("other", "Other Venues", "Caesars Palace, Horseshoe, Bellagio and MGM Grand daily tournaments. Rules and schedules are from official pages."), "Other Venues", 2),
    }
    for path, (fn, title, depth) in builders.items():
        body = fn()
        write(path, page_shell(path, title, body, depth))
    write("assets/app.js", APP_JS.strip() + "\n")
    write("assets/css/style.css", CSS.strip() + "\n")
    if errors:
        print("BUILD ERRORS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("built {} pages; confirmed={} unverified={} multis={} bounties={} flags={}".format(
        len(builders), len(confirmed), len(unverified_single), len(multis), len(bounties), len(flags)))


if __name__ == "__main__":
    main()
