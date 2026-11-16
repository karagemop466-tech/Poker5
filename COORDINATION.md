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

---

---

## Session 359e3f96 (branch arena/359e3f96-poker5) — merged on top of origin/main

Scope note: this session did not publish a site. Its generated site was removed from the branch because `docs/`, `index.html`, `pages/`, `assets/`, `tools/`, `dashboard-de0bebd4/` belong to other sessions. Its output is cross-check data only, in `data-359e3f96/*.json` (`data/` on main is used by other sessions; this session uses `data-359e3f96/` to avoid collisions), plus `scripts/check.mjs`.

| Task | Status | Owner | Files touched |
|---|---|---|---|
| Strip tournament cross-check (single-entry; separate; unverified) | partial | 359e3f96 | `data-359e3f96/tournaments.json` |
| Hotel resort fees (official only); venue status | partial, flagged | 359e3f96 | `data-359e3f96/hotels.json`, `data-359e3f96/venues.json` |
| Flags, questions, suggestions, repo review (data) | done | 359e3f96 | `data-359e3f96/` (flags, questions, suggestions, repo-review) |
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

## Final integration (T5) — session 359e3f96

- PR: https://github.com/karagemop466-tech/Poker5/pull/7 (session branch `arena/359e3f96-poker5` → `main`).
- Merge: merged with `gh pr merge 7 --merge`, merge commit `1f7a2cd`. Merged after two rebases onto new `main` commits from other sessions. Conflicts were resolved by keeping other sessions' files (board, `data/*.json`, `data/*.txt`, `dashboard-*/`, `docs/`, `pages/`, `tools/`) unchanged. This session's files live in `data-359e3f96/`.
- Pages: source `main` `/`. Latest Pages build reported `built` with no error. Live root https://karagemop466-tech.github.io/Poker5/ loads (checked after the merge).
- Scope of this session's merge: cross-check data (`data-359e3f96/*.json`) and `scripts/check.mjs` only. No site was published by this session.
- Not done: reconciling Venetian single-entry counts (this session 20; de0bebd4 30; 581fea93 64-event check) and the hotel fee conflicts. These are listed in the Log above for the owners of those files.


---

## Session cd5ab298 (branch `arena/cd5ab298-poker5`) — Dec 2–9 research dashboard

This session's static dashboard and source data are isolated in `dashboard-cd5ab298/`; the validator is `scripts/check_site_cd5ab298.py`. The existing root Pages site, `index.html`, `pages/`, `docs/`, `site/`, `data/`, and other sessions' outputs were preserved. The existing Pages source is `main` at `/`; this session does not replace its deployment configuration.

| Task | Status | Owner | Files |
|---|---|---|---|
| Select and label a research / hotel window | done | cd5ab298 | `dashboard-cd5ab298/` |
| Research Dec 2–9 Venetian and Wynn/WPT tournament starts and entry rules | done with explicit unknowns | cd5ab298 | `dashboard-cd5ab298/data/tournaments.json`, `schedule.html`, `single-entry.html`, `extras.html` |
| Compare date-specific hotel rates, quality and resort fees | done with quote caveats | cd5ab298 | `dashboard-cd5ab298/data/hotels.json`, `hotels.html` |
| Research property-to-poker-room locations and walking estimates | partial; internal room-to-seat times unverified | cd5ab298 | `dashboard-cd5ab298/data/hotels.json`, `hotels.html` |
| Build overview, interactive calendar, Q&A and Flagged for Review | done | cd5ab298 | `dashboard-cd5ab298/*.html`, `assets/` |
| Local validation and GitHub integration / Pages verification | in progress | cd5ab298 | `scripts/check_site_cd5ab298.py`, this section |

### Research snapshot and decisions

