"""
Verified dataset for the Las Vegas Strip poker planner.

Rules used for every value
- A value is entered only if an official page or PDF listed below states it (fetched 2026-11-16).
- If a value is not stated by an official source it is left as None and flagged as unverified.
- Nothing is inferred, computed from third-party data, or copied from memory of other events.
- Walk times are the ONLY non-official numbers. They are labelled "estimate" everywhere.

Event numbers are the official Venetian DeepStack Extravaganza IV event numbers.
"""

AS_OF = "2026-11-16"

# ---------- Official sources (each was opened during this session) ----------
SRC = {
    # Venetian / Palazzo
    "dse_page": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
    "dse_pdf": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf",
    "venetian_poker": "https://www.venetianlasvegas.com/resort/casino/poker.html",
    "venetian_suite": "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
    # Wynn
    "wynn_poker": "https://www.wynnlasvegas.com/casino/poker",
    "wynn_poster": "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf",
    "wynn_daily_structs": "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf",
    "wynn_wpt_sched": "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
    "wynn_terms": "https://www.visitwynn.com/tc/index.cfm?term_id=850250",
    # Bellagio
    "bellagio_poker": "https://bellagio.mgmresorts.com/en/casino/poker.html",
    "bellagio_fri": "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf",
    "bellagio_sat": "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
    "bellagio_sun": "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf",
    # Others
    "aria_poker": "https://aria.mgmresorts.com/en/casino/poker.html",
    "mgmgrand_404": "https://mgmgrand.mgmresorts.com/en/casino/poker.html",
    "wsop_schedule": "https://www.wsop.com/schedule/",
}


def sheet(n: int) -> str:
    """Official Venetian DSE IV structure sheet N (URL pattern taken from the official event page)."""
    return f"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf"


# Structure sheets that were OPENED and READ this session. Every sheet cited in a table row is in this dict.
# house = $ withheld for house fees per the sheet; pool = $ to prize pool per the sheet.
SHEETS_READ = {
    1: dict(name="$200 NLH Bounty (1Day), $50 starting bounty", house=40, pool=160, late_reg="8 levels + break (9:40 PM)", chips=25000, rebuy=None),
    5: dict(name="$300 NLH (1Day)", house=58, pool=242, late_reg=None, chips=None, rebuy=None),
    6: dict(name="$400 NLH (1Day)", house=65, pool=335, late_reg=None, chips=None, rebuy=None),
    7: dict(name="$600 NLH (1Day)", house=90, pool=510, late_reg=None, chips=None, rebuy=None),
    8: dict(name="$200 NLH Valuetown Bounty (1Day), $50 bounties; PokerAtlas PRO $20 off initial buy-in only", house=40, pool=160, late_reg="8 levels + break (9:40 PM)", chips=25000, rebuy=None),
    11: dict(name="$600 NLH Bounty (1Day): $200 bounties to start, $500 once in the money", house=90, pool=510, late_reg="10 levels + break (4:55 PM)", chips=40000, rebuy=None),
    15: dict(name="$300 NLH Bounty (1Day), $100 bounty per knockout", house=50, pool=250, late_reg="8 levels + break (9:40 PM)", chips=25000, rebuy=None),
    16: dict(name="$800 NLH Bounty (1Day): $200 bounties to start, $500 once in the money", house=100, pool=700, late_reg="10 levels + break (4:55 PM)", chips=40000, rebuy=None),
    17: dict(name="$600 NLH Seniors (1Day), 50+ only", house=90, pool=510, late_reg="10 levels + break (~3:55 PM)", chips=40000, rebuy=None),
    18: dict(name="$200 NLH RaceDay Stack (1Day)", house=35, pool=165, late_reg=None, chips=30000, rebuy=None),
    26: dict(name="$400 Pot Limit Omaha Bounty (1Day), $100 bounty", house=60, pool=340, late_reg="8 levels + break (~4:40 PM)", chips=30000, rebuy=None),
    28: dict(name="$600 Big O (1Day)", house=90, pool=510, late_reg="8 levels + break (~4:40 PM)", chips=30000, rebuy=None),
    29: dict(name="$200 NLH (1Day)", house=40, pool=160, late_reg=None, chips=None, rebuy=None),
    30: dict(name="$200 NLH (1Day) Progressive Knock-Out Bounty (PKO), $50 starting bounty", house=40, pool=160, late_reg="8 levels + break (9:40 PM)", chips=25000, rebuy=None),
    34: dict(name="$1,100 NLH (1Day) Progressive Knock-Out Bounty (PKO), $200 starting bounty", house=130, pool=970, late_reg="10 levels + break (4:55 PM)", chips=40000, rebuy=None),
}

