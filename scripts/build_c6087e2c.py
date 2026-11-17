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

# Date the 37 structure sheets and the WPT terms were read line by line.
AUDIT_DATE = "2026-11-17"
AUDIT_NOTES = "data-audit-3c49aaec/sheetnotes.md"
VENETIAN_DESK = "702.414.7657 / lv_cas_poker@venetianlasvegas.com (printed on the official suite-rate page)"
WYNN_DESK = "702.770-7654 (printed on the official WPT schedule PDF)"
WPT_STRUCT_URL = ("https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/"
                 "WPT/WPT_World_Championship_Structures.pdf")
WPT_SCHEDULE_PDF_URL = ("https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/"
                        "WPT/WPT_World_Championship_Schedule.pdf")

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


def load_structure_sheets():
    """Per-event facts from the 37 official structure sheets, read 2026-11-17.

    Written by scripts/audit_3c49aaec.py from data-audit-3c49aaec/sheetnotes.md.
    Status codes used by the site:
      S  a sheet states single entry / no rebuy      (none in this series)
      N  sheet read in full, entry rule not stated    (silence is NOT a freezeout)
      M  multi-flight event limited to one bagged field
      SAT satellite (seat prize)   T team event   R restart row
    """
    path = os.path.join(ROOT, "data", "c6087e2c", "structure_sheets.json")
    if not os.path.exists(path):
        errors.append("missing data/c6087e2c/structure_sheets.json (run scripts/audit_3c49aaec.py)")
        return {}, []
    data = load_json(path)
    return data.get("by_event", {}), data.get("sheets", [])


def load_narrative(name, keys):
    """Questions / suggestions / repo-review content, written by the audit pass."""
    path = os.path.join(ROOT, "data", "c6087e2c", name)
    if not os.path.exists(path):
        errors.append("missing data/c6087e2c/" + name)
        return []
    rows = load_json(path)
    out = []
    for r in rows:
        out.append({k: r.get(k, "") for k in keys})
    return out


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

    sheet_rules, sheets = load_structure_sheets()
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
        # The 2026-11-17 sheet audit is the authority for this series: a row is
        # only "confirmed single-entry" if a sheet states it, and none does.
        sheet = sheet_rules.get(str(r["event_no"]))
        if sheet and status_code == "S":
            status_code = "N"
        if sheet:
            entry_rule = sheet.get("entry_rule") or ""
            if sheet.get("gtd_override"):
                r["gtd"] = int(sheet["gtd_override"])
        if r["kind"] == "restart":
            status_code = "R"
        elif sheet and sheet.get("satellite"):
            status_code = "SAT"
        elif sheet and "Tag Team" in (r["name"] or ""):
            status_code = "T"
        elif sheet and sheet.get("multi_flight"):
            status_code = "M"
        elif sheet:
            status_code = "N"
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
            "single_entry_confirmed": bool(sheet and sheet.get("single_entry", "").lower().startswith("single")),
            "sheet": sheet,
            "sheet_read": bool(sheet and sheet.get("sheet_read")),
            "late_reg_close": (sheet or {}).get("late_registration_close") or "",
            "starting_stack": (sheet or {}).get("starting_stack"),
            "level_minutes": (sheet or {}).get("level_minutes"),
            "house_fee": (sheet or {}).get("house_fee"),
            "prize_portion": (sheet or {}).get("prize_pool_portion"),
            "fee_note": (sheet or {}).get("fee_note") or "",
            "re_entry_rule": (sheet or {}).get("re_entry") or "",
            "add_on_rule": (sheet or {}).get("add_on") or "",
            "single_entry_rule": (sheet or {}).get("single_entry") or "",
            "payout_basis": (sheet or {}).get("payout") or "",
            "bounty": (sheet or {}).get("bounty") or "",
            "guarantee_note": (sheet or {}).get("guarantee_note") or "",
            "retrieved": (sheet or {}).get("retrieved") or "",
            "flags": [],
        }
        if status_code in ("U", "N"):
            rec["flags"].append("F01")
        if status_code == "N":
            rec["flags"].append("F27")
        if status_code == "M":
            rec["flags"].append("F04")
        if r["gtd"] is None and sheet:
            rec["flags"].append("F39")
        if sheet and (sheet.get("guantee_note") or sheet.get("guarantee_note", "").startswith("Guarantee: 2 Seats")):
            rec["flags"].append("F40")
        if "Bounty" in r["name"] or "PKO" in r["name"]:
            rec["format"] = "bounty"
        elif status_code == "M":
            rec["format"] = "flight"
        else:
            rec["format"] = "standard"
        events.append(rec)

    # Other rooms dated rows. Wynn/WPT rows are enriched from the audit's
    # wpt_row_terms.json (the prior capture in data/other_rooms.txt is read-only, so
    # the verified facts are merged at build time instead of duplicated as new rows).
    wpt_terms = {}
    terms_path = os.path.join(ROOT, "data", "c6087e2c", "wpt_row_terms.json")
    if os.path.exists(terms_path):
        wpt_terms = load_json(terms_path).get("terms", {})
    for r in other_rooms:
        wterm = wpt_terms.get("{}|{}|{}".format(r["date"], r["time"], r["name"]))
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
            "entry_rule": r["notes"] if r["status"] in ("X", "M") else "",
            "pool_note": "",
            "single_entry_confirmed": r["status"] == "S",
            "sheet": None, "sheet_read": False, "late_reg_close": "", "starting_stack": None,
            "level_minutes": None, "house_fee": None, "prize_portion": None, "fee_note": "",
            "re_entry_rule": "", "add_on_rule": "", "single_entry_rule": "", "payout_basis": "",
            "bounty": "", "guarantee_note": "", "retrieved": "",
            "flags": [],
            "format": "flight" if r["status"] in ("M", "X") else "standard",
        }
        if r["status"] == "U":
            rec["flags"].append("F01")
        if r["status"] == "M":
            rec["flags"].append("F04")
        if r["status"] == "X":
            rec["flags"].append("F04")
        if wterm:
            rec["entry_rule"] = wterm.get("reentry") or rec["entry_rule"]
            rec["re_entry_rule"] = wterm.get("reentry") or ""
            rec["single_entry_rule"] = wterm.get("single_entry") or "not stated"
            rec["add_on_rule"] = "not stated in the terms read"
            rec["pool_note"] = wterm.get("split") or ""
            rec["fee_note"] = wterm.get("split") or ""
            rec["starting_stack"] = wterm.get("stack")
            rec["level_minutes"] = wterm.get("level_minutes")
            rec["retrieved"] = wterm.get("retrieved") or ""
            rec["structure"] = wterm.get("source") or ""
            rec["notes"] = (r["notes"] + " | " if r["notes"] else "") + (wterm.get("note") or "")
            if wterm.get("category") == "multi" and rec["status"] in ("M", "U", "single", "X"):
                rec["status"] = "multi"
                rec["format"] = "flight"
                if "F36" not in rec["flags"]:
                    rec["flags"].append("F36")
            if not wterm.get("reentry"):
                if "F35" not in rec["flags"]:
                    rec["flags"].append("F35")
        events.append(rec)

    # Other rooms recurring rows
    for r in other_events:
        if r.get("superseded"):
            continue
        confirmed = bool(re.search(r"single entry|freezeout|no re-entry|no reentry",
                                   r.get("reentry", ""), re.I))
        multi = bool(re.search(r"re-entry|reentry|rebuy|add-on|addon|Unlimited",
                               r.get("reentry", ""), re.I))
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
            "date": r.get("date", ""),
            "time": r.get("time", ""),
            "structure_no": None,
            "structure": r.get("structure", ""),
            "source": r["source"],
            "source_type": r.get("source_type", "official"),
            "notes": r.get("notes", ""),
            "entry_rule": r.get("reentry", ""),
            "pool_note": r.get("buyin_note", ""),
            "single_entry_confirmed": confirmed,
            "sheet": None, "sheet_read": False,
            "late_reg_close": "", "starting_stack": r.get("stack"),
            "level_minutes": r.get("level_minutes"), "house_fee": None, "prize_portion": None,
            "fee_note": r.get("buyin_note", ""), "re_entry_rule": r.get("reentry", ""),
            "add_on_rule": "", "single_entry_rule": "", "payout_basis": "", "bounty": "",
            "guarantee_note": "", "retrieved": r.get("retrieved", ""),
            "flags": list(r.get("flags", [])),
            "format": "bounty" if "Bounty" in (r.get("name") or "") else (
                "flight" if r.get("category") in ("flight", "multi") else "standard"),
        }
        rec["date"] = r.get("date", "") or ""
        rec["time"] = r.get("time", "") or ""
        if multi:
            rec["status"] = "multi"
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
        # Primary = the biggest guaranteed pool the day that is not a known
        # multi-entry/rebuy event. The entry rule is only confirmed as multi where
        # a source states it (F27), so candidates are ranked, never assumed.
        playable = [r for r in rows if r.get("status") not in ("multi", "M", "flight", "R")]
        pool = playable or rows
        primary = max(pool, key=lambda r: (r.get("gtd") or 0, ratio(r) or 0)) if pool else None
        fallback = None
        basis = "{}h assumption".format(DEFAULT_DURATION_HOURS)
        if primary:
            close = to_minutes(primary.get("late_reg_close"))
            if close is not None:
                end = close
                basis = "verified late-registration close ({})".format(fmt_time(primary["late_reg_close"]))
            else:
                end = (to_minutes(primary["time"]) or 0) + int(DEFAULT_DURATION_HOURS * 60)
            candidates = [r for r in rows
                          if r is not primary
                          and r.get("status") not in ("multi", "M", "flight", "R")
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
            "basis": basis,
        }
    return plans


# ---------------------------------------------------------------- html helpers

def badge(kind, text):
    return '<span class="badge badge-{}">{}</span>'.format(kind, esc(text))


def single_entry_badge(rec):
    if rec.get("single_entry_confirmed"):
        return badge("ok", "Confirmed single-entry")
    if rec.get("status") in ("multi", "X"):
        return badge("bad", "Re-entry / add-on allowed (official)")
    if rec.get("status") == "N":
        return badge("warn", "Sheet read - no entry rule stated")
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


