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

## Strict-entry research dashboard (session b50aa7f5)

Open the current source-linked research dashboard at [site-b50aa7f5/](./site-b50aa7f5/). It applies a strict **single-entry-overall** standard: as of November 16, 2026, no upcoming event is verified for the primary list. Confirmed re-entry/rebuy events, entry-cap-unknown events, and restricted events remain separately labeled. See the site's source ledger for the underlying schedules, structure sheets, hotel pages, and third-party route estimates.

The Dec 3–6, 2026 hotel quotes are illustrative snapshots only; no trip dates were supplied. The comparison does not rank hotels overall. This dashboard is a separate, session-scoped static site and does not replace the repository's other research outputs.

### Build and test this dashboard

Requires Node.js 20 or newer; no install step or external package is needed.

```sh
npm run check
npm run dev
```

`npm run check` runs the Node test suite and builds the publishable files into `site-b50aa7f5/`. `npm run dev` serves that folder locally on port 4173; open `http://localhost:4173`. GitHub Pages uses the existing `main` `/` source, so the dashboard is available at `/Poker5/site-b50aa7f5/` after merge.

## Session cd5ab298: Dec 2–9 research dashboard

The isolated, source-backed dashboard is in [`dashboard-cd5ab298/`](dashboard-cd5ab298/index.html) and will be served under [`/Poker5/dashboard-cd5ab298/`](https://karagemop466-tech.github.io/Poker5/dashboard-cd5ab298/) by the existing root-based Pages site. It does not replace the root site or other session outputs.

- Snapshot: Nov 16, 2026; hotel window Dec 2–9 (7 nights, 2 adults; Dec 9 is checkout day).
- 56 Venetian / Wynn-WPT calendar rows; zero events confirmed strict single-entry. Unknown terms and official-source conflicts are on its Flagged for Review page.
- Wynn's ~$5,642.92 after-tax amount is an estimate from the rounded $711 average/night; Venetian's $7,054.77 displayed estimate has a capacity warning. Neither should be treated as a guaranteed booking.
- Check this dashboard with `python3 scripts/check_site_cd5ab298.py`. It validates local links, data and quote arithmetic; it does not live-probe external sites.
