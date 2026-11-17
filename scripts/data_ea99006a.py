#!/usr/bin/env python3
"""Session ea99006a - source data writer.

Every value below was read from an official source during this session
(retrieval date 2026-11-17).  Nothing is inferred: where an official source is
silent the field is left empty and a flag row is emitted instead.

Run:  python3 scripts/data_ea99006a.py
Writes data/ea99006a/*.json
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ea99006a")
RETRIEVED = "2026-11-17"

BASE = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures"
SHEET = BASE + "/dse_nov_2026-structure_{}.pdf"
SCHEDULE_PAGE = ("https://www.venetianlasvegas.com/resort/casino/poker/"
                 "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")

# --------------------------------------------------------------------------
# 1. Venetian DeepStack Extravaganza IV - structure sheets (all 37 read)
# --------------------------------------------------------------------------
# rule: confirmed_single | multi | unknown
SHEETS = {
    1: dict(events="09, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64", title="$200 No Limit Hold'em Bounty (1Day)",
            buyin=200, fee="$40", pool="$160 of every $200", gtd="8,000", chips="25,000", level="30 min",
            late="8 levels + Break (9:40 PM)", start="5:10 PM", rule="unknown",
            excerpt="No re-entry, rebuy or add-on text appears on the sheet. $50 bounty per elimination.",
            notes="Bounty: prize pool + bounties."),
    2: dict(events="07", title="$400 No Limit Hold'em (Day A+B)",
            buyin=400, fee="$70", pool="$330 of every $400", gtd="75,000", chips="40,000", level="40 min",
            late="9 levels + Break (5:55 PM)", start="11:10 AM", rule="multi",
            excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
            notes="Two starting flights (1A, 1B). Day 2 @ 11:00 AM."),
    3: dict(events="19", title="$400 No Limit Hold'em (Day A+B+C)",
            buyin=400, fee="$70", pool="$330 of every $400", gtd="75,000", chips="40,000", level="40 min",
            late="9 levels + Break (5:55 PM)", start="11:10 AM", rule="multi",
            excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
            notes="Three starting flights (1A, 1B, 1C). Day 2 @ 11:00 AM."),
    4: dict(events="59", title="$600 No Limit Hold'em (Day A+B+C)",
            buyin=600, fee="$95", pool="$505 of every $600", gtd="150,000", chips="40,000", level="40 min",
            late="9 levels + Break (5:55 PM)", start="11:10 AM", rule="multi",
            excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight. Day 1A pre-registration discount: $580 instead of $600.",
            notes="Three starting flights. Day 2 @ 11:00 AM."),
    5: dict(events="02, 12", title="$300 No Limit Hold'em (1Day)",
            buyin=300, fee="$58", pool="$242 of every $300", gtd="10,000", chips="40,000", level="30 min",
            late="10 levels + Break (~4:55 PM)", start="11:10 AM", rule="unknown",
            excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
            notes=""),
    6: dict(events="10", title="$400 No Limit Hold'em (1Day)",
            buyin=400, fee="$65", pool="$335 of every $400", gtd="15,000", chips="40,000", level="30 min",
            late="10 levels + Break (~4:55 PM)", start="11:10 AM", rule="unknown",
            excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
            notes=""),
    7: dict(events="14, 28, 63", title="$600 No Limit Hold'em (1Day)",
            buyin=600, fee="$90", pool="$510 of every $600", gtd="30,000 (#14, #63); 40,000 (#28)",
            gtd_map={"14": "30,000", "28": "40,000", "63": "30,000"},
            chips="40,000", level="30 min", late="10 levels + Break (~4:55 PM)", start="11:10 AM",
            rule="unknown", excerpt="No re-entry, rebuy or add-on text appears on the sheet.", notes=""),
    8: dict(events="18, 58", title="$200 No Limit Hold'em Valuetown Bounty (1Day)",
            buyin=200, fee="$40", pool="$160 of every $200", gtd="20,000", chips="25,000", level="30 min",
            late="8 levels + Break (9:40 PM)", start="5:10 PM", rule="multi",
            excerpt="07. ... PokerAtlas PRO players will receive a twenty ($20) rake discount on their initial $200 buy in only ... All subsequent buy in's after the initial buy in will be $200.",
            notes="'Subsequent buy in's' shows more than one buy-in per player is possible."),
    9: dict(events="01", title="$300 No Limit Hold'em (Day B+D)",
            buyin=300, fee="$60", pool="$240 of every $300", gtd="75,000", chips="30,000", level="30 min",
            late="6 levels + Break (~8:40 PM)", start="5:10 PM", rule="multi",
            excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
            notes="Flights 1A-1D. Day 2 @ 12:00 PM."),
    10: dict(events="01", title="$300 No Limit Hold'em (Day A+C)",
             buyin=300, fee="$60", pool="$240 of every $300", gtd="75,000", chips="30,000", level="40 min",
             late="6 levels + Break (~3:40 PM)", start="11:10 AM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
             notes="Flights 1A-1D. Day 2 @ 12:00 PM."),
    11: dict(events="16, 30, 54", title="$600 No Limit Hold'em Bounty (1Day)",
             buyin=600, fee="$90", pool="$510 of every $600",
             gtd="30,000 (#16); 40,000 (#30); 50,000 (#54)",
             gtd_map={"16": "30,000", "30": "40,000", "54": "50,000"},
             chips="40,000", level="30 min",
             late="10 levels + Break (4:55 PM)", start="11:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet. $200 bounty, $500 in the money.",
             notes="Bounty: prize pool + bounties."),
    12: dict(events="26", title="$800 No Limit Hold'em (Day A+C+E)",
             buyin=800, fee="$110", pool="$690 of every $800", gtd="500,000", chips="40,000", level="40 min",
             late="6 levels + Break (~3:40 PM)", start="11:10 AM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
             notes="Six starting flights (1A-1F). Day 2 @ 12:00 PM."),
    13: dict(events="26", title="$800 No Limit Hold'em (Day B+D)",
             buyin=800, fee="$110", pool="$690 of every $800", gtd="500,000", chips="40,000", level="30 min",
             late="6 levels + Break (~8:40 PM)", start="5:10 PM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
             notes="Six starting flights (1A-1F)."),
    14: dict(events="26", title="$800 No Limit Hold'em (Day F Turbo)",
             buyin=800, fee="$110", pool="$690 of every $800", gtd="500,000", chips="40,000", level="20 min",
             late="6 levels + Break (~7:25 PM)", start="5:10 PM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
             notes="Six starting flights (1A-1F)."),
    15: dict(events="29, 31, 34, 38, 42, 50, 51, 53, 55", title="$300 No Limit Hold'em Bounty (1Day)",
             buyin=300, fee="$50", pool="$250 of every $300", gtd="15,000", chips="25,000", level="30 min",
             late="8 levels + Break (9:40 PM)", start="5:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet. $100 bounty per elimination.",
             notes="Bounty: prize pool + bounties."),
    16: dict(events="36", title="$800 No Limit Hold'em Bounty (1Day)",
             buyin=800, fee="$100", pool="$700 of every $800", gtd="75,000", chips="40,000", level="30 min",
             late="10 levels + Break (4:55 PM)", start="11:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet. $200/$500 bounty.",
             notes="Bounty: prize pool + bounties."),
    17: dict(events="24, 32", title="$600 No Limit Hold'em Seniors (1Day) - 50+",
             buyin=600, fee="$90", pool="$510 of every $600", gtd="40,000", chips="40,000", level="30 min",
             late="10 levels + Break (~3:55 PM)", start="10:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="Must be 50+. Pays 15% of the field."),
    18: dict(events="03, 04, 05", title="$200 No Limit Hold'em RaceDay Stack (1Day)",
             buyin=200, fee="$35", pool="$165 of every $200", gtd="", chips="30,000", level="20/15 min",
             late="6 levels + Break (~12:25 PM)", start="10:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="No guarantee stated on the sheet."),
    19: dict(events="33, 37", title="$100 NLH LIPS Ladies Milestone Satellite (1Day)",
             buyin=100, fee="$20", pool="$80 of every $100", gtd="2 seats", chips="20,000", level="20 min",
             late="6 levels + Break (~6:25 PM)", start="4:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="Satellite: prizes are seats into Event #39, not cash. Female players only."),
    20: dict(events="49", title="$1,100 No Limit Hold'em Seniors (Day A+B) - 50+",
             buyin=1100, fee="$140", pool="$960 of every $1,100", gtd="300,000", chips="40,000", level="40 min",
             late="9 levels + Break (~4:55 PM)", start="10:10 AM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
             notes="Two starting flights. Day 2 @ 10:00 AM. Must be 50+."),
    21: dict(events="47", title="$2,200 No Limit Hold'em PokerAtlas Championship (Day 1A)",
             buyin=2200, fee="$225", pool="$1,975 of every $2,200", gtd="1,000,000", chips="40,000",
             level="40 min", late="9 levels + Break (~4:55 PM)", start="10:10 AM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
             notes="Day 1A and Day 1B. Day 2 @ 1:00 PM, Day 3 @ 11:00 AM."),
    22: dict(events="20", title="$300 Pot Limit Omaha Double Board Bomb Pot (1Day)",
             buyin=300, fee="$58", pool="$242 of every $300", gtd="10,000", chips="30,000", level="30 min",
             late="8 levels + break (~4:40 PM)", start="12:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.", notes="8-handed."),
    23: dict(events="57", title="$600 Pot Limit Omaha Double Board Bomb Pot (1Day)",
             buyin=600, fee="$90", pool="$510 of every $600", gtd="25,000", chips="30,000", level="30 min",
             late="8 levels + break (~4:40 PM)", start="12:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.", notes="8-handed."),
    24: dict(events="41, 44", title="$260 NLH Milestone Satellite to Event #47 (1Day)",
             buyin=260, fee="$40", pool="$220 of every $260", gtd="2 seats", chips="20,000", level="20 min",
             late="6 levels + Break (~6:25 PM)", start="4:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="Satellite: prizes are seats into Event #47, not cash."),
    25: dict(events="45, 46, 48", title="$260 NLH Turbo Milestone Satellite to Event #47 (1Day)",
             buyin=260, fee="$35", pool="$225 of every $260", gtd="2 seats", chips="20,000", level="15 min",
             late="6 levels", start="#45 8:10 PM / #46 9:10 AM / #48 12:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="Satellite: prizes are seats into Event #47, not cash."),
    26: dict(events="17", title="$400 Pot Limit Omaha Bounty (1Day)",
             buyin=400, fee="$60", pool="$340 of every $400", gtd="15,000", chips="30,000", level="30 min",
             late="8 levels + break (~4:40 PM)", start="12:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet. $100 bounty.", notes="8-handed."),
    27: dict(events="40", title="$600 Pot Limit Omaha Bounty (1Day)",
             buyin=600, fee="$90", pool="$510 of every $600", gtd="25,000", chips="30,000", level="30 min",
             late="8 levels + break (~4:40 PM)", start="12:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet. $200 bounty.", notes="8-handed."),
    28: dict(events="27", title="$600 BIG O (1Day)",
             buyin=600, fee="$90", pool="$510 of every $600", gtd="25,000", chips="30,000", level="30 min",
             late="8 levels + break (~4:40 PM)", start="12:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.", notes="8-handed."),
    29: dict(events="06", title="$200 No Limit Hold'em (1Day)",
             buyin=200, fee="$40", pool="$160 of every $200", gtd="", chips="30,000", level="30 min",
             late="8 levels + Break (~3:40 PM)", start="11:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="No guarantee stated on the sheet."),
    30: dict(events="08", title="$200 No Limit Hold'em Progressive Knock-Out Bounty (1Day)",
             buyin=200, fee="$40", pool="$160 of every $200", gtd="8,000", chips="25,000", level="30 min",
             late="8 levels + Break (9:40 PM)", start="5:10 PM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="PKO. Bounty: prize pool + bounties."),
    31: dict(events="35", title="$600 NLH LIPS Poker Jingle Tag Team (1Day)",
             buyin=600, fee="$80 house + $10 LIPS", pool="$510 of every $600", gtd="10,000", chips="40,000",
             level="30 min", late="8 levels + Break (~2:40 PM)", start="10:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="Teams rotate players every level. Female/Female or Female/Male."),
    32: dict(events="39", title="$800 NLH LIPS Ladies (2Day) - female only",
             buyin=800, fee="$90 house + $20 LIPS", pool="$690 of every $800", gtd="40,000", chips="40,000",
             level="40 min", late="9 levels + Break (~4:55 PM)", start="Day 1 Dec 10 10:10 AM",
             rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="Day 2 Dec 11 10:00 AM. Female players only."),
    33: dict(events="43", title="$600 No Limit Hold'em LIPS Kings and Queens Bounty (1Day)",
             buyin=600, fee="$80 house + $10 LIPS", pool="$510 of every $600", gtd="30,000", chips="40,000",
             level="30 min", late="10 levels + Break (4:55 PM)", start="11:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet. $200 bounty.",
             notes="Bounty: prize pool + bounties."),
    34: dict(events="52", title="$1,100 No Limit Hold'em Progressive Knock-Out Bounty (1Day)",
             buyin=1100, fee="$130", pool="$970 of every $1,100", gtd="75,000", chips="40,000", level="30 min",
             late="10 levels + Break (4:55 PM)", start="11:10 AM", rule="unknown",
             excerpt="No re-entry, rebuy or add-on text appears on the sheet.",
             notes="PKO, $200 starting bounty. Bounty: prize pool + bounties."),
    35: dict(events="56", title="$1,100 No Limit Hold'em (Day A+C+E)",
             buyin=1100, fee="$140", pool="$960 of every $1,100", gtd="500,000", chips="40,000", level="40 min",
             late="9 levels + Break (~4:55 PM)", start="10:10 AM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight. Day 1A pre-registration $40 discount: $1,060.",
             notes="Five starting flights (1A-1E). Day 2 @ 11:00 AM."),
    36: dict(events="56", title="$1,100 No Limit Hold'em (Day B+D)",
             buyin=1100, fee="$140", pool="$960 of every $1,100", gtd="500,000", chips="40,000", level="30 min",
             late="9 levels + Break (~11:10 PM)", start="6:10 PM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight. Day 1B pre-registration $40 discount: $1,060.",
             notes="Five starting flights (1A-1E)."),
    37: dict(events="47", title="$2,200 No Limit Hold'em PokerAtlas Championship (Day 1B)",
             buyin=2200, fee="$225", pool="$1,975 of every $2,200", gtd="1,000,000", chips="40,000",
             level="30 min", late="9 levels + Break (~11:10 PM)", start="6:10 PM", rule="multi",
             excerpt="08. Any player who bags chips for Day 2 may not play a subsequent flight.",
             notes="Day 1A and Day 1B."),
}

# schedule rows: date | start | event_no | name | flight | sheet
VENETIAN_ROWS = [
    ("2026-11-16", "11:10", "1", "$300 No Limit Hold'em 1A $75K GTD", "1A", 10, "entry"),
    ("2026-11-16", "17:10", "1", "$300 No Limit Hold'em 1B $75K GTD", "1B", 9, "entry"),
    ("2026-11-17", "11:10", "1", "$300 No Limit Hold'em 1C $75K GTD", "1C", 10, "entry"),
    ("2026-11-17", "17:10", "1", "$300 No Limit Hold'em 1D $75K GTD", "1D", 9, "entry"),
    ("2026-11-18", "11:10", "2", "$300 No Limit Hold'em $10K GTD (1Day)", "", 5, "entry"),
    ("2026-11-18", "12:00", "1", "$300 No Limit Hold'em Day 2 Restart", "", 10, "restart"),
    ("2026-11-19", "10:10", "3", "$200 NLH RaceDay Stack (1Day)", "", 18, "entry"),
    ("2026-11-20", "10:10", "4", "$200 NLH RaceDay Stack (1Day)", "", 18, "entry"),
    ("2026-11-21", "10:10", "5", "$200 NLH RaceDay Stack (1Day)", "", 18, "entry"),
    ("2026-11-22", "11:10", "6", "$200 No Limit Hold'em (1Day)", "", 29, "entry"),
    ("2026-11-23", "11:10", "7", "$400 No Limit Hold'em 1A $75K GTD", "1A", 2, "entry"),
    ("2026-11-23", "17:10", "8", "$200 No Limit Hold'em $8K GTD (1Day) - Progressive Knock-Out Bounty (PKO)", "", 30, "entry"),
    ("2026-11-24", "11:10", "7", "$400 No Limit Hold'em 1B $75K GTD", "1B", 2, "entry"),
    ("2026-11-24", "17:10", "9", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-11-25", "11:00", "7", "$400 No Limit Hold'em Day 2 Restart", "", 2, "restart"),
    ("2026-11-25", "11:10", "10", "$400 No Limit Hold'em $15K GTD (1Day)", "", 6, "entry"),
    ("2026-11-25", "17:10", "11", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-11-26", "11:10", "12", "$300 No Limit Hold'em $10K GTD (1Day)", "", 5, "entry"),
    ("2026-11-26", "17:10", "13", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-11-27", "11:10", "14", "$600 No Limit Hold'em $30K GTD (1Day)", "", 7, "entry"),
    ("2026-11-27", "17:10", "15", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-11-28", "11:10", "16", "$600 No Limit Hold'em Bounty $30K GTD (1Day) - $200 bounties to start & $500 bounties in the money", "", 11, "entry"),
    ("2026-11-28", "12:10", "17", "$400 Pot Limit Omaha Bounty $15K GTD (1Day)", "", 26, "entry"),
    ("2026-11-28", "17:10", "18", "$200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) - POKERATLAS PRO MEMBER $20 RAKE DISCOUNT", "", 8, "entry"),
    ("2026-11-29", "11:10", "19", "$400 No Limit Hold'em 1A $75K GTD", "1A", 3, "entry"),
    ("2026-11-29", "12:10", "20", "$300 Pot Limit Omaha $10K GTD (1Day) - Double Board Bomb Pot", "", 22, "entry"),
    ("2026-11-29", "17:10", "21", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-11-30", "11:10", "19", "$400 No Limit Hold'em 1B $75K GTD", "1B", 3, "entry"),
    ("2026-11-30", "17:10", "22", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-12-01", "11:10", "19", "$400 No Limit Hold'em 1C $75K GTD", "1C", 3, "entry"),
    ("2026-12-01", "17:10", "23", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-12-02", "10:10", "24", "$600 No Limit Hold'em Seniors $40K GTD (1Day) - Must be 50+ years of age to participate", "", 17, "entry"),
    ("2026-12-02", "11:00", "19", "$400 No Limit Hold'em Day 2 Restart", "", 3, "restart"),
    ("2026-12-02", "17:10", "25", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-12-03", "11:10", "26", "$800 No Limit Hold'em 1A $500K GTD", "1A", 12, "entry"),
    ("2026-12-03", "12:10", "27", "$600 BIG O $25K GTD (1Day)", "", 28, "entry"),
    ("2026-12-03", "17:10", "26", "$800 No Limit Hold'em 1B $500K GTD", "1B", 13, "entry"),
    ("2026-12-04", "11:10", "26", "$800 No Limit Hold'em 1C $500K GTD", "1C", 12, "entry"),
    ("2026-12-04", "17:10", "26", "$800 No Limit Hold'em 1D $500K GTD", "1D", 13, "entry"),
    ("2026-12-05", "11:10", "26", "$800 No Limit Hold'em 1E $500K GTD", "1E", 12, "entry"),
    ("2026-12-05", "17:10", "26", "$800 No Limit Hold'em 1F (Turbo) $500K GTD", "1F", 14, "entry"),
    ("2026-12-06", "11:10", "28", "$600 No Limit Hold'em $40K GTD (1Day)", "", 7, "entry"),
    ("2026-12-06", "12:00", "26", "$800 No Limit Hold'em Day 2 Restart", "", 12, "restart"),
    ("2026-12-06", "17:10", "29", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-07", "11:10", "30", "$600 No Limit Hold'em Bounty $40K GTD (1Day) - $200 bounties to start & $500 bounties in the money", "", 11, "entry"),
    ("2026-12-07", "17:10", "31", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-08", "10:10", "32", "$600 No Limit Hold'em Seniors $40K GTD (1Day) - Must be 50+ years of age to participate", "", 17, "entry"),
    ("2026-12-08", "16:10", "33", "$100 NLH LIPS Ladies Milestone Satellite (1Day) - Awards Direct Entry to Event # 39", "", 19, "satellite"),
    ("2026-12-08", "17:10", "34", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-09", "10:10", "35", "$600 NLH LIPS Poker Jingle Tag Team $10K GTD (1Day)", "", 31, "entry"),
    ("2026-12-09", "11:10", "36", "$800 No Limit Hold'em Bounty $75K GTD (1Day) - $200 bounties to start & $500 bounties in the money", "", 16, "entry"),
    ("2026-12-09", "16:10", "37", "$100 NLH LIPS Ladies Milestone Satellite (1Day) - Awards Direct Entry to Event # 39", "", 19, "satellite"),
    ("2026-12-09", "17:10", "38", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-10", "10:10", "39", "$800 No Limit Hold'em LIPS Ladies $40K GTD (2Day) - Women in Poker - Main Event", "", 32, "entry"),
    ("2026-12-10", "12:10", "40", "$600 Pot Limit Omaha Bounty $25K GTD (1Day)", "", 27, "entry"),
    ("2026-12-10", "16:10", "41", "$260 NLH Milestone Satellite (1Day) - Awards Direct Entry to Event # 47", "", 24, "satellite"),
    ("2026-12-10", "17:10", "42", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-11", "10:00", "39", "$800 No Limit Hold'em LIPS Ladies Day 2 Restart - Play Down to Final 7 - Streamed Final Table (PokerGO)", "", 32, "restart"),
    ("2026-12-11", "11:10", "43", "$600 No Limit Hold'em LIPS $30K GTD (1Day) - KINGS and QUEENS Bounty - Open to all players", "", 33, "entry"),
    ("2026-12-11", "16:10", "44", "$260 NLH Milestone Satellite (1Day) - Awards Direct Entry to Event # 47", "", 24, "satellite"),
    ("2026-12-11", "19:00", "39", "$800 No Limit Hold'em LIPS Ladies Final Table - Streamed Final Table (PokerGO)", "", 32, "final"),
    ("2026-12-11", "20:10", "45", "$260 NLH Turbo Milestone Satellite (1Day) - Awards Direct Entry to Event # 47", "", 25, "satellite"),
    ("2026-12-12", "09:10", "46", "$260 NLH Turbo Milestone Satellite (1Day) - Awards Direct Entry to Event # 47", "", 25, "satellite"),
    ("2026-12-12", "10:10", "47", "$2,200 No Limit Hold'em 1A $1 Mill GTD - PokerAtlas Championship Title Event", "1A", 21, "entry"),
    ("2026-12-12", "12:10", "48", "$260 NLH Turbo Milestone Satellite (1Day) - Awards Direct Entry to Event # 47", "", 25, "satellite"),
    ("2026-12-12", "18:10", "47", "$2,200 No Limit Hold'em 1B $1 Mill GTD - PokerAtlas Championship Title Event", "1B", 37, "entry"),
    ("2026-12-13", "10:10", "49", "$1,100 No Limit Hold'em Seniors 1A $300K GTD - Must be 50+ years of age to participate", "1A", 20, "entry"),
    ("2026-12-13", "13:00", "47", "$2,200 NLH PokerAtlas Championship Title Event Day 2 Restart - Play Down to Final 7 - Streamed Final Table (PokerGO)", "", 21, "restart"),
    ("2026-12-13", "17:10", "50", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-14", "10:10", "49", "$1,100 No Limit Hold'em Seniors 1B $300K GTD - Must be 50+ years of age to participate", "1B", 20, "entry"),
    ("2026-12-14", "11:00", "47", "$2,200 NLH PokerAtlas Championship Title Event Day 3 Restart - Streamed Final Table (PokerGO)", "", 21, "restart"),
    ("2026-12-14", "17:10", "51", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-15", "10:00", "49", "$1,100 No Limit Hold'em Seniors Day 2 Restart", "", 20, "restart"),
    ("2026-12-15", "11:10", "52", "$1,100 No Limit Hold'em $75K GTD (1Day) - Progressive Knock-Out Bounty (PKO)", "", 34, "entry"),
    ("2026-12-15", "17:10", "53", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-16", "11:10", "54", "$600 No Limit Hold'em Bounty $50K GTD (1Day) - $200 bounties to start & $500 bounties in the money", "", 11, "entry"),
    ("2026-12-16", "17:10", "55", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", "", 15, "entry"),
    ("2026-12-17", "10:10", "56", "$1,100 No Limit Hold'em 1A $500K GTD - $40 Rake Discount for Entries Before 10:10 a.m.", "1A", 35, "entry"),
    ("2026-12-17", "12:10", "57", "$600 Pot Limit Omaha $25K GTD (1Day) - Double Board Bomb Pot", "", 23, "entry"),
    ("2026-12-17", "18:10", "56", "$1,100 No Limit Hold'em 1B $500K GTD - $40 Rake Discount for Entries Before 6:10 p.m.", "1B", 36, "entry"),
    ("2026-12-18", "10:10", "56", "$1,100 No Limit Hold'em 1C $500K GTD", "1C", 35, "entry"),
    ("2026-12-18", "18:10", "56", "$1,100 No Limit Hold'em 1D $500K GTD", "1D", 36, "entry"),
    ("2026-12-19", "10:10", "56", "$1,100 No Limit Hold'em 1E $500K GTD", "1E", 35, "entry"),
    ("2026-12-19", "17:10", "58", "$200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) - POKERATLAS PRO MEMBER $20 RAKE DISCOUNT", "", 8, "entry"),
    ("2026-12-20", "11:00", "56", "$1,100 No Limit Hold'em Day 2 Restart", "", 35, "restart"),
    ("2026-12-20", "11:10", "59", "$600 No Limit Hold'em 1A $150K GTD - $20 Rake Discount for Entries Before 11:10 a.m.", "1A", 4, "entry"),
    ("2026-12-20", "17:10", "60", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-12-21", "11:10", "59", "$600 No Limit Hold'em 1B $150K GTD", "1B", 4, "entry"),
    ("2026-12-21", "17:10", "61", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-12-22", "11:10", "59", "$600 No Limit Hold'em 1C $150K GTD", "1C", 4, "entry"),
    ("2026-12-22", "17:10", "62", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
    ("2026-12-23", "11:00", "59", "$600 No Limit Hold'em Day 2 Restart", "", 4, "restart"),
    ("2026-12-23", "11:10", "63", "$600 No Limit Hold'em $30K GTD (1Day)", "", 7, "entry"),
    ("2026-12-23", "17:10", "64", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", "", 1, "entry"),
]

# events whose official sheet states a bagging rule but the event has one Day 1
# (kept explicit so the build never has to guess)
SINGLE_DAY_MULTI = set(["18", "58"])


def build_venetian():
    rows = []
    for date, start, ev, name, flight, sheet, kind in VENETIAN_ROWS:
        s = SHEETS[sheet]
        rule = s["rule"]
        rows.append(dict(
            venue="The Venetian Resort", room="Venetian Poker Room", date=date, start=start,
            day="", event_no=ev, name=name, flight=flight, kind=kind,
            buyin=s["buyin"], house_fee=s["fee"], to_prize_pool=s["pool"],
            guarantee=(s.get("gtd_map") or {}).get(ev, s["gtd"]),
            chips=s["chips"], levels=s["level"],
            late_reg=s["late"], sheet_start=s["start"], sheet_title=s["title"],
            entry_rule=rule, rule_excerpt=s["excerpt"],
            notes=(s["notes"] + (" This structure sheet covers events %s, whose guarantees differ: %s."
                                 % (s["events"], s["gtd"])) if s.get("gtd_map") else s["notes"]),
            source=SHEET.format(sheet), source_label="structure sheet %d" % sheet,
            schedule_source=SCHEDULE_PAGE, retrieved=RETRIEVED,
        ))
    return rows


# --------------------------------------------------------------------------
# 2. WPT World Championship festival, Wynn Las Vegas (Nov 27 - Dec 21, 2026)
# --------------------------------------------------------------------------
WPT_SCHEDULE = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WPT_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
WPT_TERMS = "https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf"
WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"

WPT_RULES = {
    "$600 NLH $400K": ("multi", "Unlimited re-entry for each starting flight will be available until the start of level 9. A player who advances to Day 2 is prohibited from entering a subsequent starting flight."),
    "$600 TORSE": ("multi", "Unlimited re-entry will be available until the start of level 9"),
    "$400 PLO": ("multi", "Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.)"),
    "$600 Mixed Triple Draw": ("multi", "Unlimited re-entry will be available until the start of level 9"),
    "$800 NLH $1M": ("multi", "Unlimited re-entry for each starting flight will be available until the start of level 9. A player who advances to Day 2 is prohibited from entering a subsequent starting flight."),
    "$600 Limit Omaha 8": ("multi", "Unlimited re-entry will be available until the start of level 9"),
    "$600 Limit Omaha 8/Stud 8": ("multi", "Unlimited re-entry will be available until the start of level 9"),
    "$1,100 PLO": ("multi", "Unlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.)"),
    "$1,600 NLH $1M": ("multi", "Unlimited re-entry for each starting flight will be available until the start of level 10. A player who advances to Day 2 is prohibited from entering a subsequent starting flight."),
    "$600 HORSE": ("multi", "Unlimited re-entry will be available until the start of level 9 (approximately 4:30 p.m.)"),
    "WPT Prime Championship": ("multi", "One (1) Entry and One (1) re-entry for each starting flight will be available until the start of level 10 (approximately 6:45 p.m.)."),
    "$600 NLH Turbo": ("multi", "Unlimited re-entry will be available until the start of level 9."),
    "$1,600 PLO Mystery Bounty": ("multi", "Unlimited re-entry for each starting flight will be available until the start of level 10."),
}
WPT_UNREAD = ("unread", "Entry terms for this event were not read individually during this audit. See the official structures PDF and the Flagged page.")

# date, start, event, buyin, guarantee, chips, levels, kind, rule_key
WPT_ROWS = [
    ("2026-11-27", "11:00", "No Limit Hold'em Day 1A", 600, 400000, "40,000", "30/40", "entry", "$600 NLH $400K"),
    ("2026-11-27", "12:00", "TORSE", 600, None, "35,000", "30", "entry", "$600 TORSE"),
    ("2026-11-27", "13:00", "PLO", 400, None, "30,000", "30", "entry", "$400 PLO"),
    ("2026-11-27", "17:00", "No Limit Hold'em Day 1B", 600, 400000, "40,000", "30/40", "entry", "$600 NLH $400K"),
    ("2026-11-28", "11:00", "No Limit Hold'em Day 1C", 600, 400000, "40,000", "30/40", "entry", "$600 NLH $400K"),
    ("2026-11-28", "12:00", "Mixed Triple Draw (A-5, 2-7, Badugi)", 600, None, "35,000", "30", "entry", "$600 Mixed Triple Draw"),
    ("2026-11-28", "17:00", "No Limit Hold'em Day 1D", 600, 400000, "40,000", "30/40", "entry", "$600 NLH $400K"),
    ("2026-11-29", "11:00", "No Limit Hold'em Day 1E", 600, 400000, "40,000", "30/40", "entry", "$600 NLH $400K"),
    ("2026-11-29", "18:00", "No Limit Hold'em Day 1F", 600, 400000, "40,000", "20/40", "entry", "$600 NLH $400K"),
    ("2026-11-30", "11:00", "No Limit Hold'em Day 1A", 800, 1000000, "40,000", "30/40", "entry", "$800 NLH $1M"),
    ("2026-11-30", "12:00", "Limit Omaha 8", 600, None, "35,000", "30", "entry", "$600 Limit Omaha 8"),
    ("2026-11-30", "13:00", "No Limit Hold'em Day 2", 800, 1000000, "40,000", "30/40", "restart", "$800 NLH $1M"),
    ("2026-11-30", "17:00", "No Limit Hold'em Day 1B", 800, 1000000, "40,000", "30/40", "entry", "$800 NLH $1M"),
    ("2026-12-01", "11:00", "No Limit Hold'em Day 1C", 800, 1000000, "40,000", "30/40", "entry", "$800 NLH $1M"),
    ("2026-12-01", "12:00", "Limit Omaha 8 / Stud 8", 600, None, "35,000", "30", "entry", "$600 Limit Omaha 8/Stud 8"),
    ("2026-12-01", "13:00", "PLO", 1100, None, "30,000", "30", "entry", "$1,100 PLO"),
    ("2026-12-01", "17:00", "No Limit Hold'em Day 1D", 800, 1000000, "40,000", "30/40", "entry", "$800 NLH $1M"),
    ("2026-12-02", "11:00", "No Limit Hold'em Day 1E", 800, 1000000, "40,000", "30/40", "entry", "$800 NLH $1M"),
    ("2026-12-02", "18:00", "No Limit Hold'em Day 1F", 800, 1000000, "40,000", "20/40", "entry", "$800 NLH $1M"),
    ("2026-12-03", "11:00", "No Limit Hold'em Day 1A", 1600, 1000000, "40,000", "40", "entry", "$1,600 NLH $1M"),
    ("2026-12-03", "13:00", "No Limit Hold'em Day 2", None, None, "40,000", "40", "restart", "$1,600 NLH $1M"),
    ("2026-12-03", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, "20,000", "20", "satellite", None),
    ("2026-12-04", "11:00", "No Limit Hold'em Day 1B", 1600, 1000000, "40,000", "40", "entry", "$1,600 NLH $1M"),
    ("2026-12-04", "12:00", "HORSE", 600, None, "35,000", "30", "entry", "$600 HORSE"),
    ("2026-12-04", "13:00", "No Limit Hold'em Final Table", None, None, "", "", "final", "$1,600 NLH $1M"),
    ("2026-12-04", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, "20,000", "20", "satellite", None),
    ("2026-12-05", "11:00", "No Limit Hold'em Day 2", 1100, 5000000, "40,000", "40/60", "restart", "WPT Prime Championship"),
    ("2026-12-05", "11:00", "WPT Prime Championship Day 1A", 1100, 5000000, "40,000", "40/60", "entry", "WPT Prime Championship"),
    ("2026-12-05", "21:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
    ("2026-12-06", "11:00", "WPT Prime Championship Day 1B", 1100, 5000000, "40,000", "40/60", "entry", "WPT Prime Championship"),
    ("2026-12-06", "11:00", "PLO Mystery Bounty Day 1A", 1600, 500000, "40,000", "40", "entry", "$1,600 PLO Mystery Bounty"),
    ("2026-12-06", "12:00", "Milestone Satellite to $1,100 Prime Championship", 200, None, "20,000", "20", "satellite", None),
    ("2026-12-06", "18:00", "PLO Mystery Bounty Day 1B", 1600, 500000, "40,000", "20/40", "entry", "$1,600 PLO Mystery Bounty"),
    ("2026-12-06", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, "20,000", "20", "satellite", None),
    ("2026-12-06", "21:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
    ("2026-12-07", "11:00", "WPT Prime Championship Day 1C", 1100, 5000000, "40,000", "40/60", "entry", "WPT Prime Championship"),
    ("2026-12-07", "11:00", "HORSE (2 Day)", 1100, None, "40,000", "40", "entry", None),
    ("2026-12-07", "12:00", "PLO Mystery Bounty Day 2", None, None, "", "", "restart", "$1,600 PLO Mystery Bounty"),
    ("2026-12-07", "13:00", "PLO $500 Bounty", 1600, 100000, "30,000", "30", "entry", None),
    ("2026-12-07", "19:00", "Milestone Satellite Package to Prime and World Championship", 1600, None, "20,000", "25", "satellite", None),
    ("2026-12-07", "21:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
    ("2026-12-08", "11:00", "WPT Prime Championship Day 1D", 1100, 5000000, "40,000", "40/60", "entry", "WPT Prime Championship"),
    ("2026-12-08", "19:00", "Milestone Satellite to $10,400 World Championship", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-08", "21:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
    ("2026-12-09", "11:00", "No Limit Hold'em (2 Day)", 1600, 1000000, "40,000", "40", "entry", None),
    ("2026-12-09", "12:00", "WPT Prime Championship Day 2", None, None, "", "", "restart", "WPT Prime Championship"),
    ("2026-12-09", "13:00", "PLO $1,000 Bounty", 3000, 250000, "30,000", "30", "entry", None),
    ("2026-12-09", "13:00", "Limit Omaha 8", 800, None, "35,000", "30", "entry", None),
    ("2026-12-09", "14:00", "Milestone Satellite to $10,400 World Championship", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-09", "19:00", "Milestone Satellite to $10,400 World Championship", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-09", "21:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
    ("2026-12-10", "10:00", "Super Gold Million Mystery Bounty Day 1A", 400, 3000000, "30,000", "30/40", "entry", None),
    ("2026-12-10", "12:00", "WPT Prime Championship Day 3", None, None, "", "", "restart", "WPT Prime Championship"),
    ("2026-12-10", "18:00", "Super Gold Million Mystery Bounty Day 1B", 400, 3000000, "30,000", "20/40", "entry", None),
    ("2026-12-11", "10:00", "Super Gold Million Mystery Bounty Day 1C", 400, 3000000, "30,000", "30/40", "entry", None),
    ("2026-12-11", "12:00", "WPT Prime Championship Day 4", None, None, "", "", "restart", "WPT Prime Championship"),
    ("2026-12-11", "18:00", "Super Gold Million Mystery Bounty Day 1D", 400, 3000000, "30,000", "20/40", "entry", None),
    ("2026-12-12", "10:00", "No Limit Hold'em", 800, 100000, "30,000", "30", "entry", None),
    ("2026-12-12", "13:00", "PLO", 3000, 250000, "30,000", "30", "entry", None),
    ("2026-12-12", "14:00", "WPT Prime Championship Final Table", None, None, "", "", "final", "WPT Prime Championship"),
    ("2026-12-12", "14:00", "Super Gold Million Mystery Bounty Day 2", None, None, "", "", "restart", None),
    ("2026-12-12", "14:00", "Milestone Satellite to $10,400 World Championship 1A/B", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-12", "16:00", "Milestone Satellite to $10,400 Ladies NLH Championship", 200, None, "20,000", "20", "satellite", None),
    ("2026-12-12", "19:00", "Milestone Satellite to $10,400 World Championship 1A/B", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-12", "21:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
    ("2026-12-13", "11:00", "WPT World Championship Day 1A - $1,000,000 Added", 10400, None, "100,000", "60/90", "entry", None),
    ("2026-12-13", "11:00", "Ladies NLH Championship (2 Day)", 1100, 250000, "40,000", "40", "entry", None),
    ("2026-12-13", "11:00", "TORSE (2 Day)", 1100, None, "40,000", "40", "entry", None),
    ("2026-12-13", "11:00", "No Limit Hold'em Day 1A", 800, 500000, "40,000", "40", "entry", None),
    ("2026-12-13", "12:00", "PLO Day 1A", 1600, 1000000, "40,000", "40", "entry", None),
    ("2026-12-13", "12:00", "Milestone Satellite to $10,400 World Championship 1B", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-13", "13:00", "Super Gold Million Mystery Bounty Day 3", None, None, "", "", "restart", None),
    ("2026-12-13", "18:00", "Milestone Satellite to $10,400 World Championship 1B/C", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-14", "11:00", "WPT World Championship Day 1B - $1,000,000 Added", 10400, None, "100,000", "60/90", "entry", None),
    ("2026-12-14", "11:00", "No Limit Hold'em Day 1B", 800, 500000, "40,000", "40", "entry", None),
    ("2026-12-14", "12:00", "PLO Day 1B", 1600, 1000000, "40,000", "40", "entry", None),
    ("2026-12-14", "12:00", "Mixed Triple Draw (A-5, 2-7, Badugi) (2 Day)", 1100, None, "40,000", "40", "entry", None),
    ("2026-12-14", "12:00", "Milestone Satellite to $10,400 World Championship 1C", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-14", "14:00", "Super Gold Million Mystery Bounty Final Table", None, None, "", "", "final", None),
    ("2026-12-14", "18:00", "Milestone Satellite to $10,400 World Championship 1C", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-14", "19:00", "PLO Turbo", 1100, 100000, "30,000", "20", "entry", None),
    ("2026-12-14", "21:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
    ("2026-12-15", "11:00", "WPT World Championship Day 1C - $1,000,000 Added", 10400, None, "100,000", "60/90", "entry", None),
    ("2026-12-15", "11:00", "No Limit Hold'em Day 2", None, None, "", "", "restart", None),
    ("2026-12-15", "11:00", "Milestone Satellite to $10,400 World Championship 1C/Day 2", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-15", "12:00", "PLO Day 2", None, None, "", "", "restart", None),
    ("2026-12-15", "12:00", "Big O", 1100, None, "30,000", "30", "entry", None),
    ("2026-12-15", "13:00", "PLO Progressive Bounty (PKO)", 3000, 250000, "30,000", "30", "entry", None),
    ("2026-12-15", "18:00", "Milestone Satellite to $10,400 World Championship Day 2", 1100, None, "20,000", "25", "satellite", None),
    ("2026-12-15", "19:00", "NLH $500 Bounty Turbo", 1600, 100000, "30,000", "20", "entry", None),
    ("2026-12-16", "11:00", "No Limit Hold'em Day 1A", 1100, 1000000, "40,000", "40", "entry", None),
    ("2026-12-16", "12:00", "WPT World Championship Day 2 (registration open until the start of Day 2)", None, None, "", "", "restart", None),
    ("2026-12-16", "12:00", "PLO Double Board Bomb Pot", 800, None, "30,000", "30", "entry", None),
    ("2026-12-16", "13:00", "PLO 6-Max", 10500, None, "100,000", "30/40", "entry", None),
    ("2026-12-16", "13:00", "HORSE", 800, None, "35,000", "30", "entry", None),
    ("2026-12-16", "18:00", "Milestone Satellite to $25K NLH High Roller", 3000, None, "20,000", "25", "satellite", None),
    ("2026-12-16", "18:00", "Milestone Satellite to $3,000 NLH", 400, None, "20,000", "20", "satellite", None),
    ("2026-12-16", "19:00", "No Limit Hold'em Day 1B", 1100, 1000000, "40,000", "20/40", "entry", None),
    ("2026-12-17", "11:00", "Seniors NLH Championship (3 Day)", 1100, 500000, "40,000", "40", "entry", None),
    ("2026-12-17", "11:00", "Wynn Mixed Championship (2 Day)", 1600, None, "40,000", "40/60", "entry", None),
    ("2026-12-17", "12:00", "WPT World Championship Day 3", None, None, "", "", "restart", None),
    ("2026-12-17", "12:00", "No Limit Hold'em Day 2", None, None, "", "", "restart", None),
    ("2026-12-17", "12:00", "No Limit Hold'em Day 1A", 3000, 2000000, "40,000", "40", "entry", None),
    ("2026-12-17", "13:00", "NLH High Roller (2 Day)", 25800, None, "200,000", "40/60", "entry", None),
    ("2026-12-17", "14:00", "Milestone Satellite to $3,000 NLH", 400, None, "20,000", "20", "satellite", None),
    ("2026-12-17", "19:00", "Milestone Satellite to $3,000 NLH", 400, None, "20,000", "20", "satellite", None),
    ("2026-12-18", "10:00", "Milestone Satellite to $3,000 NLH", 400, None, "20,000", "15", "satellite", None),
    ("2026-12-18", "12:00", "WPT World Championship Day 4", None, None, "", "", "restart", None),
    ("2026-12-18", "12:00", "No Limit Hold'em Day 1B", 3000, 2000000, "40,000", "40", "entry", None),
    ("2026-12-18", "12:00", "Limit Omaha 8 Championship (2 Day)", 1600, None, "40,000", "40/60", "entry", None),
    ("2026-12-18", "12:00", "No Limit Hold'em", 600, 100000, "30,000", "30", "entry", None),
    ("2026-12-18", "13:00", "NLH 6-Max", 10500, None, "100,000", "30/40", "entry", None),
    ("2026-12-18", "14:00", "Milestone Satellite to $5,000 Seniors High Roller", 600, None, "20,000", "20", "satellite", None),
    ("2026-12-18", "18:00", "NLH Turbo", 1100, 100000, "30,000", "20", "entry", None),
    ("2026-12-19", "11:00", "Seniors High Roller (3 Day)", 5000, 250000, "50,000", "60", "entry", None),
    ("2026-12-19", "11:00", "NLH Mystery Bounty Day 1A", 1600, 1000000, "40,000", "40", "entry", None),
    ("2026-12-19", "12:00", "WPT World Championship Day 5", None, None, "", "", "restart", None),
    ("2026-12-19", "12:00", "No Limit Hold'em Day 2", None, None, "", "", "restart", None),
    ("2026-12-19", "12:00", "Milestone Satellite to $1,600 Mystery Bounty", 300, None, "20,000", "20", "satellite", None),
    ("2026-12-19", "13:00", "PLO", 10500, None, "100,000", "30/40", "entry", None),
    ("2026-12-19", "13:00", "NLH 6-Max", 3000, 500000, "30,000", "30", "entry", None),
    ("2026-12-19", "13:00", "TORSE Championship (2 Day)", 1600, None, "40,000", "40/60", "entry", None),
    ("2026-12-19", "17:00", "Milestone Satellite to $1,600 Mystery Bounty", 300, None, "20,000", "20", "satellite", None),
    ("2026-12-19", "18:00", "NLH 6-Max Turbo", 600, 50000, "30,000", "20", "entry", None),
    ("2026-12-19", "19:00", "NLH Mystery Bounty Day 1B", 1600, 1000000, "40,000", "20/40", "entry", None),
    ("2026-12-20", "11:00", "NLH Mystery Bounty Day 1C", 1600, 1000000, "40,000", "40", "entry", None),
    ("2026-12-20", "12:00", "No Limit Hold'em Final Table", None, None, "", "", "final", None),
    ("2026-12-20", "12:00", "No Limit Hold'em", 600, 50000, "30,000", "30", "entry", None),
    ("2026-12-20", "13:00", "NLH 8-Max", 10500, None, "100,000", "30/40", "entry", None),
    ("2026-12-20", "13:00", "Mixed Triple Draw (A-5, 2-7, Badugi)", 600, None, "35,000", "30", "entry", "$600 Mixed Triple Draw"),
    ("2026-12-20", "14:00", "WPT World Championship Final Table", None, None, "", "", "final", None),
    ("2026-12-20", "18:00", "5-Card PLO Turbo", 600, 50000, "30,000", "20", "entry", None),
    ("2026-12-20", "19:00", "NLH Mystery Bounty Day 1D", 1600, 1000000, "40,000", "20/40", "entry", None),
    ("2026-12-21", "12:00", "No Limit Hold'em", 1100, 100000, "30,000", "30", "entry", None),
    ("2026-12-21", "13:00", "NLH Mystery Bounty Day 2", None, None, "", "", "restart", None),
    ("2026-12-21", "20:00", "NLH Turbo", 600, 50000, "30,000", "20", "entry", "$600 NLH Turbo"),
]


def build_wpt():
    rows = []
    for date, start, name, buyin, gtd, chips, levels, kind, key in WPT_ROWS:
        rule, excerpt = WPT_RULES.get(key, WPT_UNREAD) if key else WPT_UNREAD
        note = ""
        if date == "2026-12-16":
            note = ("Official schedule PDF labels this block 'Dec. 18 Wednesday'; Wednesday of that "
                    "week is 16 December 2026 and the block sits between Tue 15 and Thu 17. "
                    "Dated 2026-12-16 here and flagged.")
        if date == "2026-12-05" and name == "No Limit Hold'em Day 2":
            note = "Continuation row; the PDF repeats the parent event's $1,100 buy-in and $5,000,000 guarantee on it."
        rows.append(dict(
            venue="Wynn Las Vegas", room="Wynn Las Vegas Poker Room (Encore)", date=date, start=start,
            day="", event_no="", name=name, flight="", kind=kind,
            buyin=buyin, house_fee="", to_prize_pool="", guarantee=gtd, chips=chips, levels=levels,
            late_reg="", sheet_start="", sheet_title="", entry_rule=rule, rule_excerpt=excerpt,
            notes=note, source=WPT_TERMS, source_label="official structures PDF",
            schedule_source=WPT_SCHEDULE, retrieved=RETRIEVED,
        ))
    return rows


# --------------------------------------------------------------------------
# 3. Other Strip / near-Strip rooms
# --------------------------------------------------------------------------
CAESARS_FLYER = ("https://www.caesars.com/content/dam/empire/clv/casino/poker/"
                 "tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf")

WYNN_DAILY_STRUCT = ("https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/"
                     "Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf")
WYNN_DAILY_POSTER = ("https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/"
                     "Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf")

# Wynn daily tournaments, read from the official structures PDF and poster.
# Every one of them states a re-entry fee, or a rebuy / add-on, so every one of
# them is multi-entry. None is a freezeout.
WYNN_DAILY = [
    dict(name="Daily NLH $10,000 Guarantee (Monday-Thursday)", day="Mon-Thu", start="12:00",
         buyin=200, gtd=10000, chips="25,000", levels="30 min", fee="$26 tournament fee, $12 staff, $162 to the prize pool",
         rule="multi",
         excerpt=("The Tournament entry fee, as well as the re-entry fee, is $200. Registration and re-entries "
                  "will be available until the start of level 9 (approximately 4:30 p.m.)."),
         note="Begins at 12 p.m. Offered Monday-Thursday; may be suspended during other series."),
    dict(name="Daily NLH Rebuy & Add-on $40,000 Guarantee (Friday)", day="Friday", start="12:00",
         buyin=240, gtd=40000, chips="25,000", levels="30 min",
         fee="$35 tournament fee, $15 staff, $190 of each entry and rebuy to the prize pool",
         rule="multi",
         excerpt=("Registration, rebuys and add-ons will be available until the start of level 9. Re-entry is NOT "
                  "allowed. Unlimited $200 rebuys for 25,000 tournament chips are available any time a player is at "
                  "15,000 chips or less. One (1) $100 add-on for 15,000 tournament chips is available any time until "
                  "the end of registration."),
         note="Begins at 12 p.m. Re-entry is not allowed, but unlimited rebuys plus an add-on are, so more money buys more chips."),
    dict(name="Daily NLH $25,000 Guarantee (Saturday)", day="Saturday", start="12:00",
         buyin=200, gtd=25000, chips="25,000", levels="30 min", fee="$26 tournament fee, $12 staff, $162 to the prize pool",
         rule="multi",
         excerpt=("The Tournament entry fee, as well as the re-entry fee, is $200. Registration, re-entries, and one "
                  "(1) add-on per entry will be available until the start of level 11 (approximately 5:30 p.m.). One "
                  "(1) $100 add-on for 25,000 tournament chips is available any time until the end of registration."),
         note="Begins at 12 p.m. Offered Saturday; may be suspended during other series."),
    dict(name="Daily NLH $25,000 Guarantee (Sunday)", day="Sunday", start="12:00",
         buyin=200, gtd=25000, chips="25,000", levels="30 min", fee="$26 tournament fee, $12 staff, $162 to the prize pool",
         rule="multi",
         excerpt=("The Tournament entry fee, as well as the re-entry fee, is $200. Registration, re-entries, and one "
                  "(1) add-on per entry will be available until the start of level 11 (approximately 5:30 p.m.). One "
                  "(1) $100 add-on for 25,000 tournament chips is available any time until the end of registration."),
         note="Begins at 12 p.m. Offered Sunday; may be suspended during other series."),
    dict(name="Nightly NLH $10,000 Guarantee (Monday-Sunday)", day="Nightly", start="18:00",
         buyin=160, gtd=10000, chips="25,000", levels="20 min", fee="$20 tournament fee, $10 staff, $130 to the prize pool",
         rule="multi",
         excerpt=("The Tournament entry fee, as well as the re-entry fee, is $160. Registration, re-entries, and one "
                  "(1) add-on per entry will be available until the start of level 9 (approximately 9:00 p.m.). One "
                  "(1) $100 add-on for 25,000 tournament chips is available any time until the end of registration."),
         note="Begins at 6 p.m., offered Monday-Sunday. The latest verified usable start on the Strip."),
]


def build_other():
    out = []
    # Caesars Palace - official daily flyer. Recurring: the flyer states times but not days of week.
    caesars_rows = [
        ("10:00", 100, 50, 1000, "$30", "$70 of every $100"),
        ("14:00", 160, 50, 1000, "$45", "$115 of every $160"),
        ("18:00", 100, 50, 1000, "$30", "$70 of every $100"),
        ("21:00", 160, 50, 1000, "$45", "$115 of every $160"),
    ]
    for start, buyin, addon, gtd, fee, pool in caesars_rows:
        out.append(dict(
            venue="Caesars Palace", room="Caesars Palace Poker Room", date="", start=start, day="Daily",
            event_no="", name="Daily No-Limit Texas Hold'em", flight="", kind="entry",
            buyin=buyin, house_fee=fee, to_prize_pool=pool, guarantee=gtd, chips="20,000",
            levels="20 min", late_reg="Registration closes at the start of level 7",
            sheet_start=start, sheet_title="Daily NLH", entry_rule="multi",
            rule_excerpt=("3. Participants may only register themselves, but may re-enter, by paying the "
                          "entry fee, upon elimination within the first break of play. Optional $50 add-on "
                          "for 15,000 chips, taken at the first break only ($45 to the prize pool, $5 fee)."),
            notes="Days of the week are not stated on the official flyer; treated as daily and flagged.",
            source=CAESARS_FLYER, source_label="official daily tournament flyer",
            schedule_source=CAESARS_FLYER, retrieved=RETRIEVED,
        ))
    # Wynn daily tournaments - official structures PDF + official poster
    for d in WYNN_DAILY:
        out.append(dict(
            venue="Wynn Las Vegas", room="Wynn Las Vegas Poker Room (Encore)", date="", start=d["start"],
            day=d["day"], event_no="", name=d["name"], flight="", kind="entry",
            buyin=d["buyin"], house_fee=d["fee"], to_prize_pool="", guarantee=d["gtd"], chips=d["chips"],
            levels=d["levels"], late_reg="", sheet_start=d["start"], sheet_title="Wynn daily tournament",
            entry_rule=d["rule"], rule_excerpt=d["excerpt"],
            notes=(d["note"] + " Whether these run during the WPT World Championship (27 Nov - 21 Dec 2026) "
                   "is not stated by any official source - see flag F07."),
            source=WYNN_DAILY_STRUCT, source_label="official daily structures PDF",
            schedule_source=WYNN_DAILY_POSTER, retrieved=RETRIEVED,
        ))

    # South Point - official page text only (schedule is published as images)
    sp_rows = [("10:10", 120), ("14:10", 120), ("18:10", 120), ("22:10", 120),
               ("10:10", 300), ("14:10", 300), ("18:10", 300), ("22:10", 300)]
    for start, buyin in sp_rows:
        out.append(dict(
            venue="South Point", room="South Point Poker Room", date="", start=start, day="Daily",
            event_no="", name="Daily tournament ($%d buy-in)" % buyin, flight="", kind="entry",
            buyin=buyin, house_fee="", to_prize_pool="", guarantee=None, chips="", levels="",
            late_reg="", sheet_start=start, sheet_title="", entry_rule="unread",
            rule_excerpt=("The official room page states tournaments daily at 10:10 am, 2:10 pm, 6:10 pm "
                          "and 10:10 pm with buy-ins of $120 and $300. The detailed schedule and structure "
                          "are published only as images, so guarantees, levels and entry rules were not read."),
            notes="Off-Strip (Las Vegas Blvd South). Not within walking distance of the Strip; flagged.",
            source="https://southpointcasino.com/casino/poker-room",
            source_label="official poker room page",
            schedule_source="https://southpointcasino.com/casino/poker-room/daily-tournament-schedule",
            retrieved=RETRIEVED,
        ))
    return out


# --------------------------------------------------------------------------
# 4. Venues (rooms) with their official status
# --------------------------------------------------------------------------
VENUES = [
    dict(key="venetian", name="The Venetian Resort", room="Venetian Poker Room (The Palazzo, level 2, Grand Canal Shoppes)",
         area="Strip - north / centre", status="open_official",
         status_note=("Official poker-room page: 'Our Poker Room is located at The Palazzo on level 2 of Grand Canal "
                      "Shoppes. The Poker Room features 50 tables spread across 14,000 square feet of space, making it "
                      "the largest room on the Las Vegas Strip', open 24 hours. Official series page: DeepStack "
                      "Extravaganza IV, 16 November - 23 December 2026, 'More than $3.6 Million in guaranteed "
                      "tournament prize pools'."),
         source="https://www.venetianlasvegas.com/resort/casino/poker.html"),
    dict(key="wynn", name="Wynn Las Vegas", room="Wynn Las Vegas Poker Room (in Encore)",
         area="Strip - north", status="open_official",
         status_note=("Official Wynn poker page lists the WPT World Championship, 27 November - "
                      "21 December 2026. The official WPT terms state registration is in the "
                      "'Wynn Las Vegas Poker Room, located in Encore at Wynn Las Vegas'."),
         source=WYNN_POKER),
    dict(key="caesars", name="Caesars Palace", room="Caesars Palace Poker Room",
         area="Strip - centre", status="open_official",
         status_note="Official casino page: 'The Poker Room at Caesars Palace is open 24/7 with both live-action cash games and daily tournaments.'",
         source="https://www.caesars.com/caesars-palace/casino"),
    dict(key="horseshoe", name="Horseshoe Las Vegas", room="Hall of Fame Poker Room",
         area="Strip - centre", status="open_official_no_schedule",
         status_note="Official page: 20 tables and '6 exciting tournament times daily'. No schedule or structure is published.",
         source="https://www.caesars.com/horseshoe-las-vegas/casino"),
    dict(key="resortsworld", name="Resorts World Las Vegas", room="Resorts World Poker Room",
         area="Strip - north", status="open_official_no_schedule",
         status_note="The official site has a poker-room section under Gaming. No tournament schedule or structure was retrieved.",
         source="https://www.rwlasvegas.com/gaming/poker-room/"),
    dict(key="southpoint", name="South Point Hotel & Casino", room="South Point Poker Room",
         area="Las Vegas Blvd South (off-Strip)", status="open_official_partial",
         status_note="Official room page states four daily tournaments and $120/$300 buy-ins; the detailed schedule is published as images only.",
         source="https://southpointcasino.com/casino/poker-room"),
    dict(key="bellagio", name="Bellagio", room="Bellagio Poker Room",
         area="Strip - centre", status="unverified",
         status_note="The official poker-room URL returned 'page not found' during this session. Not verified.",
         source="https://bellagio.mgmresorts.com/en/casino/poker-room.html"),
    dict(key="mgmgrand", name="MGM Grand", room="MGM Grand Poker Room",
         area="Strip - south / centre", status="unverified",
         status_note="No official poker-room page was retrieved during this session. Not verified.",
         source="https://mgmgrand.mgmresorts.com/en/casino.html"),
    dict(key="aria", name="ARIA", room="ARIA Poker Room",
         area="Strip - centre", status="unverified",
         status_note="No official poker-room page was retrieved during this session. Not verified.",
         source="https://aria.mgmresorts.com/en/casino.html"),
]


# --------------------------------------------------------------------------
# 5. Hotels
# --------------------------------------------------------------------------
HOTELS = [
    dict(key="venetian", name="The Venetian Resort (Venetian / Palazzo towers)", tier="Luxury",
         area="Strip - north / centre", room="Venetian Poker Room", on_property=True,
         resort_fee=55.0, resort_fee_text="$55 plus tax per night",
         resort_fee_source="https://www.venetianlasvegas.com/resort/resort-fee.html",
         resort_fee_note=("Official resort-fee page: 'Rates include a daily Resort Fee of $55 plus tax "
                          "per night, payable upon check-in.' Includes Canyon Ranch fitness access for two, "
                          "in-suite internet, boarding-pass printing, local calls, PressReader."),
         booking="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date={IN}&children[]=0&departure_date={OUT}&view=calendar",
         address="", address_source="",
         parking=("Complimentary self-parking for non-registered hotel guests who play for three hours or more in "
                  "tournaments or cash games (official player-parking page). The poker room has direct access to "
                  "The Palazzo self-parking garage."),
         parking_source="https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html",
         cancel="", cancel_source="",
         poker_rate=("Reduced suite rates are offered to players who stay at The Venetian or The Palazzo and play "
                     "poker with a Venetian Rewards card (official poker suite-rates page)."),
         poker_rate_source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         quality_note="AAA Five Diamond (Palazzo). On the same property as the Venetian poker room."),
    dict(key="wynn", name="Wynn Las Vegas / Encore", tier="Luxury", area="Strip - north",
         room="Wynn Las Vegas Poker Room (Encore)", on_property=True,
         resort_fee=None, resort_fee_text="", resort_fee_source="",
         resort_fee_note=("No official resort-fee page could be retrieved: both "
                          "wynnlasvegas.com/resort-fee and wynnlasvegas.com/hotel/resort-fee.html return "
                          "'this page has checked out'. Flagged for review."),
         booking="https://www.wynnlasvegas.com/",
         parking="", parking_source="", cancel="", cancel_source="",
         quality_note=("On the same property as the Wynn poker room: the official WPT terms state the "
                       "poker room is 'located in Encore at Wynn Las Vegas'.")),
    dict(key="caesars", name="Caesars Palace", tier="Upper upscale", area="Strip - centre",
         room="Caesars Palace Poker Room", on_property=True,
         resort_fee=None, resort_fee_text="", resort_fee_source="",
         resort_fee_note=("The official resort-fee URL redirects to the general hotel page and does not "
                          "state a fee. Flagged for review."),
         booking="https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates&propCode=clv&roomCount=1&roomDetails=[{%22adults%22:2,%22children%22:0}]",
         address="3570 Las Vegas Blvd South, Las Vegas, NV 89109",
         address_source="https://www.caesars.com/caesars-palace/casino",
         parking="", parking_source="",
         cancel="FREE 48-Hour Cancellation (shown on the official booking widget)",
         cancel_source="https://www.caesars.com/caesars-palace/hotel",
         quality_note="On the same property as the Caesars Palace poker room (official casino page)."),
    dict(key="horseshoe", name="Horseshoe Las Vegas", tier="Upscale", area="Strip - centre",
         room="Hall of Fame Poker Room", on_property=True,
         resort_fee=None, resort_fee_text="", resort_fee_source="",
         resort_fee_note="No official resort-fee page was retrieved. Flagged for review.",
         booking="https://www.caesars.com/book/hotel-calendar?dateSearchFormat=flexible-dates&propCode=blv&roomCount=1&roomDetails=[{%22adults%22:2,%22children%22:0}]",
         address="3645 Las Vegas Blvd South, Las Vegas, NV 89109",
         address_source="https://www.caesars.com/horseshoe-las-vegas/casino",
         parking="", parking_source="",
         cancel="FREE 48-Hour Cancellation (shown on the official booking widget)",
         cancel_source="https://www.caesars.com/horseshoe-las-vegas/casino",
         quality_note="On the same property as the Hall of Fame Poker Room (official casino page)."),
    dict(key="resortsworld", name="Resorts World Las Vegas (Hilton / Conrad / Crockfords)", tier="Luxury",
         area="Strip - north", room="Resorts World Poker Room", on_property=True,
         resort_fee=55.0, resort_fee_text="$55 per room, per day (waived under the 'All Resort, No Fees' offer)",
         resort_fee_source="https://www.rwlasvegas.com/offers/all-resort-no-fees/",
         resort_fee_note=("Official offer terms: 'The daily resort fee of $55 per room, will be waived for "
                          "each night of your stay when booked under this offer. Standard room rate taxes "
                          "still apply and are not waived. An additional incidental deposit of $150 per room "
                          "will be required at check-in for each night of your stay.' Offer valid for travel "
                          "through 28 December 2026; blackout dates may apply."),
         booking=("https://reservations.rwlasvegas.com/ibe/shop.aspx?selectedTower=HILTON&hotelID=17726&"
                  "checkin={IN}&checkout={OUT}&nights=7&adults=2&children=0"),
         address="", address_source="",
         parking=("Self-parking is complimentary for Nevada residents with NV plates and for Genting "
                  "Rewards Elite, Prime, Monarch and Imperial tiers (official offer terms)."),
         parking_source="https://www.rwlasvegas.com/offers/all-resort-no-fees/",
         cancel="Reservations must be cancelled at least 48 hours before check-in for a refund of the deposit.",
         cancel_source="https://www.rwlasvegas.com/offers/all-resort-no-fees/",
         quality_note="Newest large resort on the north Strip. Poker room status: official site shows a poker-room section; no tournament schedule retrieved."),
]

TAX_RATE = 13.38
TAX_SOURCE = ("https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/"
              "original/as/pubhear-roomtax-ord-sb1d2.pdf")
TAX_NOTE = ("Clark County ordinance (Senate Bill 1, effective 1 March 2017), combined transient lodging tax "
            "schedule: 'Resort hotel within primary gaming corridor ... 13.38%'. Every Strip hotel in this "
            "table sits in the primary gaming corridor. Confirm the current schedule before relying on it.")

TRIP = dict(check_in="2026-12-06", check_out="2026-12-13", nights=7, adults=2, rooms=1,
            rationale=("Chosen automatically to sit inside the two officially-verified Strip series "
                       "(Venetian DeepStack Extravaganza IV, 16 Nov - 23 Dec 2026, and the WPT World "
                       "Championship festival at Wynn, 27 Nov - 21 Dec 2026) and to maximise the number of "
                       "Venetian events whose official structure sheet shows no re-entry, rebuy or add-on "
                       "text. 6-13 December carries 14 such entries, the highest of any 7-night window in "
                       "the series. Adjust it with the date filter; the whole site follows your choice."))


# --------------------------------------------------------------------------
# 6. Routes (hotel -> venue).  Only on-property pairs are verified.
# --------------------------------------------------------------------------
def maps_link(a, b):
    import urllib.parse
    return ("https://www.google.com/maps/dir/?api=1&origin=" + urllib.parse.quote(a) +
            "&destination=" + urllib.parse.quote(b) + "&travelmode=walking")


VENUE_FOR_ROUTE = {
    "venetian": ("The Venetian Resort Las Vegas", "The Venetian Resort Las Vegas poker room"),
    "wynn": ("Wynn Las Vegas", "Wynn Las Vegas poker room"),
    "caesars": ("Caesars Palace Las Vegas", "Caesars Palace Las Vegas poker room"),
    "horseshoe": ("Horseshoe Las Vegas", "Horseshoe Las Vegas poker room"),
    "resortsworld": ("Resorts World Las Vegas", "Resorts World Las Vegas poker room"),
    "southpoint": ("South Point Hotel Casino and Spa Las Vegas", "South Point poker room"),
}


def build_routes():
    rows = []
    for h in HOTELS:
        for vk, (vlabel, vroom) in VENUE_FOR_ROUTE.items():
            same = (h["key"] == vk)
            rows.append(dict(
                hotel=h["name"], hotel_key=h["key"], venue=vlabel, venue_key=vk,
                same_property=same,
                minutes=0 if same else None,
                verified=same,
                method=("On the same property: the poker room is inside the hotel. Verified from the "
                        "official pages linked on each row." if same else
                        "No official source states a walking time between these properties. "
                        "Left blank on purpose - open the route link and check it yourself."),
                maps=maps_link(h["name"], vlabel),
            ))
    return rows


# --------------------------------------------------------------------------
# 7. Flagged for review
# --------------------------------------------------------------------------
FLAGS = [
    ("F01", "Entry rules", "No Venetian structure sheet states a single-entry / freezeout limit",
     "All 37 official DSE IV structure sheets were read. None contains a one-entry, no-re-entry or freezeout statement. "
     "An event is therefore never labelled 'confirmed single-entry'.",
     SCHEDULE_PAGE),
    ("F02", "Entry rules", "Venetian multi-flight events allow more than one entry",
     "Events 01, 07, 19, 26, 47, 49, 56 and 59 have multiple starting flights, and each sheet carries the rule "
     "'Any player who bags chips for Day 2 may not play a subsequent flight', which only restricts a player who "
     "has bagged. They are listed as multi-entry, not single-entry.",
     SHEET.format(10)),
    ("F03", "Entry rules", "Events #18 and #58 reference 'subsequent buy in's'",
     "Structure sheet 8 (PokerAtlas Valuetown Bounty) states 'All subsequent buy in's after the initial buy in will be "
     "$200', which shows more than one buy-in per player is possible.",
     SHEET.format(8)),
    ("F04", "Entry rules", "Every WPT / Wynn event whose terms were read permits re-entry",
     "Unlimited re-entry (until level 9 or level 10) on the $600, $800, $1,100 PLO, $1,600, TORSE, HORSE, Mixed Triple Draw, "
     "Limit Omaha 8 and NLH Turbo events; the $1,100 WPT Prime Championship allows one entry plus one re-entry per flight.",
     WPT_TERMS),
    ("F05", "Source defect", "WPT schedule PDF date error: a block is labelled 'Dec. 18 Wednesday'",
     "The block sits between Tuesday 15 December and Thursday 17 December and is headed 'Dec. 18 Wednesday'. "
     "18 December 2026 is a Friday; the Wednesday of that week is 16 December. Those rows are dated 2026-12-16 here.",
     WPT_SCHEDULE),
    ("F06", "Source defect", "WPT continuation rows repeat the parent buy-in and guarantee",
     "The row 'Dec. 5 Saturday 11 a.m. No Limit Hold'em Day 2' shows $1,100 and $5,000,000, which are the Prime "
     "Championship's values, not a separate entry price. Continuation rows are marked as such and excluded from entry counts.",
     WPT_SCHEDULE),
    ("F07", "Coverage", "Wynn daily tournaments: suspension policy does not name the WPT series",
     "The official page says 'the Daily Tournament schedule will be suspended during each Wynn Signature, Wynn Millions, "
     "and Classic tournament series'. It does not say whether the WPT World Championship (27 Nov - 21 Dec 2026) suspends them.",
     WYNN_POKER),
    ("F08", "Hotels", "Wynn resort fee not verified",
     "wynnlasvegas.com/resort-fee and wynnlasvegas.com/hotel/resort-fee.html both return 'this page has checked out'. "
     "The Wynn resort-fee field is left blank.",
     "https://www.wynnlasvegas.com/casino/poker"),
    ("F09", "Hotels", "Caesars Palace and Horseshoe resort fees not verified",
     "The official resort-fee URLs redirect to the hotel landing pages and do not state a fee. Fields left blank.",
     "https://www.caesars.com/caesars-palace/hotel"),
    ("F10", "Coverage", "MGM Resorts rooms (Bellagio, MGM Grand, ARIA) not verified",
     "The official poker-room URLs and the MGM resort-fee URL return 'page not found'. No rows were invented for these rooms.",
     "https://bellagio.mgmresorts.com/en/casino/poker-room.html"),
    ("F11", "Coverage", "Horseshoe publishes no schedule",
     "The official casino page says the Hall of Fame Poker Room has 20 tables and '6 exciting tournament times daily' "
     "but links no schedule or structure sheet.",
     "https://www.caesars.com/horseshoe-las-vegas/casino"),
    ("F12", "Coverage", "South Point publishes its schedule as images only",
     "Times (10:10, 14:10, 18:10, 22:10) and buy-ins ($120, $300) come from the official page text. Guarantees, "
     "levels and entry rules are inside image files and were not read. South Point is also off-Strip and not walkable to it.",
     "https://southpointcasino.com/casino/poker-room"),
    ("F13", "Coverage", "Resorts World tournament schedule not retrieved",
     "The official site has a poker-room section under Gaming, but no schedule or structure sheet was retrieved.",
     "https://www.rwlasvegas.com/gaming/poker-room/"),
    ("F14", "Hotels", "No dated nightly room rate was captured",
     "Official booking engines are JavaScript applications; no date-specific rate could be read from an official source "
     "during this session. Every rate field is blank. Enter the rate you see on the official booking link and the site "
     "stores it as a dated log entry.",
     "https://www.venetianlasvegas.com/resort/resort-fee.html"),
    ("F15", "Routes", "Cross-property walking times are not published officially",
     "Only hotel-to-its-own-poker-room (0 minutes, same property) is verified. Every other pair is blank and carries a "
     "route link so you can check it yourself. No walking time is estimated or filled in.",
     "https://www.google.com/maps/dir/?api=1&origin=The+Venetian+Resort+Las+Vegas&destination=Wynn+Las+Vegas&travelmode=walking"),
    ("F16", "Data", "Some events have no guarantee on the official sheet",
     "Event #06 and the RaceDay Stack events #03, #04 and #05 state no guarantee on the structure sheet. The guarantee "
     "field is left blank rather than copied from the schedule text or inferred.",
     SHEET.format(29)),
    ("F17", "Data", "Per-flight differences inside one event number",
     "Event #01 has two sheets (Day A+C, 40-minute levels, registration closes ~3:40 PM; Day B+D, 30-minute levels, "
     "closes ~8:40 PM). Event #26 has three sheets (A+C+E 40 min; B+D 30 min; Day F Turbo 20 min). Rows point at their "
     "own sheet.", SHEET.format(10)),
    ("F18", "Resolved", "Event #40 was truncated in an earlier session's capture",
     "The official page row reads '$600 Pot Limit Omaha Bounty $25K GTD (1Day)' with structure sheet 27, which confirms "
     "event 40, $600 buy-in and a $25,000 guarantee. Resolved; no longer flagged as unknown.",
     SHEET.format(27)),
    ("F19", "Disagreement", "Earlier root pages claimed 31 confirmed single-entry events",
     "The 37-sheet audit behind this build found zero explicit single-entry statements, so the root pages were rebuilt. "
     "Earlier sessions' dashboards are preserved under their own folders and are not edited.",
     SHEET.format(1)),
    ("F20", "Tax", "13.38% verified against the Clark County ordinance, but the schedule may have changed",
     "The rate comes from the Clark County transient lodging ordinance (Senate Bill 1, effective 1 March 2017) table row "
     "'Resort hotel within primary gaming corridor ... 13.38%'. Confirm the current schedule before relying on it.",
     TAX_SOURCE),
    ("F21", "Coverage", "Not every WPT event's entry terms were read individually",
     "Terms were read for 13 distinct events in the official structures PDF. The rest are marked 'entry terms not read' "
     "rather than being copied from a sibling event.",
     WPT_TERMS),
    ("F22", "Coverage", "Caesars Palace daily flyer does not state which days it runs",
     "The official flyer gives four start times and buy-ins but no days of the week. Rows are shown as 'Daily' and flagged.",
     CAESARS_FLYER),
    ("F23", "Coverage", "Wynn daily tournaments: all four structures are re-entry, rebuy or add-on",
     "The official Wynn daily structures PDF states a re-entry fee for the $200 Monday-Thursday, $200 Saturday, "
     "$200 Sunday and $160 nightly events, plus unlimited $200 rebuys and a $100 add-on on the $240 Friday event. "
     "No Wynn daily tournament is a freezeout. All five are listed on the multi-entry page.",
     "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"),
    ("F24", "Coverage", "Wynn dailies may not run during the WPT World Championship",
     "The official page says dailies are suspended during Wynn Signature, Wynn Millions and Classic series. It does "
     "not say whether the WPT World Championship (27 Nov - 21 Dec 2026) suspends them. The structures PDF only says "
     "'may be suspended during Seniors Events, Classic Events, or other Tournament Series'.",
     "https://www.wynnlasvegas.com/casino/poker"),
    ("F25", "Source defect", "The Venetian series page still labels the WPT Fall Festival as the current series",
     "On 17 November 2026 the official page shows 'Current Series: WPT Fall Festival October 28 - November 15, 2026' "
     "while listing DeepStack Extravaganza IV (16 Nov - 23 Dec 2026) as the next series. The DSE IV rows are used "
     "because they are the current window; the label on the official page lags.",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"),
    ("F26", "Coverage", "Horseshoe and Resorts World publish no poker schedule at all",
     "Horseshoe's official casino page says the Hall of Fame Poker Room has 20 tables and '6 exciting tournament "
     "times daily' but links no schedule. A guessed Caesars content-dam URL for a Horseshoe flyer returned an empty "
     "document. Resorts World's site has a poker-room section under Gaming with no schedule. No rows invented.",
     "https://www.caesars.com/horseshoe-las-vegas/casino"),
    ("F27", "Routes", "Venetian poker room is in The Palazzo, not The Venetian tower",
     "The official poker-room page states the room is at The Palazzo on level 2 of Grand Canal Shoppes, reached from "
     "The Venetian lobby via the Waterfall Atrium escalator. Allow indoor walking time if you stay in the Venetian "
     "tower, and note the room is a long inside walk from the Strip entrance.",
     "https://www.venetianlasvegas.com/resort/casino/poker.html"),
]


# --------------------------------------------------------------------------
# 8. Open questions: what we have, what is missing, how to close it
# --------------------------------------------------------------------------
QUESTIONS = [
    dict(id="Q01", q="What are your exact trip dates and your nightly budget / quality floor?",
         have=("A default window of 6-13 December 2026 is set and every page follows it. It was chosen to sit inside "
               "both verified Strip series and to maximise the number of Venetian events with no re-entry text."),
         missing="Your real dates, your nightly budget ceiling and the minimum hotel quality you will accept.",
         how=("Change the dates with the date filter on any table, or read the 'How the default window was chosen' "
              "block on the Trip planner page. Nothing else on the site has to be re-entered.")),
    dict(id="Q02", q="Is any DSE IV event actually a freezeout?",
         have="All 37 official structure sheets read; none states a one-entry limit.",
         missing="An official statement of the entry cap for the events whose sheets are silent.",
         how=("Ask the Venetian poker cage / tournament desk to confirm the re-entry policy for a specific event number, "
              "or check the printed structure sheet posted in the room on the day. Until then the row stays 'unverified' "
              "and is never promoted to single-entry.")),
    dict(id="Q03", q="What is the true nightly hotel cost for your dates?",
         have=("Resort fees: Venetian $55 + tax (official), Resorts World $55 per room per day (official, waived on the "
               "'All Resort, No Fees' offer through 28 Dec 2026). Tax: 13.38% (Clark County ordinance)."),
         missing="The nightly room rate itself, parking charges, and each hotel's cancellation deadline for your dates.",
         how=("Open the official booking link on the Hotels page for your dates, read the itemised total on the checkout "
              "screen (room, resort fee, tax, parking) and paste the figures into the rate log. The log keeps each entry "
              "dated and computes true cost/night = rate + resort fee + tax.")),
    dict(id="Q04", q="Is the walk from your hotel to the poker room under 30 minutes?",
         have="On-property pairs are 0 minutes and verified from official pages.",
         missing="Every cross-property walking time. No official source publishes one.",
         how="Open the route link on the Routes page (Google Maps walking directions) and time it yourself, or ask the hotel. The 30-minute filter works on what you record."),
    dict(id="Q05", q="Can two events on the same day actually be played back to back?",
         have=("Official start times, official level lengths, official late-registration close times, and the rule that "
               "each Day 1 plays down to about 12.5% of the field."),
         missing="Finish times. No official source states when an event ends.",
         how=("The schedule page gives each day a primary event and a conditional fallback, and marks overlap using the "
              "structure clock rather than a guessed finish time. Confirm the day's plan at the desk on the morning.")),
    dict(id="Q06", q="Do the Wynn daily tournaments run during the WPT World Championship?",
         have="The official page says dailies are suspended during Wynn Signature, Wynn Millions and Classic series.",
         missing="Whether the WPT World Championship festival (27 Nov - 21 Dec 2026) also suspends them.",
         how="Call the Wynn poker room on (702) 770-7654 (printed on the official schedule PDF) or check wynnpoker.com."),
    dict(id="Q07", q="Are the MGM Resorts rooms (Bellagio, MGM Grand, ARIA) running tournaments in this window?",
         have="Nothing. The official poker-room URLs returned 'page not found' during this session.",
         missing="Any official schedule or structure for those rooms.",
         how=("Search each property's own site for its poker room and its tournament calendar, then add the source to the "
              "Sources page. No rows were invented for these rooms.")),
    dict(id="Q08", q="What is the entry fee split and the real cost of an entry?",
         have="House fee and prize-pool contribution for every Venetian event, straight from each structure sheet.",
         missing="The equivalent split for WPT events not individually read, and for the Caesars daily.",
         how="Read the 'Entry Fee' line on the official structure sheet for the event. The Tournaments page shows the split where it was published."),
    dict(id="Q09", q="How many entries should the trip budget for?",
         have="Buy-in for every verified row, plus a calculator for entries x buy-ins + nights x true hotel cost.",
         missing="Your bankroll and your appetite for re-entry (which multiplies the cost of a multi-entry event).",
         how="Set the number of entries per event on the Trip planner page; it prices single-entry and multi-entry plans side by side."),
    dict(id="Q10", q="Are the guarantees in this table comparable to each other?",
         have="Each guarantee exactly as the official sheet states it, including whether bounties are inside it.",
         missing="A like-for-like comparison where one room counts bounties in the guarantee and another does not.",
         how="The ratio column (guarantee / entry fee) is labelled descriptive, not a forecast, and bounty and flight events are labelled separately. Compare only within a format."),
]


# --------------------------------------------------------------------------
# 9. Suggestions (choose a path before anything is changed)
# --------------------------------------------------------------------------
SUGGESTIONS = [
    dict(id="S01", title="Put a one-line entry rule on every table row",
         problem="A reader cannot tell at a glance whether an event is a freezeout, a re-entry or simply unknown.",
         options=["Keep the three-way label (confirmed / multi-entry / unverified)",
                  "Add a plain-English sentence per row ('You may buy in again until 4:55 PM')",
                  "Add a colour-coded badge and drop the text"],
         effect="The second option costs one more column and removes most misreads. It does not change any data."),
    dict(id="S02", title="Ask the poker rooms for a written single-entry statement",
         problem="Silence on a structure sheet is not a one-entry promise, so nothing can be confirmed as a freezeout.",
         options=["Email each room's tournament desk and publish the reply with a date",
                  "Photograph the printed structure sheet in the room on the day",
                  "Leave the rows unverified and plan around them"],
         effect="Only the first two can move an event from unverified to confirmed. Until then a freezeout plan is an assumption."),
    dict(id="S03", title="Capture dated hotel quotes instead of a single number",
         problem="Room rates move daily; a single figure goes stale and the true nightly cost with it.",
         options=["Keep the dated rate log and paste a new quote each time you check",
                  "Add a screenshot field per log entry",
                  "Show only the resort fee and tax, which are stable"],
         effect="The log is the only option that keeps a like-for-like history. Screenshots make disputes resolvable."),
    dict(id="S04", title="Time the walks yourself and record them",
         problem="No official source publishes hotel-to-poker-room walking times, so the 30-minute filter is nearly empty.",
         options=["Record the walking time you measure and store it with a date",
                  "Only accept on-property hotels until a walk is measured",
                  "Accept a third-party routing estimate and label it as an estimate"],
         effect="The first option makes the filter useful and stays honest. The third fills the table but is not an official value."),
    dict(id="S05", title="Run the official-source check every morning, not once a day at random",
         problem="Schedules, structures and fees change without notice.",
         options=["GitHub Actions cron at 13:00 UTC (6 AM Las Vegas) every day",
                  "Twice daily (06:00 and 18:00 Las Vegas)",
                  "Weekly"],
         effect="A morning run matches the brief's 'pull the schedule each morning'. Twice daily catches intraday changes at double the Actions minutes."),
    dict(id="S06", title="Publish one site instead of thirteen session dashboards",
         problem="Earlier sessions each left a dashboard in its own folder; the same question has several different answers.",
         options=["Keep this root site as the single answer and demote the rest to an archive index",
                  "Keep every dashboard and add a comparison page",
                  "Delete the older dashboards"],
         effect="The first option gives one answer per question and keeps earlier work reachable. Deleting loses source history."),
    dict(id="S07", title="Price a plan that assumes one entry, and one that assumes re-entry",
         problem="A multi-entry event can cost two, three or more buy-ins; a plan that assumes one entry understates the cost badly.",
         options=["Show both totals side by side on the planner",
                  "Show only the single-entry total",
                  "Show a range with no assumptions stated"],
         effect="Side-by-side totals make the downside visible before you commit money."),
    dict(id="S08", title="Reconfirm everything before any non-refundable payment",
         problem="Every value here is a snapshot from an official page on 2026-11-17.",
         options=["Re-run the source check and read the change log before booking",
                  "Call the room and the hotel to confirm",
                  "Book a refundable rate only"],
         effect="Refundable rates are the cheapest insurance; Caesars and Horseshoe advertise free 48-hour cancellation and Resorts World requires 48 hours' notice for a deposit refund."),
]


# --------------------------------------------------------------------------
# write
# --------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    ven = build_venetian()
    wpt = build_wpt()
    oth = build_other()
    data = dict(
        retrieved=RETRIEVED,
        schedule_page=SCHEDULE_PAGE,
        venetian=ven,
        wpt=wpt,
        other=oth,
        venues=VENUES,
        hotels=HOTELS,
        routes=build_routes(),
        flags=[dict(id=i, area=a, title=t, detail=d, source=s) for i, a, t, d, s in FLAGS],
        questions=QUESTIONS,
        suggestions=SUGGESTIONS,
        tax=dict(rate=TAX_RATE, source=TAX_SOURCE, note=TAX_NOTE),
        trip=TRIP,
        sheets=dict((str(k), dict(v, url=SHEET.format(k))) for k, v in SHEETS.items()),
    )
    for name, obj in (("venetian.json", ven), ("wpt.json", wpt), ("other.json", oth),
                      ("venues.json", VENUES), ("hotels.json", HOTELS),
                      ("routes.json", data["routes"]), ("flags.json", data["flags"]),
                      ("questions.json", QUESTIONS), ("suggestions.json", SUGGESTIONS),
                      ("meta.json", dict(retrieved=RETRIEVED, tax=data["tax"], trip=TRIP,
                                         schedule_page=SCHEDULE_PAGE,
                                         sheets=data["sheets"])),
                      ("all.json", data)):
        with open(os.path.join(OUT, name), "w") as fh:
            json.dump(obj, fh, indent=1, sort_keys=False)
    print("rows: venetian=%d wynn/wpt=%d other=%d routes=%d flags=%d" %
          (len(ven), len(wpt), len(oth), len(data["routes"]), len(data["flags"])))


if __name__ == "__main__":
    main()