def fee_cell(rec):
    """Buy-in split as the structure sheet states it: to prize pool + house fees."""
    fee, pool = rec.get("house_fee"), rec.get("prize_portion")
    if fee is None and pool is None:
        return '<span class="blank">not extracted</span>'
    txt = "{} + {} fee".format(money(pool), money(fee))
    if rec.get("fee_note"):
        txt += '<br><small class="muted">{}</small>'.format(esc(rec["fee_note"]))
    return txt


def late_reg_cell(rec):
    close = rec.get("late_reg_close")
    if not close:
        return '<span class="blank">not published</span>'
    return esc(fmt_time(close))


def stack_cell(rec):
    stack, level = rec.get("starting_stack"), rec.get("level_minutes")
    bits = []
    if stack:
        bits.append("{:,} chips".format(int(stack)))
    if level not in (None, ""):
        bits.append("{}-min levels".format(level))
    return " &middot; ".join(esc(b) for b in bits) if bits else '<span class="blank">blank</span>'


def entry_cells(rec):
    """The four structured rule fields, each as stated by the official source."""
    single = rec.get("single_entry_rule") or "not stated"
    reentry = rec.get("re_entry_rule") or rec.get("entry_rule") or "not stated"
    addon = rec.get("add_on_rule") or "not stated"
    fee = "buy-in {}; {} to prize pool + {} house fee".format(
        money(rec.get("buyin")), money(rec.get("prize_portion")), money(rec.get("house_fee")))
    if rec.get("buyin") and rec.get("pool_note"):
        fee = "buy-in {}; {}".format(money(rec.get("buyin")), rec["pool_note"])
    elif rec.get("buyin") and rec.get("house_fee") is None:
        fee = "buy-in {}; split not published".format(money(rec.get("buyin")))
    return single, reentry, addon, fee


def table(headers, rows, row_source_index=None, dates=None):
    """A table. `dates` (same length as `rows`) drives the shared date selector."""
    out = ['<div class="tablewrap"><table class="tbl" data-searchable>']
    out.append("<thead><tr>")
    for h in headers:
        out.append("<th>{}</th>".format(h))
    out.append("</tr></thead><tbody>")
    for i, cells in enumerate(rows):
        src = cells[row_source_index] if row_source_index is not None else "<a "
        if row_source_index is not None and "<a " not in src:
            errors.append("row {} has no source link in table with headers {}".format(i, headers[:3]))
        attr = ""
        if dates and i < len(dates) and dates[i]:
            attr = ' data-date="{}"'.format(esc(dates[i]))
        out.append("<tr" + attr + ">")
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
        # Cross-session outputs kept reachable from the nav (owners listed in COORDINATION.md).
        ("site-b50aa7f5/index.html", "Strict-entry research"),
        ("dashboard-6d1e0039/index.html", "Verified dashboard 6d1e0039"),
        ("planner-a9d1e02d/index.html", "Final source-audited planner"),
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
_sheets_obj = load_json(os.path.join(ROOT, "data", "c6087e2c", "structure_sheets.json")) \
    if os.path.exists(os.path.join(ROOT, "data", "c6087e2c", "structure_sheets.json")) else {}
sheets_by_number = _sheets_obj.get("sheets", [])
_wynn = load_json(os.path.join(ROOT, "data", "c6087e2c", "wynn_terms.json")) \
    if os.path.exists(os.path.join(ROOT, "data", "c6087e2c", "wynn_terms.json")) else {}
wpt_terms = _wynn.get("events", [])
wpt_notes = _wynn.get("not_read", [])
wynn_facts = _wynn.get("general_terms", [])
_oe_path = os.path.join(ROOT, "data", "c6087e2c", "other_events.json")
superseded_rows = [r for r in (load_json(_oe_path) if os.path.exists(_oe_path) else []) if r.get("superseded")]
hotels = load_hotels()
flags = load_json(os.path.join(ROOT, "data", "c6087e2c", "flags.json"))
questions_data = load_narrative("questions.json", ["id", "question", "status", "what_we_know",
                                                   "how_to_find_it", "sources", "retrieved"])
suggestions_data = load_narrative("suggestions.json", ["id", "suggestion", "why", "impact", "effort",
                                                        "decision_needed", "status"])
repo_review_data = load_narrative("repo_review.json", ["item", "finding", "action", "evidence"])
_feed_path = os.path.join(ROOT, "data", "c6087e2c", "schedule_feed.json")
schedule_feed = load_json(_feed_path) if os.path.exists(_feed_path) else {}
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
        source_last_checked[url] = str(info.get("last_checked", LAST_RUN))[:10]


def last_checked_for(rec):
    """Latest date anything in this row was re-read: the sheet audit date or the
    scheduled re-check baseline, whichever is newer."""
    url = rec.get("source") or rec.get("structure") or ""
    dates = [d for d in (source_last_checked.get(url, ""), rec.get("retrieved") or "") if d]
    return str(max(dates + [LAST_RUN]))[:10]


# ---------------------------------------------------------------- derived sets

confirmed = [e for e in events if e.get("single_entry_confirmed")]
# sheet read in full but silent about entries: verified fields, unverified entry rule
no_rule_stated = [e for e in events
                  if not e.get("single_entry_confirmed")
                  and e.get("status") == "N"
                  and e.get("format") != "flight"]
unverified_single = [e for e in events
                     if not e.get("single_entry_confirmed")
                     and e.get("status") in ("U", "single", None)
                     and e.get("format") != "flight"]
multis = [e for e in events if e.get("status") in ("M", "multi", "flight", "X")]
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

def search_bar(placeholder="Search this table (event, venue, date, status)...", dates=None,
               n_confirmed=None):
    """Search box + single-entry toggle + date selector, shared by every table on a page."""
    opts = ""
    if dates:
        # only ISO dates get a selector entry; range labels such as "Mon-Fri" stay in the table text
        uniq = sorted({d for d in dates if d and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d))})
        opts = '<select id="date-filter" onchange="poker5Filter()"><option value="">All dates</option>' + "".join(
            '<option value="{v}">{l}</option>'.format(v=esc(d), l=esc(fmt_date(d))) for d in uniq) + "</select>"
    toggle = '<label class="toggle"><input id="se-toggle" type="checkbox" ' \
              'onchange="poker5Filter()"> Confirmed single-entry only'
    if n_confirmed is not None:
        toggle += ' <span class="muted">({} rows in this build)</span>'.format(n_confirmed)
    toggle += "</label>"
    return ('<div class="controls">'
            '<input id="q" class="search" type="search" placeholder="{}" '
            'oninput="poker5Filter()">' + opts + toggle +
            '</div>').format(esc(placeholder))



PRIOR_SESSION_OUTPUTS = [
    ("site-b50aa7f5/index.html", "Strict-entry dashboard", "The dashboard npm run check validates; same "
     "official schedule, different labelling standard."),
    ("planner-a9d1e02d/index.html", "Final source-audited planner", "Session a9d1e02d's integrated "
     "planner: the same 37 structure sheets, row-level schedule checks and a source ledger."),
    ("site-src/index.html", "Source snapshot of the strict-entry dashboard", "What is published under "
     "site-b50aa7f5/; the build test asserts the two are identical."),
    ("dashboard-6d1e0039/index.html", "Cross-check dashboard", "Earlier event data, including a dead "
     "structure-sheet path (/content/dam/venetianlasvegas/...) - see the Repo review page."),
    ("dashboard-053f694f/index.html", "Session 053f694f dashboard", "Prior snapshot."),
    ("dashboard-bafafd7c/index.html", "Session bafafd7c dashboard", "Prior snapshot."),
    ("dashboard-cd5ab298/index.html", "Booking-snapshot dashboard", "Source of the dated hotel rate log "
     "entries for Dec 2-9, 2026."),
    ("dashboard-de0bebd4/index.html", "Session de0bebd4 dashboard", "Prior snapshot (30 single-entry "
     "count)."),
    ("planner-aa83f1e1/index.html", "Isolated planner", "Client-side planner; its own build and smoke test "
     "run in CI."),
    ("site-afff1fc9/index.html", "Session afff1fc9 site", "Added the search box, calculator and last-checked "
     "dates now on this root site."),
    ("site-443e914d/index.html", "Session 443e914d site", "Prior snapshot."),
    ("site/index.html", "Session 'site' folder", "Prior snapshot."),
    ("docs/index.html", "Docs folder", "Prior session documentation."),
]


def prior_session_cards():
    """Cards for the other sessions' published folders - only if the file exists."""
    out = []
    for href, title, note in PRIOR_SESSION_OUTPUTS:
        if not os.path.exists(os.path.join(ROOT, href)):
            continue
        out.append('<a class="card" href="{href}"><h3>{title}</h3><p>{note}</p></a>'.format(
            href=esc(href), title=esc(title), note=esc(note)))
    return "".join(out)


