# Coordination — Poker5

Shared task board for agent sessions working on this repo.

## Rules
- Claim a task by writing your session ID and file scope, then commit and push immediately.
- Never start a task another session has claimed.
- Keep scopes non-overlapping: each session edits only the files in its claimed scope.
- If a task requires changing a file owned by another session, log the request here instead of editing it.
- Make small, frequent commits, and run `git pull --rebase` before every push.
- On merge conflict, stop, resolve without discarding other session's work, log what happened.
- When finished, record sources, verification performed, and irregularities here and mark done.
- Never mark verified without checking against an official source; link that source.
- Shared outputs (table data, index, navigation) changed only by final integration session.
- If a session crashes or its claim is >60 minutes old with no commits, another session may take over and note the handoff.

## Session
- Session ID: `053f694f`
- Working branch: `arena/053f694f-poker5` (fixed for this session by Arena; the `session-<id>/<task>` naming in the rules above is not used here because the branch name is fixed)
- Base: `main` @ `0ba2e55`
- Note: sibling branches `arena/2ed7df1a`, `arena/3dfaf2a5`, `arena/66cdf731`, `arena/9c91bba7`, `arena/aa83f1e1`, `arena/b50aa7f5`, `arena/cd5ab298` also claim research/site tasks. This session did not edit them. Overlap is logged under Flagged for Review.

## Tasks

| Task | Status | Owner | File scope | Sources | Verification | Irregularities |
|------|--------|-------|------------|---------|--------------|----------------|
| T1: Create COORDINATION.md and claim tasks | done | 053f694f | COORDINATION.md | — | — | Sibling branches overlap; see Flagged |
| T2: Research single-entry tournaments near Strip | in progress (partial) | 053f694f | data/tournaments.json, data/tournaments.md | Venetian DSE IV schedule + structure sheets; Wynn WPT and daily PDFs; Caesars 2026 flyer; Bellagio PDFs | Structure sheets read line-by-line for the rows in data; see Flagged | Multiple; see Flagged |
| T3: Research hotels within 30-min walk | in progress (partial) | 053f694f | data/hotels.json, data/hotels.md | Venetian resort-fee page; Wynn official offer terms | Resort fee only; no official rates or walk times | Rates and walk times not verified; see Flagged |
| T4: Executive summary | done | 053f694f | summary.html | — | Reviewed against data files | — |
| T5: Suggestions section | done | 053f694f | summary.html | — | — | — |
| T6: Questions / missing info | done | 053f694f | summary.html | — | — | — |
| T7: Build GitHub Pages site | done | 053f694f | index.html, tournaments.html, hotels.html, schedule.html, dashboard.html, summary.html, flagged.html, assets/, scripts/build_site.py | generated from data/*.json | Build script output checked | — |
| T8: PR, merge, Pages deploy | in progress | 053f694f | — | PR #8: https://github.com/karagemop466-tech/Poker5/pull/8 | pending | pending |
| T9: Record PR link and merge result | in progress | 053f694f | COORDINATION.md | PR #8 | pending | pending |

## Integration
- PR: https://github.com/karagemop466-tech/Poker5/pull/8 (base `main`, head `arena/053f694f-poker5`)
- Merge result: pending (recorded after merge)

## Flagged for Review
See flagged.html on the published site for the full list. Summary of open items:
- Venetian event-number mapping conflicts (event 01 on two sheets; PKO event 08 vs. schedule numbering).
- Bellagio Saturday PDF: buy-in conflict ($1,100 heading vs $600 rule), stale date (9/13/26).
- Wynn daily poster is a 2025 asset; validity for 2026 unconfirmed.
- Resorts World poker room reported closed (third-party only); not confirmed.
- Hotel rates and walk times not verified; no true nightly cost computed.
