# Poker5 — Las Vegas Strip poker trip planner

**Live site:** https://karagemop466-tech.github.io/Poker5/

An independent, evidence-first planner for a Las Vegas Strip poker trip: which
tournaments are genuinely single-entry, what each one costs, how long a playing
day runs, which days fit two events, and what a hotel night really costs once the
resort fee and room tax are added.

Every value on the site comes from an official source — a casino's own schedule,
structure sheet, hotel terms page, or the Clark County room-tax ordinance — and
every row links to it. Anything that could not be confirmed is blank and listed on
the **Flagged for review** page. Nothing is inferred.

## How the site is built

```
official pages / PDFs
        │  scripts/scrape_251c122f.py      (daily GitHub Actions; reads the
        │                                   Venetian DSE IV schedule + 37 sheets)
        ▼
data/c6087e2c/  (preserved source capture: schedule_live.json, structures.json)
        │
        ▼
data/ea99006a/  (verified dataset the published site is built from)
        │  scripts/build_ea99006a.py        (generates index.html + pages/)
        ▼
index.html, pages/**, assets/**             (published by GitHub Pages from main `/`)
        │  scripts/check_ea99006a.py        (fails on a missing source link or
        │  scripts/recheck_ea99006a.py       a broken internal/external link)
```

* `scripts/scrape_251c122f.py` reads the official Venetian DeepStack Extravaganza IV
  schedule and every structure-sheet PDF it links (37 sheets), extracts the
  late-registration cutoff, level length, starting chips, guarantee and house fee
  with the exact excerpt each value came from, and hashes the hotel/venue pages on
  a watch list so a change can be spotted. It has a network-free `--self-test`.
* `scripts/build_ea99006a.py` is the **canonical generator of the published root
  site**. It refuses to publish a data row without a source link or an internal
  link that does not resolve, and it emits the shared `assets/app.js` that powers
  the search box, date filter, single-entry toggle, trip-cost calculator, hotel
  true-cost calculator, dated rate log and the 30-minute walk filter.
* `scripts/check_ea99006a.py` re-checks every generated page: table rows must
  carry an official `https` source, and every internal and external link must
  resolve.
* `scripts/recheck_ea99006a.py` re-fetches every official source URL, hashes it
  and records what changed; `.github/workflows/recheck-ea99006a.yml` runs it on a
  schedule and commits a change log.

**Single-entry standard.** A row is labelled *Confirmed single-entry* only when an
official source states a one-entry limit. All 37 official Venetian structure
sheets were read on 2026-11-17; none contains a one-entry, no-re-entry or freezeout
statement, and every WPT / Wynn event whose terms were read permits re-entry. The
site therefore reports **0 confirmed single-entry events**. The 47 entry rows whose
sheet shows no re-entry, rebuy or add-on text are the closest available candidates
and stay labelled *Entry cap not stated*; the 92 rows that explicitly allow re-entry,
flights or add-ons are kept on a separate Multi-entry / advantage page.

Daily jobs:
* `.github/workflows/daily-scrape.yml` — reads the official schedule and sheets and
  rebuilds the canonical root site (13:37 UTC).
* `.github/workflows/recheck-ea99006a.yml` — re-fetches every source and records
  changes (06:00 and 12:00 UTC).
* `.github/workflows/quality.yml` — validates and rebuilds on every PR and push to
  `main`.

## Local commands

```sh
python3 scripts/scrape_251c122f.py --self-test   # parser self-test, no network
python3 scripts/build_ea99006a.py                # regenerate the root site
python3 scripts/check_ea99006a.py                # verify sources and links
python3 scripts/recheck_ea99006a.py --offline    # validate the source ledger
node serve.mjs 4173                              # local preview on 0.0.0.0:4173
```

The agent sandbox that authors this repository cannot open a TCP connection to
casino hosts, so the live reading happens on GitHub Actions runners; the capture
is committed under `data/` and every excerpt in it can be checked against the
linked PDF.

## Other files in the repo

`docs/`, `site/`, `site-*/`, `dashboard-*/`, `planner-*/`, `data-*/` and `tools/`
are output from earlier parallel sessions. They are preserved unchanged and are
not part of the published root site. `COORDINATION.md` is the shared task board
and records every session's scope and results.

## Notes

Independent planning tool, not affiliated with any casino, poker room or hotel.
Values change without notice; confirm before you book or play. Must be 21+.
If gambling is a problem, call 1-800-522-4700.
