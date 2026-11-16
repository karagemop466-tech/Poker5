# Repo Review — karagemop466-tech/Poker5

Reviewed on 2026-11-16 (America/Los_Angeles). Scope: every tracked file on `main` at `0ba2e55`, and every file added on `arena/b1f117c3-poker5`.

## Files reviewed line by line

| File | Lines | Finding |
|---|---|---|
| `README.md` | 1 | Contains only `# Poker5`. No description, usage, or license. **Irregularity (minor):** no documentation for the Pages site. Not changed in this session. |
| `COORDINATION.md` | — | Task board (T1–T7). Added in this session. Owner column lists one session for all tasks. No irregularity in the data. |
| `.github/` | — | Not present on `main`. No Actions workflow is used; Pages builds from the legacy branch source. |
| `site/`, `tools/` | — | Added in this session (`site/` = this session's generated site; `tools/build_site.py`, `tools/validate.py`, `tools/data_source.py`). `docs/`, `index.html`, `pages/`, and `tools/build.py` belong to other sessions and were not edited. |

Lines 1–1 of `README.md` were read; the file has no further content.

## Repository settings checked (GitHub API)

- Default branch `main`, public repository.
- GitHub Pages: status `built`, source `main` branch, path `/` (root), URL https://karagemop466-tech.github.io/Poker5/, HTTPS enforced.
- **Irregularity:** the Pages source is `main` `/` (root). A change to `/docs` returns HTTP 403 for this session's token, so it was not attempted again. This session's site is published from `site/` under the root source, at https://karagemop466-tech.github.io/Poker5/site/.
- **Irregularity:** other sessions' work (`index.html`, `pages/`, `docs/`) already covers the same brief on `main`. This session keeps its files under `site/` so nothing is overwritten.

## Source-data irregularities found while building the site

These also appear on the Flagged for Review page (`docs/flagged.html`) with links.

1. Bellagio poker page says play "will resume on Saturday, July 26". July 26, 2026 is a Sunday. The page looks stale.
2. Bellagio Saturday PDF: heading reads $1100 buy-in, file name reads $1000, rules allocate a $600 buy-in.
3. Bellagio Saturday PDF lists a Day 2 date of 9/13/26, which is before the as-of date.
4. Venetian DeepStack page still references the WPT Fall Festival, which ended Nov 15, 2026.
5. Venetian `/resort/casino/poker/tournaments.html` returns 404.
6. Venetian resort-fee URLs tried (`/resort/casino/poker/resort-fee.html`, `/hotel/resort-fee.html`) return 404.
7. Venetian `$300` structure sheets disagree on house fee and prize pool per entry (#5: $58 / $242; #10: $60 / $240).
8. Venetian `$400` structure sheets disagree on house fee and prize pool per entry (#2/#3: $70 / $330; #6: $65 / $335).
9. Venetian event numbers repeat across flights of one event (for example #19 for 1A–1C, #26 for 1A–1F, #47 for 1A/1B) and a few numbers reappear on different days. Rows are keyed on date, start time, and event number together.
10. Wynn's poker page `wynnlasvegas.com/Casino/Poker` was removed; `wynnlasvegas.com/hotel` shows a "checked out" page.
11. Wynn's Mon–Thu and Sat/Sun events are labelled as daily events but allow re-entry.
12. Caesars daily NLH flyer lists a $1,000 guarantee for each event; the pool breakdown should be checked against it.
13. Golden Nugget poker page is blank. Resorts World poker page covers dining only. ARIA page has no tournament list.
14. The PokerAtlas MGM Grand calendar is dated 2025 and was not used.

## Values that could not be verified (left blank or marked)

- Nightly room rates for every hotel (dynamic pricing; no official static rate found).
- Walking time from each hotel to each poker room (not measured from an official source).
- Official resort fees for The Venetian, The Palazzo, Bellagio, ARIA, and Caesars Palace. Third-party figures only; they conflict.
- Official Clark County lodging tax rate (13.38% from third-party sources only).
- Single-entry status for 31 Venetian rows and 46 Wynn WPT rows (structure sheets not read).
- Single-entry status for Wynn's nightly $160 event (structure sheet not read).

## What is verified

- 45 Venetian rows: single-entry status confirmed from the structure sheet (no re-entry or add-on language).
- Wynn Mon–Thu, Friday, and Sat/Sun daily terms from the official structures PDF.
- Caesars daily NLH schedule and re-entry/add-on terms from the official flyer.
- Bellagio Friday, Saturday, and Sunday terms from the official PDFs (advantage section).
- Wynn resort fee $55 plus tax from the official Wynn terms page.

## Recommendations

See Suggestions on the site (S1–S10). None has been implemented; each needs the user's decision.
