# Repo review — karagemop466-tech/Poker5

Reviewed again on **2026-11-19** by session `bdcaf0bf`, over the whole working tree
at `main` (`216bab6` and later). The site-level review with the file-by-file
inventory is published at
https://karagemop466-tech.github.io/Poker5/pages/repo-review.html and the irregularity
queue at https://karagemop466-tech.github.io/Poker5/pages/flagged-review.html;
this file is the short version of what a reviewer should know before trusting any
number in the repository, plus what changed in this pass.

## What this pass fixed

1. **Two generators were writing the same published files from different datasets.**
   `.github/workflows/daily-scrape.yml` rebuilt the root site from
   `data/c6087e2c/` (via `scripts/build_c6087e2c.py`) and
   `.github/workflows/recheck-ea99006a.yml` rebuilt it from `data/ea99006a/` (via
   `scripts/build_ea99006a.py`). Both committed `index.html` and `pages/**` to
   `main`, so the published answers alternated between runs - one job reported 0
   confirmed single-entry events, the other reported 55, from the same 94 schedule
   rows. This was the repository's most serious defect (flag **B02**).
   **Now fixed:** only `scripts/build_bdcaf0bf.py` writes the root site, from the
   merged `data/bdcaf0bf/`; the two older jobs keep refreshing their own data
   folders and no longer touch `index.html`, `pages/` or `assets/`.
   `.github/workflows/integrate-bdcaf0bf.yml` is the single publication loop.
2. **`scripts/build_251c122f.py` once deleted pages it did not generate**
   (`pages/method.html`, `pages/monitor.html`, `pages/routes.html`). The canonical
   builder writes files and never deletes; its checker fails the build if any
   internal link stops resolving.
3. **A third "confirmed single-entry" count (55) came from a different standard, not
   from better data.** `data/c6087e2c/structures.json` holds the full text of all 37
   official structure sheets; re-reading that text with an independent keyword pass
   finds **no** one-entry, no-re-entry, freezeout, max-entry or add-on sentence for
   any of the 94 Venetian rows. 55 vs 0 is therefore a *definitional* choice
   ("silence is enough" vs "silence is not a rule"), and both verdicts are now kept
   per row (`prev_verdict_251c122f`, `prev_rule_ea99006a`) with the disagreements
   published instead of resolved by majority.
4. **A published "no re-entry" claim was wrong for two rows.** Events #18 and #58
   (PokerAtlas Valuetown Bounty) carry a sheet sentence selling *subsequent*
   buy-ins at a member price; an earlier session graded them confirmed single-entry.
   They are now in the excluded section with the sentence quoted.
5. **The root docs contradicted the site.** `README.md`, `EXECUTIVE_SUMMARY.md` and
   `REPO_REVIEW.md` described one session's dataset and its page names
   (`pages/flagged.html`, `pages/qa.html`); they now describe the merged dataset.
   The old page names still resolve: the build emits them as clearly labelled
   aliases of the canonical pages.

## Structure of the repository now

| Area | State |
|---|---|
| `index.html`, `pages/**` | generated only by `scripts/build_bdcaf0bf.py`; 15 subpages + 3 venue pages + 4 labelled aliases |
| `assets/bdcaf0bf.css`, `assets/bdcaf0bf.js` | the site's own stylesheet and script, written by the same build |
| `assets/app.js`, `assets/css/style.css` | an earlier session's assets, left untouched: the node test suite and that session's archived pages still read them |
| `data/c6087e2c/` | the Venetian capture: schedule rows, all 37 structure-sheet texts with hashes, scrape and watch status. Refreshed by `daily-scrape.yml` |
| `data/ea99006a/` | the WPT / Wynn / other-room dataset, its URL ledger and change log. Refreshed by `recheck-ea99006a.yml` |
| `data/bdcaf0bf/` | the merged, re-verified dataset the published site reads, plus this session's dated re-reads (`facts_20261119.json`) |
| `data/`, `data-*/`, `dashboard-*/`, `planner-*/`, `site*/`, `docs/`, `tools/` | output from earlier parallel sessions, preserved unchanged and reachable from the landing page's "Earlier sessions" panel |
| `scripts/` | one builder / checker per session; `integrate_bdcaf0bf.py`, `build_bdcaf0bf.py`, `check_bdcaf0bf.py` and `recheck_bdcaf0bf.py` are the canonical set |
| `test/research.test.mjs` | 9 node tests over `site-src/` and `site-b50aa7f5/` plus two assertions about the root planner page and `assets/app.js`; they still pass unchanged |

