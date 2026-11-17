#!/usr/bin/env python3
"""Daily official-source scraper for the Poker5 root site.

Why this script exists
----------------------
The agent sandbox that authors this repo cannot open a TCP connection to any
casino/hotel host (TLS is closed by the sandbox network policy). GitHub Actions
runners have normal internet access, so the *reading* of official pages and
PDFs is delegated to this script and the workflow that runs it
(`.github/workflows/daily-scrape.yml`).

What it does, every run
-----------------------
1. Fetches the official Venetian DeepStack Extravaganza IV schedule page and
   parses every row: date, start time, event number, event name, structure-sheet
   link.
2. Downloads every distinct structure sheet PDF referenced by that page and
   extracts, from the PDF text only:
       - event number(s) the sheet covers
       - start time, starting chips, level duration
       - the late-registration line (levels + break + clock time)
       - the guarantee line
       - the house-fee / prize-pool-per-entry line
       - any re-entry / rebuy / add-on / double-entry / paid-stack language
       - the full rule list as a verbatim excerpt
3. Writes:
       data/c6087e2c/schedule_live.json   parsed schedule rows + retrieval time
       data/c6087e2c/structures.json      per-sheet extracted rule fields
       data/c6087e2c/scrape_status.json   per-URL HTTP status, sha256, timestamp
4. Never writes a value it did not read. A field that is absent from the PDF is
   stored as null (or "" for text) and reported as missing in scrape_status.

Nothing here decides whether an event is "good". It only records what the
official document says, with the exact excerpt and the retrieval timestamp.

Usage:
    python3 scripts/scrape_251c122f.py            # live fetch (needs network)
    python3 scripts/scrape_251c122f.py --self-test  # parser self-test, no network
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "c6087e2c")

DSE_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
           "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
UA = ("Mozilla/5.0 (compatible; Poker5-official-source-scraper/1.0; "
      "+https://github.com/karagemop466-tech/Poker5)")
TIMEOUT = 45
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday")

# Pages whose *values* a human must read (dynamic booking UIs, T&C pages). The
# scraper only records the HTTP status, a content hash and any verbatim
# resort-fee lines it can see, so a change can be spotted without the scraper
# ever asserting a value.
WATCH_URLS = {
    "venetian_resort_fee": "https://www.venetianlasvegas.com/resort/resort-fee.html",
    "venetian_suite_rates": "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
    "venetian_hotel_policies": "https://www.venetianlasvegas.com/hotel/hotel-policies.html",
    "wynn_resort_fee_terms": "https://www.wynnlasvegas.com/terms-and-conditions/849338",
    "wynn_poker": "https://www.wynnlasvegas.com/casino/poker",
    "caesars_poker_tournaments": "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
    "bellagio_poker": "https://bellagio.mgmresorts.com/en/casino/poker.html",
    "mgm_grand_poker": "https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
    "aria_poker": "https://aria.mgmresorts.com/en/casino/poker.html",
    "wpt_world_championship": "https://www.worldpokertour.com/event/main-tour-wpt-world-championship-at-wynn-las-vegas-season-2026",
    "clark_county_room_tax": "https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf",
}


# --------------------------------------------------------------------- fetching
def fetch(url: str) -> tuple[bytes | None, dict]:
    """GET a URL with a descriptive UA. Returns (body, status-record)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    rec = {"url": url, "retrieved_at": now_iso(), "status": None, "sha256": "",
           "bytes": 0, "note": ""}
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                body = resp.read()
                rec["status"] = resp.status
                rec["sha256"] = hashlib.sha256(body).hexdigest()
                rec["bytes"] = len(body)
                return body, rec
        except urllib.error.HTTPError as exc:
            rec["status"] = exc.code
            rec["note"] = "HTTP {}".format(exc.code)
            if 400 <= exc.code < 500:
                return None, rec
        except Exception as exc:  # noqa: BLE001 - network errors of many kinds
            rec["status"] = "error"
            rec["note"] = "{}: {}".format(type(exc).__name__, exc)
        time.sleep(2 * attempt)
    return None, rec


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------- html parsing
class TableRows(HTMLParser):
    """Collect the cell text of every <tr> in the document."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[list[dict]] = []
        self._row: list[dict] | None = None
        self._cell: dict | None = None
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = {"text": [], "href": None}
            self._in_cell = True
        elif tag == "a" and self._cell is not None:
            href = attrs.get("href") or ""
            if href and self._cell["href"] is None:
                self._cell["href"] = href
        elif tag == "br" and self._cell is not None:
            self._cell["text"].append(" ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            text = re.sub(r"\s+", " ", "".join(self._cell["text"])).strip()
            self._row.append({"text": text, "href": self._cell["href"]})
            self._cell = None
            self._in_cell = False
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None and self._in_cell:
            self._cell["text"].append(data)


def parse_date(text: str) -> str:
    """'Monday, November 16, 2026' -> '2026-11-16'. Returns '' if not a date."""
    m = re.search(r"([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})", text or "")
    if not m or m.group(1) not in MONTHS:
        return ""
    return "{:04d}-{:02d}-{:02d}".format(int(m.group(3)), MONTHS[m.group(1)],
                                         int(m.group(2)))


def parse_clock(text: str) -> str:
    """'5:10 PM' -> '17:10'. Returns '' when absent."""
    m = re.search(r"(\d{1,2}):(\d{2})\s*([AP])M", text or "", re.I)
    if not m:
        return ""
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ap == "P" and h != 12:
        h += 12
    if ap == "A" and h == 12:
        h = 0
    return "{:02d}:{:02d}".format(h, mi)


def parse_schedule_html(html_text: str) -> list[dict]:
    """Extract every date/time/#/name/sheet row from the official schedule."""
    parser = TableRows()
    parser.feed(html_text)
    rows = []
    for cells in parser.rows:
        texts = [c["text"] for c in cells]
        if len(texts) < 4:
            continue
        date = parse_date(texts[0])
        if not date:
            continue
        time_24 = parse_clock(texts[1])
        ev_raw = texts[2].strip()
        ev = int(ev_raw) if ev_raw.isdigit() else None
        name = texts[3].strip()
        href = ""
        for c in cells[4:]:
            if c["href"] and ".pdf" in c["href"].lower():
                href = c["href"]
                break
        if href.startswith("/"):
            href = "https://www.venetianlasvegas.com" + href
        sheet_no = None
        m = re.search(r"structure_(\d+)\.pdf", href)
        if m:
            sheet_no = int(m.group(1))
        rows.append({
            "date": date,
            "time": time_24,
            "time_label": texts[1].strip(),
            "event_no": ev,
            "name": name,
            "structure_no": sheet_no,
            "structure_url": href,
        })
    return rows


