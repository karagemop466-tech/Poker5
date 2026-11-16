# Poker5

Las Vegas Strip live poker tournament and hotel planner. Every value is taken from an official operator or tournament page; anything unverified is left blank and listed on the **Flagged for Review** page.

## Live site

GitHub Pages (built from `docs/` on `main` by `.github/workflows/pages.yml`). Expected URL: https://karagemop466-tech.github.io/Poker5/ (confirmed only after the first deploy).

Pages:
- `index.html` – landing dashboard
- `tournaments.html` – single-entry live tournaments (verified)
- `multi-entry.html` – re-entry, rebuy, add-on and flight formats (kept separate)
- `schedule.html` – verified day plan
- `hotels.html` – hotel resort fees and blanks for unverified values
- `analysis.html` – calculated findings
- `executive-summary.html`, `questions.html`, `suggestions.html`
- `flagged-review.html` – irregularities and unverified items, with source links
- `sources.html` – every source URL used

## Repository layout

| Path | Purpose |
|---|---|
| `data/sources.json` | Every source URL, labelled official or third-party |
| `data/tournaments_single_entry.json` | Verified single-entry events (Venetian) |
| `data/tournaments_multi_entry.json` | Multi-entry / re-entry / flight formats |
| `data/hotels.json` | Hotel rows; blank = unverified |
| `data/pending_and_flags.json` | Pending tournaments, hotel items, repo irregularities |
| `tools/build_site.py` | Stdlib-only generator that writes `docs/` from `data/` |
| `tools/check_links.py` | Link gate: no broken internal links; every external URL must be in `data/sources.json` |
| `research/verification.md` | Row-by-row verification log |
| `.github/workflows/pages.yml` | Builds, gates, and deploys `docs/` to GitHub Pages |
| `docs/` | Generated static site (do not edit by hand; edit `data/` and rebuild) |
| `COORDINATION.md` | Shared task board for parallel agent sessions |

## Rebuild

```bash
python3 tools/build_site.py
python3 tools/check_links.py
```

## Verification approach

- Single-entry rows (36): date, weekday, start, buy-in, and guarantee re-checked against the official schedule PDF and event page. See `research/verification.md` for the row-by-row table. Structure-sheet fields for older rows were recorded in an earlier session and are not all re-read.
- Multi-entry formats are classified from the official terms; they are never ranked against single-entry events.
- Derived values (guarantee ÷ buy-in, prize pool per entry = buy-in − house fee) are arithmetic on verified inputs and are labelled as calculated.
- No value is inferred. Blanks are intentional and flagged.
