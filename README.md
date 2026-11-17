# Poker5

Las Vegas Strip poker tournament and hotel planner, published with GitHub Pages.

Live site: https://karagemop466-tech.github.io/Poker5/

## What is in this repo

- `index.html`, `pages/*.html`, `pages/venues/*.html`, `assets/css/style.css`,
  `assets/app.js`: the static root site (built output), published from `main` `/`.
- `data/c6087e2c/`: the verified inputs for the root site — Venetian schedule rows
  (`venetian_dse_2026.psv`), other rooms (`other_events.json`), hotels
  (`hotels.json`), flags (`flags.json`), the dated rate log (`rates_log.json`),
  walking routes (`walking.json`) and the source re-check baseline
  (`last_checked.json`).
- `scripts/build_c6087e2c.py`: regenerates the root site from `data/c6087e2c/`.
  Run `python3 scripts/build_c6087e2c.py`.
- `scripts/recheck_sources.py`: scheduled re-check of every official source URL.
  `--seed` records the baseline, `--offline` prints it, a live run fetches and
  diffs each URL.
- `scripts/check_root_site.py`: validates links, source anchors and the baseline.
- Other sessions' outputs (`docs/`, `site/`, `site-*/`, `dashboard-*/`,
  `planner-aa83f1e1/`, `data-*/`, `tools/`, `scripts/build_*` other than
  `build_c6087e2c.py`) are preserved as they were and are linked from the landing
  page. They are not edited by the root-site integration.
- `COORDINATION.md`: the shared task board for parallel work.

## Features of the root site

- **Single-entry is not inferred from silence.** A structure sheet that does not
  mention re-entry, rebuys or add-ons does *not* make an event single-entry. An
  event is labelled *confirmed* only when its official text states a single-entry
  or no-re-entry rule. The audit of the 37 Venetian sheets found no such statement,
  so the count of confirmed single-entry events is 0 (flag F27). Rows whose rule is
  not stated stay *not stated* / *unverified*.
- **Structured rule fields.** Each event row carries the entry rule, buy-in,
  guarantee, format (standard / bounty / flight) and a source link, with a
  retrieval date.
- **Guarantee ÷ entry fee** is shown as a *descriptive ratio, not a forecast*.
  Bounty and flight events are labelled separately.
- **Last checked** date on every row, from the scheduled source re-check.
- **Scheduled source re-check.** `scripts/recheck_sources.py` runs daily
  (`.github/workflows/recheck.yml`), re-reads every official URL, diffs it
  against the stored baseline and flags rows whose source changed. A change can
  only be detected for a URL that already has a recorded content hash, so the
  first successful live run records the baseline. Hashes are of the raw response,
  so pages with dynamic content may show changes that need a human look. Changes
  are reported for review and never edit data automatically. The morning schedule
  feed (`--feed`) checks that each captured Venetian event name is still on the
  official page.
- **Trip-cost calculator** (`pages/planner.html`): entries × buy-ins + nights ×
  true hotel cost (room rate + resort fee + tax).
- **Hotels** with a dated rate log (checkout total, nightly average, resort fee,
  tax, parking, rate timestamp) and the true nightly cost, plus a ≤30-minute
  walking-route filter (only on-property 0-minute routes are verified).
- **Per-venue pages** (`pages/venues/`): Venetian, Wynn and other venues, each
  with its events and hotels.
- **Filters**: a global search box, a date filter and a confirmed-single-entry
  toggle on the tables.
- **Overlap check** (`pages/schedule.html`): a per-day primary event and a
  conditional fallback, using a clearly-labelled duration assumption (durations
  are not verified from official sources).

## Verification rule

Each table value comes from an official source linked in its row. Values that
cannot be confirmed are left blank and listed on the Flagged for Review page.
Nothing is inferred or filled in. The build fails if a row has no source link
or if an internal link is broken.

This is an independent planning tool. It is not affiliated with any casino,
poker room or hotel. Values change without notice. Confirm before booking or
playing. Must be 21+.

## Build and validate

```sh
python3 scripts/build_c6087e2c.py     # regenerate the root site
python3 scripts/check_root_site.py    # links, source anchors, baseline
python3 scripts/recheck_sources.py --offline   # print the re-check baseline
```

CI (`.github/workflows/quality.yml`) runs the build, the root-site check and the
offline re-check on every push and pull request.