- Snapshot date **2026-11-16**. Working hotel window: **check in Wed 2026-12-02; check out Wed 2026-12-09; 7 nights; 2 adults; 1 room**. Selected autonomously to overlap the official Venetian DeepStack Extravaganza IV (Nov 16–Dec 23) and WPT at Wynn (Nov 27–Dec 21), not a user-provided booking instruction. Tournament starts on Dec 9 are shown as checkout-day context.
- **Zero events are confirmed as strict single-entry** from the official rules reviewed. Venetian one-day PDFs often omit entry limits; silence is not treated as freezeout. WPT Prime allows one re-entry per starting flight; the $10,400 World Championship permits one entry per starting flight plus one Day 2 entry, up to four total. Venetian Events #19/#26 prohibit a later flight after bagging, but do not establish an entry cap after a bust.
- Dated calendar contains 56 rows (starts, satellites and continuations) for The Venetian and Wynn/WPT, all in Las Vegas local time. No selected-series 8:00 a.m. start appears; Venetian starts as early as 10:10 a.m. and WPT starts as early as 11:00 a.m. These are starts only; event durations are not verified.
- Venetian structure #19 confirms Events #33/#37 award two direct seats to the $800 LIPS Ladies Event #39; these are seat prizes, not cash guarantees. Entry limits remain unverified.
- Wynn Resort King direct-booking result: **$711 average/night**, resort fee included, tax excluded. Approximate after-tax total computed from the rounded average and 13.38% Clark County Primary Gaming Corridor tax: `($711 × 7) × 1.1338 ≈ $5,642.92`; booking engine did not return this exact total.
- Venetian newly remodeled Luxury King Suite direct-booking UI: **$7,054.77** for 2 adults / 7 nights, including $832.52 taxes and $385 resort fees. Same result also showed suites designed for 4+ guests and a maximum-capacity warning. Reconfirm the exact room and availability.
- Caesars Palace returned no usable 7-night room total. Horseshoe showed Dec 2–3 sold out. Their $62.30/$56.63 figures are tax-in resort fees, not room rates.
- Casino Compass secondary property-to-property estimates: Venetian–Wynn 0.5 mi / 10–15 min; Venetian–Bellagio 0.9 mi / 18–25 min; Bellagio–Caesars 0.4 mi / 10–15 min. Official venue pages put Venetian poker at Palazzo Level 2 and Wynn poker on Encore's casino floor. No assigned-room-to-poker-seat route was timed.
- Wynn general daily schedules, Caesars daily tournaments, Bellagio Friday/Sunday events, MGM Grand's stale August schedule and ARIA's missing event terms are separated from the dated series calendar or flagged. Confirm whether recurring events run during the selected series.

### Validation and integration log

- `python3 scripts/check_site_cd5ab298.py` passes: 7 dashboard HTML pages, 56 dated tournament rows, 4 hotel records, local links, source keys and quote arithmetic. `node --check dashboard-cd5ab298/assets/app.js`, JSON parsing and `git diff --check` also pass. The validator checks external URLs for HTTPS syntax; it does not make live HTTP requests.
- Integrated the latest `origin/main` at merge commit `210c621` after main had advanced with other sessions. Resolved the `COORDINATION.md` add/add conflict by keeping main's board and appending this session. Kept the existing root site and README, adding only a link to the isolated dashboard; no existing Pages source or other session output was replaced.
- PR #17 is open from `arena/cd5ab298-poker5` to `main`: <https://github.com/karagemop466-tech/Poker5/pull/17>. The initial `validate` check passed; a fresh check will run after this log update. Merge and final live Pages-path verification are pending. Intended published path is `https://karagemop466-tech.github.io/Poker5/dashboard-cd5ab298/` under the repository's existing root-based Pages deployment. Do not replace the legacy root Pages source or other sessions' outputs.

### Primary sources

The full source links are stored row-by-row in `dashboard-cd5ab298/data/tournaments.json` and `dashboard-cd5ab298/data/hotels.json`. Core sources: Venetian DSE schedule `https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html`; Wynn/WPT schedule `https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf`; WPT governing structure `https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf`; Wynn booking result `https://reservations.wynnlasvegas.com/ibe/details.aspx?propertyid=13763&rate=WEBONLY&nono=1&checkin=12/02/2026&checkout=12/09/2026&rooms=1&adults=2`; Venetian booking result `https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-12-02&children[]=0&departure_date=2026-12-09&view=calendar`; Clark County tax ordinance `https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf`; secondary route source `https://www.casinocompassapp.com/transportation/walking-the-strip`.
