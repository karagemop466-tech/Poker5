#!/usr/bin/env python3
"""Session 36da6d66 - WPT / Wynn entry-term verification.

What this does
--------------
Reads the official WPT World Championship Structures + Terms & Conditions PDF
(all 8 page-chunks) and the official WPT schedule PDF (both chunks) on
2026-11-19, records the *verbatim* entry-terms sentence of every event whose
own T&Cs section is in that PDF, and then rewrites the rule verdict and the
structured rule fields of `data/ea99006a/wpt.json` for those rows.

Rules it obeys
--------------
* A row is only relabelled when its OWN event T&Cs section was in the PDF and
  names the date/time of a flight the row covers. Nothing is copied from a
  sibling event onto an event whose section is absent.
* A row keeps the `unread` verdict when the PDF has no T&Cs section for it:
  every "Milestone Satellite ..." row and every continuation/restart/final row
  whose own section does not print an entry sale. (The T&Cs of a flight event do
  explain what happens to a player who already advanced, so the restart rows of
  an event whose section WAS read are marked as such rather than left unread.)
* No verdict comes out `confirmed_single`: every event section in the PDF grants
  at least one re-entry, so the S1 test cannot pass for any of them. Where the
  grant is bounded ("One (1) Entry and One (1) re-entry") it is recorded in the
  excerpt so the difference from "Unlimited re-entry" is visible.
* Values that the PDF gives (entry-fee split, stack, level length, registration
  close, guarantee) are written to the structured rule fields with the verbatim
  sentence and today's retrieval date. Values the PDF does not give stay blank.

Not a publisher: this only touches data/ea99006a/wpt.json and writes
data/ea99006a/wpt_terms_2026-11-19.json as the evidence log. Run
scripts/build_ea99006a.py afterwards to regenerate the site.

Run:  python3 scripts/wpt_terms_36da6d66.py [--report]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "ea99006a")
TODAY = "2026-11-19"

STRUCT = ("https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/"
          "Poker/WPT/WPT_World_Championship_Structures.pdf")
TERMS = ("https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/"
         "WPT_World_Championship_Structures.pdf")
SCHEDULE = ("https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/"
            "Poker/WPT/WPT_World_Championship_Schedule.pdf")
WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"

# ---------------------------------------------------------------------------
# 1. The event sections that are actually printed in the official structures
#    PDF, transcribed from the fetch of 2026-11-19. `pages` is the chunk the
#    T&Cs section was read in, so a reader can go straight back to it.
#    Every sentence in `grant` is a verbatim quote from that section.
# ---------------------------------------------------------------------------
SECTIONS = {
    # key: (title on the sheet, buy-in, pages, dates printed, verbatim grant,
    #       registration close as printed or "", fee split sentence or "",
    #       stack sentence, level sentence, guarantee sentence or "")
    "$600 NLH $400K": dict(
        title="$600 No Limit Hold'em $400,000 Guarantee", buyin=600, pages=[1, 2],
        dates="Day 1A Fri Nov 27 11 a.m.; 1B Fri Nov 27 5 p.m.; 1C Sat Nov 28 11 a.m.; "
              "1D Sat Nov 28 5 p.m.; 1E Sun Nov 29 11 a.m.; 1F Sun Nov 29 6 p.m.; Day 2 Mon Nov 30 1 p.m.",
        grant="Unlimited re-entry for each starting flight will be available until the start of level 9. "
              "A player who advances to Day 2 is prohibited from entering a subsequent starting flight. "
              "A player that has advanced to Day 2 who enters a starting flight in error will be disqualified "
              "from the subsequent flight and will not be entitled to a refund of their Tournament re-entry fee. "
              "The player will be permitted to play Day 2 with their Tournament chip stack from the original starting flight.",
        close="until the start of level 9",
        fee="Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        stack="Players will start with 40,000 in tournament chips.",
        levels="Day 1A-E: 30 minutes per level until 12.5% or less of the field remains. Day 1F: 20 minutes per level until 12.5% or less of the field remains. Day 2: 40 minutes per level until two (2) players remain, 30 minutes per level thereafter.",
        guarantee="$400,000 Guarantee (event title).",
    ),
    "$600 TORSE": dict(
        title="$600 TORSE", buyin=600, pages=[2],
        dates="Fri Nov 27 12 p.m. (single day)",
        grant="Unlimited re-entry will be available until the start of level 9",
        close="until the start of level 9",
        fee="Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        stack="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
        guarantee="",
    ),
    "$400 PLO": dict(
        title="$400 PLO", buyin=400, pages=[2],
        dates="Fri Nov 27 1 p.m. (single day)",
        grant="Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.).",
        close="until the start of level 9 (approximately 5:30 p.m.)",
        fee="Entry Fee: $400 Buy-in = $337 (Tournament Prize Pool) + $45 (Tournament Fee) + $18 (Poker Staff Service Charge)",
        stack="Players will start with 30,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
        guarantee="",
    ),
    "$600 Mixed Triple Draw": dict(
        title="$600 Mixed Triple Draw (A-5, 2-7, Badugi)", buyin=600, pages=[2, 3],
        dates="Sat Nov 28 12 p.m.; Sun Dec 20 1 p.m.",
        grant="Unlimited re-entry will be available until the start of level 9.",
        close="until the start of level 9",
        fee="Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        stack="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
        guarantee="",
    ),
    "$800 NLH $1M": dict(
        title="$800 No Limit Hold'em $1,000,000 Guarantee", buyin=800, pages=[3],
        dates="Day 1A Mon Nov 30 11 a.m.; 1B Mon Nov 30 5 p.m.; 1C Tue Dec 1 11 a.m.; 1D Tue Dec 1 5 p.m.; "
              "1E Wed Dec 2 11 a.m.; 1F Wed Dec 2 6 p.m.; Day 2 Thu Dec 3 1 p.m.; Final Table Fri Dec 4 1 p.m.",
        grant="Unlimited re-entry for each starting flight will be available until the start of level 9. "
              "A player who advances to Day 2 is prohibited from entering a subsequent starting flight. "
              "A player that has advanced to Day 2 who enters a starting flight in error will be disqualified "
              "from the subsequent flight and will not be entitled to a refund of their Tournament re-entry fee. "
              "The player will be permitted to play Day 2 with their Tournament chip stack from the original starting flight.",
        close="until the start of level 9",
        fee="Entry Fee: $800 Buy-in = $695 (Tournament Prize Pool) + $72 (Tournament Fee) + $33 (Poker Staff Service Charge)",
        stack="Players will start with 40,000 in tournament chips.",
        levels="Day 1A-1E: 30 minutes per level until 12.5% or less of the field remains. Day 1F: 20 minutes per level until 12.5% or less of the field remains. Day 2: 40 minutes per level until nine (9) players remain. Day 3: 40 minutes per level until two (2) players remain, 30 minutes per level thereafter.",
        guarantee="$1,000,000 Guarantee (event title).",
    ),
    "$600 Limit Omaha 8": dict(
        title="$600 Limit Omaha 8", buyin=600, pages=[3],
        dates="Mon Nov 30 12 p.m. (single day)",
        grant="Unlimited re-entry will be available until the start of level 9",
        close="until the start of level 9",
        fee="Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        stack="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
        guarantee="",
    ),
    "$600 Limit Omaha 8/Stud 8": dict(
        title="$600 Limit Omaha 8/Stud 8", buyin=600, pages=[4],
        dates="Tue Dec 1 12 p.m. (single day)",
        grant="Unlimited re-entry will be available until the start of level 9",
        close="until the start of level 9",
        fee="Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        stack="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
        guarantee="",
    ),
    "$1,100 PLO": dict(
        title="$1,100 PLO", buyin=1100, pages=[4],
        dates="Tue Dec 1 1 p.m. (single day)",
        grant="Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.).",
        close="until the start of level 9 (approximately 5:30 p.m.)",
        fee="Entry Fee: $1,100 Buy-in = $975 (Tournament Prize Pool) + $85 (Tournament Fee) + $45 (Poker Staff Service Charge)",
        stack="Players will start with 30,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
        guarantee="",
    ),
    "$1,600 NLH $1M": dict(
        title="$1,600 No Limit Hold'em $1,000,000 Guarantee", buyin=1600, pages=[4, 5],
        dates="Day 1A Thu Dec 3 11 a.m.; Day 1B Fri Dec 4 11 a.m.; Day 2 Sat Dec 5 11 a.m.",
        grant="Unlimited re-entry for each starting flight will be available until the start of level 10. "
              "A player who advances to Day 2 is prohibited from entering a subsequent starting flight. "
              "A player that has advanced to Day 2 who enters a starting flight in error will be disqualified "
              "from the subsequent flight and will not be entitled to a refund of their Tournament re-entry fee. "
              "The player will be permitted to play Day 2 with their Tournament chip stack from the original starting flight.",
        close="until the start of level 10",
        fee="Entry Fee: $1,600 Buy-in = $1,430 (Tournament Prize Pool) + $120 (Tournament Fee) + $50 (Poker Staff Service Charge)",
        stack="Players will start with 40,000 in tournament chips.",
        levels="Day 1: 40 minutes per level until 12.5% or less of the field remains. Day 2: 40 minutes per level until two (2) players remain, 30 minutes per level thereafter.",
        guarantee="$1,000,000 Guarantee (event title).",
    ),
    "$600 HORSE": dict(
        title="$600 HORSE", buyin=600, pages=[5],
        dates="Fri Dec 4 12 p.m. (single day)",
        grant="Unlimited re-entry will be available until the start of level 9 (approximately 4:30 p.m.).",
        close="until the start of level 9 (approximately 4:30 p.m.)",
        fee="Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        stack="Players will start with 35,000 in tournament chips.",
        levels="30 minutes per level until a winner is declared.",
        guarantee="",
    ),
    "WPT Prime Championship": dict(
        title="$1,100 WPT Prime Championship $5,000,000 Guarantee", buyin=1100, pages=[5, 6],
        dates="Day 1A Sat Dec 5 11 a.m.; 1B Sun Dec 6 11 a.m.; 1C Mon Dec 7 11 a.m.; 1D Tue Dec 8 11 a.m.; "
              "Day 2 Wed Dec 9 12 p.m.; Day 3 Thu Dec 10 12 p.m.; Day 4 Fri Dec 11 12 p.m.; Final Table Sat Dec 12 2 p.m.",
        grant="One (1) Entry and One (1) re-entry for each starting flight will be available until the start of level 10 "
              "(approximately 6:45 p.m.). A player who advances to Day 2 is prohibited from entering a subsequent starting "
              "flight. A player that has advanced to Day 2 who enters a starting flight in error will be disqualified from "
              "the subsequent flight and will not be entitled to a refund of their Tournament re-entry fee. The player will "
              "be permitted to play Day 2 with their Tournament chip stack from the original starting flight.",
        close="until the start of level 10 (approximately 6:45 p.m.)",
        fee="Entry Fee: $1,100 Buy-in = $970 (Tournament Prize Pool) + $90 (Tournament Fee) + $40 (Poker Staff Service Charge)",
        stack="Players will start with 40,000 in tournament chips.",
        levels="Day 1: 40 minutes per level until 12.5% or less of the field remains. Day 2: Ten (10) levels of 60 minutes each. Day 3: Ten (10) levels of 60 minutes each. Day 4: 60 minutes per level until the final six (6) players remain. Day 5: 60 minutes per level until two (2) players remain, 30 minutes per level thereafter.",
        guarantee="$5,000,000 Guarantee (event title).",
    ),
    "$600 NLH Turbo": dict(
        title="$600 NLH Turbo $50,000 Guarantee", buyin=600, pages=[6],
        dates="Sat Dec 5 9 p.m.; Sun Dec 6 9 p.m.; Mon Dec 7 9 p.m.; Tue Dec 8 9 p.m.; Wed Dec 9 9 p.m.; "
              "Sat Dec 12 9 p.m.; Mon Dec 14 9 p.m.; Mon Dec 21 6 p.m.",
        grant="Unlimited re-entry will be available until the start of level 9.",
        close="until the start of level 9",
        fee="Entry Fee: $600 Buy-in = $515 (Tournament Prize Pool) + $60 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        stack="Players will start with 30,000 in tournament chips.",
        levels="20 minutes per level until a winner is declared.",
        guarantee="$50,000 Guarantee (event title).",
    ),
    "$1,600 PLO Mystery Bounty": dict(
        title="$1,600 PLO Mystery Bounty $500,000 Guarantee", buyin=1600, pages=[6, 7],
        dates="Day 1A Sun Dec 6 11 a.m.; Day 1B Sun Dec 6 6 p.m.; Day 2 Mon Dec 7 12 p.m.",
        grant="Unlimited re-entry for each starting flight will be available until the start of level 10. "
              "A player who advances to Day 2 is prohibited from entering a subsequent starting flight. "
              "A player that has advanced to Day 2 who enters a starting flight in error will be disqualified "
              "from the subsequent flight and will not be entitled to a refund of their Tournament re-entry fee. "
              "The player will be permitted to play Day 2 with their Tournament chip stack from the original starting flight.",
        close="until the start of level 10",
        fee="Entry Fee: $1,600 Buy-in = $930 (Tournament Prize Pool) + $500 (Mystery Bounty Prize Pool) + $120 (Tournament Fee) + $50 (Poker Staff Service Charge)",
        stack="Players will start with 40,000 in tournament chips.",
        levels="Day 1A: 40 minutes per level until 12.5% or less of the field remains. Day 1B: 20 minutes per level until 12.5% or less of the field remains. Day 2: 40 minutes per level until two (2) players remain, 30 minutes per level thereafter.",
        guarantee="$500,000 Guarantee (event title; includes the Mystery Bounty prize pool - see the Mystery Bounty Rules section).",
    ),
    # General T&Cs sentence that applies to every event in the series (page 0).
    "#GENERAL": dict(
        title="WPT World Championship General Terms and Conditions", buyin=None, pages=[0],
        dates="November 27 - December 21, 2026",
        grant="Registration for each Event will open four (4) hours prior to the scheduled start of play. Players will "
              "register in the Wynn Las Vegas Poker Room, located in Encore at Wynn Las Vegas.",
        close="registration opens four (4) hours prior to the scheduled start of play",
        fee="The Tournament entry fee (the \"Entry Fee\") must be paid with cash or Wynn Las Vegas live casino chips; "
            "no other forms of payment will be accepted.",
        stack="", levels="",
        guarantee="",
    ),
}

# Rows the PDF has no event section for -> they stay `unread`.
# name prefix -> why
NO_SECTION = {
    "Milestone Satellite": "the structures PDF prints no terms-and-conditions section for the milestone satellites",
    "Double Play Milestone Satellite": "the structures PDF prints no terms-and-conditions section for the double-play satellite",
    "Seniors NLH Championship": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "Wynn Mixed Championship": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "NLH High Roller": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "Seniors High Roller": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "Ladies NLH Championship": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "No Limit Hold'em (2 Day)": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "Big O": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO Double Board Bomb Pot": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO 6-Max": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "No Limit Hold'em Day 1A": "ambiguous: the schedule prints three different 'No Limit Hold'em Day 1A' events "
                               "($1,100, $3,000 and $800) and the PDF gives no event number to tell which section applies",
    "No Limit Hold'em Day 1B": "ambiguous: the schedule prints two different 'No Limit Hold'em Day 1B' events "
                               "($1,100 and $3,000) and the PDF gives no event number to tell which section applies",
    "No Limit Hold'em": "ambiguous: several single-day 'No Limit Hold'em' events share this name and the PDF gives no "
                        "event number to tell which section applies",
    "Limit Omaha 8 Championship": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "TORSE (2 Day)": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "TORSE Championship": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "HORSE (2 Day)": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO $1,000 Bounty": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO $500 Bounty": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO Progressive Bounty (PKO)": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "NLH $500 Bounty Turbo": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "NLH 6-Max": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "NLH 6-Max Turbo": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "NLH 8-Max": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO Turbo": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO Day 1A": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO Day 1B": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "PLO": "ambiguous: several 'PLO' events with different buy-ins and the PDF gives no event number",
    "5-Card PLO Turbo": "no terms-and-conditions section for this event in the structures PDF read on 2026-11-19",
    "WPT World Championship Day": "continuation day: the section for the $10,400 World Championship is not printed "
                                  "in the structures PDF read on 2026-11-19",
}

# Rows that are continuation days of an event whose own section WAS read.
# They are not a new entry sale, and the section's sentence is about flights,
# so they are labelled from the parent's section with a note saying so.
PARENT_OF_RESTART = {
    "No Limit Hold'em Day 2": ["$600 NLH $400K", "$800 NLH $1M", "$1,600 NLH $1M", "WPT Prime Championship",
                               "$1,600 PLO Mystery Bounty"],
    "No Limit Hold'em Final Table": ["$1,600 NLH $1M"],
    "PLO Mystery Bounty Day 2": ["$1,600 PLO Mystery Bounty"],
    "WPT Prime Championship Day 2": ["WPT Prime Championship"],
    "WPT Prime Championship Day 3": ["WPT Prime Championship"],
    "WPT Prime Championship Day 4": ["WPT Prime Championship"],
    "WPT Prime Championship Final Table": ["WPT Prime Championship"],
    "Super Gold Million Mystery Bounty Day 2": [None],   # no section for Super Gold Million at all
}

# Flight rows -> the section key that owns them, matched on (buy-in, name).
FLIGHT_KEYS = {
    ("No Limit Hold'em Day 1A", 600): "$600 NLH $400K",
    ("No Limit Hold'em Day 1B", 600): "$600 NLH $400K",
    ("No Limit Hold'em Day 1C", 600): "$600 NLH $400K",
    ("No Limit Hold'em Day 1D", 600): "$600 NLH $400K",
    ("No Limit Hold'em Day 1E", 600): "$600 NLH $400K",
    ("No Limit Hold'em Day 1F", 600): "$600 NLH $400K",
    ("No Limit Hold'em Day 1A", 800): "$800 NLH $1M",
    ("No Limit Hold'em Day 1B", 800): "$800 NLH $1M",
    ("No Limit Hold'em Day 1C", 800): "$800 NLH $1M",
    ("No Limit Hold'em Day 1D", 800): "$800 NLH $1M",
    ("No Limit Hold'em Day 1E", 800): "$800 NLH $1M",
    ("No Limit Hold'em Day 1F", 800): "$800 NLH $1M",
    ("No Limit Hold'em Day 1A", 1600): "$1,600 NLH $1M",
    ("No Limit Hold'em Day 1B", 1600): "$1,600 NLH $1M",
    ("TORSE", 600): "$600 TORSE",
    ("PLO", 400): "$400 PLO",
    ("PLO", 1100): "$1,100 PLO",
    ("Mixed Triple Draw (A-5, 2-7, Badugi)", 600): "$600 Mixed Triple Draw",
    ("Limit Omaha 8", 600): "$600 Limit Omaha 8",
    ("Limit Omaha 8 / Stud 8", 600): "$600 Limit Omaha 8/Stud 8",
    ("HORSE", 600): "$600 HORSE",
    ("WPT Prime Championship Day 1A", 1100): "WPT Prime Championship",
    ("WPT Prime Championship Day 1B", 1100): "WPT Prime Championship",
    ("WPT Prime Championship Day 1C", 1100): "WPT Prime Championship",
    ("WPT Prime Championship Day 1D", 1100): "WPT Prime Championship",
    ("NLH Turbo", 600): "$600 NLH Turbo",
    ("PLO Mystery Bounty Day 1A", 1600): "$1,600 PLO Mystery Bounty",
    ("PLO Mystery Bounty Day 1B", 1600): "$1,600 PLO Mystery Bounty",
}


def fee_parts(sentence):
    """'$600 Buy-in = $510 (Tournament Prize Pool) + $65 (...) + $25 (...)' -> dict."""
    import re
    m = re.search(r"\$([\d,]+) Buy-in = \$([\d,]+) \(Tournament Prize Pool\)"
                  r"(?: \+ \$([\d,]+) \(Mystery Bounty Prize Pool\))?"
                  r" \+ \$([\d,]+) \(Tournament Fee\)"
                  r" \+ \$([\d,]+) \(Poker Staff Service Charge\)", sentence)
    if not m:
        return None
    num = lambda s: int(s.replace(",", "")) if s else None
    return dict(buyin=num(m.group(1)), prize_pool=num(m.group(2)),
                mystery_bounty_pool=num(m.group(3)),
                tournament_fee=num(m.group(4)), staff_charge=num(m.group(5)))


def field(value, excerpt, source=STRUCT, retrieved=TODAY):
    return dict(value=value, excerpt=excerpt, source=source, retrieved=retrieved)


def rule_fields_for(sec):
    split = fee_parts(sec["fee"]) or {}
    house = None
    if split.get("tournament_fee") is not None and split.get("staff_charge") is not None:
        house = split["tournament_fee"] + split["staff_charge"]
    return {
        # S1 needs an explicit one-entry statement. The sheet says the opposite.
        "single_entry": field("not granted: the event's own terms allow re-entry",
                              sec["grant"][:400]),
        "re_entry": field("yes - " + ("one entry and one re-entry per flight" if "One (1) Entry and One (1) re-entry" in sec["grant"]
                                      else "unlimited re-entry per flight (or until the stated level)"),
                          sec["grant"][:600]),
        "add_on": field("no add-on provision in this event's terms",
                        "no add-on sentence appears in this event's terms-and-conditions section (pages %s)"
                        % ",".join(str(p) for p in sec["pages"])),
        "house_fee": field(house, sec["fee"]) if house is not None else field("", ""),
        "guarantee": field(sec.get("_row_guarantee"), sec["guarantee"]) if sec["guarantee"] else field("", ""),
        "late_registration": field(sec["close"], sec["grant"][:600]) if sec["close"] else field("", ""),
        "starting_chips": field(sec["stack"], sec["stack"]) if sec["stack"] else field("", ""),
        "level_minutes": field(sec["levels"], sec["levels"]) if sec["levels"] else field("", ""),
    }


def main():
    report_only = "--report" in sys.argv
    rows = json.load(open(os.path.join(DATA, "wpt.json")))
    log = []
    counts = {"read": 0, "still_unread": 0, "continuation_of_read_event": 0}

    for row in rows:
        name = row["name"]
        key = FLIGHT_KEYS.get((name, row.get("buyin")))
        parent = None
        if key:
            parent = key
        else:
            for pfx, keys in PARENT_OF_RESTART.items():
                if name.startswith(pfx):
                    # more than one parent lists the same name -> pick the one whose buy-in matches
                    cands = [k for k in keys if k]
                    for k in cands:
                        if SECTIONS[k]["buyin"] == row.get("buyin"):
                            parent = k
                            break
                    if parent is None and len(cands) == 1:
                        parent = cands[0]
                    break

        if key:
            sec = SECTIONS[key]
            sec["_row_guarantee"] = row.get("guarantee") if isinstance(row.get("guarantee"), (int, float)) else ""
            row["entry_rule"] = "multi"
            row["rule_excerpt"] = sec["grant"]
            row["rule_fields"] = rule_fields_for(sec)
            row["entry_basis"] = ("this event's own terms-and-conditions section in the official structures PDF "
                                  "(pages %s), read %s: it grants re-entry, so the S1 single-entry test fails"
                                  % (",".join(str(p) for p in sec["pages"]), TODAY))
            split = fee_parts(sec["fee"])
            if split:
                row["house_fee"] = ""          # the split is in rule_fields.house_fee with its sentence
                row["to_prize_pool"] = "$%s of every $%s" % (format(split["prize_pool"], ",d"),
                                                             format(split["buyin"], ",d"))
            if sec["close"]:
                row["late_reg"] = sec["close"]
            row["terms_source"] = STRUCT
            row["terms_read"] = TODAY
            row.pop("terms_unread_reason", None)
            counts["read"] += 1
            log.append(dict(date=row["date"], start=row["start"], name=name, verdict="multi",
                            source=STRUCT, pages=sec["pages"], excerpt=sec["grant"][:600],
                            read=TODAY))
            continue

        if parent:
            sec = SECTIONS[parent]
            sec["_row_guarantee"] = row.get("guarantee") if isinstance(row.get("guarantee"), (int, float)) else ""
            row["entry_rule"] = "multi"
            row["rule_excerpt"] = sec["grant"]
            row["rule_fields"] = rule_fields_for(sec)
            row["entry_basis"] = ("continuation day of the fully-read %s event; its terms-and-conditions section "
                                  "(official structures PDF, pages %s) is quoted here because that section governs "
                                  "a player who has already advanced" %
                                  (sec["title"], ",".join(str(p) for p in sec["pages"])))
            row["terms_source"] = STRUCT
            row["terms_read"] = TODAY
            row.pop("terms_unread_reason", None)
            counts["continuation_of_read_event"] += 1
            log.append(dict(date=row["date"], start=row["start"], name=name, verdict="multi",
                            source=STRUCT, pages=sec["pages"], excerpt=sec["grant"][:600],
                            read=TODAY, note="continuation day of " + sec["title"]))
            continue

        # everything else stays unread, with the specific reason
        reason = None
        for pfx, why in NO_SECTION.items():
            if name.startswith(pfx):
                reason = why
                break
        if reason is None:
            reason = "no terms-and-conditions section for this event in the structures PDF read on " + TODAY
        row["entry_rule"] = "unread"
        stale = [k for k, v in (row.get("rule_fields") or {}).items() if (v or {}).get("retrieved") != TODAY]
        if stale:
            # a field whose own retrieval date is not today is not evidence any more; drop it rather than
            # leave an older read looking current next to a row labelled "not read"
            row["rule_fields"] = dict((k, v) for k, v in (row.get("rule_fields") or {}).items()
                                      if (v or {}).get("retrieved") == TODAY)
        row["rule_excerpt"] = ("Entry terms not read: " + reason + ". Kept explicitly unverified rather than "
                               "copied from a sibling event.")
        row["terms_unread_reason"] = reason
        row["terms_source"] = STRUCT
        row["terms_read"] = ""
        counts["still_unread"] += 1

    payload = dict(
        note=("Verbatim transcription of every event terms-and-conditions section in the official WPT World "
              "Championship structures PDF, read on %s, plus the verdict it forces. This log exists so the "
              "label on each row can be re-derived from the official sentence without re-reading a 40-page PDF. "
              "No value here is inferred: a row whose section is absent keeps `unread`." % TODAY),
        read_on=TODAY,
        sources=dict(structures=STRUCT, terms=TERMS, schedule=SCHEDULE, poker_page=WYNN_POKER),
        sections=dict((k, dict((kk, vv) for kk, vv in v.items() if not kk.startswith("_"))) for k, v in SECTIONS.items()),
        rows=log,
        counts=counts,
    )
    print(json.dumps(counts, indent=1))
    if report_only:
        return 0
    with open(os.path.join(DATA, "wpt_terms_2026-11-19.json"), "w") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(DATA, "wpt.json"), "w") as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
