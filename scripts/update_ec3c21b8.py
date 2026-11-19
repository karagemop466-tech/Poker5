#!/usr/bin/env python3
"""Session ec3c21b8 - one-shot data corrections from the 2026-11-19 live re-read.

Every change is listed in data/ec3c21b8/reverify.json and on the Flagged for review
page (F56-F59). Re-run  python3 scripts/recheck_ec3c21b8.py  afterwards to confirm
the stored data now matches the live-read transcription.

Changes:
  wpt.json
    1. Fill the 24 blank satellite guarantees from the official schedule sign
       (seat/prize counts, verbatim; the sign states none for the $25K High Roller
       satellite, so that cell stays blank).
    2. The three "No Limit Hold'em Day 2" rows (Nov 30, Dec 3, Dec 5): the schedule
       sign prints the NEXT event's money figures in these rows' columns, while the
       event terms pages state each event's own Day 2 date/time. Publish the
       terms-page figures, keep both readings in guarantee_note, and correct the
       Dec 5 row's rule excerpt, which the earlier capture had taken from the WPT
       Prime Championship section (flag F58).
    3. Dec 21 NLH Turbo: note the official-source start-time conflict (terms page
       6 p.m. vs schedule sign 8 p.m.; published value follows the sign; F58).
    4. last_checked = 2026-11-19 on every row (both official Wynn PDFs re-read).
  venetian.json
    5. Event #39 (LIPS Ladies, sheet 32) entry/restart/final rows: the sheet grants
       no re-entry, rebuy or add-on and has no flights; the earlier capture had
       mislabelled a Day-2 continuation sentence as flight language and published
       the rows as multi-entry. Publish "Cap not stated" (S1 condition 4 - no
       multi-day structure - is not met; no entry-grant sentence exists), with the
       corrected basis and evidence (flag F56).
    6. last_checked = 2026-11-19 on every row whose structure sheet was re-read
       live this session (sheets 12, 17, 19, 20, 21, 27, 31, 32, 33, 37).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-19"

SIGN_URL = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
TERMS_URL = "https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf"

# (date, start, name prefix) -> guarantee text exactly as the sign prints it
SAT_GUARANTEES = {
    ("2026-12-03", "19:00", "Double Play"): "25 Prizes",
    ("2026-12-04", "19:00", "Double Play"): "25 Prizes",
    ("2026-12-06", "12:00", "Milestone Satellite to $1,100 Prime"): "50 Seats",
    ("2026-12-06", "19:00", "Double Play"): "25 Prizes",
    ("2026-12-07", "19:00", "Milestone Satellite Package"): "25 Prizes",
    ("2026-12-08", "19:00", "Milestone Satellite to $10,400 World Championship"): "25 Seats",
    ("2026-12-09", "14:00", "Milestone Satellite to $10,400 World Championship"): "25 Seats",
    ("2026-12-09", "19:00", "Milestone Satellite to $10,400 World Championship"): "25 Seats",
    ("2026-12-12", "14:00", "Milestone Satellite to $10,400 World Championship 1A/B"): "75 Seats",
    ("2026-12-12", "16:00", "Milestone Satellite to $10,400 Ladies"): "10 Seats",
    ("2026-12-12", "19:00", "Milestone Satellite to $10,400 World Championship 1A/B"): "25 Seats",
    ("2026-12-13", "12:00", "Milestone Satellite to $10,400 World Championship 1B"): "25 Seats",
    ("2026-12-13", "18:00", "Milestone Satellite to $10,400 World Championship 1B/C"): "25 Seats",
    ("2026-12-14", "12:00", "Milestone Satellite to $10,400 World Championship 1C"): "25 Seats",
    ("2026-12-14", "18:00", "Milestone Satellite to $10,400 World Championship 1C"): "25 Seats",
    ("2026-12-15", "11:00", "Milestone Satellite to $10,400 World Championship 1C/Day 2"): "10 Seats",
    ("2026-12-15", "18:00", "Milestone Satellite to $10,400 World Championship Day 2"): "10 Seats",
    # 2026-12-16 18:00 $25K High Roller satellite: the sign prints no guarantee cell.
    ("2026-12-16", "18:00", "Milestone Satellite to $3,000 NLH"): "25 Seats",
    ("2026-12-17", "14:00", "Milestone Satellite to $3,000 NLH"): "25 Seats",
    ("2026-12-17", "19:00", "Milestone Satellite to $3,000 NLH"): "25 Seats",
    ("2026-12-18", "10:00", "Milestone Satellite to $3,000 NLH"): "10 Seats",
    ("2026-12-18", "14:00", "Milestone Satellite to $5,000 Seniors"): "10 Seats",
    ("2026-12-19", "12:00", "Milestone Satellite to $1,600 Mystery Bounty"): "10 Seats",
    ("2026-12-19", "17:00", "Milestone Satellite to $1,600 Mystery Bounty"): "10 Seats",
}

DAY2_FIX = {
    ("2026-11-30", "13:00"): {
        "buyin": 600,
        "guarantee": 400000,
        "guarantee_note": (
            "The schedule sign prints $800 / $1,000,000 in this Day-2 row's money columns, but the "
            "$600 No Limit Hold'em $400,000 GTD terms page states 'Day 2: Monday, November 30, 2026 "
            "at 1 p.m.' - its own Day 2, with a $600 buy-in ($510 prize pool + $65 fee + $25 staff) "
            "and $400,000 guarantee. The sign's figures are the next event's ($800 / $1,000,000). "
            "Both readings are kept here and the row is not ranked (flag F58)."),
        "notes": (
            "Day 2 of the $600 No Limit Hold'em $400K GTD (terms page: Day 2 Mon Nov 30, 1 p.m.). "
            "Published buy-in and guarantee follow the event's terms page; the schedule sign's money "
            "columns disagree (flag F58)."),
    },
    ("2026-12-03", "13:00"): {
        "buyin": 800,
        "guarantee": 1000000,
        "guarantee_note": (
            "The schedule sign prints $1,600 / $1,000,000 in this Day-2 row's money columns, but the "
            "$800 No Limit Hold'em $1,000,000 GTD terms page states 'Day 2: Thursday, December 3, 2026 "
            "at 1 p.m.' - its own Day 2, with an $800 buy-in ($690 prize pool + $72 fee + $33 staff) "
            "and $1,000,000 guarantee. The sign's buy-in is the next event's ($1,600). Both readings "
            "are kept here and the row is not ranked (flag F58)."),
        "notes": (
            "Day 2 of the $800 No Limit Hold'em $1M GTD (terms page: Day 2 Thu Dec 3, 1 p.m.). "
            "Published buy-in and guarantee follow the event's terms page; the schedule sign's money "
            "columns disagree (flag F58)."),
    },
    ("2026-12-05", "11:00"): {
        "buyin": 1600,
        "guarantee": 1000000,
        "excerpt": ("Unlimited re-entry for each starting flight will be available until the start of "
                    "level 10. A player who advances to Day 2 is prohibited from entering a subsequent "
                    "starting flight."),
        "guarantee_note": (
            "The schedule sign prints $1,100 / $5,000,000 in this Day-2 row's money columns, but the "
            "$1,600 No Limit Hold'em $1,000,000 GTD terms page states 'Day 2: Saturday, December 5, 2026 "
            "at 11 a.m.' - its own Day 2, with a $1,600 buy-in ($1,430 prize pool + $120 fee + $50 "
            "staff) and $1,000,000 guarantee. The sign's figures ($1,100 / $5,000,000) are the WPT "
            "Prime Championship's, whose own Day 2 both official documents list separately on Dec 9. "
            "Both readings are kept here and the row is not ranked (flag F58)."),
        "notes": (
            "Day 2 of the $1,600 No Limit Hold'em $1M GTD (terms page: Day 2 Sat Dec 5, 11 a.m.). "
            "Published buy-in and guarantee follow the event's terms page; the schedule sign's money "
            "columns carry the WPT Prime Championship figures and its chips/levels columns follow the "
            "Prime's structure (40,000 / 40-60), while the $1,600 terms page describes Day 2 as "
            "40-minute levels to heads-up then 30 minutes (flag F58). The earlier capture had also "
            "quoted the Prime's 'One (1) Entry and One (1) re-entry' registration text on this row; "
            "the row now quotes the $1,600 event's own registration text."),
    },
}

SHEETS_REREAD = {
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_12.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_17.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_19.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_20.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_21.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_27.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_31.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_32.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_33.pdf",
    "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_37.pdf",
}

E39_BASIS = (
    "no re-entry, rebuy or add-on sentence appears anywhere in the sheet's 12 numbered rules; the "
    "event has one starting day (Dec 10) but continues on Dec 11 (Day 2) and a streamed final "
    "table, so S1 condition (4) - no flight or multi-day structure - is not met and the row is "
    "published as Cap not stated. The earlier capture had read the Day-2 continuation sentence "
    "('Day 2 will resume at 10:00 AM ...') as flight language and published Multi-entry; corrected "
    "2026-11-19 after a live re-read of sheet 32 (flag F56).")
E39_EVIDENCE_STD = (
    "S1 not satisfied (2026-11-19 re-read): sheet read + event named + registration close stated + "
    "no re-entry/rebuy/add-on/purchased-stack provision, but the sheet documents a two-day "
    "structure, so the row is published as Cap not stated, never as confirmed single-entry.")


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
        return json.load(fh)


def save(name, data):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
        fh.write("\n")


# ---------------------------------------------------------------- wpt.json
wpt = load("data/ea99006a/wpt.json")
filled, day2, turbo = 0, 0, 0
for r in wpt:
    r["last_checked"] = TODAY
    key = (r.get("date"), r.get("start"))
    if r.get("kind") == "satellite" and r.get("guarantee") in (None, ""):
        for (d, s, prefix), g in SAT_GUARANTEES.items():
            if (d, s) == key and r.get("name", "").startswith(prefix):
                r["guarantee"] = g
                filled += 1
                break
    fix = DAY2_FIX.get(key)
    if fix and r.get("name") == "No Limit Hold'em Day 2":
        r["buyin"] = fix["buyin"]
        r["guarantee"] = fix["guarantee"]
        r["guarantee_note"] = fix["guarantee_note"]
        r["notes"] = fix["notes"]
        if fix.get("excerpt"):
            r["rule_excerpt"] = fix["excerpt"]
        day2 += 1
    if key == ("2026-12-21", "20:00") and r.get("name") == "NLH Turbo":
        note = ("Start-time conflict between two official documents: the event terms page lists "
                "'Monday, December 21, 2026 at 6 p.m.' while the schedule sign lists 8 p.m. The "
                "published time follows the sign; flag F58.")
        r["notes"] = (r.get("notes") + " " if r.get("notes") else "") + note
        turbo += 1
save("data/ea99006a/wpt.json", wpt)
print("wpt.json: %d satellite guarantees filled, %d Day-2 rows corrected, %d turbo row noted"
      % (filled, day2, turbo))

# ---------------------------------------------------------------- venetian.json
ven = load("data/ea99006a/venetian.json")
e39, refreshed = 0, 0
for r in ven:
    if r.get("source") in SHEETS_REREAD:
        r["last_checked"] = TODAY
        refreshed += 1
    if r.get("event_no") == "39":
        r["entry_rule"] = "unknown"
        r["entry_basis"] = (E39_BASIS if r.get("kind") == "entry" else
                            "continuation row (Day 2 / streamed final table) of a single-flight "
                            "event; entry terms carry over from the Day 1 row - Cap not stated "
                            "(corrected 2026-11-19, flag F56)")
        ev = r.get("entry_evidence") or {}
        if ev:
            ev["flight_sentences"] = []
            ev["standard"] = E39_EVIDENCE_STD
        e39 += 1
save("data/ea99006a/venetian.json", ven)
print("venetian.json: %d event-39 rows re-labelled, %d rows refreshed" % (e39, refreshed))
