# COORDINATION.md — shared task board

Session ID for this work: `arena-bafafd7c` (branch `arena/bafafd7c-poker5`, base `0ba2e55` of `main`).

## Branch note
The task text asks for `session-<id>/<task>` branches. The Arena session rules fix this session to the single branch
`arena/bafafd7c-poker5`, so every task below is claimed on that branch. Only this session was observed on the repo
(`main` has one commit, no other session branches or claims existed before this file).

## Task board

| ID | Task | Status | Owner | File scope |
|----|------|--------|-------|-----------|
| T1 | Repo review (line-by-line, irregularities) | in progress | arena-bafafd7c | `docs/repo-review.html`, read-only on `README.md` |
| T2 | Single-entry tournaments — Las Vegas Strip (Venetian DeepStack Extravaganza IV) | in progress | arena-bafafd7c | `scripts/data.py` (single-entry section), `docs/single-entry.html` |
| T3 | Multi-entry / re-entry / flight / unverified-format events (separate section) | in progress | arena-bafafd7c | `scripts/data.py` (multi-entry section), `docs/multi-entry.html` |
| T4 | Hotels within 30-min walk of tournaments, resort fees, true-cost fields | in progress | arena-bafafd7c | `scripts/data.py` (hotel section), `docs/hotels.html` |
| T5 | 8 AM–all-day schedule | in progress | arena-bafafd7c | `docs/schedule.html` |
| T6 | Static site build, GitHub Pages config, link checker | in progress | arena-bafafd7c | `scripts/build_site.py`, `scripts/check_links.py`, `docs/*` (shell/nav), `.github/workflows/*` |
| T7 | Questions, suggestions (not implemented), Flagged for Review, sources | in progress | arena-bafafd7c | `docs/questions.html`, `docs/suggestions.html`, `docs/flagged.html`, `docs/sources.html` |
| T8 | Integration: combined re-verification, build + link check, PR to `main`, merge, Pages check | in progress | arena-bafafd7c | final integration only (this branch) |

Status values: unclaimed / in progress / done / needs review. "needs review" items are published on the Flagged for Review page.

## Log

- 2026-11-16 — arena-bafafd7c — Claimed T1–T8 on branch `arena/bafafd7c-poker5`. Repo contained only `README.md` ("# Poker5"). Created this file.
