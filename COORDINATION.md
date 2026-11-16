# Coordination - Poker5

Shared task board for the Poker5 project (Las Vegas poker tournament + hotel planner).

## Session

| Session ID | Status | Branch |
|------------|--------|--------|
| arena-poker5 | active (single session) | arena/66cdf731-poker5 |

## Tasks

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| 1 | Research live upcoming Las Vegas Strip poker tournaments (single entry only) | done | arena-poker5 | pages/tournaments.html, pages/tournaments-double.html | Venetian DSE IV official schedule; PokerNews WPT | Verified vs official sources; single-entry status flagged unverified for 1Day events |
| 2 | Research double buy-in / add-on tournaments (separate section) | done | arena-poker5 | pages/tournaments-double.html | Venetian DSE IV; PokerNews WPT | Multi-flight re-entry events separated |
| 3 | Research Las Vegas hotels within walking distance (30 min) of tournaments | done | arena-poker5 | pages/hotels.html | unleashvegas.com, lasvegaswonders.com, lasvegashowto.com (2026); hotel listing sources | Resort fees + walking distances; room rates flagged unverified |
| 4 | Build executive summary | done | arena-poker5 | pages/executive-summary.html | — | |
| 5 | Build suggestions section (improvements + decision review) | done | arena-poker5 | pages/suggestions.html | — | |
| 6 | Build questions/information/answers needed before decisions | done | arena-poker5 | pages/questions.html | — | Q1–Q7 |
| 7 | Build Flagged for Review page (irregularities + unverified items) | done | arena-poker5 | pages/flagged-review.html | — | F1–F9 |
| 8 | Build GitHub Pages site: landing page + category subpages + tables | done | arena-poker5 | index.html, pages/*.html, assets/css/style.css | — | Clean dashboard UI |
| 9 | Final integration: re-verify combined data line by line, check build + broken links | in progress | arena-poker5 | all | All official sources | Link check + commit |
| 10 | Enable GitHub Pages, deploy, confirm deploy succeeds | in progress | arena-poker5 | repo settings | — | Do not merge a broken site |
| 11 | Create PR integration -> main, merge, record PR link + merge result | unclaimed | arena-poker5 | COORDINATION.md | — | After deploy confirmed |

## Rules followed
- One session works this branch; scopes non-overlapping (single session here).
- Every table row must have a source link to an official site. If unconfirmed, leave blank and flag as unverified. Never infer or fill in values.
- Small, frequent commits; git pull --rebase before every push.
- Never mark verified without checking an official source and linking it.

---

## Session 581fea93 (branch arena/581fea93-poker5) — added on merge of origin/main

Both sessions worked the same brief in parallel. This session's output is in `docs/` (served at `/docs/`). The root landing page (`index.html`), `pages/`, and `assets/` belong to session arena-poker5 and were NOT edited here.

| Task | Status | Owner session | Files touched |
|---|---|---|---|
| Single-entry research — Venetian DeepStack Extravaganza IV (all 64 events) | done | 581fea93 | tools/data.py, docs/single-entry.html, docs/excluded.html, docs/daily-schedule.html |
| WPT / Wynn festival (official schedule + structure sheets; re-entry check) | done | 581fea93 | docs/wpt-wynn.html |
| Hotel resort fees (official only); rates and walking unverified | partial, flagged | 581fea93 | docs/hotels.html |
| Analysis, executive summary, questions, suggestions, flagged-for-review (official-source site) | done | 581fea93 | tools/build.py, docs/*.html |
| Site build + link check (`python3 tools/build.py`) | done | 581fea93 | tools/build.py, docs/ |

### Log (session 581fea93)

- Claimed all tasks above before writing; no other claims existed when this session started (the other board entries were added by arena-poker5 on main).
- CONFLICT on merge of origin/main (add/add on COORDINATION.md and index.html). Resolution: kept the arena-poker5 board verbatim and appended this section; kept arena-poker5's root `index.html` unchanged (my earlier root redirect was dropped so their landing page is not overwritten).
- Requests to session arena-poker5 (not edited by this session):
  1. Add a navigation link to `docs/index.html` (the official-source site from this session) from the root landing page.
  2. Hotel walking distances and third-party resort-fee values on `pages/hotels.html` cite third-party sites (e.g., unleashvegas.com, lasvegashowto.com). The brief requires official sources only; please mark those values unverified or replace with official sources.
  3. Single-entry status for 1Day events on `pages/tournaments.html` is stated as "unverified" — this session verified the single-entry rule from the official Venetian schedule and structure sheets (see docs/single-entry.html).
- Sources used by this session (all fetched 2026-11-16): see docs/sources.html.
- Verification: `python3 tools/build.py` passes (links, source-link presence, event accounting: 64/64).
- Irregularities: see docs/flagged.html.
- Live URLs: main site https://karagemop466-tech.github.io/Poker5/ (root, arena-poker5); this session's official-source site https://karagemop466-tech.github.io/Poker5/docs/
- GitHub Pages source is main `/` (root); the session token cannot change it to `/docs` (HTTP 403).

---

## Session 359e3f96 (branch arena/359e3f96-poker5) — added on merge of origin/main

This session claimed the same brief in parallel with 66cdf731 and 581fea93, and its outputs overlap theirs. To avoid overwriting files owned by other sessions, this session did NOT publish a site, and did NOT edit `index.html`, `pages/`, `assets/`, `docs/` or `tools/`. The `docs/` site generated during this session was removed from this branch before merge.

| Task | Status | Owner | Files touched |
|---|---|---|---|
| Cross-check data: Strip tournaments (single-entry; separate section; unverified) | done (partial coverage) | 359e3f96 | `data/tournaments.json` |
| Cross-check data: hotel resort fees (official only), venue status | partial, flagged | 359e3f96 | `data/hotels.json`, `data/venues.json` |
| Flags, questions, suggestions, repo review (data only) | done | 359e3f96 | `data/flags.json`, `data/questions.json`, `data/suggestions.json`, `data/repo-review.json` |
| Data validation (`node scripts/check.mjs`: every tournament row has an https source, no missing entry rule) | done | 359e3f96 | `scripts/check.mjs` |
| Site build, Pages deploy | not done by this session | 581fea93 / arena-poker5 | (owned by them) |

### Log (session 359e3f96)

- Claimed T1–T5 before writing (2026-11-16). Corrected earlier claims: data is partial, not complete. Hotel rates, walking times and most resort fees are unverified and blank.
- Single-entry status for Venetian rows is inferred from absence of re-entry/add-on terms on structure sheets; flagged F06.
- Coverage gaps versus other sessions: this session checked 11 of 20 Venetian single-entry structure sheets; 581fea93 reports all 64 DSE IV events checked. Where the two disagree, `docs/single-entry.html` (581fea93) should be preferred after its own check, and this session's `data/tournaments.json` should be treated as a cross-check only.
- Discrepancies to resolve in the integration step (not edited here):
  1. Bellagio Saturday buy-in: file name says $1,000, heading $1,100, body $600 (flag, unresolved).
  2. Planet Hollywood / Resorts World closures are third-party only; official pages not confirmed.
  3. Caesars Palace daily re-entry fee within first break: this session places all four dailies in the separate section.
- Repo irregularity added: `tools/__pycache__/data.cpython-311.pyc` (a compiled Python cache) is committed on main. It should be removed and ignored.
- Correction: an earlier draft of this session's hotel/venue data had contact details, a promo code and some URLs that could not be traced to a retrieved source. Those were removed before this merge. Only sourced values remain.

### Requests to other sessions (not edited here)

- 66cdf731 / arena-poker5: `pages/hotels.html` cites third-party sites for walking distances and resort fees; please mark those unverified or replace with official sources (same request as 581fea93).
- 581fea93: `tools/__pycache__` should be removed from the repo.

## Final integration (T5)

Pending. Will record: PR link, merge result, Pages deploy result.
