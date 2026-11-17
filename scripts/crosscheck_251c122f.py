#!/usr/bin/env python3
"""Cross-check the merged verified dataset and the built site.

Fails (exit 1) when a check that protects the "no hallucination" rule breaks:

  1. every schedule row in the official capture has exactly one merged record;
  2. every record's single-entry verdict can be reproduced from the stored
     rule fields (verdict == single_entry_confirmed only when a sheet was read,
     its event-number list covers the row, and no re-entry language was found);
  3. every row that reports a buy-in or guarantee also carries a source URL;
  4. every structure sheet in the capture has a URL and a retrieval timestamp;
  5. the built site contains no table row that lacks a source link unless it is
     explicitly flagged;
  6. every date/time in the merged dataset exists in the official capture.

Run: python3 scripts/crosscheck_251c122f.py
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "c6087e2c")
errors: list[str] = []
notes: list[str] = []


def load(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    live = load("schedule_live.json")
    merged = load("events_verified.json")
    structures = load("structures.json")

    live_keys = [(r["date"], r["time"], r["event_no"]) for r in live["rows"]]
    merged_keys = [(e["date"], e["time"], e["event_no"]) for e in merged["events"]]
    if sorted(map(str, live_keys)) != sorted(map(str, merged_keys)):
        errors.append("schedule rows and merged records differ: {} vs {}".format(
            len(live_keys), len(merged_keys)))
    dupes = {k for k in merged_keys if merged_keys.count(k) > 1}
    if dupes:
        notes.append("repeated (date,time,event#) keys in the capture: {} "
                     "(flights of one event legitimately share an event "
                     "number)".format(sorted(map(str, dupes))[:6]))

    for e in merged["events"]:
        v = e["verdict"]
        sheet = structures["sheets"].get(str(e.get("structure_no")), {})
        sheet_ok = bool(sheet) and "error" not in sheet
        covered = e["event_no"] in (sheet.get("event_numbers") or []) if sheet_ok else False
        adds = bool(sheet.get("adds_a_second_entry")) if sheet_ok else False
        if v == "single_entry_confirmed":
            if not sheet_ok:
                errors.append("{} {} #{}: confirmed without a read sheet".format(
                    e["date"], e["time"], e["event_no"]))
            elif not covered:
                errors.append("{} {} #{}: confirmed but the sheet's event-number "
                              "list does not cover it".format(
                                  e["date"], e["time"], e["event_no"]))
            elif adds:
                errors.append("{} {} #{}: confirmed although the sheet carries "
                              "re-entry/rebuy/add-on language".format(
                                  e["date"], e["time"], e["event_no"]))
            elif sheet.get("multi_day_format"):
                errors.append("{} {} #{}: confirmed although the sheet is a "
                              "multi-day format".format(
                                  e["date"], e["time"], e["event_no"]))
        if v in ("unverified",) and sheet_ok and covered and not adds \
                and not sheet.get("multi_day_format") \
                and not sheet.get("flight_language") \
                and not re.search(r"\b1[a-f]\b", e.get("name", ""), re.I):
            errors.append("{} {} #{}: left unverified although its read sheet "
                          "supports single entry".format(
                              e["date"], e["time"], e["event_no"]))
        if (e.get("buyin") or e.get("gtd")) and not e.get("source"):
            errors.append("{} {} #{}: value without a source".format(
                e["date"], e["time"], e["event_no"]))
        if not e.get("retrieved_at"):
            errors.append("{} {} #{}: no retrieval timestamp".format(
                e["date"], e["time"], e["event_no"]))
        if e["verdict"] == "single_entry_confirmed" and not e.get("sheet_retrieved_at"):
            errors.append("{} {} #{}: confirmed without a sheet retrieval date".format(
                e["date"], e["time"], e["event_no"]))

    # A guarantee printed on a structure sheet must be recorded with the scope
    # the sheet states, and a conflict must never be filled in silently.
    for e in merged["events"]:
        conf = e.get("gtd_conflict")
        if conf:
            if not conf.get("schedule") or not conf.get("sheet"):
                errors.append("{} {} #{}: guarantee conflict not recorded with "
                              "both values".format(e["date"], e["time"], e["event_no"]))
            if e.get("gtd_basis") != "structure sheet":
                errors.append("{} {} #{}: conflicted guarantee not attributed"
                              .format(e["date"], e["time"], e["event_no"]))
    for n, s in structures["sheets"].items():
        if not s.get("url"):
            errors.append("sheet {}: no URL".format(n))
        if not s.get("retrieved_at"):
            errors.append("sheet {}: no retrieval timestamp".format(n))

    # site-level: every searchable table row that has a Source column must
    # carry a link or be explicitly flagged
    pages = [os.path.join(ROOT, "index.html")]
    pages += glob.glob(os.path.join(ROOT, "pages", "**", "*.html"), recursive=True)
    for f in pages:
        with open(f, encoding="utf-8") as fh:
            txt = fh.read()
        for tbl in re.findall(r"<table[^>]*data-searchable[^>]*>.*?</table>", txt, re.S):
            heads = re.findall(r"<th[^>]*>(.*?)</th>", tbl, re.S)
            if not any("source" in h.lower() for h in heads):
                continue
            for row in re.findall(r"<tr>(.*?)</tr>", tbl, re.S)[1:]:
                if "<td" not in row:
                    continue
                if "<a " in row or "Flagged" in row:
                    continue
                errors.append("{}: row without source link".format(
                    os.path.relpath(f, ROOT)))
                break

    counts = merged["counts"]
    print("merged rows: {}".format(len(merged["events"])))
    print("verdicts:", json.dumps(counts["verdicts"], sort_keys=True))
    print("sheets read: {}/{}".format(
        counts["sheets_in_capture"] - counts["sheets_unread"],
        counts["sheets_in_capture"]))
    print("discrepancies: {}".format(len(merged.get("discrepancies", []))))
    for n in notes:
        print("note:", n)
    if errors:
        print("CROSS-CHECK FAILED")
        for e in errors[:40]:
            print(" -", e)
        return 1
    print("cross-check OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
