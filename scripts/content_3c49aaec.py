"""Narrative content produced by the 2026-11-17 structure-sheet audit (session 3c49aaec).

Flags continue the numbering already used by data/c6087e2c/flags.json (F01-F25),
so this session's findings start at F27. Nothing here is a claim about a value:
every entry names the official document it came from, and what is missing.
"""

from data_3c49aaec import (DSE_URL, SHEET_URL, WPT_STRUCTURES_URL, WPT_SCHEDULE_URL,
                           WYNN_POKER_URL, WPT_DAILY_STRUCTURES_URL, TAX, RETRIEVED)

VENETIAN_CONTACT = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"

# ------------------------------------------------------------------- flags ----
FLAGS = [
    dict(id="F27", item="No Venetian DSE IV structure sheet states single entry",
         value_shown="'No entry rule stated' on the 51 ranked Venetian rows; 0 rows labelled Confirmed single-entry",
         status="Unverified",
         sources=[DSE_URL, SHEET_URL.format(n=1), SHEET_URL.format(n=32)],
         to_clear="All 37 official structure sheets were read in full on 2026-11-17: none contains the words "
                  "single entry, freezeout, no rebuy or no add-on and none states an entry cap. Only a written "
                  "rule from the room clears the flag for a specific event number (Venetian poker desk "
                  "702.414.7657 / lv_cas_poker@venetianlasvegas.com, both printed on the official suite-rate "
                  "page). Prior sessions published 31 / 30 / 20 / 0 confirmed counts for this same schedule."),
    dict(id="F28", item="Live hotel room rates are not retrievable from an official machine-readable source",
         value_shown="Dated snapshots only (2026-11-16 booking-UI captures, 2026-11-17 official 'as low as' page)",
         status="Unverified",
         sources=["https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
                  "https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-12-02&children[]=0&departure_date=2026-12-09&view=calendar"],
         to_clear="Open the per-date booking link on the Hotels page for your dates and record the itemised "
                  "checkout total in data/c6087e2c/rates_log.json with its timestamp."),
    dict(id="F29", item="The Venetian poker-suite rate is conditional, not a public rate",
         value_shown="$119 / $209 'as low as', shown with its conditions",
         status="Conditional",
         sources=["https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"],
         to_clear="Official page: requires 6 hours of live cash play OR a $300+ tournament buy-in for each "
                  "night stayed, met before 2 a.m. on the last night, or the rate reverts to the prevailing "
                  "rate; quoted only up to 130-150 days out; booked by phone 866.255.8936 with code EPOKR25. "
                  "Ask the agent to confirm that your tournament entries qualify every night."),
    dict(id="F30", item="Wynn resort-fee figure comes from a promotional terms page, not a live quote",
         value_shown="$55 + tax per night (stated, with its date condition)",
         status="Partly verified",
         sources=["https://www.wynnlasvegas.com/terms-and-conditions/849338"],
         to_clear="The official terms page states $50 plus tax for bookings before Jan 15, 2025 and $55 plus "
                  "tax on or after that date, but the page is the terms of a promotion whose stay window closed "
                  "2025-06-30. Confirm the fee shown in the booking flow for your dates."),
    dict(id="F31", item="Wynn 'self-parking included in the resort fee' claim not reproduced",
         value_shown="blank", status="Unverified",
         sources=["https://www.wynnlasvegas.com/terms-and-conditions/849338"],
         to_clear="A prior session recorded free self-parking for up to two vehicles. The Wynn terms page read "
                  "on 2026-11-17 says nothing about parking, so the parking cell is blank. Read the Wynn poker "
                  "page FAQ on parking, or confirm on the folio."),
    dict(id="F32", item="Wynn daily-tournament suspension list does not name the WPT festival",
         value_shown="'suspended during Wynn Signature, Wynn Millions and Classic' (official wording)",
         status="Contradiction between sessions",
         sources=[WYNN_POKER_URL],
         to_clear="Prior sessions state dailies are suspended during the WPT festival (Nov 27 - Dec 21). The "
                  "official page read 2026-11-17 names three other series and says dailies run 'during non-event "
                  "timeframes'. Wynn poker: 702.770-7654 (printed on the official WPT schedule PDF)."),
    dict(id="F33", item="Bellagio, Park MGM, Cosmopolitan, Caesars, ARIA and MGM Grand resort fees not verified",
         value_shown="blank (numeric field cleared; prior 'secondary source' $50-$55 figures removed)",
         status="Unverified",
         sources=["https://bellagio.mgmresorts.com/en/casino/poker.html", "https://www.caesars.com/caesars-palace"],
         to_clear="bellagio.mgmresorts.com/en/resort/fees.html returns a 404 page and no official fee page for "
                  "these properties could be retrieved; Caesars Rewards advertises 'No resort fees on any hotel "
                  "stay' as a program benefit, which is not a public rate. Take the fee from the booking folio."),
    dict(id="F34", item="Caesars Palace / Horseshoe daily tournament details not re-read in this audit",
         value_shown="prior-session rows kept, labelled unverified",
         status="Unverified",
         sources=["https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"],
         to_clear="Re-read the official Caesars poker-tournament page and record buy-in, guarantee, add-on and "
                  "entry rule together, then move the row out of the flagged list."),
    dict(id="F35", item="WPT structures PDF not transcribed for every schedule row",
         value_shown="rule blank on the affected rows; 13 events carry the sentence read in full",
         status="Unverified",
         sources=[WPT_STRUCTURES_URL, WPT_SCHEDULE_URL],
         to_clear="The $10,400 World Championship Registration paragraph was not in the chunks retrieved "
                  "2026-11-17 (a prior session read it as one entry per flight plus one Day 2 entry, up to four), "
                  "and no sentence was transcribed for the Super Gold Million, the Seniors events, the 6-Max "
                  "events or the Limit/TORSE championships. Those rows keep the entry rule blank and sit in the "
                  "multi-entry or candidate sections - never labelled single-entry."),
    dict(id="F36", item="Every WPT World Championship event read so far allows re-entry",
         value_shown="13 events labelled Multi-entry with the official sentence quoted",
         status="Verified (multi-entry)",
         sources=[WPT_STRUCTURES_URL, WPT_SCHEDULE_URL],
         to_clear="No clearing action: 11 events state 'Unlimited re-entry' until level 9 or 10, the WPT Prime "
                  "Championship states one entry plus one re-entry per starting flight, and multi-flight events "
                  "prohibit a further flight only once you advance to Day 2. No WPT event read here qualifies "
                  "as single-entry."),
    dict(id="F37", item="Structure-sheet cross-reference text for Event #26 is inconsistent",
         value_shown="sheet numbers taken from the official schedule rows, not from the sheet footers",
         status="Source inconsistency",
         sources=[SHEET_URL.format(n=12), SHEET_URL.format(n=13), SHEET_URL.format(n=14)],
         to_clear="Sheet 12 (flights A+C+E) points to 'DAYS B+D+F' and sheet 13 points to 'DAYS A+C+F', but the "
                  "1F flight has its own turbo sheet (14). The mapping used on this site comes from the schedule "
                  "row links, so the footers are not relied on."),
    dict(id="F38", item="Event #40 was missing from earlier captures",
         value_shown="$600 Pot Limit Omaha Bounty $25K GTD (1-Day), Thu Dec 10, 12:10 PM",
         status="Cleared by this audit",
         sources=[DSE_URL, SHEET_URL.format(n=27)],
         to_clear="Re-reading the official schedule and structure sheet 27 on 2026-11-17 recovered the row that "
                  "was truncated in data/c6087e2c/venetian_dse_2026.psv; the row is now complete and the "
                  "'ROW TRUNCATED IN CAPTURE' placeholder is gone."),
    dict(id="F39", item="Four Venetian events publish no guarantee at all",
         value_shown="blank guarantee, no ratio",
         status="Missing from source",
         sources=[SHEET_URL.format(n=18), SHEET_URL.format(n=29)],
         to_clear="RaceDay Stack events #03, #04 and #05 (sheet 18) and event #06 (sheet 29) print no guarantee "
                  "line, so they cannot be ranked on guarantee value. Ask the room for the target field."),
    dict(id="F40", item="Seven Venetian events guarantee seats, not cash",
         value_shown="labelled Satellite; excluded from cash ranking",
         status="Verified (satellite)",
         sources=[SHEET_URL.format(n=19), SHEET_URL.format(n=24), SHEET_URL.format(n=25)],
         to_clear="No action: sheets 19, 24 and 25 state 'Guarantee: 2 Seats' and a milestone rule (a player who "
                  "reaches 200,000 chips takes the seat and stops playing). Ranking them by cash guarantee would "
                  "be wrong, so they sit in their own section."),
    dict(id="F41", item="Bounty guarantees mix the prize pool and the bounty pool",
         value_shown="ratio shown with the format label 'Bounty' and the sheet's own wording",
         status="Verified (read the label)",
         sources=[SHEET_URL.format(n=1), SHEET_URL.format(n=8), SHEET_URL.format(n=11)],
         to_clear="No action: sheets state e.g. '$8,000 (prize pool + total bounties)'. The raw guarantee / "
                  "buy-in ratio therefore overstates cash. Sheet 8 also caps the PokerAtlas PRO discount at the "
                  "initial entry ($180 once, every later entry $200), which is an extra-money-buys-extra-chances "
                  "detail worth reading next to the ratio."),
    dict(id="F42", item="Event finishing times are never published",
         value_shown="overlap check uses start and the sheet's late-registration close, not a run time",
         status="Missing from source",
         sources=[SHEET_URL.format(n=1), SHEET_URL.format(n=25)],
         to_clear="Sheets give start, level length, late-registration close and 'plays until ~12.5% of the field "
                  "remains', but no expected end time. Pairs whose windows cannot overlap are labelled 'possible "
                  "if you are out before the cutoff'; #45/#46/#48 have no clock time at all and are 'unknown'."),
    dict(id="F43", item="Walking minutes are not published by any official source",
         value_shown="0 min for on-property routes only; every other route blank with a map link",
         status="Unverified",
         sources=[DSE_URL, WPT_STRUCTURES_URL],
         to_clear="Only 'on the same property' and 'the Wynn poker room is located in the Encore tower' are "
                  "sourced. Time the route links on the Hotels page (or record a measured walk) before relying "
                  "on the 30-minute filter; unverified pairs are hidden rather than estimated."),
    dict(id="F44", item="Hotel quality has no official score to cite",
         value_shown="blank", status="Needs your choice",
         sources=["https://github.com/karagemop466-tech/Poker5"],
         to_clear="The brief ranks cost and quality above distance, but no property publishes a quality score on "
                  "the pages read. Pick a rating source (AAA diamond rating or Forbes Travel Guide) and record "
                  "the rating with its date and URL; otherwise the column stays out so nothing is guessed."),
    dict(id="F45", item="Whether the resort fee is itself taxed needs a folio check",
         value_shown="13.38% applied to rate + fee in the calculator, labelled as an assumption",
         status="Partly verified",
         sources=[TAX["source"]],
         to_clear="The Clark County ordinance sets 13.38% for a resort hotel inside the Primary Gaming Corridor "
                  "(12.5% county/state + 0.88% stadium district). Both the Venetian and Wynn pages say the fee "
                  "is 'plus tax', but the tax base is confirmed only on the itemised folio."),
    dict(id="F46", item="Repo irregularities found during this audit",
         value_shown="listed on the Repo Review page",
         status="Process",
         sources=["https://github.com/karagemop466-tech/Poker5",
                  "https://github.com/karagemop466-tech/Poker5/blob/main/_config.yml"],
         to_clear="Eleven per-session site folders are published side by side with the root site; _config.yml "
                  "excludes scripts/ and test/ but not those folders; the Pages source is main at / and no "
                  "session token can change it (403), which is why sessions parked output in their own folder; "
                  "'npm run check' tests one session's dashboard while CI runs four sessions' builds; three "
                  "monitor workflows write baselines to main on overlapping schedules."),
    dict(id="F47", item="WPT schedule PDF has internal inconsistencies in its own listing",
         value_shown="rows transcribed as printed; inconsistency noted in the row note",
         status="Source inconsistency",
         sources=[WPT_SCHEDULE_URL],
         to_clear="The official schedule PDF lists a 'Dec. 17 Thursday' row after the Dec 18 rows and repeats the "
                  "$1,100 Day 1B and $600 PLO lines under Dec 18; the structures PDF prints 'BadugI' for Badugi "
                  "and calls the $800 event two-day while its schedule runs three days. Nothing was corrected by "
                  "inference - the printed text stands."),
    dict(id="F48", item="Wynn daily-tournament poster is a 2025 asset; the general terms PDF was read only in part",
         value_shown="Wynn daily rows kept as multi-entry/unverified with the poster cited",
         status="Unverified",
         sources=[WPT_DAILY_STRUCTURES_URL,
                  "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"],
         to_clear="The daily-tournament general terms (chunk 0) were read on 2026-11-17 and state registration "
                  "rules, payment, ante, TDA rules and a $5,000 W-2G threshold, but contain no re-entry or "
                  "add-on sentence; the per-event pages (chunks 1-2) could not be retrieved in this environment. "
                  "The poster asset's own date is 2025."),
]

