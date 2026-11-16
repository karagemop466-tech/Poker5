# COORDINATION.md — Shared Task Board

Shared task board for all agent sessions working in this repository.

**Status values:** `unclaimed` · `in progress` · `done` · `needs review`
(`needs review` = published on the *Flagged for Review* page and does not block anything.)

**Branch rule (this session):** this session works only on its assigned branch
`arena/de0bebd4-poker5` (session `de0bebd4`). The `session-<id>/<task>` naming in the
original brief is recorded as an irregularity (see below); the assigned branch name is fixed by the platform.

---

## Task board

| # | Task | Status | Owner (session) | Files / scope | Notes |
|---|------|--------|-----------------|---------------|-------|
| T1 | Repo review (line-by-line, sourced, irregularities flagged) | done | de0bebd4 | `README.md`, `COORDINATION.md`, `docs/flagged.html` | See Log: REPO-REVIEW |
| T2 | Live tournament research — Las Vegas Strip (official sources) | done | de0bebd4 | `data/tournaments_*.txt`, `data/*.json` | Official Venetian, Wynn, MGM Grand, Bellagio sources |
| T3 | Hotel research — resort fees, walking distance, rates | done (partial — see flags) | de0bebd4 | `data/hotels.json` | Most rates & walking distances not verifiable from official sources → left blank and flagged |
| T4 | Site build (GitHub Pages, `docs/`) | done | de0bebd4 | `docs/**`, `scripts/build_site.py` | Static site, no external dependencies |
| T5 | Integration: combined data re-verification, link check, build, PR, merge, Pages deploy | in progress | de0bebd4 | all | Final integration step (this session is the only active session) |

---

## Claims

- **2026-11-16 · session `de0bebd4`** — claimed T1–T5. No other session was active on this repository at claim time (repository contained only `README.md` and one commit `0ba2e55`).

---

## Log

### REPO-REVIEW (T1) — de0bebd4
- Repository state at start: `README.md` (`# Poker5`), single commit `0ba2e55 Initial commit`, no code, no build, no tests, no CI, no `.gitignore`, no license.
- `COORDINATION.md` did not exist; created by this session.
- Irregularities:
  1. The brief's branch naming (`session-<id>/<task>`) conflicts with the platform-assigned branch (`arena/de0bebd4-poker5`). The platform branch was used.
  2. The brief's links (`[COORDINATION.md](http://COORDINATION.md)`) and the `&amp;lt;` escapes in the branch-name text are malformed; treated as plain filenames/patterns.
  3. The brief references a "final integration session" and per-task branches; in this run one session performed all tasks, so the integration step is performed by the same session (recorded here).
- Sources: https://github.com/karagemop466-tech/Poker5 (repository itself).

### TOURNAMENTS (T2) — de0bebd4
- Primary official sources fetched (see `docs/sources.html` for the full list):
  - Venetian DeepStack Extravaganza IV schedule page and all 37 structure sheets referenced by it (only the ones listed in the flagged/verified tables were read; see flags).
  - Wynn Las Vegas poker page, WPT World Championship schedule PDF (both pages), Daily Tournament poster and Daily Structures PDF.
  - MGM Grand poker page, MGM Grand weekly schedule PDF, MGM Grand $120 NLH structure PDF.
  - Bellagio poker page, Bellagio Friday $600 and Saturday $1,100 structure PDFs.
- Verification performed: each row copied from the official page/PDF; single-entry status decided from the structure sheet text (rebuy/re-entry/add-on/paid-chip language). Rows whose structure was not read are marked **Unverified format**.
- Irregularities: see `docs/flagged.html`.

### HOTELS (T3) — de0bebd4
- Official resort-fee text confirmed: Wynn ($55 + tax, visitwynn.com T&C), Resorts World ($55 per room per night, rwlasvegas.com offer T&C).
- Not confirmed from an official source (conflicting aggregator figures): Venetian, MGM Grand, Bellagio.
- Nightly rates and walking distances: not available from official sources → blank and flagged.

### SITE (T4) — de0bebd4
- Built static site in `docs/` from `data/` by `scripts/build_site.py`. GitHub Pages source: `main` branch, `/docs` folder.

### INTEGRATION (T5) — de0bebd4
- Pending: link check, rebuild, PR `arena/de0bebd4-poker5` → `main`, merge, Pages deploy verification. Results will be appended below.
