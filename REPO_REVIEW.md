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

These also appear on the Flagged for Review page (`site/flagged.html`) with links.

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

---

# Repo review — 2026-11-17 (session aecba91e)

Scope: every tracked path on `main` at `cee51b4` plus this session's branch, read file by file, and
each prior session's headline claim compared against the files it says it produced.

## What the repository holds

188 tracked files. Twelve sessions answered the same brief independently; almost nothing was merged
across them, so the same tables exist in several mutually inconsistent copies.

| Tree | Owner session | State on 2026-11-17 |
|---|---|---|
| `index.html`, `pages/`, `assets/css/style.css`, `data/c6087e2c/`, `scripts/build_c6087e2c.py` | c6087e2c | live Pages root; regenerated by CI from its own data |
| `site/`, `tools/`, `data/` | b1f117c3 | intact, 8 pages |
| `docs/` | 581fea93 | intact |
| `site-443e914d/`, `data-443e914d/`, `research-443e914d/`, `tools/check_links.py` | 443e914d | intact; its link gate only validates its own tree |
| `site-b50aa7f5/`, `site-src/`, `serve.mjs`, `test/`, `scripts/build.mjs` | b50aa7f5 | intact; `npm run check` is the repo-level gate over these |
| `dashboard-cd5ab298/`, `scripts/check_site_cd5ab298.py`, workflow | cd5ab298 | intact |
| `dashboard-de0bebd4/`, `data/de0bebd4/`, `REVIEW_DE0BEBC4.md` | de0bebd4 | intact |
| `dashboard-053f694f/` | 053f694f | intact |
| `dashboard-bafafd7c/` | bafafd7c | intact; its COORDINATION entry says the board was read but no file list matches a committed output of its own |
| `planner-aa83f1e1/`, `_site-aa83f1e1/` (ignored), `scripts/{build,check,smoke}_aa83f1e1.mjs` | aa83f1e1 | intact; CI runs its build |
| `COORDINATION.md` | shared, append-only | board for all of the above |
| `data/aecba91e/`, `site-aecba91e/`, `assets/{css/dashboard.css,js/app.js}`, `scripts/*_aecba91e.mjs`, `scripts/build-aecba91e.mjs`, `.github/workflows/source-monitor-aecba91e.yml` | aecba91e (this session) | new |

## Irregularities found in the repository itself

1. **Two CI jobs regenerate the root landing page.** `quality.yml` runs `scripts/build_c6087e2c.py`
   and the planner's `build_aa83f1e1.mjs`, so any other session writing `index.html` or `pages/*.html`
   has its change overwritten on the next push. This session therefore publishes under
   `site-aecba91e/` and touches no root page. **Not fixed** — it needs a decision about which session
   owns the root; recorded here and on the site's Repo review page.
2. **The same fact is stated seven different ways across sessions.** "How many Venetian DSE events are
   single-entry", counted from each tree's own data file as it stands in `main`:

   | Tree | File read now | Rows it publishes |
   |---|---|---|
   | cd5ab298 | `dashboard-cd5ab298/data/tournaments.json` | 56 schedule rows, and it states zero events pass a strict single-entry test |
   | b50aa7f5 | `site-b50aa7f5/data.mjs` | 11 events |
   | aa83f1e1 | `planner-aa83f1e1/data/tournaments.json` | 25 events (2 flagged outside the window) |
   | de0bebd4 | `dashboard-de0bebd4/data/single_entry.json` | 30 rows |
   | 443e914d | `data-443e914d/tournaments_single_entry.json` | 36 rows, all labelled single-entry *by inference* in the file's own `_note` |
   | b1f117c3 | `site/data/tournaments.json` + `EXECUTIVE_SUMMARY.md` | 83 Venetian rows, 45 claimed verified single-entry |
   | aecba91e | `data/aecba91e/venetian_dse_iv.psv` | 94 rows → 54 single-entry, 29 advantage, 11 continuations |

   Nothing in the repo states which rule produced which number, which is why this session publishes
   its rules as text (`data/aecba91e/site.json` → R1…R6) and prints the reason on every excluded row.
   The counts are not reconciled by picking one; the rule is what makes them differ.
3. **Two rows in `data-443e914d/tournaments_single_entry.json` are labelled single-entry on inference**
   (the file's own `_note` says the entry rule was inferred, not read). Carried here as
   Advantage/unverified, never as confirmed.
4. **Two sessions read the same official page and recorded opposite results.** `dashboard-053f694f/flagged.html`
   states: "Session de0bebd4 log lists the Venetian resort fee as officially unconfirmed. The Venetian
   official resort-fee page states $55 plus tax per night." — while `dashboard-053f694f/hotels.html`
   leaves **The Palazzo** fee blank with the flag "Palazzo fee not stated on the official page read".
   This session's `data/aecba91e/reference.json` had carried $55 for the Palazzo on that same page,
   which is an inference about which tower the page covers. It is now blank, and the disagreement is
   published as flag R-F14.
5. **No license file.** Nothing in the repo states reuse terms for the data files. **Not fixed** — the
   maintainer's call.
6. **`node_modules/` is git-ignored while `package.json` has no dependencies.** `npm run check` works
   because it needs nothing but Node; a future contributor will read the absence of dependencies as
   intentional. Left as is.
7. **`_site-aa83f1e1/` is session aa83f1e1's local build output and is correctly git-ignored**
   (`git ls-files | grep -c '^_site-aa83f1e1'` → 0), so it is present in working trees but not in the
   repository. Recorded, not an issue.
8. **`.github/workflows/` holds two workflows that both run on every push** and neither validates the
   other sessions' trees; there is no single job that fails when any published page links to a missing
   file. This session adds `source-monitor-aecba91e.yml` for its own tree only, deliberately not
   editing another session's workflow.

## Checks run on 2026-11-17

| Check | Command | Result |
|---|---|---|
| Repo gate | `npm run check` | pass (8 tests, build of `site-b50aa7f5` OK) |
| 443e914d link gate | `python3 tools/check_links.py` | pass (11 pages, 45 external URLs) |
| cd5ab298 gate | `python3 scripts/check_site_cd5ab298.py` | pass (7 pages, 56 rows) |
| b1f117c3 validator | `python3 tools/validate.py` | 0 errors |
| aa83f1e1 build | `node scripts/build_aa83f1e1.mjs` | pass, 25 tournament records |
| this session | `node scripts/build-aecba91e.mjs && node scripts/check_site_aecba91e.mjs && node scripts/smoke_site_aecba91e.mjs` | pass (23 pages, 94 rows, 582 links) |
| transcription | `node scripts/verify_transcription_aecba91e.mjs` | pass (94 rows agree with the second reading) |