# --------------------------------------------------------------- questions ----
QUESTIONS = [
    dict(id="Q1", q="Do the Venetian one-day events allow a re-entry or an add-on?",
         status="Open - blocks the label, not the schedule work",
         need="Single-entry is the point of the trip and no sheet in the series says either way.",
         how="Ask the Venetian poker desk for the written re-entry/add-on rule for the event numbers you plan to "
             "play (702.414.7657 / lv_cas_poker@venetianlasvegas.com on the official suite-rate page). Add the "
             "answer to structure_sheets.json as a source excerpt; the site then moves the row to 'Confirmed'.",
         source=DSE_URL),
    dict(id="Q2", q="Which dates is the trip, and how many nights?",
         status="Open",
         need="Rates, availability, the day plan and the trip-cost total all depend on the dates. The site uses "
              "the official series window Nov 16 - Dec 23, 2026 and one worked example stay, Dec 2-9, 2026.",
         how="Confirm the arrival and departure dates; every rate figure is dated and must be re-read for the "
              "chosen window before it is used as a cost.",
         source="https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-12-02&children[]=0&departure_date=2026-12-09&view=calendar"),
    dict(id="Q3", q="Is the $119 'as low as' poker-suite rate available for those nights?",
         status="Open",
         need="It is the only official room-rate figure for the host property and it drives the trip-cost "
              "estimate; the logged booking-UI snapshot for the same week is about $1,008 per night, i.e. a "
              "different order of magnitude.",
         how="Call 866.255.8936 quoting code EPOKR25 (both printed on the official page) and confirm the "
              "qualifying-play requirement is met each night.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="Q4", q="Is the room tax charged on the resort fee as well as the rate?",
         status="Partly answered",
         need="True nightly cost = rate + fee + tax; 'plus tax' on the fee changes the arithmetic by roughly $7 "
              "per night at the $55 fee.",
         how="Compare the itemised folio lines (room, resort fee, 13.38% tax) with the calculator's assumption "
              "once a quote exists.", source=TAX["source"]),
    dict(id="Q5", q="How long does each event actually run?",
         status="Open",
         need="'Play all day from 8 AM' only works if an early event finishes before the next one starts.",
         how="No official end time exists. The site uses the published late-registration close and flags pairs "
              "whose windows cannot both be entered; ask the room for a typical finish for the events you pick.",
         source=SHEET_URL.format(n=1)),
    dict(id="Q6", q="Is there an 8:00 AM tournament start anywhere on the Strip?",
         status="Answered: no",
         need="The brief asks for an all-day schedule from 8 AM.",
         how="Re-reading the official pages on 2026-11-17: the earliest Venetian start is 9:10 AM (event #46 "
              "satellite, Fri Dec 12) and most early events start 10:10 or 11:10 AM; the earliest WPT start is "
              "10:00 AM (Super Gold Million Day 1A). No official 8:00 AM start exists in these rooms, so the "
              "day plan is built from the earliest verified start instead.",
         source=DSE_URL),
    dict(id="Q7", q="Which hotel-to-venue walks are actually under 30 minutes?",
         status="Open for off-property pairs",
         need="The 30-minute limit is a hard filter in the brief and cost/quality are only compared inside it.",
         how="Time the route links on the Hotels page for the pairs that matter and record the minutes in "
              "walking.json; on-property routes are already verified at 0 minutes.", source=None),
    dict(id="Q8", q="Do Wynn daily tournaments run during the WPT festival?",
         status="Open - sessions disagree",
         need="It decides whether a Wynn evening event can be a same-day fallback for a Venetian day.",
         how="The official Wynn page suspends dailies during the Wynn Signature, Wynn Millions and Classic "
              "series and says they run 'during non-event timeframes'; WPT is not named. Confirm with Wynn "
              "poker (702.770-7654 on the official WPT schedule PDF).", source=WYNN_POKER_URL),
    dict(id="Q9", q="Is there an entry cap or a maximum field size?",
         status="Open",
         need="A capped field changes what a guarantee means; the brief requires the total entry fee and the "
              "guarantee to be confirmed before ranking.",
         how="No sheet in the series publishes a cap - only payout percentages ('pays 12.5% of the field') and "
              "'all pre-registered stacks in play' language. Ask per event number.", source=SHEET_URL.format(n=16)),
    dict(id="Q10", q="What exactly does the $10,400 WPT World Championship allow?",
         status="Open",
         need="It is the festival's flagship event and the largest buy-in in the window.",
         how="Open the official WPT structures PDF at the World Championship terms and transcribe the "
              "Registration paragraph; until then the event is shown in the multi-entry section with the rule "
              "blank (F35).", source=WPT_STRUCTURES_URL),
    dict(id="Q11", q="Which hotel quality score should the ranking use?",
         status="Needs your choice",
         need="Cost and quality outrank distance in the brief, but no property publishes a quality score.",
         how="Pick AAA diamond ratings or Forbes Travel Guide, and the site will store the rating with its date "
              "and URL. Without your choice the column stays blank (F44).", source=None),
    dict(id="Q12", q="Should events whose sheet is silent stay in the main list?",
         status="Needs your choice",
         need="51 ranked rows carry every field verified except the entry rule; moving them to a "
              "watchlist would leave the main list empty for this series.",
         how="Decide: keep them labelled 'No entry rule stated' (current behaviour) or restrict the main list to "
              "confirmed rows only. Nothing is asserted about their entry rule either way.", source=DSE_URL),
]

