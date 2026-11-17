#!/usr/bin/env python3
"""Daily re-check of official URLs listed in site-afff1fc9/data/sources.json.

For each monitored URL: fetch, hash the bytes (sha256), compare with the previous run, and record
last_checked (UTC date), status, and changed (bool). A change does not overwrite data; it is written to
monitor_state.json and shown on the Flagged for Review and Sources pages for a human to review.
Network failures are recorded per URL and do not fail the job.
"""
import datetime as dt
import hashlib
import json
import os
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site-afff1fc9", "data")
UA = "Mozilla/5.0 (compatible; poker-planner-monitor/1.0; +https://github.com/karagemop466-tech/Poker5)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 (https official URLs only)
        return r.status, r.read()


def main():
    src = json.load(open(os.path.join(DATA, "sources.json"), encoding="utf-8"))
    state_path = os.path.join(DATA, "monitor_state.json")
    prev = json.load(open(state_path, encoding="utf-8")) if os.path.exists(state_path) else {"checks": {}}
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    checks = {}
    for s in src["sources"]:
        if not s.get("monitored") or not s["url"].startswith("https://"):
            continue
        old = prev.get("checks", {}).get(s["id"], {})
        try:
            status, body = fetch(s["url"])
            digest = hashlib.sha256(body).hexdigest()
            changed = bool(old.get("sha256")) and old.get("sha256") != digest
            checks[s["id"]] = {"last_checked": today, "http_status": status, "sha256": digest,
                               "bytes": len(body), "changed": changed,
                               "changed_on": today if changed else old.get("changed_on"),
                               "error": None}
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            checks[s["id"]] = {"last_checked": old.get("last_checked"), "http_status": None,
                               "sha256": old.get("sha256"), "bytes": old.get("bytes"),
                               "changed": old.get("changed", False), "changed_on": old.get("changed_on"),
                               "error": f"{type(e).__name__}: {e}"}
        print(s["id"], checks[s["id"]]["http_status"], "changed" if checks[s["id"]]["changed"] else "", checks[s["id"]]["error"] or "")
    state = {"last_run": today, "note": "Hash comparison of raw bytes. Pages with dynamic content may show false changes; review each one.",
             "checks": checks}
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
