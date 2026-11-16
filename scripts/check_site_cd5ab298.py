#!/usr/bin/env python3
"""Dependency-free checks for the static poker research dashboard."""
from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "dashboard-cd5ab298"
ERRORS: list[str] = []


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.title_seen = False
        self.h1_count = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if attrs_map.get("id"):
            self.ids.add(attrs_map["id"] or "")
        if tag == "a" and attrs_map.get("href"):
            self.hrefs.append(attrs_map["href"] or "")
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title and data.strip():
            self.title_seen = True


def fail(message: str) -> None:
    ERRORS.append(message)


def check_html_links() -> int:
    pages = sorted(SITE_ROOT.glob("*.html"))
    if not pages:
        fail("no root-level HTML pages found")
        return 0
    parsed: dict[Path, PageParser] = {}
    for page in pages:
        parser = PageParser()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fail(f"{page.relative_to(SITE_ROOT)}: could not parse HTML: {exc}")
            continue
        parsed[page] = parser
        if not parser.title_seen:
            fail(f"{page.relative_to(SITE_ROOT)}: missing <title>")
        if parser.h1_count != 1:
            fail(f"{page.relative_to(SITE_ROOT)}: expected exactly one <h1>, found {parser.h1_count}")

    for page, parser in parsed.items():
        for href in parser.hrefs:
            parts = urlsplit(href)
            if parts.scheme in {"https", "http", "mailto", "tel"}:
                if parts.scheme == "http":
                    fail(f"{page.relative_to(SITE_ROOT)}: use https for external link {href}")
                continue
            if parts.scheme or parts.netloc:
                fail(f"{page.relative_to(SITE_ROOT)}: unsupported link scheme in {href}")
                continue
            local_path = unquote(parts.path)
            target = (page.parent / local_path).resolve() if local_path else page.resolve()
            if not target.exists():
                fail(f"{page.relative_to(SITE_ROOT)}: broken local link {href}")
                continue
            if parts.fragment and target.suffix == ".html" and target in parsed:
                if parts.fragment not in parsed[target].ids:
                    fail(f"{page.relative_to(SITE_ROOT)}: missing anchor #{parts.fragment} in {target.relative_to(SITE_ROOT)}")
    return len(pages)


def check_data() -> int:
    path = SITE_ROOT / "data" / "tournaments.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"data/tournaments.json: invalid JSON: {exc}")
        return 0
    sources = data.get("sources", {})
    events = data.get("events", [])
    window = data.get("window", {})
    start, end = window.get("start"), window.get("end")
    seen: set[tuple[str, str, str, str]] = set()
    statuses = {"unverified", "multi-flight", "re-entry", "continuation", "satellite", "review"}
    for index, event in enumerate(events, start=1):
        prefix = f"event {index} ({event.get('name', 'unnamed')})"
        date, time = event.get("date", ""), event.get("time", "")
        if not (start <= date <= end):
            fail(f"{prefix}: date {date!r} is outside the published window")
        if len(time) != 5 or time[2] != ":" or not time[:2].isdigit() or not time[3:].isdigit():
            fail(f"{prefix}: invalid 24-hour start time {time!r}")
        if time.startswith("08:"):
            fail(f"{prefix}: 8:00 a.m. starts were not expected in the selected schedule")
        if event.get("status") not in statuses:
            fail(f"{prefix}: unknown status {event.get('status')!r}")
        for key in ("schedule", "rules"):
            source_key = event.get(key)
            if source_key not in sources:
                fail(f"{prefix}: missing {key} source {source_key!r}")
        signature = (date, time, event.get("venue", ""), event.get("name", ""))
        if signature in seen:
            fail(f"{prefix}: duplicate date/time/venue/name row")
        seen.add(signature)
    for key, source in sources.items():
        parts = urlsplit(source.get("url", ""))
        if parts.scheme != "https" or not parts.netloc:
            fail(f"source {key}: expected an absolute https URL")
    if not events:
        fail("tournament dataset is empty")
    print(f"Data: {len(events)} schedule rows, {len(sources)} source URLs, snapshot {data.get('snapshot')}")
    return len(events)


def check_hotel_data() -> int:
    path = SITE_ROOT / "data" / "hotels.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"data/hotels.json: invalid JSON: {exc}")
        return 0
    sources = data.get("sources", {})
    stay = data.get("stay", {})
    properties = {item.get("name"): item for item in data.get("properties", [])}
    if stay.get("nights") != 7 or stay.get("adults") != 2:
        fail("hotel data: expected a seven-night stay for two adults")
    for key, source in sources.items():
        parts = urlsplit(source.get("url", ""))
        if parts.scheme != "https" or not parts.netloc:
            fail(f"hotel source {key}: expected an absolute https URL")
    wynn = properties.get("Wynn Las Vegas", {})
    if round(wynn.get("displayedAverageNightly", 0) * stay.get("nights", 0), 2) != wynn.get("displayedSubtotalEstimate"):
        fail("hotel data: Wynn displayed-average subtotal does not match its seven-night estimate")
    if round(wynn.get("displayedSubtotalEstimate", 0) * (1 + wynn.get("lodgingTaxRate", 0)), 2) != wynn.get("totalEstimate"):
        fail("hotel data: Wynn estimated total does not reconcile with the published tax calculation")
    venetian = properties.get("The Venetian Resort", {})
    venetian_sum = round(venetian.get("roomRatesBeforeTax", 0) + venetian.get("resortFeesBeforeTax", 0) + venetian.get("taxes", 0), 2)
    if venetian_sum != venetian.get("displayedTotal"):
        fail("hotel data: Venetian displayed total does not reconcile with its components")
    if not data.get("routes") or not data.get("importantCaveat"):
        fail("hotel data: missing walking route estimates or their caveat")
    print(f"Hotels: {len(data.get('properties', []))} property records, {len(sources)} source URLs, {len(data.get('routes', []))} route estimates")
    return len(data.get("properties", []))


def main() -> int:
    pages = check_html_links()
    rows = check_data()
    hotel_records = check_hotel_data()
    for asset in (SITE_ROOT / "assets" / "styles.css", SITE_ROOT / "assets" / "app.js", SITE_ROOT / "assets" / "mark.svg"):
        if not asset.is_file():
            fail(f"missing required asset {asset.relative_to(SITE_ROOT)}")
    if not (SITE_ROOT / "flagged-for-review.html").is_file():
        fail("missing required Flagged for Review page")
    if ERRORS:
        print("Site checks FAILED:")
        for error in ERRORS:
            print(f" - {error}")
        return 1
    print(f"Site checks passed: {pages} HTML pages, {rows} dated tournament rows, {hotel_records} hotel records, local links and required assets OK.")
    print("External links are validated for HTTPS syntax; availability is not probed by this local checker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
