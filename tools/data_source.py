"""Hand-entered research data. Every row carries an official source URL or is marked unverified.

Single-entry status values:
  "verified"    - the event's official structure sheet was reviewed and shows no re-entry, rebuy or add-on terms
  "unverified"  - official schedule lists the event, but its structure sheet was NOT reviewed
Advantage types: "re-entry", "rebuy", "add-on", "purchased chips"
"""

AS_OF = "2026-11-16"

V = "https://www.venetianlasvegas.com"
S_SCHED = V + "/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"
S_PAGE = V + "/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
S_SERIES = V + "/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"
S_POKER = V + "/resort/casino/poker.html"

def struct(n):
    return f"{V}/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf"

WYNN_POKER = "https://www.wynnlasvegas.com/casino/poker"
WYNN_DAILY_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"
WYNN_DAILY_STRUCTS = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"
WYNN_WPT_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
WYNN_WPT_STRUCTS = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
WYNN_TERMS = "https://www.wynnlasvegas.com/terms-and-conditions/850257"
BEL_POKER = "https://bellagio.mgmresorts.com/en/casino/poker.html"
BEL_FRI = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-%24600-nlh.pdf"
BEL_SAT = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-%241000-nlh.pdf"
BEL_SUN = "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-%24400-horse.pdf"
CAE_FLYER = "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"
CAE_PAGE = "https://www.caesars.com/caesars-palace/casino"
ARIA_POKER = "https://aria.mgmresorts.com/en/casino/poker.html"
RW_POKER = "https://www.rwlasvegas.com/gaming/poker-room/poker-room-dining/"
WSOP_SCHED = "https://www.wsop.com/schedule/"

