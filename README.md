# Poker5 — Las Vegas Strip poker trip planner

**Live site:** https://karagemop466-tech.github.io/Poker5/

An independent, evidence-first planner for a Las Vegas Strip poker trip: which
tournaments have an explicit single-entry/no-rebuy/no-add-on policy, what each
entry costs, how long a playing day may run, which days could fit two events, and
what a hotel night costs once the resort fee and room tax are considered.

Every value on the site comes from an official source — a casino's own schedule,
structure sheet, hotel terms page, or the Clark County room-tax ordinance — and
every row links to it. Anything that could not be confirmed is blank and listed on
the **Flagged for review** page. Nothing is inferred.

## How the site is built

```
official pages / PDFs
        │  scripts/scrape_251c122f.py      (runs daily in GitHub Actions)
        ▼
data/c6087e2c/schedule_live.json, structures.json, scrape_status.json, watch_status.json
        │  scripts/merge_251c122f.py       (applies the single-entry standard)
        ▼
data/c6087e2c/events_verified.json
        │  scripts/build_251c122f.py       (generates index.html + pages/)
        ▼
index.html, pages/**, assets/            (published by GitHub Pages from main `/`)
        │  scripts/crosscheck_251c122f.py  (fails if a verdict cannot be reproduced)
```

* `scripts/scrape_251c122f.py` reads the official Venetian DeepStack Extravaganza IV
  schedule and every structure-sheet PDF it links (37 sheets), extracts the
  late-registration cutoff, level length, starting chips, guarantee and house fee
  with the exact excerpt each value came from, and hashes the hotel/venue pages on
  a watch list so a change can be spotted. It has a network-free `--self-test`.
* `scripts/merge_251c122f.py` requires affirmative official language for a
  **confirmed single-entry** verdict: the row's own sheet must match the event,
  describe a one-day event, and state a one-entry cap/freezeout plus no re-entry,
  no rebuy and no add-on. Silence is not proof; one-day rows without those written
  rules are flagged and excluded from ranking. Disagreements between official
  sources are recorded and shown, never resolved by picking one.
* `scripts/build_251c122f.py` generates the site and refuses to publish a data row
  without a source link or an internal link that does not resolve.
* `scripts/crosscheck_251c122f.py` re-derives every verdict from the stored rule
  fields and fails the build if one cannot be reproduced.

Daily job: `.github/workflows/daily-scrape.yml` (13:37 UTC). Quality gate:
`.github/workflows/quality.yml`.

## Local commands

```sh
python3 scripts/scrape_251c122f.py --self-test   # parser self-test, no network
python3 scripts/merge_251c122f.py                # capture -> events_verified.json
python3 scripts/build_251c122f.py                # regenerate the site
python3 scripts/crosscheck_251c122f.py           # verify verdicts, sources, links
node serve.mjs 4173                              # local preview on 0.0.0.0:4173
```

The agent sandbox that authored this repository cannot open a TCP connection to
casino hosts, so the live reading happens on GitHub Actions runners; the capture
is committed to `data/c6087e2c/` and every excerpt in it can be checked against
the linked PDF.

## Other files in the repo

`docs/`, `site/`, `site-*/`, `dashboard-*/`, `planner-aa83f1e1/`, `data-*/` and
`tools/` are output from earlier parallel sessions. They are preserved unchanged
and are not part of the published root site. `COORDINATION.md` is the shared task
board and records every session's scope and results.

## Notes

Independent planning tool, not affiliated with any casino, poker room or hotel.
Values change without notice; confirm before you book or play. Must be 21+.
If gambling is a problem, call 1-800-522-4700.
