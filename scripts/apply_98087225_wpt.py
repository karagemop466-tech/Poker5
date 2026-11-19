#!/usr/bin/env python3
"""Apply the session 98087225 WPT verification to the published data.

Inputs (all official, read 2026-11-19):
  data/98087225/wynn_wpt_schedule_official_2026-11-19.tsv   (transcribed schedule)
  data/98087225/wpt_schedule_check.json                       (scripts/verify_98087225_wpt.py --write)
  data/98087225/wpt_terms_read.json                           (13 events read from the structures PDF)

Effects on data/ea99006a/wpt.json:
  * every row: schedule_check = result of the line-by-line schedule comparison
  * 'multi' rows (re-entry granted by the event's own text in the structures PDF): rule_read_on, parent_event_rule
  * 'unread' rows: source now points to the schedule that supports their values (the structures
    PDF the row previously cited does not contain their terms); entry_rule stays 'unread'
  * flagged schedule/structure conflicts get flag_ref
Effects on data/ea99006a/flags.json: adds F56-F58.
Idempotent: re-running produces the same files.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WPT = ROOT / "data/ea99006a/wpt.json"
FLAGS = ROOT / "data/ea99006a/flags.json"
CHECK = ROOT / "data/98087225/wpt_schedule_check.json"

STRUCT = "https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf"
SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
READ = "2026-11-19"

CONFLICT_FLAG = {
    ("2026-11-30", "13:00", "No Limit Hold'em Day 2"): "F56",
    ("2026-12-03", "13:00", "No Limit Hold'em Day 2"): "F56",
    ("2026-12-05", "11:00", "No Limit Hold'em Day 2"): "F56",
    ("2026-12-21", "20:00", "NLH Turbo"): "F57",
}


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    rows = json.loads(WPT.read_text(encoding="utf-8"))
    check = {d["index"]: d for d in json.loads(CHECK.read_text(encoding="utf-8"))["details"]}
    counts = {"multi_read": 0, "unread_repointed": 0, "parent": 0, "flagged": 0}
    for i, r in enumerate(rows):
        c = check[i]
        label = c.get("schedule_printed_label", "")
        note = "Date, start time, buy-in and printed guarantee matched the official Wynn WPT schedule (read %s)." % READ
        if "Wednesday = Dec 16" in label:
            note += " The schedule prints this block as 'Dec. 18 Wednesday'; read as Wednesday 16 Dec (flag F05)."
        r["schedule_check"] = note
        if c["status"] != "match":
            raise SystemExit("row %d no longer matches the schedule: %s" % (i, c["status"]))

        if r["entry_rule"] == "multi":
            r["rule_read_on"] = READ
            r["rule_source"] = STRUCT
            counts["multi_read"] += 1
            if any(k in r["name"] for k in ("Day 2", "Day 3", "Day 4", "Final Table")):
                r["parent_event_rule"] = True
                counts["parent"] += 1
        elif r["entry_rule"] == "unread":
            r["source"] = SCHED
            r["source_label"] = "official WPT schedule (entry terms not in the structures PDF)"
            r["terms_note"] = ("Entry terms not read. The official WPT structures PDF (read %s) contains terms for 13 events, "
                               "none of which is this one; the per-event structure sheet the schedule refers to was not located."
                               % READ)
            counts["unread_repointed"] += 1

        key = (r["date"], r["start"], r["name"])
        if key in CONFLICT_FLAG:
            r["flag_ref"] = CONFLICT_FLAG[key]
            counts["flagged"] += 1
    dump(WPT, rows)

    flags = json.loads(FLAGS.read_text(encoding="utf-8"))
    flags = [f for f in flags if f["id"] not in ("F56", "F57", "F58")]
    flags += [
        {"id": "F56", "area": "Source defect",
         "title": "WPT Day 2 dates: the official schedule and the structures PDF disagree",
         "detail": "Structures PDF: the $800 No Limit Hold'em Day 2 is Thu Dec 3 at 1 p.m. (the schedule prints Mon Nov 30 1 p.m.); the $1,600 No Limit Hold'em Day 2 is Sat Dec 5 at 11 a.m. (the schedule prints Thu Dec 3 1 p.m.). The schedule's Sat Dec 5 11 a.m. 'No Limit Hold'em Day 2' line carries $1,100 / $5,000,000, which matches neither event. Rows 2026-11-30 13:00, 2026-12-03 13:00 and 2026-12-05 11:00 keep the schedule's date and buy-in, so their date is not confirmed by the structures PDF. Ask the Wynn poker desk which date is correct before planning a Day 2.",
         "source": SCHED, "status": "new (98087225); needs review", "last_updated": READ},
        {"id": "F57", "area": "Source defect",
         "title": "WPT NLH Turbo on Mon Dec 21: 6 p.m. in the structures PDF, 8 p.m. in the schedule",
         "detail": "The structures PDF lists the Monday Dec 21 NLH Turbo at 6 p.m.; the official schedule lists 8 p.m. The row keeps the schedule time (20:00). Confirm before relying on it.",
         "source": SCHED, "status": "new (98087225); needs review", "last_updated": READ},
        {"id": "F58", "area": "Coverage",
         "title": "91 WPT schedule lines have no entry terms in the document the site cited for them",
         "detail": "All 136 WPT rows match the official schedule on date, start time and buy-in, and on guarantee where the schedule prints one (see data/98087225/wpt_schedule_check.json). The structures PDF (read in full on %s) contains terms for 13 events only, and 45 site rows match them (re-entry granted, so classified multi). The other 91 lines (Milestone satellites, Super Gold Million Mystery Bounty, Seniors, Ladies, High Roller, Big O, PLO 6-Max, the Dec 18 NLH and NLH Turbo variants and similar) are not in it. Their rows previously cited that PDF; they now cite the schedule, and their entry terms remain unread and unverified. The schedule says 'See structure sheet for details'; those sheets were not located." % READ,
         "source": STRUCT, "status": "new (98087225); needs review", "last_updated": READ},
    ]
    dump(FLAGS, flags)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
