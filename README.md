# Felt & Stay — Las Vegas Poker Planner

A source-linked, static planner for the working **Dec 13–20, 2026** Las Vegas research window. That date range is a research assumption aligned with the WPT World Championship; it is **not a date choice by the user**.

## What is here

- **Dashboard** — entry-rule findings, hotel quote snapshots, and current caveats.
- **Tournaments** — filterable, source-linked listings with a strict single-entry definition.
- **Hotels** — date-specific booking evidence, fee breakdowns, and explicit quote-vs-estimate labels.
- **Analysis, Q&A, Suggestions, Flagged Review, Publication** — rationale, open questions, and release workflow.
- **Research notes and JSON** — [`research/tournaments.md`](research/tournaments.md), [`research/hotels.md`](research/hotels.md), [`data/tournaments.json`](data/tournaments.json), and [`data/hotels.json`](data/hotels.json).

No strict single-entry event is confirmed in the reviewed sources. “Unverified” is not treated as “single-entry,” and this reviewed subset is not a complete Las Vegas tournament calendar. Hotel prices are snapshots, not reservations.

## Run locally

The site has no package dependencies. Build and validate with Node.js 22 or newer:

```sh
node --check assets/app.js
node scripts/smoke.mjs
node scripts/build.mjs
python3 -m http.server 4173 --bind 0.0.0.0 --directory _site
```

Then open `http://localhost:4173` locally. The builder validates JSON, source IDs, uncertainty/summary counts, quoted price arithmetic, internal links, and copies the site to `_site/`.

## Publication

`.github/workflows/quality.yml` runs on pushes and pull requests. `.github/workflows/pages.yml` builds and deploys `_site/` from `main` to GitHub Pages. See the in-site Publication page and [`COORDINATION.md`](COORDINATION.md) for the source review and release checklist.
