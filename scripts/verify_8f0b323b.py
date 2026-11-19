"""Session 8f0b323b - dated, official-source re-verification records.

Every entry here was read live on 2026-11-19 by the platform page reader in this
session, from the official URL that is stored beside it, and is published on the
`pages/reverify.html` page of the site. Nothing in this module is inferred: an
entry either quotes the official sentence that was read, or records that the
official page did not return the value.

Rules this module follows, and the rest of the site follows for these values:
  * a value is only "verified" here when the sentence behind it was read today;
  * a value whose page still returns the older figure is a MISMATCH and is
    logged, never silently corrected in a second place;
  * a value whose official page does not publish it stays blank and is logged
    as not published - it is not copied from a third-party site.
"""

SESSION = "8f0b323b"
READ_ON = "2026-11-19"
READ_METHOD = ("Platform page reader, full page text, one official URL per row, read on 2026-11-19 "
               "in this session. The reader returns the text of the page as served to it; a value is "
               "recorded only where that text prints it.")

# ---------------------------------------------------------------------------
# 1. Official rows re-read line by line
# ---------------------------------------------------------------------------
# Each check: what was read, the official URL, the exact sentence (or datum)
# read, what the site had stored, and the verdict.
CHECKS = [
    dict(id="V01", group="Tournament schedule",
         item="Venetian DeepStack Extravaganza IV: all 94 schedule rows (date, start time, event number, name, buy-in, guarantee, structure-sheet number)",
         url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         read="Series runs November 16 - December 23, 2026, 'More than $3.6 Million in guaranteed tournament prize pools'; 94 dated rows from 16 Nov 2026 to 23 Dec 2026.",
         stored="94 rows in data/ea99006a/venetian.json",
         verdict="match",
         note=("Every row's date, start time, event number, structure-sheet link, buy-in and guarantee was compared one by one "
               "by scripts/recheck_8f0b323b.py. 90 rows matched on every field. 4 rows differ in the trailing promotional text of "
               "the event NAME only (rows 6, 7, 8 'Race to finish before the Race' and row 49 'Tag Teams Consist of "
               "Female/Female or Female/Male'); the stored rows keep the sheet text and carry that promotional line in their notes. "
               "No date, time, buy-in or guarantee differs. See F62."),
         script="scripts/recheck_8f0b323b.py"),
    dict(id="V02", group="Tournament schedule",
         item="Venetian DSE IV headline events and guarantees (series page)",
         url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         read=("#26 $800 NLH $500K GTD (Dec 3-6); #47 $2,200 NLH $1M GTD (Dec 12-14); #49 $1,100 Seniors 50+ $300K GTD "
               "(Dec 13-15); #56 $1,100 NLH $500K GTD (Dec 17-20); #59 $600 NLH $150K GTD (Dec 20-23)."),
         stored="pages/venues/venetian.html headline table",
         verdict="match",
         note="The five headline blocks on the venue page agree with the live series text, including the $1M PokerAtlas Championship Title Event dates.",
         script=""),
    dict(id="V03", group="Tournament schedule",
         item="Venetian single-entry classification for the trip window (events 28, 29, 30, 31, 34, 36, 41, 42, 44, 45, 46, 48, 50, 51, 53, 55)",
         url="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_8.pdf",
         read="Structure sheet 8 rule 07: 'All subsequent buy in's after the initial buy in will be $200.' (sheet 8 covers events #18 and #58)",
         stored="data/ea99006a/venetian.json marks #18 and #58 entry_rule='multi'",
         verdict="match",
         note=("The stored canonical data already treats the 'subsequent buy in's' sentence as a second-entry grant, which is the "
               "conservative reading. Sheets 7, 11, 15, 16, 24 and 25 (behind the trip-window single-entry rows) were re-read in the "
               "previous session (data/d615f79e) and were NOT re-read in this one; that limitation is carried forward on the "
               "Verification page rather than presented as fresh evidence."),
         script=""),

    dict(id="V04", group="Walking routes",
         item="Venetian poker-room location, hours and indoor directions from each lobby",
         url="https://www.venetianlasvegas.com/resort/casino/poker.html",
         read=("'Our Poker Room is located at The Palazzo on level 2 of Grand Canal Shoppes. The Poker Room features 50 tables "
               "spread across 14,000 square feet'; open 24 hours, 12:00 AM - 11:59 PM every day; 'From The Venetian Lobby: "
               "proceed across The Venetian casino floor, to Restaurant Row. Enter the Waterfall Atrium ... take the escalator up "
               "to level 2'; 'From The Palazzo Lobby: proceed across The Palazzo Casino Floor to the self-parking elevators ... "
               "The Poker Room will be straight ahead'; 'convenient access to The Palazzo self-parking garage'."),
         stored="room listed as at The Palazzo, level 2, Grand Canal Shoppes (F27)",
         verdict="match",
         note=("This is the evidence behind the 0-minute 'same property' row for a Venetian or Palazzo stay, and it also shows why "
               "an indoor allowance matters: the room is up an escalator at the far end of the Grand Canal Shoppes, not at the "
               "Venetian lobby. No walk time to another property is published anywhere (N03)."),
         script=""),

    dict(id="V10", group="Hotel cost",
         item="Venetian mandatory resort fee",
         url="https://www.venetianlasvegas.com/resort/resort-fee.html",
         read="'Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in.'",
         stored="$55 plus tax per night",
         verdict="match",
         note="Unchanged. The page also lists what the fee buys (Canyon Ranch access for two, in-suite internet, boarding-pass printing, local calls, PressReader).",
         script=""),
    dict(id="V11", group="Hotel cost",
         item="Venetian poker suite rate and its play condition",
         url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         read=("'These rates will start as low as $119 and $209 and can be higher. Future rates are only provided out to a maximum "
               "of 150 days'; 'you will be required to play six hours of active live cash gameplay or buy in to a $300 or higher "
               "tournament for each night stayed'; 'Failure ... will result in your nightly suite rate being adjusted to the "
               "prevailing rate'; 'There is a $55 resort fee per night stayed.' Booking code EPOKR25, phone 866.255.8936."),
         stored="floor rate from $119 / $209, six-hour or $300+ buy-in condition, $55 resort fee",
         verdict="match",
         note=("Still a published FLOOR, not a quote for 6-13 December 2026. The page states future rates are given out only to 150 "
               "days, which is why no date-specific figure can be read from it."),
         script=""),
    dict(id="V12", group="Hotel cost",
         item="Venetian self-parking charges for a registered hotel guest",
         url="https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html",
         read=("'The daily fee for registered hotel guests is $20/day, seven days a week. For non-hotel guests, the fee is $20/day "
               "Monday - Thursday, and $25/day Friday - Sunday. Valet parking is $40/day.' Poker players who play three hours or "
               "more in a tournament or cash game receive complimentary self-parking for the day."),
         stored="no per-stay parking figure was stored for the Venetian",
         verdict="new",
         note=("This is the first dated capture of a Venetian per-day parking figure for a registered hotel guest. It is a rate, not a "
               "stay total: the trip cost only includes parking if the traveller parks, and the poker-room three-hour benefit can make "
               "it $0. Shown as a dated observation and used in the calculator's optional parking line."),
         script=""),
    dict(id="V13", group="Hotel cost",
         item="Wynn / Encore resort fee and what it includes",
         url="https://www.wynnlasvegas.com/terms-and-conditions/DK26WLV2",
         read=("'A daily resort fee of $55 plus tax will be added to your room account for each room night, which entitles you to "
               "receive complimentary self-parking for up to two vehicles; in-room Wi-Fi of 15 Mbps ... fitness center ... digital newsstand.'"),
         stored="$55 plus tax; complimentary self-parking for up to two vehicles",
         verdict="match",
         note="Unchanged.",
         script=""),
    dict(id="V14", group="Hotel cost",
         item="Wynn / Encore deposit and cancellation deadline for the published offer",
         url="https://www.wynnlasvegas.com/terms-and-conditions/DK26WLV2",
         read=("'A deposit of one (1) night of room and tax will be charged at the time of booking and cancellations must be received "
               "at least 48 hours prior to arrival date or deposit will be forfeited.' Blackout dates listed include "
               "'November 17-21, 2026' and 'December 31, 2026'."),
         stored="48 hours before arrival (offer DK26WLV2)",
         verdict="match",
         note=("Confirmed again today: the 48-hour figure is what the live offer terms say; the earlier 72-hour figure remains withdrawn "
               "(F55). The offer's own stay window is 2 October 2026 - 31 March 2027 and it requires a two-night stay, so it does NOT "
               "price a 7-night trip - see F63."),
         script=""),
    dict(id="V15", group="Hotel cost",
         item="Bellagio mandatory resort fee",
         url="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
         read=("'A daily resort fee of $55.00 plus applicable tax will be applied to all reservations.' Waived for MGM Rewards Gold+ "
               "on eligible reservations. Additional occupant charge $50 plus tax per occupant per night above 2 occupants."),
         stored="blank - MGM resort fees had never been read from an official page (F10)",
         verdict="new",
         note=("Closes the Bellagio half of F10. The value is a mandatory per-night fee plus tax on all reservations, so it belongs in "
               "the true-cost formula exactly like the Venetian and Wynn fees. Not a room rate."),
         script=""),
    dict(id="V16", group="Hotel cost",
         item="ARIA mandatory resort fee",
         url="https://aria.mgmresorts.com/en/terms-and-conditions.html",
         read="'A daily resort fee of $55.00 plus applicable tax will be applied to all reservations.' Check-in 3:00 pm, check-out 11:00 am.",
         stored="blank - never read from an official page (F10)",
         verdict="new",
         note="Closes the ARIA half of F10. Same structure as Bellagio's fee.",
         script=""),
    dict(id="V17", group="Hotel cost",
         item="MGM Grand mandatory resort fee",
         url="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
         read=("'A daily resort fee of $50.00 plus applicable tax will be applied to all reservations.' Additional occupant charge "
               "$40 plus tax per occupant per night above 2 occupants."),
         stored="blank - never read from an official page (F10)",
         verdict="new",
         note="Closes the MGM Grand half of F10. Note the different amount: $50, not $55 - MGM fees are property-specific, so one corporate figure must not be reused for all MGM rooms.",
         script=""),
    dict(id="V18", group="Hotel cost",
         item="Bellagio / ARIA / MGM Grand deposit and cancellation deadline (standard reservation terms)",
         url="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
         read=("Bellagio and ARIA: 'The first night's deposit is fully refundable provided a timely notice of cancellation is received ... "
               "at least 72 hours prior to the arrival date, unless specifically excluded by booked offer.' MGM Grand states the same "
               "72-hour rule and uses 877.880.0880 for Room Reservations."),
         stored="blank - no MGM cancellation term had been read (F33, Q14)",
         verdict="new",
         note=("This is the standard reservation term, not the term of a specific discounted rate plan; the page itself says an offer may "
               "exclude it. Recorded as the standard term on the hotels page and flagged as rate-plan dependent."),
         script=""),
    dict(id="V19", group="Hotel cost",
         item="MGM Resorts self-parking and valet rates (Bellagio, ARIA, Vdara, Cosmopolitan, MGM Grand, Mandalay Bay, W, Park MGM, NY-NY, Luxor, Excalibur)",
         url="https://www.mgmresorts.com/en/things-to-do/parking.html",
         read=("Self-parking over 0-24 hours: $20 Mon-Thu, $25 Fri-Sun; registered hotel guest $20 either way. Valet parking $40 daily, "
               "all days. 'Prices may be higher during special events.' Registered hotel guests also get in-out privileges across MGM "
               "Las Vegas destinations within the same 24-hour period."),
         stored="blank - parking was never captured for the MGM rooms",
         verdict="new",
         note=("Closes part of F33 for the MGM rooms. The same page prints approximate walking times to T-Mobile Arena, not to the "
               "Venetian poker room, so it adds nothing to the route evidence (F15/F50)."),
         script=""),
    dict(id="V21", group="Coverage",
         item="Horseshoe Hall of Fame Poker Room: size, games and whether a schedule is published",
         url="https://www.caesars.com/horseshoe-las-vegas/casino",
         read=("'The Hall of Fame Poker Room at Horseshoe Las Vegas features 20 tables and offers many exciting varieties of live "
               "poker ... Test your luck with 6 exciting tournament times daily.' The page links no schedule, no buy-in, no "
               "guarantee and no structure sheet."),
         stored="Horseshoe publishes no poker schedule (F11)",
         verdict="match",
         note=("Confirmed again, and worth stating precisely: the casino page asserts that six tournament times run daily, but no "
               "official Horseshoe page read in this session publishes any of them. A row cannot be created from another site's "
               "list, so the tournaments table has no Horseshoe rows and the coverage gap stays visible."),
         script=""),

    dict(id="V20", group="Hotel cost",
         item="Caesars Palace / Horseshoe mandatory resort fee",
         url="https://www.caesars.com/corporate/disclaimer",
         read=("'Room reservations are subject to a daily resort fee between $45-$60 plus applicable tax. Resort fees are waived for "
               "Diamond and Seven Stars.' (Hotel Disclaimer section.)"),
         stored="corporate range $45-$60 plus tax, marked not property-specific",
         verdict="match",
         note=("Re-read and unchanged, and it is still not a property-specific number: the same sentence covers every Caesars "
               "Entertainment property, so it cannot be used as Caesars Palace's or Horseshoe's fee. Both stay blank in the cost "
               "column and remain on the flagged page (F09). The waiver sentence is new evidence worth keeping."),
         script=""),

    dict(id="V30", group="Other official pages",
         item="Clark County combined transient lodging tax rate",
         url="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf",
         read="Ordinance table: resort hotel within the primary gaming corridor 13.38%.",
         stored="13.38%",
         verdict="not re-read",
         note=("Not re-opened in this session. The 13.38% figure is carried forward from the 2026-11-19 county read recorded under F20, "
               "and the Treasury-style arithmetic in the calculator states it as an assumption. Re-open the PDF before payment."),
         script=""),
]