# ---------------------------------------------------------------- pdf parsing
def pdf_text(body: bytes) -> str:
    from pypdf import PdfReader  # imported lazily so --self-test needs no pypdf
    reader = PdfReader(io.BytesIO(body))
    out = []
    for page in reader.pages:
        out.append(page.extract_text() or "")
    return "\n".join(out)


def _clean(text: str) -> str:
    # Real PDF text has no markdown, but strip it anyway so the parser is
    # identical for raw PDF text and for the copied excerpts in the self-test.
    text = text.replace("\u2019", "'").replace("**", "")
    return re.sub(r"[ \t]+", " ", text).strip()


def find_line(text: str, *patterns: str) -> str:
    """Return the first line matching any pattern (case-insensitive)."""
    for line in text.splitlines():
        for pat in patterns:
            if re.search(pat, line, re.I):
                return _clean(line)
    return ""


def parse_structure(text: str) -> dict:
    """Extract the rule fields from one Venetian structure-sheet PDF."""
    flat = _clean(text)
    text = text.replace("**", "")
    lines = [_clean(l) for l in text.splitlines() if _clean(l)]

    title = lines[0] if lines else ""
    subtitle = ""
    for line in lines[:6]:
        if re.search(r"Day\s*A|Day 2|Flight|Turbo", line, re.I) and line != title:
            subtitle = line
            break

    # Event number(s). Observed forms:
    #   "Event Number: 07"  "Event Numbers: 02 and 12"
    #   "Event Numbers: 09, 11, 13, 15, 21, ... and 64"
    ev_line = find_line(text, r"Event Numbers?\s*:", r"^Event Numbers?\b")
    ev_numbers = []
    if ev_line:
        for tok in re.findall(r"\d{1,2}", ev_line):
            n = int(tok)
            if 0 < n <= 99 and n not in ev_numbers:
                ev_numbers.append(n)

    start_line = find_line(text, r"Start Time\s*:")
    chips_line = find_line(text, r"Starting Chips\s*:")
    level_line = find_line(text, r"Level Duration\s*:")
    # The explicit "Late Registration:" line wins; the level-table note
    # "Registration Closes" is only a fallback (it carries no level count).
    late_line = find_line(text, r"Late Registration\s*:") or find_line(
        text, r"Registration Closes")
    gtd_line = find_line(text, r"Guarantee\s*:")
    fee_line = find_line(text, r"of the \$[\d,]+\s*Buy-?In is withheld")
    pool_line = find_line(text, r"prize pool consists of")

    m = re.search(r"Starting Chips\s*:\s*([\d,]+)", chips_line, re.I)
    starting_chips = int(m.group(1).replace(",", "")) if m else None

    m = re.search(r"Level Duration\s*:\s*(\d+)\s*minute", level_line, re.I)
    level_minutes = int(m.group(1)) if m else None

    m = re.search(r"Late Registration\s*:\s*(.+)$", late_line, re.I)
    late_text = m.group(1).strip() if m else ""
    late_clock = parse_clock(late_text) if late_text else ""
    m = re.search(r"(\d+)\s*levels?", late_text, re.I)
    late_levels = int(m.group(1)) if m else None

    m = re.search(r"Guarantee\s*:\s*\$([\d,]+)", gtd_line, re.I)
    guarantee = int(m.group(1).replace(",", "")) if m else None

    m = re.search(r"\$([\d,]+)\s+of the\s+\$([\d,]+)\s+Buy-?In is withheld", fee_line, re.I)
    house_fee = int(m.group(1).replace(",", "")) if m else None
    fee_buyin = int(m.group(2).replace(",", "")) if m else None
    m = re.search(r"prize pool consists of\s+\$([\d,]+)", flat, re.I)
    pool_per_entry = int(m.group(1).replace(",", "")) if m else None

    multi_day = bool(re.search(r"Day\s*A\+|Day\s*2|Day 2 and|2 ?Day", flat, re.I))
    flight_language = bool(re.search(r"starting flight|subsequent flight", flat, re.I))

    rule_hits = []
    for kw, pat in (
        ("re-entry", r"\bre-?\s?entr(y|ies|ing)\b"),
        ("reentry", r"\breentry\b"),
        ("rebuy", r"\bre-?\s?bu(y|ys|ying)\b"),
        ("add-on", r"\badd-?\s?on\b"),
        ("double entry", r"\bdouble (buy|entry|stack)\b"),
        ("paid chips", r"\bpurchas(e|ing) (extra )?(chips|stack)\b"),
        ("alternate stack", r"\balternate (stack|entry)\b"),
    ):
        m = re.search(pat, flat, re.I)
        if m:
            start = max(0, m.start() - 90)
            rule_hits.append({"keyword": kw,
                              "excerpt": flat[start:m.end() + 90].strip()})

    rules = []
    for line in lines:
        if re.match(r"^\d{1,2}\.\s", line) or re.match(r"^[a-d]\.\s", line):
            rules.append(line)
    rules_excerpt = "\n".join(rules)[:2400]

    return {
        "sheet_title": title,
        "sheet_subtitle": subtitle,
        "event_numbers": ev_numbers,
        "start_time": parse_clock(start_line) if start_line else "",
        "start_time_label": start_line,
        "starting_chips": starting_chips,
        "level_minutes": level_minutes,
        "late_registration": late_text,
        "late_registration_clock": late_clock,
        "late_registration_levels": late_levels,
        "chips_line": chips_line,
        "level_line": level_line,
        "guarantee": guarantee,
        "guarantee_line": gtd_line,
        "house_fee": house_fee,
        "fee_buyin": fee_buyin,
        "pool_per_entry": pool_per_entry,
        "fee_line": fee_line,
        "pool_line": pool_line,
        "multi_day_format": multi_day,
        "flight_language": flight_language,
        "restriction_keywords": rule_hits,
        "adds_a_second_entry": bool(rule_hits),
        "rules_excerpt": rules_excerpt,
        "text_length": len(flat),
        "text_sha256": hashlib.sha256(flat.encode("utf-8")).hexdigest(),
    }