# -------------------------------------------------------------- suggestions ----
SUGGESTIONS = [
    dict(id="S1", title="Keep the written-rule standard for 'single entry' on every page",
         detail="Three states, never two: CONFIRMED (a sheet says so), NO RULE STATED (sheet read, silent) and "
                "NOT READ. This series has 0 confirmed rows, 51 no-rule-stated rows and 7 events (24 rows) limited "
                "to one flight, which ends the 31/30/20/0 disagreement between earlier sessions.",
         impact="high", effort="low",
         decide="Your choice: keep NO RULE STATED rows in the ranked list (current) or move them to a watchlist."),
    dict(id="S2", title="Two phone calls sharpen the whole site",
         detail="Venetian poker desk: the re-entry/add-on rule for the event numbers you plan to play. Wynn poker "
                "desk: do the daily tournaments run during WPT? Each answer becomes a sourced excerpt on the "
                "row, which is the only field missing for ranking and for the day plan.",
         impact="high", effort="low", decide="Both numbers are printed on the official pages already linked."),
    dict(id="S3", title="Turn the trip calculator into a per-night qualifier checker",
         detail="The official Venetian poker rate requires 6 hours of cash play or a $300+ tournament buy-in each "
                "night. Every buy-in is in the dataset, so the planner can show whether a chosen day qualifies "
                "and price the night at the poker rate, or mark the rate unverified when it does not.",
         impact="high", effort="medium",
         decide="Approve the automatic check, and decide what to show for a non-qualifying night."),
    dict(id="S4", title="Publish one site, not eleven dashboards",
         detail="Each session published its own folder under the same URL, which is honest but unreadable. Move "
                "prior folders under /archive/ with a banner, or list them on a session index, and keep the root "
                "site as the single product.",
         impact="medium", effort="medium", decide="Needs your approval; only an integration session should move "
                                                  "another session's folder."),
    dict(id="S5", title="Score hotel quality from a declared source, or drop the column",
         detail="Cost and quality outrank distance in the brief, but no official page scores quality. Pick AAA "
                "diamonds or Forbes Travel Guide, record the rating with its date and URL, then rank on cost + "
                "rating; otherwise leave the column out so nothing is paraphrased from review sites.",
         impact="medium", effort="low", decide="Choose the rating source, or forbid quality ranking."),
    dict(id="S6", title="Extend the morning monitor from 'source changed' to 'value changed'",
         detail="The re-check job already re-reads every official URL, records a hash and marks rows whose source "
                "changed. The next step is to parse the schedule row and the sheet's Guarantee / Late "
                "Registration / Start Time lines and diff the parsed values, so a guarantee moving is reported "
                "rather than a hash change.",
         impact="high", effort="medium", decide="Approve the parse rules; a loose regex would report noise."),
    dict(id="S7", title="Log the day-before schedule delta",
         detail="The Venetian page updates start times, results and cancellations. A nightly job that appends the "
                "parsed rows to a dated log would show whether an event you planned moved, filled or was "
                "cancelled, with the date it changed.",
         impact="medium", effort="medium", decide="Decide whether the bot may commit to main without review."),
    dict(id="S8", title="Show implied field size next to the ratio",
         detail="Sheets state the guarantee and 'pays 12.5% of the field'. guarantee / (buy-in - house fee) / "
                "0.125 gives the entries needed before the guarantee stops being a floor. That is arithmetic on "
                "published numbers, labelled as such - not a forecast of your result.",
         impact="medium", effort="low", decide="Approve showing this arithmetic, or keep ratios only."),
    dict(id="S9", title="Make the walk filter a route log instead of a boolean",
         detail="Store hotel, venue, mode, minutes, source and date per observation. One timed walk entered "
                "once is reused by every plan; pairs nobody has measured stay hidden by the 30-minute filter "
                "instead of showing an estimate.",
         impact="medium", effort="low", decide="Approve your own timed walks as a source class."),
    dict(id="S10", title="Rank only events with both a confirmed entry fee and a confirmed guarantee",
         detail="This is the rule the site enforces: 47 of the 51 ranked rows carry both numbers, 4 events publish no "
                "guarantee at all and are excluded from the ranking (F39), and satellites guarantee seats so they "
                "are ranked separately (F40). Keeping it means no row is ever filled from memory or a "
                "third-party page.",
         impact="high", effort="none (already implemented)", decide="Nothing to do - a rule worth keeping."),
    dict(id="S11", title="Add the WPT rows to the day plan once you pick the hotel",
         detail="The WPT schedule rows are now in the dataset with dates, starts, stacks and level lengths, so "
                "if you stay at Wynn/Encore the same primary-plus-fallback logic can run across both rooms - but "
                "no verified walk time between the two properties exists yet (F43), which is why they are not "
                "combined into one day today.",
         impact="medium", effort="low", decide="Pick the hotel first; combining rooms needs the walk measured."),
]

