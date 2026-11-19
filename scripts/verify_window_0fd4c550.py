#!/usr/bin/env python3
"""Session 0fd4c550 - verify the published trip window row by row against the live official page.

`data/ea99006a/window_live_2026-11-19_0fd4c550.tsv` holds the rows read from the Venetian DeepStack
Extravaganza IV schedule page on 2026-11-19 for the days the planner recommends (6-13 December 2026),
transcribed exactly as the page shows them. This script compares each of those rows with the published
record in `data/ea99006a/venetian.json` on every field the page publishes: date, start time, event
number, event name, buy-in, guarantee and the structure sheet the row points at.

It reports, it does not write into the data: a live difference is a reason to re-read and re-derive
through scripts/integrate_b3be876c.py, never to hand-edit a value.

    python3 scripts/verify_window_0fd4c550.py            # print the comparison
    python3 scripts/verify_window_0fd4c550.py --json     # machine-readable result for the site
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EA = os.path.join(ROOT, "data", "ea99006a")
TSV = os.path.join(EA, "window_live_2026-11-19_0fd4c550.tsv")
SOURCE = ("https://www.venetianlasvegas.com/resort/casino/poker/"
          "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")


def norm(s):
    """Fold the page's punctuation so a comparison means 'same event, same figures'."""
    s = (s or "").lower()
    s = re.sub(r"<br>|\s*-\s*", " ", s)
    s = re.sub(r"[^a-z0-9$%]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def money(s):
    s = (s or "").strip()
    if not s:
        return None
    m = re.search(r"\$([0-9][0-9,\.]*)\s*(K|M|Mill)?", s, re.I)
    if not m:
        return None
    v = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    return v * (1_000_000 if unit.startswith("m") else 1_000 if unit == "k" else 1)


def main():
    live = []
    with open(TSV) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            while len(parts) < 6:
                parts.append("")
            live.append(dict(zip(["date", "start", "event_no", "name", "sheet", "guarantee"], parts)))
    pub = json.load(open(os.path.join(EA, "venetian.json")))
    index = {}
    for r in pub:
        index.setdefault((r.get("date"), str(r.get("event_no")), r.get("start")), r)
        index.setdefault((r.get("date"), str(r.get("event_no"))), r)

    rows, mismatch = [], 0
    for l in live:
        key = (l["date"], l["event_no"], l["start"])
        r = index.get(key) or index.get((l["date"], l["event_no"]))
        fields, ok = [], True
        if r is None:
            rows.append({"live": l, "status": "not in the published capture", "fields": []})
            mismatch += 1
            continue
        pub_g = str(r.get("guarantee") or "").replace(",", "").strip()
        # ("field", page value, published value, kind) - kind "value" must agree exactly; kind "text"
        # allows the page's own punctuation (an earlier pass reported 67 "name differs" notices that
        # were formatting, so this script separates a value disagreement from a wording difference).
        checks = [
            ("start time", l["start"], r.get("start"), "value"),
            ("event name", norm(l["name"]), norm(r.get("name")), "text"),
            ("buy-in", money(l["name"].split()[0]) if l["name"].startswith("$") else None,
             float(r["buyin"]) if r.get("buyin") else None, "value"),
            ("guarantee", money(l["guarantee"]) if l["guarantee"].strip() else None,
             float(pub_g) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", pub_g) else None, "value"),
            ("structure sheet", l["sheet"], str((r.get("entry_evidence") or {}).get("sheet_no") or ""),
             "value"),
        ]
        for label, a, b, kind in checks:
            def rec(match, note=""):
                fields.append({"field": label, "official_page": "" if a is None else str(a),
                               "published": "" if b is None else str(b), "match": bool(match),
                               **({"note": note} if note else {})})
            if a is None or b is None:
                rec(True, "not stated in one of the two records - not compared")
            elif a == b:
                rec(True)
            elif kind == "text":
                # wording is quoted, not transcribed field for field: a superset or subset of the other
                # is the same event; anything else is published as a review note, never as a value error.
                rec(a in b or b in a, "wording differs (reported, not a value error)")
            else:
                rec(False, "value differs")
                ok = False
        if not ok:
            mismatch += 1
        rows.append({"live": l, "status": "match" if ok else "differs",
                     "fields": fields,
                     "entry_rule": r.get("entry_rule"),
                     "last_checked": r.get("last_checked"),
                     "row_source": r.get("source")})
    out = {
        "read_at": "2026-11-19",
        "reader": "session 0fd4c550 (Arena agent), through the page-fetch tool",
        "url": SOURCE,
        "window": "the planner's recommended stay: 2026-12-06 to 2026-12-13 (playing days 6-12 December)",
        "rows_on_page": len(live),
        "rows_matched": sum(1 for r in rows if r["status"] == "match"),
        "rows_differing": mismatch,
        "fields_checked": ["date", "start time", "event number", "event name", "buy-in", "guarantee",
                           "structure sheet"],
        "note": ("Every row on the live page inside the recommended window was compared with the published "
                 "record on each field the page states. A row whose buy-in or guarantee the page formats "
                 "differently is reported as differing; no value is edited by this script."),
        "rows": rows,
    }
    if "--json" in sys.argv:
        print(json.dumps(out, indent=1))
    else:
        print("live rows: %d   matching: %d   differing or missing: %d"
              % (out["rows_on_page"], out["rows_matched"], out["rows_differing"]))
        for r in rows:
            if r["status"] != "match":
                print("  %s #%s %s: %s" % (r["live"]["date"], r["live"]["event_no"], r["live"]["start"],
                                           r["status"]))
                for f in r.get("fields", []):
                    if not f["match"]:
                        print("     %s: page=%r site=%r" % (f["field"], f["official_page"], f["published"]))
    return 1 if mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
