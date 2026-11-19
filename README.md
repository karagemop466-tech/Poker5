# Poker5 — Las Vegas Strip poker trip planner

**Live site:** https://karagemop466-tech.github.io/Poker5/

An independent, evidence-first planner for a Las Vegas Strip poker trip: which
tournaments an official source shows to be free of paid re-entry, add-ons and extra
flights, what each one costs, how long a playing day runs, which days can hold a
second event, and what a hotel night really costs once the mandatory resort fee and
the room tax are added.

Every value on the site comes from an official source — a casino's own schedule,
structure sheet, hotel terms page, or the Clark County room-tax ordinance — and
every row links to it. Anything that could not be confirmed is blank and listed on
the **Flagged for review** page. Nothing is inferred.

## The single-entry standard the site applies

A row is listed as satisfying a single-entry policy only when **its own** structure
sheet was read in full, that sheet's event-number list includes the event, the event
is one day, and the text contains no re-entry, rebuy, add-on, double-entry,
alternate-stack or purchased-chip language. The label then reads *"sheet read - no
re-entry language"*: the absence of a rule is not a rule, and no official source in
this window states a one-entry limit for any event. Anything a source does state as
paid re-entry, an add-on, extra flights or a membership-priced first buy-in is moved
to the Advantage / multi-entry page with the sentence that caused it, and is excluded
from the ranking and from the day plan. Satellites and tag-team events are labelled
separately and never ranked. An event is ranked only when both its total entry fee
and its guarantee are published, and the value shown is `guarantee / buy-in` as a
description, never a forecast.

Counts as of the 2026-11-19 re-verification (247 merged rows): 0 with an official
one-entry statement, 53 read with no re-entry language, 75 excluded for paid
advantage, 35 continuation rows, 84 with no published terms, 41 rankable, 14 rows the
earlier sessions classified differently, 38 items in the review queue.

## How the site is built

```
official pages / PDFs  (read on a GitHub Actions runner: this sandbox cannot open a TCP
                       connection to a casino host, so the reading is done where it can)
        │
        ├── scripts/scrape_251c122f.py  ->  data/c6087e2c/   Venetian schedule page + all 37
        │     scripts/merge_251c122f.py                       structure sheets, with the excerpt,
        │                                                     hash and timestamp behind every value
        ├── scripts/data_ea99006a.py    ->  data/ea99006a/   WPT / Wynn / other rooms, the URL
        │     scripts/recheck_ea99006a.py                     ledger and its change log
        └── data/bdcaf0bf/facts_20261119.json                 this session's dated re-read of
                                                              each official page (quote + result)
        ▼
scripts/integrate_bdcaf0bf.py   joins the three inputs, re-reads the sheet text with an
        │                       independent keyword pass, applies one published standard,
        │                       and keeps every disagreement as data
        ▼
data/bdcaf0bf/*.json            events, hotels, rates log, day plan, windows, flags,
        │                       conflicts, sources, per-URL monitor state
        ▼
scripts/build_bdcaf0bf.py       writes index.html, pages/**, assets/bdcaf0bf.{css,js} -
        │                       the ONLY generator of the published site
        ▼
GitHub Pages (main, root "/")
        ▲
scripts/check_bdcaf0bf.py, scripts/check_root_site.py, scripts/crosscheck_251c122f.py,
scripts/check_ea99006a.py, npm test, and a jsdom smoke test of the live interactions
```

Publication is one scheduled job: `.github/workflows/integrate-bdcaf0bf.yml`
(12:50 UTC, about 05:00 in Las Vegas) re-reads every URL in the ledger, re-runs the
merge, rebuilds the site, validates it and commits. The older per-session jobs keep
refreshing their own `data/` folders but no longer write the root site - two
generators doing that used to make the published answers alternate, which is
flagged as **B02** and explained in `REPO_REVIEW.md`.

What each canonical script guarantees:

* `scripts/integrate_bdcaf0bf.py` — joins the captures; grades every event on a
  three-level ladder (`explicit_one_entry` / `no_reentry_language` / `multi_entry_paid`,
  plus `continuation` and `not_read`); attaches to every row the structured rule
  fields (single-entry rule, max entries, re-entry, add-on, entry structure, fee,
  guarantee, starting chips, level length, late registration, start time), each with
  its own verbatim excerpt, source URL and retrieval date; derives a duration only
  where the sheet's own level count and level length make one; keeps both earlier
  verdicts per row and writes `conflicts.json`.
* `scripts/build_bdcaf0bf.py` — the only writer of the published site. Refuses a
  data row without an official source link, refuses a broken internal link, and is
  deterministic: two runs in a row produce no diff.
* `scripts/check_bdcaf0bf.py` — re-derives every entry grade from the stored
  structure-sheet text with its own keyword pass, recomputes every ratio, every true
  nightly cost and every duration, checks the 30-minute walk rule, the one-primary
  per day rule and the ledger coverage, and parses the site JavaScript with node.
* `scripts/recheck_bdcaf0bf.py` — re-reads each URL, stores status, hash and date, and
  marks the rows whose source moved. It never overwrites a captured value; `--offline`
  validates the ledger with no network, which is what runs in the sandbox.

## Local commands

```sh
python3 scripts/integrate_bdcaf0bf.py        # captures -> data/bdcaf0bf/ (the merged dataset)
python3 scripts/build_bdcaf0bf.py            # regenerate index.html + pages/** + assets/bdcaf0bf.*
python3 scripts/check_bdcaf0bf.py            # grades, sources, links, plan, hotel arithmetic
python3 scripts/recheck_bdcaf0bf.py --offline # validate the URL ledger without a network
node work/bdcaf0bf/smoke_dom.mjs             # jsdom test of search, filters, toggle, calculator
python3 scripts/scrape_251c122f.py --self-test  # parser self-test, no network
python3 scripts/check_root_site.py           # an earlier session's root-site checker
python3 scripts/crosscheck_251c122f.py       # an earlier session's verdict checker
npm test                                     # the repository's node test suite
node serve.mjs 4173                          # local preview on 0.0.0.0:4173
```

## Other files in the repo

`docs/`, `site/`, `site-*/`, `dashboard-*/`, `planner-*/`, `data-*/` and
`tools/` are output from earlier parallel sessions; so are `pages/venues/*`
aliases listed on the landing page. They are preserved unchanged
and are not part of the published root site. `COORDINATION.md` is the shared task
board and records every session's scope and results.

## Notes

Independent planning tool, not affiliated with any casino, poker room or hotel.
Values change without notice; confirm before you book or play. Must be 21+.
If gambling is a problem, call 1-800-522-4700.