# ---------------------------------------------------------------------------
# 2. Things that were looked for and are NOT published by the official page
# ---------------------------------------------------------------------------
# A blank here is evidence: the official page was opened and did not print the
# value. Each entry says what was looked for and what the page said instead.
NOT_PUBLISHED = [
    dict(id="N01", what="A date-specific room rate for 6-13 December 2026 at any Strip hotel",
         tried=["https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
                "https://www.venetianlasvegas.com/resort/resort-fee.html"],
         result=("The Venetian publishes a starting floor ('as low as $119 and $209 and can be higher') and states future rates are "
                 "given out only to 150 days. No page prints a nightly rate for a specific date. Booking engines are JavaScript "
                 "applications and return no price to a page reader."),
         site_effect="Every room-rate cell stays blank; the trip planner reports the hotel term as Incomplete (F14/F51)."),
    dict(id="N02", what="A Caesars Palace or Horseshoe property-specific resort fee",
         tried=["https://www.caesars.com/caesars-palace/hotel", "https://www.caesars.com/corporate/disclaimer"],
         result=("The hotel page prints no fee. The corporate disclaimer prints only the $45-$60 range that applies to all properties."),
         site_effect="Both fee cells stay blank and are listed as unverified (F09)."),
    dict(id="N03", what="An official walking time between two different Strip properties, e.g. Wynn to the Venetian poker room",
         tried=["https://www.mgmresorts.com/en/things-to-do/parking.html",
                "https://www.venetianlasvegas.com/resort/casino/poker.html"],
         result=("The MGM parking page prints walking times to T-Mobile Arena only. No hotel or poker-room page prints a walking time "
                 "to another property's poker room."),
         site_effect="Cross-property walk times stay blank and flagged; the ≤30-minute filter cannot be applied to them (F15/F50)."),
    dict(id="N04", what="A published finish time for any DeepStack Extravaganza IV event",
         tried=["https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"],
         result=("The schedule prints start times, guarantees and structure-sheet links. Registration-close times appear on the "
                 "structure sheets; finish times appear nowhere."),
         site_effect="The overlap check needs the traveller's assumed playing length and is labelled as an assumption (Q17)."),
    dict(id="N05", what="A Horseshoe or Resorts World poker tournament schedule",
         tried=["https://www.caesars.com/horseshoe-las-vegas/casino", "https://www.rwlasvegas.com/casino/poker/"],
         result=("The Resorts World poker URL returned a marketing eblast page with no schedule and no room details; the Caesars "
                 "Horseshoe casino page links no schedule. Nothing was invented."),
         site_effect="No rows exist for these rooms; they remain coverage gaps (F11/F13/F26)."),
    dict(id="N07", what="A street address on the MGM reservation-terms pages (used for a walking route)",
         tried=["https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
                "https://aria.mgmresorts.com/en/terms-and-conditions.html",
                "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html"],
         result=("The terms pages print the resort fee, occupancy and cancellation rules and no street address. The three MGM "
                 "hotels this pass added therefore have an empty address cell, so no maps route link is generated for them and no "
                 "walking time can be derived."),
         site_effect="Address and route cells stay blank and flagged for the three MGM hotels; their fee and cancellation evidence "
                     "is still published because it does not depend on an address."),
    dict(id="N06", what="A full hotel-reservation checkout total (room + resort fee + tax + parking, itemised)",
         tried=["https://www.venetianlasvegas.com/booking", "https://www.wynnlasvegas.com/"],
         result=("No official page prints an itemised checkout total without a completed JavaScript booking flow. Terms pages print "
                 "the fee and the tax treatment separately."),
         site_effect="The calculator multiplies a dated nightly rate by nights and adds the documented fee and tax; it labels the "
                     "result an arithmetic estimate, not a quote (F51)."),
]