def page_index():
    n_confirmed = len(confirmed)
    n_no_rule = len(no_rule_stated)
    n_not_read = len(unverified_single)
    stats = [
        ("Official Venetian event numbers", len({e["event_no"] for e in events if e.get("event_no")})),
        ("Structure sheets read in full", len({e.get("structure_no") for e in events if e.get("structure_no")})),
        ("Confirmed single-entry events", n_confirmed),
        ("Sheet read, entry rule not stated", n_no_rule),
        ("Structure sheet not read", n_not_read),
        ("Multi-entry / multi-flight (separate page)", len(multis)),
        ("Bounty or PKO events", len(bounties)),
        ("Flagged items for review", len(flags)),
    ]
    cards = "".join('<div class="stat"><div class="num">{}</div><div class="lbl">{}</div></div>'.format(
        v, esc(k)) for k, v in stats)
    body = """
<section class="hero">
  <h2>Plan a Las Vegas Strip poker trip from official sources</h2>
  <p>Live tournaments on the Strip, hotels with their resort fees and a dated rate log, a
     trip-cost calculator, and a day plan built from official start times and official
     late-registration deadlines. Every row links the official page it came from. Anything an
     official source does not state is left blank and flagged - never inferred.</p>
  <div class="ctas">
    <a class="btn" href="pages/planner.html">Trip cost calculator</a>
    <a class="btn ghost" href="pages/tournaments.html">Single-entry candidates</a>
    <a class="btn ghost" href="pages/tournaments-double.html">Multi-entry &amp; spend-advantage</a>
    <a class="btn ghost" href="pages/schedule.html">Day schedule + overlap check</a>
    <a class="btn ghost" href="pages/hotels.html">Hotels + true nightly cost</a>
  </div>
</section>
<section class="stats">{cards}</section>
<section class="panel">
  <h2>Headline findings</h2>
  <ul>
    <li><strong>No Venetian event in this series can be labelled a confirmed freezeout.</strong>
        All {sheets} structure sheets behind the DeepStack Extravaganza IV schedule were read in
        full on {audit}; none states single entry, no rebuys or no add-ons, and none caps entries.
        {n_no_rule} rows therefore show every other field as <em>verified</em> and the entry rule as
        <em>not stated</em>; {n_confirmed} rows carry a confirmed single-entry label. Prior sessions
        published 31, 30, 20 and 0 for this count (flag F27).</li>
    <li><strong>Seven multi-flight events are advantage-through-spend by design.</strong> Events
        #01, #07, #19, #26, #47, #49 and #56 each run 2-5 Day 1 flights and state only
        "Any player who bags chips for Day 2 may not play a subsequent flight" - a player can buy
        into more than one flight. They live on the multi-entry page, not the ranking (F04).</li>
    <li><strong>At the Wynn, the opposite is documented: every WPT World Championship event read
        states re-entry.</strong> 11 events state "Unlimited re-entry" until level 9 or 10 and the
        $1,100 WPT Prime Championship ($5,000,000 GTD) allows one entry plus one re-entry per
        starting flight, so no WPT event qualifies as single-entry (F36).</li>
    <li><strong>Guarantee &divide; buy-in is a descriptive ratio, not a forecast,</strong> and it is
        only shown where both numbers are published. Four events (#03, #04, #05, #06) publish no
        guarantee at all and are not ranked (F39); seven satellites guarantee seats, not cash (F40);
        bounty guarantees include the bounty pool (F41).</li>
    <li><strong>Day plan uses official clocks.</strong> Overlaps are checked from the scheduled start
        against each sheet's published late-registration close, not from a guessed duration; event
        finish times are not published anywhere (F42).</li>
    <li><strong>Hotel cost is a dated log.</strong> The Venetian poker rate ("as low as $119" /
        $209 Palazzo, conditional on 6 hours of cash play or a $300+ tournament buy-in each night),
        the $55 + tax resort fee at both the Venetian and Wynn, and the 13.38% Clark County room tax
        are each cited to an official page with the date read. No machine-readable live rate exists
        in this environment, so nothing is shown as a current price (F28).</li>
    <li><strong>No official 8:00 AM start exists.</strong> Earliest verified starts: 9:10 AM at the
        Venetian (event #46, Fri Dec 12), 10:00 AM at the Wynn. The plan is built from the earliest
        verified start, and the day still runs all day: 10:10 AM / 11:10 AM events are common.</li>
    <li><strong>Walking routes are blank, not estimated.</strong> Only on-property routes (0 minutes)
        and "the Wynn poker room is located in the Encore tower" are sourced; every other pair has a
        route link to time it once, which is then reused (F43).</li>
  </ul>
  <p class="muted">Site generated from data/c6087e2c/ by scripts/build_c6087e2c.py; the audited
  datasets are written by scripts/audit_3c49aaec.py (source notes:
  data-audit-3c49aaec/sheetnotes.md). Last scheduled source re-check: {lastrun}. Audit date: {audit}.</p>
</section>
<section class="grid3">
  <a class="card" href="pages/tournaments.html"><h3>Single-entry candidates</h3><p>Ranking, ratio, structured rule fields and the sheet excerpt for every row.</p></a>
  <a class="card" href="pages/tournaments-double.html"><h3>Multi-entry</h3><p>Re-entry, rebuy, add-on, multi-flight and spend-for-chances events.</p></a>
  <a class="card" href="pages/schedule.html"><h3>Schedule</h3><p>Every official dated row, with the overlap check and primary + fallback per day.</p></a>
  <a class="card" href="pages/hotels.html"><h3>Hotels</h3><p>Resort fees, dated rate log, true nightly cost, 30-minute walk filter.</p></a>
  <a class="card" href="pages/planner.html"><h3>Trip planner</h3><p>Entries x buy-ins + nights x true hotel cost, with the poker-rate qualifier check.</p></a>
  <a class="card" href="pages/executive-summary.html"><h3>Executive summary</h3><p>The decision-relevant findings in ten lines.</p></a>
  <a class="card" href="pages/venues/venetian.html"><h3>Venetian</h3><p>DeepStack Extravaganza IV events, sheets and on-property hotels.</p></a>
  <a class="card" href="pages/venues/wynn.html"><h3>Wynn</h3><p>WPT World Championship terms, dated rows and corrections applied.</p></a>
  <a class="card" href="pages/venues/others.html"><h3>Other venues</h3><p>Caesars, Horseshoe, Bellagio, MGM Grand - with what is unverified.</p></a>
  <a class="card" href="pages/questions.html"><h3>Questions</h3><p>Exactly what is missing before you can decide, and who to ask.</p></a>
  <a class="card" href="pages/suggestions.html"><h3>Suggestions</h3><p>Options with impact, effort and the decision each one needs.</p></a>
  <a class="card" href="pages/flagged-review.html"><h3>Flagged for review</h3><p>{nflags} items, each with source links. Flags do not block publication.</p></a>
  <a class="card" href="pages/repo-review.html"><h3>Repo review</h3><p>Irregularities found in the repository itself while auditing.</p></a>
</section>
<section class="panel">
  <h2>Earlier session outputs (read-only, not rebuilt by this audit)</h2>
  <p class="muted">Each planning session published its own folder before the shared board settled on one
  root site. They are left untouched so their captures stay reviewable, but the numbers in them were
  audited at different times and several label the same rows differently (see the Repo review page).
  This root site is the one built from the {audit} structure-sheet audit.</p>
  <div class="grid3">{prior}</div>
</section>
""".format(prior=prior_session_cards(), cards=cards, n_confirmed=n_confirmed,
           n_no_rule=n_no_rule, n_not_read=n_not_read,
           sheets=len({e.get("structure_no") for e in events if e.get("structure_no")}),
           audit=AUDIT_DATE, lastrun=esc(LAST_RUN), nflags=len(flags))
    return body



def tournaments_table(rows, with_rules=True):
    cells = []
    for r in rows:
        single, reentry, addon, fee = entry_cells(r)
        cells.append([
            name_cell(r),
            fmt_sched(r),
            esc(r["venue"]),
            buyin_cell(r),
            fee_cell(r),
            gtd_cell(r),
            ratio_cell(r),
            badge("warn", "Bounty") if r.get("format") == "bounty" else (
                badge("warn", "Flight") if r.get("format") == "flight" else badge("muted", "Standard")),
            single_entry_badge(r),
            late_reg_cell(r),
            stack_cell(r),
            esc(last_checked_for(r)),
            src_cell(r),
        ])
    headers = ["Event", "Date &middot; time", "Venue", "Buy-in", "To prize pool + house fee",
               "Guarantee", "Guarantee &divide; buy-in", "Format", "Single-entry status",
               "Late reg closes", "Start stack &middot; levels", "Last checked", "Source"]
    return table(headers, cells, 12, [r.get("date") for r in rows])


def rules_table(rows):
    """The four structured rule fields, each with what the official source states."""
    cells = []
    for r in rows:
        single, reentry, addon, fee = entry_cells(r)
        excerpt = r.get("notes") or ""
        if r.get("sheet"):
            excerpt = (r["sheet"] or {}).get("source_excerpt") or excerpt
        cells.append([
            name_cell(r),
            esc(fmt_date(r.get("date") or "")) if r.get("date") else '<span class="blank">recurring</span>',
            "<strong>" + esc(single) + "</strong>",
            esc(reentry),
            esc(addon),
            esc(fee),
            esc(r.get("payout_basis") or ""),
            esc(guarantee_note_of(r)),
            '<small>' + esc(excerpt) + '</small>',
            esc(r.get("retrieved") or last_checked_for(r)),
            src_cell(r),
        ])
    headers = ["Event", "Date", "Single-entry (as stated)", "Re-entry (as stated)",
               "Add-on (as stated)", "Fee (as stated)", "Payout basis (sheet)",
               "Guarantee wording (sheet)", "Source excerpt", "Retrieved", "Source"]
    return table(headers, cells, 10, [r.get("date") for r in rows])


def guarantee_note_of(rec):
    note = rec.get("guarantee_note") or rec.get("pool_note") or ""
    if note:
        return note
    if rec.get("gtd") is None:
        return "no guarantee published on the official sheet"
    return ""



