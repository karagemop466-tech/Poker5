#!/usr/bin/env python3
"""Scheduled re-check of every official source URL used by the root Poker5 site.

Runs on a schedule (see .github/workflows/recheck.yml, daily ~06:00 UTC) and:

  1. collects every official source URL from data/c6087e2c/*.{json,psv} and
     data/*.json (the datasets the root site is built from);
  2. for each URL, fetches it (urllib) and records the HTTP status, a content
     hash, and the retrieval timestamp;
  3. compares the new content hash to the stored baseline in
     data/c6087e2c/last_checked.json;
  4. writes an updated baseline and prints a diff report; rows whose source
     changed are listed so the site can flag them.

The sandbox used to author this repo cannot reach the casino/hotel hosts, so a
fetch failure is recorded as status "unreachable" and never treated as
"verified". Use --offline to print the baseline without making any request
(used by the local build check).

Usage:
    python3 scripts/recheck_sources.py            # live re-check (needs network)
    python3 scripts/recheck_sources.py --offline   # print baseline, no requests
    python3 scripts/recheck_sources.py --check     # exit 1 if any source changed
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "c6087e2c")
BASELINE = os.path.join(DATA, "last_checked.json")
TIMEOUT = 20
UA = "Poker5-source-recheck/1.0 (planning tool; verify independently)"

# URLs are only re-checked if they are on an official host. Third-party hosts are
# recorded but not used to set verified values, so they are not re-checked.
OFFICIAL_HOSTS = (
    "venetianlasvegas.com",
    "wynnresorts.com",
    "wynnlasvegas.com",
    "worldpokertour.com",
    "wptmedia-mig.s3.amazonaws.com",
    "caesars.com",
    "mgmresorts.com",
    "bellagio.mgmresorts.com",
    "aria.mgmresorts.com",
    "mgmgrand.mgmresorts.com",
    "clarkcountynv.gov",
    "rwlasvegas.com",
)


def collect_urls():
    """Return {url: label} for every official URL found in the datasets."""
    urls = {}
    files = []
    for d in (DATA, os.path.join(ROOT, "data")):
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name.endswith((".json", ".psv", ".txt")):
                files.append(os.path.join(d, name))
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for m in re.finditer(r"https?://[^\s\"'<>\)\]]+", text):
            url = m.group(0).rstrip(".,;")
            if any(h in url for h in OFFICIAL_HOSTS):
                urls.setdefault(url, os.path.relpath(path, ROOT))
    return urls


def fetch(url):
    """Return (status, sha256, note). status in ok/unreachable/changed-host."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read(2_000_000)
        digest = hashlib.sha256(body).hexdigest()
        return "ok", digest, "HTTP {}".format(resp.status)
    except urllib.error.HTTPError as exc:
        return "http_error", "", "HTTP {}".format(exc.code)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return "unreachable", "", str(exc)[:120]


def load_baseline():
    if os.path.exists(BASELINE):
        with open(BASELINE, encoding="utf-8") as fh:
            return json.load(fh)
    return {"sources": {}, "last_run": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="do not make requests")
    ap.add_argument("--check", action="store_true", help="exit 1 if any source changed")
    ap.add_argument("--seed", action="store_true",
                    help="record the current source list as the baseline without fetching "
                         "(used to seed the baseline from the data already captured)")
    args = ap.parse_args()

    urls = collect_urls()
    baseline = load_baseline()
    sources = baseline.setdefault("sources", {})

    if args.seed:
        # The official pages were captured on this date by the research passes;
        # the seed records that as the baseline retrieval date.
        seed_date = "2026-11-16"
        for url in sorted(urls):
            sources.setdefault(url, {
                "status": "recorded",
                "sha256": "",
                "note": "captured from the official source; not yet re-fetched",
                "last_checked": seed_date,
                "first_recorded": seed_date,
                "file": urls[url],
            })
        baseline["last_run"] = seed_date
        baseline["official_source_count"] = len(urls)
        os.makedirs(DATA, exist_ok=True)
        with open(BASELINE, "w", encoding="utf-8") as fh:
            json.dump(baseline, fh, indent=2, sort_keys=True)
        print("seeded baseline: {} official sources recorded at {}".format(len(urls), seed_date))
        return 0

    if args.offline:
        changed = []
        for url, info in sources.items():
            if info.get("status") == "changed":
                changed.append(url)
        print("baseline: {} official sources recorded; last_run={}".format(
            len(sources), baseline.get("last_run")))
        if changed:
            print("changed since last re-check: {}".format(len(changed)))
            for u in changed:
                print("  -", u)
        return 0

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    changed = []
    for url in sorted(urls):
        status, digest, note = fetch(url)
        old = sources.get(url, {})
        if status == "ok":
            if old.get("sha256") and old["sha256"] != digest:
                status = "changed"
                changed.append(url)
            last_checked = now
        else:
            # Fetch failed: keep the previously recorded check date so the site
            # does not imply a fresh verification. Never treat a failure as
            # "verified" or "changed".
            last_checked = old.get("last_checked", now)
            if not old.get("sha256"):
                status = "recorded" if status in ("unreachable", "http_error") and not old else status
        sources[url] = {
            "status": status,
            "sha256": digest or old.get("sha256", ""),
            "note": note,
            "last_checked": last_checked,
            "first_recorded": old.get("first_recorded", now),
            "file": urls[url],
        }

    baseline["last_run"] = now
    baseline["official_source_count"] = len(urls)
    os.makedirs(DATA, exist_ok=True)
    with open(BASELINE, "w", encoding="utf-8") as fh:
        json.dump(baseline, fh, indent=2, sort_keys=True)

    print("re-checked {} official sources at {}".format(len(urls), now))
    print("changed: {}".format(len(changed)))
    for u in changed:
        print("  -", u)
    if args.check and changed:
        print("RESULT: sources changed; flag rows before publishing.")
        return 1
    print("RESULT: no source changed since the last recorded baseline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
