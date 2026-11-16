# COORDINATION.md — shared task board

Session ID for this work: `arena-bafafd7c` (branch `arena/bafafd7c-poker5`, base `0ba2e55` of `main`).

## Branch note
The task text asks for `session-<id>/<task>` branches. The Arena session rules fix this session to the single branch
`arena/bafafd7c-poker5`, so every task below is claimed and committed on that branch. No other session branches or
claims existed on the repo when this file was created (`main` has no COORDINATION.md).

## Task board

| ID | Task | Status | Owner | Files touched |
|----|------|--------|-------|---------------|
| T1 | Repo review (line-by-line, irregularities, links) | done | arena-bafafd7c | `docs/repo-review.html` |
| T2 | Single-entry tournaments, Las Vegas Strip (Venetian DeepStack Extravaganza IV), ranked | done | arena-bafafd7c | `scripts/data.py`, `docs/single-entry.html` |
| T3 | Rebuys / re-entry / paid-chip events (separate section) and unverified-format events | done | arena-bafafd7c | `scripts/data.py`, `docs/multi-entry.html`, `docs/flagged.html` |
| T4 | Hotels within a 30-minute walk: official resort fees, walk estimates, rate gaps | done (partial: base rates and Encore/Bellagio/ARIA/Resorts World fees NOT verified) | arena-bafafd7c | `scripts/data.py`, `docs/hotels.html` |
| T5 | Day schedule (official start and registration-close times, Nov 16 – Dec 23) | done (no verified single-entry start before 10:10 AM) | arena-bafafd7c | `docs/schedule.html` |
| T6 | Static site build, link and source-coverage checker | done | arena-bafafd7c | `scripts/build_site.py`, `scripts/check_links.py`, `docs/*` |
| T7 | Questions, suggestions (not implemented), Flagged for Review, sources | done | arena-bafafd7c | `docs/questions.html`, `docs/suggestions.html`, `docs/flagged.html`, `docs/sources.html` |
| T8 | Integration: re-verify, build, check, PR to `main`, merge, Pages check | in progress (PR #11 open) | arena-bafafd7c | `COORDINATION.md`, `docs/*` (final integration only, this branch) |

Status values: unclaimed / in progress / done / needs review. Items marked "needs review" are published on the
Flagged for Review page.

## Integration record

- PR: https://github.com/karagemop466-tech/Poker5/pull/11 (`arena/bafafd7c-poker5` → `main`)
- Merge result: _to be filled in by the integration step_
- Pages deploy: _to be filled in by the integration step_

## Log

- 2026-11-16 — arena-bafafd7c — Claimed T1–T8 on branch `arena/bafafd7c-poker5`. Repo contained only `README.md` ("# Poker5"). Created this file.
- 2026-11-16 — arena-bafafd7c — Re-verified every value against official pages and PDFs. Removed values that were not sourced (invented URLs, unverified tax and fee figures, a guessed Bellagio Saturday guarantee). Rebuilt `scripts/data.py` from source-checked values only. Built `docs/` and ran `scripts/check_links.py` (PASS).
