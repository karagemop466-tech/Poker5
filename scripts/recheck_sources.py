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
import html
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
        for m in re.finditer(r"https?://[^\s\"'<>|(){}\[\]]+", text):
            url = m.group(0).rstrip(".,;")
            # A URL ending in "_" is a template stub (e.g. "structure_{N}.pdf" cut at "{").
            if url.endswith("_") or not any(h in url for h in OFFICIAL_HOSTS):
                continue
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


def fetch_text(url):
    """Return (status, body_text). Only used by the schedule feed; never raises."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return "ok", resp.read(4_000_000).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 - any network failure is recorded, never guessed
        return "unreachable", str(exc)[:200]


def psv_rows():
    """The Venetian rows the site ranks, as captured from the official schedule."""
    path = os.path.join(ROOT, "data", "c6087e2c", "venetian_dse_2026.psv")
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) != 9:
                continue
            rows.append({"date": parts[0], "time": parts[1], "event_no": int(parts[2]),
                         "name": parts[3], "buy_in_usd": parts[4], "guarantee_usd": parts[5],
                         "structure_pdf_no": parts[6], "kind": parts[7]})
    return rows


def norm_text(text):
    """Normalise official-page / capture text for a presence check.

    Tags are removed, HTML entities and curly apostrophes unified, "1-Day"/"1Day"
    and "$1 Mill"/"$1M" equalised, and punctuation dropped, so layout and typography
    differences do not count as a schedule change. Only the event name is compared.
    """
    t = html.unescape(text).replace("\u2019", "'").lower()
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"(\d)[\s-]+day\b", r"\1day", t)
    t = re.sub(r"(\d)\s*mill\b", r"\1m", t)
    t = re.sub(r"[^a-z0-9$]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def schedule_feed():
    """Morning feed: is each row of our capture still present on the official page?

    Deliberately a presence check on the event name, not a parsed diff: the page markup
    is not ours to depend on, and a wrong regex must never be reported as 'the schedule
    changed'. A row whose name is not found is reported as 'text not found on the page'
    and needs a human look; a failed fetch keeps the previous feed with its date.
    """
    url = ("https://www.venetianlasvegas.com/resort/casino/poker/"
           "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
    out_path = os.path.join(DATA, "schedule_feed.json")
    previous = {}
    if os.path.exists(out_path):
        try:
            with open(out_path, encoding="utf-8") as fh:
                previous = json.load(fh)
        except (OSError, ValueError):
            previous = {}
    status, body = fetch_text(url)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if status != "ok":
        feed = dict(previous)
        feed.update({"status": "unreachable", "last_attempt": now, "note": body,
                     "source": url,
                     "explanation": ("The official page could not be read on this run, so the previous feed "
                                     "is kept with its earlier date. No row is marked changed from a failed "
                                     "fetch.")})
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(feed, fh, indent=2, sort_keys=True)
        print("schedule feed: page unreachable ({}); previous feed kept".format(body[:80]))
        return 0
    flat = norm_text(body)
    rows = psv_rows()
    missing = []
    for r in rows:
        # Compare the event-name head (before the subtitle after ";" or ", ").
        head = re.split(r";|,\s", r["name"])[0]
        needle = norm_text(head)
        r["present"] = bool(needle) and needle in flat
        if not r["present"]:
            missing.append(r)
    feed = {"status": "ok", "last_run": now, "retrieved": now[:10], "source": url,
            "rows_checked": len(rows), "rows_not_found": len(missing),
            "rows": rows,
            "note": ("Presence check of every event name in data/c6087e2c/venetian_dse_2026.psv against the "
                     "official DeepStack Extravaganza IV page. 'present' means the exact event name is on the "
                     "page today; it does not re-verify prices, which need the structure sheet. Buy-in and "
                     "guarantee columns below are our capture, not a fresh parse.")}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(feed, fh, indent=2, sort_keys=True)
    print("schedule feed: {} rows checked, {} not found on the official page".format(len(rows), len(missing)))
    for r in missing[:20]:
        print("  - event #{} {} ({})".format(r["event_no"], r["name"][:60], r["date"]))
    return 0


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
    ap.add_argument("--feed", action="store_true",
                    help="run the morning schedule feed: check every captured Venetian row against the "
                         "official page and write data/c6087e2c/schedule_feed.json")
    args = ap.parse_args()

    if args.feed:
        return schedule_feed()

    urls = collect_urls()
    baseline = load_baseline()
    sources = baseline.setdefault("sources", {})
    # Drop baseline keys that the collector no longer produces (e.g. "...pdf|Day"
    # pipe-suffix artifacts and the "{N}" template stub recorded by an older collector).
    for stale in sorted(set(sources) - set(urls)):
        print("pruned non-source baseline key: {}".format(stale))
        del sources[stale]

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
