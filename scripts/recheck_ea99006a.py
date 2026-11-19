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


MORNING_FEED_EXTRA = [
    ("https://bellagio.mgmresorts.com/en/casino/poker.html", "Bellagio poker room page (official, live)"),
    ("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf",
     "Bellagio Friday NLH $600 official PDF"),
    ("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
     "Bellagio Saturday NLH official PDF"),
    ("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf",
     "Bellagio Sunday $400 H.O.R.S.E. official PDF"),
    ("https://aria.mgmresorts.com/en/casino/poker.html", "ARIA poker room page (official, live)"),
]


def collect_urls():
    """Every official URL that backs a row, plus the hotel / tax / venue pages."""
    urls = {}

    def add(u, label):
        if u and u.startswith("https://"):
            urls.setdefault(u, label)

    # Session fe101311: official Strip-room pages that the morning feed must read every day.
    # Bellagio's poker-room.html timed out on the scheduled run, so the live poker page and
    # its three official tournament PDFs (readable at claim time) are monitored as well.
    for u, label in MORNING_FEED_EXTRA:
        add(u, label)

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
    templates = {}
    for h in load("hotels.json", []):
        add(h.get("resort_fee_source"), "resort fee page")
        add(h.get("parking_source"), "parking source")
        add(h.get("cancel_source"), "cancellation source")
        b = h.get("booking")
        if b and b.startswith("https://") and ("{" in b or "}" in b):
            templates.setdefault(b, "official booking template (not fetchable)")
        else:
            add(b, "official booking")
    for f in load("flags.json", []):
        add(f.get("source"), "flag source")
    for r in load("routes.json", []):
        m = r.get("maps")
        if m and m.startswith("https://"):
            templates.setdefault(m, "walking route link (dynamic page, not hashed)")
    urls["_templates"] = templates
    return urls


ROOM_GROUPS = [
    ("Venetian Poker Room", "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
     lambda u: "venetianlasvegas.com" in u and ("deepstack" in u or "structures" in u or "poker" in u)),
    ("Wynn / WPT World Championship", "https://www.wynnlasvegas.com/casino/poker",
     lambda u: ("wynnlasvegas.com" in u or "cdn.wynnresorts.com" in u or "worldpokertour.com" in u
                or "wptmedia" in u) and "{" not in u),
    ("Caesars Palace / Horseshoe", "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
     lambda u: "caesars.com" in u and "{" not in u),
    ("Bellagio / MGM Grand / ARIA", "https://bellagio.mgmresorts.com/en/casino/poker.html",
     lambda u: "mgmresorts.com" in u or "mgm-bellagio-poker" in u),
    ("South Point", "https://southpointcasino.com/casino/poker-room",
     lambda u: "southpointcasino.com" in u),
    ("Resorts World", "https://www.rwlasvegas.com/gaming/poker-room/",
     lambda u: "rwlasvegas.com" in u and "{" not in u),
]


def write_morning_feed(ledger):
    """Per-room morning feed derived from the monitor ledger: every Strip room's
    official schedule source, when it was last read, and whether it changed."""
    rooms = []
    for name, source, match in ROOM_GROUPS:
        urls = [u for u in ledger if match(u)]
        if not urls:
            continue
        checked = [ledger[u].get("last_checked") for u in urls if ledger[u].get("last_checked")]
        rooms.append(dict(
            room=name, source=source,
            checked_at=max(checked) if checked else "",
            urls=len(urls),
            ok=sum(1 for u in urls if ledger[u].get("status") in ("ok", "template", "route-link")),
            changed=sum(1 for u in urls if ledger[u].get("status") == "changed"),
            failed=sum(1 for u in urls if ledger[u].get("status") == "error"),
        ))
    feed = dict(generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                note=("Per-room morning feed: each official schedule source for each Strip room, re-read on the "
                      "scheduled run. 'changed' means a human must re-read the source before trusting any row "
                      "backed by it; values are never rewritten automatically."),
                rooms=rooms)
    with open(os.path.join(DATA, "morning_feed.json"), "w") as fh:
        json.dump(feed, fh, indent=1)
    print("morning feed: %d rooms" % len(rooms))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read()
        return resp.status, body


def main():
    offline = "--offline" in sys.argv
    urls = collect_urls()
    templates = urls.pop("_templates", {})
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

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for u, label in templates.items():
        status = "route-link" if "route link" in label else "template"
        if u not in ledger:
            ledger[u] = dict(url=u, label=label, sha256="", bytes=0, http=0,
                             first_checked=now, last_checked="", last_attempt="",
                             status=status)
        else:
            ledger[u]["status"] = status
    print("%d official sources under monitor (%d booking templates not fetchable)"
          % (len(urls), len(templates)))
    if offline:
        n_templates = sum(1 for e in ledger.values() if e.get("status") == "template")
        missing = [u for u in urls if u not in ledger]
        print("offline: %d sources already in the ledger, %d not yet checked, %d booking templates"
              % (len(ledger), len(missing), n_templates))
        print("offline: ledger OK (read-only; nothing written)")
        return 0

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

    for u, e in ledger.items():
        if "{" in u:
            e["status"] = "template"
    with open(LEDGER, "w") as fh:
        json.dump(ledger, fh, indent=1, sort_keys=True)
    with open(CHANGELOG, "w") as fh:
        json.dump(log, fh, indent=1)
    write_morning_feed(ledger)
    print("checked %d, ok %d, failed %d, changed %d" % (len(urls), ok, len(failed), len(changed)))
    for u, l, a, b in changed:
        print("  CHANGED %s (%s) %s -> %s" % (l, u, a, b))
    for u, e in failed:
        print("  FAILED  %s %s" % (u, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
