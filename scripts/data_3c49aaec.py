"""Verified datasets for the Poker5 root site (session 3c49aaec, 2026-11-17).

Every value below was read from the official source linked next to it on
2026-11-17 (UTC). Where an official source does not state a value the field is
None / "" and the row is flagged - nothing is inferred.

Sources are the Venetian DeepStack Extravaganza IV schedule page and its 37
structure sheets, the Wynn/WPT World Championship schedule and structures PDFs,
the Wynn daily-tournament structures PDF, each property's official resort-fee or
terms page, and the Clark County transient-lodging tax ordinance.
"""

RETRIEVED = "2026-11-17"

DSE_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
           "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
SHEET_URL = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/"
             "deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf")

BAG_LIMIT = ("Any player who bags chips for Day 2 may not play a subsequent flight.")
NO_LIMIT_SENTENCE = ("Sheet read in full: it states the buy-in split, starting stack, "
                     "level length, late-registration close and payout percentage, but it "
                     "contains no sentence about single entry, re-entry, rebuys or add-ons. "
                     "Silence is not a rule, so single-entry is NOT confirmed.")

# sheet number -> facts transcribed from that structure sheet (all fetched 2026-11-17).
# fee entries are (buy_in, house_fee_withheld, prize_pool_portion, note).
SHEETS = {
    1: dict(events=[9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64],
            title="$200 No Limit Hold'em Bounty (1Day)", start="17:10", stack=25000,
            level=30, late_reg="8 levels + Break (9:40 PM)", late_reg_close="21:40",
            gtd=8000, gtd_note="prize pool + total bounties", payout="pays 12.5% of the field",
            fee=[(200, 40, 160, "")], bounty="$50 per elimination",
            entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    2: dict(events=[7], title="$400 No Limit Hold'em Day A+B 11:10 AM, Day 2 11:00 AM",
            start="11:10", stack=40000, level=40, late_reg="9 levels + Break (5:55 PM)",
            late_reg_close="17:55", gtd=75000, gtd_note="", payout="each flight plays to ~12.5% of the field",
            fee=[(400, 70, 330, "")], bounty=None, entry_rule=BAG_LIMIT,
            excerpt="Rule 03: each starting flight plays to ~12.5% of the field; Day 2 combines 1A and 1B. "
                    "Rule 08: " + BAG_LIMIT + " No re-entry/add-on sentence."),
    3: dict(events=[19], title="$400 No Limit Hold'em Day A+B+C 11:10 AM, Day 2 11:00 AM",
            start="11:10", stack=40000, level=40, late_reg="9 levels + Break (5:55 PM)",
            late_reg_close="17:55", gtd=75000, gtd_note="", payout="each flight plays to ~12.5% of the field",
            fee=[(400, 70, 330, "")], bounty=None, entry_rule=BAG_LIMIT,
            excerpt="Rule 03 combines 1A, 1B and 1C on Day 2. Rule 08: " + BAG_LIMIT +
                    " No re-entry/add-on sentence."),
    4: dict(events=[59], title="$600 No Limit Hold'em Day A+B+C 11:10 AM, Day 2 11:00 AM",
            start="11:10", stack=40000, level=40, late_reg="9 levels + Break (5:55 PM)",
            late_reg_close="17:55", gtd=150000, gtd_note="", payout="each flight plays to ~12.5% of the field",
            fee=[(600, 95, 505, "Day 1A only: $20 fee discount for pre-start registrants, total buy-in $580")],
            bounty=None, entry_rule=BAG_LIMIT,
            excerpt="Rule 07: $95 of the $600 is withheld for house fees; on Day 1A only, pre-start "
                    "registrants get a $20 fee discount ($580 instead of $600). Rule 08: " + BAG_LIMIT),
    5: dict(events=[2, 12], title="$300 No Limit Hold'em (1Day)", start="11:10", stack=40000,
            level=30, late_reg="10 levels + Break (~4:55 PM)", late_reg_close="16:55",
            gtd=10000, gtd_note="", payout="pays 12.5% of the field",
            fee=[(300, 58, 242, "")], bounty=None, entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    6: dict(events=[10], title="$400 No Limit Hold'em (1Day)", start="11:10", stack=40000,
            level=30, late_reg="10 levels + Break (~4:55 PM)", late_reg_close="16:55",
            gtd=15000, gtd_note="", payout="pays 12.5% of the field",
            fee=[(400, 65, 335, "")], bounty=None, entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    7: dict(events=[14, 28, 63], title="$600 No Limit Hold'em (1Day)", start="11:10", stack=40000,
            level=30, late_reg="10 levels + Break (~4:55 PM)", late_reg_close="16:55",
            gtd=None, gtd_note="sheet states $30,000 for Events #14 and #63 and $40,000 for Event #28",
            payout="pays 12.5% of the field", fee=[(600, 90, 510, "")], bounty=None,
            entry_rule=None, excerpt=NO_LIMIT_SENTENCE,
            gtd_by_event={14: 30000, 28: 40000, 63: 30000}),
    8: dict(events=[18, 58], title="$200 No Limit Hold'em Valuetown Bounty (1Day) - PokerAtlas PRO $20 rake discount",
            start="17:10", stack=25000, level=30, late_reg="8 levels + Break (9:40 PM)",
            late_reg_close="21:40", gtd=20000, gtd_note="prize pool + total bounties",
            payout="pays 12.5% of the field",
            fee=[(200, 40, 160, "PokerAtlas PRO members: $20 off the INITIAL $200 buy-in ($180 total); "
                                "'All subsequent buy in's after the initial buy in will be $200'")],
            bounty="$50 per elimination", entry_rule=None,
            excerpt="Rule 07 caps the member discount at the initial entry and prices every later entry at "
                     "$200, i.e. extra money buys extra attempts. No single-entry sentence."),
    9: dict(events=[1], title="$300 No Limit Hold'em Day B+D 5:10 PM, Day 2 12:00 PM", start="17:10",
            stack=30000, level=30, late_reg="6 levels + Break (~8:40 PM)", late_reg_close="20:40",
            gtd=75000, gtd_note="", payout="each flight plays to ~12.5% of the field",
            fee=[(300, 60, 240, "")], bounty=None, entry_rule=BAG_LIMIT,
            excerpt="Sheet for flights 1B and 1D. Rule 08: " + BAG_LIMIT +
                    " Footer: 'SEE OTHER STRUCTURE SHEET FOR DAYS A+C'."),
    10: dict(events=[1], title="$300 No Limit Hold'em Day A+C 11:10 AM, Day 2 12:00 PM", start="11:10",
             stack=30000, level=40, late_reg="6 levels + Break (~3:40 PM)", late_reg_close="15:40",
             gtd=75000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(300, 60, 240, "")], bounty=None, entry_rule=BAG_LIMIT,
             excerpt="Sheet for flights 1A and 1C; 40-minute levels and a 3:40 PM registration close, i.e. "
                     "the two sheet families differ by design (this resolves the old 'event 01 on two sheets "
                     "with different times' flag). Rule 08: " + BAG_LIMIT),
    11: dict(events=[16, 30, 54], title="$600 No Limit Hold'em Bounty (1Day)", start="11:10",
             stack=40000, level=30, late_reg="10 levels + Break (4:55 PM)", late_reg_close="16:55",
             gtd=None, gtd_note="prize pool + total bounties: $30,000 (#16), $40,000 (#30), $50,000 (#54)",
             payout="pays 12.5% of the field", fee=[(600, 90, 510, "")],
             bounty="$200 per elimination, $500 once in the money; the winner keeps their own bounty",
             entry_rule=None, excerpt=NO_LIMIT_SENTENCE,
             gtd_by_event={16: 30000, 30: 40000, 54: 50000}),
    12: dict(events=[26], title="$800 No Limit Hold'em Day A+C+E 11:10 AM, Day 2 12:00 PM", start="11:10",
             stack=40000, level=40, late_reg="6 levels + Break (~3:40 PM)", late_reg_close="15:40",
             gtd=500000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(800, 110, 690, "")], bounty=None, entry_rule=BAG_LIMIT,
             excerpt="Rule 08: " + BAG_LIMIT + " Footer says 'SEE OTHER STRUCTURE SHEET FOR DAYS B+D+F' "
                     "while the sheet title lists A+C+E; the sheet family for 1F is #14 (Turbo) - "
                     "cross-reference inconsistency flagged."),
    13: dict(events=[26], title="$800 No Limit Hold'em Day B+D 5:10 PM, Day 2 12:00 PM", start="17:10",
             stack=40000, level=30, late_reg="6 levels + Break (~8:40 PM)", late_reg_close="20:40",
             gtd=500000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(800, 110, 690, "")], bounty=None, entry_rule=BAG_LIMIT,
             excerpt="Rule 08: " + BAG_LIMIT + " Footer says 'SEE OTHER STRUCTURE SHEET FOR DAYS A+C+F' "
                     "but 1E is on sheet 12 - cross-reference inconsistency flagged."),
    14: dict(events=[26], title="$800 No Limit Hold'em Day F (Turbo) 5:10 PM, Day 2 12:00 PM", start="17:10",
             stack=40000, level=20, late_reg="6 levels + Break (~7:25 PM)", late_reg_close="19:25",
             gtd=500000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(800, 110, 690, "")], bounty=None, entry_rule=BAG_LIMIT,
             excerpt="Turbo flight: 20-minute levels, registration closes ~7:25 PM. Rule 08: " + BAG_LIMIT),
    15: dict(events=[29, 31, 34, 38, 42, 50, 51, 53, 55], title="$300 No Limit Hold'em Bounty (1Day)",
             start="17:10", stack=25000, level=30, late_reg="8 levels + Break (9:40 PM)",
             late_reg_close="21:40", gtd=15000, gtd_note="prize pool + total bounties",
             payout="pays 12.5% of the field", fee=[(300, 50, 250, "")], bounty="$100 per elimination",
             entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    16: dict(events=[36], title="$800 No Limit Hold'em Bounty (1Day)", start="11:10", stack=40000,
             level=30, late_reg="10 levels + Break (4:55 PM)", late_reg_close="16:55",
             gtd=75000, gtd_note="prize pool + total bounties", payout="pays 12.5% of the field",
             fee=[(800, 100, 700, "")],
             bounty="$200 per elimination, $500 once in the money; the winner keeps their own bounty",
             entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    17: dict(events=[24, 32], title="$600 No Limit Hold'em Seniors (1Day) - 50+ only", start="10:10",
             stack=40000, level=30, late_reg="10 levels + Break (~3:55 PM)", late_reg_close="15:55",
             gtd=40000, gtd_note="", payout="pays 15% of the field", fee=[(600, 90, 510, "")],
             bounty=None, entry_rule=None,
             excerpt=NO_LIMIT_SENTENCE + " Rule 02 adds: a player who buys in without being 50+ is not "
                     "entitled to prize money or a refund."),
    18: dict(events=[3, 4, 5], title="$200 No Limit Hold'em RaceDay Stack (1Day)", start="10:10",
             stack=30000, level="20/15", late_reg="6 levels + Break (~12:25 PM)", late_reg_close="12:25",
             gtd=None, gtd_note="the sheet prints no guarantee line", payout="pays 12.5% of the field",
             fee=[(200, 35, 165, "")], bounty=None, entry_rule=None,
             excerpt=NO_LIMIT_SENTENCE + " No guarantee is published for this event."),
    19: dict(events=[33, 37], title="$100 NLH LIPS Ladies (1Day) Milestone Satellite to Event #39",
             start="16:10", stack=20000, level=20, late_reg="6 levels + Break (~6:25 PM)",
             late_reg_close="18:25", gtd=None, gtd_note="Guarantee: 2 Seats (tournament entry, not cash)",
             payout="winners receive direct entry to Event #39 plus odd money",
             fee=[(100, 20, 80, "")], bounty=None, entry_rule=None,
             excerpt="Milestone rule: a player who reaches 200,000 chips gets the seat and stops playing. "
                     "Open to female players 21+. No entry-limit sentence."),
    20: dict(events=[49], title="$1,100 No Limit Hold'em Seniors Day A+B 10:10 AM, Day 2 10:00 AM (50+)",
             start="10:10", stack=40000, level=40, late_reg="9 levels + Break (~4:55 PM)",
             late_reg_close="16:55", gtd=300000, gtd_note="", payout="each flight plays to ~15% of the field",
             fee=[(1100, 140, 960, "")], bounty=None, entry_rule=BAG_LIMIT,
             excerpt="Rule 08: " + BAG_LIMIT + " Rule 02: non-50+ entrants forfeit prize money and refund."),
    21: dict(events=[47], title="$2,200 No Limit Hold'em PokerAtlas Championship Day 1A 10:10 AM, "
                               "Day 2 1:00 PM, Day 3 11:00 AM",
             start="10:10", stack=40000, level=40, late_reg="9 levels + Break (~4:55 PM)",
             late_reg_close="16:55", gtd=1000000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(2200, 225, 1975, "")], bounty=None, entry_rule=BAG_LIMIT,
             excerpt="Day 2 plays down to seven players; Day 3 is the streamed PokerGO final table. "
                     "Rule 08: " + BAG_LIMIT),
    22: dict(events=[20], title="$300 Pot Limit Omaha Double Board Bomb Pot (1Day)", start="12:10",
             stack=30000, level=30, late_reg="8 levels + break (~4:40 PM)", late_reg_close="16:40",
             gtd=10000, gtd_note="", payout="plays 8-handed, pays 12.5% of the field",
             fee=[(300, 58, 242, "")], bounty=None, entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    23: dict(events=[57], title="$600 Pot Limit Omaha Double Board Bomb Pot (1Day)", start="12:10",
             stack=30000, level=30, late_reg="8 levels + break (~4:40 PM)", late_reg_close="16:40",
             gtd=25000, gtd_note="", payout="plays 8-handed, pays 12.5% of the field",
             fee=[(600, 90, 510, "")], bounty=None, entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    24: dict(events=[41, 44], title="$260 NLH (1Day) Milestone Satellite to Event #47", start="16:10",
             stack=20000, level=20, late_reg="6 levels + Break (~6:25 PM)", late_reg_close="18:25",
             gtd=None, gtd_note="Guarantee: 2 Seats (tournament entry, not cash)",
             payout="winners receive direct entry to Event #47 plus odd money",
             fee=[(260, 40, 220, "")], bounty=None, entry_rule=None,
             excerpt="Milestone 200,000 chips awards the seat and removes the player from play. "
                     "No entry-limit sentence."),
    25: dict(events=[45, 46, 48], title="$260 NLH Turbo (1Day) Milestone Satellite to Event #47",
             start="varies by flight", stack=20000, level=15,
             late_reg="6 levels (sheet prints no clock time)", late_reg_close=None,
             gtd=None, gtd_note="Guarantee: 2 Seats (tournament entry, not cash)",
             payout="winners receive direct entry to Event #47 plus odd money",
             fee=[(260, 35, 225, "")], bounty=None, entry_rule=None,
             excerpt="Sheet gives three start times: #45 8:10 PM, #46 9:10 AM, #48 12:10 PM. "
                     "Late registration is '6 levels' with no clock time, so the cutoff is not verified. "
                     "No entry-limit sentence."),
    26: dict(events=[17], title="$400 Pot Limit Omaha Bounty (1Day)", start="12:10", stack=30000,
             level=30, late_reg="8 levels + break (~4:40 PM)", late_reg_close="16:40",
             gtd=15000, gtd_note="prize pool + total bounties", payout="plays 8-handed, pays 12.5% of the field",
             fee=[(400, 60, 340, "")], bounty="$100 per elimination; the winner keeps their own bounty",
             entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    27: dict(events=[40], title="$600 Pot Limit Omaha Bounty (1Day)", start="12:10", stack=30000,
             level=30, late_reg="8 levels + break (~4:40 PM)", late_reg_close="16:40",
             gtd=25000, gtd_note="prize pool + total bounties", payout="plays 8-handed, pays 12.5% of the field",
             fee=[(600, 90, 510, "")], bounty="$200 per elimination; the winner keeps their own bounty",
             entry_rule=None,
             excerpt=NO_LIMIT_SENTENCE + " This sheet is also the source that re-established the Event #40 "
                     "row (Thu Dec 10, 12:10 PM, $600 PLO Bounty, $25K GTD), truncated in an earlier capture."),
    28: dict(events=[27], title="$600 BIG O (1Day)", start="12:10", stack=30000, level=30,
             late_reg="8 levels + break (~4:40 PM)", late_reg_close="16:40", gtd=25000, gtd_note="",
             payout="plays 8-handed, pays 12.5% of the field", fee=[(600, 90, 510, "")], bounty=None,
             entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    29: dict(events=[6], title="$200 No Limit Hold'em (1Day)", start="11:10", stack=30000, level=30,
             late_reg="8 levels + Break (~3:40 PM)", late_reg_close="15:40", gtd=None,
             gtd_note="the sheet prints no guarantee line", payout="pays 12.5% of the field",
             fee=[(200, 40, 160, "")], bounty=None, entry_rule=None,
             excerpt=NO_LIMIT_SENTENCE + " No guarantee is published for this event."),
    30: dict(events=[8], title="$200 No Limit Hold'em (1Day) Progressive Knock-Out Bounty (PKO)",
             start="17:10", stack=25000, level=30, late_reg="8 levels + Break (9:40 PM)",
             late_reg_close="21:40", gtd=8000, gtd_note="prize pool + total bounties",
             payout="pays 12.5% of the field", fee=[(200, 40, 160, "")],
             bounty="PKO: every player starts as a $50 bounty; half of a captured bounty is kept, half is added "
                    "to the captor's own bounty",
             entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    31: dict(events=[35], title="$600 No Limit Hold'em (1Day) LIPS Poker Jingle Tag Team", start="10:10",
             stack=40000, level=30, late_reg="8 levels + Break (~2:40 PM)", late_reg_close="14:40",
             gtd=10000, gtd_note="", payout="pays 12.5% of the field",
             fee=[(600, 90, 510, "$80 house fees + $10 flat LIPS fee")], bounty=None,
             entry_rule=None,
             excerpt="Teams of two (female/female or female/male) rotate every level; failing to switch is a "
                     "disqualification. No entry-limit sentence."),
    32: dict(events=[39], title="$800 NLH LIPS Ladies (2Day) Women in Poker Main Event; Day 1 Dec 10 "
                               "10:10 AM, Day 2 Dec 11 10:00 AM, final table ~7:00 PM",
             start="10:10", stack=40000, level=40, late_reg="9 levels + Break (~4:55 PM)",
             late_reg_close="16:55", gtd=40000, gtd_note="", payout="Day 1 plays to ~12.5% of the field; "
                               "Day 2 is in the money and plays down to seven for the streamed final table",
             fee=[(800, 110, 690, "$90 house fees + $20 flat LIPS fee")], bounty=None, entry_rule=None,
             excerpt="Female players 21+ only. The sheet has no 'bags chips may not play another flight' rule "
                     "because Event #39 has a single Day 1; it also states no re-entry or add-on rule, so "
                     "single-entry is still NOT confirmed."),
    33: dict(events=[43], title="$600 No Limit Hold'em LIPS (1Day) Kings and Queens Bounty - open to all players",
             start="11:10", stack=40000, level=30, late_reg="10 levels + Break (4:55 PM)",
             late_reg_close="16:55", gtd=30000, gtd_note="prize pool + total bounties",
             payout="pays 12.5% of the field", fee=[(600, 90, 510, "$80 house fees + $10 flat LIPS fee")],
             bounty="$200 per elimination; the winner keeps their own bounty", entry_rule=None,
             excerpt=NO_LIMIT_SENTENCE),
    34: dict(events=[52], title="$1,100 No Limit Hold'em (1Day) Progressive Knock-Out Bounty (PKO)",
             start="11:10", stack=40000, level=30, late_reg="10 levels + Break (4:55 PM)",
             late_reg_close="16:55", gtd=75000, gtd_note="prize pool + total bounties",
             payout="pays 12.5% of the field", fee=[(1100, 130, 970, "")],
             bounty="PKO: every player starts as a $200 bounty; half kept, half carried",
             entry_rule=None, excerpt=NO_LIMIT_SENTENCE),
    35: dict(events=[56], title="$1,100 No Limit Hold'em Day A+C+E 10:10 AM, Day 2 11:00 AM",
             start="10:10", stack=40000, level=40, late_reg="9 levels + Break (~4:55 PM)",
             late_reg_close="16:55", gtd=500000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(1100, 140, 960, "Day 1A only: $40 fee discount for pre-start registrants, total buy-in $1,060")],
             bounty=None, entry_rule=BAG_LIMIT, excerpt="Rule 07 documents the Day 1A $40 discount. "
                     "Rule 08: " + BAG_LIMIT),
    36: dict(events=[56], title="$1,100 No Limit Hold'em Day B+D 6:10 PM, Day 2 11:00 AM", start="18:10",
             stack=40000, level=30, late_reg="9 levels + Break (~11:10 PM)", late_reg_close="23:10",
             gtd=500000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(1100, 140, 960, "Day 1B only: $40 fee discount for pre-start registrants, total buy-in $1,060")],
             bounty=None, entry_rule=BAG_LIMIT, excerpt="Rule 07 documents the Day 1B $40 discount. "
                     "Rule 08: " + BAG_LIMIT),
    37: dict(events=[47], title="$2,200 No Limit Hold'em PokerAtlas Championship Day 1B 6:10 PM, "
                               "Day 2 1:00 PM, Day 3 11:00 AM",
             start="18:10", stack=40000, level=30, late_reg="9 levels + Break (~11:10 PM)",
             late_reg_close="23:10", gtd=1000000, gtd_note="", payout="each flight plays to ~12.5% of the field",
             fee=[(2200, 225, 1975, "")], bounty=None, entry_rule=BAG_LIMIT,
             excerpt="Rule 08: " + BAG_LIMIT),
}

MULTI_FLIGHT_EVENTS = {1, 7, 19, 26, 47, 49, 56}   # events with more than one Day 1 flight
SATELLITE_EVENTS = {33, 37, 41, 44, 45, 46, 48}     # pay seats, not cash prizes
BANNER_MULTI_EVENTS = MULTI_FLIGHT_EVENTS           # bag-limit rule -> money buys more attempts

# ---------------------------------------------------------------- Wynn / WPT ---
WPT_SCHEDULE_URL = ("https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/"
                    "Poker/WPT/WPT_World_Championship_Schedule.pdf")
WPT_STRUCTURES_URL = ("https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/"
                      "Poker/WPT/WPT_World_Championship_Structures.pdf")
WPT_DAILY_STRUCTURES_URL = ("https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/"
                            "Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf")
WYNN_POKER_URL = "https://www.wynnlasvegas.com/casino/poker"

UNLIMITED = "Unlimited re-entry will be available until the start of level 9"
UNLIMITED_10 = "Unlimited re-entry will be available until the start of level 10"
FLIGHT_RULE = ("Unlimited re-entry for each starting flight ... until the start of level 9. "
               "A player who advances to Day 2 is prohibited from entering a subsequent starting flight.")

WPT_TERMS = [
    dict(name="$600 No Limit Hold'em ($400,000 GTD)", dates="Nov 27-30, 2026 (Day 1A-1F) + Day 2 Nov 30",
         buyin=600, gtd=400000, split="$510 prize pool + $65 tournament fee + $25 poker staff service charge",
         stack=40000, registration=FLIGHT_RULE, level="30 min (1F: 20 min)", tables="9-handed"),
    dict(name="$600 TORSE", dates="Nov 27, 2026 12:00 PM", buyin=600, gtd=None,
         split="$510 + $65 + $25", stack=35000, registration=UNLIMITED,
         level="30 min", tables="6-handed; final table 7-handed"),
    dict(name="$400 PLO", dates="Nov 27, 2026 1:00 PM", buyin=400, gtd=None,
         split="$337 + $45 + $18", stack=30000,
         registration=UNLIMITED + " (approximately 5:30 p.m.)", level="30 min",
         tables="8-handed; final table 9-handed"),
    dict(name="$600 Mixed Triple Draw (A-5, 2-7, Badugi)", dates="Nov 28 and Dec 20, 2026", buyin=600,
         gtd=None, split="$510 + $65 + $25", stack=35000, registration=UNLIMITED,
         level="30 min", tables="6-handed; final table 7-handed"),
    dict(name="$800 No Limit Hold'em ($1,000,000 GTD)", dates="Nov 30 - Dec 4, 2026 (Day 1A-1F, Day 2, final table)",
         buyin=800, gtd=1000000, split="$695 + $72 + $33", stack=40000, registration=FLIGHT_RULE,
         level="30 min (1F: 20 min)", tables="9-handed"),
    dict(name="$600 Limit Omaha 8", dates="Nov 30, 2026 12:00 PM", buyin=600, gtd=None,
         split="$510 + $65 + $25", stack=35000, registration=UNLIMITED, level="30 min",
         tables="8-handed; final table 9-handed"),
    dict(name="$600 Limit Omaha 8 / Stud 8", dates="Dec 1, 2026 12:00 PM", buyin=600, gtd=None,
         split="$510 + $65 + $25", stack=35000, registration=UNLIMITED, level="30 min",
         tables="8-handed; final table 9-handed"),
    dict(name="$1,100 PLO", dates="Dec 1, 2026 1:00 PM", buyin=1100, gtd=None,
         split="$975 + $85 + $45", stack=30000,
         registration=UNLIMITED + " (approximately 5:30 p.m.)", level="30 min",
         tables="8-handed; final table 9-handed"),
    dict(name="$1,600 No Limit Hold'em ($1,000,000 GTD)", dates="Dec 3-5, 2026 (Day 1A, 1B, Day 2)",
         buyin=1600, gtd=1000000, split="$1,430 + $120 + $50", stack=40000,
         registration="Unlimited re-entry for each starting flight ... until the start of level 10. "
                      "A player who advances to Day 2 is prohibited from entering a subsequent starting flight.",
         level="40 min", tables="9-handed"),
    dict(name="$600 HORSE", dates="Dec 4, 2026 12:00 PM", buyin=600, gtd=None, split="$510 + $65 + $25",
         stack=35000, registration=UNLIMITED + " (approximately 4:30 p.m.)", level="30 min",
         tables="8-handed; final table 9-handed"),
    dict(name="$1,100 WPT Prime Championship ($5,000,000 GTD)", dates="Dec 5-12, 2026 (4 starting flights)",
         buyin=1100, gtd=5000000, split="$970 + $90 + $40", stack=40000,
         registration="One (1) Entry and One (1) re-entry for each starting flight ... until the start of "
                      "level 10 (approximately 6:45 p.m.). A player who advances to Day 2 is prohibited from "
                      "entering a subsequent starting flight.",
         level="Day 1: 40 min; Days 2-4: 60 min", tables="9-handed Day 1"),
    dict(name="$600 NLH Turbo ($50,000 GTD)", dates="Dec 5, 6, 7, 8, 9, 12, 14 at 9 PM; Dec 21 at 6 PM",
         buyin=600, gtd=50000, split="$515 + $60 + $25", stack=30000, registration=UNLIMITED,
         level="20 min", tables="9-handed"),
    dict(name="$1,600 PLO Mystery Bounty ($500,000 GTD)", dates="Dec 6-7, 2026 (Day 1A 11 AM, 1B 6 PM, Day 2 12 PM)",
         buyin=1600, gtd=500000, split="$930 prize pool + $500 mystery bounty pool + $120 fee + $50 staff charge",
         stack=40000, registration=FLIGHT_RULE.replace("level 9", "level 10"),
         level="Day 1A 40 min; Day 1B 20 min; Day 2 40 min", tables="8-handed; final table 9-handed"),
]

# Selected rows transcribed from the official WPT schedule PDF (buy-in / guarantee /
# chips / level structure). The PDF also lists mixed-game, satellite and continuation
# rows; those are not transcribed here and are not presented as a complete schedule.
WPT_ROWS = [
    ("2026-11-27", "11:00", "No Limit Hold'em Day 1A", 600, 400000, 40000, "30/40"),
    ("2026-11-27", "17:00", "No Limit Hold'em Day 1B", 600, 400000, 40000, "30/40"),
    ("2026-11-28", "11:00", "No Limit Hold'em Day 1C", 600, 400000, 40000, "30/40"),
    ("2026-11-28", "17:00", "No Limit Hold'em Day 1D", 600, 400000, 40000, "30/40"),
    ("2026-11-29", "11:00", "No Limit Hold'em Day 1E", 600, 400000, 40000, "30/40"),
    ("2026-11-29", "18:00", "No Limit Hold'em Day 1F", 600, 400000, 40000, "20/40"),
    ("2026-11-30", "11:00", "No Limit Hold'em Day 1A", 800, 1000000, 40000, "30/40"),
    ("2026-11-30", "17:00", "No Limit Hold'em Day 1B", 800, 1000000, 40000, "30/40"),
    ("2026-12-01", "11:00", "No Limit Hold'em Day 1C", 800, 1000000, 40000, "30/40"),
    ("2026-12-01", "17:00", "No Limit Hold'em Day 1D", 800, 1000000, 40000, "30/40"),
    ("2026-12-02", "11:00", "No Limit Hold'em Day 1E", 800, 1000000, 40000, "30/40"),
    ("2026-12-02", "18:00", "No Limit Hold'em Day 1F", 800, 1000000, 40000, "20/40"),
    ("2026-12-03", "11:00", "No Limit Hold'em Day 1A", 1600, 1000000, 40000, "40"),
    ("2026-12-04", "11:00", "No Limit Hold'em Day 1B", 1600, 1000000, 40000, "40"),
    ("2026-12-05", "11:00", "WPT Prime Championship Day 1A", 1100, 5000000, 40000, "40/60"),
    ("2026-12-06", "11:00", "WPT Prime Championship Day 1B", 1100, 5000000, 40000, "40/60"),
    ("2026-12-07", "11:00", "WPT Prime Championship Day 1C", 1100, 5000000, 40000, "40/60"),
    ("2026-12-08", "11:00", "WPT Prime Championship Day 1D", 1100, 5000000, 40000, "40/60"),
    ("2026-12-10", "10:00", "Super Gold Million Mystery Bounty Day 1A", 400, 3000000, 30000, "30/40"),
    ("2026-12-10", "18:00", "Super Gold Million Mystery Bounty Day 1B", 400, 3000000, 30000, "20/40"),
    ("2026-12-11", "10:00", "Super Gold Million Mystery Bounty Day 1C", 400, 3000000, 30000, "30/40"),
    ("2026-12-11", "18:00", "Super Gold Million Mystery Bounty Day 1D", 400, 3000000, 30000, "20/40"),
    ("2026-12-12", "10:00", "No Limit Hold'em", 800, 100000, 30000, "30"),
    ("2026-12-12", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-13", "11:00", "WPT World Championship Day 1A ($1,000,000 added by ClubWPT Gold)", 10400, None,
     100000, "60/90"),
    ("2026-12-13", "11:00", "Ladies NLH Championship (2 Day)", 1100, 250000, 40000, "40"),
    ("2026-12-13", "11:00", "No Limit Hold'em Day 1A", 800, 500000, 40000, "40"),
    ("2026-12-14", "11:00", "WPT World Championship Day 1B ($1,000,000 added by ClubWPT Gold)", 10400, None,
     100000, "60/90"),
    ("2026-12-14", "11:00", "No Limit Hold'em Day 1B", 800, 500000, 40000, "40"),
    ("2026-12-15", "11:00", "WPT World Championship Day 1C ($1,000,000 added by ClubWPT Gold)", 10400, None,
     100000, "60/90"),
    ("2026-12-17", "11:00", "Seniors NLH Championship (3 Day)", 1100, 500000, 40000, "40"),
    ("2026-12-17", "12:00", "No Limit Hold'em Day 1A", 3000, 2000000, 40000, "40"),
    ("2026-12-18", "11:00", "No Limit Hold'em Day 1A", 1100, 1000000, 40000, "40"),
    ("2026-12-18", "12:00", "No Limit Hold'em Day 1B", 3000, 2000000, 40000, "40"),
    ("2026-12-18", "19:00", "NLH Turbo", 1100, 100000, 30000, "20"),
    ("2026-12-19", "11:00", "Seniors High Roller (3 Day)", 5000, 250000, 50000, "60"),
    ("2026-12-19", "11:00", "NLH Mystery Bounty Day 1A", 1600, 1000000, 40000, "40"),
    ("2026-12-19", "13:00", "NLH 6-Max", 3000, 500000, 30000, "30"),
    ("2026-12-19", "18:00", "NLH 6-Max Turbo", 600, 50000, 30000, "20"),
    ("2026-12-19", "19:00", "NLH Mystery Bounty Day 1B", 1600, 1000000, 40000, "20/40"),
    ("2026-12-20", "11:00", "NLH Mystery Bounty Day 1C", 1600, 1000000, 40000, "40"),
    ("2026-12-20", "12:00", "No Limit Hold'em", 600, 50000, 30000, "30"),
    ("2026-12-20", "19:00", "NLH Mystery Bounty Day 1D", 1600, 1000000, 40000, "20/40"),
    ("2026-12-21", "12:00", "No Limit Hold'em", 1100, 100000, 30000, "30"),
    ("2026-12-21", "20:00", "NLH Turbo", 600, 50000, 30000, "20"),
]

WPT_NOTES = {
    "championship_entry_rule": (
        "The $10,400 WPT World Championship terms were read only in part in this session (the "
        "Registration paragraph falls between two retrieved chunks). A prior session recorded "
        "'one entry per starting flight plus one Day 2 entry, up to four total'; that is NOT "
        "re-verified here. Treated as multi-entry until the sentence is read in full."),
    "super_gold_million": (
        "Super Gold Million Mystery Bounty, $400 buy-in, $3,000,000 GTD (announced on the official "
        "Wynn poker page, retrieved 2026-11-17). Its structure-sheet re-entry sentence was not read "
        "in this session - flagged, not classified."),
}

# Official facts stated on the Wynn poker page (retrieved 2026-11-17).
WYNN_DAILY = [
    dict(fact="Daily tournaments run twice a day during non-event timeframes",
         value="official page text", source=WYNN_POKER_URL),
    dict(fact="Total guaranteed prize pools across the daily schedule",
         value="$200,000 weekly", source=WYNN_POKER_URL),
    dict(fact="Friday daily event", value="$40,000 guaranteed NLH Rebuy", source=WYNN_POKER_URL),
    dict(fact="Evening daily event", value="$10,000 guaranteed every evening at 6 p.m.",
         source=WYNN_POKER_URL),
    dict(fact="Daily schedule suspension",
         value="suspended during each Wynn Signature, Wynn Millions, and Classic tournament series "
               "(WPT is not named in that sentence)", source=WYNN_POKER_URL),
    dict(fact="Poker room location (affects the walk from the tower)",
         value="registration takes place in the Wynn Las Vegas Poker Room, located in Encore at "
               "Wynn Las Vegas", source=WPT_STRUCTURES_URL),
    dict(fact="Payment rule for entry fees",
         value="Entry Fee must be paid with cash or Wynn Las Vegas live casino chips; no other "
               "forms of payment", source=WPT_STRUCTURES_URL),
    dict(fact="WPT registration window",
         value="registration for each Event opens four (4) hours before the scheduled start",
         source=WPT_STRUCTURES_URL),
]

# --------------------------------------------------------------- hotels -------
# resort_fee values are only filled from an official property page read today.
TAX = dict(rate_pct=13.38, label="13.38% combined transient lodging tax, resort hotel within the "
           "Primary Gaming Corridor (12.5% county/state stack + 0.88% stadium district)",
           source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/"
                  "original/as/pubhear-roomtax-ord-sb1d2.pdf",
           retrieved="2026-11-17",
           caveat="The cited Clark County ordinance table is the document stored in this repository; "
                  "confirm the rate in force on the booking folio before paying.")

HOTELS = [
    dict(hotel="The Venetian Resort", tower="Venetian / Palazzo (same resort)",
         role="Hosts the DeepStack Extravaganza IV poker room",
         resort_fee_usd=55,
         resort_fee_text="$55 plus tax per night, payable upon check-in (official resort-fee page)",
         fee_source="https://www.venetianlasvegas.com/resort/resort-fee.html",
         fee_inclusions="Canyon Ranch fitness access for two; in-suite internet; boarding-pass printing; "
                        "unlimited local and toll-free calls; PressReader newspapers/magazines",
         poker_rate="$119 (Venetian) / $209 (Palazzo) 'as low as', Luxury King Suite, single/double occupancy; "
                    "requires 6 hrs of cash play or a $300+ tournament buy-in per night, met before 2 a.m. "
                    "on the last night, otherwise the rate reverts to the prevailing rate",
         poker_rate_source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         parking=None, quality=None,
         booking=("https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-12-02"
                 "&children[]=0&departure_date=2026-12-09&view=calendar"),
         booking_note=("booking link pre-set to the worked-example stay Dec 2-9, 2026; change the dates in "
                       "the URL or on the page for your own trip"),
         flags=["F27", "F28", "F29"]),
    dict(hotel="Wynn Las Vegas", tower="Wynn (poker room is in Encore)",
         role="Hosts the WPT World Championship (Nov 27 - Dec 21, 2026)",
         resort_fee_usd=55,
         resort_fee_text="$55 plus tax per night for reservations booked on or after Jan 15, 2025 "
                         "($50 before that date)",
         fee_source="https://www.wynnlasvegas.com/terms-and-conditions/849338",
         fee_inclusions="In-room Wi-Fi for four devices; fitness centre for up to two; resort pools and "
                        "sundecks; concierge; digital newsstand; unlimited local/domestic long-distance calls; "
                        "Alexa in-room services",
         poker_rate=None, quality=None,
         booking="https://www.wynnlasvegas.com/",
         cancellation="$50 surcharge per guest above two; deposit of one night of room and tax at booking; "
                      "cancellations at least 72 hours before arrival or the deposit is forfeited; $150 per "
                      "night incidentals authorisation at check-in (same terms page)",
         parking=None,
         flags=["F30", "F31", "F32"]),
    dict(hotel="Encore at Wynn Las Vegas", tower="Encore", role="Wynn sister tower; the poker room is in this tower",
         resort_fee_usd=None, resort_fee_text=None, fee_source="https://www.wynnlasvegas.com/casino/poker",
         fee_inclusions=None, poker_rate=None, quality=None, parking=None,
         booking="https://www.wynnlasvegas.com/", flags=["F18", "F33"]),
    dict(hotel="Bellagio", tower="Bellagio", role="Hosts the Bellagio poker room tournaments",
         resort_fee_usd=None, resort_fee_text=None,
         fee_source="https://bellagio.mgmresorts.com/en/casino/poker.html",
         fee_inclusions=None, poker_rate=None, quality=None, parking=None,
         booking="https://bellagio.mgmresorts.com/book-room/",
         cancellation="Not verified - no official cancellation-policy page retrieved for these dates",
         flags=["F33"]),
    dict(hotel="Caesars Palace", tower="Caesars Palace", role="Caesars/Horseshoe daily tournament rooms",
         resort_fee_usd=None, resort_fee_text=None,
         fee_source="https://www.caesars.com/caesars-palace",
         fee_inclusions=None, poker_rate=None, quality=None, parking=None,
         booking="https://www.caesars.com/book/?propcode=CLV&action=FindRooms",
         cancellation="Official Caesars Palace homepage (2026-11-17) advertises 'FREE 48-Hour Cancellation' with "
                      "an asterisk and 'Terms apply'; the rate-specific deadline was not retrieved",
         flags=["F34"]),
    dict(hotel="Park MGM", tower="Park MGM",
         role="MGM campus south of the Venetian; no poker tournament schedule verified in this audit",
         resort_fee_usd=None, resort_fee_text=None, fee_source="https://parkmgm.mgmresorts.com/en.html",
         fee_inclusions=None, poker_rate=None, quality=None, parking=None,
         booking="https://parkmgm.mgmresorts.com/book-room/",
         cancellation="Not verified", flags=["F33"]),
    dict(hotel="The Cosmopolitan of Las Vegas", tower="Cosmopolitan",
         role="MGM campus between Park MGM and the Venetian; no poker tournament schedule verified in this audit",
         resort_fee_usd=None, resort_fee_text=None,
         fee_source="https://cosmopolitanlasvegas.mgmresorts.com/en.html",
         fee_inclusions=None, poker_rate=None, quality=None, parking=None,
         booking="https://cosmopolitanlasvegas.mgmresorts.com/redirect/bookaroom",
         cancellation="Not verified", flags=["F33"]),
]

# Dated rate log. Rates are dynamic, so every observation is stored with its own
# date and provenance instead of one "current" number.
RATE_LOG = [
    dict(hotel="The Venetian Resort", checkin="2026-12-02", checkout="2026-12-09", nights=7,
         occupancy="2 adults, 1 room", room_type="Newly remodeled Luxury King Suite",
         checkout_total=7054.77, nightly_average=1007.82, resort_fee_total=385.00, tax_total=832.52,
         parking=None, cancellation_deadline=None, observed="2026-11-16",
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-12-02&children[]=0&departure_date=2026-12-09&view=calendar",
         source_label="Venetian official booking UI, captured by session cd5ab298",
         verified=False,
         caveats=["Captured 2026-11-16 by an earlier session; this session could not re-read the booking "
                  "engine (it is JavaScript-driven) on 2026-11-17, so the figure is a dated snapshot, "
                  "not a current quote.",
                  "Nightly average = checkout total / nights (derived), not a printed per-night rate.",
                  "The booking UI also warned about maximum occupancy for suite types."]),
    dict(hotel="Wynn Las Vegas", checkin="2026-12-02", checkout="2026-12-09", nights=7,
         occupancy="2 adults, 1 room", room_type="Wynn Resort King (direct booking)",
         checkout_total=None, nightly_average=711.00, resort_fee_total=None, tax_total=None,
         parking=None, cancellation_deadline="72 hours before arrival (per the Wynn terms page read 2026-11-17)",
         observed="2026-11-16",
         source="https://www.wynnlasvegas.com/terms-and-conditions/849338",
         source_label="Wynn official booking result recorded by session cd5ab298; cancellation policy from the "
                      "Wynn terms page re-read 2026-11-17",
         verified=False,
         caveats=["The engine returned a rounded $711 average per night with the resort fee included and tax "
                  "excluded; no checkout total was returned, so the total is left blank rather than computed.",
                  "The 2026-11-16 note claiming 'self-parking included in the resort fee' is NOT supported by "
                  "the Wynn terms page read on 2026-11-17, so parking is blank and flagged."]),
    dict(hotel="The Venetian Resort", checkin="any date in the poker series", checkout="n/a", nights=None,
         occupancy="1-2 adults, Luxury King Suite", room_type="Poker suite rate",
         checkout_total=None, nightly_average=None, resort_fee_total=None, tax_total=None,
         parking=None, cancellation_deadline=None, observed="2026-11-17",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         source_label="Venetian official poker suite-rate page read 2026-11-17",
         verified=True,
         caveats=["Official page states rates 'start as low as $119 and $209 and can be higher', are only "
                  "quoted out to a maximum of 150 days from the current date, and require qualifying poker "
                  "play each night (6 hours of cash play or a $300+ tournament buy-in) before 2 a.m. on the "
                  "last night; otherwise the rate reverts to the prevailing rate.",
                  "$55 resort fee per night stayed is stated on the same page.",
                  "Venetian Rewards earns $2 per hour played, redeemable in part toward tournament buy-ins "
                  "(same page) - a cost offset, not a rate."]),
]

# Walking routes. Only a stated duration from an official or map source is recorded;
# everything else is left null with a one-click route link so the number can be checked.
MAP_ROUTE = "https://www.google.com/maps/dir/{a}/{b}"
ROUTES = [
    dict(hotel="The Venetian Resort", venue="The Venetian poker room (Palazzo Level 2)", minutes=0,
         verified=True, note="On the same property: the DeepStack Extravaganza IV poker suite is in the "
                             "Venetian/Palazzo resort complex.",
         source=DSE_URL),
    dict(hotel="The Palazzo", venue="The Venetian poker room", minutes=0, verified=True,
         note="The Venetian suite-rate page treats The Venetian and The Palazzo as one resort for the poker "
              "rate, so the walk is inside the same complex.", source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(hotel="Wynn Las Vegas", venue="Wynn poker room (in Encore)", minutes=None, verified=False,
         note="The official WPT terms state registration is in the Wynn Las Vegas Poker Room LOCATED IN "
               "ENCORE, so the tower-to-room walk is not zero; the minutes are not published.",
         source=WPT_STRUCTURES_URL),
    dict(hotel="Encore at Wynn Las Vegas", venue="Wynn poker room (in Encore)", minutes=0, verified=True,
         note="The poker room is in the Encore tower (official WPT general terms, rule 3).",
         source=WPT_STRUCTURES_URL),
    dict(hotel="Park MGM", venue="The Venetian poker room", minutes=None, verified=False,
         note="No official or map duration captured; open the route link to time it.", source=None),
    dict(hotel="The Cosmopolitan of Las Vegas", venue="The Venetian poker room", minutes=None, verified=False,
         note="No official or map duration captured; open the route link to time it.", source=None),
    dict(hotel="Bellagio", venue="Bellagio poker room", minutes=0, verified=True,
         note="On the same property.", source="https://bellagio.mgmresorts.com/en/casino/poker.html"),
    dict(hotel="Bellagio", venue="The Venetian poker room", minutes=None, verified=False,
         note="No official or map duration captured.", source=None),
    dict(hotel="Caesars Palace", venue="Caesars Palace poker room", minutes=0, verified=True,
         note="On the same property.", source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(hotel="Caesars Palace", venue="The Venetian poker room", minutes=None, verified=False,
         note="No official or map duration captured.", source=None),
    dict(hotel="Wynn Las Vegas", venue="The Venetian poker room", minutes=None, verified=False,
         note="Wynn and the Venetian face each other across Sands Avenue, but no official source publishes a "
               "walking time; verify with the route link before relying on it.", source=None),
]
