#!/usr/bin/env python3
"""Guard (session 0fd4c550): the scheduled re-check must not move the published meaning.

`recheck-ea99006a.yml` runs `scripts/integrate_b3be876c.py` on every scheduled run and commits whatever
changes. That is only safe while the generator is idempotent against the committed records: it re-derives
`data/ea99006a/*.json` from its own embedded text, so any published correction that the generator does not
carry gets reverted - and republished - the next morning. That is exactly what happened before this guard
(flag F47 back to the pre-correction wording, Q01 rewritten, Q11 and S10/S11 clobbered with other content,
and `trip.check_out` written as the last playing day of a 7-night window).

This check runs the generator and compares its output with the committed data, ignoring dates only.
Any other difference fails. It always restores the tree before exiting, so it can run in CI safely.

    python3 scripts/check_idempotency_0fd4c550.py
"""
import datetime as dt
import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EA = os.path.join(ROOT, "data", "ea99006a")
B3 = os.path.join(ROOT, "data", "b3be876c")
FILES = ["venetian.json", "hotels.json", "flags.json", "questions.json", "suggestions.json",
         "meta.json", "rates_log.json", "all.json", "rate_snapshots.json", "change_log.json"]
B3FILES = ["integration_report.json", "verification.json", "monitor_summary.json", "value_changes.json"]
TODAY = dt.date.today().isoformat()


def normalise(obj):
    """Return a comparable structure in which every date-like value is a placeholder.

    Legitimate drift is a date moving to today's date (the generator stamps read dates and the
    `last_checked` columns from the run date). Nothing else may move without a code change.
    """
    if isinstance(obj, dict):
        return {k: normalise(v) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        return [normalise(v) for v in obj]
    if isinstance(obj, str):
        s = obj.replace(TODAY, "<DATE>")
        # full ISO timestamps and the y-m-d forms of this month: dates only, so text stays meaningful
        for pat in (dt.date.today().strftime("%Y-%m"), "<DATE>"):
            s = s.replace(pat, "<DATE>")
        return s
    return obj


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"__unparseable__": str(exc)}


def main():
    snap = tempfile.mkdtemp(prefix="idem-snap-")
    saved = {}
    for d, names in ((EA, FILES), (B3, B3FILES)):
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                tgt = os.path.join(snap, os.path.basename(d), n)
                os.makedirs(os.path.dirname(tgt), exist_ok=True)
                shutil.copy2(p, tgt)
                saved[p] = tgt
    try:
        proc = subprocess.run([sys.executable, os.path.join("scripts", "integrate_b3be876c.py")],
                              cwd=ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            print("FAIL: scripts/integrate_b3be876c.py exited %d\n%s" % (proc.returncode, proc.stderr[-2000:]))
            return 1
        diffs = []
        for p, snap_p in saved.items():
            before = normalise(load(snap_p))
            after = normalise(load(p))
            if before != after:
                rel = os.path.relpath(p, ROOT)
                a = json.dumps(before, indent=1, sort_keys=True).splitlines()
                b = json.dumps(after, indent=1, sort_keys=True).splitlines()
                body = [l for l in difflib.unified_diff(a, b, "committed/" + rel, "regenerated/" + rel, n=1, lineterm="")]
                diffs.append("\n".join(body[:40]))
        if diffs:
            print("FAIL: the scheduled generator does not reproduce the committed records.")
            print("Every block below is a published value or piece of published text that a scheduled run")
            print("would change. Fix it in scripts/integrate_b3be876c.py (the generator is the source of the")
            print("published records), or make the check ignore a genuinely volatile field - never by")
            print("editing the data file alone, because the next run would revert it.\n")
            print(("\n\n".join(diffs))[:8000])
            return 1
        print("OK - regenerating from the committed capture reproduces every published record "
              "(dates aside): %d files compared." % len(saved))
        return 0
    finally:
        for p, snap_p in saved.items():
            shutil.copy2(snap_p, p)
        shutil.rmtree(snap, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
