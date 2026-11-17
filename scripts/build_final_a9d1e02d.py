#!/usr/bin/env python3
"""Validate the final-source dataset and generate the isolated Pages planner."""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "planner-a9d1e02d"
DATA = ROOT / "data" / "final"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - keep validation diagnostics useful
        raise ValueError(f"cannot parse {path.relative_to(ROOT)}: {exc}") from exc


def shell(title: str, page: str, *, root: str = ".", venue: str = "") -> str:
    venue_attr = f' data-venue="{html.escape(venue, quote=True)}"' if venue else ""
    asset_root = html.escape(root, quote=True)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#173c30">
  <meta name="description" content="Official-source Las Vegas poker tournament planner, hotel snapshot and trip-cost calculator with explicit unknowns.">
  <title>{html.escape(title)} · Poker5 final source planner</title>
  <link rel="stylesheet" href="{asset_root}/assets/site.css">
  <script defer src="{asset_root}/assets/app.js"></script>
</head>
<body data-page="{html.escape(page, quote=True)}" data-root="{asset_root}"{venue_attr}>
  <div id="site-header"></div>
  <main id="main"><div id="page-content" aria-live="polite"></div></main>
  <div id="site-footer"></div>
</body>
</html>
'''


class HTMLReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.references.append(value)


def validate_built_site(venue_ids: list[str]) -> None:
    expected = {"index.html", "tournaments.html", "hotels.html", "venues.html", "sources.html", "method.html"}
    missing = sorted(name for name in expected if not (OUT / name).is_file())
    missing += [f"venues/{venue_id}.html" for venue_id in venue_ids if not (OUT / "venues" / f"{venue_id}.html").is_file()]
    if missing:
        raise SystemExit(f"generated planner pages are missing: {', '.join(missing)}")
    for page in OUT.rglob("*.html"):
        parser = HTMLReferences()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.references:
            if reference.startswith(("https://", "http://", "mailto:", "tel:", "#", "data:")):
                continue
            target = (page.parent / reference.split("?", 1)[0].split("#", 1)[0]).resolve()
            if not target.exists():
                raise SystemExit(f"{page.relative_to(ROOT)}: broken local href/src: {reference}")
    for local_name, canonical in (
        ("tournaments.json", DATA / "events.json"),
        ("hotels.json", DATA / "hotels.json"),
        ("venues.json", DATA / "venues.json"),
        ("source-ledger.json", DATA / "source-ledger.json"),
    ):
        if (OUT / "data" / local_name).read_bytes() != canonical.read_bytes():
            raise SystemExit(f"planner data snapshot differs from canonical source: {local_name}")


def read_schedule() -> list[dict[str, str]]:
    psv = ROOT / "data" / "c6087e2c" / "venetian_dse_2026.psv"
    fields = ["date", "time", "event_no", "name", "buy_in", "guarantee", "sheet", "kind", "notes"]
    rows: list[dict[str, str]] = []
    with psv.open(encoding="utf-8", newline="") as f:
        for row in csv.reader((line for line in f if line.strip() and not line.lstrip().startswith("#")), delimiter="|"):
            if len(row) != len(fields):
                raise ValueError(f"Venetian schedule row has {len(row)} fields, expected {len(fields)}: {row!r}")
            rows.append(dict(zip(fields, row, strict=True)))
    return rows


def validate(events_doc: dict[str, Any], hotels_doc: dict[str, Any], venues_doc: dict[str, Any], ledger_doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = ledger_doc.get("sources", [])
    source_by_id = {s.get("id"): s for s in sources}
    if len(source_by_id) != len(sources):
        errors.append("source ledger contains duplicate IDs")
    for source in sources:
        sid = source.get("id", "<missing id>")
        if not isinstance(source.get("url"), str) or not source["url"].startswith("https://"):
            errors.append(f"{sid}: source URL is not HTTPS")
        if not source.get("title") or not source.get("publisher") or not source.get("checkedAt"):
            errors.append(f"{sid}: title, publisher and checkedAt are required")
        monitor = source.get("monitor")
        if monitor:
            if monitor.get("mode") not in {"availability", "markers", "pdf-markers"}:
                errors.append(f"{sid}: unsupported monitor mode {monitor.get('mode')!r}")
            if monitor.get("mode") in {"markers", "pdf-markers"} and not monitor.get("markers"):
                errors.append(f"{sid}: marker monitor has no expected markers")

    sources_ven = {f"venetian-structure-{n:02d}" for n in range(1, 38)}
    missing_pdf = sorted(sources_ven - source_by_id.keys())
    if missing_pdf:
        errors.append(f"source ledger is missing Venetian structure PDFs: {', '.join(missing_pdf)}")
    sheet_prices = [200, 400, 400, 600, 300, 400, 600, 200, 300, 300, 600, 800, 800, 800, 300, 800, 600, 200, 100, 1100, 2200, 300, 600, 260, 260, 400, 600, 600, 200, 200, 600, 800, 600, 1100, 1100, 1100, 2200]
    for sheet_no, price in enumerate(sheet_prices, 1):
        source = source_by_id.get(f"venetian-structure-{sheet_no:02d}", {})
        monitor = source.get("monitor", {})
        if monitor.get("mode") != "pdf-markers" or f"${price:,}" not in monitor.get("markers", []):
            errors.append(f"Venetian structure PDF {sheet_no}: monitor must check the audited buy-in marker ${price:,}")
    notes_path = DATA / "structure-notes.md"
    note_rows = re.findall(r"^\|\s*(\d{1,2})\s*\|", notes_path.read_text(encoding="utf-8"), re.M)
    if sorted(map(int, note_rows)) != list(range(1, 38)):
        errors.append("structure-notes.md must contain one row for each Venetian PDF 1–37")

    rows = read_schedule()
    start, end = events_doc.get("meta", {}).get("window", {}).get("start"), events_doc.get("meta", {}).get("window", {}).get("end")
    ven_expected = [r for r in rows if r["kind"] == "entry" and start <= r["date"] <= end]
    ven_events = [e for e in events_doc.get("events", []) if e.get("venueId") == "venetian" and e.get("recordType") == "entry"]
    ven_keys: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in ven_expected:
        flight = re.search(r"\b1([A-F])\b", row["name"])
        key = (row["date"], row["event_no"], flight.group(1) if flight else "")
        if key in ven_keys:
            errors.append(f"duplicate official Venetian schedule key: {key}")
        ven_keys[key] = row
    matched: set[tuple[str, str, str]] = set()
    for event in ven_events:
        event_id = event.get("id", "<missing id>")
        number_match = re.search(r"#(\d+)", event.get("eventNumber", ""))
        flight_match = re.search(r"Flight 1([A-F])", event.get("eventNumber", ""))
        if not number_match:
            errors.append(f"{event_id}: missing Venetian event number")
            continue
        key = (event.get("date", ""), number_match.group(1), flight_match.group(1) if flight_match else "")
        row = ven_keys.get(key)
        if not row:
            errors.append(f"{event_id}: no matching official schedule row for {key}")
            continue
        if key in matched:
            errors.append(f"{event_id}: duplicate planner row for {key}")
        matched.add(key)
        expected = {
            "time": row["time"],
            "buyInUsd": int(row["buy_in"]),
            "guaranteeUsd": int(row["guarantee"]) if row["guarantee"] else None,
            "structureSheet": int(row["sheet"]),
        }
        for field, value in expected.items():
            if event.get(field) != value:
                errors.append(f"{event_id}: {field}={event.get(field)!r}, schedule says {value!r}")
        if "venetian-schedule" not in event.get("sourceIds", []):
            errors.append(f"{event_id}: missing official schedule citation")
        sheet_source = f"venetian-structure-{int(row['sheet']):02d}"
        if sheet_source not in event.get("sourceIds", []):
            errors.append(f"{event_id}: missing structure-sheet citation {sheet_source}")
        if event.get("entryStatus") == "single-entry":
            errors.append(f"{event_id}: unsupported strict single-entry classification")
        for rule in ("totalEntryCap", "reEntry", "rebuy", "addOn", "lateRegistration"):
            if not isinstance(event.get(rule), dict) or "status" not in event[rule]:
                errors.append(f"{event_id}: missing separate rule field {rule}")
        # Venetian entry-rule omissions are deliberately represented as unknown.
        for rule in ("totalEntryCap", "reEntry", "rebuy", "addOn"):
            fact = event.get(rule, {})
            if fact.get("status") != "unknown":
                errors.append(f"{event_id}: Venetian {rule} must remain unknown unless explicit source text supports it")
    missing_rows = sorted(set(ven_keys) - matched)
    if missing_rows:
        errors.append(f"Venetian official entry rows not represented: {missing_rows}")
    if len(ven_expected) != 17:
        errors.append(f"expected 17 Venetian entry rows in the window; found {len(ven_expected)}")

    valid_statuses = {"unconfirmed", "multiple-entry", "conflicting", "continuation", "single-entry"}
    event_ids: set[str] = set()
    for event in events_doc.get("events", []):
        eid = event.get("id", "<missing id>")
        if eid in event_ids:
            errors.append(f"duplicate event ID: {eid}")
        event_ids.add(eid)
        if event.get("entryStatus") not in valid_statuses:
            errors.append(f"{eid}: unsupported entryStatus {event.get('entryStatus')!r}")
        if not event.get("sourceIds"):
            errors.append(f"{eid}: no official source IDs")
        for sid in event.get("sourceIds", []):
            if sid not in source_by_id:
                errors.append(f"{eid}: source ID does not exist: {sid}")
        for field in ("totalEntryCap", "reEntry", "rebuy", "addOn", "lateRegistration"):
            if not isinstance(event.get(field), dict) or "status" not in event[field]:
                errors.append(f"{eid}: missing independent {field} fact")
        if event.get("entryStatus") == "single-entry":
            errors.append(f"{eid}: strict single-entry is not supported by reviewed source set")
        if event.get("buyInUsd") is not None and event["buyInUsd"] < 0:
            errors.append(f"{eid}: negative buy-in")
        if event.get("guaranteeUsd") is not None and event["guaranteeUsd"] < 0:
            errors.append(f"{eid}: negative guarantee")

    hotel_window = hotels_doc.get("meta", {}).get("window", {})
    if hotel_window.get("checkIn") != "2026-12-13" or hotel_window.get("checkOut") != "2026-12-20":
        errors.append("hotel comparison must stay on the distinct Dec 13–20 snapshot")
    if hotel_window.get("isUserSelected") is not False:
        errors.append("hotel snapshot must be marked as working dates, not user-selected")
    hotel_ids = {p.get("id") for p in hotels_doc.get("properties", [])}
    property_rows = hotels_doc.get("properties", [])
    if len(hotel_ids) != len(property_rows):
        errors.append("hotel properties contain duplicate IDs")
    for prop in property_rows:
        if prop.get("id") not in hotel_ids:
            errors.append(f"duplicate hotel ID: {prop.get('id')}")
        booking_id = prop.get("bookingSourceId")
        if booking_id and booking_id not in source_by_id:
            errors.append(f"hotel {prop.get('id')}: booking source is missing: {booking_id}")
        address_id = prop.get("addressSourceId")
        if address_id and address_id not in source_by_id:
            errors.append(f"hotel {prop.get('id')}: address source is missing: {address_id}")
        if prop.get("addressStatus") == "official-property-page" and (not prop.get("address") or not address_id):
            errors.append(f"hotel {prop.get('id')}: verified address requires a value and official citation")
        if not prop.get("address") and prop.get("addressStatus") == "official-property-page":
            errors.append(f"hotel {prop.get('id')}: verified address unexpectedly blank")
        fee = prop.get("fee", {})
        for sid in fee.get("sourceIds", []):
            if sid not in source_by_id:
                errors.append(f"hotel {prop.get('id')}: resort-fee source is missing: {sid}")
    for quote in hotels_doc.get("quotes", []):
        if quote.get("propertyId") not in hotel_ids:
            errors.append(f"hotel quote {quote.get('id')}: unknown property ID")
        for sid in quote.get("sourceIds", []):
            if sid not in source_by_id:
                errors.append(f"hotel quote {quote.get('id')}: source is missing: {sid}")
    for item in hotels_doc.get("parking", []):
        for sid in item.get("sourceIds", []):
            if sid not in source_by_id:
                errors.append(f"parking record {item.get('propertyId')}: source is missing: {sid}")

    venue_ids = {v.get("id") for v in venues_doc.get("venues", [])}
    for venue in venues_doc.get("venues", []):
        if venue.get("hotelId") and venue["hotelId"] not in hotel_ids:
            errors.append(f"venue {venue.get('id')}: hotelId does not exist: {venue['hotelId']}")
        if venue.get("bookingSourceId") not in source_by_id:
            errors.append(f"venue {venue.get('id')}: bookingSourceId does not exist")
        for sid in venue.get("sourceIds", []):
            if sid not in source_by_id:
                errors.append(f"venue {venue.get('id')}: source is missing: {sid}")
    for event in events_doc.get("events", []):
        if event.get("venueId") not in venue_ids:
            errors.append(f"{event.get('id')}: venue does not exist: {event.get('venueId')}")

    return errors


def build() -> None:
    events = load_json(DATA / "events.json")
    hotels = load_json(DATA / "hotels.json")
    venues = load_json(DATA / "venues.json")
    ledger = load_json(DATA / "source-ledger.json")
    errors = validate(events, hotels, venues, ledger)
    if errors:
        print("Data validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "venues").mkdir(exist_ok=True)
    # Planner-local snapshots are generated from the canonical data/final sources.
    for source_path, target_name in (
        (DATA / "events.json", "tournaments.json"),
        (DATA / "hotels.json", "hotels.json"),
        (DATA / "venues.json", "venues.json"),
        (DATA / "source-ledger.json", "source-ledger.json"),
    ):
        (OUT / "data" / target_name).write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")

    pages = {
        "index.html": ("Poker5 final source planner", "home", ".", ""),
        "tournaments.html": ("Tournament schedule", "tournaments", ".", ""),
        "hotels.html": ("Hotels and trip budget", "hotels", ".", ""),
        "venues.html": ("Venue directory", "venues", ".", ""),
        "sources.html": ("Official source ledger", "sources", ".", ""),
        "method.html": ("Method and limitations", "method", ".", ""),
    }
    for name, (title, page, root, venue) in pages.items():
        (OUT / name).write_text(shell(title, page, root=root, venue=venue), encoding="utf-8")
    for venue in venues["venues"]:
        (OUT / "venues" / f"{venue['id']}.html").write_text(
            shell(f"{venue['property']} venue guide", "venue", root="..", venue=venue["id"]), encoding="utf-8"
        )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    validate_built_site([v["id"] for v in venues["venues"]])
    print(
        f"Built {OUT.relative_to(ROOT)}: {len(venues['venues'])} venue pages, "
        f"{len(events['events'])} planner rows, {len(ledger['sources'])} source records."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="validate data without writing planner files")
    args = parser.parse_args()
    if args.check_only:
        errors = validate(
            load_json(DATA / "events.json"), load_json(DATA / "hotels.json"),
            load_json(DATA / "venues.json"), load_json(DATA / "source-ledger.json")
        )
        if errors:
            print("Data validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            raise SystemExit(1)
        print("Data validation passed.")
    else:
        build()


if __name__ == "__main__":
    main()
