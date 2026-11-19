#!/usr/bin/env python3
"""Session 2723deea - independent re-read diff of the trip-window schedule rows.

Compares the hand transcription of the official Venetian DeepStack Extravaganza IV
schedule page made in this session (data/2723deea/official_schedule_window_2026-11-19.tsv,
fetched 2026-11-19) against data/ea99006a/venetian.json for the automatically
selected planning window.

What it checks per row, and what it deliberately does NOT check:
  * date, start time, event number, structure-sheet number: exact string match;
  * event name: compared after lower-casing, collapsing whitespace, dropping the
    "<br>" markup the page uses and dropping the descriptive "<br>- ..." tail,
    because the site's name field carries that tail and the page's row carries it
    after a line break.  A difference is reported, never auto-fixed.
  * buy-in, house fee and guarantee are NOT on the schedule page at all - they live
    on the structure sheets - so they are not compared here.  They are recorded in
    data/2723deea/reverify.json against the sheet text read in this session.

Exit code 0 = every comparable field matches; 1 = a mismatch (printed).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "data", "2723deea", "official_schedule_window_2026-11-19.tsv")
DATA = os.path.join(ROOT, "data", "ea99006a", "venetian.json")
OUT = os.path.join(ROOT, "data", "2723deea", "schedule_diff.json")
WINDOW = ("2026-12-06", "2026-12-12")


def norm_name(s):
    s = (s or "").replace("<br>", " ")
    s = re.sub(r"-\s+", "-", s)          # "- $200" tails stay attached to nothing
    s = s.split(" - ")[0]                 # the site stores the page's "<br>- ..." tail
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def to24(t):
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", t.strip(), re.I)
    h, mi, ap = int(m.group(1)), m.group(2), m.group(3).upper()
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return "%02d:%s" % (h, mi)


def main():
    rows = []
    with open(TSV, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            d, t, no, name, sheet = line.rstrip("\n").split("\t")
            rows.append({"date": d, "start": to24(t), "event_no": no, "name": name,
                         "sheet_no": sheet})
    ven = [e for e in json.load(open(DATA, encoding="utf-8"))
           if WINDOW[0] <= e.get("date", "") <= WINDOW[1]]

    def key(r):
        return (r["date"], r["start"], r["event_no"])

    by_key = {}
    for e in ven:
        by_key.setdefault(key(e), []).append(e)

    diffs, matched = [], 0
    used = set()
    for r in rows:
        cands = [e for e in by_key.get(key(r), []) if id(e) not in used]
        if not cands:
            diffs.append({"kind": "missing_from_site", "row": r})
            continue
        e = cands[0]
        used.add(id(e))
        matched += 1
        if norm_name(r["name"]) != norm_name(e.get("name")):
            diffs.append({"kind": "name_text_differs", "official": r["name"],
                          "site": e.get("name"), "key": key(r)})
        m = re.search(r"structure_(\d+)\.pdf", e.get("source", ""))
        if not m or m.group(1) != r["sheet_no"]:
            diffs.append({"kind": "sheet_number_differs",
                          "official": r["sheet_no"],
                          "site": m.group(1) if m else None, "key": key(r)})
    extra = [e for e in ven if id(e) not in used]
    for e in extra:
        diffs.append({"kind": "missing_from_official_read", "site": {
            "date": e.get("date"), "start": e.get("start"),
            "event_no": e.get("event_no"), "name": e.get("name")}})

    out = {
        "session": "2723deea",
        "read_at": "2026-11-19",
        "official_source": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
        "window": {"from": WINDOW[0], "to": WINDOW[1]},
        "official_rows": len(rows),
        "site_rows_in_window": len(ven),
        "matched_rows": matched,
        "diffs": diffs,
        "note": ("Name differences are the page's '<br>- ...' tail versus the site's joined text and are "
                 "reported, not fixed. Buy-in, house fee and guarantee are not published on the schedule "
                 "page and are verified separately against the structure sheets."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("official rows in window: %d | site rows in window: %d | matched: %d | diffs: %d"
          % (len(rows), len(ven), matched, len(diffs)))
    for d in diffs[:20]:
        print(" -", d)
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
