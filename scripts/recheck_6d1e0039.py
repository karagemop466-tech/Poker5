#!/usr/bin/env python3
"""Scheduled re-check of every official URL this dashboard depends on (session 6d1e0039).

What it does
------------
1. Reads data-6d1e0039/sources.json for the URL list.
2. Fetches each URL with a plain HTTP client (no JavaScript, no browser), normalises the text
   (collapses whitespace so a CDN re-render does not look like a content change) and hashes it.
3. Compares the hash with data-6d1e0039/source-hashes.json from the previous run.
4. Writes data-6d1e0039/change-log.json: one entry per URL per run, with the date, HTTP status,
   byte size before/after and whether the content changed. A page that fails is recorded as an
   error, never as "changed", so a blocked scraper cannot look like a schedule update.
5. Writes the new hashes for the next run.

Also stamps data-6d1e0039/events.json retrieved dates by rewriting data-6d1e0039/last-checked.json,
which the site builder reads for the "last checked" column.

Exit code is 0 even when a page changed (a change is a prompt to re-read, not a failure).
Exit code is 1 only when the script itself could not run.

Run locally:  python3 scripts/recheck_6d1e0039.py --dry-run
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data-6d1e0039")
SOURCES = os.path.join(DATA, "sources.json")
HASHES = os.path.join(DATA, "source-hashes.json")
CHANGES = os.path.join(DATA, "change-log.json")
CHECKED = os.path.join(DATA, "last-checked.json")

UA = ("Mozilla/5.0 (compatible; poker5-recheck/1.0; +https://github.com/karagemop466-tech/Poker5) "
      "recheck-session-6d1e0039")


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return r.status, raw


def normalise(raw, url):
    """Strip markup-ish noise so a CDN re-render is not a content change."""
    if raw[:4] == b"%PDF":
        text = raw.decode("latin-1", "ignore")
        # keep stream length stable-ish: hash the raw bytes of PDFs, they are the document
        return raw
    text = raw.decode("utf-8", "ignore")
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.encode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="fetch and report, do not write state")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    src = json.load(open(SOURCES))
    urls = src["urls"]
    if args.limit:
        urls = urls[:args.limit]

    prev = {}
    if os.path.exists(HASHES):
        try:
            prev = json.load(open(HASHES)).get("hashes", {})
        except Exception:
            prev = {}

    changes = []
    if os.path.exists(CHANGES):
        try:
            changes = json.load(open(CHANGES)).get("changes", [])
        except Exception:
            changes = []

    new_hashes = dict(prev)
    ok = 0
    changed = 0
    failed = 0

    for url in urls:
        entry = {"checked": today, "at": now, "url": url, "status": None, "changed": False,
                 "note": "", "bytesBefore": None, "bytesAfter": None}
        try:
            status, raw = fetch(url)
            body = normalise(raw, url)
            digest = hashlib.sha256(body).hexdigest()
            entry["status"] = status
            entry["bytesAfter"] = len(raw)
            entry["bytesBefore"] = prev.get(url, {}).get("bytes")
            if url not in prev:
                entry["note"] = "first snapshot recorded"
            elif prev[url].get("sha256") != digest:
                entry["changed"] = True
                entry["note"] = ("content changed since "
                                 + str(prev[url].get("checked", "an earlier run"))
                                 + " - re-read this source before trusting the rows that cite it")
                changed += 1
            else:
                entry["note"] = "unchanged"
            new_hashes[url] = {"sha256": digest, "checked": today, "at": now,
                               "status": status, "bytes": len(raw)}
            ok += 1
        except urllib.error.HTTPError as ex:
            entry["status"] = ex.code
            entry["note"] = "HTTP error - recorded as an error, not as a content change"
            failed += 1
        except Exception as ex:  # network, timeout, TLS
            entry["status"] = "error"
            entry["note"] = f"{type(ex).__name__}: {ex}"[:300]
            failed += 1
        changes.append(entry)
        print(f"[{entry['status']}] {'CHANGED ' if entry['changed'] else ''}{url} :: {entry['note']}")
        time.sleep(0.4)  # be polite to the official servers

    if args.dry_run:
        print(f"\ndry run: {ok} fetched, {changed} changed, {failed} failed, {len(urls)} urls")
        return 0

    # keep the log bounded but never drop the most recent full run
    changes = changes[-4000:]
    os.makedirs(DATA, exist_ok=True)
    with open(CHANGES, "w") as f:
        json.dump({"session": "6d1e0039", "updated": now, "changes": changes}, f, indent=1)
    with open(HASHES, "w") as f:
        json.dump({"session": "6d1e0039", "updated": now, "hashes": new_hashes}, f, indent=1)

    per_url = {}
    for c in changes:
        per_url[c["url"]] = c["checked"]
    with open(CHECKED, "w") as f:
        json.dump({"session": "6d1e0039", "updated": now, "lastChecked": per_url}, f, indent=1)

    # a GitHub-step summary so the run is readable from the Actions UI
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("## Re-check run " + now + "\n\n")
            f.write(f"- URLs fetched: **{ok}**\n- Content changed: **{changed}**\n"
                    f"- Errors: **{failed}**\n\n")
            if changed:
                f.write("### Changed sources (re-read before trusting these rows)\n\n")
                for c in changes:
                    if c.get("changed") and c["checked"] == today:
                        f.write(f"- {c['url']}\n")
                f.write("\n")
            errs = [c for c in changes if c["checked"] == today and isinstance(c["status"], int)
                    and c["status"] >= 400]
            if errs:
                f.write("### Pages that returned an error\n\n")
                for c in errs:
                    f.write(f"- HTTP {c['status']} {c['url']}\n")

    print(f"\n{ok} fetched, {changed} changed, {failed} failed, {len(urls)} urls")
    return 0


if __name__ == "__main__":
    sys.exit(main())
