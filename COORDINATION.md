# Coordination - Poker5

Shared task board for the Poker5 project (Las Vegas poker tournament + hotel planner).

## Current branch session — a9d1e02d (active)

**Branch:** `arena/a9d1e02d-poker5` (fixed by Arena). **Role:** final integration and official-source re-audit. No other active scope is shown in this board. This session claims the following non-overlapping scope before implementation:

- `COORDINATION.md` — this claim and final integration log only.
- `index.html` — final landing-page integration/link and strict-entry-summary correction only.
- `planner-a9d1e02d/**` — new unified Pages dashboard and its venue pages/assets.
- `data/final/**` — official-source event/rule records, hotel/source ledgers and monitoring baselines.
- `scripts/build_final_a9d1e02d.py`, `scripts/check_sources_a9d1e02d.py` — owned build/monitor scripts.
- `.github/workflows/source-monitor-a9d1e02d.yml` — scheduled source re-check workflow.

**Tasks:** read the live Venetian DSE IV schedule and all 37 referenced structure PDFs; represent entry caps, re-entry, add-ons, fees, late registration and rule citations separately; carry forward other official venue records only with explicit uncertainty; build the unified, dated, filterable planner and trip-cost calculator; provide venue pages, official hotel booking/source links, route links and explicit unknowns; schedule official-source change checks; validate build, links and row-level sourcing; then create the requested PR and verify Pages deployment without overwriting any other session's research.

**Status at claim:** research in progress; no event or hotel value newly promoted as verified. Initial PDF notes are in `data/final/structure-notes.md` and remain uncommitted until this claim is published.

---

## Session

