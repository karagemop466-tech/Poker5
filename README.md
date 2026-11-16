# Poker5

Las Vegas Strip poker tournament and hotel planner, published with GitHub Pages.

Live site: https://karagemop466-tech.github.io/Poker5/

## What is in this repo

- `index.html`, `pages/*.html`, `assets/css/style.css`: the static site (built output).
- `data/c6087e2c/`: the verified inputs for this site. Venetian schedule rows (`venetian_dse_2026.psv`), other rooms (`other_events.json`), hotels (`hotels.json`), flagged items (`flags.json`).
- `scripts/build_c6087e2c.py`: regenerates the root site from `data/c6087e2c/`. Run `python3 scripts/build_c6087e2c.py`.
- Other sessions' outputs (`docs/`, `site/`, `dashboard-*/`, `tools/`, `data/*.json|md|txt`) are kept as they were and are linked from the landing page.
- `COORDINATION.md`: the task board for parallel work.

## Verification rule

Each table value comes from an official source linked in its row. Values that cannot be confirmed are left blank and listed on the Flagged for Review page. Nothing is inferred or filled in.

This is an independent planning tool. It is not affiliated with any casino, poker room or hotel. Values change without notice. Confirm before booking or playing. Must be 21+.

---

## Session 443e914d outputs (Las Vegas Strip poker and hotel planner, single-entry focus)

Static site: https://karagemop466-tech.github.io/Poker5/site-443e914d/ (served from `main`, legacy Pages build, source `main` `/`).

| Path | Purpose |
|---|---|
| `data-443e914d/sources.json` | Every source URL, labelled official or third-party |
| `data-443e914d/tournaments_single_entry.json` | 36 one-day Venetian rows, Nov 18 – Dec 23, 2026. Single-entry status is inferred (flag P-00) |
| `data-443e914d/tournaments_multi_entry.json` | Re-entry, rebuy, add-on, and flight formats, kept separate |
| `data-443e914d/hotels.json` | Hotel rows; blank = unverified |
| `data-443e914d/pending_and_flags.json` | Pending items, hotel flags, repo irregularities |
| `tools/build_443e914d.py` | Generates `site-443e914d/` from `data-443e914d/` |
| `tools/check_links.py` | Link gate: no broken internal links; external URLs must be in `data-443e914d/sources.json` |
| `research-443e914d/verification.md` | Row-by-row check log (36/36 match the official schedule and event page) |

Rebuild and check: `python3 tools/build_443e914d.py && python3 tools/check_links.py`

---

## Session aa83f1e1 outputs — source-linked poker and stay planner

Static subsite: https://karagemop466-tech.github.io/Poker5/planner-aa83f1e1/ (served from the existing GitHub Pages `main` / source; isolated so the root site and other sessions' outputs remain intact).

| Path | Purpose |
|---|---|
| `planner-aa83f1e1/index.html` and `planner-aa83f1e1/pages/` | Dashboard, tournaments, hotels, analysis, Q&A, suggestions, flagged review, and publication pages |
| `planner-aa83f1e1/data/tournaments.json` | Source-linked tournament records; zero strict single-entry events confirmed in the reviewed subset |
| `planner-aa83f1e1/data/hotels.json` | Date-specific Venetian quote, Wynn pre-tax display, estimates, fees, and walking caveats |
| `planner-aa83f1e1/research/` | Source-by-source research notes and unresolved questions |
| `scripts/build_aa83f1e1.mjs` | Validates the session dataset and builds a local preview in `_site-aa83f1e1/` |
| `scripts/smoke_aa83f1e1.mjs` | Smoke-renders all eight pages |
| `.github/workflows/quality.yml` | Runs JavaScript, smoke, data, source-reference, link, and build checks |

The Dec 13–20, 2026 stay window is a research assumption, not user-selected. Locally run `node --check planner-aa83f1e1/assets/app.js && node scripts/smoke_aa83f1e1.mjs && node scripts/build_aa83f1e1.mjs`, then serve with `python3 -m http.server 4173 --bind 0.0.0.0 --directory _site-aa83f1e1`. This session deliberately does not add a competing Pages deployment workflow; the existing root Pages site publishes the subdirectory after merge.