# ---------------------------------------------------------------------------
# 3. Rate observations read today (dated log entries, never a single value)
# ---------------------------------------------------------------------------
# Only what the official page prints. `kind` distinguishes a published floor
# from a rate for the planned dates. None of these is a quote for 6-13 Dec 2026.
RATE_OBSERVATIONS = [
    dict(hotel="The Venetian Resort (Venetian / Palazzo towers)", hotel_key="venetian",
         observed_on=READ_ON, kind="published starting rate, not a dated quote",
         nightly_low=119.0, nightly_high=209.0, currency="USD",
         resort_fee_per_night=55.0, tax_rate_pct=13.38,
         room_type="Luxury King Suite, single/double occupancy", occupancy="2 adults, 1 room",
         condition=("Poker suite rate: six hours of active live cash play, or a $300+ tournament buy-in, per night stayed; "
                    "booked by phone on 866.255.8936 with code EPOKR25 and a Venetian Rewards number. Nights that fail the "
                    "condition are re-priced at the prevailing rate."),
         parking_per_day="registered hotel guest $20/day; $0 for poker players who play three hours or more and have a supervisor confirm it",
         cancellation="",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         source_2="https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html"),
    dict(hotel="Wynn Las Vegas / Encore", hotel_key="wynn",
         observed_on=READ_ON, kind="offer terms, no nightly figure published",
         nightly_low=None, nightly_high=None, currency="USD",
         resort_fee_per_night=55.0, tax_rate_pct=13.38,
         room_type="Wynn Resort King (offer DK26WLV2, two-night maximum)", occupancy="single or double",
         condition=("Blackout dates include 17-21 November 2026 and 31 December 2026; offer runs 2 October 2026 - 31 March 2027 and "
                    "is limited to two consecutive nights, so it cannot price a seven-night stay."),
         parking_per_day="$0 - complimentary self-parking for up to two vehicles is included in the resort fee",
         cancellation="48 hours before arrival, or the one-night deposit is forfeited",
         source="https://www.wynnlasvegas.com/terms-and-conditions/DK26WLV2",
         source_2=""),
    dict(hotel="Bellagio", hotel_key="bellagio",
         observed_on=READ_ON, kind="mandatory fee and cancellation term, no nightly figure published",
         nightly_low=None, nightly_high=None, currency="USD",
         resort_fee_per_night=55.0, tax_rate_pct=13.38,
         room_type="", occupancy="2 adults, 1 room",
         condition="Fee applies to all reservations; waived for MGM Rewards Gold+ on eligible reservations.",
         parking_per_day="$20 self-parking (registered hotel guest), $40 valet",
         cancellation="72 hours before arrival (standard term; a booked offer may exclude it)",
         source="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
         source_2="https://www.mgmresorts.com/en/things-to-do/parking.html"),
    dict(hotel="ARIA Resort & Casino", hotel_key="aria",
         observed_on=READ_ON, kind="mandatory fee and cancellation term, no nightly figure published",
         nightly_low=None, nightly_high=None, currency="USD",
         resort_fee_per_night=55.0, tax_rate_pct=13.38,
         room_type="", occupancy="2 adults, 1 room",
         condition="Fee applies to all reservations; waived for MGM Rewards Gold+ on eligible reservations.",
         parking_per_day="$20 self-parking (registered hotel guest), $40 valet",
         cancellation="72 hours before arrival (standard term; a booked offer may exclude it)",
         source="https://aria.mgmresorts.com/en/terms-and-conditions.html",
         source_2="https://www.mgmresorts.com/en/things-to-do/parking.html"),
    dict(hotel="MGM Grand", hotel_key="mgmgrand",
         observed_on=READ_ON, kind="mandatory fee and cancellation term, no nightly figure published",
         nightly_low=None, nightly_high=None, currency="USD",
         resort_fee_per_night=50.0, tax_rate_pct=13.38,
         room_type="", occupancy="2 adults, 1 room",
         condition="Fee applies to all reservations; waived for MGM Rewards Gold+ on eligible reservations.",
         parking_per_day="$20 self-parking (registered hotel guest), $40 valet",
         cancellation="72 hours before arrival (standard term; a booked offer may exclude it)",
         source="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
         source_2="https://www.mgmresorts.com/en/things-to-do/parking.html"),
    dict(hotel="Resorts World Las Vegas (Hilton / Conrad / Crockfords)", hotel_key="resortsworld",
         observed_on=READ_ON, kind="offer term, no nightly figure published",
         nightly_low=None, nightly_high=None, currency="USD",
         resort_fee_per_night=55.0, tax_rate_pct=13.38,
         room_type="", occupancy="2 adults, 1 room",
         condition="Carried forward from the 'All Resort, No Fees' offer terms recorded on 2026-11-19 by an earlier session; not re-read here.",
         parking_per_day="",
         cancellation="48 hours before check-in for a deposit refund",
         source="https://www.rwlasvegas.com/offers/all-resort-no-fees/",
         source_2=""),
]

