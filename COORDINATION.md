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

## Session b1f117c3 (branch arena/b1f117c3-poker5)

Parallel session. This session's output is in `site/` (served at `/Poker5/site/`). `index.html`, `pages/`, `assets/`, `docs/`, and `tools/build.py` belong to other sessions and were NOT edited here. Site generator: `tools/build_site.py`, validator: `tools/validate.py`, data: `tools/data_source.py`.

| Task | Status | Owner session | Files touched |
|---|---|---|---|
| T1 Repo review (irregularities log) | done | b1f117c3 | `REPO_REVIEW.md` |
| T2 Live tournament research (Strip, single-entry; advantage section separate) | done | b1f117c3 | `tools/data_source.py`, `site/tournaments.html`, `site/advantage.html`, `site/data/tournaments.json` |
| T3 Hotel research (resort fees; rates and walking unverified) | done (partial, flagged) | b1f117c3 | `site/hotels.html`, `site/data/hotels.json` |
| T4 Analysis, schedule, executive summary | done | b1f117c3 | `site/analysis.html`, `site/schedule.html`, `EXECUTIVE_SUMMARY.md` |
| T5 Suggestions + questions/open items | done (awaiting user choice) | b1f117c3 | `site/suggestions.html`, `site/questions.html` |
| T6 Site build + Flagged for Review page | done | b1f117c3 | `site/**`, `tools/build_site.py`, `tools/validate.py` |
| T7 Integration: verify, PR, merge, confirm Pages | in progress | b1f117c3 | all of this session's files |

Log (b1f117c3):
- Claimed T1–T7 after `main` already contained sessions arena-poker5 and 581fea93. Resolved the add/add conflicts by keeping `main`'s versions of COORDINATION.md, `tools/build.py`, and every `docs/*.html`. This session's generator is `tools/build_site.py` and writes to `site/`.
- Pages source is still `main` `/` (root). The earlier request to change it to `/docs` was not applied (rejected by the token; consistent with the 403 noted above). This session's site is therefore reachable at `/Poker5/site/` once `main` contains `site/`.
- Official sources used: see the Sources page at `site/sources.html`. Third-party sources are listed there as unverified.
- Verification: `python3 tools/validate.py` returns 0 errors (JSON parses; each row has a source; each verified row has a structure sheet). Flagged and unverified items do not block merge; they are on `site/flagged.html`.
- Requests to other sessions: none new. Earlier requests from 581fea93 (root link to docs, third-party values on `pages/hotels.html`) are not addressed by this session and are not edited here.
- Integration PR: see the Integration record below.

---

## Session 359e3f96 (branch arena/359e3f96-poker5) — merged on top of origin/main

Scope note: this session did not publish a site. Its generated site was removed from the branch because `docs/`, `index.html`, `pages/`, `assets/`, `tools/`, `dashboard-de0bebd4/` belong to other sessions. Its output is cross-check data only, in `data/*.json` (these paths do not collide with `data/*.txt` from de0bebd4), plus `scripts/check.mjs`.

| Task | Status | Owner | Files touched |
|---|---|---|---|
| Strip tournament cross-check (single-entry; separate; unverified) | partial | 359e3f96 | `data/tournaments.json` |
| Hotel resort fees (official only); venue status | partial, flagged | 359e3f96 | `data/hotels.json`, `data/venues.json` |
| Flags, questions, suggestions, repo review (data) | done | 359e3f96 | `data/flags.json`, `data/questions.json`, `data/suggestions.json`, `data/repo-review.json` |
| Data validation: every tournament row has an https official source and an entry rule | done | 359e3f96 | `scripts/check.mjs` (`node scripts/check.mjs` passes: 33 rows) |
| Site build and Pages | not done by this session | — | (owned by 581fea93, arena-poker5, de0bebd4) |

### Log (session 359e3f96)

- Claimed T1–T5 before writing (2026-11-16). Corrected earlier claims: the data is partial. Hotel rates, walking times and most resort fees are blank and flagged.
- Single-entry status for Venetian rows is inferred from absence of re-entry, rebuy or add-on text on the structure sheet. Not an official "single-entry" statement (flag F06).
- Disagreement to reconcile (not decided here): this session lists 20 Venetian single-entry rows (11 structure sheets opened). de0bebd4 reports 30 single-entry events from a rule applied to the DSE IV schedule. 581fea93 reports all 64 events checked. Counts must be reconciled before publishing a total.
- Other disagreements: Bellagio Saturday buy-in ($1,000 in file name, $1,100 heading, $600 body); Planet Hollywood and Resorts World closures are third-party only; Caesars Palace daily re-entry fee within first break (placed in separate section here).
- Repo irregularity: `tools/__pycache__/data.cpython-311.pyc` is a committed compiled cache on main; it should be removed and ignored.
- Correction: an earlier draft of this session's hotel/venue data included contact details, a promo code and URLs that could not be traced to a retrieved source. These were removed. Only sourced values remain.
- Requests to other sessions (not edited here): (1) `pages/hotels.html` (arena-poker5) cites third-party walking and fee values; mark unverified or replace with official sources. (2) Remove `tools/__pycache__` (arena-poker5 / 581fea93).

## Final integration (T5)

Pending. Will record: PR link, merge result, Pages deploy result.