# ---- Venetian DeepStack Extravaganza IV (Nov 16 - Dec 23, 2026). Entry-level rows only
# (restarts / Day 2 / final-table rows are in the official PDF but not listed here).
# tuple: date, start, event#, name, buy-in ($), guarantee ($ or None), reg-close, structure#, status
#   status: "verified" | "unverified" | "satellite"
VEN = [
 ("2026-11-16","11:10 AM",1,"$300 No Limit Hold'em 1A",300,75000,"3:40 PM",10,"verified"),
 ("2026-11-16","5:10 PM",1,"$300 No Limit Hold'em 1B",300,75000,"8:40 PM",9,"unverified"),
 ("2026-11-17","11:10 AM",1,"$300 No Limit Hold'em 1C",300,75000,"3:40 PM",10,"verified"),
 ("2026-11-17","5:10 PM",1,"$300 No Limit Hold'em 1D",300,75000,"8:40 PM",9,"unverified"),
 ("2026-11-18","11:10 AM",2,"$300 No Limit Hold'em (1-Day)",300,10000,"4:55 PM",5,"verified"),
 ("2026-11-19","10:10 AM",3,"$200 NLH RaceDay Stack (1-Day), race to finish before the race",200,None,"12:25 PM",18,"unverified"),
 ("2026-11-20","10:10 AM",4,"$200 NLH RaceDay Stack (1-Day), race to finish before the race",200,None,"12:25 PM",18,"unverified"),
 ("2026-11-21","10:10 AM",5,"$200 NLH RaceDay Stack (1-Day), race to finish before the race",200,None,"12:25 PM",18,"unverified"),
 ("2026-11-22","11:10 AM",6,"$200 No Limit Hold'em (1-Day)",200,None,"3:40 PM",29,"verified"),
 ("2026-11-23","11:10 AM",7,"$400 No Limit Hold'em 1A",400,75000,"5:55 PM",2,"verified"),
 ("2026-11-23","5:10 PM",8,"$200 No Limit Hold'em Progressive Knock-Out Bounty (1-Day)",200,8000,"9:40 PM",30,"unverified"),
 ("2026-11-24","11:10 AM",7,"$400 No Limit Hold'em 1B",400,75000,"5:55 PM",2,"verified"),
 ("2026-11-24","5:10 PM",9,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-11-25","11:10 AM",10,"$400 No Limit Hold'em (1-Day)",400,15000,"4:55 PM",6,"verified"),
 ("2026-11-25","5:10 PM",11,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-11-26","11:10 AM",12,"$300 No Limit Hold'em (1-Day)",300,10000,"4:55 PM",5,"verified"),
 ("2026-11-26","5:10 PM",13,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-11-27","11:10 AM",14,"$600 No Limit Hold'em (1-Day)",600,30000,"4:55 PM",7,"verified"),
 ("2026-11-27","5:10 PM",15,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-11-28","11:10 AM",16,"$600 No Limit Hold'em Bounty (1-Day), $200 bounties to start, $500 once in the money",600,30000,"4:55 PM",11,"verified"),
 ("2026-11-28","12:10 PM",17,"$400 Pot Limit Omaha Bounty (1-Day)",400,15000,"4:40 PM",26,"unverified"),
 ("2026-11-28","5:10 PM",18,"$200 NLH PokerAtlas Valuetown Bounty (1-Day)",200,20000,"9:40 PM",8,"unverified"),
 ("2026-11-29","11:10 AM",19,"$400 No Limit Hold'em 1A",400,75000,"5:55 PM",3,"verified"),
 ("2026-11-29","12:10 PM",20,"$300 Pot Limit Omaha Double Board Bomb Pot (1-Day)",300,10000,"4:40 PM",22,"unverified"),
 ("2026-11-29","5:10 PM",21,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-11-30","11:10 AM",19,"$400 No Limit Hold'em 1B",400,75000,"5:55 PM",3,"verified"),
 ("2026-11-30","5:10 PM",22,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-12-01","11:10 AM",19,"$400 No Limit Hold'em 1C",400,75000,"5:55 PM",3,"verified"),
 ("2026-12-01","5:10 PM",23,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-12-02","10:10 AM",24,"$600 No Limit Hold'em Seniors (1-Day), 50+ only",600,40000,"3:55 PM",17,"unverified"),
 ("2026-12-02","5:10 PM",25,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-12-03","11:10 AM",26,"$800 No Limit Hold'em 1A",800,500000,"3:40 PM",12,"verified"),
 ("2026-12-03","12:10 PM",27,"$600 BIG O (1-Day)",600,25000,"4:40 PM",28,"unverified"),
 ("2026-12-03","5:10 PM",26,"$800 No Limit Hold'em 1B",800,500000,"8:40 PM",13,"unverified"),
 ("2026-12-04","11:10 AM",26,"$800 No Limit Hold'em 1C",800,500000,"3:40 PM",12,"verified"),
 ("2026-12-04","5:10 PM",26,"$800 No Limit Hold'em 1D",800,500000,"8:40 PM",13,"unverified"),
 ("2026-12-05","11:10 AM",26,"$800 No Limit Hold'em 1E",800,500000,"3:40 PM",12,"verified"),
 ("2026-12-05","5:10 PM",26,"$800 No Limit Hold'em 1F (Turbo)",800,500000,"7:25 PM",14,"unverified"),
 ("2026-12-06","11:10 AM",28,"$600 No Limit Hold'em (1-Day)",600,40000,"4:55 PM",7,"verified"),
 ("2026-12-06","5:10 PM",29,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-07","11:10 AM",30,"$600 No Limit Hold'em Bounty (1-Day), $200 bounties to start, $500 in the money",600,40000,"4:55 PM",11,"verified"),
 ("2026-12-07","5:10 PM",31,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-08","10:10 AM",32,"$600 No Limit Hold'em Seniors (1-Day), 50+ only",600,40000,"3:55 PM",17,"unverified"),
 ("2026-12-08","4:10 PM",33,"$100 NLH LIPS Ladies Milestone Satellite (1-Day), awards direct entry to Event #39",100,None,"6:25 PM",19,"satellite"),
 ("2026-12-08","5:10 PM",34,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-09","10:10 AM",35,"$600 NLH LIPS Poker Jingle Tag Team (1-Day), tag teams F/F or F/M",600,10000,"2:40 PM",31,"unverified"),
 ("2026-12-09","11:10 AM",36,"$800 No Limit Hold'em Bounty (1-Day), $200 bounties to start, $500 in the money",800,75000,"4:55 PM",16,"unverified"),
 ("2026-12-09","4:10 PM",37,"$100 NLH LIPS Ladies Milestone Satellite (1-Day), awards direct entry to Event #39",100,None,"6:25 PM",19,"satellite"),
 ("2026-12-09","5:10 PM",38,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-10","10:10 AM",39,"$800 No Limit Hold'em LIPS Ladies (2-Day), Women in Poker Main Event",800,40000,"4:55 PM",32,"unverified"),
 ("2026-12-10","12:10 PM",40,"$600 Pot Limit Omaha Bounty (1-Day)",600,25000,"4:40 PM",27,"unverified"),
 ("2026-12-10","4:10 PM",41,"$260 NLH Milestone Satellite (1-Day), awards direct entry to Event #47",260,None,None,24,"satellite"),
 ("2026-12-10","5:10 PM",42,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-11","11:10 AM",43,"$600 No Limit Hold'em LIPS, Kings and Queens Bounty (1-Day), open to all",600,30000,"4:55 PM",33,"unverified"),
 ("2026-12-11","4:10 PM",44,"$260 NLH Milestone Satellite (1-Day), awards direct entry to Event #47",260,None,None,24,"satellite"),
 ("2026-12-11","8:10 PM",45,"$260 NLH Turbo Milestone Satellite (1-Day), awards direct entry to Event #47",260,None,None,25,"satellite"),
 ("2026-12-12","9:10 AM",46,"$260 NLH Turbo Milestone Satellite (1-Day), awards direct entry to Event #47",260,None,None,25,"satellite"),
 ("2026-12-12","10:10 AM",47,"$2,200 No Limit Hold'em 1A, PokerAtlas Championship Title Event",2200,1000000,"4:55 PM",21,"verified"),
 ("2026-12-12","12:10 PM",48,"$260 NLH Turbo Milestone Satellite (1-Day), awards direct entry to Event #47",260,None,None,25,"satellite"),
 ("2026-12-12","6:10 PM",47,"$2,200 No Limit Hold'em 1B, PokerAtlas Championship Title Event",2200,1000000,"11:10 PM",37,"unverified"),
 ("2026-12-13","10:10 AM",49,"$1,100 No Limit Hold'em Seniors 1A, 50+ only",1100,300000,"4:55 PM",20,"unverified"),
 ("2026-12-13","5:10 PM",50,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-14","10:10 AM",49,"$1,100 No Limit Hold'em Seniors 1B, 50+ only",1100,300000,"4:55 PM",20,"unverified"),
 ("2026-12-14","5:10 PM",51,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-15","11:10 AM",52,"$1,100 No Limit Hold'em Progressive Knock-Out Bounty (1-Day)",1100,75000,"4:55 PM",34,"unverified"),
 ("2026-12-15","5:10 PM",53,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-16","11:10 AM",54,"$600 No Limit Hold'em Bounty (1-Day), $200 bounties to start, $500 in the money",600,50000,"4:55 PM",11,"verified"),
 ("2026-12-16","5:10 PM",55,"$300 No Limit Hold'em Bounty (1-Day)",300,15000,"9:40 PM",15,"verified"),
 ("2026-12-17","10:10 AM",56,"$1,100 No Limit Hold'em 1A ($40 rake discount if registered before 10:10 AM)",1100,500000,"4:55 PM",35,"verified"),
 ("2026-12-17","12:10 PM",57,"$600 Pot Limit Omaha Double Board Bomb Pot (1-Day)",600,25000,"4:40 PM",23,"unverified"),
 ("2026-12-17","6:10 PM",56,"$1,100 No Limit Hold'em 1B ($40 rake discount if registered before 6:10 PM)",1100,500000,"11:10 PM",36,"unverified"),
 ("2026-12-18","10:10 AM",56,"$1,100 No Limit Hold'em 1C",1100,500000,"4:55 PM",35,"verified"),
 ("2026-12-18","6:10 PM",56,"$1,100 No Limit Hold'em 1D",1100,500000,"11:10 PM",36,"unverified"),
 ("2026-12-19","10:10 AM",56,"$1,100 No Limit Hold'em 1E",1100,500000,"4:55 PM",35,"verified"),
 ("2026-12-19","5:10 PM",58,"$200 NLH PokerAtlas Valuetown Bounty (1-Day), PokerAtlas PRO $20 rake discount",200,20000,"9:40 PM",8,"unverified"),
 ("2026-12-20","11:10 AM",59,"$600 No Limit Hold'em 1A ($20 rake discount if registered before 11:10 AM)",600,150000,"5:55 PM",4,"unverified"),
 ("2026-12-20","5:10 PM",60,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-12-21","11:10 AM",59,"$600 No Limit Hold'em 1B",600,150000,"5:55 PM",4,"unverified"),
 ("2026-12-21","5:10 PM",61,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-12-22","11:10 AM",59,"$600 No Limit Hold'em 1C",600,150000,"5:55 PM",4,"unverified"),
 ("2026-12-22","5:10 PM",62,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
 ("2026-12-23","11:10 AM",63,"$600 No Limit Hold'em (1-Day)",600,30000,"4:55 PM",7,"verified"),
 ("2026-12-23","5:10 PM",64,"$200 No Limit Hold'em Bounty (1-Day)",200,8000,"9:40 PM",1,"verified"),
]

# Prize pool per entry, as stated on each structure sheet (buy-in minus house fees)
POOL_PER_ENTRY = {
 1: (160, 200, "structure 1"), 2: (330, 400, "structure 2"), 3: (330, 400, "structure 3"),
 5: (242, 300, "structure 5"), 6: (335, 400, "structure 6"), 7: (510, 600, "structure 7"),
 10: (240, 300, "structure 10"), 11: (510, 600, "structure 11"), 12: (690, 800, "structure 12"),
 15: (250, 300, "structure 15"), 21: (1975, 2200, "structure 21"), 29: (160, 200, "structure 29"),
 35: (960, 1100, "structure 35"),
}
# Structure sheets that were actually opened and read (drives the "verified" status)
STRUCTS_READ = [1,2,3,5,6,7,10,11,12,15,21,29,35]

# ---- Wynn Las Vegas: daily tournaments (official poster + terms). All have re-entry or rebuy/add-on terms.
WYNN_DAILY = [
 # days, time, buy-in, guarantee, advantage type, note, source
 ("Monday-Thursday","12:00 PM",200,10000,"re-entry","Entry fee doubles as re-entry fee; registration and re-entries until start of level 9 (~4:30 PM).",WYNN_DAILY_STRUCTS),
 ("Friday","12:00 PM",240,40000,"rebuy, add-on","Unlimited $200 rebuys when at 15,000 chips or less; one $100 add-on for 15,000 chips; re-entry NOT allowed.",WYNN_DAILY_STRUCTS),
 ("Saturday & Sunday","12:00 PM",200,25000,"re-entry","Entry fee doubles as re-entry fee.",WYNN_DAILY_STRUCTS),
 ("Nightly","6:00 PM",160,10000,"unverified","Listed on official poster; structure sheet not reviewed, so re-entry status is unknown.",WYNN_DAILY_POSTER),
]

# ---- Wynn WPT World Championship schedule (Nov 27 - Dec 13 rows read; re-entry NOT reviewed) ----
WPT = [
 ("2026-11-27","11:00 AM","No Limit Hold'em Day 1A",600,400000),
 ("2026-11-27","12:00 PM","TORSE",600,None),
 ("2026-11-27","1:00 PM","Pot Limit Omaha",400,None),
 ("2026-11-27","5:00 PM","No Limit Hold'em Day 1B",600,400000),
 ("2026-11-28","11:00 AM","No Limit Hold'em Day 1C",600,400000),
 ("2026-11-28","12:00 PM","Mixed Triple Draw (A-5, 2-7, Badugi)",600,None),
 ("2026-11-28","5:00 PM","No Limit Hold'em Day 1D",600,400000),
 ("2026-11-29","11:00 AM","No Limit Hold'em Day 1E",600,400000),
 ("2026-11-29","6:00 PM","No Limit Hold'em Day 1F",600,400000),
 ("2026-11-30","11:00 AM","No Limit Hold'em Day 1A",800,1000000),
 ("2026-11-30","12:00 PM","Limit Omaha 8",600,None),
 ("2026-11-30","5:00 PM","No Limit Hold'em Day 1B",800,1000000),
 ("2026-12-01","11:00 AM","No Limit Hold'em Day 1C",800,1000000),
 ("2026-12-01","12:00 PM","Limit Omaha 8/5/Stud 8",600,None),
 ("2026-12-01","1:00 PM","Pot Limit Omaha",1100,None),
 ("2026-12-01","5:00 PM","No Limit Hold'em Day 1D",800,1000000),
 ("2026-12-02","11:00 AM","No Limit Hold'em Day 1E",800,1000000),
 ("2026-12-02","6:00 PM","No Limit Hold'em Day 1F",800,1000000),
 ("2026-12-03","11:00 AM","No Limit Hold'em Day 1A",1600,1000000),
 ("2026-12-04","11:00 AM","No Limit Hold'em Day 1B",1600,1000000),
 ("2026-12-04","12:00 PM","HORSE",600,None),
 ("2026-12-05","11:00 AM","WPT Prime Championship Day 1A",1100,5000000),
 ("2026-12-05","9:00 PM","No Limit Hold'em Turbo",600,50000),
 ("2026-12-06","11:00 AM","WPT Prime Championship Day 1B",1100,5000000),
 ("2026-12-06","11:00 AM","PLO Mystery Bounty Day 1A",1600,500000),
 ("2026-12-06","6:00 PM","PLO Mystery Bounty Day 1B",1600,500000),
 ("2026-12-06","9:00 PM","No Limit Hold'em Turbo",600,50000),
 ("2026-12-07","11:00 AM","WPT Prime Championship Day 1C",1100,5000000),
 ("2026-12-07","11:00 AM","HORSE (2 Day)",1100,None),
 ("2026-12-07","1:00 PM","PLO $500 Bounty",1600,100000),
 ("2026-12-07","9:00 PM","No Limit Hold'em Turbo",600,50000),
 ("2026-12-08","11:00 AM","WPT Prime Championship Day 1D",1100,5000000),
 ("2026-12-08","9:00 PM","No Limit Hold'em Turbo",600,50000),
 ("2026-12-09","11:00 AM","No Limit Hold'em (2 Day)",1600,1000000),
 ("2026-12-09","1:00 PM","PLO $1,000 Bounty",3000,250000),
 ("2026-12-09","1:00 PM","Limit Omaha 8",800,None),
 ("2026-12-09","9:00 PM","No Limit Hold'em Turbo",600,50000),
 ("2026-12-10","10:00 AM","Super Gold Million Mystery Bounty Day 1A",400,3000000),
 ("2026-12-10","6:00 PM","Super Gold Million Mystery Bounty Day 1B",400,3000000),
 ("2026-12-11","10:00 AM","Super Gold Million Mystery Bounty Day 1C",400,3000000),
 ("2026-12-11","6:00 PM","Super Gold Million Mystery Bounty Day 1D",400,3000000),
 ("2026-12-12","10:00 AM","No Limit Hold'em",800,100000),
 ("2026-12-12","1:00 PM","Pot Limit Omaha",3000,250000),
 ("2026-12-12","9:00 PM","No Limit Hold'em Turbo",600,50000),
 ("2026-12-13","11:00 AM","WPT World Championship Day 1A ($1,000,000 added*)",10400,None),
 ("2026-12-13","11:00 AM","Ladies NLH Championship (2 Day)",1100,250000),
]

# ---- Caesars Palace daily NLH (official flyer). All include re-entry and/or add-on.
CAESARS = [
 ("Daily","10:00 AM",100,1000,"add-on, re-entry","$50 add-on for 15,000 chips at first break; re-entry by paying entry fee after elimination within first break; registration closes at start of level 7.",CAE_FLYER),
 ("Daily","2:00 PM",160,1000,"add-on, re-entry","$50 add-on for 15,000 chips at first break; re-entry within first break; registration closes at start of level 7.",CAE_FLYER),
 ("Daily","6:00 PM",100,1000,"add-on, re-entry","$50 add-on for 15,000 chips at first break; re-entry within first break; registration closes at start of level 7.",CAE_FLYER),
 ("Daily","9:00 PM",160,1000,"add-on, re-entry","$50 add-on for 15,000 chips at first break; re-entry within first break; registration closes at start of level 7.",CAE_FLYER),
]

# ---- Bellagio poker (official PDFs). Each event sells an optional staff gratuity that buys extra starting chips.
BELLAGIO = [
 ("Friday","11:00 AM",600,"Re-entry allowed through end of level 8. Optional $40 staff gratuity grants +15,000 starting chips.","re-entry, purchased chips",BEL_FRI,"Heading reads $600 NLH; rules allocate $510 pool, $50 admin, $40 optional gratuity."),
 ("Saturday","11:00 AM",600,"Optional $40 staff gratuity grants +20,000 starting chips. Registration open through level 10. PDF heading reads '$1100 Buy-In' and the file name reads $1000, but the rules allocate a $600 buy-in.","purchased chips",BEL_SAT,"Heading ($1,100) conflicts with rules ($600) and file name ($1,000)."),
 ("Sunday","11:00 AM",400,"Re-entry allowed through end of level 8. Optional $25 staff gratuity grants +15,000 starting chips. HORSE format.","re-entry, purchased chips",BEL_SUN,"HORSE format."),
]

# ---- Hotels. Only Wynn's resort fee is confirmed from an official page.
HOTELS = [
 # property, poker room (official location), resort fee before tax, fee status, fee source, fee source type, notes
 ("Wynn Las Vegas","Encore at Wynn Las Vegas (official T&C states the poker room is in Encore)",55,"Verified (official)",WYNN_TERMS,"official","Official Wynn terms: daily resort fee $55 plus tax per room night."),
 ("The Venetian Resort","The Palazzo, level 2, Grand Canal Shoppes (official)",None,"Unverified: third-party figures only",
   "https://www.resortfeechecker.com/1443-resort_fee_venetian_resort_las_vegas.html","third-party",
   "Third-party sites report $62.36 per night including tax (approximately $55 before tax). Not confirmed on an official Venetian page."),
 ("The Palazzo at The Venetian","The Palazzo, level 2, Grand Canal Shoppes (official)",None,"Unverified: third-party figures only",
   "https://www.resortfeechecker.com/1769973-resort_fee_palazzo_venetian.html","third-party",
   "Third-party sites report $62.36 per night including tax. Not confirmed on an official page."),
 ("Bellagio","North side of casino, next to Sportsbook (official)",None,"Unverified: sources conflict",
   "https://www.applevacations.com/hotels/bellagio/","third-party",
   "A third-party page quotes a '$55.00 plus applicable tax' resort fee. Another third-party guide lists $50. Official Bellagio page not retrieved."),
 ("ARIA Resort & Casino","East side of casino floor, next to Main Valet (official)",None,"Unverified: sources conflict",
   "https://www.virginatlantic.com/holidays/holiday-types/city-breaks/hotels/aria-resort-and-casino","third-party",
   "A third-party page quotes '$55 plus tax per room, per day'. Another third-party guide lists $50. Official ARIA page not retrieved."),
 ("Caesars Palace","Caesars Palace casino (poker room location per official Caesars page)",None,"Unverified: third-party figures only",
   "https://www.resortfeechecker.com/41245-resort_fee_caesars_palace.html","third-party",
   "Third-party sites report a $62.30 total with tax (about $54.95 before tax). Not confirmed on an official Caesars page."),
]
TAX_NOTE = ("Clark County lodging tax on the Strip is reported at 13.38% by third-party sources that cite Clark County. "
            "The official Clark County tax page has not been retrieved, so this is unverified.")
TAX_SOURCES = ["https://unleashvegas.com/guides/vegas-basics/resort-fees",
               "https://www.roommaster.com/hotel-tax/nevada"]
