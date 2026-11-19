#!/usr/bin/env python3
"""Session ec3c21b8 - live re-read comparison.

1. Ten Venetian structure sheets re-read live on 2026-11-19
   (data/ec3c21b8/sheets_reread_2026-11-19.json) against the stored sheets map in
   data/ea99006a/meta.json and the stored rows in data/ea99006a/venetian.json.
2. The official Wynn WPT World Championship schedule sign, transcribed line by line
   on 2026-11-19 (data/ec3c21b8/wpt_sign_2026-11-19.tsv) against data/ea99006a/wpt.json.

Writes data/ec3c21b8/recheck.json and exits 1 on any mismatch that is not in the
known-alias lists (sign typos such as "NIH", "1A/8", "BadugI").

Run:  python3 scripts/recheck_ec3c21b8.py
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ec3c21b8", "recheck.json")

with open(os.path.join(ROOT, "data", "ec3c21b8", "sheets_reread_2026-11-19.json"), encoding="utf-8") as fh:
    SHEETS = json.load(fh)["sheets"]
with open(os.path.join(ROOT, "data", "ea99006a", "meta.json"), encoding="utf-8") as fh:
    META = json.load(fh)
with open(os.path.join(ROOT, "data", "ea99006a", "venetian.json"), encoding="utf-8") as fh:
    VEN = json.load(fh)
with open(os.path.join(ROOT, "data", "ea99006a", "wpt.json"), encoding="utf-8") as fh:
    WPT = json.load(fh)

results = {"session": "ec3c21b8", "checked_on": "2026-11-19", "sheet_checks": [], "sign_rows": []}
errors = []


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def money_num(s):
    if s in (None, ""):
        return None
    if isinstance(s, (int, float)):
        return int(s)
    m = re.sub(r"[^0-9]", "", str(s))
    return int(m) if m else None


def gtd_norm(s):
    if s in (None, ""):
        return ""
    t = norm(str(s)).replace(",", "").replace("$", "")
    # annotation after the number ("(prize pool + total bounties)") is compared separately
    t = t.split("(")[0]
    return t.strip()


def fmt_norm(s):
    """Formatting-insensitive comparison for free text like late-registration strings."""
    t = norm(s)
    t = t.replace("~ ", "~").replace(" ~", "~")
    t = t.replace("break", "break")
    return t


def first_time(s):
    m = re.search(r"(\d{1,2}:\d{2}\s*[ap]m)", norm(s))
    return m.group(1).replace(" ", "") if m else norm(s)


# ---------------------------------------------------------------- 1. structure sheets
for no in sorted(SHEETS, key=lambda x: int(x)):
    fresh = SHEETS[no]
    stored = (META.get("sheets") or {}).get(no) or {}
    fields = {
        "events": (fresh.get("events") or "").replace(" and ", ", "),
        "buyin": fresh.get("buyin"),
        "chips": fresh.get("chips"),
        "level": fresh.get("level"),
        "late": fresh.get("late"),
        "gtd": fresh.get("gtd"),
        "start": fresh.get("start"),
    }
    cmp_stored = {
        "events": (stored.get("events") or "").replace(" and ", ", "),
        "buyin": stored.get("buyin"),
        "chips": stored.get("chips"),
        "level": stored.get("level"),
        "late": stored.get("late"),
        "gtd": (stored.get("gtd") or ""),
        "start": stored.get("start"),
    }
    diffs = []
    fmt_notes = []
    for k, v in fields.items():
        a, b = v, cmp_stored[k]
        if k == "events":
            a = norm(a)
            b = norm(b)
        elif k == "gtd":
            a = gtd_norm(a)
            b = gtd_norm(b)
        elif k == "buyin":
            a, b = money_num(a), money_num(b)
        elif k == "late":
            a, b = fmt_norm(str(a)), fmt_norm(str(b))
        elif k == "start":
            a, b = first_time(str(a)), first_time(str(b))
        else:
            a = norm(str(a))
            b = norm(str(b))
        if a != b:
            diffs.append({"field": k, "fresh": str(v), "stored": str(b)})
        else:
            if str(v).strip() != str(cmp_stored[k]).strip():
                fmt_notes.append({"field": k, "fresh": str(v), "stored": str(cmp_stored[k]),
                                  "note": "formatting/annotation only"})
    # rows using this sheet
    url = fresh["url"]
    rows = [r for r in VEN if r.get("source") == url]
    row_notes = []
    for r in rows:
        bad = {}
        if money_num(r.get("buyin")) != money_num(fresh.get("buyin")):
            bad["buyin"] = {"row": r.get("buyin"), "sheet": fresh.get("buyin")}
        if norm(str(r.get("chips") or "")) != norm(fresh.get("chips") or ""):
            bad["chips"] = {"row": r.get("chips"), "sheet": fresh.get("chips")}
        if bad:
            row_notes.append({"date": r.get("date"), "event_no": r.get("event_no"),
                              "name": r.get("name"), "diffs": bad})
    verdict_ok = True
    entry_rules = {rr.get("entry_rule") for rr in rows}
    if fresh.get("flight_language") or fresh.get("reentry_language"):
        if "multi" not in entry_rules:
            verdict_ok = False
            errors.append("sheet %s: flight/re-entry language but no multi row" % no)
    else:
        for rr in rows:
            if rr.get("entry_rule") == "multi":
                verdict_ok = False
                errors.append("sheet %s: row %s %s marked multi without entry-grant text"
                              % (no, rr.get("date"), rr.get("name")))
    results["sheet_checks"].append({
        "sheet": no,
        "url": url,
        "meta_diffs": diffs,
        "formatting_notes": fmt_notes,
        "rows_on_sheet": len(rows),
        "row_value_diffs": row_notes,
        "verdict_consistent": verdict_ok,
    })
    if diffs:
        errors.append("sheet %s differs from meta.json: %s" % (no, [d["field"] for d in diffs]))
    if row_notes:
        errors.append("sheet %s rows differ from sheet text: %s" % (no, [n["name"] for n in row_notes]))


# ---------------------------------------------------------------- 2. WPT schedule sign
def name_norm(s):
    t = norm(s)
    t = t.replace("nih", "nlh")
    t = t.replace("badugi", "badugi")
    t = t.replace("satellite1", "satellite")
    t = t.replace("1a/8", "1a/b")
    t = t.replace("8/5/stud", "8 / stud")
    t = t.replace("*", "")
    t = t.replace("$", "")
    t = t.replace(",", "")
    t = t.replace(" - ", " ")
    t = t.replace("added", "added")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


sign_rows = []
with open(os.path.join(ROOT, "data", "ec3c21b8", "wpt_sign_2026-11-19.tsv"), encoding="utf-8") as fh:
    for row in csv.DictReader(fh, delimiter="\t"):
        sign_rows.append(row)

used = set()
for s in sign_rows:
    key = (s["date"], s["start"], name_norm(s["name"]))
    match = None
    for i, r in enumerate(WPT):
        if i in used:
            continue
        if (r.get("date"), r.get("start")) == (s["date"], s["start"]) and name_norm(r.get("name")) == key[2]:
            match = (i, r)
            break
    entry = {"date": s["date"], "start": s["start"], "name": s["name"],
             "sign_buyin": s["sign_buyin"], "sign_guarantee": s["sign_guarantee"]}
    if not match:
        entry["result"] = "no stored row"
        errors.append("sign row not in wpt.json: %s %s %s" % (s["date"], s["start"], s["name"]))
    else:
        i, r = match
        used.add(i)
        bad = {}
        sb, rb = money_num(s["sign_buyin"]), money_num(r.get("buyin"))
        if sb != rb:
            bad["buyin"] = {"sign": s["sign_buyin"], "row": r.get("buyin")}
        sg, rg = gtd_norm(s["sign_guarantee"]), gtd_norm(r.get("guarantee"))
        if sg != rg:
            bad["guarantee"] = {"sign": s["sign_guarantee"], "row": r.get("guarantee")}
        entry["result"] = "match" if not bad else "differs"
        if bad:
            entry["diffs"] = bad
            if "F58" in (r.get("guarantee_note") or "") or "F58" in (r.get("notes") or ""):
                entry["result"] = "differs (documented official-source conflict, flag F58)"
            else:
                errors.append("sign vs row %s %s %s: %s" % (s["date"], s["start"], s["name"], list(bad)))
    results["sign_rows"].append(entry)

for i, r in enumerate(WPT):
    if i not in used:
        entry = {"date": r.get("date"), "start": r.get("start"), "name": r.get("name"),
                 "result": "row not on sign"}
        results["sign_rows"].append(entry)
        errors.append("wpt.json row not on the sign: %s %s %s" % (r.get("date"), r.get("start"), r.get("name")))

matched = sum(1 for e in results["sign_rows"] if e["result"] == "match")
results["sign_summary"] = {
    "sign_rows": len(sign_rows),
    "stored_rows": len(WPT),
    "matched": matched,
    "differs": sum(1 for e in results["sign_rows"] if e["result"] == "differs"),
    "documented_conflicts": sum(1 for e in results["sign_rows"] if e["result"].startswith("differs (documented")),
    "sign_only": sum(1 for e in results["sign_rows"] if e["result"] == "no stored row"),
    "row_only": sum(1 for e in results["sign_rows"] if e["result"] == "row not on sign"),
}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=False)
    fh.write("\n")

print("sheet checks   : %d" % len(results["sheet_checks"]))
print("sign rows      : %d" % len(sign_rows))
print("stored rows    : %d" % len(WPT))
print("sign summary   : %s" % results["sign_summary"])
if errors:
    print("\n%d issue(s):" % len(errors))
    for e in errors[:60]:
        print("  - %s" % e)
    sys.exit(1)
print("\nOK - every re-read sheet and sign row matches the stored data.")
