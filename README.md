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