# ---------- SINGLE-ENTRY (verified) : Venetian DeepStack Extravaganza IV ----------
# Every row: official event #, date, start time, official name, buy-in, guarantee (None if the official schedule shows none),
# registration close time, structure sheet # (read), house fee & prize pool (from the sheet), chips.
# Schedule source: DSE PDF. Structure source: the sheet listed.
SINGLE_ENTRY = [
    dict(event=2, date="2026-11-18", start="11:10 AM", name="$300 No Limit Hold'em (1Day)", buyin=300, gtd=10000, reg_close="4:55 PM", chips=40000, sheet=5),
    dict(event=3, date="2026-11-19", start="10:10 AM", name="$200 NLH RaceDay Stack (1Day)", buyin=200, gtd=None, reg_close="12:25 PM", chips=30000, sheet=18),
    dict(event=4, date="2026-11-20", start="10:10 AM", name="$200 NLH RaceDay Stack (1Day)", buyin=200, gtd=None, reg_close="12:25 PM", chips=30000, sheet=18),
    dict(event=5, date="2026-11-21", start="10:10 AM", name="$200 NLH RaceDay Stack (1Day)", buyin=200, gtd=None, reg_close="12:25 PM", chips=30000, sheet=18),
    dict(event=6, date="2026-11-22", start="11:10 AM", name="$200 No Limit Hold'em (1Day)", buyin=200, gtd=None, reg_close="3:40 PM", chips=30000, sheet=29),
    dict(event=8, date="2026-11-23", start="5:10 PM", name="$200 NLH (1Day) Progressive Knock-Out Bounty (PKO)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=30),
    dict(event=9, date="2026-11-24", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=10, date="2026-11-25", start="11:10 AM", name="$400 No Limit Hold'em (1Day)", buyin=400, gtd=15000, reg_close="4:55 PM", chips=40000, sheet=6),
    dict(event=11, date="2026-11-25", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=12, date="2026-11-26", start="11:10 AM", name="$300 No Limit Hold'em (1Day)", buyin=300, gtd=10000, reg_close="4:55 PM", chips=40000, sheet=5),
    dict(event=13, date="2026-11-26", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=14, date="2026-11-27", start="11:10 AM", name="$600 No Limit Hold'em (1Day)", buyin=600, gtd=30000, reg_close="4:55 PM", chips=40000, sheet=7),
    dict(event=15, date="2026-11-27", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=16, date="2026-11-28", start="11:10 AM", name="$600 NLH Bounty (1Day)", buyin=600, gtd=30000, reg_close="4:55 PM", chips=40000, sheet=11),
    dict(event=17, date="2026-11-28", start="12:10 PM", name="$400 Pot Limit Omaha Bounty (1Day)", buyin=400, gtd=15000, reg_close="4:40 PM", chips=30000, sheet=26),
    dict(event=18, date="2026-11-28", start="5:10 PM", name="$200 NLH PokerAtlas Valuetown Bounty (1Day)", buyin=200, gtd=20000, reg_close="9:40 PM", chips=25000, sheet=8),
    dict(event=21, date="2026-11-29", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=22, date="2026-11-30", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=23, date="2026-12-01", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=24, date="2026-12-02", start="10:10 AM", name="$600 NLH Seniors (1Day) - 50+ only", buyin=600, gtd=40000, reg_close="3:55 PM", chips=40000, sheet=17),
    dict(event=25, date="2026-12-02", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=27, date="2026-12-03", start="12:10 PM", name="$600 Big O (1Day)", buyin=600, gtd=25000, reg_close="4:40 PM", chips=30000, sheet=28),
    dict(event=28, date="2026-12-06", start="11:10 AM", name="$600 No Limit Hold'em (1Day)", buyin=600, gtd=40000, reg_close="4:55 PM", chips=40000, sheet=7),
    dict(event=29, date="2026-12-06", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=30, date="2026-12-07", start="11:10 AM", name="$600 NLH Bounty (1Day)", buyin=600, gtd=40000, reg_close="4:55 PM", chips=40000, sheet=11),
    dict(event=31, date="2026-12-07", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=32, date="2026-12-08", start="10:10 AM", name="$600 NLH Seniors (1Day) - 50+ only", buyin=600, gtd=40000, reg_close="3:55 PM", chips=40000, sheet=17),
    dict(event=34, date="2026-12-08", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=36, date="2026-12-09", start="11:10 AM", name="$800 NLH Bounty (1Day)", buyin=800, gtd=75000, reg_close="4:55 PM", chips=40000, sheet=16),
    dict(event=38, date="2026-12-09", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=42, date="2026-12-10", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=50, date="2026-12-13", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=51, date="2026-12-14", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=52, date="2026-12-15", start="11:10 AM", name="$1,100 NLH (1Day) Progressive Knock-Out Bounty (PKO)", buyin=1100, gtd=75000, reg_close="4:55 PM", chips=40000, sheet=34),
    dict(event=53, date="2026-12-15", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=54, date="2026-12-16", start="11:10 AM", name="$600 NLH Bounty (1Day)", buyin=600, gtd=50000, reg_close="4:55 PM", chips=40000, sheet=11),
    dict(event=55, date="2026-12-16", start="5:10 PM", name="$300 NLH Bounty (1Day)", buyin=300, gtd=15000, reg_close="9:40 PM", chips=25000, sheet=15),
    dict(event=58, date="2026-12-19", start="5:10 PM", name="$200 NLH PokerAtlas Valuetown Bounty (1Day)", buyin=200, gtd=20000, reg_close="9:40 PM", chips=25000, sheet=8),
    dict(event=60, date="2026-12-20", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=61, date="2026-12-21", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=62, date="2026-12-22", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
    dict(event=63, date="2026-12-23", start="11:10 AM", name="$600 No Limit Hold'em (1Day)", buyin=600, gtd=30000, reg_close="4:55 PM", chips=40000, sheet=7),
    dict(event=64, date="2026-12-23", start="5:10 PM", name="$200 NLH Bounty (1Day)", buyin=200, gtd=8000, reg_close="9:40 PM", chips=25000, sheet=1),
]

# Venetian single-entry events whose sheet rule text was read in this session: none of them contains re-entry,
# rebuy, add-on, optional chip purchase, or subsequent-flight language. (Sheets 1,5,6,7,8,11,15,16,17,18,26,28,29,30,34.)
# Venetian sheets 5, 6, 7, 18, 29 were read in an earlier pass of this session; their house/pool numbers are used only
# where the sheet gives them (see SHEETS_READ).

# ---------- MULTI-ENTRY / REBUY / ADD-ON / PAID-ADVANTAGE (separate section) ----------
MULTI_ENTRY = [
    dict(venue="Wynn Las Vegas", name="Monday–Thursday NLH", start="12:00 PM", buyin=200, gtd=10000,
         rule="Re-entry at the same $200 fee until the start of level 9 (official daily structure sheet).",
         kind="Re-entry", src="wynn_daily_structs", src2="wynn_poster"),
    dict(venue="Wynn Las Vegas", name="Friday NLH Rebuy & Add-on", start="12:00 PM", buyin=240, gtd=40000,
         rule="Unlimited $200 rebuys while at 15,000 chips or less, and one $100 add-on. The sheet also says 'Re-entry is NOT allowed'; that wording conflicts with the rebuy rule (flagged).",
         kind="Rebuy + add-on", src="wynn_daily_structs", src2="wynn_poster"),
    dict(venue="Wynn Las Vegas", name="Saturday NLH", start="12:00 PM", buyin=200, gtd=25000,
         rule="Re-entry at $200 until the start of level 9 (official daily structure sheet).",
         kind="Re-entry", src="wynn_daily_structs", src2="wynn_poster"),
    dict(venue="Wynn Las Vegas", name="Sunday NLH", start="12:00 PM", buyin=200, gtd=25000,
         rule="Re-entry at $200 until the start of level 9 (official daily structure sheet).",
         kind="Re-entry", src="wynn_daily_structs", src2="wynn_poster"),
    dict(venue="Wynn Las Vegas", name="Nightly NLH", start="6:00 PM", buyin=160, gtd=10000,
         rule="Entry and re-entry fee are both $160; one $100 add-on; registration, re-entries and add-on until the start of level 9 (about 9:00 PM). Fee split $20 tournament fee, $10 staff, $130 prize pool.",
         kind="Re-entry + add-on", src="wynn_daily_structs", src2="wynn_poster"),
    dict(venue="Bellagio", name="Friday NLH $600", start="11:00 AM", buyin=600, gtd=None,
         rule="Buy-in and re-entry through the end of level 8. $600 = $510 prize pool + $50 admin fee + $40 OPTIONAL staff gratuity, which grants 15,000 extra chips. Guarantee not stated.",
         kind="Re-entry + paid chips", src="bellagio_fri", src2="bellagio_poker"),
    dict(venue="Bellagio", name="Saturday NLH (flights 1A–1C and D)", start="11:00 AM", buyin=None, gtd=None,
         rule="Sheet header says '$1100 BUY-IN'; its rule 07 says '$600 Buy-in'; its file name says $1000. Buy-in CONFLICT, so left blank. Optional $40 gratuity grants 20,000 extra chips. Each flight plays to the money.",
         kind="Flights + paid chips + buy-in conflict", src="bellagio_sat", src2="bellagio_poker"),
    dict(venue="Bellagio", name="Sunday H.O.R.S.E. $400", start="11:00 AM", buyin=400, gtd=None,
         rule="Buy-in and re-entry through the end of level 8. $400 = $340 prize pool + $35 house fee + $25 OPTIONAL staff gratuity, which grants 15,000 extra chips. Guarantee not stated.",
         kind="Re-entry + paid chips", src="bellagio_sun", src2="bellagio_poker"),
]

# ---------- UNVERIFIED FORMAT (not in the ranking) ----------
# Venetian events whose structure sheet was NOT read in this session, or whose official name marks them as flights,
# satellites, tag-team or two-day events. Values are from the official schedule PDF only.
UNVERIFIED_VENETIAN = [
    dict(event=1, date="2026-11-16 to 2026-11-17", start="11:10 AM / 5:10 PM", name="$300 NLH 1A/1B/1C/1D flights", buyin=300, gtd=75000, reg_close="3:40 PM / 8:40 PM", kind="Flight format", sheets="10 (1A, 1C), 9 (1B, 1D)"),
    dict(event=7, date="2026-11-23 to 2026-11-25", start="11:10 AM", name="$400 NLH 1A/1B flights + Day 2 restart", buyin=400, gtd=75000, reg_close="5:55 PM", kind="Flight format", sheets="2"),
    dict(event=19, date="2026-11-29 to 2026-12-01", start="11:10 AM", name="$400 NLH 1A/1B/1C flights + Day 2 restart Dec 2", buyin=400, gtd=75000, reg_close="5:55 PM", kind="Flight format", sheets="3"),
    dict(event=26, date="2026-12-03 to 2026-12-06", start="11:10 AM", name="$800 NLH 1A–1F flights + Day 2 restart Dec 6", buyin=800, gtd=500000, reg_close="3:40 PM / 8:40 PM", kind="Flight format", sheets="12, 13, 14"),
    dict(event=47, date="2026-12-12 to 2026-12-14", start="10:10 AM", name="$2,200 NLH PokerAtlas Championship 1A/1B flights + Day 2/3 restarts", buyin=2200, gtd=1000000, reg_close="4:55 PM / 11:10 PM", kind="Flight format", sheets="21, 37"),
    dict(event=49, date="2026-12-13 to 2026-12-15", start="10:10 AM", name="$1,100 NLH Seniors 1A/1B flights (50+) + Day 2 restart", buyin=1100, gtd=300000, reg_close="4:55 PM", kind="Flight format (50+)", sheets="20"),
    dict(event=56, date="2026-12-17 to 2026-12-20", start="10:10 AM", name="$1,100 NLH 1A–1E flights + Day 2 restart Dec 20", buyin=1100, gtd=500000, reg_close="4:55 PM / 11:10 PM", kind="Flight format", sheets="35, 36"),
    dict(event=59, date="2026-12-20 to 2026-12-23", start="11:10 AM", name="$600 NLH 1A/1B/1C flights + Day 2 restart Dec 23", buyin=600, gtd=150000, reg_close="5:55 PM", kind="Flight format", sheets="4"),
    dict(event=33, date="2026-12-08", start="4:10 PM", name="$100 NLH LIPS Ladies Milestone Satellite (2 seats)", buyin=100, gtd=None, reg_close="6:25 PM", kind="Satellite (awards entry to #39)", sheets="19"),
    dict(event=37, date="2026-12-09", start="4:10 PM", name="$100 NLH LIPS Ladies Milestone Satellite (2 seats)", buyin=100, gtd=None, reg_close="6:25 PM", kind="Satellite (awards entry to #39)", sheets="19"),
    dict(event=41, date="2026-12-10", start="4:10 PM", name="$260 NLH Milestone Satellite (2 seats)", buyin=260, gtd=None, reg_close="6:25 PM", kind="Satellite (awards entry to #47)", sheets="24"),
    dict(event=44, date="2026-12-11", start="4:10 PM", name="$260 NLH Milestone Satellite (2 seats)", buyin=260, gtd=None, reg_close="6:25 PM", kind="Satellite (awards entry to #47)", sheets="24"),
    dict(event=45, date="2026-12-11", start="8:10 PM", name="$260 NLH Turbo Milestone Satellite (2 seats)", buyin=260, gtd=None, reg_close="9:55 PM", kind="Satellite (awards entry to #47)", sheets="25"),
    dict(event=46, date="2026-12-12", start="9:10 AM", name="$260 NLH Turbo Milestone Satellite (2 seats)", buyin=260, gtd=None, reg_close="10:55 AM", kind="Satellite (awards entry to #47)", sheets="25"),
    dict(event=48, date="2026-12-12", start="12:10 PM", name="$260 NLH Turbo Milestone Satellite (2 seats)", buyin=260, gtd=None, reg_close="1:55 PM", kind="Satellite (awards entry to #47)", sheets="25"),
    dict(event=20, date="2026-11-29", start="12:10 PM", name="$300 PLO Double Board Bomb Pot (1Day)", buyin=300, gtd=10000, reg_close="4:40 PM", kind="PLO (format not read)", sheets="22"),
    dict(event=35, date="2026-12-09", start="10:10 AM", name="$600 NLH LIPS Poker Jingle Tag Team (1Day) - tag teams F/F or F/M", buyin=600, gtd=10000, reg_close="2:40 PM", kind="Tag team", sheets="31"),
    dict(event=39, date="2026-12-10 to 2026-12-11", start="10:10 AM", name="$800 NLH LIPS Ladies (2Day) - women's main event", buyin=800, gtd=40000, reg_close="4:55 PM", kind="Two-day, women's event", sheets="32"),
    dict(event=40, date="2026-12-10", start="12:10 PM", name="$600 Pot Limit Omaha Bounty (1Day)", buyin=600, gtd=25000, reg_close="4:40 PM", kind="PLO bounty (format not read)", sheets="27"),
    dict(event=43, date="2026-12-11", start="11:10 AM", name="$600 NLH LIPS Kings and Queens Bounty (1Day)", buyin=600, gtd=30000, reg_close="4:55 PM", kind="Bounty (format not read)", sheets="33"),
    dict(event=57, date="2026-12-17", start="12:10 PM", name="$600 Pot Limit Omaha Double Board Bomb Pot (1Day)", buyin=600, gtd=25000, reg_close="4:40 PM", kind="PLO (format not read)", sheets="23"),
]

# Wynn WPT World Championship (from the official WPT schedule PDF, chunk 1 of 2 only).
# Entry formats (flights, re-entry) were NOT read, so these are unverified and not ranked.
WYNN_WPT_UNVERIFIED = [
    dict(name="$600 NLH 1A (Nov 27, 11 a.m.)", buyin=600, gtd=400000, note="Flight code 1A; format not read."),
    dict(name="$800 NLH 1A (Nov 30)", buyin=800, gtd=1000000, note="Flight code 1A; format not read."),
    dict(name="$1,600 NLH 1A (Dec 3)", buyin=1600, gtd=1000000, note="Flight code 1A; format not read."),
    dict(name="$1,100 WPT Prime Championship 1A (Dec 5)", buyin=1100, gtd=5000000, note="Flight code 1A; format not read."),
    dict(name="$400 Super Gold Million Mystery Bounty (Dec 10–12)", buyin=400, gtd=3000000, note="Format not read."),
    dict(name="WPT World Championship Day 1A (Dec 13)", buyin=10400, gtd=None, note="Footnote: $1,000,000 added via ClubWPT Gold, which the footnote says is not available in Nevada. Flagged."),
    dict(name="$1,100 Ladies NLH Championship (Dec 13)", buyin=1100, gtd=250000, note="Footnote says $11,100. Conflict, flagged."),
]

# ---------- HOTELS ----------
# walk_min = estimate from public OpenStreetMap routing (see WALK_NOTE). Not an official value.
WALK_NOTE = ("Estimate only: OSRM foot route on OpenStreetMap data, measured to a reference point near the Venetian "
             "(-115.1693352, 36.1217073). That reference point and the Wynn origin are NOT sourced from an official page, "
             "so these times are unverified. Times assume 3 mph.")
OSRM_ROUTES = {
    "Wynn": ("https://router.project-osrm.org/route/v1/foot/-115.1654043,36.1266219;-115.1693352,36.1217073?overview=false", 1352.2),
    "Encore": ("https://router.project-osrm.org/route/v1/foot/-115.1648801,36.1294358;-115.1693352,36.1217073?overview=false", 1763.2),
    "Bellagio": ("https://router.project-osrm.org/route/v1/foot/-115.1770065,36.1131149;-115.1693352,36.1217073?overview=false", 1754.3),
    "ARIA": ("https://router.project-osrm.org/route/v1/foot/-115.1779977,36.1070287;-115.1693352,36.1217073?overview=false", 2941.3),
    "Resorts World": ("https://router.project-osrm.org/route/v1/foot/-115.1661576,36.1336945;-115.1693352,36.1217073?overview=false", 3387.2),
}

HOTELS = [
    dict(name="The Venetian / The Palazzo", walk_km=None, walk_min=None, walk_note="On site. The poker room is on level 2 of Grand Canal Shoppes in The Palazzo (official).",
         resort_fee="$55 per night stayed", fee_src="venetian_suite",
         base_rate="'As low as $119 and $209' (official). Conditional: six hours of live cash play or a $300+ tournament buy-in on each night stayed; blackout dates may apply; figures vary by date.",
         parking="Complimentary self-parking for non-registered guests who play 3+ hours (official, poker page).",
         src_price="venetian_suite", notes="Rate is not a date-specific price. Confirm the poker-rate play rule with the poker room (702.414.7657, official)."),
    dict(name="Wynn Las Vegas", walk_km=OSRM_ROUTES["Wynn"][1] / 1000, walk_min=17, walk_note="Estimate (not official).",
         resort_fee="$55 plus tax per room night (official Wynn terms, for Wynn Resort King and Two Queens)", fee_src="wynn_terms",
         base_rate=None, parking="Resort fee includes self-parking for up to two vehicles (same official terms).",
         src_price="wynn_terms", notes="The Wynn terms page is for an expired 2026 promotion (Concours package); fee must be re-confirmed on the live booking page."),
    dict(name="Encore at Wynn Las Vegas", walk_km=OSRM_ROUTES["Encore"][1] / 1000, walk_min=22, walk_note="Estimate (not official).",
         resort_fee=None, fee_src=None, base_rate=None, parking=None, src_price=None, notes="No official Encore page was read."),
    dict(name="Bellagio", walk_km=OSRM_ROUTES["Bellagio"][1] / 1000, walk_min=22, walk_note="Estimate (not official).",
         resort_fee=None, fee_src=None, base_rate=None, parking=None, src_price=None,
         notes="No official MGM resort-fee page was read. Official Bellagio poker page gives the room phone 702.693.7291."),
    dict(name="ARIA Resort & Casino", walk_km=OSRM_ROUTES["ARIA"][1] / 1000, walk_min=37, walk_note="Estimate (not official). Over 30 minutes.",
         resort_fee=None, fee_src=None, base_rate=None, parking=None, src_price=None, notes="Official ARIA poker page has no schedule; fees not read."),
    dict(name="Resorts World Las Vegas", walk_km=OSRM_ROUTES["Resorts World"][1] / 1000, walk_min=42, walk_note="Estimate (not official). Over 30 minutes.",
         resort_fee=None, fee_src=None, base_rate=None, parking=None, src_price=None, notes="No official poker page was retrievable; fees not read."),
]
