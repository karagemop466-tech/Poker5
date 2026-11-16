# Coordination Board — Poker5

Shared task board for the Las Vegas poker tournament & hotel research + GitHub Pages site project.

## Conventions
- Claim a task by writing your session ID and file scope, then commit and push the claim immediately.
- Never start a task another session has claimed.
- Keep scopes non-overlapping: each session works on its own branch/worktree and edits only files in its claimed scope.
- If a task requires changing a file owned by another session, log the request here instead of editing it.
- Make small, frequent commits; run `git pull --rebase` before every push.
- When a task is finished, record sources, verification performed, and irregularities here and mark it done.
- Shared outputs (table data, index/navigation) are changed only by the final integration session once all other tasks are done.

## Session ID (this session)
- Session ID: `session-1` (branch `arena/3dfaf2a5-poker5`, branched from `0ba2e556`)

## Tasks

| # | Task | Status | Owner | File scope | Sources | Verification | Irregularities |
|---|------|--------|-------|------------|---------|--------------|----------------|
| 1 | Research live upcoming poker tournaments near Las Vegas Strip (official sources) | in progress | session-1 | `data/tournaments.md`, `tournaments.html` | wsop.com, caesars.com, wynnlasvegas.com, venetianlasvegas.com, aria.com, bellagio.com, mgmresorts.com | Pending official-site checks | Pending |
| 2 | Research hotels within walking distance of tournaments (official hotel sites) | unclaimed | session-1 | `data/hotels.md`, `hotels.html` | wynnlasvegas.com, venetianlasvegas.com, aria.com, bellagio.com, mgmresorts.com, caesars.com | Pending | Pending |
| 3 | Build executive summary | unclaimed | session-1 | `executive-summary.html` | (derived from tasks 1-2) | Pending | Pending |
| 4 | Build suggestions section (site improvement suggestions) | unclaimed | session-1 | `suggestions.html` | n/a | Pending | Pending |
| 5 | Build questions/info/answers list (pre-decision items) | unclaimed | session-1 | `questions.html` | n/a | Pending | Pending |
| 6 | Build Flagged for Review page (irregularities + unverified items) | unclaimed | session-1 | `flagged-for-review.html` | (from tasks 1-2) | Pending | Pending |
| 7 | Build GitHub Pages site: landing page + subpages, clean dashboard UI, tables, analysis | unclaimed | session-1 | `index.html`, `*.html`, `assets/css/*.css`, `assets/js/*.js` | n/a | Build check + broken-link check | Pending |
| 8 | Verify all table rows line by line against official sources; blank + flag unverified | unclaimed | session-1 | All data files + pages | Official sources listed above | Pending | Pending |
| 9 | Final integration: merge branches, re-verify combined data, confirm build with no broken links, publish GitHub Pages | unclaimed | session-1 | All | All | Pending | Pending |
| 10 | Create PR from integration branch to main, merge, confirm Pages deploys, record PR link + merge result here | unclaimed | session-1 | `COORDINATION.md` | n/a | Pending | Pending |

## Notes
- Today's date (user local, UTC): 2026-11-16. Focus research on tournaments on/after this date.
- No manual user input: work autonomously, verify from official sources, no hallucinations.
- If a value cannot be confirmed from an official source, leave it blank and mark it "unverified".
- The repo currently contains only `README.md` (`# Poker5`).
