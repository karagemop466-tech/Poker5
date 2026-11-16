# Coordination - Poker5

Shared task board for the Poker5 project (Las Vegas Strip poker tournament and hotel planner).
Live site: https://karagemop466-tech.github.io/Poker5/

## Sessions

| Session ID | Branch | Status | Notes |
|---|---|---|---|
| arena-poker5 (66cdf731) | arena/66cdf731-poker5 | done, merged to main (PR #1, commit 47b2e73) | Earlier session. Its site content was audited in this session and found to contain unverified and secondary-source values. Rebuilt here. See Repo Review. |
| c6087e2c | arena/c6087e2c-poker5 | active (single session) | This session. Rebuilt the site from official data and reopened the earlier board's items 9-11. |

## Task board (session c6087e2c)

| # | Task | Status | Owner | Claimed | Files touched | Sources / verification | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Audit the existing site on main, line by line | done | c6087e2c | 2026-11-16 | pages/*.html, index.html, README.md | Official pages re-read; each claim checked | Findings on pages/repo-review.html |
| 2 | Verify the Venetian DeepStack Extravaganza IV schedule (every row) | done | c6087e2c | 2026-11-16 | data/venetian_dse_2026.psv | Official DSE IV page and structure PDFs | Event #40 row truncated in capture (F02) |
| 3 | Verify other rooms: Wynn daily and WPT, Bellagio, MGM Grand, Caesars Palace and Horseshoe, ARIA | done | c6087e2c | 2026-11-16 | data/other_events.json | Official poster, structures PDF, WPT event page, Caesars page, Bellagio/MGM/ARIA pages | Partial values flagged (F10-F17) |
| 4 | Verify hotel resort fees and room-rate inputs | done | c6087e2c | 2026-11-16 | data/hotels.json | Official Venetian suite-rate page; Wynn terms page | Bellagio, ARIA, MGM Grand: secondary only (F08, F09). Caesars, Horseshoe: not checked (F21) |
| 5 | Build the generator and the site | done | c6087e2c | 2026-11-16 | scripts/build_site.py, index.html, pages/*.html, assets/css/style.css | Build passes. 0 broken internal links. Every table row has a source link | Generator enforces the source-link rule |
| 6 | Flagged for Review page | done | c6087e2c | 2026-11-16 | data/flags.json, pages/flagged-review.html | Each item links its sources | 25 items; they do not block merge |
| 7 | README and this board | done | c6087e2c | 2026-11-16 | README.md, COORDINATION.md | - | - |
| 8 | Final integration: rebase on main, build, PR to main, merge, confirm Pages deploy, record PR and merge here | in progress | c6087e2c | 2026-11-16 | all | Build and link check re-run before the PR | See Integration record below |
| 9 | (reopened from earlier board) Single-entry status verification | blocked: needs official confirmation | c6087e2c | 2026-11-16 | data/*.json | No official source states single-entry for any event | Left as Unverified (F01). Not a merge blocker |
| 10 | (reopened from earlier board) Deploy and confirm the Pages build | in progress | c6087e2c | 2026-11-16 | repo settings | gh api repos/.../pages/builds/latest | Confirm after merge |
| 11 | (reopened from earlier board) Create PR integration to main, merge, record | in progress | c6087e2c | 2026-11-16 | COORDINATION.md | - | Merge result recorded below |

## Rules followed

- Every table value is taken from an official source or is left blank and flagged. Nothing is inferred.
- Secondary sources are used only where labelled "Secondary", and never to set a verified value.
- Every table row carries a source link. The build fails if a row has none.
- git pull --rebase before every push.
- Stale-claim rule (60 minutes): no claim was left open across the session; all claims were worked in this session.

## Conflicts log

- 2026-11-16: origin/main advanced from 0ba2e55 to 47b2e73 (PR #1 from the earlier session) before this session's first push. Resolved by fast-forwarding to origin/main, then replacing the earlier site content after the audit (see Repo Review).
- Branch naming: the coordination protocol asks for session-<id>/<task> branches. This session's instructions restrict all work to arena/c6087e2c-poker5 and forbid creating other branches, so every task runs on that branch. No parallel claims existed, so there were no scope conflicts.

## Integration record

- PR: pending (to be recorded after creation)
- Merge result: pending
- Pages deploy: pending
