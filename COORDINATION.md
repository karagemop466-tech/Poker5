# Coordination board

Last updated: 2026-11-16 (UTC)

| Task | Status | Owner/session | File scope |
|---|---|---|---|
| Verify live/upcoming single-entry poker tournaments from official room/operator sources; record source-by-source findings and flags | complete — no strict single-entry event confirmed; unresolved terms flagged | `arena/aa83f1e1-poker5` | `research/tournaments.md`, `data/tournaments.json` |
| Verify nearby hotel walking distance and official date-specific room/resort-fee pricing; record unknowns rather than infer | complete — Venetian quote captured; Wynn total and official walking times remain unverified | `arena/aa83f1e1-poker5` | `research/hotels.md`, `data/hotels.json` |
| Integrate the research into the dashboard, analysis, Q&A, suggestions, flagged-review pages, and publication workflow | complete | `arena/aa83f1e1-poker5` | `index.html`, `pages/`, `assets/`, `scripts/`, `README.md` |
| Final source/link/build verification and GitHub Pages release | in progress | `arena/aa83f1e1-poker5` | `.github/workflows/`, site files, `COORDINATION.md` |

## Working log

- 2026-11-16: Initialized the board after confirming no coordination file existed. Research tasks were claimed by the current Arena branch session. Source-based research uses official tournament/operator and hotel pages; unavailable or date-dependent facts remain blank and are surfaced under Flagged for Review.
- 2026-11-16: Added source-linked tournament and hotel datasets plus narrative research notes. The Dec 13–20 window remains a working assumption, not a user-selected travel date.
- 2026-11-16: Confirmed the WPT World Championship event-details page explicitly permits up to four entries (one per starting flight plus a Day 2 entry); retained Bellagio Saturday's inconsistency and all unresolved entry, tax-total, and official walking-route facts as flags.
- 2026-11-16: Research is integrated into a static dashboard and dedicated directory, hotel, analysis, Q&A, suggestions, flagged-review, and publication pages. Local JavaScript syntax, data/source, internal-link, static-build, and all-page smoke checks passed; GitHub PR/Pages deployment checks remain pending.