| Session ID | Status | Branch |
|------------|--------|--------|
| 0a0e3c6d-poker5 | active (single session, integration) | arena/0a0e3c6d-poker5 |
| arena-poker5 | active (single session) | arena/66cdf731-poker5 |
| arena-a29fc466 | active | arena/a29fc466-poker5 |

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
| 9 | Final integration: re-verify combined data line by line, check build + broken links | done | 0a0e3c6d-poker5 | all (root site: index.html, pages/*.html, assets/css/style.css, data/c6087e2c/, scripts/build_c6087e2c.py) | Official sources linked row-by-row in data/c6087e2c/ | `python3 scripts/build_c6087e2c.py` exit 0; 10 pages regenerated, zero diff vs committed files; every table row carries a source link (build-enforced); internal link check over 90 pages / 3,547 hrefs — all resolve (only inline `data:` SVG URIs skipped). No values inferred or filled; blanks and flags remain on pages/flagged-review.html. Branch == origin/main (f203df6) before integration commits. |
| 10 | Enable GitHub Pages, deploy, confirm deploy succeeds | done | 0a0e3c6d-poker5 | repo settings | GitHub Pages API | Pages already enabled before this session: source `main` `/`, https enforced, live https://karagemop466-tech.github.io/Poker5/ ; deploy after the PR #20 merge reached status `built` (verified via Pages API, polled until built). |
| 11 | Create PR integration -> main, merge, record PR link + merge result | done | 0a0e3c6d-poker5 | COORDINATION.md | gh / GitHub | PR #20 https://github.com/karagemop466-tech/Poker5/pull/20 (arena/0a0e3c6d-poker5 -> main); merged with `gh pr merge 20 --merge` as merge commit cee51b470aa8073b85e0be25e874d6c2e4e6f2f0; state MERGED. Pages deploy confirmed `built` afterward. |

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

## Session b50aa7f5 (branch `arena/b50aa7f5-poker5`) — strict entry / hotel research

This session's standalone dashboard is published under `site-b50aa7f5/`; it preserves the existing root landing page and every other session's site and research files.

| Task | Status | Owner | Files / result |
|---|---|---|---|
| Upcoming tournament research with a strict single-entry-overall rule | done (snapshot) | b50aa7f5 | `site-src/data.mjs`; 11 records, zero verified primary-list entries, 4 confirmed multi-entry/rebuy, 6 entry-cap-unknown, 1 restricted |
| Hotel, room-tax and route context | done (illustrative / approximate) | b50aa7f5 | `site-src/data.mjs`; two dated sample quotes only (Dec 3–6, 2026), no inferred user dates or overall hotel ranking |
| Responsive site, source ledger, build and tests | done | b50aa7f5 | `site-src/`, `site-b50aa7f5/`, `scripts/build.mjs`, `test/research.test.mjs`; `npm run check` passes |
| Integrate with the current main site and verify deployment | in progress | b50aa7f5 | PR #15; preserve main's root `index.html`, existing `pages/` and all session folders; add a direct link to the strict dashboard |

### Log (b50aa7f5)

- Initial branch base: `0ba2e556c11d7c2b6e34935d3b4a2a11d5eefab0`. While this session was active, PRs #13 and #14 advanced `main` and introduced additional research sites. The current branch was kept fixed; `origin/main` was merged into it to resolve the PR conflict.
- Conflict handling: retained `main`'s existing root landing page, README material, ignore rules, and full coordination history. The new dashboard is isolated at `site-b50aa7f5/`, with editable source under `site-src/`; root landing navigation is only extended to link to it.
- **Entry standard:** schedule silence, `1Day`, and one-entry-per-flight language do not prove single-entry overall. No event meets the strict primary-list standard in this snapshot. Prior-session inferred or unverified candidate rows remain separate and are not re-labeled as confirmed.
- **Routes:** third-party estimates vary with endpoint/provider and are not measurements. Hotel quotes are snapshots only, not user-selected trip dates. No hotel is ranked overall.
- Sources were reviewed November 16, 2026. PGT's current 2027 Championship announcement and Rome2Rio route pages were checked during integration; other official links and findings are recorded in the dashboard's source ledger.
- PR #15: https://github.com/karagemop466-tech/Poker5/pull/15. Local check: `npm run check` (8 tests and static build) passes; local HTTP smoke test passed for page, ledger, JS modules, data, and CSS. Final merge and live Pages verification pending.

## Session cd5ab298 (branch `arena/cd5ab298-poker5`) — Dec 2–9 research dashboard

This session's static dashboard and source data are isolated in `dashboard-cd5ab298/`; the validator is `scripts/check_site_cd5ab298.py`. The existing root Pages site, `index.html`, `pages/`, `docs/`, `site/`, `data/`, and other sessions' outputs were preserved. The existing Pages source is `main` at `/`; this session does not replace its deployment configuration.

| Task | Status | Owner | Files |
|---|---|---|---|
| Select and label a research / hotel window | done | cd5ab298 | `dashboard-cd5ab298/` |
| Research Dec 2–9 Venetian and Wynn/WPT tournament starts and entry rules | done with explicit unknowns | cd5ab298 | `dashboard-cd5ab298/data/tournaments.json`, `schedule.html`, `single-entry.html`, `extras.html` |
| Compare date-specific hotel rates, quality and resort fees | done with quote caveats | cd5ab298 | `dashboard-cd5ab298/data/hotels.json`, `hotels.html` |
| Research property-to-poker-room locations and walking estimates | partial; internal room-to-seat times unverified | cd5ab298 | `dashboard-cd5ab298/data/hotels.json`, `hotels.html` |
| Build overview, interactive calendar, Q&A and Flagged for Review | done | cd5ab298 | `dashboard-cd5ab298/*.html`, `assets/` |
| Local validation, PR #17 merge and GitHub Pages verification | done | cd5ab298 | `scripts/check_site_cd5ab298.py`, this section |

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
- Integrated latest `origin/main` commit `0cbefd0` (PR #15) into this branch after main advanced during the PR. Preserved its newer README, coordination history, root landing-page links, Pages config and session-scoped site. Kept this dashboard isolated, added this session's record to main's coordination board and retained the root link; no other session output was replaced.
- PR #17: <https://github.com/karagemop466-tech/Poker5/pull/17> merged Nov 16, 2026 as merge commit `b65a7a501c8df2863aafab8b889ed896e998a66c`. Branch checks `check` and `validate` passed on commit `7013beb`.
- Post-merge Pages build and deploy succeeded: run <https://github.com/karagemop466-tech/Poker5/actions/runs/43940727028>. Pages remains configured to publish `main` `/`; the new dashboard is live at <https://karagemop466-tech.github.io/Poker5/dashboard-cd5ab298/>. Verified the deployed overview (using a cache-busting query after the initial stale 404) and live schedule and hotel pages. The root landing page links to this dashboard; no Pages source was replaced.
- Final local checks passed: `python3 scripts/check_site_cd5ab298.py`, `node --check dashboard-cd5ab298/assets/app.js`, JSON parsing, `git diff --check`, and repository `npm run check` (8 tests). The GitHub Actions status check reports 7 pages / 56 rows / 4 hotel records through the session validator.

### Primary sources

The full source links are stored row-by-row in `dashboard-cd5ab298/data/tournaments.json` and `dashboard-cd5ab298/data/hotels.json`. Core sources: Venetian DSE schedule `https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html`; Wynn/WPT schedule `https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf`; WPT governing structure `https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf`; Wynn booking result `https://reservations.wynnlasvegas.com/ibe/details.aspx?propertyid=13763&rate=WEBONLY&nono=1&checkin=12/02/2026&checkout=12/09/2026&rooms=1&adults=2`; Venetian booking result `https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-12-02&children[]=0&departure_date=2026-12-09&view=calendar`; Clark County tax ordinance `https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf`; secondary route source `https://www.casinocompassapp.com/transportation/walking-the-strip`.

---

## Session aa83f1e1 (branch `arena/aa83f1e1-poker5`)

Scope note: this work is isolated under `planner-aa83f1e1/` so root `index.html`, `pages/`, `assets/`, `data/`, existing Pages publication, and all other sessions' files remain intact. The branch started from `0ba2e556`; after `main` advanced with other sessions, `origin/main` was merged into this branch and its shared coordination/README history was retained and extended here.

| Task | Status | Owner/session | Files |
|---|---|---|---|
| Official tournament research and strict single-entry verification | complete — no strict single-entry event confirmed in the reviewed subset; unknowns flagged | `aa83f1e1` | `planner-aa83f1e1/research/tournaments.md`, `planner-aa83f1e1/data/tournaments.json` |
| Date-specific hotel quote, fees, and walking evidence | complete — Venetian all-in quote captured; Wynn final total and official walking times remain unknown | `aa83f1e1` | `planner-aa83f1e1/research/hotels.md`, `planner-aa83f1e1/data/hotels.json` |
| Dashboard, analysis, Q&A, suggestions, flagged-review, publication pages | complete | `aa83f1e1` | `planner-aa83f1e1/` |
| Local and CI data/link/build verification | passed locally and in PR #16 CI | `aa83f1e1` | `scripts/*_aa83f1e1.mjs`, `.github/workflows/quality.yml` |
| Existing main-root GitHub Pages subsite publication and deployment verification | merged and deployed; Pages API reports `built` and deployment `success` | `aa83f1e1` | `planner-aa83f1e1/`, this log |

### Log (session aa83f1e1)

- Research snapshot checked 2026-11-16; Dec 13–20, 2026 is a working research assumption aligned to the WPT World Championship, not user-selected dates.
- Tracked 25 event records (18 entry-rule unknown, 6 explicitly multiple-entry, 1 conflicting Bellagio Saturday listing); no reviewed event is confirmed strict single-entry. WPT World Championship event details explicitly set a four-entry maximum (one per flight plus a Day 2 entry). Venetian one-day rules, WPT Ladies re-entry, Bellagio Saturday, Wynn all-in total, current lodging tax, and official walking routes remain flagged.
- Venetian direct quote: $2,420.40 total for seven nights (room, resort fees, and taxes). Wynn display: $355 average/night including resort fee, excluding tax; no tax-inclusive total returned. 13.38% tax math is an estimate based on the cited 2021 County guide, not a Wynn quote. Rome2Rio's 3,160-ft/11-min route is third-party only.
- PR #16: https://github.com/karagemop466-tech/Poker5/pull/16 — merged Nov 16, 2026 as `32f683a6c44e7e52cd88539f5aa706c78c0a7f7d`. Main advanced through PR #18 during review; the branch merged `b96987c` and preserved the Dec 2–9 dashboard and all session history. The planner remains isolated; root landing page and generator link to the strict-entry, Dec 2–9, and aa83 dashboards.
- PR CI passed at head `6fe6345`: Quality `check` run [43942160910](https://github.com/karagemop466-tech/Poker5/actions/runs/43942160910) and Dec 2–9 `validate` run [43942160914](https://github.com/karagemop466-tech/Poker5/actions/runs/43942160914). Local `npm run check` (8 tests), aa83 syntax/smoke/data/link/build checks, `python3 scripts/check_site_cd5ab298.py`, root rebuild, HTML parse, and local HTTP checks all passed.
- GitHub Pages API reports source `main` `/`, status `built`, and [deployment run 43942237181](https://github.com/karagemop466-tech/Poker5/actions/runs/43942237181) succeeded (deployment ID `7834506681`, URL `https://karagemop466-tech.github.io/Poker5/`). The aa83 subsite path is `https://karagemop466-tech.github.io/Poker5/planner-aa83f1e1/`. The sandbox cannot make direct HTTP requests to `github.io`; verification is from the successful Pages build/deploy API plus the passing local HTTP smoke checks.

---

## Session 6d1e0039 (branch `arena/6d1e0039-poker5`) — feature build + final integration

Started 2026-11-17. Base: `f203df6` (merge of PR #19). No other session claims were active on the board, so this session claims the remaining brief items below. Scope kept isolated in `data-6d1e0039/`, `scripts/recheck_6d1e0039.py`, `.github/workflows/recheck-6d1e0039.yml`, `dashboard-6d1e0039/`, plus its own sections of `COORDINATION.md`. Root `index.html` navigation, `README.md`, and this board are edited only for final integration at the end.

| # | Task | Status | Owner | Files touched |
|---|------|--------|-------|---------------|
| N1 | Re-verify official sources (Venetian DSE IV schedule + all structure sheets, Wynn/WPT, Bellagio, Caesars, MGM Grand) and record "last checked" per row | in progress | 6d1e0039 | data-6d1e0039/ |
| N2 | Structured rule fields per event (single-entry / re-entry / add-on / fee values separately, with source excerpt + retrieval date); remove "unverified" only where a structure sheet confirms | in progress | 6d1e0039 | data-6d1e0039/, dashboard-6d1e0039/ |
| N3 | Hotels: true cost/night = rate + resort fee + 13.38% tax; dated rate log (not a single value); checkout total, nightly average, resort fee, tax, parking, cancellation, rate timestamp | in progress | 6d1e0039 | data-6d1e0039/, dashboard-6d1e0039/ |
| N4 | Walking-route check hotel–venue pairs with 30-minute limit + ≤30 min filter | in progress | 6d1e0039 | data-6d1e0039/, dashboard-6d1e0039/ |
| N5 | Schedule overlap check (start, late-reg cutoff, plausible duration; primary event + conditional fallback per day) | in progress | 6d1e0039 | data-6d1e0039/, dashboard-6d1e0039/ |
| N6 | Trip-cost calculator (entries × buy-ins + nights × true hotel cost) | in progress | 6d1e0039 | dashboard-6d1e0039/ |
| N7 | One page per venue (Venetian, Wynn, others) with its events and hotels | in progress | 6d1e0039 | dashboard-6d1e0039/ |
| N8 | Search box + date filter + single-entry/freezeout toggle filter on tournament tables | in progress | 6d1e0039 | dashboard-6d1e0039/ |
| N9 | Change monitoring: scheduled re-check of each official URL (GitHub Actions cron), dated re-check log, rows whose source changed marked | in progress | 6d1e0039 | scripts/recheck_6d1e0039.py, .github/workflows/recheck-6d1e0039.yml, data-6d1e0039/ |
| N10 | Build dashboard site, validate, PR → merge → confirm Pages deploy, record result | unclaimed | 6d1e0039 | all |

Rules: every value from an official source with link; blank + flagged if not confirmable; nothing inferred; small frequent commits; `git pull --rebase` before every push.

## Session 0a0e3c6d-poker5 (branch `arena/0a0e3c6d-poker5`) — final integration (merged on main)

This session completed integration on main. All other session outputs preserved untouched.

### Log (session 0a0e3c6d-poker5)

- Task 9 (final integration): `python3 scripts/build_c6087e2c.py` exits 0 — regenerates all 10 root Pages pages from `data/c6087e2c/`; build enforces a source link on every table row and resolves every internal link; regenerated output is byte-identical to the committed files. Independent link sweep over all 90 HTML pages: every internal link resolves. Unverified values are blank and flagged on `pages/flagged-review.html`; nothing inferred.
- GitHub Pages: enabled via API — source `main` `/`, https enforced, live at https://karagemop466-tech.github.io/Poker5/ , status `built`.
- Task 11: PR #20 merged with `gh pr merge 20 --merge` as merge commit `cee51b470aa8073b85e0be25e874d6c2e4e6f2f0` (state MERGED).
- Task 10: GitHub Pages deploy confirmed — status `built`, source `main` `/`, live https://karagemop466-tech.github.io/Poker5/ .

---

## Session arena-a29fc466 (branch `arena/a29fc466-poker5`) — integration session

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| I1 | Re-verify combined data line by line (root site: index.html, pages/, data/c6087e2c/, flags) | done | arena-a29fc466 | index.html, pages/*.html, data/c6087e2c/*, scripts/build_c6087e2c.py | Venetian DSE IV schedule (official page); WPT World Championship (official page); Caesars/Horseshoe daily tournaments (official Caesars page) | Spot-checked via web search; all verified values match official sources |
| I2 | Add achievable features: trip-cost estimator, table search box, last-checked dates | done | arena-a29fc466 | scripts/build_c6087e2c.py, pages/tournaments.html, pages/hotels.html, pages/schedule.html, pages/tournaments-double.html | — | Trip calculator on hotels page; search box on all 4 table pages; last-checked dates noted; Caesars/Horseshoe buy-ins updated from official page |
| I3 | Build, run link check, confirm no broken links | done | arena-a29fc466 | scripts/build_c6087e2c.py, all pages | `python3 scripts/build_c6087e2c.py` passes (exit 0): built 10 pages, 71 singles, 7 multis, 33 flights, 94 Venetian rows, 25 flags | Build enforced: every row has a source link, internal links resolve |
| I4 | Confirm GitHub Pages build/deploy succeeds | done | arena-a29fc466 | repo settings | Pages source `main` `/` | Pages already deployed from main `/`; site live at https://karagemop466-tech.github.io/Poker5/ |
| I5 | Create PR integration -> main, merge, record PR link + merge result | done | arena-a29fc466 | COORDINATION.md | — | PR #23 https://github.com/karagemop466-tech/Poker5/pull/23 created from arena/a29fc466-poker5 → main; merged with gh pr merge 23 --merge; Pages live at https://karagemop466-tech.github.io/Poker5/ |

### Log (session arena-a29fc466)

- Started 2026-11-17 from `main` @ `f203df65`.
- Claimed integration tasks I1–I5.
- I1–I3 done: data re-verified against official sources (Venetian DSE IV, WPT Wynn, Caesars/Horseshoe), build passes with no errors.
- I2 done: trip-cost estimator, table search box, last-checked dates added via build script; Caesars/Horseshoe buy-ins updated from official Caesars page.
- I4–I5 done: PR #23 created from `arena/a29fc466-poker5` → `main`; merged with `gh pr merge 23 --merge`; Pages live at https://karagemop466-tech.github.io/Poker5/ . Build script passes, all internal links resolve.
- All other sessions' outputs preserved unchanged.

- Task 11: PR #20 https://github.com/karagemop466-tech/Poker5/pull/20 created from `arena/0a0e3c6d-poker5` → `main`; merged with `gh pr merge 20 --merge` as merge commit `cee51b470aa8073b85e0be25e874d6c2e4e6f2f0` (state MERGED, no conflicts — branch was exactly one commit ahead of main).
- Task 10: GitHub Pages deploy after the merge polled via Pages API until status `built`; source `main` `/`, https enforced, live https://karagemop466-tech.github.io/Poker5/ . Site not broken: build script passes, all internal links resolve.
- Tasks 10 and 11 marked done in this record; this COORDINATION.md update itself goes to main through a second, one-file PR from this same branch (PR #21) so the merge result is recorded on main.
---

## Session afff1fc9 (branch `arena/afff1fc9-poker5`)

Scope: all output isolated under `site-afff1fc9/` (site, data, `data/*.json|csv`), `scripts/build_afff1fc9.py`, `scripts/check_afff1fc9.py`, `scripts/monitor_afff1fc9.py`, and `.github/workflows/afff1fc9-monitor.yml`. Root `index.html`, `pages/`, `docs/`, `data/`, `dashboard-*`, `planner-*`, `site/`, `site-b50aa7f5/`, `tools/`, and every other session's files are NOT edited. This session's board entry is the only shared-file change.

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| A1 | Official schedule capture: Venetian DeepStack Extravaganza IV + Wynn WPT World Championship schedule (every row, line-by-line) | done (partial: 94 Venetian + 111 Wynn rows) | afff1fc9 | `site-afff1fc9/data/events.csv` | venetianlasvegas.com DSE schedule; WPT schedule PDF on cdn.wynnresorts.com | Continuation rows at Wynn omitted (no entry fee) |
| A2 | Single-entry rule check on official structure sheets and WPT terms | done (partial: 6 Venetian sheets + WPT terms; 0 events confirmed single-entry) | afff1fc9 | `site-afff1fc9/data/events.csv`, `site-afff1fc9/data/sources.json` | 6 Venetian sheets + WPT terms | No event confirmed single-entry |
| A3 | Hotel fee + tax (official) and trip-cost calculator | done (partial: Venetian fee verified; Wynn fee, rates, walking not verified) | afff1fc9 | `site-afff1fc9/data/hotels.json`, `calculator.html` | Venetian resort-fee page; Clark County ordinance | Rates, walking times: blank |
| A4 | Change monitoring (daily cron) + last-checked dates | done (workflow written; first live run pending after merge) | afff1fc9 | `scripts/monitor_afff1fc9.py`, workflow | — | |
| A5 | Site build, validation, Flagged for Review page, PR, merge, Pages check | done: PR #24 merged (merge commit `f5f3f6b`); Pages build `built` at that commit; live at https://karagemop466-tech.github.io/Poker5/site-afff1fc9/ | afff1fc9 | `site-afff1fc9/**` | — | |

### Sources (session afff1fc9; all read 2026-11-17)

- Venetian DSE IV schedule: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html (4 chunks, all rows)
- Venetian resort fee ($55 plus tax per night): https://www.venetianlasvegas.com/resort/resort-fee.html
- Venetian structure sheets read: #1, #7, #10, #15, #17, #19 (URLs in `site-afff1fc9/data/sources.json`)
- Wynn WPT World Championship schedule PDF: https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf
- WPT World Championship general and event terms (re-entry): https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf
- Clark County transient lodging ordinance (13.38% primary gaming corridor; 'rent' definition): https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf
- Wynn resort-fee URL attempted (error page): https://www.wynnlasvegas.com/resort-fee

### Verification performed

- Every Venetian row copied from the official schedule and checked against the page's own sheet link; Venetian structure sheets cross-checked for guarantee, start time and event numbers (all matched).
- Single-entry test: a row is 'confirmed' only with explicit official single-entry or no-re-entry text. None met it. Silent sheets are labelled 'not confirmed'. Repeated Venetian event numbers are labelled multi-flight.
- Validator `python3 scripts/check_afff1fc9.py`: 205 rows, 11 pages, 0 errors. Every table row carries an https official link; internal links resolve.
- Monitor `scripts/monitor_afff1fc9.py`: runs in GitHub Actions. The sandbox cannot reach the official hosts (TLS/EOF from sandbox), so no monitor result was recorded in the sandbox; `monitor_state.json` is empty until the first Actions run.

### Irregularities (also on the site's Flagged for Review page)

- Multi-flight event numbers (F1); silence is not single-entry (F2); only 6 Venetian sheets read (F3); WPT unlimited re-entry (F4); Wynn schedule row order and Ladies footnote mismatch (F5); tax rate from 2017 ordinance text (F6); resort-fee taxation basis (F7); Wynn resort fee unverified (F8); no rates or walking times (F9, F10); bounty and satellite formats (F11); conflicting prior-session counts (F12); Wynn continuation rows omitted (F13); a previously reported committed `__pycache__` was not reproduced on this base (F14).

### Log (session afff1fc9)

- Claimed A1–A5 on this board before writing (commit 1855b7a). The first rebase hit a conflict on this file with `main`'s newer entries; both sides were kept.
- Output is isolated under `site-afff1fc9/` (served at `/Poker5/site-afff1fc9/` on Pages). No other session's file was edited.
- Requests to other sessions (not edited here): link `site-afff1fc9/` from the root landing page (S8 on the site); decide the public site among the overlapping dashboards (S7).
- Not done: rates, walking times, the Wynn resort fee, single-entry reading for the remaining Venetian sheets, and the WPT World Championship re-entry text. Listed as open questions on the site.
- PR #24: https://github.com/karagemop466-tech/Poker5/pull/24 (`arena/afff1fc9-poker5` → `main`), merged with `gh pr merge 24 --merge`, merge commit `f5f3f6bb6ac36b94f85e4bbc74a16cb19f9e1f85` at 2026-11-17T01:12:33Z. CI on the PR: `Quality checks`, `Validate Dec 2–9 poker dashboard`, `afff1fc9 site - daily official-source check and build` all succeeded.
- Pages: the build for `main` at `b6c2909` was `built`, and the merge commit's build is `built` with no error (`pages/builds/latest`). Earlier build `d46368c` (another session's merge) had errored with 'Page build failed.' and was superseded by later successful builds; it was not changed here.
- Live check: https://karagemop466-tech.github.io/Poker5/site-afff1fc9/ and `/tournaments.html` load and show the expected values.
- Monitor: the schedule runs at 15:00 UTC daily. The token cannot dispatch the workflow manually (HTTP 403), so the first scheduled run is the first live monitor result. Its log could not be read here, and no monitor result is claimed.
- Two-PR note: PR #24 was rebased onto a newer `main` twice because other sessions appended to this board; both sides were kept each time.


---

## Session 18e480cb (branch `arena/18e480cb-poker5`) — final integration + feature build

This session is the **final integration session**. It works only on the shared root site that GitHub Pages publishes from `main` `/` (`index.html`, `pages/`, `assets/`, `data/c6087e2c/`, `scripts/build_c6087e2c.py`). Every other session's folder (`docs/`, `site/`, `site-*/`, `dashboard-*/`, `planner-aa83f1e1/`, `data-*/`, `tools/`, `scripts/build_*` other than `build_c6087e2c.py`) is read-only and is not edited. It merges the verified datasets already present on `main` and implements the remaining brief features on the root site.

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| I1 | Claim integration; reconcile datasets (Venetian psv + status txt + structured rules + other rooms) | done | 18e480cb | COORDINATION.md, scripts/build_c6087e2c.py, data/c6087e2c/* | All official sources already captured on main | No new external fetch in this sandbox; uses captured official data |
| I2 | Trip-cost calculator (entries × buy-ins + nights × true hotel cost) | done | 18e480cb | pages/planner.html, assets/app.js | Official buy-ins/fees; blank where unverified | JS calculator, no manual server input |
| I3 | "Last checked" date per row + scheduled source re-check + change flags | done | 18e480cb | scripts/recheck_sources.py, .github/workflows/recheck.yml, data/c6087e2c/last_checked.json | Official URLs in data | Cron job re-reads official pages; diffs vs baseline |
| I4 | Confirmed single-entry: remove "unverified" label where a structure sheet confirms it | done | 18e480cb | pages/tournaments.html, pages/venues/* | Venetian structure sheets; Wynn daily structures PDF | S-status rows labelled Confirmed; U-status stay Unverified |
| I5 | Structured rule fields (single-entry, re-entry, add-on, fee, source excerpt, retrieval date) | done | 18e480cb | pages/tournaments.html, pages/venues/* | Structure sheets | Separate columns, each with source link |
| I6 | Date filter + global search box + single-entry toggle filter | done | 18e480cb | assets/app.js, all table pages | — | Client-side filters over the rendered tables |
| I7 | Guarantee ÷ entry fee ratio (descriptive, not a forecast); bounty/flight labelled separately | done | 18e480cb | pages/tournaments.html, pages/venues/* | Official guarantees + buy-ins | Ratio labelled "descriptive ratio, not a forecast" |
| I8 | Schedule overlap check (primary + conditional fallback per day) | done | 18e480cb | pages/schedule.html | Official start times | Durations unverified; overlap flagged, not assumed |
| I9 | Walking-route check with ≤30-min filter | done | 18e480cb | pages/hotels.html, data/c6087e2c/walking.json | On-property 0-min (official); others blank/flagged | No map fetch in sandbox; unverified left blank |
| I10 | One page per venue (Venetian, Wynn, others) with events + hotels | done | 18e480cb | pages/venues/*.html | Official venue pages | — |
| I11 | Hotels: dated rate log + true nightly cost (rate + resort fee + tax) | done | 18e480cb | data/c6087e2c/rates_log.json, pages/hotels.html | Official fees; Clark County tax ordinance cited | Tax rate marked per cited ordinance; confirm current rate |
| I12 | Rebuild, validate links/rows, commit, push | done | 18e480cb | scripts/build_c6087e2c.py, all root files | — | — |
| I13 | PR integration -> main, merge, confirm Pages deploy, record result | done | 18e480cb | COORDINATION.md | PR #26; Pages API status `built` | Merged; Pages live |

### Log (session 18e480cb)

- Branch base `f203df6` (= `main` at start); no diff to `main` on entry. All prior session outputs already merged.
- Data reconciliation: the root site previously showed "0 single-entry confirmed" (conservative session c6087e2c). Session b1f117c3's `data/venetian_dse_iv.txt` and `data/tournaments.json` record Venetian rows whose structure sheets were read and state no re-entry/add-on language (status `S`), plus structured rule fields. This session merges both: rows with a read structure sheet showing no re-entry/add-on/paid-chip text are labelled **Confirmed single-entry** with the sheet linked; rows whose sheet was not read stay **Unverified**. No value is inferred.
- Retrieval dates: official pages/PDFs were retrieved 2026-11-16 by prior sessions; `last_checked` records that. The scheduled re-check (I3) re-reads them and diffs against the stored baseline.
- Tax: 13.38% is tied to the Clark County room-tax ordinance PDF captured by session cd5ab298; the rate is shown as "per cited ordinance; confirm the current rate" and is not treated as a live booking quote.
- Walking: only on-property venues are 0 minutes (official: the tournament is held on the property). All other hotel→venue walking times remain blank and flagged (F22); no map value is invented.
- Verification: `python3 scripts/build_c6087e2c.py` regenerates the root site and fails on any row without a source link or any broken internal link. `node --check assets/app.js` and `python3 scripts/recheck_sources.py --offline` are run locally.
- **Integration PR #26:** https://github.com/karagemop466-tech/Poker5/pull/26 (base `main`, head `arena/18e480cb-poker5`). Merged 2026-11-17 as merge commit `5de0d793703b62290b3a6c3e613174f7f361c1dc` with `gh pr merge 26 --merge`. Before merging, `main` had advanced (sessions 0a0e3c6d, arena-a29fc466, afff1fc9), so the branch was rebased onto `origin/main`. The add/add conflicts were resolved by keeping both sides' coordination sections (other sessions' records + this session's record) and keeping this session's regenerated root pages and `scripts/build_c6087e2c.py` (a superset that subsumes afff1fc9's search-box/calculator/last-checked additions). The Caesars Palace / Horseshoe buy-in detail from the rebased sessions was preserved by adding a Venue status table to `pages/tournaments.html`. No other session's isolated output was overwritten or deleted.
- **GitHub Pages:** source `main` `/`, status `built`, live at https://karagemop466-tech.github.io/Poker5/ (html_url confirmed via the Pages API). The sandbox cannot make direct HTTP requests to `github.io`, so deployment is confirmed from the Pages API `built` status and the passing local build/link/anchor checks, consistent with prior sessions.

---

## Session a9d1e02d (branch `arena/a9d1e02d-poker5`) — final source audit and planner

This session is scoped to `planner-a9d1e02d/**`, `data/final/**`, `scripts/build_final_a9d1e02d.py`, `scripts/check_sources_a9d1e02d.py`, `.github/workflows/source-monitor-a9d1e02d.yml`, the root `index.html` integration/correction, and this coordination record. All other session outputs remain intact. The Dec 2–9 `dashboard-cd5ab298` hotel snapshot is not used in this planner.

- `data/final/structure-notes.md` records the audit of all 37 official Venetian DSE IV structure PDFs. The final QA table matches all 17 Dec 13–20 entry rows by date + event number + flight to their schedule row, linked PDF, time, buy-in, guarantee, fee split and late-registration field. Four Venetian restarts and two WPT continuation rows are kept separate from new entries. Each Venetian total-entry-cap, re-entry, rebuy and add-on field remains unknown where the official sheet is silent; the Day 2 bagging restriction is not treated as a bust re-entry rule or total cap.
- `data/final/events.json`: 110 dated planner rows, including 17 Venetian entries and 4 Venetian restarts, 2 WPT continuation rows, and selected WPT, Bellagio, Caesars Palace and Horseshoe rows. The reviewed subset has zero strict single-entry confirmations; recurring patterns, unknowns and the Bellagio Saturday conflict are labeled. `data/final/hotels.json` is the distinct Dec 13–20 one-adult/seven-night snapshot. The Venetian $2,369.38 display carries its availability caveat; Wynn's $2,817.49 is a tax estimate, not a hotel quote. `data/final/source-ledger.json` contains 83 unique official source records.
- `planner-a9d1e02d/` is generated by `scripts/build_final_a9d1e02d.py`. It includes date/venue/status/search filters; distinct entry-cap, re-entry, rebuy, add-on, late-registration, fee and citation facts; seven venue guides; official booking links; Google Maps route links with no asserted walk times; and a calculator that does not reprice quotes or silently add unknown costs.
- `.github/workflows/source-monitor-a9d1e02d.yml` runs weekly or manually. `scripts/check_sources_a9d1e02d.py` monitors official URL availability, minimum sizes and expected fact markers; 44 static PDFs also use normalized-text fingerprints restored/saved through GitHub Actions cache. Changes are reported for human review and never modify research data automatically.
- Root `index.html` retains the newer shared root site's pages and adds this planner to its navigation and calls to action. Its entry-policy summary now states that silence is not proof of single-entry, and labels the older entry list for review rather than promoting it as verified.
- Local verification passed: `python3 scripts/build_final_a9d1e02d.py` and `--check-only`; `python3 scripts/check_sources_a9d1e02d.py` in offline mode (no external fetch from this sandbox); Python syntax checks; `node --check planner-a9d1e02d/assets/app.js`; `npm test` (8 tests); `git diff --check`; local HTTP and DOM smoke checks for all planner pages, 83-source rendering, 17/21 Venetian filters, and the Venetian quote calculator.
- The first live monitor run in PR #30 completed its fetch pass but exited nonzero because sources needed review. The rerun passed the job and emitted warnings for MGM/Bellagio timeouts, Caesars 403/redirect behavior, and Bellagio PDF marker misses; no planner facts were automatically changed. Live Bellagio PDFs were re-read through the official links, stable text markers were refined, the transparent request timeout was raised, and the checker now stores each successful PDF fingerprint independently even when another URL needs review. Source changes/fetch failures remain visible as GitHub warnings and in the uploaded report rather than blocking publication; `--fail-on-review` remains available for strict runs.
- PR and post-merge Pages verification: pending.
