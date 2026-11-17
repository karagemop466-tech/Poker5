#!/usr/bin/env python3
"""Session ea99006a - official source monitor.

Re-fetches every official URL that backs a table row, hashes it, and records
whether it changed since the last run.

    python3 scripts/recheck_ea99006a.py --offline   # validate the ledger, no network
    python3 scripts/recheck_ea99006a.py             # fetch every source (needs network)

Outputs, both committed:
    data/ea99006a/last_checked.json   url -> {sha256, bytes, checked_at, status}
    data/ea99006a/change_log.json     append-only list of change events

Exit status is 0 even when sources change: a changed source is information, not
a build failure. It exits 1 only when the ledger or the data files are broken.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "ea99006a")
LEDGER = os.path.join(DATA, "last_checked.json")
CHANGELOG = os.path.join(DATA, "change_log.json")
UA = "Poker5-source-monitor/1.0 (GitHub Actions; contact via repository issues)"
TIMEOUT = 45
SLEEP = 1.0


def load(name, default):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    with open(p) as fh:
        return json.load(fh)


def collect_urls():
    """Every official URL that backs a row, plus the hotel / tax / venue pages."""
    urls = {}

    def add(u, label):
        if u and u.startswith("https://"):
            urls.setdefault(u, label)

    for name in ("venetian.json", "wpt.json", "other.json"):
        for r in load(name, []):
            add(r.get("source"), r.get("source_label") or "event source")
            add(r.get("schedule_source"), "schedule source")
    meta = load("meta.json", {})
    add(meta.get("schedule_page"), "Venetian schedule page")
    for k, s in (meta.get("sheets") or {}).items():
        add(s.get("url"), "Venetian structure sheet %s" % k)
    add((meta.get("tax") or {}).get("source"), "Clark County tax ordinance")
    for v in load("venues.json", []):
        add(v.get("source"), "venue page")
    for h in load("hotels.json", []):
        add(h.get("resort_fee_source"), "resort fee page")
        add(h.get("parking_source"), "parking source")
        add(h.get("cancel_source"), "cancellation source")
        add(h.get("booking"), "official booking")
    for f in load("flags.json", []):
        add(f.get("source"), "flag source")
    for r in load("routes.json", []):
        add(r.get("maps"), "walking route")
    return urls


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read()
        return resp.status, body


def main():
    offline = "--offline" in sys.argv
    urls = collect_urls()
    ledger = load("last_checked.json", {})
    log = load("change_log.json", [])
    if not urls:
        print("FAIL: no source URLs found in data/ea99006a")
        return 1
    if "--seed" in sys.argv:
        added = 0
        for u, label in urls.items():
            if u not in ledger:
                ledger[u] = dict(url=u, label=label, sha256="", bytes=0, http=0,
                                 first_checked="", last_checked="", last_attempt="",
                                 status="pending-first-run")
                added += 1
        with open(LEDGER, "w") as fh:
            json.dump(ledger, fh, indent=1, sort_keys=True)
        print("seeded %d new URLs; %d under monitor" % (added, len(ledger)))
        return 0

    print("%d official sources under monitor" % len(urls))
    if offline:
        missing = [u for u in urls if u not in ledger]
        print("offline: %d sources already in the ledger, %d not yet checked"
              % (len(ledger), len(missing)))
        print("offline: ledger OK")
        return 0

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    changed, failed, ok = [], [], 0
    for i, (url, label) in enumerate(sorted(urls.items())):
        try:
            status, body = fetch(url)
            sha = hashlib.sha256(body).hexdigest()
        except Exception as exc:
            failed.append((url, "%s: %s" % (type(exc).__name__, exc)))
            prev = ledger.get(url)
            if prev:
                entry = dict(prev, last_attempt=now, status="error",
                             error="%s: %s" % (type(exc).__name__, exc))
            else:
                entry = dict(url=url, label=label, sha256="", bytes=0, http=0,
                             first_checked=now, last_checked="", last_attempt=now,
                             status="error", error=("%s: %s" % (type(exc).__name__, exc)))
            ledger[url] = entry
            continue
        prev = ledger.get(url)
        entry = dict(url=url, label=label, sha256=sha, bytes=len(body), http=status,
                     first_checked=(prev or {}).get("first_checked", now),
                     last_checked=now, last_attempt=now, status="ok")
        if prev and prev.get("sha256") and prev["sha256"] != sha:
            entry["status"] = "changed"
            changed.append((url, label, prev["sha256"][:12], sha[:12]))
            log.append(dict(changed_at=now, url=url, label=label,
                            old_sha256=prev["sha256"], new_sha256=sha,
                            old_bytes=prev.get("bytes"), new_bytes=len(body)))
        ledger[url] = entry
        ok += 1
        time.sleep(SLEEP)

    with open(LEDGER, "w") as fh:
        json.dump(ledger, fh, indent=1, sort_keys=True)
    with open(CHANGELOG, "w") as fh:
        json.dump(log, fh, indent=1)
    print("checked %d, ok %d, failed %d, changed %d" % (len(urls), ok, len(failed), len(changed)))
    for u, l, a, b in changed:
        print("  CHANGED %s (%s) %s -> %s" % (l, u, a, b))
    for u, e in failed:
        print("  FAILED  %s %s" % (u, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