# ------------------------------------------------------------- repo review -----
REPO_REVIEW = [
    dict(item="Published site vs data folders",
         finding="GitHub Pages publishes main at /. The root site (index.html, pages/, assets/) is generated by "
                 "scripts/build_c6087e2c.py from data/c6087e2c/, but eleven per-session folders "
                 "(docs/, site/, site-*/, dashboard-*/, planner-aa83f1e1/) are published under the same URL, each "
                 "with its own numbers for the same official schedule.",
         evidence="https://github.com/karagemop466-tech/Poker5",
         action="This session regenerates the root site from the 2026-11-17 audit and labels the other folders "
                "as prior session output rather than editing them."),
    dict(item="Confirmed single-entry counts contradicted across sessions",
         finding="Sessions published 31, 30, 20 and 0 'confirmed single-entry' counts from the same 37 structure "
                 "sheets, depending on whether silence was treated as confirmation.",
         evidence="https://github.com/karagemop466-tech/Poker5/blob/main/COORDINATION.md",
         action="All 37 sheets were read in full and the written-rule standard adopted: 0 confirmed rows, 51 "
                "labelled 'no entry rule stated', 24 rows (7 events) labelled multi-flight, 7 satellite rows and "
                "11 restart rows. Site-wide copy now states the standard instead of asserting freezeouts."),
    dict(item="A truncated data row was published as a gap",
         finding="The Event #40 row of data/c6087e2c/venetian_dse_2026.psv shipped with 'ROW TRUNCATED IN CAPTURE' "
                 "as the event name and no buy-in, guarantee or time, while the official page lists the event.",
         evidence=SHEET_URL.format(n=27),
         action="Re-read the official schedule and sheet 27 and wrote the row back into the psv: Thu Dec 10, "
                "12:10 PM, $600 Pot Limit Omaha Bounty, $25K GTD, 8-handed, $200 bounties (F38)."),
    dict(item="Numeric hotel values from secondary sources",
         finding="data/c6087e2c/hotels.json carried numeric resort fees of $50-$55 for Bellagio, ARIA and MGM "
                 "Grand sourced from news/aggregator pages, and a 'self-parking included' note for Wynn that the "
                 "official terms page does not state.",
         evidence="https://github.com/karagemop466-tech/Poker5/blob/main/data/c6087e2c/hotels.json",
         action="Numeric fields for unverified properties are cleared to blank with the explanatory text kept in "
                "a labelled cell, and the Wynn parking claim is removed (F31, F33). Only the Venetian and Wynn "
                "figures with an official page read in 2026-11-17 keep a number."),
    dict(item="Duplicate scheduled monitors",
         finding=".github/workflows/recheck.yml (06:00 UTC), recheck-6d1e0039.yml and the afff1fc9 monitor "
                 "(15:00 UTC) all re-read official URLs and write a baseline back to main.",
         evidence="https://github.com/karagemop466-tech/Poker5/tree/main/.github/workflows",
         action="Left running; the shared 06:00 job is the one the root site reads. Consolidation is suggestion "
                "S6/S7, not a unilateral change to another session's workflow."),
    dict(item="npm check does not cover the published site",
         finding="package.json 'npm run check' validates site-b50aa7f5 only, while CI also runs four other "
                 "sessions' build scripts; a broken root site would not be caught by npm.",
         evidence="https://github.com/karagemop466-tech/Poker5/blob/main/package.json",
         action="CI quality.yml regenerates the root site with the shared build and then runs "
                 "scripts/check_root_site.py, which is the gate this session had to pass."),
    dict(item="Tooling and build artefacts in the published tree",
         finding="_config.yml excludes scripts/ and test/ from the Pages build but not the other sessions' data "
                 "and script folders; __pycache__ was reported committed by an earlier session.",
         evidence="https://github.com/karagemop466-tech/Poker5/blob/main/_config.yml",
         action="No change beyond this session's own files; .gitignore already covers __pycache__/ and *.pyc, "
                "and no __pycache__ is present on this branch."),
    dict(item="WPT data in other_sessions' folders contradicted by the official structures PDF",
         finding="data/c6087e2c/other_events.json listed 'PLO, $1,600, $1M GTD' as a single-entry candidate while "
                 "the official WPT structures PDF states '$1,600 No Limit Hold'em $1,000,000 GTD' with unlimited "
                 "re-entry per flight, and a separate '$1,600 PLO Mystery Bounty $500,000 GTD'.",
         evidence=WPT_STRUCTURES_URL,
         action="The row is relabelled from the official document (game, guarantee and entry rule corrected, "
                "multi-entry) with the discrepancy recorded in the row note; other WPT rows were checked against "
                "the same PDF and only those whose sentence was read are labelled."),
    dict(item="Dead source path used by another session's dataset",
         finding="data-6d1e0039/events.json links structure PDFs under /content/dam/venetianlasvegas/... which "
                 "returns 404; the working path is /content/dam/vlvweb/...",
         evidence=SHEET_URL.format(n=1),
         action="Recorded here only - that folder is read-only for this session. Every link this site generates "
                "uses the working /content/dam/vlvweb/ path and was fetched on 2026-11-17."),
]