# --------------------------------------------------------------------- driver
def main_live() -> int:
    os.makedirs(DATA, exist_ok=True)
    status: dict[str, dict] = {}
    errors: list[str] = []

    body, rec = fetch(DSE_URL)
    status[DSE_URL] = rec
    if body is None:
        print("FATAL: schedule page unreachable:", rec.get("note"))
        with open(os.path.join(DATA, "scrape_status.json"), "w", encoding="utf-8") as fh:
            json.dump({"last_run": now_iso(), "ok": False,
                       "sources": status, "errors": ["schedule page unreachable"]},
                      fh, indent=1)
        return 1

    html_text = body.decode("utf-8", "replace")
    rows = parse_schedule_html(html_text)
    print("schedule rows parsed:", len(rows))
    if len(rows) < 50:
        errors.append("only {} schedule rows parsed (expected ~95); the page "
                      "layout may have changed".format(len(rows)))
    if not rows:
        with open(os.path.join(DATA, "schedule_live.json"), "w", encoding="utf-8") as fh:
            json.dump({"source": DSE_URL, "retrieved_at": rec["retrieved_at"],
                       "rows": [], "note": "no rows parsed"}, fh, indent=1)
        with open(os.path.join(DATA, "scrape_status.json"), "w", encoding="utf-8") as fh:
            json.dump({"last_run": now_iso(), "ok": False, "sources": status,
                       "errors": errors}, fh, indent=1)
        return 1

    sheet_urls: dict[int, str] = {}
    for r in rows:
        if r["structure_no"] and r["structure_url"]:
            sheet_urls.setdefault(r["structure_no"], r["structure_url"])

    structures: dict[str, dict] = {}
    for n in sorted(sheet_urls):
        url = sheet_urls[n]
        body, srec = fetch(url)
        status[url] = srec
        entry: dict = {"sheet_no": n, "url": url,
                       "retrieved_at": srec["retrieved_at"],
                       "http_status": srec["status"],
                       "pdf_sha256": srec["sha256"]}
        if body is None:
            entry["error"] = srec.get("note") or "unreachable"
            structures[str(n)] = entry
            errors.append("sheet {} not read: {}".format(n, entry["error"]))
            continue
        try:
            text = pdf_text(body)
        except Exception as exc:  # noqa: BLE001
            entry["error"] = "pdf parse failed: {}: {}".format(type(exc).__name__, exc)
            structures[str(n)] = entry
            errors.append("sheet {} pdf parse failed".format(n))
            continue
        entry.update(parse_structure(text))
        structures[str(n)] = entry
        print("sheet {:>2}: events={} late={} gtd={} fee_hits={}".format(
            n, entry["event_numbers"], entry["late_registration_clock"] or "-",
            entry["guarantee"], len(entry["restriction_keywords"])))
        time.sleep(0.7)

    # ---- watched hotel / venue pages: hash + verbatim fee lines only
    watch: dict[str, dict] = {}
    for key, url in WATCH_URLS.items():
        body, wrec = fetch(url)
        status[url] = wrec
        entry = {"url": url, "name": key, "http_status": wrec["status"],
                 "sha256": wrec["sha256"], "retrieved_at": wrec["retrieved_at"],
                 "bytes": wrec["bytes"]}
        if body is not None and url.endswith(".pdf"):
            try:
                text = pdf_text(body)
            except Exception:  # noqa: BLE001
                text = ""
        elif body is not None:
            text = body.decode("utf-8", "replace")
        else:
            text = ""
        if text:
            plain = re.sub(r"<[^>]+>", " ", text)
            plain = re.sub(r"\s+", " ", plain.replace("&nbsp;", " "))
            hits = []
            for m in re.finditer(r"[^.]{0,120}?resort fee[^.]{0,140}?\.", plain, re.I):
                line = m.group(0).strip()
                if "$" in line and line not in hits:
                    hits.append(line)
                if len(hits) >= 4:
                    break
            entry["resort_fee_excerpts"] = hits
        watch[key] = entry
        print("watch {:>28}: HTTP {} bytes {}".format(key, wrec["status"], wrec["bytes"]))
        time.sleep(0.4)
    write_json("watch_status.json", {
        "last_run": now_iso(),
        "note": ("HTTP status + content hash + verbatim 'resort fee' sentences for "
                 "each watched official page. No value is parsed or asserted by the "
                 "scraper; the excerpts exist so a human can read the current "
                 "wording and so a hash change can be spotted."),
        "pages": watch,
    })

    write_json("schedule_live.json", {
        "source": DSE_URL,
        "retrieved_at": rec["retrieved_at"],
        "row_count": len(rows),
        "note": ("Parsed from the official schedule page by "
                 "scripts/scrape_251c122f.py. Every field is copied from the "
                 "page; nothing is inferred."),
        "rows": rows,
    })
    write_json("structures.json", {
        "source_note": ("Extracted from the official Venetian structure-sheet "
                        "PDFs linked by the official schedule page. Each sheet "
                        "records the excerpt it was read from. A field that is "
                        "absent from the PDF is null; it is never filled in."),
        "sheets": structures,
    })
    write_json("scrape_status.json", {
        "last_run": now_iso(), "ok": not errors,
        "schedule_rows": len(rows), "sheets_read": len(
            [1 for s in structures.values() if "error" not in s]),
        "sheets_total": len(sheet_urls),
        "errors": errors, "sources": status,
    })
    print("sheets read: {}/{}".format(
        len([1 for s in structures.values() if "error" not in s]), len(sheet_urls)))
    return 0 if not errors else 0  # data is still valid; errors are reported


