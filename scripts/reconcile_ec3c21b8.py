#!/usr/bin/env python3
"""Session ec3c21b8 - reconciler: re-apply this session's unique deltas on the merged tree.

After merging origin/main (sessions 98087225, 36da6d66, 2723deea, 8f0b323b, 22f06ff9,
1efddebe, 0a0d8e6b and others landed in parallel), main's data supersedes this branch
where the same facts were already published. Only the deltas that remain unique are
applied here, every one of them traceable to a source read in this session and each
carrying its flag (F70-F72; the Day-2 and Turbo conflicts are already flagged on main
as F58/F59/F61 and are referenced, not duplicated).

Run  python3 scripts/recheck_ec3c21b8.py  afterwards: the sign TSV and the 10-sheet
transcripts must then match the stored rows, with the three Day-2 rows reported as
documented official-source conflicts (F58).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-19"

SIGN_URL = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
TERMS_URL = "https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf"
TERMS_CDN = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"

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
    ("2026-12-12", "14:00", "Milestone Satellite to $10,400 World Championship 1A"): "75 Seats",
    ("2026-12-12", "16:00", "Milestone Satellite to $10,400 Ladies"): "10 Seats",
    ("2026-12-12", "19:00", "Milestone Satellite to $10,400 World Championship 1A"): "25 Seats",
    ("2026-12-13", "12:00", "Milestone Satellite to $10,400 World Championship 1B"): "25 Seats",
    ("2026-12-13", "18:00", "Milestone Satellite to $10,400 World Championship 1B"): "25 Seats",
    ("2026-12-14", "12:00", "Milestone Satellite to $10,400 World Championship 1C"): "25 Seats",
    ("2026-12-14", "18:00", "Milestone Satellite to $10,400 World Championship 1C"): "25 Seats",
    ("2026-12-15", "11:00", "Milestone Satellite to $10,400 World Championship 1C"): "10 Seats",
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

# The three "No Limit Hold'em Day 2" rows. The schedule sign prints the NEXT event's
# money columns; the event terms pages state these exact slots as the $600/$800/$1,600
# events' own Day 2 (flag F58 on main keeps the disagreement). Rows publish the
# terms-page figures and keep both readings in guarantee_note.
DAY2_FIX = {
    ("2026-11-30", "13:00"): {
        "buyin": 600,
        "guarantee": 400000,
        "guarantee_note": (
            "The schedule sign prints $800 / $1,000,000 in this Day-2 row's money columns, but the "
            "$600 No Limit Hold'em $400,000 GTD terms section states 'Day 2: Monday, November 30, 2026 "
            "at 1 p.m.' - its own Day 2, with a $600 buy-in ($510 prize pool + $65 fee + $25 staff) "
            "and $400,000 guarantee. The sign's figures are the next event's ($800 / $1,000,000). "
            "Both readings are kept here and the row is not ranked (flag F58)."),
        "notes": (
            "Day 2 of the $600 No Limit Hold'em $400K GTD (terms section: Day 2 Mon Nov 30, 1 p.m.). "
            "Published buy-in and guarantee follow the event's terms section; the schedule sign's money "
            "columns disagree (flag F58)."),
    },
    ("2026-12-03", "13:00"): {
        "buyin": 800,
        "guarantee": 1000000,
        "entry_rule": "multi",
        "rule_excerpt": ("Unlimited re-entry for each starting flight will be available until the start "
                         "of level 9. A player who advances to Day 2 is prohibited from entering a "
                         "subsequent starting flight."),
        "entry_basis": (
            "bound to the $800 No Limit Hold'em $1M GTD terms section by its own words 'Day 2: "
            "Thursday, December 3, 2026 at 1 p.m.' (the schedule line is that Day 2; the name alone "
            "would be ambiguous, the stated Day-2 date and time are not); the section grants unlimited "
            "re-entry per starting flight until the start of level 9, read 2026-11-19"),
        "terms_read": "2026-11-19",
        "terms_source": TERMS_CDN,
        "guarantee_note": (
            "The schedule sign prints $1,600 / $1,000,000 in this Day-2 row's money columns, but the "
            "$800 No Limit Hold'em $1,000,000 GTD terms section states 'Day 2: Thursday, December 3, 2026 "
            "at 1 p.m.' - its own Day 2, with an $800 buy-in ($690 prize pool + $72 fee + $33 staff) "
            "and $1,000,000 guarantee. The sign's buy-in is the next event's ($1,600). Both readings "
            "are kept here and the row is not ranked (flag F58)."),
        "notes": (
            "Day 2 of the $800 No Limit Hold'em $1M GTD (terms section: Day 2 Thu Dec 3, 1 p.m.). "
            "Published buy-in and guarantee follow the event's terms section; the schedule sign's money "
            "columns disagree (flag F58)."),
    },
    ("2026-12-05", "11:00"): {
        "buyin": 1600,
        "guarantee": 1000000,
        "rule_excerpt": ("Unlimited re-entry for each starting flight will be available until the start "
                         "of level 10. A player who advances to Day 2 is prohibited from entering a "
                         "subsequent starting flight."),
        "guarantee_note": (
            "The schedule sign prints $1,100 / $5,000,000 in this Day-2 row's money columns, but the "
            "$1,600 No Limit Hold'em $1,000,000 GTD terms section states 'Day 2: Saturday, December 5, 2026 "
            "at 11 a.m.' - its own Day 2, with a $1,600 buy-in ($1,430 prize pool + $120 fee + $50 "
            "staff) and $1,000,000 guarantee. The sign's figures ($1,100 / $5,000,000) are the WPT "
            "Prime Championship's, whose own Day 2 both official documents list separately on Dec 9. "
            "Both readings are kept here and the row is not ranked (flag F58)."),
        "notes": (
            "Day 2 of the $1,600 No Limit Hold'em $1M GTD (terms section: Day 2 Sat Dec 5, 11 a.m.). "
            "Published buy-in and guarantee follow the event's terms section; the schedule sign's money "
            "columns carry the WPT Prime Championship figures and its chips/levels columns follow the "
            "Prime's structure (40,000 / 40-60), while the $1,600 terms section describes Day 2 as "
            "40-minute levels to heads-up then 30 minutes (flag F58). The earlier capture had also "
            "quoted the Prime's 'One (1) Entry and One (1) re-entry' registration text on this row; "
            "the row now quotes the $1,600 event's own registration text."),
    },
}


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
        return json.load(fh)


def save(name, data):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
        fh.write("\n")


# ---------------------------------------------------------------- wpt.json
wpt = load("data/ea99006a/wpt.json")
filled = day2 = turbo = 0
for r in wpt:
    r["last_checked"] = TODAY
    key = (r.get("date"), r.get("start"))
    nm = (r.get("name") or "").lower()
    if r.get("kind") == "satellite" and r.get("guarantee") in (None, ""):
        for (d, s, prefix), g in SAT_GUARANTEES.items():
            if (d, s) == key and nm.startswith(prefix.lower()):
                r["guarantee"] = g
                filled += 1
                break
    fix = DAY2_FIX.get(key)
    if fix and r.get("name") == "No Limit Hold'em Day 2":
        r["buyin"] = fix["buyin"]
        r["guarantee"] = fix["guarantee"]
        r["guarantee_note"] = fix["guarantee_note"]
        r["notes"] = fix["notes"]
        if fix.get("rule_excerpt"):
            r["rule_excerpt"] = fix["rule_excerpt"]
        if fix.get("entry_rule"):
            r["entry_rule"] = fix["entry_rule"]
        if fix.get("entry_basis"):
            r["entry_basis"] = fix["entry_basis"]
        if fix.get("terms_read"):
            r["terms_read"] = fix["terms_read"]
        if fix.get("terms_source"):
            r["terms_source"] = fix["terms_source"]
        day2 += 1
    if key == ("2026-12-21", "20:00") and r.get("name") == "NLH Turbo":
        note = ("Start-time conflict between two official documents: the terms section lists "
                "'Monday, December 21, 2026 at 6 p.m.' while the schedule sign lists 8 p.m. The "
                "published time follows the sign; flag F59.")
        if "flag F59" not in (r.get("notes") or ""):
            r["notes"] = (r.get("notes") + " " if r.get("notes") else "") + note
        turbo += 1
save("data/ea99006a/wpt.json", wpt)
print("wpt.json: %d satellite guarantees filled, %d Day-2 rows corrected, %d turbo row noted"
      % (filled, day2, turbo))

# ---------------------------------------------------------------- venetian.json
ven = load("data/ea99006a/venetian.json")
fixed = 0
for r in ven:
    if r.get("event_no") == "39":
        ev = r.get("entry_evidence") or {}
        for holder in (r, ev):
            for k in ("entry_basis", "standard"):
                if isinstance(holder.get(k), str) and "(flag F71)" in holder[k]:
                    holder[k] = holder[k].replace("(flag F71)", "(flag F71)")
                    fixed += 1
save("data/ea99006a/venetian.json", ven)
print("venetian.json: %d flag references renumbered (F56 -> F71)" % fixed)

# ---------------------------------------------------------------- registers
def next_id(items, prefix):
    n = 0
    for x in items:
        try:
            n = max(n, int(x["id"][1:]))
        except (ValueError, KeyError, TypeError):
            pass
    return "%s%02d" % (prefix, n + 1)


def append_unique(path, prefix, new_items, title_key="title"):
    items = load(path)
    titles = {x.get(title_key, "") for x in items}
    for it in new_items:
        if it[title_key] in titles:
            print("  skip duplicate:", it[title_key][:60])
            continue
        it["id"] = next_id(items, prefix)
        items.append(it)
        titles.add(it[title_key])
        print("  added", it["id"], "|", it[title_key][:70])
    save(path, items)


append_unique("data/ea99006a/flags.json", "F", [
    {
        "area": "Entry rules",
        "title": "Venetian #39 (LIPS Ladies $800, 2Day) was published multi-entry on a Day-2 continuation sentence; corrected to Cap not stated",
        "detail": "Structure sheet 32 was re-read live on 2026-11-19 (12 numbered rules). No rule grants a re-entry, rebuy, add-on or purchased stack, and the event has no starting flights (one Day 1, Dec 10, with Day 2 Dec 11 and a streamed final table). The earlier capture had quoted the sentence 'Day 2 will resume at 10:00 AM ...' as flight language and published the three rows (Day 1, Day 2 restart, final table) as 'Multi-entry: re-entry, add-on or flights' while their own excerpt said the opposite. The rows now read 'Cap not stated': S1 condition (4) (no flight or multi-day structure) is not met, so the event cannot join the no-second-entry set, and no text grants a second entry. Review the wording of S1 condition (4) if single-flight multi-day events should qualify.",
        "source": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_32.pdf",
        "status": "open",
        "last_updated": TODAY,
    },
    {
        "area": "Tournament data",
        "title": "24 WPT satellite seat/prize guarantees were blank although the official schedule sign states them; filled from the sign",
        "detail": "The Wynn WPT schedule sign prints a seats/prizes guarantee for every milestone satellite (for example '25 Seats', '50 Seats', '75 Seats', '10 Seats', '25 Prizes'). The earlier capture stored only money guarantees, leaving 24 satellite rows blank. Re-read live on 2026-11-19 and filled verbatim from the sign (data/ec3c21b8/wpt_sign_2026-11-19.tsv). The Milestone Satellite to the $25K NLH High Roller (Dec 16) has no guarantee cell on the sign and stays blank. Seat and prize counts are shown as seats, not cash, and are never divided by a buy-in in the ranking.",
        "source": SIGN_URL,
        "status": "open",
        "last_updated": TODAY,
    },
    {
        "area": "Official sources disagree",
        "title": "Wynn sign footnote: 'The Tournament Entry for the Ladies Championship is $11,100' while its own table lists $1,100",
        "detail": "The schedule sign's footnote reads 'The Tournament Entry for the Ladies Championship is $11,100. Ladies will receive a discounted entry.' while the same sign's table lists the Ladies NLH Championship (2 Day, Dec 13) at $1,100 with a $250,000 guarantee, and the stored row uses $1,100. The $11,100 figure appears inconsistent (an extra digit, or $1,110 with the discounted entry) and is not used anywhere. Confirm with the room before relying on either figure.",
        "source": SIGN_URL,
        "status": "open",
        "last_updated": TODAY,
    },
])

append_unique("data/ea99006a/questions.json", "Q", [
    {
        "q": "What are the entry terms (re-entry / re-buy / add-on caps) of the WPT events whose schedule lines still carry 'Entry terms not read - unverified', and of the eight South Point daily tournaments?",
        "have": "Those rows are verified on schedule fields (date, start, buy-in, guarantee, chips, level length) from the official Wynn schedule sign and the South Point poker-room page, re-read 2026-11-19. 48 WPT rows now hold their event terms section's verbatim entry text (read 2026-11-19 by sessions ec3c21b8, 98087225 and 36da6d66), which shows every one of those events grants re-entry. The remaining terms exist only in sources not machine-readable here: the WPT structures document's later pages (this environment extracts text up to page 30) and the per-event sheets the schedule footnotes call 'See structure sheet' (not found published on the Wynn poker page), plus South Point's rules-sheet JPG images.",
        "missing": "The entry terms for the remaining WPT rows and the eight South Point rows. Until they are read, those rows carry 'Entry terms not read - unverified' and cannot enter any single-entry comparison, and no label is removed on their behalf.",
        "how": "Ask the Wynn poker room for the per-event structure sheets the schedule footnotes reference, and South Point for its rules sheets in text form; or read the full structures PDF past page 30 and the JPG rules sheets manually and record each Registration sentence with its URL and retrieval date. Treat every one of those rows as cap unknown until then.",
    },
], title_key="q")

append_unique("data/ea99006a/suggestions.json", "S", [
    {
        "title": "Close the remaining unverified rows: human-readable entry-terms capture",
        "problem": "The rows that still carry an unverified label do so only because their official entry terms are not machine-readable in the build environment: the WPT structures PDF truncates at page 30 of extracted text, the per-event sheets its footnotes reference were not found published online, and South Point publishes its rules as JPG images.",
        "options": [
            "A human reads the remaining WPT event terms and South Point rules sheets and pastes each entry sentence into data/ with its URL and retrieval date (fastest, no code)",
            "Ask each room in writing for the entry cap per event (also resolves the F01 standard question)",
            "Add OCR to the capture pipeline for the South Point JPG rules sheets",
            "Leave the rows unverified and keep them out of every plan (current state, honest but incomplete)"
        ],
        "effect": "Each closed row loses its unverified label and joins either the no-second-entry set or the multi-entry section, with the official sentence stored on the row.",
    },
])
print("registers updated")
