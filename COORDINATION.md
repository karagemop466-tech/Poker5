# Coordination — Poker5

Shared task board for agent sessions working on this repo.

## Rules
- Claim a task by writing your session ID and file scope, then commit and push immediately.
- Never start a task another session has claimed.
- Keep scopes non-overlapping: each session works on its own branch (or git worktree) named session-<id>/<task> and edits only the files in its claimed scope.
- If a task requires changing a file owned by another session, log the request here instead of editing it.
- Make small, frequent commits, and run `git pull --rebase` before every push.
- On merge conflict, stop, resolve without discarding other session's work, log what happened.
- When finished, record sources, verification performed, and irregularities here and mark done.
- Never mark verified without checking against an official source; link that source.
- Shared outputs (table data, index, navigation) changed only by final integration session.
- If a session crashes or its claim is >60 minutes old with no commits, another session may take over and note the handoff.

## Session
- This session ID: arena (single session)
- Working branch: arena/2ed7df1a-poker5 (current branch, fixed per Arena)

## Tasks

| Task | Status | Owner | File scope | Sources | Verification | Irregularities |
|------|--------|-------|------------|---------|--------------|----------------|
| T1: Create COORDINATION.md and claim tasks | done | arena | COORDINATION.md | — | — | — |
| T2: Research live upcoming single-entry poker tournaments near Las Vegas Strip | done | arena | data/tournaments.md | venetianlasvegas.com (official DSE IV schedule + structure PDFs) | Verified against official Venetian schedule + structure PDFs (see irregularities in flagged-review.md) | Flagged: single-entry status is structural interpretation; GTD blank for Events 3/4/5/6; other rooms third-party only |
| T3: Research hotels within 30-min walking distance | done | arena | data/hotels.md | official hotel sites + third-party aggregators | Resort fees verified officially only at Wynn ($45/$55); rates dynamic/unverified; walking times approximate | Flagged: nightly rates blank/unverified; resort fees third-party except Wynn |
| T4: Executive summary | done | arena | site/executive-summary.md | — | — | — |
| T5: Suggestions section (site improvements) | done | arena | site/suggestions.md | — | — | — |
| T6: Q&A / missing information section | done | arena | site/questions.md | — | — | — |
| T7: Build GitHub Pages site | done | arena | docs/*.html, docs/style.css | — | Built; all internal links resolve; no bad entities | — |
| T8: PR, merge, GitHub Pages deploy | in progress | arena | — | — | pending | — |
| T9: Record PR link and merge result | unclaimed | arena | COORDINATION.md | — | pending | — |

## Flagged for Review
- (none yet)
