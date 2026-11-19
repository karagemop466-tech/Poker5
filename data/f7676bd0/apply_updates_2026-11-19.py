#!/usr/bin/env python3
"""Apply the 2026-11-19 live captures to data/ea99006a (session f7676bd0).

Every value written here comes from an official page read on 2026-11-19; see
data/f7676bd0/live-capture-2026-11-19.md for the raw capture log. Nothing is
estimated: figures the pages did not return stay null and are flagged.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATA = os.path.join(ROOT, "data", "ea99006a")

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)

def save(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

V_BOOK = "https://www.venetianlasvegas.com/booking/?adults=2&children=0&checkin=2026-12-06&checkout=2026-12-13&view=calendar"
V_TERMS = "https://www.venetianlasvegas.com/content/venetian/us/en/legal/hotel-terms-and-conditions.html"
V_CONTACT = "https://www.venetianlasvegas.com/resort/contact.html"
V_POKER = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
C_CLV = "https://www.caesars.com/book/hotel-calendar?propCode=clv&arrivalDate=12/06/2026&departureDate=12/13/2026&adults=2&rooms=1&flexibleCalendar=1101100110000000000000000000000000000000000000000000000000000000"
C_BLV = "https://www.caesars.com/book/hotel-calendar?propCode=blv&arrivalDate=12/06/2026&departureDate=12/13/2026&adults=2&rooms=1&flexibleCalendar=1101100110000000000000000000000000000000000000000000000000000000"
W_DETAILS = "https://reservations.wynnlasvegas.com/ibe/details.aspx?hotelID=13763&langID=1&rmID=68658&checkin=12/06/2026&checkout=12/13/2026"
W_CONTACT = "https://www.wynnlasvegas.com/about-us/contact-information"
RW_IBE = "https://reservations.rwlasvegas.com/ibe/shop.aspx?selectedTower=HILTON&hotelID=17726&checkin=2026-12-06&checkout=2026-12-13&nights=7&adults=2"
RW_OFFER = "https://www.rwlasvegas.com/offers/all-resort-no-fees"
RW_LOC = "https://www.rwlasvegas.com/location-directions/"
GM = "https://www.google.com/maps/dir"

def gm(a, b):
    return "%s/%s/%s/data=!4m2!4m1!3e2" % (GM, a, b)

A_VEN = "3355+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"
A_WYN = "Wynn+Las+Vegas,+3131+Las+Vegas+Blvd+South,+Las+Vegas,+NV"
A_WYN2 = "3131+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"
A_CAE = "3570+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"
A_HOR = "3645+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"
A_RW = "3000+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"
A_SP = "9777+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"

# ---------------------------------------------------------------- routes.json
routes = load("routes.json")
# hotel_key, venue_key -> (minutes, miles, via, reverse_minutes, reverse_miles, reverse_via, url, reverse_url)
MEAS = {
    ("venetian", "wynn"): (26, 1.1, "Encore Resort Blvd", 14, 0.5, "Wynn Main Gate Dr",
                           gm(A_VEN, A_WYN), gm(A_WYN, A_VEN)),
    ("wynn", "venetian"): (14, 0.5, "Wynn Main Gate Dr", 26, 1.1, "Encore Resort Blvd",
                           gm(A_WYN, A_VEN), gm(A_VEN, A_WYN)),
    ("venetian", "caesars"): (26, 1.1, "Mystere Dreams Ave", 25, 1.0, "Mystere Dreams Ave",
                              gm(A_VEN, A_CAE), gm(A_CAE, A_VEN)),
    ("caesars", "venetian"): (25, 1.0, "Mystere Dreams Ave", 26, 1.1, "Mystere Dreams Ave",
                              gm(A_CAE, A_VEN), gm(A_VEN, A_CAE)),
    ("venetian", "horseshoe"): (30, 1.3, "Krueger Dr", 31, 1.3, "Krueger Dr",
                                gm(A_VEN, A_HOR), gm(A_HOR, A_VEN)),
    ("horseshoe", "venetian"): (31, 1.3, "Krueger Dr", 30, 1.3, "Krueger Dr",
                                gm(A_HOR, A_VEN), gm(A_VEN, A_HOR)),
    ("venetian", "resortsworld"): (21, 0.9, "Las Vegas Blvd S", 21, 0.9, "Las Vegas Blvd S",
                                   gm(A_VEN, A_RW), gm(A_RW, A_VEN)),
    ("resortsworld", "venetian"): (21, 0.9, "Las Vegas Blvd S", 21, 0.9, "Las Vegas Blvd S",
                                   gm(A_RW, A_VEN), gm(A_VEN, A_RW)),
    ("venetian", "southpoint"): (204, 9.0, "Frank Sinatra Dr and Las Vegas Blvd S", None, None, None,
                                gm(A_VEN, A_SP), None),
    ("wynn", "caesars"): (47, 2.1, "Fashion Show Dr", 39, 1.7, "Las Vegas Blvd S",
                          gm(A_WYN2, A_CAE), gm(A_CAE, A_WYN2)),
    ("caesars", "wynn"): (39, 1.7, "Las Vegas Blvd S", 47, 2.1, "Fashion Show Dr",
                          gm(A_CAE, A_WYN2), gm(A_WYN2, A_CAE)),
    ("wynn", "horseshoe"): (40, 1.7, "Las Vegas Blvd S", 39, 1.7, "Las Vegas Blvd S",
                            gm(A_WYN2, A_HOR), gm(A_HOR, A_WYN2)),
    ("horseshoe", "wynn"): (39, 1.7, "Las Vegas Blvd S", 40, 1.7, "Las Vegas Blvd S",
                            gm(A_HOR, A_WYN2), gm(A_WYN2, A_HOR)),
    ("wynn", "resortsworld"): (11, 0.5, "Encore Resort Blvd", 12, 0.5, "Encore Resort Blvd",
                               gm(A_WYN2, A_RW), gm(A_RW, A_WYN2)),
    ("resortsworld", "wynn"): (12, 0.5, "Encore Resort Blvd", 11, 0.5, "Encore Resort Blvd",
                               gm(A_RW, A_WYN2), gm(A_WYN2, A_RW)),
    ("wynn", "southpoint"): (204, 8.9, "Las Vegas Blvd S", None, None, None,
                            gm(A_WYN2, A_SP), None),
    ("caesars", "horseshoe"): (18, 0.8, "Jay Sarno Wy", 19, 0.8, "Jay Sarno Wy",
                               gm(A_CAE, A_HOR), gm(A_HOR, A_CAE)),
    ("horseshoe", "caesars"): (19, 0.8, "Jay Sarno Wy", 18, 0.8, "Jay Sarno Wy",
                               gm(A_HOR, A_CAE), gm(A_CAE, A_HOR)),
    ("caesars", "resortsworld"): (33, 1.5, "Las Vegas Blvd S", 34, 1.5, "Las Vegas Blvd S",
                                  gm(A_CAE, A_RW), gm(A_RW, A_CAE)),
    ("resortsworld", "caesars"): (34, 1.5, "Las Vegas Blvd S", 33, 1.5, "Las Vegas Blvd S",
                                  gm(A_RW, A_CAE), gm(A_CAE, A_RW)),
    ("caesars", "southpoint"): (180, 8.0, "Frank Sinatra Dr and Las Vegas Blvd S", None, None, None,
                               gm(A_CAE, A_SP), None),
    ("horseshoe", "resortsworld"): (33, 1.5, "Las Vegas Blvd S", 34, 1.5, "Las Vegas Blvd S",
                                    gm(A_HOR, A_RW), gm(A_RW, A_HOR)),
    ("resortsworld", "horseshoe"): (34, 1.5, "Las Vegas Blvd S", 33, 1.5, "Las Vegas Blvd S",
                                    gm(A_RW, A_HOR), gm(A_HOR, A_RW)),
    ("horseshoe", "southpoint"): (165, 7.2, "Las Vegas Blvd S", None, None, None,
                                 gm(A_HOR, A_SP), None),
    ("resortsworld", "southpoint"): (198, 8.7, "Las Vegas Blvd S", None, None, None,
                                    gm(A_RW, A_SP), None),
}

for r in routes:
    key = (r["hotel_key"], r["venue_key"])
    if r.get("same_property"):
        r["verified"] = True
        r["retrieved"] = "2026-11-19"
        r["method"] = ("On the same property: the poker room is inside the hotel. Re-verified 2026-11-19 "
                       "from the official poker page (the Venetian poker room is at The Palazzo, level 2, "
                       "Grand Canal Shoppes).")
        continue
    m = MEAS[key]
    minutes, miles, via, rmin, rmiles, rvia, url, rurl = m
    r["minutes"] = minutes
    r["verified"] = True
    r["distance_miles"] = miles
    r["via"] = via
    r["maps"] = url
    r["retrieved"] = "2026-11-19"
    rev = ""
    if rmin is not None:
        r["reverse_minutes"] = rmin
        r["reverse_distance_miles"] = rmiles
        r["reverse_via"] = rvia
        rev = (" The reverse direction measured %d min (%.1f mi, via %s) the same day; Google Maps walking "
               "routes are asymmetric by entrance pin placement (flag F58), so each direction is stored as "
               "measured and neither figure is smoothed." % (rmin, rmiles, rvia))
    r["method"] = ("Measured on Google Maps walking directions between the official street addresses on "
                   "2026-11-19 (primary walking route: %d min, %.1f mi, via %s).%s The walk is to the "
                   "property entrance; the poker room is inside the destination property, so add in-property "
                   "walking time. No hotel page publishes this figure (flag F50)."
                   % (minutes, miles, via, rev))
save("routes.json", routes)

# ---------------------------------------------------------------- hotels.json
hotels = load("hotels.json")
by_key = {h["key"]: h for h in hotels}

v = by_key["venetian"]
v["address"] = "3355 Las Vegas Blvd. South, Las Vegas, NV 89109"
v["address_source"] = V_CONTACT
v["cancel"] = ("One night's room rate and tax (or the full stay for some offers) charged as the deposit when "
               "the reservation is confirmed; prepaid offers are non-cancellable and non-refundable; a no-show "
               "cancels the entire reservation and forfeits the first-night deposit; early departure fee $100 "
               "plus tax (official hotel terms, read 2026-11-19).")
v["cancel_source"] = V_TERMS
v["cancel_read"] = "2026-11-19"
v["parking"] = ("Hotel guests $20 per day; non-guests $20 per day Mon-Thu and $25 per day Fri-Sun; valet $40 "
                "per day; Nevada residents the first 3 hours free; Sapphire+ self-parking free, Ruby+ valet "
                "free (official hotel terms, read 2026-11-19). Poker validation: registered hotel guests and "
                "non-registered players with 3+ hours of live play are comped self-parking (official poker "
                "pages).")
v["parking_source"] = V_TERMS
v["parking_read"] = "2026-11-19"
v["resort_fee_read"] = "2026-11-19"
v["tax_note"] = "Daily rates do not include the applicable Clark County Room Tax of 13.38% (official hotel terms)."
v["tax_note_source"] = V_TERMS
v["check_in_out"] = "Check-in 3:00 p.m., check-out 11:00 a.m. (official hotel terms)."

w = by_key["wynn"]
w["address"] = "3131 Las Vegas Blvd. South, Las Vegas, NV 89109"
w["address_source"] = W_CONTACT
w["cancel"] = ("Deposit of one night's room rate and tax charged at booking; free cancellation until 72 hours "
               "before arrival on the Flexible Getaway and 'Your Fall to Have It All' rates (one night's room "
               "rate and tax penalty after that), and until 48 hours before arrival on offer DK26WLV2 and the "
               "Wynn Rewards Exclusive rate (read 2026-11-19).")
w["cancel_source"] = W_DETAILS
w["cancel_read"] = "2026-11-19"
w["parking"] = ("Self-parking is complimentary to registered guests; the $55 resort fee includes complimentary "
                "self-parking for up to two vehicles; incidentals $150 per night (official terms, read "
                "2026-11-19).")
w["parking_source"] = "https://www.wynnlasvegas.com/terms-and-conditions/DK26WLV2"
w["parking_read"] = "2026-11-19"
w["resort_fee_read"] = "2026-11-19"
w["rate_caveat"] = ("Only a floor: from-prices without dates ('Flexible Getaway From $319', 'Your Fall to Have "
                    "It All From $253'). For the recommended window (Dec 6-13, 2026) dated quotes of $818 and "
                    "$688 average per night (fee included, taxes excluded) are captured in the rate log. "
                    "Two member plans show sign-in-only prices.")

c = by_key["caesars"]
c["resort_fee"] = 54.95
c["resort_fee_tax"] = 7.35
c["resort_fee_total"] = 62.30
c["resort_fee_text"] = "Resort fees: $62.30 ($54.95 plus $7.35 tax) per room per day"
c["resort_fee_verified"] = True
c["resort_fee_read"] = "2026-11-19"
c["resort_fee_source"] = C_CLV
c["resort_fee_note"] = ("Official booking-page Hotel Policies (read 2026-11-19): 'Resort fees: $62.30 ($54.95 "
                        "plus $7.35 tax). Resort fees are not assessed for Diamond and Seven Stars guests. "
                        "Deposit: $100 per day. Please note that there will be a $50 per night plus tax fee for "
                        "no show if reservation is not cancelled by 6pm of arrival date.' The corporate "
                        "disclaimer's $45-$60 range remains the figure published for other Caesars properties.")
c["booking_note"] = ("Booking page renders with 'FREE 48-Hour Cancellation' and 'Resort fees and taxes are not "
                     "included in the room rate displayed' (read 2026-11-19); the December 2026 rate calendar "
                     "returned 'Sorry! Our website is currently experiencing technical difficulties' on that "
                     "date, so no dated Caesars Palace quote is stored (flag F56).")
c["cancel"] = ("FREE 48-Hour Cancellation (official booking widget); deposit $100 per day; comp-room no-show "
               "fee $50 plus tax unless cancelled by 6 p.m. of arrival date (read 2026-11-19).")
c["cancel_source"] = C_CLV
c["cancel_read"] = "2026-11-19"
c["parking"] = ("Parking surcharge applies; complimentary for Platinum+ cardholders and registered hotel "
                "guests; Nevada residents the first 3 hours free on non-event days (read 2026-11-19). No "
                "dollar amounts are published.")
c["parking_source"] = C_CLV
c["parking_read"] = "2026-11-19"

hs = by_key["horseshoe"]
hs["resort_fee"] = 49.95
hs["resort_fee_tax"] = 6.68
hs["resort_fee_total"] = 56.63
hs["resort_fee_text"] = "Resort fees: $56.63 ($49.95 plus $6.68 tax) per room per day"
hs["resort_fee_verified"] = True
hs["resort_fee_read"] = "2026-11-19"
hs["resort_fee_source"] = C_BLV
hs["resort_fee_note"] = ("Official booking-page Hotel Policies (read 2026-11-19): 'Resort fees: $56.63 ($49.95 "
                         "plus $6.68 tax)'. The same page's calendar caption says displayed rates 'include "
                         "applicable resort fees'; how the fee is itemised in a stay total was not returned.")
hs["booking_note"] = ("Booking page renders the December 2026 flexible calendar with 'FREE 48-Hour "
                      "Cancellation' and 'Resort fees and taxes are not included in the room rate displayed' "
                      "(read 2026-11-19); daily figures are captured in the rate log (flag F59 on their "
                      "per-date meaning).")
hs["cancel"] = ("FREE 48-Hour Cancellation (official booking widget); deposit $50 per day; pet fee $75; "
                "rollaway $30 per day (read 2026-11-19).")
hs["cancel_source"] = C_BLV
hs["cancel_read"] = "2026-11-19"
hs["parking"] = ("Parking surcharge applies; complimentary for Platinum+ cardholders and registered hotel "
                 "guests; Nevada residents the first 3 hours free on non-event days (read 2026-11-19). No "
                 "dollar amounts are published.")
hs["parking_source"] = C_BLV
hs["parking_read"] = "2026-11-19"

rw = by_key["resortsworld"]
rw["address"] = ("3000 South Las Vegas Boulevard, Las Vegas, Nevada 89109 (Hilton tower 999 Resorts World Ave, "
                 "Conrad 111, Crockfords 333)")
rw["address_source"] = RW_LOC
rw["cancel"] = ("Deposit of the first night's room rate plus taxes charged at booking; free cancellation until "
                "48 hours before check-in ('2-day cancelation period for full refund eligibility'); $150 per "
                "night incidental deposit at check-in (offer terms, read 2026-11-19).")
rw["cancel_source"] = RW_OFFER
rw["cancel_read"] = "2026-11-19"
rw["parking"] = ("Self-parking is complimentary for Nevada residents with NV plates and for Genting Rewards "
                 "Elite, Prime, Monarch and Imperial members; fee amounts for other guests are not published "
                 "(offer page, read 2026-11-19).")
rw["parking_source"] = RW_OFFER
rw["parking_read"] = "2026-11-19"
rw["resort_fee_read"] = "2026-11-19"
rw["resort_fee_note"] = ("The $55 daily resort fee is waived on the official 'All Resort, No Fees' offer for "
                         "travel through December 28, 2026; the standard fee is $55 per room per day. The "
                         "offer page also states 'Rates do not include Standard room rate taxes of 13.38%'. "
                         "The official booking engine's December 2026 calendar shows conflicting fee-inclusion "
                         "captions (flag F57).")
rw["rate_caveat"] = ("Rooms-only convention pricing before taxes and the waived $55 resort fee. No dated quote "
                     "was returned for the Dec 6-13 window: the official booking engine displayed a December "
                     "2026 calendar (figures captured in the rate log) and reported no rate for the 7-night "
                     "query (flag F57/F59).")
save("hotels.json", hotels)

# ---------------------------------------------------------------- rate_snapshots.json
snap = load("rate_snapshots.json")
snap["note"] = ("Dated log of hotel stay captures (rates are a log, never a single value). Each entry is a "
                "snapshot with its rate timestamp and the official source it was read from. Fields that the "
                "official pages never returned are left null - never inferred. Like-for-like comparison needs "
                "the same room type, occupancy and cancellation policy; until a hotel returns one itemised "
                "checkout total for the trip dates, the calculator stays incomplete. For 2026-12-06 to "
                "2026-12-13 two dated Wynn quotes and two official December calendars (Horseshoe, Resorts "
                "World) were captured on 2026-11-19 alongside a logged Venetian engine attempt; calendars are "
                "raw daily displays, not checkout totals (flags F32, F57, F59).")
snap["tax_note"] = ("Clark County room tax: 13.38% (official ordinance). The Venetian hotel terms confirm it "
                    "from the hotel side: 'Daily rates do not include the applicable Clark County Room Tax of "
                    "13.38%' (read 2026-11-19). The Horseshoe fee tax ($6.68 on $49.95) and Caesars Palace fee "
                    "tax ($7.35 on $54.95) are consistent with it. The Wynn quotes display 'Includes Resort "
                    "Fee, Excludes taxes' and returned no tax figure.")
entries = snap.setdefault("entries", [])
entries.append({
    "id": "RS-2026-11-19-WYNN-FLEX",
    "kind": "dated booking-engine quote",
    "hotel": "Wynn Las Vegas",
    "hotel_key": "wynn",
    "room_type": "Wynn Resort King (640 sq ft), 1 King, non-smoking",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "occupancy": "2 adults, 1 room",
    "checkout_total": None,
    "nightly_average": 818.0,
    "room_rate_per_night": None,
    "resort_fee_per_night": 55.0,
    "resort_fee_total": None,
    "tax_total": None,
    "tax_note": "Page caption: 'Includes Resort Fee, Excludes taxes'; no tax figure was returned.",
    "parking": "Self-parking complimentary to registered guests (up to two vehicles); incidentals $150 per night.",
    "cancellation_deadline": "72 hours before arrival (one night's room rate and tax penalty); one night's room rate and tax charged at booking.",
    "rate_timestamp": "2026-11-19",
    "source": W_DETAILS,
    "source_label": "Wynn official booking engine, rate details for the stay (read 2026-11-19)",
    "verified": True,
    "caveats": [
        "Displayed as an average nightly rate for the 7-night 'Dec. 6 - 13, 2026' stay; the page shows no checkout total.",
        "The displayed rate includes the $55 resort fee and excludes taxes.",
        "The same stay under 'Your Fall to Have It All' (book by November 24, 2026) displays $688.00 average per night.",
        "Wonder of Wynn and Wynn Rewards Exclusive plans show sign-in-only prices and were not captured.",
    ],
})
entries.append({
    "id": "RS-2026-11-19-WYNN-FALL",
    "kind": "dated booking-engine quote",
    "hotel": "Wynn Las Vegas",
    "hotel_key": "wynn",
    "room_type": "Wynn Resort King (640 sq ft), 1 King, non-smoking",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "occupancy": "2 adults, 1 room",
    "checkout_total": None,
    "nightly_average": 688.0,
    "room_rate_per_night": None,
    "resort_fee_per_night": 55.0,
    "resort_fee_total": None,
    "tax_total": None,
    "tax_note": "Page caption: 'Includes Resort Fee, Excludes taxes'; no tax figure was returned.",
    "parking": "Self-parking complimentary to registered guests (up to two vehicles); incidentals $150 per night.",
    "cancellation_deadline": "72 hours before arrival (one night's room rate and tax penalty); offer must be booked by November 24, 2026.",
    "rate_timestamp": "2026-11-19",
    "source": W_DETAILS,
    "source_label": "Wynn official booking engine, rate details for the stay (read 2026-11-19)",
    "verified": True,
    "caveats": [
        "'Your Fall to Have It All' offer, displayed as $688.00 average per night for the 7-night stay; the page shows no checkout total.",
        "The displayed rate includes the $55 resort fee and excludes taxes; one night's room rate and tax is charged at booking.",
        "The offer's extra-savings dates are December 6-9, 2026 (one-week stay minimum); the per-night breakdown was not displayed.",
    ],
})
entries.append({
    "id": "RS-2026-11-19-HORSESHOE-CAL",
    "kind": "flexible-date calendar capture",
    "hotel": "Horseshoe Las Vegas",
    "hotel_key": "horseshoe",
    "room_type": "not stated (calendar shows the lowest available rate)",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "occupancy": "2 adults, 1 room",
    "checkout_total": None,
    "nightly_average": None,
    "room_rate_per_night": None,
    "resort_fee_per_night": 49.95,
    "resort_fee_total": None,
    "tax_total": None,
    "tax_note": "Calendar caption says displayed rates 'include applicable resort fees'; tax treatment of the displayed figures is not stated. The fee itself is itemised in Hotel Policies as $49.95 plus $6.68 tax.",
    "parking": "Parking surcharge applies; complimentary for Platinum+ cardholders and registered hotel guests; Nevada residents the first 3 hours free on non-event days (same page).",
    "cancellation_deadline": "Free 48-hour cancellation (booking widget); deposit $50 per day (Hotel Policies, same page).",
    "rate_timestamp": "2026-11-19",
    "calendar_rates": {"2026-12-06": 245, "2026-12-07": 202, "2026-12-08": 151, "2026-12-09": 134,
                       "2026-12-10": 325, "2026-12-11": 432, "2026-12-12": 449},
    "calendar_other": {"2026-12-13": 55},
    "source": C_BLV,
    "source_label": "Caesars official booking engine, Horseshoe December 2026 calendar (read 2026-11-19)",
    "verified": True,
    "caveats": [
        "Caption: 'Rates shown reflect the lowest available rate and include applicable resort fees. All pricing may vary by length of stay.'",
        "The page does not state whether a date's figure is for the night of that date or for a stay beginning that date (flag F59); stored as a raw display map.",
        "No checkout total is displayed; these figures are not a stay quote. The seven figures for Dec 6-12 sum to $1,938, but that arithmetic is not a booking total and is not stored as one.",
        "Other December displays: Dec 1 $457; Dec 2-3 no rate ('The rate is not available. Select an alternate rate.'); Dec 4 $194; Dec 5 $330; Dec 13 $55.",
    ],
})
entries.append({
    "id": "RS-2026-11-19-RW-CAL",
    "kind": "flexible-date calendar capture",
    "hotel": "Resorts World Las Vegas (Hilton tower)",
    "hotel_key": "resortsworld",
    "room_type": "Double Queen (two queen beds)",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "occupancy": "2 adults, 1 room",
    "checkout_total": None,
    "nightly_average": None,
    "room_rate_per_night": None,
    "resort_fee_per_night": 55.0,
    "resort_fee_total": None,
    "tax_total": None,
    "tax_note": "Two conflicting captions appear on the same page (flag F57): 'Calendar pricing excludes daily resort fee and taxes' and 'Calendar pricing includes $55 daily resort fee and excludes taxes'. 'Rates do not include Standard room rate taxes of 13.38%'.",
    "parking": "Self-parking complimentary for Nevada residents and Genting Rewards Elite+ members (offer page).",
    "cancellation_deadline": "Deposit of the first night's room rate plus taxes at booking; free cancellation until 48 hours before check-in (offer terms).",
    "rate_timestamp": "2026-11-19",
    "calendar_rates": {"2026-12-06": 354, "2026-12-07": 654, "2026-12-08": 354, "2026-12-09": 414,
                       "2026-12-10": 414, "2026-12-12": 454},
    "calendar_other": {"2026-12-13": 184},
    "source": RW_IBE,
    "source_label": "Resorts World official booking engine, December 2026 calendar (read 2026-11-19)",
    "verified": True,
    "caveats": [
        "Conflicting fee-inclusion captions on one page (flag F57); the stored figures are the raw displays.",
        "The 7-night Dec 6-13 query returned 'The rate is not available. Select an alternate rate.', so no stay quote exists.",
        "Dec 11 displayed no number; the legend marks such dates Unavailable / Closed to Arrival / Closed to Departure.",
        "The six displayed figures for Dec 6-12 sum to $2,586 (Dec 11 blank) - arithmetic only, not a booking total, not stored as one.",
        "Per-date meaning not stated by the page (flag F59).",
    ],
})
entries.append({
    "id": "RS-2026-11-19-VENETIAN-ATTEMPT",
    "kind": "booking-engine attempt (no rate returned)",
    "hotel": "The Venetian Resort",
    "hotel_key": "venetian",
    "room_type": "suite-and-rate grid (Promo Suite, Luxury, Premium, Bella, Fortuna, Prestigia, Murano, Piazza, Concierge)",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "occupancy": "2 adults, 1 room",
    "checkout_total": None,
    "nightly_average": None,
    "room_rate_per_night": None,
    "resort_fee_per_night": 55.0,
    "resort_fee_total": None,
    "tax_total": None,
    "tax_note": "Caption captured: 'Pricing shown is best available suite and rate, includes daily resort fee, excludes taxes'.",
    "parking": "Hotel guests $20 per day; non-guests $20/$25; valet $40 per day (official hotel terms).",
    "cancellation_deadline": "Not returned by the booking engine; the hotel terms state first-night (or full-stay) deposit at confirmation and no refund for prepaid offers.",
    "rate_timestamp": "2026-11-19",
    "source": V_BOOK,
    "source_label": "Venetian official booking engine, calendar view attempt (read 2026-11-19)",
    "verified": False,
    "caveats": [
        "The booking engine rendered only '$XXX' placeholders server-side on 2026-11-19; no numeric rate was returned, so nothing is stored.",
        "The official poker-suite rates ($119/$209, conditional on 6 hours of live play or a $300+ entry every night) are floors published 150 days out and are not quotes for these dates.",
    ],
})
entries.append({
    "id": "RS-2026-11-19-CAESARS-ATTEMPT",
    "kind": "booking-engine attempt (search error)",
    "hotel": "Caesars Palace",
    "hotel_key": "caesars",
    "room_type": None,
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "occupancy": "2 adults, 1 room",
    "checkout_total": None,
    "nightly_average": None,
    "room_rate_per_night": None,
    "resort_fee_per_night": 54.95,
    "resort_fee_total": None,
    "tax_total": None,
    "tax_note": "Hotel Policies on the same page itemise the fee tax: $54.95 plus $7.35 tax per night.",
    "parking": "Parking surcharge applies; complimentary for Platinum+ and registered guests (same page).",
    "cancellation_deadline": "FREE 48-Hour Cancellation (booking widget); deposit $100 per day (Hotel Policies).",
    "rate_timestamp": "2026-11-19",
    "source": C_CLV,
    "source_label": "Caesars official booking engine, Caesars Palace December 2026 attempt (read 2026-11-19)",
    "verified": False,
    "caveats": [
        "The rate search returned 'Sorry! Our website is currently experiencing technical difficulties' on 2026-11-19 and rendered no calendar; retry needed (flag F56).",
        "The same page's Hotel Policies block did return the resort fee ($62.30) and deposit terms.",
    ],
})
save("rate_snapshots.json", snap)

# ---------------------------------------------------------------- rates_log.json
rates = load("rates_log.json")
rates.append({
    "id": "RL-2026-11-19-WYNN-QUOTES",
    "hotel": "Wynn Las Vegas",
    "hotel_key": "wynn",
    "kind": "dated booking-engine quote",
    "observed_on": "2026-11-19",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "room": "Wynn Resort King",
    "occupancy": "2 adults, 1 room",
    "nightly_low": 688.0,
    "nightly_high": 818.0,
    "nightly_average": None,
    "checkout_total": None,
    "resort_fee_per_night": 55.0,
    "resort_fee_total": None,
    "tax_rate_pct": None,
    "tax_total": None,
    "true_nightly_low": 780.05,
    "true_nightly_high": 927.45,
    "cancellation_deadline": "72 hours before arrival (one night's room rate and tax penalty); one night's room rate and tax charged at booking.",
    "parking": "Self-parking complimentary to registered guests (up to two vehicles).",
    "source": W_DETAILS,
    "source_label": "Wynn official booking engine (read 2026-11-19)",
    "verified": True,
    "disp": "Wynn Resort King, 7-night stay Dec 6-13, 2026: Flexible Getaway $818.00 avg/night; 'Your Fall to Have It All' $688.00 avg/night (book by Nov 24, 2026). Both 'Includes Resort Fee, Excludes taxes'.",
    "caveats": [
        "Displayed values are averages per night for the stay; no checkout total was returned.",
        "The resort fee is included in the displayed prices; taxes are excluded and no tax figure was returned.",
        "true_nightly_low/high is arithmetic only: the displayed average times the 13.38% ordinance rate, not a hotel quote.",
        "Wonder of Wynn and Wynn Rewards Exclusive plans show sign-in-only prices and were not captured.",
    ],
})
rates.append({
    "id": "RL-2026-11-19-WYNN-FLOORS",
    "hotel": "Wynn Las Vegas",
    "hotel_key": "wynn",
    "kind": "published starting rate (undated)",
    "observed_on": "2026-11-19",
    "room": "Wynn Resort King",
    "nightly_low": 253.0,
    "nightly_high": 319.0,
    "checkout_total": None,
    "resort_fee_per_night": 55.0,
    "tax_rate_pct": 13.38,
    "source": "https://reservations.wynnlasvegas.com/ibe/shop.aspx?selectedTower=WYNN&hotelID=13763",
    "source_label": "Wynn official booking index (read 2026-11-19)",
    "verified": True,
    "disp": "Booking index floors: 'Flexible Getaway From $319'; 'Your Fall to Have It All From $253'.",
    "caveats": [
        "From-prices without dates; not quotes. For the recommended window the same plans quote $688-$818 (see the dated entry).",
        "All Wynn fees ($55 resort fee) are per room per day and are taxed; taxes are not included in the displayed prices.",
    ],
})
rates.append({
    "id": "RL-2026-11-19-HORSESHOE-CAL",
    "hotel": "Horseshoe Las Vegas",
    "hotel_key": "horseshoe",
    "kind": "flexible-date calendar capture",
    "observed_on": "2026-11-19",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "room": "not stated (lowest available rate)",
    "occupancy": "2 adults, 1 room",
    "nightly_low": 134.0,
    "nightly_high": 449.0,
    "checkout_total": None,
    "resort_fee_per_night": 49.95,
    "resort_fee_total": None,
    "tax_rate_pct": 13.38,
    "tax_total": None,
    "true_nightly_low": None,
    "true_nightly_high": None,
    "cancellation_deadline": "Free 48-hour cancellation; deposit $50 per day.",
    "parking": "Surcharge applies; complimentary for Platinum+ and registered guests.",
    "source": C_BLV,
    "source_label": "Caesars official booking engine, Horseshoe calendar (read 2026-11-19)",
    "verified": True,
    "disp": "December 2026 displays for the trip window: Dec 6 $245; Dec 7 $202; Dec 8 $151; Dec 9 $134; Dec 10 $325; Dec 11 $432; Dec 12 $449 (Dec 13 $55).",
    "caveats": [
        "Caption: 'Rates shown reflect the lowest available rate and include applicable resort fees. All pricing may vary by length of stay.'",
        "Per-date meaning (night of vs stay from) is not stated on the page (flag F59); no true_nightly figures are computed from these displays.",
        "No checkout total is displayed; the seven figures sum to $1,938 as arithmetic only.",
    ],
})
rates.append({
    "id": "RL-2026-11-19-RW-CAL",
    "hotel": "Resorts World Las Vegas (Hilton tower)",
    "hotel_key": "resortsworld",
    "kind": "flexible-date calendar capture",
    "observed_on": "2026-11-19",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "room": "Double Queen",
    "occupancy": "2 adults, 1 room",
    "nightly_low": 354.0,
    "nightly_high": 654.0,
    "checkout_total": None,
    "resort_fee_per_night": 55.0,
    "resort_fee_total": None,
    "tax_rate_pct": 13.38,
    "tax_total": None,
    "true_nightly_low": None,
    "true_nightly_high": None,
    "cancellation_deadline": "First night's room rate plus taxes as deposit; free cancellation until 48 hours before check-in.",
    "parking": "Self-parking complimentary for Nevada residents and Elite+ members.",
    "source": RW_IBE,
    "source_label": "Resorts World official booking engine, calendar (read 2026-11-19)",
    "verified": True,
    "disp": "December 2026 displays for the trip window: Dec 6 $354; Dec 7 $654; Dec 8 $354; Dec 9 $414; Dec 10 $414; Dec 11 (no number); Dec 12 $454 (Dec 13 $184).",
    "caveats": [
        "Conflicting captions on one page: 'Calendar pricing excludes daily resort fee and taxes' vs 'Calendar pricing includes $55 daily resort fee and excludes taxes' (flag F57).",
        "The 7-night query itself returned 'The rate is not available. Select an alternate rate.'",
        "Dec 11 displayed no number; per-date meaning is not stated (flag F59); no true_nightly figures are computed from these displays.",
    ],
})
rates.append({
    "id": "RL-2026-11-19-ATTEMPTS",
    "hotel": "The Venetian Resort / Caesars Palace",
    "hotel_key": "venetian",
    "kind": "booking-engine attempts (no rate returned)",
    "observed_on": "2026-11-19",
    "checkin": "2026-12-06",
    "checkout": "2026-12-13",
    "nights": 7,
    "checkout_total": None,
    "nightly_low": None,
    "nightly_high": None,
    "resort_fee_per_night": 55.0,
    "source": V_BOOK,
    "source_label": "Venetian and Caesars official booking engines (read 2026-11-19)",
    "verified": False,
    "disp": "No numeric rate was returned by either engine on 2026-11-19.",
    "caveats": [
        "The Venetian calendar view rendered '$XXX' placeholders only; its caption reads 'Pricing shown is best available suite and rate, includes daily resort fee, excludes taxes'.",
        "The Caesars Palace December 2026 search returned 'Sorry! Our website is currently experiencing technical difficulties' (flag F56); its Hotel Policies block did return the $62.30 fee.",
    ],
})
save("rates_log.json", rates)

# ---------------------------------------------------------------- flags.json
flags = load("flags.json")
fby = {f["id"]: f for f in flags}
fby["F09"]["title"] = "Caesars Palace and Horseshoe resort fees verified on their booking pages (was: not verified)"
fby["F09"]["detail"] = ("Resolved 2026-11-19: the official booking-page Hotel Policies blocks publish property "
                        "fees - Caesars Palace $62.30 per night ($54.95 plus $7.35 tax), Horseshoe $56.63 per "
                        "night ($49.95 plus $6.68 tax) - and are stored in hotels.json with deposits ($100/day, "
                        "$50/day) and 48-hour cancellation. The old resort-fee URLs still redirect to marketing "
                        "pages; the corporate $45-$60 range remains the only figure published for other Caesars "
                        "properties.")
fby["F09"]["source"] = C_BLV
fby["F46"]["detail"] = ("Resolved 2026-11-19 for the two candidate properties: booking-page Hotel Policies give "
                        "exact fees (Caesars Palace $54.95 plus $7.35 tax; Horseshoe $49.95 plus $6.68 tax). "
                        "The corporate disclaimer still publishes only the $45-$60 range for other Caesars "
                        "properties.")
fby["F14"]["title"] = "Dated nightly rates: Wynn captured for the window; Venetian and Caesars Palace still missing"
fby["F14"]["detail"] = ("Updated 2026-11-19: the Wynn booking engine published dated quotes for Dec 6-13, 2026 "
                        "($818 Flexible Getaway, $688 'Your Fall to Have It All', both average/night, fee "
                        "included, taxes excluded) and both are in the rate log. The Horseshoe and Resorts World "
                        "engines published December calendars (raw displays, flags F57/F59). The Venetian engine "
                        "returned '$XXX' placeholders and the Caesars Palace calendar errored, so no dated quote "
                        "exists for those two; the Venetian poker-suite rates remain floors, not quotes.")
fby["F14"]["source"] = W_DETAILS
fby["F15"]["detail"] = ("Updated 2026-11-19: still no hotel page publishes a cross-property walking time, but all "
                        "30 pairs were measured on Google Maps walking between the official addresses and are "
                        "stored per pair with retrieval date. Walking to the Venetian room: Wynn 14 min, Resorts "
                        "World 21 min, Caesars Palace 25 min, Horseshoe 30 min (one direction; see F58/F59 on "
                        "asymmetry). The on-property Venetian route remains zero minutes.")
fby["F15"]["source"] = gm(A_WYN, A_VEN)
fby["F32"]["detail"] = ("Updated 2026-11-19: the dated log now holds two dated Wynn quotes, two December calendar "
                        "captures (Horseshoe, Resorts World) and two logged engine attempts (Venetian, Caesars "
                        "Palace) for the recommended window. They are still not like-for-like: averages vs raw "
                        "daily displays vs attempts, differing rooms and rate plans, and no hotel returned an "
                        "itemised checkout total.")
fby["F32"]["source"] = W_DETAILS
fby["F33"]["detail"] = ("Updated 2026-11-19: parking and cancellation terms are now captured for all five "
                        "candidate hotels. Dollar parking fees are published only by the Venetian ($20/$25/$40 "
                        "per day, poker validation 3+ hours). Caesars Palace and Horseshoe publish policy text "
                        "(surcharge; free for Platinum+ and guests; locals 3 hours) without amounts; Resorts "
                        "World comps self-parking for locals and Elite+ members; Wynn comps registered guests.")
fby["F33"]["source"] = V_TERMS
fby["F50"]["title"] = "No hotel page publishes a walking time between two properties (routes now measured on Google Maps)"
fby["F50"]["detail"] = ("Still true - and worked around on 2026-11-19 by measuring every pair on Google Maps "
                        "walking directions between official street addresses. Values are routing estimates "
                        "retrieved on one date, not hotel-published facts, and include only the sidewalk route "
                        "to the property entrance, not in-property time.")
fby["F50"]["source"] = gm(A_VEN, A_WYN)
fby["F51"]["title"] = "The true-cost figure can now be completed for the Wynn stay, not for the others"
fby["F51"]["detail"] = ("Updated 2026-11-19: a dated official Wynn quote for Dec 6-13 exists ($688-$818 average "
                        "per night, fee included, taxes excluded), so the planner's hotel side can be completed "
                        "for a Wynn stay by typing that figure into the calculator. For the Venetian, Caesars "
                        "Palace, Horseshoe and Resorts World no itemised checkout total for the window was "
                        "returned, so the calculator stays incomplete for those until one is captured.")
fby["F51"]["source"] = W_DETAILS
flags.extend([
    {"id": "F56", "area": "Hotels",
     "title": "The Caesars Palace booking calendar returned a technical error on 2026-11-19",
     "detail": ("The official December 2026 rate calendar for Caesars Palace rendered 'Sorry! Our website is "
                "currently experiencing technical difficulties' and no rates, while the same engine rendered the "
                "Horseshoe calendar minutes later. No dated Caesars Palace quote is stored; retry needed."),
     "source": C_CLV},
    {"id": "F57", "area": "Hotels",
     "title": "Resorts World calendar shows conflicting resort-fee captions",
     "detail": ("One page displays both 'Calendar pricing excludes daily resort fee and taxes' and 'Calendar "
                "pricing includes $55 daily resort fee and excludes taxes'. Both captions are stored verbatim; "
                "the displayed calendar figures are kept as raw displays and no fee-inclusive interpretation is "
                "claimed."),
     "source": RW_IBE},
    {"id": "F58", "area": "Hotels",
     "title": "Google Maps walking routes are asymmetric by direction",
     "detail": ("Measured 2026-11-19: Wynn to Venetian 14 min (0.5 mi) but Venetian to Wynn 26 min (1.1 mi); "
                "Caesars Palace to Wynn 39 min but Wynn to Caesars Palace 47 min. Entrance pin placement and "
                "route choice differ per direction. Both directions are stored as measured; neither is smoothed "
                "or symmetrized."),
     "source": gm(A_VEN, A_WYN)},
    {"id": "F59", "area": "Hotels",
     "title": "Horseshoe to Venetian measures 31 minutes - over the 30-minute limit - in one direction",
     "detail": ("Venetian to Horseshoe measured exactly 30 min (1.3 mi, via Krueger Dr) while Horseshoe to "
                "Venetian measured 31 min (1.3 mi) on 2026-11-19. Which direction the 30-minute limit applies to "
                "changes the verdict for this hotel; both figures are published so the reader can decide. "
                "Separately, the Caesars/Horseshoe/Resorts World calendars do not state whether a date's "
                "displayed figure is for the night of that date or a stay beginning that date."),
     "source": gm(A_HOR, A_VEN)},
])
save("flags.json", flags)

# ---------------------------------------------------------------- questions.json
qs = load("questions.json")
qby = {q["id"]: q for q in qs}
qby["Q03"]["have"] = ("Resort fees (all five candidates, official): Venetian $55 plus tax; Wynn $55 plus tax; "
                      "Caesars Palace $62.30 total ($54.95 plus $7.35 tax); Horseshoe $56.63 total ($49.95 plus "
                      "$6.68 tax); Resorts World $55 waived on the 'All Resort, No Fees' offer through 28 Dec "
                      "2026. Tax 13.38% (Clark County ordinance, confirmed by the Venetian hotel terms). Dated "
                      "Wynn quotes for Dec 6-13: $688-$818 average per night (fee included, taxes excluded). "
                      "Dated December calendars for Horseshoe and Resorts World (raw displays). Parking and "
                      "cancellation terms for all five (official).")
qby["Q03"]["missing"] = ("An itemised checkout total for the actual stay at any hotel (room + fee + tax + "
                         "parking): the Wynn pages show averages only, the calendars are raw daily displays with "
                         "an undefined per-date meaning, and the Venetian and Caesars Palace engines returned no "
                         "rates at all on 2026-11-19.")
qby["Q03"]["how"] = ("Open the official booking link on the Hotels page for your dates and read the itemised "
                     "checkout screen; record it in the dated log. The Wynn calculator figure can already be "
                     "entered from the captured quote ($688-$818/night); the rest need a checkout total first.")
qby["Q14"]["have"] = ("Cancellation terms (official, read 2026-11-19): Venetian - first-night or full-stay "
                      "deposit at confirmation, prepaid offers non-refundable, no-show forfeits the deposit, "
                      "early-departure fee $100 plus tax. Wynn - one night's room rate and tax at booking; 72-"
                      "hour free cancellation on Flexible Getaway / Fall offers, 48-hour on DK26WLV2 and Wynn "
                      "Rewards Exclusive. Caesars Palace - FREE 48-Hour Cancellation, deposit $100/day. "
                      "Horseshoe - 48-hour, deposit $50/day. Resorts World - first-night deposit, 48-hour free "
                      "cancellation, $150/night incidentals.")
qby["Q14"]["missing"] = ("Which exact rate plan will be booked at each hotel (cancellation terms are "
                         "rate-plan-specific at the Wynn), and the cancellation terms behind the displayed "
                         "Horseshoe/Resorts World calendar figures.")
qby["Q16"]["q"] = "Is the calculator's hotel input backed by a dated quote for these dates?"
qby["Q16"]["have"] = ("For the Wynn yes: $688 ('Your Fall to Have It All') and $818 (Flexible Getaway) average "
                      "per night for Dec 6-13, 2026, fee included, taxes excluded (official booking engine, "
                      "read 2026-11-19). The Venetian $119/$209 poker-suite rates are floors only.")
qby["Q16"]["missing"] = ("Itemised checkout totals for the Venetian, Caesars Palace, Horseshoe and Resorts "
                         "World; the calculator stays incomplete until one is recorded for the hotel actually "
                         "chosen.")
qby["Q16"]["how"] = ("Type the captured Wynn figure into the calculator on the planner page if you plan to stay "
                     "there, or record a dated quote in the rate log for another hotel.")
qs.extend([
    {"id": "Q18", "q": "Which entrance does each walking route use, and should the limit be judged per direction?",
     "have": ("Google Maps walking times measured both ways on 2026-11-19 are stored per direction "
              "(e.g. Wynn to Venetian 14 min vs Venetian to Wynn 26 min; Horseshoe to Venetian 31 min vs the "
              "other way 30 min)."),
     "missing": ("The official entrance each route targets, and a rule for which direction the 30-minute limit "
                 "applies to. Both directions are shown so the reader can decide."),
     "how": ("Open the route link per row and walk it once at the pace you would actually use, from the "
             "entrance you would leave by; record your own minutes in the panel on the routes page.")},
    {"id": "Q19", "q": "What does a date in the Caesars/Horseshoe/Resorts World calendars price - the night of that date, or a stay starting it?",
     "have": ("The raw December 2026 displays for each candidate hotel (stored per date in the rate log and "
              "stay captures). The Horseshoe caption: 'Rates shown reflect the lowest available rate and include "
              "applicable resort fees. All pricing may vary by length of stay.'"),
     "missing": ("The per-date meaning; the pages do not state it. Until it is confirmed, the figures are not "
                 "added up into a stay total and no nightly average is claimed."),
     "how": ("Ask the hotel's reservations line in writing, or run a one-night and a multi-night query for the "
             "same date and compare what the engine displays.")},
])
save("questions.json", qs)

# ---------------------------------------------------------------- suggestions.json
sugs = load("suggestions.json")
sugs.extend([
    {"id": "S15",
     "title": "Nightly calendar capture for the hotels whose booking engines render server-side",
     "problem": ("The Horseshoe and Resorts World calendars returned full December price maps in one read, while "
                 "the Venetian and Caesars Palace engines returned nothing. One nightly scheduled capture of the "
                 "two working engines would turn the rate log into a real price history."),
     "options": ["Extend the monitor's hotel group to the two booking-engine URLs and store the per-date map",
                 "Snapshot only the seven trip nights to keep the diff small",
                 "Leave manual: rates are a log the reader appends"],
     "effect": ("Price history and change badges for hotel rates, like the ones event rows already have. In "
                "review - not implemented.")},
    {"id": "S16",
     "title": "Show both directions of every walk and let the filter use the direction that matters",
     "problem": ("Walking routes are asymmetric (Wynn to Venetian 14 min vs Venetian to Wynn 26 min). The table "
                 "shows one direction per row; a reader deciding on the walk home after midnight sees the "
                 "reverse row only if they look for it."),
     "options": ["Add a 'reverse' column with the measured minutes",
                 "Judge the 30-minute filter on the slower of the two directions",
                 "Keep per-direction rows as now and sort pairs together"],
     "effect": "Safer late-night planning. In review - not implemented."},
    {"id": "S17",
     "title": "Store the GTD to entry-fee ratio as a data field",
     "problem": ("The ratio is computed at render time (schedule tables, planner) but is not a stored field, so "
                 "it cannot be sorted or exported from the data files alone."),
     "options": ["Compute and store ratio fields when the data files are written",
                 "Add a small export script that derives the field on demand",
                 "Keep it render-only"],
     "effect": "Makes the ranking reproducible outside the site build. In review - not implemented."},
])
save("suggestions.json", sugs)

# ---------------------------------------------------------------- meta.json
meta = load("meta.json")
live = meta.setdefault("integration", {}).setdefault("live_reads", {})
live.update({
    "venetian_hotel_terms": "2026-11-19",
    "venetian_contact_address": "2026-11-19",
    "wynn_contact_address": "2026-11-19",
    "wynn_booking_quotes_dec6-13": "2026-11-19",
    "resortsworld_address": "2026-11-19",
    "resortsworld_ibe_calendar": "2026-11-19",
    "caesars_palace_booking_policies": "2026-11-19",
    "horseshoe_booking_policies_and_calendar": "2026-11-19",
    "venetian_booking_attempt": "2026-11-19",
    "google_maps_walking_matrix": "2026-11-19",
})
save("meta.json", meta)

print("data updates applied")
