#!/usr/bin/env python3
"""Line-by-line check of data/ea99006a/wpt.json against the official Wynn WPT schedule.

Source (read 2026-11-19, transcribed to data/98087225/wynn_wpt_schedule_official_2026-11-19.tsv):
  https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf

For every WPT row the script looks for the schedule line with the same date and start time and
compares buy-in and guarantee. It never edits the published data; it writes a report only.

Usage: python3 scripts/verify_98087225_wpt.py [--write]
"""
import csv
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WPT = ROOT / "data/ea99006a/wpt.json"
SCHED = ROOT / "data/98087225/wynn_wpt_schedule_official_2026-11-19.tsv"
REPORT = ROOT / "data/98087225/wpt_schedule_check.json"

MONTHS = {"Nov.": 11, "Dec.": 12}


def sched_date(label):
    # "Dec. 13" -> 2026-12-13 (the printed label is used as-is)
    m = re.match(r"(Nov\.|Dec\.)\s+(\d+)", label.strip())
    return datetime.date(2026, MONTHS[m.group(1)], int(m.group(2))).isoformat()


def sched_time(label):
    m = re.match(r"(\d+)(?::(\d\d))?\s*([ap])\.?m\.?", label.strip().lower())
    h = int(m.group(1)) % 12
    if m.group(3) == "p":
        h += 12
    return "%02d:%02d" % (h, int(m.group(2) or 0))


def norm(s):
    s = s.lower().replace("’", "'").replace("\\", "")
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9$ ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_schedule():
    rows = []
    with open(SCHED, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if not r["time"]:
                continue
            label = r["pdf_date_label"]
            d = sched_date(label)
            if "Wednesday = Dec 16" in r["weekday_label"]:
                d = "2026-12-16"  # printed as 'Dec. 18 Wednesday'; see flag
            rows.append({
                "date": d,
                "time": sched_time(r["time"]),
                "event": r["event"].strip(),
                "buyin": int(r["buyin"]) if r["buyin"].strip().isdigit() else None,
                "guarantee": r["guarantee"].strip(),
                "printed_label": label + " " + r["weekday_label"],
            })
    return rows


def money(v):
    if v in (None, "", "None"):
        return None
    try:
        return int(str(v).replace(",", "").replace("$", ""))
    except ValueError:
        return None


def main():
    write = "--write" in sys.argv
    sched = load_schedule()
    rows = json.loads(WPT.read_text(encoding="utf-8"))
    out = []
    counts = {"match": 0, "buyin_mismatch": 0, "no_schedule_line": 0, "guarantee_mismatch": 0}
    for i, r in enumerate(rows):
        cands = [s for s in sched if s["date"] == r["date"] and s["time"] == r["start"]]
        rec = {"index": i, "date": r["date"], "start": r["start"], "name": r["name"],
               "entry_rule": r["entry_rule"], "buyin": r["buyin"], "guarantee": r["guarantee"]}
        if not cands:
            rec["status"] = "no_schedule_line"
            counts["no_schedule_line"] += 1
            out.append(rec)
            continue
        def _score(s):
            # prefer a schedule line whose money fields agree, then the closest event name
            agree = (money(r["buyin"]) == s["buyin"]) + (money(r["guarantee"]) == money(s["guarantee"]))
            names = set(norm(s["event"]).split()) & set(norm(r["name"]).split())
            return (agree, len(names))
        best = max(cands, key=_score)
        rec["schedule_event"] = best["event"]
        rec["schedule_printed_label"] = best["printed_label"]
        rec["schedule_buyin"] = best["buyin"]
        rec["schedule_guarantee"] = best["guarantee"]
        problems = []
        if money(r["buyin"]) is not None and best["buyin"] is not None and money(r["buyin"]) != best["buyin"]:
            problems.append("buyin")
            counts["buyin_mismatch"] += 1
        g_row = money(r["guarantee"])
        g_sch = money(best["guarantee"]) if best["guarantee"][:1] == "$" or best["guarantee"][:1].isdigit() else None
        if g_row is not None and g_sch is not None and g_row != g_sch:
            problems.append("guarantee")
            counts["guarantee_mismatch"] += 1
        rec["status"] = "mismatch:" + ",".join(problems) if problems else "match"
        if not problems:
            counts["match"] += 1
        out.append(rec)
    summary = {"checked_at": "2026-11-19", "source": "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
               "rows": len(rows), "counts": counts, "details": out}
    print(json.dumps({k: v for k, v in summary.items() if k != "details"}, indent=1))
    for rec in out:
        if rec["status"] != "match":
            print(rec["date"], rec["start"], rec["name"][:55].ljust(55), rec["status"], rec.get("schedule_event", "")[:45])
    if write:
        REPORT.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", REPORT.relative_to(ROOT))


if __name__ == "__main__":
    main()
