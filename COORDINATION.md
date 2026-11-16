# Coordination - Poker5

Shared task board for the Poker5 project (Las Vegas poker tournament + hotel planner).

## Session

| Session ID | Status | Branch |
|------------|--------|--------|
| arena-poker5 | active (single session) | arena/66cdf731-poker5 |

## Tasks

| # | Task | Status | Owner | Files touched | Sources / verification | Notes |
|---|------|--------|-------|---------------|------------------------|-------|
| 1 | Research live upcoming Las Vegas Strip poker tournaments (single entry only) | in progress | arena-poker5 | data/tournaments.md | Official casino/poker room sites | Verify each row against official source; blank + flag if unverified |
| 2 | Research double buy-in / add-on tournaments (separate section) | unclaimed | arena-poker5 | data/tournaments-double.md | Official casino/poker room sites | Separate from single-entry |
| 3 | Research Las Vegas hotels within walking distance (30 min) of tournaments | unclaimed | arena-poker5 | data/hotels.md | Official hotel sites | True cost/night incl. resort fees; quality > cost > distance |
| 4 | Build executive summary | unclaimed | arena-poker5 | pages/executive-summary.html | — | |
| 5 | Build suggestions section (improvements + decision review) | unclaimed | arena-poker5 | pages/suggestions.html | — | |
| 6 | Build questions/information/answers needed before decisions | unclaimed | arena-poker5 | pages/questions.html | — | |
| 7 | Build Flagged for Review page (irregularities + unverified items) | unclaimed | arena-poker5 | pages/flagged-review.html | — | Links to sources |
| 8 | Build GitHub Pages site: landing page + category subpages + tables | unclaimed | arena-poker5 | index.html, pages/*.html, assets/ | — | Clean dashboard UI |
| 9 | Final integration: re-verify combined data line by line, check build + broken links | unclaimed | arena-poker5 | all | All official sources | Integration session |
| 10 | Enable GitHub Pages, deploy, confirm deploy succeeds | unclaimed | arena-poker5 | repo settings | — | Do not merge a broken site |
| 11 | Create PR integration -> main, merge, record PR link + merge result | unclaimed | arena-poker5 | COORDINATION.md | — | After deploy confirmed |

## Rules followed
- One session works this branch; scopes non-overlapping (single session here).
- Every table row must have a source link to an official site. If unconfirmed, leave blank and flag as unverified. Never infer or fill in values.
- Small, frequent commits; git pull --rebase before every push.
- Never mark verified without checking an official source and linking it.
