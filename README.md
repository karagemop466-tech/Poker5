# Poker5

Las Vegas Strip poker tournament and hotel planner. Values are taken from official operator or tournament pages. Anything unverified is left blank and listed on the **Flagged for Review** page.

## Live site (session 443e914d)

Served as static files from the `main` branch (GitHub Pages legacy build, source `main` `/`):

- Landing page: https://karagemop466-tech.github.io/Poker5/site-443e914d/
- Pages: `index`, `tournaments` (single-entry, 36 rows), `multi-entry` (separate), `schedule`, `hotels`, `analysis`, `executive-summary`, `questions`, `suggestions`, `flagged-review`, `sources`.

Other sessions' sites on this repository are at their own paths and are not changed by this session.

## Files owned by this session (443e914d)

| Path | Purpose |
|---|---|
| `data-443e914d/sources.json` | Every source URL, labelled official or third-party |
| `data-443e914d/tournaments_single_entry.json` | 36 single-entry Venetian rows (Nov 18 – Dec 23, 2026) |
| `data-443e914d/tournaments_multi_entry.json` | Re-entry, rebuy, add-on, and flight formats (kept separate) |
| `data-443e914d/hotels.json` | Hotel rows; blank = unverified |
| `data-443e914d/pending_and_flags.json` | Pending items, hotel flags, repo irregularities |
| `tools/build_443e914d.py` | Stdlib-only generator that writes `site-443e914d/` from `data-443e914d/` |
| `tools/check_links.py` | Link gate: no broken internal links; every external URL must be in `data-443e914d/sources.json` |
| `research-443e914d/verification.md` | Row-by-row verification log |
| `site-443e914d/` | Generated site (edit the data and rebuild; do not hand-edit HTML) |

## Rebuild and check

```bash
python3 tools/build_443e914d.py
python3 tools/check_links.py
```

## Verification approach

- Single-entry rows: date, weekday, start, buy-in, and guarantee re-checked against the official Venetian schedule PDF and event page (0 mismatches; see `research-443e914d/verification.md`). Structure-sheet fields for older rows were recorded in an earlier session and are not all re-read.
- Multi-entry and flight formats are never ranked against single-entry events.
- Derived values (guarantee ÷ buy-in) are arithmetic on verified inputs and are labelled as calculated.
- No value is inferred. Blanks are intentional and flagged.
