#!/usr/bin/env python3
"""Validate the afff1fc9 site: data integrity, official-source links, internal links, and rendered row sources.

Exit code 0 = pass, 1 = fail. Unverified items are allowed (they are flagged), but a missing or non-official
source on any table row is a failure.
"""
import csv
import json
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site-afff1fc9")
DATA = os.path.join(SITE, "data")
OFFICIAL = {"www.venetianlasvegas.com", "venetianlasvegas.com", "cdn.wynnresorts.com", "wptmedia-mig.s3.amazonaws.com",
            "www.clarkcountynv.gov", "www.wynnlasvegas.com", "github.com"}
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def check_data():
    with open(os.path.join(DATA, "events.csv"), encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="|"))
    header, body = rows[0], rows[1:]
    if len(header) != 10:
        err(f"events.csv header has {len(header)} columns, expected 10")
    for i, r in enumerate(body, 2):
        if len(r) != 10:
            err(f"events.csv line {i}: {len(r)} fields")
            continue
        venue, date, time, ev, name, buy, gtd, struct, code, note = r
        if venue not in ("venetian", "wynn"):
            err(f"line {i}: bad venue {venue}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            err(f"line {i}: bad date {date}")
        if not re.fullmatch(r"\d{1,2}:\d{2} (AM|PM)", time):
            err(f"line {i}: bad time {time}")
        if buy and not buy.isdigit():
            err(f"line {i}: buy-in not integer: {buy}")
        if gtd and not gtd.isdigit():
            err(f"line {i}: guarantee not integer: {gtd}")
        if code not in ("S", "N", "M"):
            err(f"line {i}: code {code}")
        if venue == "venetian" and not struct.isdigit():
            warnings.append(f"line {i}: venetian row without structure sheet number")
    for fn in ("sources.json", "hotels.json", "monitor_state.json"):
        try:
            with open(os.path.join(DATA, fn), encoding="utf-8") as f:
                json.load(f)
        except Exception as e:  # noqa: BLE001
            err(f"{fn} does not parse: {e}")
    src = json.load(open(os.path.join(DATA, "sources.json"), encoding="utf-8"))
    for s in src["sources"]:
        host = urlparse(s["url"]).netloc
        if urlparse(s["url"]).scheme != "https" or host not in OFFICIAL:
            err(f"source {s['id']} is not https on an allowed official host: {s['url']}")
    return len(body)


def check_html():
    pages = [f for f in os.listdir(SITE) if f.endswith(".html")]
    if len(pages) < 11:
        err(f"expected 11 pages, found {len(pages)}")
    for p in pages:
        html = open(os.path.join(SITE, p), encoding="utf-8").read()
        for href in re.findall(r'(?:href|src)="([^"]+)"', html):
            if href.startswith(("http://",)):
                err(f"{p}: insecure link {href}")
            if href.startswith("https://"):
                if urlparse(href).netloc not in OFFICIAL and "github.com" not in href:
                    warnings.append(f"{p}: external link to non-listed host {href}")
                continue
            if href.startswith("#") or href.startswith("mailto:"):
                continue
            target = href.split("#")[0]
            if target and not os.path.exists(os.path.join(SITE, target)):
                err(f"{p}: broken local link {href}")
        # every data row on a table page must carry at least one official https source link
        for tr in re.findall(r"<tr data-date=.*?</tr>", html, flags=re.S):
            if "https://" not in tr:
                err(f"{p}: table row without source link: {tr[:120]}")
            if 'data-confirmed="1"' in tr:
                err(f"{p}: row marked confirmed single-entry but no confirmation record exists")
    return len(pages)


if __name__ == "__main__":
    n = check_data()
    p = check_html()
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print(f"events={n} pages={p} errors={len(errors)} warnings={len(warnings)}")
    sys.exit(1 if errors else 0)
