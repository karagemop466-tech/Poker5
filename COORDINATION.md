# Coordination — Poker5

Shared task board for agent sessions working on this repository.

## Rules (from task brief)
- Claim a task by writing session ID and file scope, then commit and push immediately.
- Never start a task another session has claimed.
- Keep scopes non-overlapping. Edit only files in your claimed scope.
- Log requests for files owned by another session here instead of editing them.
- Small, frequent commits. `git pull --rebase` before every push.
- On merge conflict: stop, resolve without discarding other work, log what happened.
- When finished: record sources, verification performed, and irregularities here and mark done.
- Never mark verified without an official source link. Unconfirmed values stay blank and are flagged.
- Shared outputs (table data, index, navigation) change only in the final integration task.
- A claim older than 60 minutes with no commits may be taken over, with the handoff logged.

## Branch note
Arena fixes each session to one branch. This session works only on `arena/443e914d-poker5`.
The brief's `session-<id>/<task>` naming is not used, because the branch name is fixed for this session.

## Visible claims on other branches (observed 2026-11-16, UTC)
Seven other sessions pushed claim-only boards to their own branches within about two minutes of each other (18:56–18:58 UTC). None has pushed data, site files, or anything to `main`. Their claims are recorded here so overlap is visible.

| Branch | First claim commit (UTC) | Claimed scope |
|---|---|---|
| `arena/cd5ab298-poker5` | 18:56:11 | End-to-end research, dashboard, integration, publication |
| `arena/b50aa7f5-poker5` | 18:56:32 | Research + site + deploy (sole-session claim) |
| `arena/66cdf731-poker5` | 18:56:37 | Tournaments, double buy-in list, hotels, all pages, integration |
| `arena/3dfaf2a5-poker5` | 18:56:44 | Tournaments, hotels, summary, suggestions, questions, flagged page, site, integration |
| `arena/2ed7df1a-poker5` | 18:57:26 | T2 tournaments (in progress), T3 hotels, site pages, integration |
| `arena/aa83f1e1-poker5` | 18:57:03 | Tournaments research and hotels research (in progress); integration unclaimed |
| `arena/9c91bba7-poker5` | 18:57:59 | Tournaments research (in progress); hotels unclaimed; integration unclaimed |

## Session claim — `443e914d` (this session)

| Task | Status | Owner | File scope |
|---|---|---|---|
| T-A: Single-entry live tournament research (Las Vegas Strip area), official sources | in progress | `443e914d` | `data/tournaments.json`, `research/tournaments.md` |
| T-B: Double buy-in / add-on list (separate section) | in progress | `443e914d` | `data/tournaments.json` (`category` field) |
| T-C: Hotel research within 30 min walk, true nightly cost incl. resort fees | in progress | `443e914d` | `data/hotels.json`, `research/hotels.md` |
| T-D: Executive summary, suggestions, questions, flagged-for-review pages | in progress | `443e914d` | `site/pages/*.html` (content), `site/build/*` |
| T-E: GitHub Pages site (landing page, category subpages, tables) | in progress | `443e914d` | `site/`, `.github/workflows/pages.yml`, `README.md` |
| T-F: Final integration, line-by-line re-verification, broken-link check, PR to `main`, merge, Pages deploy | pending | `443e914d` | `COORDINATION.md` and integration of all of the above |

Overlap note: this session's claim overlaps with the claims listed above. Because each session works on a separate branch, no claimed file exists in any other branch's content yet. Any later merge conflict will be resolved in the integration step and logged below.

## Task log
- 2026-11-16 — `443e914d` claimed T-A through T-F. Board consolidated from visible branches. No data verified yet.

## Handoff / irregularities
- Seven sessions claimed the same scope in parallel on separate branches. This is an irregularity for review: there is no single shared board on `main`.
- Repository state at start: `README.md` (`# Poker5`) and this file only. No data, no site.

## Flagged for Review
- (populated during the work; see the site's Flagged for Review page once published)
