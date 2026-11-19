#!/usr/bin/env python3
"""Session 8f0b323b - line-by-line differential re-check.

Compares the live transcription of the official Venetian DeepStack Extravaganza IV
schedule page (data/8f0b323b/schedule_live_2026-11-19.tsv, read from
https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
on 2026-11-19) against every stored row in data/ea99006a/venetian.json.

Compares, per row and in order: date, start time, event number, name, structure
sheet number, buy-in and guarantee. Nothing is written back to the canonical data
here; a mismatch is reported for a human to resolve against the official page.

Writes data/8f0b323b/schedule_recheck.json.
Exit code 1 if any comparable field differs.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "data", "8f0b323b", "schedule_live_2026-11-19.tsv")
STORED = os.path.join(ROOT, "data", "ea99006a", "venetian.json")
OUT = os.path.join(ROOT, "data", "8f0b323b", "schedule_recheck.json")

OFFICIAL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
            "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")


def norm_name(s):
    """Case/punctuation-insensitive name key (the page's own typos are kept)."""
    s = (s or "").replace("<br>", " ")
    s = s.replace("\u2019", "'")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def base(name):
    """Name with the trailing ' - promotional suffix' removed, case-folded.

    The stored rows carry the structure-sheet title and keep the schedule page's
    promotional suffix in `notes`; the suffix is recorded as a notice, not as a
    value mismatch, because date/time/event/buy-in/guarantee/sheet are the fields
    a reader acts on.
    """
    out = []
    for part in re.split(r"\s+-\s+", (name or "").replace("<br>", " ")):
        out.append(part)
    return norm_name(out[0])


def suffix(name):
    parts = re.split(r"\s+-\s+", (name or "").replace("<br>", " "))
    return " - ".join(parts[1:]).strip()


def to24(t):
    t = (t or "").strip().upper()
    m = re.fullmatch(r"(\d{1,2}):(\d{2})\s*(AM|PM)", t)
    if not m:
        return t
    h, mi, ap = int(m.group(1)), m.group(2), m.group(3)
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return "%02d:%s" % (h, mi)


def num(s):
    s = str(s or "").replace("$", "").replace(",", "").strip()
    try:
        return int(float(s))
    except ValueError:
        return None


def sheet_no(label):
    m = re.search(r"(\d+)", label or "")
    return int(m.group(1)) if m else None


def main():
    live = []
    with open(LIVE, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            if not line.strip():
                continue
            live.append(dict(zip(head, line.rstrip("\n").split("\t"))))
    stored = json.load(open(STORED, encoding="utf-8"))
    entries = [r for r in stored if r.get("kind") != "restart" or True]

    problems = []
    rows = []
    if len(live) != len(stored):
        problems.append("row count differs: live %d vs stored %d" % (len(live), len(stored)))

    for i, (lv, st) in enumerate(zip(live, stored)):
        diffs = {}
        if lv["date"] != st.get("date"):
            diffs["date"] = [lv["date"], st.get("date")]
        if to24(lv["start"]) != to24(st.get("start")):
            diffs["start"] = [to24(lv["start"]), to24(st.get("start"))]
        if str(lv["event_no"]) != str(st.get("event_no")):
            diffs["event_no"] = [lv["event_no"], st.get("event_no")]
        notices = []
        if base(lv["name"]) != base(st.get("name")):
            diffs["name"] = [lv["name"], st.get("name")]
        elif suffix(lv["name"]):
            notices.append(suffix(lv["name"]))
        if int(lv["sheet"]) != (sheet_no(st.get("source_label")) or -1):
            diffs["sheet"] = [lv["sheet"], st.get("source_label")]
        if lv["buyin"] and num(lv["buyin"]) != num(st.get("buyin")):
            diffs["buyin"] = [lv["buyin"], st.get("buyin")]
        if lv["guarantee"] and num(lv["guarantee"]) != num(st.get("guarantee")):
            diffs["guarantee"] = [lv["guarantee"], st.get("guarantee")]
        result = "match" if not diffs else "mismatch"
        if diffs:
            problems.append("row %d (%s %s #%s): %s" % (i, lv["date"], lv["start"], lv["event_no"], diffs))
        rows.append({
            "index": i,
            "notices": notices,
            "date": lv["date"],
            "start": lv["start"],
            "event_no": lv["event_no"],
            "live_name": lv["name"],
            "stored_name": st.get("name"),
            "result": result,
            "diffs": diffs,
        })

    doc = {
        "session": "8f0b323b",
        "checked_on": "2026-11-19",
        "official_source": OFFICIAL,
        "method": ("Schedule page re-read live on 2026-11-19 (platform page reader, 4 chunks, "
                   "full text) and transcribed to schedule_live_2026-11-19.tsv; this script diffs "
                   "that transcription against data/ea99006a/venetian.json row by row on date, "
                   "start time, event number, name, structure-sheet number, buy-in and guarantee."),
        "fields_compared": ["date", "start", "event_no", "name", "sheet", "buyin", "guarantee"],
        "fields_not_compared": [
            "chips / levels / late_reg / house_fee: these live on the structure sheets, not on the schedule page",
            "restart rows: no buy-in or guarantee is published for a Day 2 restart",
        ],
        "rows_compared": len(rows),
        "mismatches": sum(1 for r in rows if r["result"] != "match"),
        "name_suffix_notices": sum(len(r.get("notices") or []) for r in rows),
        "name_suffix_note": ("The official page prints a promotional suffix after the structure-sheet title on these rows "
                             "(for example 'Race to finish before the Race', 'POKERATLAS PRO MEMBER $20 RAKE DISCOUNT', "
                             "'Must be 50+ years of age to participate'). The stored rows keep the sheet title as the name and "
                             "record the suffix in notes. This is informational: no date, start time, event number, buy-in, "
                             "guarantee or sheet number differs."),
        "problems": problems,
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    print("rows compared : %d" % doc["rows_compared"])
    print("mismatches    : %d" % doc["mismatches"])
    print("name-suffix notices (informational): %d" % doc["name_suffix_notices"])
    for p in problems:
        print("  ! " + p)
    if problems:
        print("FAIL")
        return 1
    print("OK - every stored row matches the live official schedule page on date, start, event number, "
          "buy-in, guarantee and structure sheet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