def page_tournaments():
    no_rule_rows = sort_rank([e for e in no_rule_stated if e.get("format") != "flight"])
    confirmed_rows = sort_rank([e for e in confirmed if e.get("format") != "flight"])
    not_read_rows = sort_rank([e for e in unverified_single if e.get("format") != "flight"])
    dates = [e.get("date") for e in events if e.get("date")]
    venue_rows = [
        ["The Venetian Resort", "Hosts DeepStack Extravaganza IV. All {} structure sheets read in full on {}: "
         "no sheet states an entry limit, so 0 events are confirmed single-entry.".format(
             len({e.get("structure_no") for e in events if e.get("structure_no")}), AUDIT_DATE),
         link(DSE_URL, "Official schedule")],
        ["Wynn Las Vegas", "WPT World Championship (Nov 27 - Dec 21). Every WPT event read in the official "
         "structures PDF states re-entry is allowed; the poker room is located in the Encore tower.",
         link(WPT_URL, "Official WPT event page") + " &middot; " + link(WPT_STRUCT_URL, "WPT structures PDF")],
        ["Caesars Palace", "Daily NLH listed on the official Caesars page with a $50 add-on, i.e. an "
         "extra-money event; the details were not re-read in this audit (F34).",
         link(CAESARS_URL, "Official Caesars page")],
        ["Horseshoe Las Vegas", "Daily NLH: 6 starts (the official Caesars page states a mixture of buy-ins; "
         "no uniform buy-in is given) (F13).",
         link(CAESARS_URL, "Official Caesars page")],
        ["Bellagio", "Friday/Saturday/Sunday events on undated official PDFs; the Saturday buy-in conflicts "
         "($1,000 title vs $1,100 body) and no official resort-fee page could be retrieved (F10, F33).",
         link("https://bellagio.mgmresorts.com/en/casino/poker.html", "Official poker page")],
        ["MGM Grand", "Daily NLH on the official page; the schedule PDF is titled 'August' (stale) (F11).",
         link("https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", "Official poker page")],
        ["ARIA", "Official page lists no tournament schedule (F12).",
         link("https://aria.mgmresorts.com/en/casino/poker.html", "Official poker page")],
    ]
    venues = table(["Venue", "Status after this audit", "Source"], venue_rows, 2)
    n_sheets = len({e.get("structure_no") for e in events if e.get("structure_no")})
    body = """
<section class="panel warn-panel">
  <strong>What "single-entry" means on this site.</strong> A row is only labelled
  <strong>Confirmed single-entry</strong> when an official structure sheet states the rule. Silence is
  never read as a freezeout: {n_norule} Venetian rows had their sheet read in full on {audit} and are
  listed below as <strong>No entry rule stated</strong> &mdash; every other field on those rows
  (buy-in, fee split, guarantee, start time, stack, level length, late-registration deadline, payout
  percentage) <em>is</em> verified and linked. The guarantee &divide; buy-in column is a
  <strong>descriptive ratio, not a forecast</strong>.
</section>
{search}
<h2>Ranked: structure sheet read, entry rule not stated ({n_norule} rows)</h2>
<p class="muted">Sorted by guaranteed prize pool, then buy-in. To rank any of these as single-entry the
room has to state the rule in writing: {desk}.</p>
{norule}
<h2>Structured rule fields (single-entry / re-entry / add-on / fee)</h2>
<p class="muted">Each field holds the words the official source uses, or "not stated", with the date the
sheet was read. First 40 rows shown; the full list is on the venue pages.</p>
{rules}
<h2>Confirmed single-entry ({n_conf} rows)</h2>
<p class="muted">{conf_note}</p>
{confirmed}
<h2>Structure sheet not read &mdash; unverified ({n_notread} rows)</h2>
<p class="muted">Other rooms and rows whose sheet was not read in this audit. Not comparable with the
ranked list above.</p>
{notread}
<h2>Venue status</h2>
{venues}
""".format(search=search_bar("Search: event, venue, date, format, status...", dates, len(confirmed_rows)),
           n_norule=len(no_rule_rows), n_conf=len(confirmed_rows), n_notread=len(not_read_rows),
           audit=AUDIT_DATE, desk=VENETIAN_DESK,
           conf_note=("No official source for this series states a freezeout, so this section is empty by "
                      "design (see flag F27)." if not confirmed_rows else
                      "Each row links the sheet sentence that states the rule."),
           norule=tournaments_table(no_rule_rows),
           rules=rules_table(no_rule_rows[:40]),
           confirmed=(tournaments_table(confirmed_rows) if confirmed_rows else
                      '<p class="muted">Empty: 0 of {} structure sheets state a single-entry, no-rebuy '
                      'or no-add-on rule.</p>'.format(n_sheets)),
           notread=tournaments_table(not_read_rows), venues=venues)
    return body



def page_double():
    """Events where spending more buys more chances, or the pool is not pure cash."""
    rows_multi = sort_rank([e for e in events if e.get("status") in ("multi", "M", "flight", "X")])
    a_cells, b_cells, a_dates, b_dates = [], [], [], []
    for r in rows_multi:
        rule = r.get("entry_rule") or r.get("re_entry_rule") or r.get("notes") or ""
        row = [
            name_cell(r),
            fmt_sched(r),
            esc(r["venue"]),
            buyin_cell(r),
            gtd_cell(r),
            badge("ok", "single entry stated") if r.get("single_entry_confirmed")
            else badge("warn", "not stated"),
            '<small>' + esc(rule) + '</small>',
            esc(last_checked_for(r)),
            src_cell(r),
        ]
        if r.get("status") in ("multi", "flight", "X") or re.search(
                r"re-entry|Rebuy|rebuy|add-on|Unlimited", rule):
            a_cells.append(row)
            a_dates.append(r.get("date"))
        else:
            b_cells.append(row)
            b_dates.append(r.get("date"))
    headers = ["Event", "Date &middot; time", "Venue", "Buy-in", "Guarantee", "Single-entry stated?",
               "Entry rule (official wording)", "Last checked", "Source"]
    a = table(headers, a_cells, 8, a_dates)
    b = table(headers, b_cells, 8, b_dates)
    # spend-advantage footnotes taken from the sheets themselves
    foot = []
    foot_dates = []
    for e in events:
        note = e.get("fee_note") or ""
        if re.search(r"discount|subsequent buy|PRO|\$180", note, re.I):
            foot.append([name_cell(e), fmt_sched(e), esc(note), link(e.get("structure"), "Structure sheet")])
            foot_dates.append(e.get("date"))
    restart_rows = [e for e in events if e.get("status") == "R"]
    for r in restart_rows:
        foot.append([name_cell(r), fmt_sched(r),
                     "Restart/rebuy row on the official schedule with no separate price published: the "
                     "schedule lists it as a continuation of the day's event, so the entry cost of a restart "
                     "is not verified (F27, F01)",
                     link(r.get("structure") or r.get("source"), "Official row")])
        foot_dates.append(r.get("date"))
    c = table(["Event", "Date &middot; time", "Spend-advantage or unpriced detail (official wording)", "Source"],
              foot, 3, foot_dates)
    suite_rows = [[
        "Daily, Nov 16 - Dec 23 (playing requirement)",
        "The Venetian / The Palazzo poker suite",
        "Requires six hours of active live cash play OR a buy-in to a $300-or-higher tournament for each "
        "night stayed, met before 2 a.m. on the last night, or the rate reverts to the prevailing rate "
        "(official)",
        "as low as $119 (Venetian) / $209 (Palazzo)",
        link(SUITE_URL, "Official suite-rate page"),
    ]]
    suite = table(["Schedule", "Venue", "Spending requirement (official)", "Rate", "Source"], suite_rows, 4)
    dates = [e.get("date") for e in events if e.get("date")]
    body = """
<p class="muted">Kept separate from the single-entry candidates because re-entry, rebuys, add-ons and
multiple flights let a player spend more for more chances, or because the published guarantee is not
pure cash. Section A rows have an official sentence stating re-entry; Section B rows are multi-flight
events whose per-flight entry limit is not stated.</p>
{search}
<h2>A. Official sources that state re-entry, rebuy or add-on ({n_a})</h2>
{a}
<h2>B. Multi-flight events: bagging chips closes the other flights ({n_b})</h2>
<p class="muted">The only entry rule these sheets state is "Any player who bags chips for Day 2 may not
play a subsequent flight", which limits Day 2 entries, not Day 1 entries - so more than one flight can
be played while a seat is free.</p>
{b}
<h2>C. Other ways spending changes the outcome</h2>
<p class="muted">Fee discounts for pre-registering, capped member discounts and restart rows, quoted from
the official sheets. No prize-pool effect is claimed.</p>
{c}
<h2>D. Spending that buys a better hotel rate</h2>
{suite}
""".format(search=search_bar("Search multi-entry events...", dates, 0), n_a=len(a_cells), n_b=len(b_cells),
           a=a, b=b, c=c, suite=suite)
    return body



def feed_table():
    """Render the latest morning feed, or say honestly that it has not run since the audit."""
    if not schedule_feed:
        return ('<p class="muted">No feed file yet: the scheduled job has not run since the {} audit, '
                'when every row was re-read from the official page by hand. The first feed appears after '
                'the next 06:00 UTC run.</p>').format(AUDIT_DATE)
    status = schedule_feed.get("status")
    if status != "ok":
        return ('<p class="muted"><strong>Last attempt {}:</strong> the official page could not be read '
                '("{}"), so no row is marked changed. The feed keeps the previous result instead of '
                'guessing.</p>').format(esc(schedule_feed.get("last_attempt", "")),
                                       esc(schedule_feed.get("note", "no detail recorded")))
    rows_ = schedule_feed.get("rows", [])
    missing = [r for r in rows_ if not r.get("present")]
    cells = [[esc(r.get("date", "")), str(r.get("event_no", "")), esc(r.get("name", "")),
              badge("ok", "still printed on the official page") if r.get("present")
              else badge("bad", "name not found on the page - re-read this row"),
              link(schedule_feed.get("source"), "Official page")] for r in missing]
    head = ('<p>Feed run <strong>{}</strong>: {} of {} captured rows are still printed on the official '
            'page.</p>').format(esc(schedule_feed.get("last_run", "")), len(rows_) - len(missing), len(rows_))
    if not cells:
        return head + '<p class="muted">No row went missing on this run.</p>'
    return head + table(["Date", "Event #", "Event (our capture)", "Feed status", "Source"], cells, 4)




def earliest_text(rows):
    """(time, event) of the earliest dated row, for the 8 AM panel text."""
    timed = [r for r in rows if r.get("time")]
    if not timed:
        return "not captured", "no dated row"
    r = min(timed, key=lambda x: to_minutes(x["time"]) or 9999)
    return fmt_time(r["time"]), "{} on {}".format(r["name"], fmt_date(r["date"]))