def write_json(name: str, obj) -> None:
    path = os.path.join(DATA, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote", os.path.relpath(path, ROOT))


# ---------------------------------------------------------------- self test
SAMPLE = """$200 No Limit Hold'em Bounty (1Day)

$200 No Limit Hold'em Bounty (1Day)

Level Time Big Blind Ante Blinds

15 Minute Break / Remove 100 Chips Registration Closes

**Event Numbers:** 09, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, and 64
**Start Time:** 5:10 PM

**Starting Chips:** 25,000

**Level Duration:** 30 minutes.

**Late Registration:** 8 levels + Break (9:40 PM)

**Guarantee:** $8,000 (prize pool + total bounties)

01. TDA rules apply to all Venetian Poker Room tournaments.
06. $40 of the $200 Buy-In is withheld for house fees (Rake +
    Staff). The prize pool consists of $160 of every $200 Buy In.
09. Players receive $50 bounty for each player they eliminate.
"""


def main_self_test() -> int:
    got = parse_structure(SAMPLE)
    expect = {
        "late_registration_clock": "21:40",
        "late_registration_levels": 8,
        "guarantee": 8000,
        "starting_chips": 25000,
        "level_minutes": 30,
        "house_fee": 40,
        "fee_buyin": 200,
        "pool_per_entry": 160,
        "adds_a_second_entry": False,
        "start_time": "17:10",
    }
    bad = []
    for k, v in expect.items():
        if got.get(k) != v:
            bad.append("{}: expected {!r} got {!r}".format(k, v, got.get(k)))
    if got["event_numbers"] != [9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64]:
        bad.append("event_numbers: {}".format(got["event_numbers"]))

    html_sample = """<table><tr><th>Date</th><th>Time</th><th>Event #</th>
    <th>Event Name</th><th>Structures</th></tr>
    <tr><td>Monday, November 16, 2026</td><td>11:10 AM</td><td>1</td>
    <td>$300 No Limit Hold'em 1A $75K GTD</td>
    <td><a href="/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_10.pdf">View</a></td></tr>
    <tr><td>Tuesday, December 1, 2026</td><td>5:10 PM</td><td>23</td>
    <td>$200 No Limit Hold'em Bounty $8K GTD (1Day)</td>
    <td><a href="https://www.venetianlasvegas.com/x/dse_nov_2026-structure_1.pdf">View</a></td></tr>
    </table>"""
    rows = parse_schedule_html(html_sample)
    if len(rows) != 2:
        bad.append("html rows: {}".format(rows))
    elif rows[0] != {"date": "2026-11-16", "time": "11:10", "time_label": "11:10 AM",
                     "event_no": 1,
                     "name": "$300 No Limit Hold'em 1A $75K GTD",
                     "structure_no": 10,
                     "structure_url": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_10.pdf"}:
        bad.append("html row 0: {}".format(rows[0]))
    elif rows[1]["date"] != "2026-12-01" or rows[1]["time"] != "17:10" \
            or rows[1]["structure_no"] != 1:
        bad.append("html row 1: {}".format(rows[1]))

    if bad:
        print("SELF-TEST FAILED")
        for b in bad:
            print(" -", b)
        return 1
    print("self-test OK: structure parser + schedule parser")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    sys.exit(main_self_test() if args.self_test else main_live())
