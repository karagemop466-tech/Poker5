# Poker5

Las Vegas Strip live poker tournament and hotel planner. Every value is taken from an official operator or tournament page; anything unverified is left blank and listed on the **Flagged for Review** page.

## Live site

GitHub Pages (built from `docs/` on `main`): https://karagemop466-tech.github.io/Poker5/

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
| `docs/` | Generated static site (do not edit by hand; edit `data/` and rebuild) |
| `COORDINATION.md` | Shared task board for parallel agent sessions |

## Rebuild

```bash
python3 tools/build_site.py
```

## Verification approach

- Each single-entry row cites the official schedule PDF (date, start, buy-in, guarantee, chips, late-registration close) and the official structure sheet (rules: no re-entry or add-on language).
- Multi-entry formats are classified from the official terms; they are never ranked against single-entry events.
- Derived values (guarantee ÷ buy-in, prize pool per entry = buy-in − house fee) are arithmetic on verified inputs and are labelled as calculated.
- No value is inferred. Blanks are intentional and flagged.