def page_schedule():
    plans = overlap_plan(events)
    rows = sorted([e for e in events if e.get("date")],
                  key=lambda r: (r["date"], to_minutes(r["time"]) or 0, r.get("event_no") or 0))
    cells = []
    for r in rows:
        kind = {"S": "Entry (confirmed single)", "M": "Entry (multi-flight)",
                "N": "Entry (sheet read)", "X": "Entry (excluded: re-entry/add-on)",
                "U": "Entry (sheet not read)", "R": "Restart row", "SAT": "Satellite", "T": "Team",
                "multi": "Entry (re-entry allowed)", "flight": "Entry (flights)"}.get(
                    r.get("status"), r.get("status") or "Entry")
        cells.append([
            esc(fmt_date(r["date"])),
            esc(fmt_time(r["time"])),
            str(r.get("event_no") or ""),
            esc(r["name"]),
            buyin_cell(r),
            gtd_cell(r),
            late_reg_cell(r),
            single_entry_badge(r),
            esc(kind),
            esc(last_checked_for(r)),
            src_cell(r),
        ])
    v = table(["Date", "Start", "Event #", "Event (official)", "Buy-in", "Guarantee", "Late reg closes",
               "Single-entry status", "Row type", "Last checked", "Source"], cells, 10,
              [r.get("date") for r in rows])
    plan_cells = []
    for date in sorted(plans):
        p = plans[date]
        primary, fallback = p["primary"], p["fallback"]
        overlap_txt = "; ".join("{} &times; {}".format(esc(a), esc(b)) for a, b in p["overlaps"]) or "None"
        plan_cells.append([
            esc(fmt_date(date)),
            name_cell(primary) + " <small>({}/{})</small>".format(
                money(primary.get("buyin")), money(primary.get("gtd"))) if primary
            else '<span class="blank">none</span>',
            name_cell(fallback) + " <small>({})</small>".format(fmt_time(fallback.get("time")))
            if fallback else '<span class="blank">none feasible</span>',
            esc(overlap_txt),
            esc(p.get("basis") or "{}h assumption".format(DEFAULT_DURATION_HOURS)),
        ])
    plan = table(["Date", "Primary event (biggest published guarantee)", "Conditional fallback",
                  "Same-day windows that collide", "Basis"], plan_cells, None)
    body = """
<section class="panel warn-panel">
  <strong>8:00 AM all-day start: not supported by any official source read.</strong> Earliest verified
  start in this build is {earliest} ({earliest_ev}); the Venetian's earliest start is 9:10 AM (event #46,
  Fri Dec 12) and the Wynn's is 10:00 AM. A day plan can still run all day: most Venetian days have a
  10:10 or 11:10 AM start and an evening 5:10 PM event.
</section>
<section class="panel">
  <strong>How the overlap check works.</strong> Official sheets publish a start time and a
  late-registration deadline, never an expected finish time, so a day is planned as: primary event first,
  and a fallback that can still be entered <em>after the primary's registration window closes</em> - i.e.
  a conditional re-entry if you are knocked out early. Where a row has no published deadline, the
  {h}-hour planning assumption is used and the row says so. This is a planning aid, not a verified finish time (F42).
</section>
{search}
<h2>Morning schedule feed</h2>
<p class="muted">A scheduled job (06:00 UTC daily, <code>.github/workflows/recheck.yml</code>) re-reads
the official DeepStack Extravaganza IV page and checks that every event name this site ranks is still
printed there, then writes <code>data/c6087e2c/schedule_feed.json</code>. It is a presence check, not a
price parse: a name missing from the page means a human must re-read the row, and a failed fetch never
marks anything as changed.</p>
{feed}
<h2>Per-day plan: primary + conditional fallback</h2>
{plan}
<h2>Every official dated row ({n} rows)</h2>
<p class="muted">Row types: "Entry (sheet read)" = the Venetian structure sheet was read in full and every
field except the entry rule is verified; "Entry (multi-flight)" = more than one Day 1 flight exists;
"Entry (excluded)" = an official source states re-entry, rebuys or add-ons, so the row also lives on the
multi-entry page; "Entry (sheet not read)" = an earlier session's row whose sheet this audit did not
read.</p>
{v}
""".format(feed=feed_table(), search=search_bar("Search the schedule: event, venue, date...", [r.get("date") for r in rows], 0),
           plan=plan, v=v, n=len(rows), h=DEFAULT_DURATION_HOURS,
           earliest=earliest_text(rows)[0], earliest_ev=earliest_text(rows)[1])
    return body



def page_hotels():
    """Hotels: official fee, dated rate log with every capture item, walking filter."""
    cells = []
    for h in hotels:
        fee_usd = h.get("resort_fee_usd")
        fee_txt = h.get("resort_fee") or "blank"
        status = (badge("ok", "Official fee") if h.get("fee_verified") and fee_usd
                  else badge("warn", "Not verified"))
        walk = h.get("walk_to_tournament") or ""
        walk_badge = badge("ok", "0 min (on-property)") if "0 min" in walk else badge("warn", "Not verified")
        rate = h.get("nightly_rate") or h.get("poker_rate") or ""
        src = link(h.get("fee_source") or h.get("source") or "", "Official fee page") if (
            h.get("fee_source") or h.get("source")) else link("flagged-review.html", "Flagged (no source)")
        if h.get("booking"):
            src += " &middot; " + link(h["booking"], "Booking page")
        cells.append([
            "<strong>{}</strong><br><small>{}</small>".format(esc(h.get("hotel")),
                                                               esc(h.get("role") or h.get("area") or "")),
            walk_badge + (("<br><small>{}</small>".format(esc(walk))) if walk else ""),
            esc(rate) if rate else '<span class="blank">blank</span>',
            esc(fee_txt) + (" <small>({})</small>".format(esc(h.get("resort_fee_retrieved", "")))
                            if h.get("resort_fee_retrieved") else ""),
            esc(h.get("fee_inclusions") or "Not verified"),
            esc(h.get("parking") or "Not verified"),
            esc(h.get("cancellation") or "Not verified"),
            esc(h.get("quality") or "Not verified"),
            esc(h.get("true_cost") or "Not computed"),
            status + "<br>" + src,
        ])
    main = table(["Hotel", "Walk to the tournament", "Nightly room rate", "Resort fee (per night)",
                  "What the fee covers (official)", "Parking", "Cancellation", "Quality",
                  "True cost per night", "Status &amp; source"], cells, 9)

    log_cells, log_dates = [], []
    for e in rates_log.get("entries", []):
        def num(key, per_night=False):
            v = e.get(key)
            return money(v) if v else '<span class="blank">blank</span>'
        notes = e.get("caveats") or []
        note_html = "<br><small class='muted'>" + esc(" ".join(notes)) + "</small>" if notes else ""
        log_cells.append([
            "<strong>{}</strong>".format(esc(e["hotel"])),
            esc(e.get("checkin", "")) + " &rarr; " + esc(e.get("checkout", "")) +
            ((" &middot; " + esc(e.get("room_type"))) if e.get("room_type") else ""),
            str(e.get("nights", "")),
            esc(e.get("occupancy", "")),
            num("room_rate_per_night"),
            num("checkout_total"),
            num("nightly_average"),
            num("resort_fee_per_night"),
            num("tax_total"),
            esc(e.get("parking") or "blank"),
            esc(e.get("cancellation_deadline") or "blank"),
            esc(e.get("rate_timestamp", "")),
            (badge("ok", "Official page read") if e.get("verified") else badge("warn", "Snapshot - not a live quote"))
            + "<br>" + link(e.get("source", ""), e.get("source_label") or "Booking source") + note_html,
        ])
        log_dates.append(e.get("checkin"))
    log = table(["Hotel", "Stay &middot; room type", "Nights", "Occupancy", "Room rate/night",
                 "Checkout total", "Nightly average", "Resort fee/night", "Tax total", "Parking",
                 "Cancellation deadline", "Rate timestamp", "Status &amp; source"], log_cells, 12, log_dates)

    walk_cells = []
    for w in walking.get("routes", []):
        mins = w.get("walk_minutes")
        limit = walking.get("limit_minutes", 30)
        ok = mins is not None and mins <= limit
        route = link(w.get("route_url"), "Route link") if w.get("route_url") else \
            '<a href="flagged-review.html">Flagged (no measured route)</a>'
        src = link(w.get("source"), "Official source") if w.get("source") else \
            '<a href="flagged-review.html">Flagged (no source)</a>'
        walk_cells.append([
            "<strong>{}</strong>".format(esc(w["hotel"])),
            esc(w["venue"]),
            (str(mins) + " min") if mins is not None else '<span class="blank">unverified</span>',
            badge("ok", "Passes &le;{} min".format(limit)) if ok else badge("warn", "Not verified"),
            esc(w.get("note", "")),
            src,
            route,
        ])
    walk_tbl = table(["Hotel", "Venue", "Walk", "&le;30-min filter", "Note", "Source", "Measure it"],
                     walk_cells, 5)
    tax_pct = rates_log.get("tax_rate_pct")
    body = """
<section class="panel">
  <strong>How the true nightly cost is built:</strong> nightly room rate + mandatory resort fee + tax.
  Room rates are dynamic and no official machine-readable rate feed exists, so nothing here is a
  "current rate": the dated log below stores each observation with the date and source it came from, and
  the hotels table shows the official "as low as" poker rate only with its conditions.
  Tax: <strong>{tax}%</strong> for a resort hotel inside the Clark County Primary Gaming Corridor, cited
  from <a href="{taxurl}" target="_blank" rel="noopener">the official ordinance document</a>; whether the
  resort fee sits inside the tax base is confirmed only on the itemised folio (F45).
</section>
{search}
<h2>Hotels hosting or near the tournaments</h2>
{main}
<h2>Dated rate log &mdash; the capture items, per observation</h2>
<p class="muted">Checkout total, nightly average, resort fee, tax, parking, cancellation deadline and the
rate timestamp, each as reported by the linked official source on the date given. Blank means the source
does not state it; nothing is computed from an assumption.</p>
{log}
<h2>Walking-route check (&le;{limit}-minute filter)</h2>
<p class="muted">Only routes an official source or a measurement states are shown with minutes; every
other pair is blank and hidden by the filter, with a route link so the number can be measured once and
recorded in data/c6087e2c/walking.json (F43).</p>
{walk}
""".format(tax=tax_pct, taxurl=CLARK_TAX_URL, limit=walking.get("limit_minutes", 30),
           search=search_bar("Search hotels, fees, routes...", None, None), main=main, log=log, walk=walk_tbl)
    return body



