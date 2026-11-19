#!/usr/bin/env python3
"""Session 6dba9b3c - give every hotel-to-poker-room pair the two official addresses it is
measured between, plus a Google Maps and an Apple Maps walking deep link built from them.

Why this exists
---------------
The brief asks for "official-address walking times for each hotel-venue pair, with the 30-minute
limit applied" and for "walking-distance verification (Google/Apple Maps) from each hotel to the
Venetian poker room". Before this step the route ledger carried a single link built from the two
*property names* and no address at all, so nobody could tell what was being measured between which
two doors, and only Google was offered.

What this writes (and does not write)
-------------------------------------
Written: origin_address / destination_address with each one's official source URL and read date,
the room's own official location sentence, the two map deep links, and a `basis` note saying which
pair is measured from two street addresses and which is not.

NOT written: walking minutes. No property publishes a walking time to a different property, so
`minutes` stays as it was (blank everywhere except the five same-property pairs, which are 0 by
definition) and the gap stays flagged (F50). No minute figure is estimated from a map distance,
and no pair's `verified` flag is changed here.

Sources are read by the agent's page-fetch tool; the read dates come from that tool's own record:
- Caesars Palace "3570 Las Vegas Blvd South / Las Vegas, NV89109" and Horseshoe Las Vegas
  "3645 Las Vegas Blvd South / Las Vegas, NV89109" are printed in the footer of each property's
  own official casino page (re-read 2026-11-19 in this session:
  https://www.caesars.com/caesars-palace/casino , https://www.caesars.com/horseshoe-las-vegas/casino).
- The Venetian, Wynn and Resorts World addresses were captured by session 96160d8f on 2026-11-19
  and are re-used verbatim from data/ea99006a/hotels.json - not re-typed, so they cannot drift.
- South Point publishes no street address on the pages read, and its own home page says the resort
  is "just a short drive from the iconic Las Vegas Strip", so its pairs are labelled as not
  measured rather than measured as far.

Run:  python3 scripts/complete_routes_6dba9b3c.py            # rewrites data/ea99006a/routes.json
      python3 scripts/complete_routes_6dba9b3c.py --check     # exit 1 if the file would change
Idempotent: the file is derived from data/ea99006a/{hotels,venues,routes}.json only, and the route
rows' own evidence fields are preserved, so a second run writes nothing.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EA = os.path.join(ROOT, "data", "ea99006a")

# The venue's own official location sentence, quoted from the property page recorded in
# data/ea99006a/venues.json. Kept here rather than invented: each entry names the file it came from.
ROOM_LOCATION = {
    "venetian": ("The Venetian's official poker-room page: \"Our Poker Room is located at The Palazzo "
                 "on level 2 of Grand Canal Shoppes.\"",
                 "https://www.venetianlasvegas.com/resort/casino/poker.html", "2026-11-19"),
    "wynn": ("Official WPT terms: registration is in the \"Wynn Las Vegas Poker Room, located in "
             "Encore at Wynn Las Vegas\" - the room is in the Encore tower.",
             "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/"
             "WPT_World_Championship_Structures.pdf", "2026-11-19"),
    "caesars": ("Official Caesars Palace casino page: \"The Poker Room at Caesars Palace is open 24/7 "
                "with both live-action cash games and daily tournaments.\"",
                "https://www.caesars.com/caesars-palace/casino", "2026-11-19"),
    "horseshoe": ("Official Horseshoe Las Vegas casino page lists the Hall of Fame Poker Room; the "
                  "property publishes no floor location for it.",
                  "https://www.caesars.com/horseshoe-las-vegas/casino", "2026-11-19"),
    "resortsworld": ("Official Resorts World poker-room page; the property publishes no floor location "
                     "for the room.", "https://www.rwlasvegas.com/gaming/poker-room/", "2026-11-19"),
    "southpoint": ("Official South Point poker-room page; the home page places the resort \"just a "
                   "short drive from the iconic Las Vegas Strip\" and no street address is published "
                   "on the pages read.", "https://southpointcasino.com/casino/poker-room", "2026-11-19"),
}


def load(name: str):
    with open(os.path.join(EA, name)) as fh:
        return json.load(fh)


def dump(name: str, data) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


def quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def maps_links(origin: str, destination: str, origin_name: str, dest_name: str):
    """Deep links built from the official street addresses where both exist, otherwise names.

    The `basis` of each link is stated in the row so a reader can see what the pin was dropped on.
    """
    o = origin or origin_name
    d = destination or dest_name
    google = ("https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=walking"
              % (quote(o), quote(d)))
    apple = "https://maps.apple.com/dir?dirflg=w&saddr=%s&daddr=%s" % (quote(o), quote(d))
    return google, apple


def build(routes, hotels_by_key, venues_by_key):
    out = []
    for row in routes:
        r = dict(row)
        hotel = hotels_by_key.get(r.get("hotel_key"), {})
        venue = venues_by_key.get(r.get("venue_key"), {})
        dest_hotel = hotels_by_key.get(r.get("venue_key"), {})
        r["origin_address"] = hotel.get("address") or ""
        r["origin_address_source"] = hotel.get("address_source") or ""
        # Only a date the address itself was read. No fallback to another field's read date:
        # an address the pipeline has not been re-read for is shown as undated, not as fresh.
        r["origin_address_read"] = hotel.get("address_read") or ""
        r["destination_address"] = dest_hotel.get("address") or ""
        r["destination_address_source"] = dest_hotel.get("address_source") or ""
        r["destination_address_read"] = dest_hotel.get("address_read") or ""
        note, src, read = ROOM_LOCATION.get(r.get("venue_key"), ("", "", ""))
        r["room_location"] = note
        r["room_location_source"] = src
        r["room_location_read"] = read
        r["venue_page"] = venue.get("source") or ""
        both = bool(r["origin_address"]) and bool(r["destination_address"])
        g, a = maps_links(r["origin_address"], r["destination_address"], r["hotel"], r["venue"])
        r["maps"] = g
        r["maps_apple"] = a
        if r.get("same_property"):
            r["basis"] = ("same property: the poker room is inside the hotel, so no street-to-street "
                          "measurement is needed (0 minutes)")
        elif both:
            if r.get("minutes") not in (None, ""):
                r["basis"] = ("the walking time on this row is a dated Google Maps walking-directions "
                              "observation between the official property names (see the method sentence); "
                              "the two official street addresses below pin the same two properties")
            else:
                r["basis"] = ("no walking time recorded; the map links below run between the two official "
                              "street addresses below, and no official source publishes a walking time "
                              "between them")
        else:
            missing = [n for n, ok in ((r["hotel"], bool(r["origin_address"])),
                                       (r["venue"], bool(r["destination_address"]))) if not ok]
            r["basis"] = ("not measured: %s publish%s no street address in this repository, so the map links "
                          "are pinned on the property names"
                          % (" and ".join(missing) or "neither endpoint",
                             "" if len(missing) == 1 else "es"))
        r["addresses_read"] = max(filter(None, [r["origin_address_read"], r["destination_address_read"],
                                                read])) if (both or r.get("same_property")) else ""
        out.append(r)
    return out


NO_TIME_METHOD = ("No official source states a walking time between these properties. Left blank on "
                  "purpose - open the route link and check it yourself.")


def universe(routes, hotels, venues):
    """Every hotel-to-room pair, not only the ones a previous run happened to write.

    The brief asks for a walking-route check per hotel-room pair, so the ledger is derived from the
    two registers (hotels x venues) instead of being an annotation of whatever rows already exist.
    A pair already in routes.json keeps its curated values (its measured minutes, its `verified`
    flag, its `method` sentence); a pair that is new gets blanks and the "no official source states a
    walking time" method, never an estimate.
    """
    have = {(r.get("hotel_key"), r.get("venue_key")): r for r in routes}
    pairs = []
    for h in hotels:
        for v in venues:
            prev = have.get((h.get("key"), v.get("key")))
            if prev:
                pairs.append(prev)
            else:
                pairs.append({"hotel": h.get("name"), "hotel_key": h.get("key"),
                              "venue": v.get("name"), "venue_key": v.get("key"),
                              "same_property": None, "minutes": None, "verified": False,
                              "method": NO_TIME_METHOD})
    return pairs


def main() -> int:
    check = "--check" in sys.argv
    routes = load("routes.json")
    hotels = load("hotels.json")
    venues = load("venues.json")
    hotels_by_key = {h.get("key"): h for h in hotels}
    venues_by_key = {v.get("key"): v for v in venues}
    out = build(universe(routes, hotels, venues), hotels_by_key, venues_by_key)
    text = dump("routes.json", out)
    path = os.path.join(EA, "routes.json")
    if check:
        if open(path).read() != text:
            print("routes.json is not what scripts/complete_routes_6dba9b3c.py generates")
            return 1
        print("routes.json matches this generator (%d pairs)" % len(out))
        return 0
    before = json.load(open(path))
    with open(path, "w") as fh:
        fh.write(text)
    measured = sum(1 for r in out if r.get("minutes") not in (None, ""))
    with_addr = sum(1 for r in out if r.get("origin_address") and r.get("destination_address"))
    print("%d pairs rewritten (%d identical rows before: %d); %d carry a walking time, "
          "%d are pinned to two official street addresses"
          % (len(out), len(before), sum(1 for a, b in zip(before, out) if a == b), measured, with_addr))
    return 0


if __name__ == "__main__":
    sys.exit(main())
