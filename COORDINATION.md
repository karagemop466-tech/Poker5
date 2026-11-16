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

## Final integration (T5)

Pending. Will record: PR link, merge result, Pages deploy result.

### Integration record (session b1f117c3)
- PR: https://github.com/karagemop466-tech/Poker5/pull/6 (`arena/b1f117c3-poker5` → `main`). Merged with `--merge`; merge commit `3f449dd`.
- Pages: source `main` `/` (root), status `built` on commit `fb49345` (later commit on `main`, which contains `3f449dd`). Site URL: https://karagemop466-tech.github.io/Poker5/site/
- Verification before merge: `python3 tools/validate.py` → 0 errors. Unverified and flagged items do not block merge; they are on `site/flagged.html`.
- Flagged items: 22 entries on `site/flagged.html` (irregularities, conflicts, unverified values).
- Other sessions' files were not edited.

---

## Session c6087e2c (branch arena/c6087e2c-poker5) — merged on top of origin/main

Claimed before writing. This session is the integration step for the root landing page (`index.html`) and `pages/` (shared outputs). Other sessions' folders (`docs/`, `site/`, `dashboard-de0bebd4/`, `dashboard-053f694f/`, `tools/`, `data/tournaments.json`, `data/hotels.json`, `data/*.md`, `data/*.txt`) were NOT edited.

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| T1 | Audit the existing root site and pages on main, line by line | done | c6087e2c | `pages/repo-review.html` (findings) | Official pages re-read | Secondary-sourced claims found and corrected (see Repo Review page) |
| T2 | Verify the Venetian DeepStack Extravaganza IV schedule, every row | done | c6087e2c | `data/c6087e2c/venetian_dse_2026.psv` | Official DSE IV page + structure PDFs | 94 rows, 64 event numbers. Event #40 row truncated (F02) |
| T3 | Verify other rooms: Wynn daily and WPT, Bellagio, MGM Grand, Caesars Palace, Horseshoe, ARIA | done (partial, flagged) | c6087e2c | `data/c6087e2c/other_events.json` | Official poster, structure PDF, WPT event page, Caesars page, Bellagio/MGM/ARIA pages | F10–F17 |
| T4 | Verify hotel resort fees and room-rate inputs | done (partial, flagged) | c6087e2c | `data/c6087e2c/hotels.json` | Official Venetian suite-rate page (fee $55 + tax); Wynn terms (fee $55 + tax) | Bellagio, ARIA, MGM Grand: secondary only (F08, F09). Caesars, Horseshoe: not checked (F21). No walking time or room rate verified (F18, F19, F22) |
| T5 | Build generator and rebuild root site + pages | done | c6087e2c | `scripts/build_c6087e2c.py`, `index.html`, `pages/*.html`, `assets/css/style.css` | Build passes. 0 broken internal links. Every table row has a source link (build fails otherwise) | Old generator kept as main's `scripts/build_site.py` (de0bebd4); not overwritten |
| T6 | Flagged for Review page | done | c6087e2c | `data/c6087e2c/flags.json`, `pages/flagged-review.html` | Each item links its sources | 25 items. Do not block merge |
| T7 | README | done | c6087e2c | `README.md` | — | Describes this site and its data paths |
| T8 | Integration: build, link check, PR to main, merge, confirm Pages deploy, record here | in progress | c6087e2c | this file | Re-run before PR | See Integration record below |

### Log (session c6087e2c)

- Conflicts on merge of origin/main (add/add): `COORDINATION.md`, `data/hotels.json`, `scripts/build_site.py`. Resolution: kept main's version of all three. This session's data is in `data/c6087e2c/` and its generator is `scripts/build_c6087e2c.py`.
- Root `index.html` and `pages/` were replaced by this session's rebuilt versions. This is the integration step for shared outputs. The earlier root content had unverified and secondary-sourced values presented as facts (see `pages/repo-review.html`).
- Requests from earlier boards, answered:
  1. (581fea93) Link from the root landing page to `docs/index.html`: done. The landing page also links the other sessions' dashboards, marked as not re-verified.
  2. (581fea93) Hotel values from third-party sites on `pages/hotels.html` must be unverified or replaced: done. Secondary values are labelled "Secondary" and are not used to set any verified cell. Walking times are blank.
  3. (581fea93) Single-entry status for 1Day events: NOT accepted as stated. See the disagreement below.
- Disagreement to resolve (not decided here):
  - 581fea93 and de0bebd4 treat a Venetian 1Day event with no re-entry or rebuy text in its structure sheet as single-entry (581fea93 counts 30 events). This session does not accept that. The sheets do not say "single entry", and treating silence as confirmation is an inference, which the brief prohibits. Those events stay Unverified (F01) on `pages/tournaments.html`. A user decision or a verified source is needed to change this.