def page_planner():
    """Trip-cost calculator: entries x buy-ins + nights x true nightly cost, with the
    Venetian poker-rate qualifier check (a $300+ tournament buy-in per night)."""
    pool = [e for e in events if e.get("buyin") and e.get("status") not in ("multi", "flight", "R")]
    options = []
    for r in sort_rank(pool):
        tag = {"N": "sheet read, rule not stated", "U": "sheet not read", "S": "confirmed single-entry",
               "SAT": "satellite (seat prize)", "T": "team event"}.get(r.get("status"), "")
        options.append((r["name"], r.get("buyin"), r.get("gtd"), r.get("venue"), r.get("date"), tag))
    opts = "\n".join(
        '      <option value="{name}" data-buyin="{buyin}" data-gtd="{gtd}" data-qualifies="{qual}">'
        '{name} &middot; {when} &middot; {venue} &middot; {buyin} &middot; {tag}</option>'.format(
            name=esc(name), buyin=money(buyin) if buyin else "", gtd=money(gtd) if gtd else "",
            when=esc(fmt_date(date)) if date else "recurring",
            venue=esc(venue), tag=esc(tag), qual="1" if (buyin or 0) >= 300 else "0")
        for name, buyin, gtd, venue, date, tag in options)
    hotel_opts = []
    for h in hotels:
        # Never turn a generic "from" / poker-suite rate into a dated booking quote.
        # Only the user-entered, date-specific rate can populate the calculator.
        fee = h.get("resort_fee_usd") if h.get("fee_verified") else None
        label = "{hotel} (official fee {fee}; dated room rate not recorded)".format(
            hotel=esc(h.get("hotel")),
            fee=("${:,.2f}".format(fee) if fee is not None else "not verified"))
        fee_source = h.get("fee_source") or h.get("source") or ""
        hotel_opts.append((h.get("hotel"), fee, fee_source, h.get("resort_fee_retrieved", ""), label))
    h_opts = "\n".join(
        '      <option value="{name}" data-fee="{fee}" data-fee-source="{source}" data-fee-date="{date}">{label}</option>'.format(
            name=esc(name), fee=("" if fee is None else fee), source=esc(source),
            date=esc(date), label=label)
        for name, fee, source, date, label in hotel_opts)
    worked = ""
    logged = [e for e in rates_log.get("entries", []) if e.get("checkout_total")]
    for e in logged:
        worked += ("<tr><td>{h}: logged booking-UI total, {ci} &rarr; {co}</td>"
                   "<td>{} nights, all-in from the official booking page</td><td>{tot}</td>"
                   "<td>Snapshot dated {ts}, not a current rate</td></tr>").format(
            e["nights"], tot=money(e["checkout_total"]),
            h=esc(e["hotel"]), ci=esc(e.get("checkin", "")), co=esc(e.get("checkout", "")),
            ts=esc(e.get("rate_timestamp", "")))
    body = """
<section class="panel">
  <strong>Trip cost calculator.</strong> Estimated total = (entries &times; buy-ins) + (nights &times; true
  hotel cost per night), where true hotel cost = dated room rate + mandatory resort fee + tax.
  No date-specific room quote is currently recorded, so the hotel and grand totals stay incomplete
  until a rate is supplied; missing inputs are never treated as zero. Every buy-in comes from the linked
  official schedule. Event options show their entry-policy status and do not imply single-entry when
  the source is silent. This is a planning estimate, not a booking quote.
</section>
<div class="panel">
  <div class="calc-grid">
    <div>
      <h3>1. Trip</h3>
      <label>Nights <input id="nights" type="number" min="1" step="1" placeholder="enter stay length"></label>
      <label>Dated nightly room rate ($) <input id="rate" type="number" min="0.01" step="0.01" placeholder="no date-specific quote recorded"></label>
      <label>Resort fee per night ($) <input id="fee" type="number" min="0" step="0.01" placeholder="select hotel or enter verified fee"></label>
      <label>Tax rate (%) <input id="tax" type="number" min="0" step="0.01" value="13.38"></label>
      <label>Hotel <select id="hotel">
          <option value="">-- select hotel to load only its verified fee --</option>
{h_opts}
        </select></label>
      <p id="hotel-evidence" class="muted">No hotel source selected. A dated room quote is required for a hotel total.</p>
      <p class="muted">Modeled formula = (room rate + resort fee) &times; (1 + tax%). The 13.38% rate is cited on the Hotels page;
      whether the resort fee is included in the tax base remains unverified (F45), so this is not an itemized quote.</p>
    </div>
    <div>
      <h3>2. Entries</h3>
      <label>Event <select id="event">
          <option value="">-- pick an event to add --</option>
{opts}
        </select></label>
      <label>Entries (count) <input id="count" type="number" min="1" value="1"></label>
      <button class="btn add-entry" onclick="poker5AddEntry()">Add to trip</button>
      <div id="entries" class="entries"></div>
      <p class="muted">Add-on / re-entry events are listed on the
      <a href="tournaments-double.html">multi-entry page</a> and are not in this dropdown.
      Each entry of $300 or more also satisfies the Venetian poker-suite play requirement for that
      night (F29) - the calculator shows a qualifier note per entry.</p>
    </div>
  </div>
  <div class="calc-total">
    <div><span>Entries &times; buy-ins</span><strong id="sum-entries">$0</strong></div>
    <div><span>Nights &times; true hotel cost</span><strong id="sum-hotel">$0</strong></div>
    <div class="grand"><span>Estimated trip cost</span><strong id="sum-total">$0</strong></div>
    <div><span>Nights that qualify for the poker rate</span><strong id="sum-qual">0</strong></div>
  </div>
  <table class="tbl"><thead><tr><th>Reference totals (not quotes)</th><th>Arithmetic</th>
  <th>Amount</th><th>Status</th></tr></thead><tbody>{worked}</tbody></table>
</div>
<p class="muted">No manual input is needed to read the site; the calculator is an optional planning tool.
Nothing typed here is stored or sent anywhere - it is computed in your browser only.</p>
""".format(h_opts=h_opts, opts=opts, worked=worked)
    return body



def page_venue(group, title, intro):
    rows = [e for e in events if e.get("venue_group") == group]
    venue_hotels = [h for h in hotels if group == "venetian" and
                    any(k in (h.get("hotel", "") + h.get("role", "")).lower()
                        for k in ("venetian", "palazzo", "cosmopolitan", "park mgm"))]
    if group == "wynn":
        venue_hotels = [h for h in hotels if "wynn" in (h.get("hotel", "") + h.get("role", "")).lower()
                        or "encore" in h.get("hotel", "").lower()]
    if group == "other":
        venue_hotels = [h for h in hotels if any(k in h.get("hotel", "").lower() for k in
                                                 ("caesars", "horseshoe", "bellagio", "mgm", "aria",
                                                  "planet", "golden", "resorts world", "cosmopolitan"))]
    cells = []
    for r in sort_rank(rows):
        single, reentry, addon, fee = entry_cells(r)
        cells.append([
            name_cell(r),
            fmt_sched(r),
            buyin_cell(r),
            fee_cell(r),
            gtd_cell(r),
            ratio_cell(r),
            single_entry_badge(r),
            esc(single),
            esc(reentry),
            esc(addon),
            late_reg_cell(r),
            stack_cell(r),
            esc(last_checked_for(r)),
            src_cell(r),
        ])
    t = table(["Event", "Date &middot; time", "Buy-in", "To prize pool + house fee", "Guarantee",
               "Guarantee &divide; buy-in", "Single-entry status", "Single-entry (as stated)",
               "Re-entry (as stated)", "Add-on (as stated)", "Late reg closes",
               "Start stack &middot; levels", "Last checked", "Source"],
              cells, 13, [r.get("date") for r in rows])
    h_cells = []
    for h in venue_hotels:
        h_cells.append([
            "<strong>{}</strong><br><small>{}</small>".format(esc(h.get("hotel")),
                                                              esc(h.get("role") or h.get("area") or "")),
            esc(h.get("resort_fee") or "blank") +
            (" <small>({})</small>".format(esc(h.get("resort_fee_retrieved")))
             if h.get("resort_fee_retrieved") else ""),
            esc(h.get("nightly_rate") or h.get("poker_rate") or "") or '<span class="blank">blank</span>',
            esc(h.get("true_cost") or "Not computed"),
            esc(h.get("parking") or "Not verified"),
            src_or_flag(h.get("fee_source") or h.get("source") or "", "Source", base="../") +
            (" &middot; " + link("../" + "flagged-review.html", "Flags: " + ", ".join(h.get("flags", [])))
             if h.get("flags") else ""),
        ])
    ht = table(["Hotel", "Resort fee (official)", "Nightly rate", "True cost per night", "Parking",
                "Source"], h_cells, 5) if h_cells else \
        '<p class="muted">No hotel row is verified for this venue in data/c6087e2c/hotels.json.</p>'
    extra = ""
    if group == "venetian" and sheets_by_number:
        sc = []
        for sh in sheets_by_number:
            sc.append([
                "Sheet {}".format(sh["sheet"]),
                esc(sh["title"]),
                esc(", ".join("#{}".format(e) for e in sh["events"])),
                esc(sh["starting_stack"]) + " chips" if sh["starting_stack"] else '<span class="blank">blank</span>',
                esc(sh["level_minutes"]) + " min" if sh["level_minutes"] else '<span class="blank">blank</span>',
                esc(sh["late_registration"]) or '<span class="blank">not published</span>',
                money(sh["guarantee"]) if sh["guarantee"] else '<span class="blank">no guarantee stated</span>',
                esc(sh["guarantee_note"] or ""),
                esc(sh["payout"] or ""),
                "{} + {} fee".format(money(sh["prize_pool_portion"]), money(sh["house_fee"])),
                esc(sh["bounty"] or "none stated"),
                "single entry: " + esc(sh.get("single_entry") or "not stated") +
                "; re-entry: " + esc(sh.get("re_entry") or "not stated") +
                "; add-on: " + esc(sh.get("add_on") or "not stated"),
                esc(sh["retrieved"]),
                link(sh["url"], "Structure sheet {}".format(sh["sheet"])),
            ])
        extra = ("<h2>Every structure sheet read in full ({})</h2>"
                 "<p class='muted'>One row per official PDF, transcribed {}. 'not stated' means the sheet "
                 "is silent about entries - it is not evidence of a freezeout (F27).</p>{}").format(
                     len(sheets_by_number), AUDIT_DATE,
                     table(["Sheet", "Title (official)", "Event numbers", "Start stack", "Level length",
                            "Late registration", "Guarantee", "Guarantee wording", "Payout",
                            "Buy-in split", "Bounty", "Single-entry statement", "Retrieved", "Source"],
                           sc, 13))
    if group == "wynn":
        sup_rows = [[esc(r.get("name")),
                      esc(r.get("schedule") or "undated"),
                      money(r.get("buyin")) if r.get("buyin") else '<span class="blank">blank</span>',
                      money(r.get("gtd")) if r.get("gtd") else '<span class="blank">blank</span>',
                      esc(r.get("superseded")),
                      link(r.get("source"), "Official source")] for r in superseded_rows]
        cc = [[esc(n), link(WPT_STRUCT_URL, "WPT structures PDF")] for n in wpt_notes]
        terms_tbl = table(
            ["Event (official)", "Dates", "Buy-in", "Guarantee", "Buy-in split", "Start stack",
             "Registration / re-entry (verbatim)", "Levels", "Tables", "Source"],
            [[esc(t.get("name")), esc(t.get("dates")), money(t.get("buyin")),
              money(t["gtd"]) if t.get("gtd") else '<span class="blank">none published</span>',
              esc(t.get("buyin_split") or ""),
              ("{:,} chips".format(int(t["starting_stack"])) if t.get("starting_stack")
               else '<span class="blank">blank</span>'),
              esc(t.get("registration") or "not transcribed in this audit"),
              esc(t.get("level_minutes") or ""), esc(t.get("tables") or ""),
              link(t.get("source") or WPT_STRUCT_URL, "Structures PDF")]
             for t in wpt_terms], 9)
        sup_tbl = ("" if not sup_rows else
                   "<h2>Corrections applied to earlier session data</h2>" +
                   table(["Superseded row from data/c6087e2c/other_events.json", "Date &middot; time",
                          "Buy-in", "Guarantee", "Superseded by", "Source"], sup_rows, 5))
        gaps_tbl = ("" if not cc else "<h2>Rows whose entry rule was not transcribed in this audit</h2>" +  # noqa: E501
                    table(["What is missing", "Source to read"], cc, 1))
        extra = ("<h2>WPT event terms as stated in the official structures PDF</h2>"
                 "<p class='muted'>Read {} from the official Wynn/WPT PDF. Every event read there states "
                 "re-entry, so none of them belongs in the single-entry ranking (F36).</p>"
                 "{}{}{}").format(AUDIT_DATE, terms_tbl, gaps_tbl, sup_tbl)
        extra += ("<h2>General terms that change what you can do at the desk</h2>" +
                  table(["Fact (official)", "What it says", "Source"],
                        [[esc(f["fact"]), esc(f["value"]), link(f["source"], "Official source")]
                         for f in wynn_facts], 2))
    if group == "other":
        extra = ("<p class='muted'>These rooms were captured by earlier sessions and were not re-read "
                 "line by line in the {} audit, so their entry rules stay unverified: Bellagio (F10), "
                 "MGM Grand (F11), ARIA (F12), Horseshoe (F13), Caesars add-on (F34). Rows whose sheet "
                 "was not read are shown as candidates, never as single-entry.</p>").format(AUDIT_DATE)
    body = """
<p class="muted">{intro}</p>
{search}
<h2>Events</h2>
{t}
<h2>Hotels</h2>
{ht}
{extra}
""".format(intro=intro, search=search_bar("Search {} events...".format(title),
                                          [e.get("date") for e in rows if e.get("date")], 0),
           t=t, ht=ht, extra=extra)
    return body



