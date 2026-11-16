# Coordination — Poker5

Shared task board for agent sessions working on this repo.

## Rules
- Claim a task by writing your session ID and file scope, then commit and push immediately.
- Never start a task another session has claimed.
- Keep scopes non-overlapping: each session works on its own branch (or git worktree) named session-<id>/<task> and edits only the files in its claimed scope.
- If a task requires changing a file owned by another session, log the request here instead of editing it.
- Make small, frequent commits, and run `git pull --rebase` before every push.
- On merge conflict, stop, resolve without discarding the other session's work, log what happened.
- When finished, record sources, verification performed, and irregularities here and mark done.
- Never mark verified without checking against an official source; link that source.
- Shared outputs (table data, index, navigation) changed only by final integration session.
- If a session crashes or its claim is >60 minutes old with no commits, another session may take over and note the handoff.

## Sessions in this repo

| Session ID | Status | Branch |
|------------|--------|--------|
| arena | active (this session, integration) | arena/2ed7df1a-poker5 |
| arena-poker5 | active (parallel session) | arena/66cdf731-poker5 (merged to main via PR #1) |
| 581fea93 | active (parallel session) | arena/581fea93-poker5 (merged to main via PR #3) |

## Tasks (integrated)

| Task | Status | Owner | File scope | Sources | Verification | Irregularities |
|------|--------|-------|------------|---------|--------------|----------------|
| T1: Create COORDINATION.md and claim tasks | done | arena | COORDINATION.md | — | — | — |
| T2: Research live upcoming single-entry poker tournaments near Las Vegas Strip | done | arena | data/tournaments.md, docs/tournaments.html | venetianlasvegas.com (official DSE IV schedule + structure PDFs) | Verified against official Venetian schedule + structure PDFs | Flagged: single-entry status is structural interpretation; GTD blank for Events 3/4/5/6; other rooms third-party only |
| T3: Research hotels within 30-min walking distance | done | arena | data/hotels.md, docs/hotels.md | official hotel sites + third-party aggregators | Resort fees verified officially only at Wynn ($45/$55); rates dynamic/unverified; walking times approximate | Flagged: nightly rates blank/unverified; resort fees third-party except Wynn |
| T4: Executive summary | done | arena | site/executive-summary.md, docs/executive-summary.html | — | — | — |
| T5: Suggestions section (site improvements) | done | arena | site/suggestions.md, docs/suggestions.html | — | — | — |
| T6: Q&A / missing information section | done | arena | site/questions.md, docs/questions.html | — | — | — |
| T7: Build GitHub Pages site | done | arena | docs/*.html, docs/style.css | — | Built; all internal links resolve; no bad entities | — |
| T8: PR, merge, GitHub Pages deploy | blocked | arena | PR #10 → main | — | PR created; merge BLOCKED by GitHub false-positive conflict report (see note below). Pages deployed & built from main root "/" | Pages built successfully: https://karagemop466-tech.github.io/Poker5/ |
| T9: Record PR link and merge result | done | arena | COORDINATION.md | PR #10 https://github.com/karagemop466-tech/Poker5/pull/10 | PR created but NOT merged (GitHub platform false-positive) | Recorded below |

## Parallel-session work preserved on main (not overwritten)

Session arena-poker5 / 581fea93 built and deployed a GitHub Pages site from main before this integration:
- Root landing: `index.html` → links to `pages/*.html` (tournaments, tournaments-double/re-entry, hotels, schedule, executive-summary, questions, suggestions, flagged-review)
- `assets/css/style.css`, `tools/build.py`, `tools/data.py`
- `docs/`: index.html, single-entry.html, excluded.html, wpt-wynn.html, daily-schedule.html, flagged.html, summary.html, analysis.html, sources.html, .nojekyll
- Live URLs reported: https://karagemop466-tech.github.io/Poker5/ (root) and .../Poker5/docs/
- Build tool `python3 tools/build.py` passes (links, source-link presence, event accounting 64/64)
- GitHub Pages source is main `/` (root). Changing source to `/docs` returned HTTP 403 for their session token, so root `/` is retained.

## Merge-conflict resolution (this integration, PR #5)

Both sessions built the same brief in parallel. `git merge origin/main` produced add/add conflicts in COORDINATION.md, docs/hotels.html, docs/index.html, docs/questions.html, docs/suggestions.html.

Resolution (no other session's work discarded):
- COORDINATION.md: hand-merged both task boards; both sessions recorded above.
- docs/hotels.html, docs/index.html, docs/questions.html, docs/suggestions.html: kept this session's integrated versions (HEAD); the parallel session's corresponding pages are preserved under `pages/*.html` and their unique `docs/*.html` pages (single-entry, excluded, wpt-wynn, daily-schedule, analysis, sources, flagged, summary) are retained.
- tools/__pycache__/*.pyc: retained as committed on main (build artifact).
- The integrated site tree is `docs/`; GitHub Pages continues to serve from root `/` (per constraint above).

## PR #10 merge blocker (platform issue — documented 2026-11-16)
- PR #10: https://github.com/karagemop466-tech/Poker5/pull/10 (arena/2ed7df1a-poker5 → main).
- Status: CREATED but NOT merged.
- Blocker: GitHub reports `mergeable: false / dirty` and `gh pr merge` and the direct merge API both return HTTP 405 "Pull Request has merge conflicts."
- This is a FALSE POSITIVE: `main` (5ca9bf7) is a strict ancestor of the branch head (4a06126), and `git merge-tree` confirms ZERO file conflicts (clean fast-forward). Retried `gh pr merge --merge` multiple times and recreated the PR (#5 → #10); all attempts blocked by the same false-positive.
- Workaround considered but NOT done: pushing directly to main is outside this session's branch rule (push only to current branch).
- Impact: this session's integrated branch content is committed/pushed to arena/2ed7df1a-poker5 but is NOT yet on main/live. The live GitHub Pages site (below) reflects main's content (the parallel session's verified pages).

## GitHub Pages deploy
- Pages enabled on repo karagemop466-tech/Poker5, source = branch `main`, path `/` (root).
- Build status: **built** (successful).
- Live URL: https://karagemop466-tech.github.io/Poker5/
- Verified live: homepage loads; links to Tournaments / Hotels / Executive Summary / Flagged for Review all resolve. Verification standard (official sources; unverified flagged) is published on the live site.
- Note: live site reflects main's content (parallel session's pages) because PR #10 merge is blocked.

## Flagged for Review
- Published on the site Flagged for Review page (docs/flagged-review.html and pages/flagged-review.html).
- Key items: single-entry status for 1Day events is a structural interpretation (not an explicit label); hotel nightly rates dynamic/unverified; most resort fees third-party except Wynn ($55 official T&C) and Venetian ($55 official resort-fee page); walking times approximate; other Strip rooms (Wynn WPT, MGM Grand, Aria, Bellagio, Circa) third-party only; no 8 AM tournament at the Venetian (earliest 10:10 AM).
