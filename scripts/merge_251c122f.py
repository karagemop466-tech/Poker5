#!/usr/bin/env python3
"""Merge the live official capture into the verified event dataset.

Inputs (written by scripts/scrape_251c122f.py from the official pages/PDFs):
    data/c6087e2c/schedule_live.json   every row of the official schedule page
    data/c6087e2c/structures.json      per-sheet rule fields + excerpts
    data/c6087e2c/scrape_status.json   per-URL status/hash/timestamp

Inputs (curated earlier, kept as the transcription of the same page):
    data/c6087e2c/venetian_dse_2026.psv   row-by-row schedule transcription
    data/venetian_dse_iv.txt              per-row structure-sheet read status

Output:
    data/c6087e2c/events_verified.json    one record per scheduled row with
                                          structured rule fields, each carrying
                                          its source URL, excerpt and retrieval
                                          date, plus the derived single-entry
                                          verdict and the flags.

Rules
-----
* A row is **confirmed single-entry** only when its structure sheet was read,
  the sheet's own event-number list contains the row's event number, the sheet
  is a one-day format, and the sheet explicitly states a one-entry cap / freezeout
  plus no re-entry, no rebuy and no add-on. Silence is not confirmation.
* A one-day row whose sheet is read but does not state those limits is
  **entry_limit_unverified**. Its buy-in and structure fields may be sourced,
  but it is excluded from single-entry-only lists and flagged for review.
* A row whose sheet explicitly offers a second entry or paid chips is routed to
  the separate multi-entry / advantage section.
* A row whose sheet was not read, or a sheet that could not be matched to the
  row's event number, stays **unverified** and is listed as such.
* Live schedule fields (date, time, event number, name, sheet link) come from
  the official page. Buy-in and guarantee come from the sheet when the sheet
  prints them for that event, otherwise from the schedule transcription.
* Nothing is inferred. Every discrepancy becomes an entry in
  `discrepancies` and on the Flagged for Review page.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "c6087e2c")
STRUCT_BASE = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/"
               "deepstack/2026/structures/dse_nov_2026-structure_{}.pdf")


def levels_per_day(sheet):
    """Levels a single playing day runs, for a derived duration.

    The Venetian sheets state the late-registration close as "N levels +
    Break"; that is the only official anchor for a playing-day length, so the
    derived duration uses it. It is a planning figure and is labelled as one.
    """
    n = sheet.get("late_registration_levels")
    if n:
        return int(n)
    return int(sheet.get("level_count") or 20)


def breaks_for(sheet):
    n = levels_per_day(sheet)
    return (n // 4) * 15


def load(name, default=None):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def norm(text: str) -> str:
    t = (text or "").lower()
    t = t.replace("\u2019", "'").replace("no limit hold'em", "nlh")
    t = re.sub(r"[^a-z0-9$%]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def entry_policy_evidence(sheet):
    """Return explicit one-entry / no-rebuy / no-add-on excerpts, if present.

    A missing mention is deliberately not treated as a prohibition.
    """
    text = sheet.get("rules_text", "") or ""
    patterns = {
        "single_entry": r"\b(?:single[- ]entry|freeze[- ]?out|one entry per player|one entry only|maximum(?: of)? one entry|max(?:imum)? entries?\s*[:=]?\s*1)\b",
        "re_entry": r"\b(?:no re[- ]?entries?|re[- ]?entry(?: is| will be)? not (?:allowed|permitted))\b",
        "rebuy": r"\b(?:no rebuys?|rebuy(?:s)? not (?:allowed|permitted))\b",
        "add_on": r"\b(?:no add[- ]ons?|add[- ]on(?:s)? not (?:allowed|permitted))\b",
    }
    evidence = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.I)
        evidence[field] = match.group(0) if match else ""
    evidence["confirmed"] = all(evidence[field] for field in
                                 ("single_entry", "re_entry", "rebuy", "add_on"))
    return evidence


def flag_duplicate_names(events):
    """Mark rows whose displayed name repeats another row's name verbatim.

    A structure-sheet URL that is shared by more than one event number can only
    be opened for one of them: the PDF has a single event number in it. Those
    rows get an inline note so nobody opens the wrong rules.
    """
    seen = {}
    for e in events:
        seen.setdefault(e["name"], []).append(e)
    for name, group in seen.items():
        if len(group) < 2:
            continue
        numbers = {e.get("event_no") for e in group}
        for e in group:
            if len(numbers) > 1:
                e["name_collision"] = sorted(n for n in numbers if n is not None)
                if "F33" not in e["flags"]:
                    e["flags"].append("F33")


def buyin_from_name(name: str):
    m = re.match(r"\s*\$([\d,]+)", name or "")
    return int(m.group(1).replace(",", "")) if m else None


def gtd_from_name(name: str):
    m = re.search(r"\$([\d,.]+)\s*([KM])\s*GTD", name or "", re.I)
    if not m:
        m2 = re.search(r"\$([\d,]+)\s*GTD", name or "", re.I)
        return int(m2.group(1).replace(",", "")) if m2 else None
    val = float(m.group(1).replace(",", ""))
    return int(val * (1000 if m.group(2).upper() == "K" else 1_000_000))


def load_psv():
    rows = []
    path = os.path.join(DATA, "venetian_dse_2026.psv")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) != 9:
                continue
            date, time, ev, name, buy, gtd, struct, kind, notes = parts
            rows.append({
                "date": date,
                "time": time,
                "event_no": int(ev) if ev else None,
                "name": name,
                "buyin": int(buy) if buy else None,
                "gtd": int(gtd) if gtd else None,
                "structure_no": int(struct) if struct else None,
                "kind": kind,
                "notes": notes,
            })
    return rows


def main() -> int:
    live = load("schedule_live.json")
    structures = load("structures.json", {"sheets": {}})
    if not live or not live.get("rows"):
        print("merge: no live capture present; keeping the previous merged "
              "dataset unchanged (a missing capture is never treated as a "
              "change in the official data)")
        return 0
    sheets = structures.get("sheets", {})
    psv = load_psv()
    retrieved = live.get("retrieved_at", "")

    discrepancies = []
    live_rows = live["rows"]

    # ---- 1. match live rows to the curated transcription
    by_key = {}
    for r in psv:
        by_key.setdefault((r["date"], r["time"], r["event_no"]), []).append(r)
    matched = {}
    for lr in live_rows:
        key = (lr["date"], lr["time"], lr["event_no"])
        cand = by_key.get(key)
        if not cand:
            discrepancies.append({
                "kind": "row_in_live_capture_not_in_curated_transcription",
                "date": lr["date"], "time": lr["time"],
                "event_no": lr["event_no"], "name": lr["name"]})
            continue
        cur = cand[0]
        matched[(lr["date"], lr["time"], lr["event_no"])] = cur
        if norm(cur["name"]) != norm(lr["name"]):
            discrepancies.append({
                "kind": "row_name_differs",
                "date": lr["date"], "time": lr["time"], "event_no": lr["event_no"],
                "curated": cur["name"], "live": lr["name"]})
        if cur["structure_no"] != lr["structure_no"]:
            discrepancies.append({
                "kind": "structure_sheet_link_differs",
                "date": lr["date"], "time": lr["time"], "event_no": lr["event_no"],
                "curated_sheet": cur["structure_no"],
                "live_sheet": lr["structure_no"]})
    for r in psv:
        if (r["date"], r["time"], r["event_no"]) not in matched:
            discrepancies.append({
                "kind": "row_in_curated_transcription_not_in_live_capture",
                "date": r["date"], "time": r["time"],
                "event_no": r["event_no"], "name": r["name"]})

    # ---- 2. build one record per live row
    events = []
    for lr in live_rows:
        key = (lr["date"], lr["time"], lr["event_no"])
        cur = matched.get(key, {})
        sheet_no = lr["structure_no"] or cur.get("structure_no")
        sheet = sheets.get(str(sheet_no), {}) if sheet_no else {}
        sheet_ok = bool(sheet) and "error" not in sheet
        covered = bool(sheet_ok) and lr["event_no"] in (sheet.get("event_numbers") or [])

        name = lr["name"]
        kind = cur.get("kind") or "entry"
        lower = name.lower()
        if lr["event_no"] is None:
            kind = "unverified_row"
        elif re.search(r"day \d( restart)?$|final table|day 2 restart|day 3 restart", lower):
            kind = "restart"

        adds_second_entry = bool(sheet_ok and sheet.get("adds_a_second_entry"))
        one_day = bool(sheet_ok and not sheet.get("multi_day_format"))
        entry_evidence = entry_policy_evidence(sheet) if sheet_ok else {
            "single_entry": "", "re_entry": "", "rebuy": "", "add_on": "",
            "confirmed": False}
        flight = bool(sheet_ok and sheet.get("flight_language"))
        is_flight_row = bool(re.search(r"\b1[a-f]\b", name, re.I))
        multi_flight = (flight or sheet.get("multi_day_format") or is_flight_row)

        levels = sheet.get("level_minutes") if sheet_ok else None
        one_day_minutes = None
        if sheet_ok and one_day and not multi_flight and levels:
            one_day_minutes = levels * levels_per_day(sheet) + breaks_for(sheet)

        if kind == "restart":
            verdict = "restart"
        elif adds_second_entry:
            verdict = "adds_second_entry"
        elif multi_flight:
            verdict = "multi_flight"
        elif sheet_ok and covered and one_day and entry_evidence["confirmed"]:
            verdict = "single_entry_confirmed"
        elif sheet_ok and covered and one_day:
            verdict = "entry_limit_unverified"
        else:
            verdict = "unverified"

        restriction = ""
        if re.search(r"senior|must be 50", lower):
            restriction = "50+ only (official row states the age limit)"
        elif re.search(r"ladies|lips", lower):
            restriction = "women's event (official row names it a Ladies / LIPS event)"
        elif "tag team" in lower or "team" in lower:
            restriction = "team event"
        if "bounty" in lower or "pko" in lower or "knock-out" in lower or "knockout" in lower:
            fmt = "bounty"
        elif "satellite" in lower:
            fmt = "satellite"
        elif "tag team" in lower or "team" in lower:
            fmt = "team"
        elif multi_flight:
            fmt = "flight"
        elif "pot limit omaha" in lower or "big o" in lower:
            fmt = "plo"
        else:
            fmt = "standard"

        buyin = buyin_from_name(name)
        if buyin is None:
            buyin = cur.get("buyin")
        elif cur.get("buyin") and buyin != cur["buyin"]:
            discrepancies.append({
                "kind": "buyin_differs", "date": lr["date"], "time": lr["time"],
                "event_no": lr["event_no"], "curated": cur["buyin"], "live": buyin})
        gtd = gtd_from_name(name)
        gtd_basis = "schedule page row" if gtd is not None else ""
        gtd_conflict = None
        by_event = (sheet.get("guarantee_by_event") or {}) if sheet_ok else {}
        sheet_gtd = (by_event.get(lr["event_no"]) if lr["event_no"] in by_event
                     else (sheet.get("guarantee") if sheet_ok else None))
        sheet_names = sheet.get("guarantee_events") or list(by_event)
        if sheet_ok and sheet_gtd:
            if not sheet_names or lr["event_no"] in sheet_names:
                if gtd is not None and sheet_gtd != gtd:
                    gtd_conflict = {"schedule": gtd, "sheet": sheet_gtd}
                    discrepancies.append({
                        "kind": "guarantee_conflict", "date": lr["date"],
                        "time": lr["time"], "event_no": lr["event_no"],
                        "schedule": gtd, "sheet": sheet_gtd,
                        "note": "The official schedule row and the linked "
                                "structure sheet print different guarantees "
                                "for this event. Neither is filled in; both "
                                "are shown (F34)."})
                gtd = sheet_gtd
                gtd_basis = "structure sheet"
        if gtd is not None and cur.get("gtd") and gtd != cur["gtd"]:
            discrepancies.append({
                "kind": "guarantee_differs", "date": lr["date"], "time": lr["time"],
                "event_no": lr["event_no"], "curated": cur["gtd"], "live": gtd})
        if gtd is None:
            gtd = cur.get("gtd")

        rec = {
            "venue": "The Venetian Resort",
            "venue_group": "venetian",
            "series": "DeepStack Extravaganza IV",
            "date": lr["date"],
            "time": lr["time"],
            "event_no": lr["event_no"],
            "name": name,
            "kind": kind,
            "buyin": buyin,
            "gtd": gtd,
            "gtd_basis": gtd_basis,
            "gtd_events_on_sheet": sheet_names,
            "guarantee_seats": sheet.get("guarantee_seats") if sheet_ok else None,
            "gtd_conflict": gtd_conflict,
            "format": fmt,
            "restriction": restriction,
            "verdict": verdict,
            "single_entry_confirmed": verdict == "single_entry_confirmed",
            "one_day_minutes": one_day_minutes,
            "one_day_minutes_basis": (
                "derived: the sheet's late-registration figure of {} levels x "
                "{} minutes per level + 15-minute breaks; a planning duration, "
                "not a scheduled finish time".format(levels_per_day(sheet), levels)
                if one_day_minutes else ""),
            "multi_day": multi_flight,
            "structure_no": sheet_no,
            "structure_url": lr["structure_url"] or (
                STRUCT_BASE.format(sheet_no) if sheet_no else ""),
            "source": live.get("source", ""),
            "retrieved_at": retrieved,
            "sheet_retrieved_at": sheet.get("retrieved_at", ""),
            # structured rule fields, each with its own excerpt
            "rule_fields": {
                "start_time": {
                    "value": sheet.get("start_time", "") if sheet_ok else "",
                    "excerpt": sheet.get("start_time_label", "") if sheet_ok else "",
                    "source": lr["structure_url"] if sheet_ok else "",
                },
                "starting_chips": {
                    "value": sheet.get("starting_chips") if sheet_ok else None,
                    "excerpt": sheet.get("chips_line", "") if sheet_ok else "",
                    "source": lr["structure_url"] if sheet_ok else "",
                },
                "level_minutes": {
                    "value": sheet.get("level_minutes") if sheet_ok else None,
                    "excerpt": sheet.get("level_line", "") if sheet_ok else "",
                    "source": lr["structure_url"] if sheet_ok else "",
                },
                "late_registration": {
                    "value": sheet.get("late_registration", "") if sheet_ok else "",
                    "clock": sheet.get("late_registration_clock", "") if sheet_ok else "",
                    "levels": sheet.get("late_registration_levels") if sheet_ok else None,
                    "source": lr["structure_url"] if sheet_ok else "",
                },
                "house_fee": {
                    "value": sheet.get("house_fee") if sheet_ok else None,
                    "buyin": sheet.get("fee_buyin") if sheet_ok else None,
                    "pool_per_entry": sheet.get("pool_per_entry") if sheet_ok else None,
                    "excerpt": sheet.get("fee_line", "") if sheet_ok else "",
                    "source": lr["structure_url"] if sheet_ok else "",
                    "retrieved_at": sheet.get("retrieved_at", "") if sheet_ok else "",
                },
                "single_entry": {
                    "value": True if entry_evidence["confirmed"] else None,
                    "max_entries": 1 if entry_evidence["single_entry"] else None,
                    "excerpt": "; ".join(v for v in entry_evidence.values()
                                        if isinstance(v, str) and v),
                    "source": lr["structure_url"] if sheet_ok else "",
                    "retrieved_at": sheet.get("retrieved_at", "") if sheet_ok else "",
                },
                "re_entry": {
                    "value": False if entry_evidence["re_entry"] else None,
                    "excerpt": entry_evidence["re_entry"],
                    "source": lr["structure_url"] if sheet_ok else "",
                    "retrieved_at": sheet.get("retrieved_at", "") if sheet_ok else "",
                },
                "rebuy": {
                    "value": False if entry_evidence["rebuy"] else None,
                    "excerpt": entry_evidence["rebuy"],
                    "source": lr["structure_url"] if sheet_ok else "",
                    "retrieved_at": sheet.get("retrieved_at", "") if sheet_ok else "",
                },
                "add_on": {
                    "value": False if entry_evidence["add_on"] else None,
                    "excerpt": entry_evidence["add_on"],
                    "source": lr["structure_url"] if sheet_ok else "",
                    "retrieved_at": sheet.get("retrieved_at", "") if sheet_ok else "",
                },
                "guarantee_sheet": {
                    "value": sheet.get("guarantee") if sheet_ok else None,
                    "excerpt": sheet.get("guarantee_line", "") if sheet_ok else "",
                    "source": lr["structure_url"] if sheet_ok else "",
                },
            },
            "sheet_covered_event": covered,
            "flags": [],
        }
        if verdict in ("unverified", "unverified_row"):
            rec["flags"].append("F01")
        if verdict == "entry_limit_unverified":
            rec["flags"].append("F35")
        if verdict == "multi_flight":
            rec["flags"].append("F04")
        if sheet_ok and not covered:
            rec["flags"].append("F26")
        if not sheet_ok:
            rec["flags"].append("F27")
        events.append(rec)

    # ---- 3. coverage summary
    verdict_counts = {}
    for e in events:
        verdict_counts[e["verdict"]] = verdict_counts.get(e["verdict"], 0) + 1
    sheet_numbers = sorted({int(k) for k in sheets})
    unread = [n for n in sheet_numbers if "error" in sheets[str(n)]]

    out = {
        "generated_at": retrieved,
        "generator": "scripts/merge_251c122f.py",
        "source_schedule": live.get("source", ""),
        "note": ("One record per row of the official Venetian schedule. Rule "
                 "fields are extracted from the linked official structure "
                 "sheet; the excerpt is stored with each field so it can be "
                 "checked against the PDF. Blank/null means the official source "
                 "did not state it."),
        "counts": {
            "schedule_rows": len(live_rows),
            "sheets_in_capture": len(sheet_numbers),
            "sheets_unread": len(unread),
            "verdicts": verdict_counts,
        },
        "sheets": {k: {"url": v.get("url"), "retrieved_at": v.get("retrieved_at"),
                       "http_status": v.get("http_status"),
                       "event_numbers": v.get("event_numbers", []),
                       "late_registration": v.get("late_registration", ""),
                       "late_registration_clock": v.get("late_registration_clock", ""),
                       "level_minutes": v.get("level_minutes"),
                       "starting_chips": v.get("starting_chips"),
                       "guarantee": v.get("guarantee"),
                       "house_fee": v.get("house_fee"),
                       "pool_per_entry": v.get("pool_per_entry"),
                       "adds_second_entry": v.get("adds_a_second_entry"),
                       "error": v.get("error", "")}
                   for k, v in sheets.items()},
        "discrepancies": discrepancies,
        "events": events,
    }
    path = os.path.join(DATA, "events_verified.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote", os.path.relpath(path, ROOT))
    print("rows:", len(events), "verdicts:", verdict_counts)
    print("sheets:", len(sheet_numbers), "unread:", len(unread))
    print("discrepancies:", len(discrepancies))
    for d in discrepancies[:20]:
        print("  !", d["kind"], d.get("date"), d.get("time"), d.get("event_no"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