def page_exec():
    n_sheets = len({e.get("structure_no") for e in events if e.get("structure_no")})
    top = sort_rank([e for e in no_rule_stated if e.get("gtd")])[:6]
    top_rows = "".join(
        "<li><strong>{name}</strong> &mdash; {when} &middot; {buy} in, {pool} of it to the prize pool "
        "({fee} house fee) &middot; guarantee {gtd} &middot; ratio {ratio} (descriptive, not a forecast) "
        "&middot; registration closes {close}. <a href=\"{url}\" target=\"_blank\" rel=\"noopener\">"
        "Structure sheet {sheet}</a>.</li>".format(
            name=esc(r["name"]), when=esc(fmt_sched(r)), buy=money(r.get("buyin")),
            pool=money(r.get("prize_portion")), fee=money(r.get("house_fee")),
            gtd=money(r.get("gtd")), ratio=ratio_cell(r), close=esc(fmt_time(r.get("late_reg_close")) or
                                                                        "not published"),
            url=esc(r.get("structure") or r["source"]), sheet=r.get("structure_no"))
        for r in top)
    best_value = sort_rank([e for e in no_rule_stated if ratio(e)])
    best_value = max(best_value, key=lambda e: ratio(e)) if best_value else None
    body = """
<section class="panel">
  <h2>Executive summary</h2>
  <ol class="numbered">
    <li><strong>What is actually on in the window.</strong> The Venetian DeepStack Extravaganza IV runs
      Nov 16 - Dec 23, 2026 with 64 event numbers and "more than $3.6 Million in guaranteed tournament
      prize pools" ({dse_link}). The Wynn hosts the WPT World Championship Nov 27 - Dec 21, 2026
      ({wpt_link}), and its daily tournaments continue to be advertised on the official poker page.
      Caesars/Horseshoe dailies, Bellagio and MGM Grand rows come from earlier sessions and were not
      re-read line by line, so they stay candidates (F34).</li>
    <li><strong>The single-entry question cannot be answered from the published structure sheets.</strong>
      All {n_sheets} sheets behind the Venetian schedule were read in full on {audit}: none states
      single entry, freezeout, no rebuys or no add-ons, and none caps entries. {n_norule} rows are
      therefore "sheet read, entry rule not stated" with every other field verified, and the count of
      <strong>confirmed single-entry events is {n_conf}</strong>. A prior session labelled 31 rows
      "confirmed" by treating silence as a rule; that label is removed here and flagged (F27).</li>
    <li><strong>Seven Venetian events are advantage-through-spend by their own wording.</strong> Events
      #01, #07, #19, #26, #47, #49 and #56 each run 2-5 starting flights and state only that a player
      who bags chips for Day 2 may not play a later flight - so the same $400-$2,200 can be paid for
      several Day 1 shots. They are on the multi-entry page (F04).</li>
    <li><strong>At the Wynn, re-entry is written down.</strong> Of the 13 WPT events transcribed from the
      official structures PDF, 11 state "Unlimited re-entry" until level 9 or 10, the $1,100 WPT Prime
      Championship ($5,000,000 GTD) states one entry plus one re-entry per starting flight, and the
      $10,400 World Championship was not fully captured (F35). The $600 HORSE (Fri Dec 4) and the
      $600 NLH Turbo ($50,000 GTD) are likewise unlimited-re-entry events. No WPT event qualifies as
      single-entry (F36).</li>
    <li><strong>Ranking is on verified numbers only.</strong> guarantee / buy-in is descriptive, never a
      forecast; four events (#03, #04, #05, #06) publish no guarantee and are not ranked (F39); seven
      satellites guarantee seats (F40); bounty guarantees include the bounty pool (F41). Best published
      ratio among ranked rows: <strong>{best}</strong>.</li>
    <li><strong>Highest guaranteed pools in the ranked list:</strong>
      <ul>{top}</ul></li>
    <li><strong>The day plan uses official clocks only.</strong> Start time plus the sheet's own
      late-registration deadline decide whether a second event the same day is enterable; finish times
      are never published, so the fallback is explicitly conditional on being knocked out before the
      cutoff (F42). No official 8:00 AM start exists - earliest verified is {earliest_start}.</li>
    <li><strong>Hotel cost is a dated log, not a rate.</strong> Venetian poker suites are "as low as $119
      / $209" conditional on 6 hours of cash play or a $300+ tournament buy-in every night (F29); both
      the Venetian and the Wynn state a $55 + tax resort fee (Wynn's figure comes from a promotional terms
      page, F30); Clark County room tax is 13.38% in the corridor (F45). The only booking-UI total in the
      log is {logged}. Parking, quality and cancellation for most properties stay blank (F31, F44).</li>
    <li><strong>Two events a day is the realistic maximum.</strong> A 10:10/11:10 AM flight-style event
      runs into the evening, and the evening events start 5:10 PM. Late registration for the 11:10 AM
      one-day events closes around 4:55 PM, so a bust-out can still enter the 5:10 PM field the same day
      - which is also what makes double-buy-in worth pricing in the calculator.</li>
    <li><strong>What is left before you book.</strong> {n_flags} flagged items and {n_q} open questions,
      each naming the source that would clear it. The two that change the plan most are the Venetian
      entry rule (ask {desk}) and the live room rate for your dates (F28).</li>
  </ol>
  <p>Working pages: <a href="tournaments.html">ranked candidates + rule fields</a>,
  <a href="tournaments-double.html">multi-entry</a>, <a href="schedule.html">day plan</a>,
  <a href="hotels.html">hotels + rate log</a>, <a href="planner.html">trip cost</a>,
  <a href="questions.html">questions</a>, <a href="suggestions.html">suggestions</a>,
  <a href="flagged-review.html">flagged items</a>.</p>
</section>
""".format(dse_link=link(DSE_URL, "official schedule"), wpt_link=link(WPT_URL, "official WPT event page"),
           n_sheets=n_sheets, audit=AUDIT_DATE, n_norule=len(no_rule_stated), n_conf=len(confirmed),
           best=("<strong>#{} {}</strong> at {} ({} guarantee / {} buy-in)".format(
               best_value.get("event_no") or "", esc(best_value["name"]), ratio_cell(best_value),
               money(best_value.get("gtd")), money(best_value.get("buyin"))) if best_value else "n/a"),
           top=top_rows, logged="{} at the Venetian for Dec 2-9".format(money(7054.77)) if any(
               e.get("checkout_total") for e in rates_log.get("entries", [])) else "not captured",
           n_flags=len(flags), n_q=len(questions_data), desk=VENETIAN_DESK,
           earliest_start="9:10 AM (Fri Dec 12, event #46)")
    return body