Nine workflows exist. **Irregularity:** several monitor jobs from different
sessions poll overlapping URL sets (`recheck.yml`, `recheck-6d1e0039.yml`,
`source-monitor-a9d1e02d.yml`, `afff1fc9-monitor.yml`), so the same official page is
fetched four times a day by four jobs that each keep their own change log. Nothing
is wrong with the data, but the duplication means a source change can appear on one
session's page and not another's. Consolidating them is a decision for the owner.

**Irregularity (minor, unfixed by choice):** `tools/__pycache__/data.cpython-311.pyc`
is a compiled artefact committed by an earlier session. It is left in place because
another session's build reads that folder; it should be removed together with a
`.gitignore` entry by whoever owns `tools/`.

**Irregularity (minor):** the repository has no `LICENSE` file and no branch
protection readable with this session's token (`GET /branches/main/protection`
returns 403 while merges from this account succeed). Both are owner decisions.

## Source-data irregularities found while re-reading (each is on the flagged page with its URL)

1. Venetian `$300` structure sheets disagree with each other on the fee/pool split
   (#5: $58 / $242; #10: $60 / $240); same for `$400` (#2/#3: $70 / $330; #6:
   $65 / $335). Both values are published side by side; neither is averaged.
2. Nine sheets print a late-registration clock that does not follow from their own
   level length (e.g. sheet 6: 10 levels + break from an 11:10 AM 30-minute-level
   start is 4:25 PM, the sheet prints 4:55 PM). The printed clock wins; the
   arithmetic is flagged.
3. Event numbers repeat across flights and occasionally across dates (#19 for 1A-1C,
   #26 for 1A-1F, #47 for 1A/1B), so rows are keyed on date + start + event number.
4. The Caesars corporate disclaimer states a resort-fee *range* ($45-$60 + tax) and
   cached copies still show $45-$50, so no single per-property fee can be published.
5. The Wynn $55 resort fee, one-night deposit and 72-hour cancellation deadline were
   read from an offer's terms &amp; conditions whose stay window closed 2025-06-30 -
   genuine Wynn terms, but their applicability to a December 2026 stay is an open
   question (flag F28).
6. The Venetian structure-sheet family spans Nov 2026 - Feb 2027 with overlapping
   sheet numbering, and the series page still advertises the WPT Fall Festival that
   ended 15 Nov 2026.
7. Bellagio's page said play "will resume on Saturday, July 26" (July 26, 2026 was a
   Sunday); its Saturday PDF's heading says $1100, its file name says $1000 and its
   rules allocate $600, and it lists a Day 2 dated before the as-of date. Not used.
8. Golden Nugget's poker page is blank, Resorts World's poker page covers dining
   only, ARIA's has no tournament list, and the PokerAtlas MGM Grand calendar is
   dated 2025. Rows for those rooms stay blank and flagged.
9. `venetianlasvegas.com/resort/about/contact-us.html` now returns 404, as did
   `/resort/casino/poker/resort-fee.html` (the live path is `/resort/resort-fee.html`).

## Values that could not be verified from any official source (left blank, never inferred)

* A dated room rate for any hotel on the planned dates; rates are stored as a log.
* Any cross-property walking time.
* A maximum-entry number for any event; a starting-stack figure for the Horseshoe
  and South Point daily lists; a guarantee for any Horseshoe, Resorts World or
  South Point event.
* Bellagio, MGM Grand and ARIA hotel terms and tournament schedules for this window
  (their pages time out from this sandbox and are recorded as fetch errors in the
  ledger rather than as verified).

## Verification method, so a reviewer can repeat it

`python3 scripts/integrate_bdcaf0bf.py` rebuilds `data/bdcaf0bf/` from the two
captures; `python3 scripts/build_bdcaf0bf.py` regenerates the site and refuses a
data row without an official source link; `python3 scripts/check_bdcaf0bf.py`
re-derives every entry grade from the stored sheet text with an independent keyword
pass, recomputes every ratio, every true nightly cost and every duration, and fails
on a broken or insecure link; `node work/bdcaf0bf/smoke_dom.mjs` runs the real site
JavaScript over the real generated pages (search, date filter, single-entry toggle,
sorting, rule-field expansion, the dated rate log and the trip calculator);
`npm test`, `python3 scripts/check_root_site.py`, `python3 scripts/crosscheck_251c122f.py`
and `python3 scripts/check_ea99006a.py` all run against the same published tree.
Live re-reads happen on GitHub Actions runners because this sandbox cannot open a
TCP connection to casino hosts; every value therefore ships with a hash, a timestamp
and a verbatim quote.