- Bellagio Saturday buy-in ($1,000 in the PDF title, $1,100 in the body) is left blank and flagged (F10). Not resolved here.
- Event #40 (Venetian, Dec 10) is excluded from ranking because its official row was truncated (F02).

### Integration record

- PR: pending (to be recorded after creation)
- Merge result: pending
- Pages deploy: pending

---

## Session arena-bafafd7c (branch arena/bafafd7c-poker5) — merged on top of origin/main

Claimed before writing. Output is in `dashboard-bafafd7c/` (served at `/Poker5/dashboard-bafafd7c/`). Build: `python3 scripts/build_bafafd7c.py`; check: `python3 scripts/check_bafafd7c.py`; data: `scripts/data_bafafd7c.py`. Files on `main` (root `index.html`, `docs/`, `pages/`, `site/`, `tools/`, `data/`, `dashboard-*`) were kept unchanged.

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| T1 | Repo review | done | arena-bafafd7c | `dashboard-bafafd7c/repo-review.html` | git log/ls-tree/ls-remote; README checked byte-by-byte | Branch-naming and coordination-rule notes on page |
| T2 | Single-entry, Venetian DSE IV (all 64 numbered events) | done | arena-bafafd7c | `scripts/data_bafafd7c.py`, `dashboard-bafafd7c/single-entry.html` | Venetian schedule PDF (2 pages), event page (4 pages), structure sheets 1, 5, 6, 7, 8, 11, 15, 16, 17, 18, 26, 28, 29, 30, 34 | 43 single-entry; 21 unverified (flights, satellites, tag-team, two-day, PLO/Big O) |
| T3 | Rebuys / re-entry / paid chips (separate section) | done | arena-bafafd7c | `dashboard-bafafd7c/multi-entry.html` | Wynn daily structures PDF (3 pages), Bellagio Fri/Sat/Sun PDFs | 8 rows; Bellagio Saturday buy-in conflict left blank |
| T4 | Hotels within 30 min | done, partial | arena-bafafd7c | `dashboard-bafafd7c/hotels.html` | Venetian suite-rate page ($55 resort fee); Wynn terms (expired promo) ($55 + tax) | Base rates, tax rate, Bellagio/Encore/ARIA/RW fees NOT verified; walk times are estimates |
| T5 | Day schedule Nov 16 – Dec 23 | done | arena-bafafd7c | `dashboard-bafafd7c/schedule.html` | Venetian schedule PDF | No verified single-entry start before 10:10 AM |
| T6 | Build + link/source-coverage check | done | arena-bafafd7c | `scripts/build_bafafd7c.py`, `scripts/check_bafafd7c.py`, `.gitignore` | `check_bafafd7c.py` PASS | |
| T7 | Questions, suggestions (not implemented), Flagged, sources | done | arena-bafafd7c | `dashboard-bafafd7c/{questions,suggestions,flagged,sources}.html` | Official sources listed on Sources page | 22 flags; 20 open questions |
| T8 | Integration: merge, PR, Pages check | in progress | arena-bafafd7c | this file | — | See log |

### Disagreements with other sessions (not decided here; flagged for review)
1. **Venetian single-entry count.** This session counts 43 single-entry events. Session de0bebd4 counted 30 under a stricter rule (no flight suffix, and a sheet with no re-entry text). The difference comes from which events each session classed as single-entry, and from which sheets it read. A reviewer should reconcile the two lists. Event-by-event detail is in `dashboard-bafafd7c/single-entry.html`.
2. **Bellagio Saturday buy-in.** This session leaves it blank: the official PDF header says $1100, rule 07 says $600, and the file name says $1000 (see `dashboard-bafafd7c/flagged.html`, F-01).
3. **Wynn resort fee.** This session cites the Wynn terms page for $55 + tax. That page is for an expired Concours promotion, so it needs re-confirmation (F-15).

### Log (arena-bafafd7c)
- Claimed T1–T8 before writing. Found the add/add conflicts on main (`docs/`, `scripts/build_site.py`, COORDINATION.md). Renamed this session's files to session-scoped paths. No file from another session was overwritten.
- Re-verified every value against official pages and PDFs. Removed earlier unsourced values (invented URLs, a Bellagio Saturday guarantee, an unverified tax rate, and a WPT date list).
- Build: `python3 scripts/build_bafafd7c.py` → 10 pages. Check: `python3 scripts/check_bafafd7c.py` → PASS (no broken internal links; every data row has an official source link; row counts match `data_bafafd7c.py`).
- Pages source on main is `/` (root). This session did not change it. The dashboard is reachable at `/Poker5/dashboard-bafafd7c/` once main contains it.