# ---------------------------------------------------------------------------
# 4. Arithmetic performed on the verified fee/tax values (shown, never hidden)
# ---------------------------------------------------------------------------
# true nightly cost = advertised nightly rate + mandatory resort fee + tax on
# the sum, using the Clark County rate. The advertised nightly rate is NOT
# verified for the trip dates, so every line below keeps that cell blank.
def fee_math():
    rows = []
    seen = {}
    for o in RATE_OBSERVATIONS:
        fee = o.get("resort_fee_per_night")
        if fee in (None, ""):
            continue
        key = (o["hotel"], fee)
        if key in seen:
            continue
        seen[key] = True
        rows.append(dict(hotel=o["hotel"], fee=fee, tax=o["tax_rate_pct"],
                         tax_on_fee=round(fee * o["tax_rate_pct"] / 100.0, 2),
                         fee_with_tax=round(fee * (1 + o["tax_rate_pct"] / 100.0), 2),
                         source=o["source"]))
    return rows


EXTRA_FLAGS = [
    dict(id="F62", area="Source mismatch",
         title="Four live schedule names carry a promotional suffix the stored rows keep in notes",
         detail=("Re-reading the official DSE IV page on 2026-11-19 showed rows #3, #4, #5 as '$200 NLH RaceDay Stack (1Day) - Race "
                 "to finish before the Race' and #35 as '$600 NLH LIPS Poker Jingle Tag Team $10K GTD (1Day) - Tag Teams Consist of "
                 "Female/Female or Female/Male', where the stored rows stop at the structure-sheet title and carry the suffix in "
                 "notes. Date, start time, event number, buy-in, guarantee and sheet number all match. Logged rather than edited: "
                 "changing event names is a data-owner decision, and no displayed value is affected."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F63", area="Hotel cost",
         title="The only Wynn terms page with a dated fee is a two-night promotional offer, not a 7-night rate",
         detail=("The Wynn page that prints the $55 resort fee and the 48-hour cancellation rule is offer DK26WLV2: two-night maximum, "
                 "select dates 2 October 2026 - 31 March 2027, blackouts including 17-21 November 2026 and 31 December 2026. It cannot "
                 "price a seven-night stay. The fee itself ($55 plus tax) is a property-wide term and is used as such; the stay "
                 "conditions are not transferable to a longer booking, so the Wynn row in the cost calculator stays Incomplete."),
         source="https://www.wynnlasvegas.com/terms-and-conditions/DK26WLV2"),
    dict(id="F64", area="Hotel cost",
         title="MGM resort fees are property-specific ($55 vs $50) and were previously left entirely blank",
         detail=("Bellagio and ARIA print $55.00 plus applicable tax; MGM Grand prints $50.00 plus applicable tax. Before this re-check "
                 "all MGM rooms were blank (F10). The three pages read on 2026-11-19 now supply the fee, the $50/$40 additional-occupant "
                 "charge, the 72-hour standard cancellation term and the parking rates. A corporate MGM figure still must not be "
                 "reused across properties, and no MGM room rate for the trip dates is published anywhere."),
         source="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html"),
    dict(id="F65", area="Entry rules",
         title="The live schedule page does not state entry rules; every single-entry label still rests on a structure sheet",
         detail=("The DSE IV schedule page prints date, time, event number, name, guarantee and a structure-sheet link. It never states "
                 "single entry, re-entry, rebuy or add-on. So the live row-level re-read in this session confirms WHAT and WHEN, not "
                 "the entry rule. The 53 'standard S1' labels therefore still rest on the structure-sheet reads logged on the "
                 "Verification page (F01), and six of the sheets behind the trip window were not re-read in this session."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
]
