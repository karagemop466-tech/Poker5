#!/usr/bin/env python3
"""Generate data-6d1e0039/*.json for session 6d1e0039.

Every value in the emitted files is either
  * copied from an official page / PDF that was fetched on RETRIEVED, or
  * explicitly null with status "unverified" / "blank".
Computed values are labelled "computed" and never presented as sourced facts.

Run: python3 scripts/gen_6d1e0039_data.py
"""
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data-6d1e0039")
RETRIEVED = "2026-11-17"

VEN_SCHEDULE = ("https://www.venetianlasvegas.com/resort/casino/poker/"
                "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
VEN_STRUCT = ("https://www.venetianlasvegas.com/content/dam/venetianlasvegas/"
              "resort/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf")
VEN_FEE = "https://www.venetianlasvegas.com/resort/resort-fee.html"
WYNN_SCHED = ("https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/"
              "Poker/WPT/WPT_World_Championship_Schedule.pdf")
WYNN_STRUCT = ("https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/"
               "Poker/WPT/WPT_World_Championship_Structures.pdf")
WYNN_TERMS = "https://www.wynnlasvegas.com/terms-and-conditions/850257"
WYNN_POKER = "https://www.wynnpoker.com/"
BELLAGIO_POKER = "https://bellagio.mgmresorts.com/en/casino/poker.html"
BELLAGIO_SAT = ("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/"
                "blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/"
                "mgm-bellagio-poker-saturdays-$1000-nlh.pdf")
BELLAGIO_FRI = ("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/"
                "blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/"
                "mgm-bellagio-poker-fridays-$600-nlh.pdf")
BELLAGIO_SUN = ("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/"
                "blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/"
                "mgm-bellagio-poker-sundays-$400-horse.pdf")
CAESARS_ARTICLE = ("https://www.caesars.com/las-vegas/explore/casino/"
                   "poker-tournaments-las-vegas-strip")
CLARK_TAX = ("https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:"
             "3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf")
COMPASS = "https://www.casinocompassapp.com/transportation/walking-the-strip"
VEN_BOOK = ("https://www.venetianlasvegas.com/book?adults%5B%5D=2&arrival_date=2026-12-02"
            "&children%5B%5D=0&departure_date=2026-12-09&view=calendar")
WYNN_BOOK = ("https://www.wynnlasvegas.com/booking?checkin=2026-12-02&checkout=2026-12-09"
             "&rooms=1&adults=2")


def row(**kw):
    base = dict(
        venue=None, venueSlug=None, eventNo=None, name=None, game=None, format=None,
        date=None, start=None, buyIn=None, guarantee=None, startingStack=None,
        levelMinutes=None, lateRegLevels=None, lateRegClock=None, payoutPercent=None,
        bountyAmount=None, capacityNote=None, days=1,
        singleEntry="unverified", reEntry=None, addOn=None, feeTotal=None,
        prizePoolPortion=None, staffFeeNote=None,
        scheduleUrl=None, structureUrl=None, retrieved=RETRIEVED,
        excerpt="", flags=[],
    )
    base.update(kw)
    return base


# ---------------------------------------------------------------- Venetian
# Group definitions taken from the 37 official structure sheets read 2026-11-17.
# "silent" => the sheet contains no re-entry / rebuy / add-on sentence at all.
VEN_GROUPS = [
    dict(sheet=1, events=[9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64],
         name="$200 No Limit Hold'em Bounty $8K GTD", game="NLH", format="Bounty (fixed $50)",
         start="17:10", guarantee=8000, stack=25000, level=30, lreg=8, lregClock="9:40 PM",
         pool=160, bounty=50),
    dict(sheet=5, events=[2, 12], name="$300 No Limit Hold'em $10K GTD", game="NLH",
         format="Freezeout-style (no rule stated)", start="11:10", guarantee=10000,
         stack=40000, level=40, lreg=10, pool=242),
    dict(sheet=6, events=[10], name="$400 No Limit Hold'em $15K GTD", game="NLH",
         format="Freezeout-style (no rule stated)", start="11:10", guarantee=15000,
         stack=40000, level=40, lreg=10, pool=335),
    dict(sheet=7, events=[14, 28, 63], name="$600 No Limit Hold'em $30K GTD", game="NLH",
         format="Freezeout-style (no rule stated)", start="11:10", guarantee=30000,
         stack=40000, level=40, lreg=10, pool=510,
         perEventGuarantee={28: 40000}, perEventName={28: "$600 No Limit Hold'em $40K GTD"}),
    dict(sheet=8, events=[18, 58], name="$200 NLH PokerAtlas Valuetown Bounty $20K GTD",
         game="NLH", format="Bounty + paid re-entry", start="17:10", guarantee=20000,
         stack=25000, level=25, lreg=8, pool=160, singleEntry="no"),
    dict(sheet=11, events=[16, 30, 54], name="$600 No Limit Hold'em Bounty", game="NLH",
         format="Bounty ($200 pre-money / $500 post-money)", start="11:10",
         stack=40000, level=40, lreg=10, lregClock="4:55 PM", pool=510, bounty=200,
         perEventGuarantee={16: 30000, 30: 40000, 54: 50000},
         perEventName={16: "$600 No Limit Hold'em Bounty $30K GTD",
                       30: "$600 No Limit Hold'em Bounty $40K GTD",
                       54: "$600 No Limit Hold'em Bounty $50K GTD"}),
    dict(sheet=15, events=[29, 31, 34, 38, 42, 50, 51, 53, 55],
         name="$300 No Limit Hold'em Bounty $15K GTD", game="NLH",
         format="Bounty (fixed $100)", start="17:10", guarantee=15000, stack=25000,
         level=25, lreg=8, lregClock="9:40 PM", pool=250, bounty=100),
    dict(sheet=16, events=[36], name="$800 No Limit Hold'em Bounty $75K GTD", game="NLH",
         format="Bounty ($200 pre-money / $500 post-money)", start="11:10",
         guarantee=75000, stack=40000, level=40, lreg=10, pool=700, bounty=200),
    dict(sheet=17, events=[24, 32], name="$600 No Limit Hold'em Seniors $40K GTD",
         game="NLH", format="Seniors (50+)", start="10:10", guarantee=40000, stack=40000,
         level=40, lreg=10, pool=510, payoutPercent=15, capacityNote="Players 50+ only"),
    dict(sheet=18, events=[3, 4, 5], name="$200 NLH RaceDay Stack", game="NLH",
         format="RaceDay stack (20/15 min levels)", start="10:10", stack=30000,
         level=20, lreg=6, lregClock="about 12:25 PM", pool=165),
    dict(sheet=22, events=[20], name="$300 Pot Limit Omaha Double Board Bomb Pot $10K GTD",
         game="PLO", format="Double board bomb pot", start="12:10", guarantee=10000,
         stack=30000, level=30, lreg=8, pool=242, capacityNote="8-handed"),
    dict(sheet=23, events=[57], name="$600 Pot Limit Omaha Double Board Bomb Pot $25K GTD",
         game="PLO", format="Double board bomb pot", start="12:10", guarantee=25000,
         stack=30000, level=30, lreg=8, pool=510, capacityNote="8-handed"),
    dict(sheet=28, events=[27], name="$600 BIG O $25K GTD", game="Big O",
         format="5-card PLO hi-lo", start="12:10", guarantee=25000, stack=30000,
         level=30, lreg=8, pool=510, capacityNote="8-handed"),
    dict(sheet=26, events=[17], name="$400 Pot Limit Omaha Bounty $15K GTD", game="PLO",
         format="Bounty (fixed $100) - Call or Make It", start="12:10", guarantee=15000,
         stack=30000, level=30, lreg=8, pool=340, bounty=100, capacityNote="8-handed"),
    dict(sheet=27, events=[40], name="$600 Pot Limit Omaha Bounty $25K GTD", game="PLO",
         format="Bounty (fixed $200)", start="12:10", guarantee=25000, stack=30000,
         level=30, lreg=8, pool=510, bounty=200, capacityNote="8-handed"),
    dict(sheet=30, events=[8], name="$200 PKO No Limit Hold'em $8K GTD", game="NLH",
         format="Progressive knockout ($50)", start="17:10", guarantee=8000, stack=25000,
         level=25, lreg=8, pool=160, bounty=50),
    dict(sheet=29, events=[6], name="$200 No Limit Hold'em", game="NLH",
         format="Freezeout-style (no rule stated)", start="11:10", stack=30000,
         level=25, lreg=8, lregClock="about 3:40 PM", pool=160),
    dict(sheet=31, events=[35], name="$600 NLH LIPS Poker Jingle Tag Team $10K GTD",
         game="NLH", format="Tag team (F/F or F/M), rotate every level", start="10:10",
         guarantee=10000, stack=40000, level=40, lreg=8, lregClock="about 2:40 PM",
         pool=510, staffFeeNote="+$10 flat LIPS fee per player",
         flags=["extra-fee"]),
    dict(sheet=33, events=[43], name="$600 NLH LIPS KINGS and QUEENS Bounty $30K GTD",
         game="NLH", format="Bounty (fixed $200)", start="11:10", guarantee=30000,
         stack=40000, level=40, lreg=10, pool=510, bounty=200,
         staffFeeNote="+$10 flat LIPS fee per player", flags=["extra-fee"]),
    dict(sheet=34, events=[52], name="$1,100 No Limit Hold'em PKO $75K GTD", game="NLH",
         format="Progressive knockout ($200)", start="11:10", guarantee=75000,
         stack=40000, level=40, lreg=10, pool=970, bounty=200),
]

# official schedule facts needed for dates / buy-ins (transcribed from the official
# schedule page; the .psv baseline in data/ holds the same rows)
VEN_ROWS = {
    2: ("2026-11-18", 300), 3: ("2026-11-19", 200), 4: ("2026-11-20", 200),
    5: ("2026-11-21", 200), 6: ("2026-11-22", 200), 8: ("2026-11-23", 200),
    9: ("2026-11-24", 200), 10: ("2026-11-25", 400), 11: ("2026-11-25", 200),
    12: ("2026-11-26", 300), 13: ("2026-11-26", 200), 14: ("2026-11-27", 600),
    15: ("2026-11-27", 200), 16: ("2026-11-28", 600), 17: ("2026-11-28", 400),
    18: ("2026-11-28", 200), 20: ("2026-11-29", 300), 21: ("2026-11-29", 200),
    22: ("2026-11-30", 200), 23: ("2026-12-01", 200), 24: ("2026-12-02", 600),
    25: ("2026-12-02", 200), 27: ("2026-12-03", 600), 28: ("2026-12-06", 600),
    29: ("2026-12-06", 300), 30: ("2026-12-07", 600), 31: ("2026-12-07", 300),
    32: ("2026-12-08", 600), 34: ("2026-12-08", 300), 35: ("2026-12-09", 600),
    36: ("2026-12-09", 800), 38: ("2026-12-09", 300), 40: ("2026-12-10", 600),
    42: ("2026-12-10", 300), 43: ("2026-12-11", 600), 50: ("2026-12-13", 300),
    51: ("2026-12-14", 300), 52: ("2026-12-15", 1100), 53: ("2026-12-15", 300),
    54: ("2026-12-16", 600), 55: ("2026-12-16", 300), 57: ("2026-12-17", 600),
    58: ("2026-12-19", 200), 60: ("2026-12-20", 200), 61: ("2026-12-21", 200),
    62: ("2026-12-22", 200), 63: ("2026-12-23", 600), 64: ("2026-12-23", 200),
}

ven_events = []
for g in VEN_GROUPS:
    for ev in g["events"]:
        d, buy = VEN_ROWS[ev]
        gtd = g.get("perEventGuarantee", {}).get(ev, g.get("guarantee"))
        name = g.get("perEventName", {}).get(ev, g["name"])
        single = g.get("singleEntry", "unverified")
        excerpt = ""
        if single == "no":
            excerpt = ("Structure sheet: \u201cAll subsequent buy in's after the initial buy in "
                       "will be $200\u201d - a second paid entry is priced, therefore re-entry is "
                       "permitted. Not single-entry.")
        elif g["sheet"] in (1, 5, 6, 7, 11, 15, 16, 17, 18, 22, 23, 26, 27, 28, 29, 30, 31, 33, 34):
            excerpt = ("Structure sheet lists buy-in split, starting stack, level length and "
                       "registration close only; it contains no sentence about re-entry, rebuys "
                       "or add-ons. Absence of a rule is not a rule, so the event stays "
                       "unverified for single-entry.")
        flags = list(g.get("flags", []))
        if gtd is None:
            flags.append("no-guarantee-published")
        ven_events.append(row(
            venue="The Venetian Resort Las Vegas", venueSlug="venetian", eventNo=ev,
            name=name, game=g["game"], format=g["format"], date=d, start=g["start"],
            buyIn=buy, guarantee=gtd, startingStack=g["stack"], levelMinutes=g["level"],
            lateRegLevels=g["lreg"], lateRegClock=g.get("lregClock"),
            payoutPercent=g.get("payoutPercent"), bountyAmount=g.get("bounty"),
            capacityNote=g.get("capacityNote"), singleEntry=single,
            feeTotal=(None if g.get("staffFeeNote") else buy - g["pool"]),
            prizePoolPortion=g["pool"], staffFeeNote=g.get("staffFeeNote"),
            scheduleUrl=VEN_SCHEDULE, structureUrl=VEN_STRUCT.format(n=g["sheet"]),
            excerpt=excerpt, flags=flags,
        ))

# Venetian multi-flight / multi-entry events
VEN_MULTI = [
    dict(eventNo=1, name="$300 No Limit Hold'em $75K GTD (4 flights)", flights="1A 2026-11-16 11:10, 1B 2026-11-16 17:10, 1C 2026-11-17 11:10, 1D 2026-11-17 17:10",
         buyIn=300, guarantee=75000, stack=30000, level="40 min (1A/1C) / 30 min (1B/1D)", sheet=10, pool=240,
         rule="Multi-flight; a player may enter each starting flight, and players who bag Day 2 may not play later flights."),
    dict(eventNo=7, name="$400 No Limit Hold'em $75K GTD (2 flights)", flights="1A 2026-11-23 11:10, 1B 2026-11-24 11:10",
         buyIn=400, guarantee=75000, stack=40000, level="40 min", sheet=2, pool=330,
         rule="Multi-flight; each starting flight is a paid entry."),
    dict(eventNo=19, name="$400 No Limit Hold'em $75K GTD (3 flights)", flights="1A 2026-11-29 11:10, 1B 2026-11-30 11:10, 1C 2026-12-01 11:10",
         buyIn=400, guarantee=75000, stack=40000, level="40 min", sheet=3, pool=330,
         rule="Multi-flight; each starting flight is a paid entry."),
    dict(eventNo=26, name="$800 No Limit Hold'em $500K GTD (6 flights)", flights="1A 2026-12-03 11:10, 1B 17:10, 1C 2026-12-04 11:10, 1D 17:10, 1E 2026-12-05 11:10, 1F 2026-12-05 17:10 (turbo)",
         buyIn=800, guarantee=500000, stack=40000, level="40 min A/C/E, 30 min B/D, 20 min F", sheet=12, pool=690,
         rule="Multi-flight; late registration closes at level 6 (day flights) and level 9 of Day 2."),
    dict(eventNo=39, name="$800 NLH LIPS Ladies $40K GTD (2 days)", flights="2026-12-10 10:10 start, Day 2 2026-12-11 10:00",
         buyIn=800, guarantee=40000, stack=40000, level="40 min", sheet=32, pool=690,
         rule="Two-day event, 12.5% advance to the streamed final table; +$20 flat LIPS fee."),
    dict(eventNo=47, name="$2,200 No Limit Hold'em $1M GTD - PokerAtlas Championship", flights="1A 2026-12-12 10:10, 1B 2026-12-12 18:10",
         buyIn=2200, guarantee=1000000, stack=None, level="40 min (1A) / 30 min (1B)", sheet=21, pool=1975,
         rule="Two starting flights plus Day 2 (Dec 13) and a streamed Day 3 final table (Dec 14)."),
    dict(eventNo=49, name="$1,100 No Limit Hold'em Seniors $300K GTD (2 flights)", flights="1A 2026-12-13 10:10, 1B 2026-12-14 10:10",
         buyIn=1100, guarantee=300000, stack=None, level="40 min", sheet=20, pool=960,
         rule="Multi-flight Seniors (50+) event, 15% advance."),
    dict(eventNo=56, name="$1,100 No Limit Hold'em $500K GTD (5 flights)", flights="1A 2026-12-17 10:10, 1B 18:10, 1C 2026-12-18 10:10, 1D 18:10, 1E 2026-12-19 10:10",
         buyIn=1100, guarantee=500000, stack=None, level="40 min A/C/E, 30 min B/D", sheet=35, pool=960,
         rule="Multi-flight; $40 discount for pre-start registration on Day 1A/1B (buys an entry, not chips)."),
    dict(eventNo=59, name="$600 No Limit Hold'em $150K GTD (3 flights)", flights="1A 2026-12-20 11:10, 1B 2026-12-21 11:10, 1C 2026-12-22 11:10",
         buyIn=600, guarantee=150000, stack=None, level=None, sheet=4, pool=505,
         rule="Multi-flight; sheet #4 covers event 59 with the Day-1A pre-start discount."),
]
ven_multi = []
for e in VEN_MULTI:
    ven_multi.append(row(
        venue="The Venetian Resort Las Vegas", venueSlug="venetian", eventNo=e["eventNo"],
        name=e["name"], game="NLH", format="Multi-flight", date=e["flights"].split(",")[0].split()[-2],
        start=e["flights"].split(",")[0].split()[-1], buyIn=e["buyIn"],
        guarantee=e["guarantee"], startingStack=e["stack"], levelMinutes=None,
        singleEntry="no", reEntry="allowed across starting flights",
        feeTotal=(e["buyIn"] - e["pool"]), prizePoolPortion=e["pool"],
        capacityNote=e["flights"], days=(2 if e["eventNo"] in (39, 47, 49) else 1),
        scheduleUrl=VEN_SCHEDULE, structureUrl=VEN_STRUCT.format(n=e["sheet"]),
        excerpt=e["rule"], flags=["multi-entry"],
    ))

# Venetian satellites (buy-in to a seat, not a prize pool)
VEN_SATS = [
    dict(eventNo=33, date="2026-12-08", start="16:10", name="$100 NLH LIPS Ladies Milestone Satellite",
         buyIn=100, stack=20000, level=20, lreg=6, sheet=19, prizes="2 seats to event #39",
         note="Female players 21+; 200,000-chip milestone format"),
    dict(eventNo=37, date="2026-12-09", start="16:10", name="$100 NLH LIPS Ladies Milestone Satellite",
         buyIn=100, stack=20000, level=20, lreg=6, sheet=19, prizes="2 seats to event #39",
         note="Female players 21+; 200,000-chip milestone format"),
    dict(eventNo=41, date="2026-12-10", start="16:10", name="$260 NLH Milestone Satellite",
         buyIn=260, stack=20000, level=None, lreg=6, sheet=24, prizes="2 seats to event #47",
         note="Milestone satellite"),
    dict(eventNo=44, date="2026-12-11", start="16:10", name="$260 NLH Milestone Satellite",
         buyIn=260, stack=20000, level=None, lreg=6, sheet=24, prizes="2 seats to event #47",
         note="Milestone satellite"),
    dict(eventNo=45, date="2026-12-11", start="20:10", name="$260 NLH Turbo Milestone Satellite",
         buyIn=260, stack=20000, level=15, lreg=6, sheet=25, prizes="2 seats to event #47",
         note="Turbo milestone satellite"),
    dict(eventNo=46, date="2026-12-12", start="09:10", name="$260 NLH Turbo Milestone Satellite",
         buyIn=260, stack=20000, level=15, lreg=6, sheet=25, prizes="2 seats to event #47",
         note="Turbo milestone satellite"),
    dict(eventNo=48, date="2026-12-12", start="12:10", name="$260 NLH Turbo Milestone Satellite",
         buyIn=260, stack=20000, level=15, lreg=6, sheet=25, prizes="2 seats to event #47",
         note="Turbo milestone satellite"),
]
ven_sats = [row(
    venue="The Venetian Resort Las Vegas", venueSlug="venetian", eventNo=s["eventNo"],
    name=s["name"], game="NLH", format="Satellite", date=s["date"], start=s["start"],
    buyIn=s["buyIn"], startingStack=s["stack"], levelMinutes=s["level"],
    lateRegLevels=s["lreg"], guarantee=None, singleEntry="unverified",
    prizePoolPortion=None, capacityNote=s["prizes"], excerpt=s["note"],
    scheduleUrl=VEN_SCHEDULE, structureUrl=VEN_STRUCT.format(n=s["sheet"]),
    flags=["satellite"],
) for s in VEN_SATS]

# ---------------------------------------------------------------- Wynn
# (date, time, event, buy-in, guarantee, chips, levels, entry-rule code, fee split)
W = [
    ("2026-11-27", "11:00", "No Limit Hold'em Day 1A ($400,000 GTD, 6 flights)", 600, 400000, 40000, "30/40", "R9", "510/65/25", "multi"),
    ("2026-11-27", "12:00", "TORSE", 600, None, 35000, "30", "R9", "510/65/25", None),
    ("2026-11-27", "13:00", "PLO", 400, None, 30000, "30", "R5:30", "337/45/18", None),
    ("2026-11-27", "17:00", "No Limit Hold'em Day 1B ($400,000 GTD, 6 flights)", 600, 400000, 40000, "30/40", "R9", "510/65/25", "multi"),
    ("2026-11-28", "11:00", "No Limit Hold'em Day 1C ($400,000 GTD, 6 flights)", 600, 400000, 40000, "30/40", "R9", "510/65/25", "multi"),
    ("2026-11-28", "12:00", "Mixed Triple Draw (A-5, 2-7, Badugi)", 600, None, 35000, "30", "R9", "510/65/25", None),
    ("2026-11-28", "17:00", "No Limit Hold'em Day 1D ($400,000 GTD, 6 flights)", 600, 400000, 40000, "30/40", "R9", "510/65/25", "multi"),
    ("2026-11-29", "11:00", "No Limit Hold'em Day 1E ($400,000 GTD, 6 flights)", 600, 400000, 40000, "30/40", "R9", "510/65/25", "multi"),
    ("2026-11-29", "18:00", "No Limit Hold'em Day 1F Turbo ($400,000 GTD)", 600, 400000, 40000, "20/40", "R9", "510/65/25", "multi"),
    ("2026-11-30", "11:00", "No Limit Hold'em Day 1A ($1,000,000 GTD, 6 flights)", 800, 1000000, 40000, "30/40", "R9", "695/72/33", "multi"),
    ("2026-11-30", "12:00", "Limit Omaha 8", 600, None, 35000, "30", "R9", "510/65/25", None),
    ("2026-11-30", "17:00", "No Limit Hold'em Day 1B ($1,000,000 GTD, 6 flights)", 800, 1000000, 40000, "30/40", "R9", "695/72/33", "multi"),
    ("2026-12-01", "11:00", "No Limit Hold'em Day 1C ($1,000,000 GTD, 6 flights)", 800, 1000000, 40000, "30/40", "R9", "695/72/33", "multi"),
    ("2026-12-01", "12:00", "Limit Omaha 8 / Stud 8", 600, None, 35000, "30", "R9", "510/65/25", None),
    ("2026-12-01", "13:00", "PLO", 1100, None, 30000, "30", "R5:30", "975/85/45", None),
    ("2026-12-01", "17:00", "No Limit Hold'em Day 1D ($1,000,000 GTD, 6 flights)", 800, 1000000, 40000, "30/40", "R9", "695/72/33", "multi"),
    ("2026-12-02", "11:00", "No Limit Hold'em Day 1E ($1,000,000 GTD, 6 flights)", 800, 1000000, 40000, "30/40", "R9", "695/72/33", "multi"),
    ("2026-12-02", "18:00", "No Limit Hold'em Day 1F Turbo ($1,000,000 GTD)", 800, 1000000, 40000, "20/40", "R9", "695/72/33", "multi"),
    ("2026-12-03", "11:00", "No Limit Hold'em Day 1A ($1,000,000 GTD)", 1600, 1000000, 40000, "40", "R10", "1430/120/50", "multi"),
    ("2026-12-03", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, 20000, "20", None, None, "sat"),
    ("2026-12-04", "11:00", "No Limit Hold'em Day 1B ($1,000,000 GTD)", 1600, 1000000, 40000, "40", "R10", "1430/120/50", "multi"),
    ("2026-12-04", "12:00", "HORSE", 600, None, 35000, "30", "R9", "510/65/25", None),
    ("2026-12-04", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, 20000, "20", None, None, "sat"),
    ("2026-12-05", "11:00", "WPT Prime Championship Day 1A ($5,000,000 GTD)", 1100, 5000000, 40000, "40/60", "R10-1", "970/90/40", "multi"),
    ("2026-12-05", "21:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", "R9", "515/60/25", None),
    ("2026-12-06", "11:00", "WPT Prime Championship Day 1B ($5,000,000 GTD)", 1100, 5000000, 40000, "40/60", "R10-1", "970/90/40", "multi"),
    ("2026-12-06", "11:00", "PLO Mystery Bounty Day 1A ($500,000 GTD)", 1600, 500000, 40000, "40", "R10", "930+500/120/50", "multi"),
    ("2026-12-06", "12:00", "Milestone Satellite to $1,100 Prime Championship", 200, None, 20000, "20", None, None, "sat"),
    ("2026-12-06", "18:00", "PLO Mystery Bounty Day 1B Turbo ($500,000 GTD)", 1600, 500000, 40000, "20/40", "R10", "930+500/120/50", "multi"),
    ("2026-12-06", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, 20000, "20", None, None, "sat"),
    ("2026-12-06", "21:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", "R9", "515/60/25", None),
    ("2026-12-07", "11:00", "WPT Prime Championship Day 1C ($5,000,000 GTD)", 1100, 5000000, 40000, "40/60", "R10-1", "970/90/40", "multi"),
    ("2026-12-07", "11:00", "HORSE (2 Day)", 1100, None, 40000, "40", None, None, None),
    ("2026-12-07", "13:00", "PLO $500 Bounty ($100,000 GTD)", 1600, 100000, 30000, "30", None, None, None),
    ("2026-12-07", "19:00", "Milestone Satellite Package to Prime and World Championship", 1600, None, 20000, "25", None, None, "sat"),
    ("2026-12-07", "21:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", "R9", "515/60/25", None),
    ("2026-12-08", "11:00", "WPT Prime Championship Day 1D ($5,000,000 GTD)", 1100, 5000000, 40000, "40/60", "R10-1", "970/90/40", "multi"),
    ("2026-12-08", "19:00", "Milestone Satellite to $10,400 World Championship", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-08", "21:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", "R9", "515/60/25", None),
    ("2026-12-09", "11:00", "No Limit Hold'em (2 Day) ($1,000,000 GTD)", 1600, 1000000, 40000, "40", None, None, "multi"),
    ("2026-12-09", "13:00", "PLO $1,000 Bounty ($250,000 GTD)", 3000, 250000, 30000, "30", None, None, None),
    ("2026-12-09", "13:00", "Limit Omaha 8", 800, None, 35000, "30", None, None, None),
    ("2026-12-09", "14:00", "Milestone Satellite to $10,400 World Championship", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-09", "19:00", "Milestone Satellite to $10,400 World Championship", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-09", "21:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", "R9", "515/60/25", None),
    ("2026-12-10", "10:00", "Super Gold Million Mystery Bounty Day 1A ($3,000,000 GTD)", 400, 3000000, 30000, "30/40", None, None, "multi"),
    ("2026-12-10", "18:00", "Super Gold Million Mystery Bounty Day 1B Turbo ($3,000,000 GTD)", 400, 3000000, 30000, "20/40", None, None, "multi"),
    ("2026-12-11", "10:00", "Super Gold Million Mystery Bounty Day 1C ($3,000,000 GTD)", 400, 3000000, 30000, "30/40", None, None, "multi"),
    ("2026-12-11", "18:00", "Super Gold Million Mystery Bounty Day 1D Turbo ($3,000,000 GTD)", 400, 3000000, 30000, "20/40", None, None, "multi"),
    ("2026-12-12", "10:00", "No Limit Hold'em ($100,000 GTD)", 800, 100000, 30000, "30", None, None, None),
    ("2026-12-12", "13:00", "PLO ($250,000 GTD)", 3000, 250000, 30000, "30", None, None, None),
    ("2026-12-12", "14:00", "Milestone Satellite to $10,400 World Championship 1A/8 (75 seats)", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-12", "16:00", "Milestone Satellite to $10,400 Ladies NLH Championship", 200, None, 20000, "20", None, None, "sat"),
    ("2026-12-12", "19:00", "Milestone Satellite to $10,400 World Championship 1A/8", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-12", "21:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", None, None, None),
    ("2026-12-13", "11:00", "WPT World Championship Day 1A ($1,000,000 added)", 10400, None, 100000, "60/90", None, None, "multi"),
    ("2026-12-13", "11:00", "Ladies NLH Championship (2 Day) ($250,000 GTD)", 1100, 250000, 40000, "40", None, None, None),
    ("2026-12-13", "11:00", "TORSE (2 Day)", 1100, None, 40000, "40", None, None, None),
    ("2026-12-13", "11:00", "No Limit Hold'em Day 1A ($500,000 GTD)", 800, 500000, 40000, "40", None, None, "multi"),
    ("2026-12-13", "12:00", "PLO Day 1A ($1,000,000 GTD)", 1600, 1000000, 40000, "40", None, None, "multi"),
    ("2026-12-13", "12:00", "Milestone Satellite to $10,400 World Championship 1B", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-13", "18:00", "Milestone Satellite to $10,400 World Championship 1B/C", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-14", "11:00", "WPT World Championship Day 1B ($1,000,000 added)", 10400, None, 100000, "60/90", None, None, "multi"),
    ("2026-12-14", "11:00", "No Limit Hold'em Day 1B ($500,000 GTD)", 800, 500000, 40000, "40", None, None, "multi"),
    ("2026-12-14", "12:00", "PLO Day 1B ($1,000,000 GTD)", 1600, 1000000, 40000, "40", None, None, "multi"),
    ("2026-12-14", "12:00", "Mixed Triple Draw (2 Day)", 1100, None, 40000, "40", None, None, None),
    ("2026-12-14", "12:00", "Milestone Satellite to $10,400 World Championship 1C", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-14", "18:00", "Milestone Satellite to $10,400 World Championship 1C", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-14", "19:00", "PLO Turbo ($100,000 GTD)", 1100, 100000, 30000, "20", None, None, None),
    ("2026-12-14", "21:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", None, None, None),
    ("2026-12-15", "11:00", "WPT World Championship Day 1C ($1,000,000 added)", 10400, None, 100000, "60/90", None, None, "multi"),
    ("2026-12-15", "11:00", "Milestone Satellite to $10,400 World Championship 1C/Day 2", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-15", "12:00", "Big O", 1100, None, 30000, "30", None, None, None),
    ("2026-12-15", "13:00", "PLO Progressive Bounty (PKO) ($250,000 GTD)", 3000, 250000, 30000, "30", None, None, None),
    ("2026-12-15", "18:00", "Milestone Satellite to $10,400 World Championship Day 2", 1100, None, 20000, "25", None, None, "sat"),
    ("2026-12-15", "19:00", "NLH $500 Bounty Turbo ($100,000 GTD)", 1600, 100000, 30000, "20", None, None, None),
    ("2026-12-16", "11:00", "No Limit Hold'em Day 1A ($1,000,000 GTD)", 1100, 1000000, 40000, "40", None, None, "multi"),
    ("2026-12-16", "12:00", "PLO Double Board Bomb Pot", 800, None, 30000, "30", None, None, None),
    ("2026-12-16", "13:00", "PLO 6-Max", 10500, None, 100000, "30/40", None, None, None),
    ("2026-12-16", "13:00", "HORSE", 800, None, 35000, "30", None, None, None),
    ("2026-12-16", "18:00", "Milestone Satellite to $25K NLH High Roller", 3000, None, 20000, "25", None, None, "sat"),
    ("2026-12-16", "18:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "20", None, None, "sat"),
    ("2026-12-16", "19:00", "No Limit Hold'em Day 1B ($1,000,000 GTD)", 1100, 1000000, 40000, "20/40", None, None, "multi"),
    ("2026-12-17", "11:00", "Seniors NLH Championship (3 Day) ($500,000 GTD)", 1100, 500000, 40000, "40", None, None, None),
    ("2026-12-17", "11:00", "Wynn Mixed Championship (2 Day)", 1600, None, 40000, "40/60", None, None, None),
    ("2026-12-17", "12:00", "No Limit Hold'em Day 1A ($2,000,000 GTD)", 3000, 2000000, 40000, "40", None, None, "multi"),
    ("2026-12-17", "13:00", "NLH High Roller (2 Day)", 25800, None, 200000, "40/60", None, None, None),
    ("2026-12-17", "14:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "20", None, None, "sat"),
    ("2026-12-17", "19:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "20", None, None, "sat"),
    ("2026-12-18", "10:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "15", None, None, "sat"),
    ("2026-12-18", "12:00", "No Limit Hold'em Day 1B ($2,000,000 GTD)", 3000, 2000000, 40000, "40", None, None, "multi"),
    ("2026-12-18", "12:00", "Limit Omaha 8 Championship (2 Day)", 1600, None, 40000, "40/60", None, None, None),
    ("2026-12-18", "12:00", "No Limit Hold'em ($100,000 GTD)", 600, 100000, 30000, "30", None, None, None),
    ("2026-12-18", "13:00", "NLH 6-Max", 10500, None, 100000, "30/40", None, None, None),
    ("2026-12-18", "14:00", "Milestone Satellite to $5,000 Seniors High Roller", 600, None, 20000, "20", None, None, "sat"),
    ("2026-12-18", "18:00", "NLH Turbo ($100,000 GTD)", 1100, 100000, 30000, "20", None, None, None),
    ("2026-12-19", "11:00", "Seniors High Roller (3 Day) ($250,000 GTD)", 5000, 250000, 50000, "60", None, None, None),
    ("2026-12-19", "11:00", "NLH Mystery Bounty Day 1A ($1,000,000 GTD)", 1600, 1000000, 40000, "40", None, None, "multi"),
    ("2026-12-19", "12:00", "Milestone Satellite to $1,600 Mystery Bounty", 300, None, 20000, "20", None, None, "sat"),
    ("2026-12-19", "13:00", "PLO", 10500, None, 100000, "30/40", None, None, None),
    ("2026-12-19", "13:00", "NLH 6-Max ($500,000 GTD)", 3000, 500000, 30000, "30", None, None, None),
    ("2026-12-19", "13:00", "TORSE Championship (2 Day)", 1600, None, 40000, "40/60", None, None, None),
    ("2026-12-19", "17:00", "Milestone Satellite to $1,600 Mystery Bounty", 300, None, 20000, "20", None, None, "sat"),
    ("2026-12-19", "18:00", "NLH 6-Max Turbo ($50,000 GTD)", 600, 50000, 30000, "20", None, None, None),
    ("2026-12-19", "19:00", "NLH Mystery Bounty Day 1B Turbo ($1,000,000 GTD)", 1600, 1000000, 40000, "20/40", None, None, "multi"),
    ("2026-12-20", "11:00", "NLH Mystery Bounty Day 1C ($1,000,000 GTD)", 1600, 1000000, 40000, "40", None, None, "multi"),
    ("2026-12-20", "12:00", "No Limit Hold'em ($50,000 GTD)", 600, 50000, 30000, "30", None, None, None),
    ("2026-12-20", "13:00", "NLH 8-Max", 10500, None, 100000, "30/40", None, None, None),
    ("2026-12-20", "13:00", "Mixed Triple Draw (A-5, 2-7, Badugi)", 600, None, 35000, "30", None, None, None),
    ("2026-12-20", "18:00", "5-Card PLO Turbo ($50,000 GTD)", 600, 50000, 30000, "20", None, None, None),
    ("2026-12-20", "19:00", "NLH Mystery Bounty Day 1D Turbo ($1,000,000 GTD)", 1600, 1000000, 40000, "20/40", None, None, "multi"),
    ("2026-12-21", "12:00", "No Limit Hold'em ($100,000 GTD)", 1100, 100000, 30000, "30", None, None, None),
    ("2026-12-21", "20:00", "NLH Turbo ($50,000 GTD)", 600, 50000, 30000, "20", None, None, None),
]
WYNN_RULES = {
    "R9": ("Re-entry allowed, unlimited", "unlimited re-entry until the start of level 9",
           "Registration: \u201cUnlimited re-entry will be available until the start of level 9.\u201d"),
    "R10": ("Re-entry allowed, unlimited", "unlimited re-entry until the start of level 10",
            "Registration: \u201cUnlimited re-entry for each starting flight will be available until the start of level 10.\u201d"),
    "R10-1": ("Re-entry capped at one per flight (multi-flight)", "1 entry + 1 re-entry per starting flight, until level 10",
              "Registration: \u201cOne (1) Entry and One (1) re-entry for each starting flight will be available until the start of level 10 (approximately 6:45 p.m.).\u201d"),
    "R5:30": ("Re-entry allowed, unlimited", "unlimited re-entry until shortly before the 5:30 p.m. registration close",
              "Registration: \u201cUnlimited re-entry will be available until the start of level 9 (approximately 5:30 p.m.).\u201d"),
}
wynn_events = []
for (d, t, nm, buy, gtd, chips, lv, rule, fees, kind) in W:
    if kind == "sat":
        wynn_events.append(row(
            venue="Wynn Las Vegas (Encore poker room)", venueSlug="wynn", name=nm, game="NLH",
            format="Satellite", date=d, start=t, buyIn=buy, startingStack=chips,
            levelMinutes=None, singleEntry="unverified", guarantee=gtd,
            scheduleUrl=WYNN_SCHED, structureUrl=WYNN_STRUCT, flags=["satellite"],
            excerpt="Milestone satellite; winners receive tournament entries, not cash."))
        continue
    r = WYNN_RULES.get(rule) if rule else None
    flags = []
    if kind == "multi":
        flags.append("multi-flight")
    if gtd is None:
        flags.append("no-guarantee-published")
    excerpt = r[2] if r else (
        "The posted structures PDF (WPT World Championship Structures, fetched 2026-11-17) "
        "does not include a terms sheet for this event, so the entry rule is blank and unverified.")
    if not r:
        flags.append("rule-not-published")
    pool = None
    fee_total = None
    staff = None
    if fees:
        parts = fees.replace("930+500", "930|500+").split("/")
        numbers = [int(x) for x in parts[0].replace("|", "").split("+") if x]
        if len(numbers) == 1:
            pool = numbers[0]
            fee_total = buy - pool
            staff = int(parts[2]) if len(parts) > 2 else None
        else:
            pool = numbers[0] + numbers[1]
            fee_total = buy - pool
            staff = int(parts[2]) if len(parts) > 2 else None
    if fees and "930" in fees:
        pool = 930
        fee_total = buy - 930 - 500
    wynn_events.append(row(
        venue="Wynn Las Vegas (Encore poker room)", venueSlug="wynn", name=nm, game=None,
        format=None, date=d, start=t, buyIn=buy, guarantee=gtd, startingStack=chips,
        levelMinutes=lv, singleEntry="no" if r else "unverified",
        reEntry=(r[1] if r else None), feeTotal=fee_total, prizePoolPortion=pool,
        staffFeeNote=(("Poker staff service charge $%d" % staff) if staff else None),
        scheduleUrl=WYNN_SCHED, structureUrl=WYNN_STRUCT, excerpt=excerpt, flags=flags,
    ))

# ---------------------------------------------------------------- Bellagio / Caesars
other_events = [
    row(venue="Bellagio", venueSlug="bellagio", name="NLH (Saturdays)", game="NLH",
        format="Optional $40 staff gratuity buys +20,000 chips", date="every Saturday",
        start="11:00", buyIn=None, guarantee=50000, startingStack=40000,
        levelMinutes=30, lateRegLevels=10, lateRegClock="about 5:15 PM",
        singleEntry="unverified", scheduleUrl=BELLAGIO_POKER, structureUrl=BELLAGIO_SAT,
        excerpt=("\u201cOf the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and "
                 "$40 is optional staff gratuity.\u201d \u201cThe voluntary staff gratuity will "
                 "grant players an extra 20,000 chips.\u201d"),
        flags=["fee-conflict", "advantage-purchase", "recurring-undated"]),
    row(venue="Caesars Palace", venueSlug="caesars-palace", name="Daily NLH (4 daily flights)",
        game="NLH", format="Daily $100 with $50 add-on at first break", date="daily",
        start="10:00 / 14:00 / 18:00 / 21:00", buyIn=100, guarantee=1000,
        startingStack=20000, levelMinutes=20, singleEntry="no",
        addOn="$50 add-on at first break for +15,000 chips",
        scheduleUrl=CAESARS_ARTICLE, structureUrl=None,
        excerpt=("\u201cfour No-Limit Hold\u2019em tournaments each day at 10 a.m., 2 p.m., 6 p.m. "
                 "and 9 p.m. Every event carries a $100 buy-in, starts you with 20,000 chips, and "
                 "features a $1,000 guaranteed prize pool\u2026 a $50 add-on at the first break "
                 "gives you an extra 15,000 chips\u201d"),
        flags=["advantage-purchase", "recurring-undated", "marketing-page-not-structure-sheet"]),
]

# ---------------------------------------------------------------- Hotels (dated log)
hotel_log = [
    dict(venue="The Venetian Resort Las Vegas", slug="venetian",
         room="Newly Remodeled Luxury King Suite (650 sq ft)",
         occupancy="2 adults, 1 suite", checkin="2026-12-02", checkout="2026-12-09",
         nights=7,
         rateSource=VEN_BOOK, resortFeeSource=VEN_FEE, taxSource=CLARK_TAX,
         roomRates=[2024.25, 1124.25, 756.75, 779.25, 231.75, 404.25, 404.25],
         roomSubtotal=5837.25, resortFeePerNight=55.0, resortFeeTotal=385.0,
         taxes=817.46, checkoutTotal=6927.21, displayedAverageNightly=872.82,
         avgIncludes="Resort fee, excludes tax",
         taxRate=0.1338, parking="Not published on an official page we could retrieve; "
                               "Venetian Rewards Sapphire tier and above includes complimentary "
                               "self and event parking (venetianlasvegas.com Rewards page, read 2026-11-17).",
         cancellation="Not captured on the quote screen; must be read on the rate rules screen "
                      "before booking.",
         timestamp=RETRIEVED, quality="Describes itself as a Forbes 4-Star resort; suite is 650 sq ft.",
         excerpt="\u201cEstimated cost of stay: $6,927.21\u201d with nightly breakdown "
                 "$2,024.25 / $1,124.25 / $756.75 / $779.25 / $231.75 / $404.25 / $404.25, "
                 "resort fee $55.00 each night, taxes $817.46.",
         notes=["Tax of $817.46 on $5,837.25 of room revenue is 14.0%; on room + resort fee "
                "($6,222.25) it is 13.14%. Both bracket the official 13.38% resort-hotel rate, so "
                "the quote is internally consistent with the county rate.",
                "Nightly average $872.82 includes the resort fee but excludes tax by the site's own footnote."]),
    dict(venue="Wynn Las Vegas", slug="wynn", room="Wynn Resort King",
         occupancy="2 adults, 1 room", checkin="2026-12-02", checkout="2026-12-09", nights=7,
         rateSource=WYNN_BOOK, resortFeeSource=WYNN_TERMS, taxSource=CLARK_TAX,
         roomRates=None, roomSubtotal=None, resortFeePerNight=55.0, resortFeeTotal=None,
         taxes=None, checkoutTotal=None, displayedAverageNightly=711.0,
         avgIncludes="Resort fee, excludes tax",
         taxRate=0.1338,
         parking="Resort fee includes complimentary self-parking for up to two vehicles "
                 "(Wynn terms page, read 2026-11-17).",
         cancellation="Not captured; the offer terms read are non-refundable / non-changeable, "
                      "so confirm the rate rules on the booking screen.",
         timestamp="2026-11-16 (prior capture) + 2026-11-17 fee check",
         quality="Forbes Travel Guide Four-Star (2026 profile); 640 sq ft resort king.",
         excerpt="Booking engine showed a rounded average of $711 per night including the $55 "
                 "resort fee and excluded taxes; the engine did not render an exact 7-night "
                 "after-tax total on the day it was read.",
         notes=["Checkout total deliberately left blank rather than estimated: an average rate is "
                "not a total and the user asked for real checkout totals.",
                "The Wynn booking engine is JavaScript-only, so it cannot be re-checked by the "
                "scheduled link checker; the link is kept for manual review."]),
    dict(venue="Bellagio", slug="bellagio", room=None, occupancy=None, checkin="2026-12-02",
         checkout="2026-12-09", nights=7, rateSource=None, resortFeeSource=None,
         taxSource=CLARK_TAX, roomRates=None, roomSubtotal=None, resortFeePerNight=55.0,
         resortFeeTotal=None, taxes=None, checkoutTotal=None, displayedAverageNightly=None,
         avgIncludes=None, taxRate=0.1338, parking=None, cancellation=None,
         timestamp=RETRIEVED,
         quality="AAA Four Diamond (2026) per prior-session capture; not re-verified today.",
         excerpt="Resort fee of $55 per night plus tax is the published MGM baseline for this "
                 "property per the prior session's capture; not re-read on an official MGM page today.",
         notes=["No checkout total could be retrieved, so the field is blank.",
                "MGM parking page URL used by earlier sessions now returns a 404."]),
    dict(venue="Resorts World Las Vegas", slug="resorts-world", room=None, occupancy=None,
         checkin="2026-12-02", checkout="2026-12-09", nights=7, rateSource=None,
         resortFeeSource=None, taxSource=CLARK_TAX, roomRates=None, roomSubtotal=None,
         resortFeePerNight=None, resortFeeTotal=None, taxes=None, checkoutTotal=None,
         displayedAverageNightly=None, avgIncludes=None, taxRate=0.1338, parking=None,
         cancellation=None, timestamp=RETRIEVED,
         quality="Not verified this session.",
         excerpt="No official rate or resort-fee page was retrieved today; every figure is blank.",
         notes=["Listed only because the brief asks for more than two venues; it is inside the "
                "30-minute walk band to the Wynn poker room and about 25 minutes to the Venetian."]),
]

# ---------------------------------------------------------------- Walking routes
routes = [
    dict(pair="The Venetian \u2194 Wynn Las Vegas", miles=0.5, minutes="10\u201315",
         path="Through the Palazzo, then across the Sands Avenue pedestrian bridge",
         within30=True, source=COMPASS,
         note="Cash-game-to-cash-game, door to door. Add 5\u201310 min for the poker rooms at "
              "either end."),
    dict(pair="The Venetian \u2194 Bellagio", miles=0.9, minutes="18\u201325",
         path="Strip walk over the Las Vegas Blvd and Flamingo Rd pedestrian bridges",
         within30=True, source=COMPASS,
         note="Upper end of the estimate plus lobby time can reach 30 minutes; treat as marginal."),
    dict(pair="Bellagio \u2194 Caesars Palace", miles=0.4, minutes="10\u201315",
         path="Flamingo Road pedestrian bridge", within30=True, source=COMPASS, note=""),
    dict(pair="Wynn \u2194 Resorts World", miles=None, minutes="12\u201318",
         path="Outdoors across Las Vegas Blvd", within30=True, source=COMPASS, note=""),
    dict(pair="The Venetian \u2194 Caesars Palace", miles=None, minutes="12\u201318",
         path="East-side sidewalk south along Las Vegas Blvd", within30=True, source=COMPASS,
         note="Caesars Palace runs a $100 daily tournament with a paid add-on, so it is in the "
              "excluded section."),
    dict(pair="The Venetian \u2194 Bellagio via Caesars", miles=None, minutes="12\u201318 + 10\u201315",
         path="Two legs; indoor cut-through at Caesars possible", within30=True, source=COMPASS,
         note="Only useful if you are willing to walk through a casino to save heat."),
]

# ---------------------------------------------------------------- Flags
flags = [
    dict(id="S01", severity="blocker",
         title="No Las Vegas Strip event is published as a true freezeout",
         detail="Across all 37 Venetian structure sheets and every Wynn terms sheet that the WPT "
                "posted, not one event states \u201cno re-entry\u201d or \u201cfreezeout\u201d. "
                "Two Venetian events are explicitly re-entry-priced (#18, #58: \u201cAll subsequent "
                "buy in's after the initial buy in will be $200\u201d) and every Wynn event with a "
                "terms sheet states unlimited re-entry. The strict single-entry list is therefore "
                "empty of confirmed rows, and every candidate is shown as unverified rather than "
                "promoted.",
         sources=[VEN_STRUCT.format(n=8), WYNN_STRUCT],
         action="Ask each poker room, in writing, whether the event is a freezeout. Until an "
                "official page says so, treat \u201cunverified\u201d rows as possibly re-entry."),
    dict(id="S02", severity="blocker",
         title="The 8:00 a.m. start goal cannot be met on the Strip",
         detail="Earliest official start found: Venetian 9:10 a.m. (event #46, Dec 12) and "
                "Venetian 10:10 a.m. for the regular slate; Wynn 10:00 a.m. (Super Gold Million, "
                "Dec 10\u201311); Horseshoe 9:00 a.m. (daily, per Caesars' own article). Nothing on "
                "an official page starts at 8:00 a.m.",
         sources=[VEN_SCHEDULE, WYNN_SCHED, CAESARS_ARTICLE],
         action="Either accept a 9:10 a.m. first start or add an off-Strip room with a pre-9 a.m. "
                "start once verified."),
    dict(id="S03", severity="review",
         title="Bellagio weekly event carries three different buy-ins in one PDF",
         detail="The Bellagio Saturday PDF is titled \u201cNLH $1100 BUY-IN\u201d, is linked from "
                "the poker page as \u201cSATURDAYS | $1,000 NLH\u201d, and rule 07 says \u201cOf the "
                "$600 Buy-in, $510 goes to the Prize Pool\u201d. The same sheet has stale dates "
                "(Day 2 \u201c9/13/26\u201d), so the sheet appears to be an un-updated template.",
         sources=[BELLAGIO_SAT, BELLAGIO_POKER],
         action="Confirm the actual Saturday buy-in with the Bellagio poker room before budgeting."),
    dict(id="S04", severity="review",
         title="Bellagio's optional $40 gratuity buys 20,000 extra chips",
         detail="Rule 09: \u201cThe voluntary staff gratuity will grant players an extra 20,000 "
                "chips.\u201d A $40 payment inside the $600 structure therefore buys a 50% larger "
                "starting stack - exactly the pay-for-advantage case the brief wants separated.",
         sources=[BELLAGIO_SAT],
         action="Keep Bellagio and Caesars out of the strict list; they are documented in the "
                "Advantage Events section."),
    dict(id="S05", severity="review",
         title="Caesars Palace advertises a paid add-on",
         detail="Caesars' own article: $100 buy-in, 20,000 chips, $1,000 GTD, and \u201ca $50 "
                "add-on at the first break gives you an extra 15,000 chips\u201d. No official "
                "structure sheet PDF was found, so the level and late-reg details are unverified.",
         sources=[CAESARS_ARTICLE],
         action="Request the official structure sheet; do not budget Caesars until then."),
    dict(id="S06", severity="review",
         title="Wynn does not publish terms for events after Dec 15",
         detail="The posted WPT World Championship Structures PDF ends at the $1,600 PLO Mystery "
                "Bounty ($500,000 GTD). Entry rules for the $10,400 World Championship, both "
                "$10,500 events, the $25,800 High Roller, Seniors, Ladies, Super Gold Million and "
                "the $1,000/$2,000/$3,000 NLH events are therefore blank.",
         sources=[WYNN_STRUCT, WYNN_SCHED],
         action="Re-check wynnpoker.com weekly; Wynn updates the structures link in place."),
    dict(id="S07", severity="review",
         title="Wynn schedule says World Championship registration stays open into Day 2",
         detail="The schedule row for Dec 16 reads \u201cWPT World Championship Day 2 (Registration "
                "open until the start of Day 2)\u201d. Late registration running into Day 2 is a "
                "material difference from a normal freezeout and is recorded as an excerpt, not "
                "interpreted.",
         sources=[WYNN_SCHED],
         action="Confirm with Wynn whether a Day-2 entrant pays a fresh $10,400 and starts at a "
                "shorter stack."),
    dict(id="S08", severity="review",
         title="Venetian resort fee is published as \u201crates include\u201d but the booking "
                "engine adds it per night",
         detail="The resort-fee page says \u201cRates include a daily Resort Fee of $55 plus tax "
                "per night, payable upon check-in\u201d, while the booking breakdown lists $55.00 as "
                "a separate line for each night and then applies 13.38% tax on the total.",
         sources=[VEN_FEE, VEN_BOOK, CLARK_TAX],
         action="Treat $55 + 13.38% as an unavoidable per-night charge; verify at check-in."),
    dict(id="S09", severity="review",
         title="LIPS events carry a flat fee that is neither prize pool nor house fee",
         detail="Structure sheets #31, #32 and #33 add a $10 (or $20 for #39) LIPS fee, so the "
                "buy-in does not equal pool plus house fee. The fee is recorded separately and the "
                "derived \u201cfee\u201d field is left blank for those events.",
         sources=[VEN_STRUCT.format(n=31), VEN_STRUCT.format(n=32), VEN_STRUCT.format(n=33)],
         action="Budget buy-in + LIPS fee when comparing cost per dollar of prize pool."),
    dict(id="S10", severity="info",
         title="Venetian multi-flight events are explicitly multi-entry",
         detail="Sheets #2, #3, #4, #9, #10, #12, #20, #21 and #35 all contain the "
                "\u201cbags for Day 2 may not play subsequent flight\u201d rule, which presumes a "
                "player can buy into more than one flight.",
         sources=[VEN_STRUCT.format(n=2), VEN_STRUCT.format(n=12), VEN_STRUCT.format(n=21)],
         action="None; they are excluded from the strict list and listed separately."),
    dict(id="S11", severity="info",
         title="Venetian event #40 row was truncated in the baseline capture - now resolved",
         detail="Prior flag F02 said event #40's name, time and buy-in were lost. Structure sheet "
                "#27 confirms $600 PLO Bounty $25,000 GTD and the schedule shows Dec 10, 12:10 p.m.",
         sources=[VEN_STRUCT.format(n=27), VEN_SCHEDULE],
         action="Closed; no further action."),
    dict(id="S12", severity="blocker",
         title="No official parking or cancellation page retrievable for the Venetian",
         detail="venetianlasvegas.com/resort/parking.html returns 404 and MGM's parking page also "
                "returns 404. Cancellation deadlines are only visible on the rate-rules screen of "
                "the booking flow, which is not linkable.",
         sources=[VEN_FEE],
         action="Read the rate rules at checkout and screenshot the cancellation deadline."),
]

questions = [
    dict(q="Is each candidate event a freezeout, and can the poker room put that in writing?",
         why="No official document on the Strip says \u201cno re-entry\u201d, which is the core of "
             "the brief. Everything else is a comparison between events that might allow a second "
             "buy-in.",
         how="Email or call the poker room; ask for the event terms, not the marketing page.",
         status="open"),
    dict(q="Does the planned trip include a weekend?",
         why="Saturday/Sunday carries the biggest guarantees (Wynn $1M flights, Venetian $500K) "
             "but also the highest hotel rates - the Venetian night of Dec 5 is $779.25 versus "
             "$231.75 on Dec 6.",
         how="Set exact dates; the calendar grid on the booking engine shows per-night prices "
             "before you commit.",
         status="open"),
    dict(q="What is the maximum acceptable cost per tournament hour?",
         why="A $600 one-day event with 40-minute levels runs roughly 10-12 hours; a $200 turbo "
             "runs 5-6. Cost per hour, not buy-in, separates the two.",
         how="Use the trip calculator on this site and sort by cost per level.",
         status="open"),
    dict(q="Will the player take the Bellagio $40 chip-gratuity or Caesars $50 add-on?",
         why="Both buy an advantage; if yes, those venues belong in the plan and the strict list "
             "must be described as a preference, not a constraint.",
         how="Decide before comparing; mixing them makes the ranking meaningless.",
         status="open"),
    dict(q="Which hotel tier is required - Venetian suite or a standard Wynn king?",
         why="Same 7 nights: Venetian $6,927.21 all-in versus Wynn's $711 average room rate "
             "before tax. Venetian includes a 650 sq ft suite; Wynn includes self-parking.",
         how="Book refundable rates on both and compare after tax at checkout.",
         status="open"),
    dict(q="Can a 9:10 a.m. start replace the 8:00 a.m. goal?",
         why="Nothing on the Strip starts at 8. The earliest verified start is 9:10 a.m.",
         how="Confirm with the Venetian that event #46's 9:10 a.m. satellite runs on Dec 12, or "
             "accept 10:10 a.m.",
         status="open"),
    dict(q="What happens if a day's primary event is a multi-flight bag?",
         why="Bagging Day 1 forces attendance on Day 2, which can collide with the next day's "
             "primary event.",
         how="Prefer one-day events as primaries and keep flights as conditionals.",
         status="open"),
    dict(q="Is a rental car or rideshare budget needed for Resorts World?",
         why="Resorts World is 12-18 minutes on foot from Wynn, but nothing else is that close; "
             "if the plan expands south, walking stops working.",
         how="Price a 7-day rideshare estimate and compare with parking fees.",
         status="blocked-by-info"),
]

suggestions = [
    dict(id="G01", title="Publish a per-event cost-per-hour column",
         body="Buy-in alone hides the difference between a 20-minute-level turbo and a 40-minute "
              "structure. Deriving hours from levels \u00d7 level length and dividing buy-in by "
              "hours gives a fair comparison. The dashboard already stores level length for every "
              "row, so this is a display change only.",
         effort="S", impact="High"),
    dict(id="G02", title="Ask the rooms for written freezeout confirmations in one batch",
         body="A single email template to Venetian, Wynn, Bellagio, Caesars and Resorts World "
              "asking \u201cis this event single-entry, and what is the late-registration cut-off\u201d "
              "would convert the largest block of unverified rows in one pass.",
         effort="S", impact="High"),
    dict(id="G03", title="Track the Venice/Wynn structure PDFs by checksum",
         body="Both rooms update their structure PDFs in place. The scheduled worker already "
              "hashes each URL; surfacing the hash change date next to each event would show "
              "exactly when a rule changed.",
         effort="S", impact="Medium"),
    dict(id="G04", title="Add a like-for-like hotel comparison at one length of stay",
         body="Seven nights, two adults, one room is the current baseline. Adding 3- and 5-night "
              "variants at the same check-in date makes the weekend premium visible instead of "
              "averaged away.",
         effort="M", impact="High"),
    dict(id="G05", title="Model the bag risk for multi-flight primaries",
         body="If a Day 1 is bagged, the next day is committed. A simple flag that a chosen "
              "primary has a Day 2 on the following day would stop the planner proposing an "
              "impossible sequence.",
         effort="M", impact="Medium"),
    dict(id="G06", title="Add an off-Strip section",
         body="The 8 a.m. goal and the no-advantage-purchase rule both point off-Strip, where "
              "rooms publish true freezeouts more often. This is the single largest coverage gap.",
         effort="L", impact="High"),
]

data = dict(
    session="6d1e0039", retrieved=RETRIEVED, generatedFor="Las Vegas Strip, Nov 16 - Dec 23 2026",
    venetianSingles=ven_events, venetianMulti=ven_multi, venetianSatellites=ven_sats,
    wynn=wynn_events, other=other_events, hotels=hotel_log, routes=routes,
    flags=flags, questions=questions, suggestions=suggestions,
)
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "events.json"), "w") as f:
    json.dump(data, f, indent=1)

# compact mirror used by the re-check script (url -> hash of expectations)
urls = sorted({VEN_SCHEDULE, VEN_FEE, WYNN_SCHED, WYNN_STRUCT, WYNN_TERMS, WYNN_POKER,
               BELLAGIO_POKER, BELLAGIO_SAT, CAESARS_ARTICLE, CLARK_TAX, COMPASS}
              | {VEN_STRUCT.format(n=n) for n in range(1, 38)})
with open(os.path.join(OUT, "sources.json"), "w") as f:
    json.dump(dict(retrieved=RETRIEVED, urls=urls), f, indent=1)

print("venetian singles:", len(ven_events), "multi:", len(ven_multi), "sats:", len(ven_sats))
print("wynn:", len(wynn_events), "other:", len(other_events), "hotels:", len(hotel_log))
print("sources:", len(urls))