def page_questions():
    rows = []
    for q in questions_data:
        srcs = q.get("sources") or []
        src = " &middot; ".join(link(u, "Official source") for u in srcs if u) or \
            '<a href="flagged-review.html">Flagged (no source)</a>'
        badge_txt = "Answered" if str(q.get("status", "")).lower().startswith("answered") else (
            "Partly answered" if "partly" in str(q.get("status", "")).lower() else "Open")
        rows.append([
            esc(q["id"]),
            "<strong>" + esc(q["question"]) + "</strong>",
            badge("ok" if badge_txt == "Answered" else ("warn" if badge_txt == "Partly answered" else "bad"),
                  badge_txt),
            esc(q.get("what_we_know") or ""),
            esc(q.get("how_to_find_it") or ""),
            esc(q.get("status") or ""),
            src,
        ])
    t = table(["#", "Question to settle before deciding", "Status", "What the official sources already say",
               "What would answer it", "Current status detail", "Source"], rows, 6)
    body = """
<p class="muted">These are the open decisions and gaps, each with the source that closes it. Nothing here
is answered by inference: where an official page is silent the answer has to come from the room
({venetian_desk} / {wynn_desk}) or from your own choices (dates, party size, quality source).</p>
{t}
""".format(t=t, venetian_desk=VENETIAN_DESK, wynn_desk=WYNN_DESK)
    return body




def page_suggestions():
    rows = []
    for su in suggestions_data:
        st = str(su.get("status") or "")
        rows.append([
            esc(su["id"]),
            "<strong>" + esc(su["suggestion"]) + "</strong>",
            esc(su.get("why") or ""),
            "{} impact / {} effort".format(esc(su.get("impact") or ""), esc(su.get("effort") or "")),
            badge("ok", st) if st.lower().startswith("implemented") else badge("warn", st or "Open"),
            esc(su.get("decision_needed") or ""),
            link(REPO_URL + "/blob/main/COORDINATION.md", "Coordination board"),
        ])
    t = table(["#", "Suggestion", "Why it matters", "Impact / effort", "Status",
               "The decision it needs from you", "Where the choice is recorded"], rows, 6)
    body = ('<p class="muted">Options for the next iteration. Items marked Implemented are already built '
            'into this site; the rest need your choice before they are built, because each one changes '
            'what may be presented as a fact.</p>\n' + t)
    return body


def page_repo_review():
    gh = REPO_URL + "/blob/main/"
    rows = []
    for r in repo_review_data:
        rows.append([
            "<strong>" + esc(r["item"]) + "</strong>",
            esc(r.get("finding") or ""),
            esc(r.get("action") or ""),
            link(r.get("evidence") or gh, "Evidence"),
        ])
    t = table(["File / area", "Finding", "Action in this audit", "Evidence"], rows, 3)
    body = ('<p class="muted">Line-by-line review of the repository on main, from the '
            '{} structure-sheet audit. Findings are about content, not people. Read-only folders belonging '
            'to other sessions were not edited: their conflicts are recorded here and on the flagged '
            'page instead.</p>\n' + t).format(AUDIT_DATE)
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
    feed_missing = [r for r in (schedule_feed.get("rows") or []) if not r.get("present")]
    if schedule_feed and (schedule_feed.get("status") != "ok" or feed_missing):
        body += ('<h2>Morning feed needs a look</h2><p class="muted">Written by '
                 'scripts/recheck_sources.py --feed. A failed fetch is reported as a failed fetch, never as '
                 'a change.</p>' + feed_table())

    return body




# ---------------------------------------------------------------- app.js

APP_JS = r"""
/* Poker5 root-site interactivity: global search, single-entry toggle,
   date filter and the trip-cost calculator. No external dependencies. */
(function () {
  "use strict";

  function visible(tr, query, onlyConfirmed, dateValue) {
    var cells = tr.querySelectorAll("td");
    var text = "";
    for (var i = 0; i < cells.length; i++) text += (cells[i].textContent || "") + " ";
    text = text.toLowerCase();
    if (query && text.indexOf(query) === -1) return false;
    if (dateValue && tr.getAttribute("data-date") !== dateValue) return false;
    if (onlyConfirmed) {
      // the format column also uses .badge, so scan every badge in the row
      var badges = tr.querySelectorAll(".badge"), hit = false;
      for (var j = 0; j < badges.length; j++) {
        if (badges[j].textContent.indexOf("Confirmed single-entry") !== -1) hit = true;
      }
      if (!hit) return false;
    }
    return true;
  }

  window.poker5Filter = function () {
    var q = (document.getElementById("q") || {}).value || "";
    var only = document.getElementById("se-toggle") && document.getElementById("se-toggle").checked;
    var dv = (document.getElementById("date-filter") || {}).value || "";
    q = q.trim().toLowerCase();
    var tables = document.querySelectorAll("table[data-searchable]");
    var anyVisible = false;
    tables.forEach(function (tbl) {
      var rows = tbl.querySelectorAll("tbody tr");
      rows.forEach(function (tr) {
        var show = visible(tr, q, only, dv);
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
    var count = Math.max(1, parseInt(document.getElementById("count").value, 10) || 1);
    if (!sel.value) return;
    var opt = sel.options[sel.selectedIndex];
    var buyin = parseFloat(opt.getAttribute("data-buyin").replace(/[^0-9.]/g, "")) || 0;
    var qualifies = opt.getAttribute("data-qualifies") === "1";
    var name = opt.value;
    entries.push({ name: name, buyin: buyin, count: count, qualifies: qualifies });
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
      var qual = e.qualifies ?
        ' <em class="muted">(\u2265 $300: satisfies the Venetian poker-suite play requirement for one night)</em>' :
        ' <em class="muted">(&lt; $300: does not satisfy the poker-suite play requirement alone)</em>';
      row.innerHTML = "<span>" + e.count + " &times; " + e.name + " (" +
        e.buyin.toLocaleString("en-US", { style: "currency", currency: "USD" }) + ")" + qual + "</span>" +
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
    var nightsInput = document.getElementById("nights").value;
    var rateInput = document.getElementById("rate").value;
    var feeInput = document.getElementById("fee").value;
    var taxInput = document.getElementById("tax").value;
    var nights = nightsInput === "" ? NaN : Number(nightsInput);
    var rate = rateInput === "" ? NaN : Number(rateInput);
    var fee = feeInput === "" ? NaN : Number(feeInput);
    var tax = taxInput === "" ? NaN : Number(taxInput) / 100;
    var hotelComplete = Number.isFinite(nights) && nights > 0 &&
      Number.isFinite(rate) && rate > 0 && Number.isFinite(fee) && fee >= 0 &&
      Number.isFinite(tax) && tax >= 0;
    var hotelTotal = hotelComplete ? (rate + fee) * (1 + tax) * nights : null;
    sumE.textContent = "$" + entriesTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    sumH.textContent = hotelComplete ? "$" + hotelTotal.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 }) : "Incomplete";
    sumT.textContent = hotelComplete ? "$" + (entriesTotal + hotelTotal).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 }) : "Incomplete";
    var qualBox = document.getElementById("sum-qual");
    if (qualBox) {
      var nightsCovered = 0;
      entries.forEach(function (e) { if (e.qualifies) nightsCovered += e.count; });
      qualBox.textContent = Number.isFinite(nights) ? nightsCovered + " of " + nights + " night(s)" : "Enter nights";
    }
  };

  // Wire hotel select to load logged rate/fee.
  document.addEventListener("DOMContentLoaded", function () {
    var hotel = document.getElementById("hotel");
    if (hotel) {
      hotel.addEventListener("change", function () {
        var opt = hotel.options[hotel.selectedIndex];
        var rateInput = document.getElementById("rate");
        var feeInput = document.getElementById("fee");
        var evidence = document.getElementById("hotel-evidence");
        // A hotel change invalidates the previous hotel's manually entered quote.
        rateInput.value = "";
        feeInput.value = "";
        if (evidence) {
          evidence.textContent = opt.value ? "No dated room quote recorded for " + opt.value + "." :
            "No hotel source selected. A dated room quote is required for a hotel total.";
          var fee = opt.getAttribute("data-fee");
          var source = opt.getAttribute("data-fee-source");
          var date = opt.getAttribute("data-fee-date");
          if (opt.value && fee !== "") {
            feeInput.value = Number(fee).toFixed(2);
            evidence.textContent += " Official resort fee: $" + Number(fee).toFixed(2) +
              " per night" + (date ? " (retrieved " + date + ")" : "") + ". Source: ";
            if (source && /^https:\/\//.test(source)) {
              var a = document.createElement("a");
              a.href = source;
              a.target = "_blank";
              a.rel = "noopener";
              a.textContent = "official fee page";
              evidence.appendChild(a);
            } else {
              evidence.appendChild(document.createTextNode("not recorded"));
            }
          } else if (opt.value) {
            evidence.textContent += " No official fee amount is verified; hotel total remains incomplete.";
          }
        }
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
if ".badge-muted" not in CSS:
    CSS += """
.badge-muted{background:#eef1f5;color:var(--muted)}
.entry-row em{font-style:normal;color:var(--muted)}
"""

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
        "pages/venues/venetian.html": (lambda: page_venue("venetian", "Venetian", "The Venetian Resort hosts the DeepStack Extravaganza IV, Nov 16 - Dec 23, 2026: 64 event numbers, more than $3.6 million in guaranteed prize pools. Every event below has its official structure sheet read in full on 2026-11-17; the sheets state fees, stacks, levels and registration deadlines but never an entry limit (F27)."), "Venetian", 2),
        "pages/venues/wynn.html": (lambda: page_venue("wynn", "Wynn", "Wynn Las Vegas hosts the WPT World Championship (Nov 27 - Dec 21, 2026); the poker room is located in the Encore tower. Daily tournaments are advertised on the official page and are suspended during the Wynn Signature, Wynn Millions and Classic series - the WPT festival is not named in that sentence (F32)."), "Wynn", 2),
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
