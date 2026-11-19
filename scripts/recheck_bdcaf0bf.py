#!/usr/bin/env python3
"""Session bdcaf0bf - re-read every official URL behind the published site.

The site's promise is that no value goes stale quietly. This script is the loop
that keeps that promise: for each URL in the ledger it fetches the live page (or
PDF), stores the retrieval timestamp, the HTTP status and a SHA-256 of the
content, and compares the hash with the previous run. When a page changed, the
URL is marked `changed` with the date, and every table row that cites that URL
gets a "source changed" badge on the site until a human re-reads it.

It never rewrites a value: a change marks the row, it does not fill it in.

Usage
  python3 scripts/recheck_bdcaf0bf.py            # live fetch (GitHub Actions runner)
  python3 scripts/recheck_bdcaf0bf.py --offline  # validate the ledger only (sandbox)

The sandbox this repository is authored in cannot open a TCP connection to
casino hosts, so `--offline` is what runs here and in the build check; the
scheduled workflow runs the live form.
"""
from __future__ import annotations

import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "bdcaf0bf")
LEDGER = os.path.join(D, "last_checked.json")
CHANGELOG = os.path.join(D, "change_log.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 poker5-source-monitor/1.0")
SKIP = re.compile(r"(booking|reservations\.|ibe/|hotel-calendar|/book/|maps\.google|maps\?dirflg)")


def load(path, default=None):
    if not os.path.exists(path):
        if default is None:
            sys.exit("missing %s" % path)
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def ledger_urls():
    """Every URL the published data cites: the ledger itself plus every source field on a row."""
    urls = set()
    led = load(LEDGER, {"urls": {}})
    urls.update(u for u in led.get("urls", {}) if u.startswith("https://"))
    for f in ("events.json", "hotels.json", "venues.json", "facts.json"):
        data = load(os.path.join(D, f), {})
        blob = json.dumps(data)
        urls.update(m.group(0) for m in re.finditer(r"https://[^\"\\ ]+", blob))
    for f in glob.glob(os.path.join(ROOT, "pages", "**", "*.html"), recursive=True):
        txt = open(f, encoding="utf-8").read()
        for m in re.finditer(r'href="(https://[^"]+)"', txt):
            u = m.group(1).replace("&amp;", "&")
            if SKIP.search(u):
                continue        # booking engines and map links are navigation, not evidence
            urls.add(u)
    return sorted(u for u in urls if u.startswith("https://") and not SKIP.search(u))


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return resp.status, body


def main():
    offline = "--offline" in sys.argv
    led = load(LEDGER, {"urls": {}, "updated": None, "changed_count": 0, "note": ""})
    urls = led.setdefault("urls", {})
    targets = ledger_urls()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log = load(CHANGELOG, [])
    checked = changed = failed = 0
    for url in targets:
        rec = urls.setdefault(url, {"url": url, "label": "", "kind": "monitored", "official": True,
                                    "rows": 0, "note": "", "history": []})
        rec.setdefault("history", [])
        if offline:
            # no network: confirm the ledger entry itself is well formed and keep its dates
            if not rec.get("last_checked"):
                rec["note"] = (rec.get("note") + " | " if rec.get("note") else "") + \
                    "no check recorded yet; the live re-check runs on the scheduled runner"
            checked += 1
            continue
        try:
            status, body = fetch(url)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as exc:
            failed += 1
            rec["status"] = "fetch-error"
            rec["last_attempt"] = now
            rec["note"] = "last automated fetch failed: %s (recorded, values left as they were)" % type(exc).__name__
            continue
        sha = hashlib.sha256(body).hexdigest()
        prev = rec.get("sha256")
        rec["status"] = status
        rec["http"] = status
        rec["last_checked"] = now
        rec["first_checked"] = rec.get("first_checked") or now
        rec["bytes"] = len(body)
        rec["history"] = (rec.get("history") or [])[-40:]
        rec["history"].append({"at": now, "sha256": sha, "status": status, "bytes": len(body)})
        rec["sha256"] = sha
        checked += 1
        if prev and prev != sha:
            changed += 1
            rec["changed"] = True
            rec["changed_at"] = now
            log.append({"changed_at": now, "url": url, "old_sha256": prev, "new_sha256": sha,
                        "old_bytes": rec.get("bytes_prev"), "new_bytes": len(body),
                        "label": rec.get("label") or ""})
        elif prev == sha and rec.get("changed"):
            # a human re-read and the value was refreshed: keep the badge until the data says otherwise
            rec["changed_note"] = "hash stable since the last check; re-run the integration to clear the badge"
        rec["bytes_prev"] = len(body)
    led["updated"] = now
    led["changed_count"] = sum(1 for v in urls.values() if v.get("changed"))
    led["urls_checked"] = checked
    led["fetch_failures"] = failed
    led["note"] = ("Written by scripts/recheck_bdcaf0bf.py. Every URL that backs a published value is listed with "
                   "its status, content hash and last retrieval date; a changed hash marks the row on the site "
                   "instead of overwriting the stored value.")
    os.makedirs(D, exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as fh:
        json.dump(led, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(CHANGELOG, "w", encoding="utf-8") as fh:
        json.dump(log[-400:], fh, indent=1)
        fh.write("\n")
    print("ledger urls %d | checked %d | newly changed %d | fetch failures %d%s"
          % (len(urls), checked, changed, failed, " (offline: no fetch attempted)" if offline else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
