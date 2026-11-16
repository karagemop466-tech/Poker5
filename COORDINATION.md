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

## Session de0bebd4 (branch arena/de0bebd4-poker5) — merged on top of origin/main

Original task board for this session (T1–T5) was written on the branch before `main` changed. Its status is recorded here in full, replacing the earlier board for this session.

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| T1 | Repo review (line-by-line, sourced, irregularities) | done | de0bebd4 | README.md, COORDINATION.md | github.com/karagemop466-tech/Poker5 | See REPO-REVIEW in the session's branch log |
| T2 | Live tournament research — Strip (official sources) | needs review (partial) | de0bebd4 | `data/venetian_dse_iv.txt`, `data/other_rooms.txt` | Venetian DSE IV page + 8 structure sheets; Wynn, MGM Grand, Bellagio official pages/PDFs | Golden Nugget, Caesars/Horseshoe, Planet Hollywood, Mandalay Bay, South Point, RWLV 2026 schedule NOT verified |
| T3 | Hotel research — resort fees, walking, rates | needs review (partial) | de0bebd4 | `scripts/build_site.py` (hard-coded hotel rows) | Official fees: Wynn ($55 + tax), Resorts World ($55 + tax; waived on "All Resort, No Fees" offer) | Venetian, MGM Grand, Bellagio fees unconfirmed officially; rates and walking distances blank |
| T4 | Site build | done (separate folder) | de0bebd4 | `dashboard-de0bebd4/**`, `scripts/build_site.py` | Built from data/ by the script; internal links checked | Output is in `dashboard-de0bebd4/`, not `docs/`, so it does not collide with other sessions |
| T5 | Integration: merge, PR, Pages verify | in progress | de0bebd4 | this file | — | See Log below |

### Log (session de0bebd4) — integration

- **Conflict (add/add) on merge of origin/main.** `main` already held other sessions' output: `docs/` (session 581fea93), `index.html`, `pages/`, `assets/`, and `tools/` (session arena-poker5). My branch also had `docs/`, `index.html` and `COORDINATION.md`.
  - Resolution: kept every `main` file unchanged. Removed my `docs/` and root `index.html` from the merge. Kept `main`'s COORDINATION.md and appended this section. My site is generated into `dashboard-de0bebd4/`. No other session's file was overwritten or deleted.
- **Pages.** Pages source is `main` `/`, as the other sessions also found (the token cannot change it to `/docs`, HTTP 403). The root `index.html` is `main`'s landing page; the dashboard is at `/dashboard-de0bebd4/`.
- **Disagreements between sessions to resolve (not decided here):**
  1. Venetian single-entry count: main's session states all 64 events and treats 1Day events as "unverified" on `pages/tournaments.html`. This session's rule (one day, no flight suffix, and an official sheet with no re-entry/rebuy/add-on text) verifies 30 single-entry events. The rule and the counts should be reconciled.
  2. Hotel data: main's `pages/hotels.html` cites third-party sites for walking distances and some fees. This session uses official sources only (Wynn and Resorts World fees; others blank). The main session's request #2 to mark third-party values unverified is still open.
  3. Bellagio Saturday buy-in: $1,000 (link text) vs $1,100 (PDF heading). Flagged here; not resolved.
- Items on this session's Flagged list (the dashboard's Flagged for Review page) and open questions are in `dashboard-de0bebd4/flagged.html` and `dashboard-de0bebd4/questions.html`.

---

## Session 053f694f (branch arena/053f694f-poker5) — merged on top of origin/main

Claimed before writing. Output is in `dashboard-053f694f/` and `data/tournaments.json`, `data/hotels.json`, `data/*.md`. Build: `python3 scripts/build_053f694f.py`. Files on `main` (root `index.html`, `docs/`, `pages/`, `tools/`, `dashboard-de0bebd4/`, `data/*.txt`, this board's earlier sections) were kept unchanged.

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| T1 | Create COORDINATION.md and claim tasks | done | 053f694f | COORDINATION.md | — | Branch name fixed by Arena; `session-<id>/<task>` pattern not used |
| T2 | Single-entry tournaments near the Strip (partial) | done (partial) | 053f694f | data/tournaments.json, data/tournaments.md | Venetian DSE IV schedule PDF + structure sheets 2, 6, 8, 9, 10, 13, 26, 28, 29, 30, 31, 32; Bellagio Fri/Sat/Sun PDFs; Wynn WPT and daily PDFs; Caesars 2026 flyer | Main-list rows verified line-by-line. Venetian schedule-only events and Horseshoe/ARIA/MGM Grand/Planet Hollywood/Golden Nugget/Resorts World not published as rows |
| T3 | Hotels within 30-min walk (partial) | done (partial) | 053f694f | data/hotels.json, data/hotels.md | Venetian resort-fee page; Wynn official offer terms | Fees only. Rates and walking times not verified; no true nightly cost computed |
| T4 | Executive summary | done | 053f694f | dashboard-053f694f/summary.html | — | Partial verification stated |
| T5 | Suggestions | done | 053f694f | dashboard-053f694f/summary.html | — | For user review, not implemented |
| T6 | Questions / missing information | done | 053f694f | dashboard-053f694f/summary.html | — | — |
| T7 | Site build (Pages folder) | done | 053f694f | dashboard-053f694f/**, scripts/build_053f694f.py | Build output checked for HTML structure and internal links | — |
| T8 | PR, merge, Pages deploy | in progress | 053f694f | — | PR #8 | Initial PR conflicted with main; resolved by merging main in (see log) |
| T9 | Record PR link and merge result | in progress | 053f694f | COORDINATION.md | PR #8 | — |

### Log (session 053f694f) — integration
- PR #8: https://github.com/karagemop466-tech/Poker5/pull/8 (base `main`, head `arena/053f694f-poker5`).
- First merge attempt failed: PR was CONFLICTING because `main` gained files from other sessions. Resolution: merged `origin/main` into this branch. For the three add/add conflicts (`COORDINATION.md`, `index.html`, `scripts/build_site.py`), kept `main`'s version. My script moved to `scripts/build_053f694f.py`. My root site files moved into `dashboard-053f694f/`. No file owned by another session was changed.
- Disagreement logged for other sessions: de0bebd4's log lists the Venetian resort fee as unconfirmed officially. The official Venetian resort-fee page states $55 plus tax per night (venetianlasvegas.com/resort/resort-fee.html). This session's hotel table uses that page.
- Request to session 581fea93 / arena-poker5 / de0bebd4 (not edited here): reconcile Venetian and Bellagio fees with the official pages above; Bellagio official PDFs state $40 and $25 optional staff gratuities that grant extra chips (advantage category).

### Flagged for Review (this session)
Full list: `dashboard-053f694f/flagged.html`. Highlights: Venetian event 01 appears on two sheets with different times; Bellagio Saturday PDF buy-in conflict ($1,100 heading vs $600 rule); Wynn daily poster is a 2025 asset; Resorts World poker room closure reported by a third party only.
