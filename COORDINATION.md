# COORDINATION.md — Shared task board

Repo: karagemop466-tech/Poker5 · Session branch: `arena/359e3f96-poker5` (base `0ba2e55`, `main`)

Note on process: this session is pinned to the single branch above, so the `session-<id>/<task>` branches described in the brief are not used. All tasks below are owned by session `359e3f96`. Other sessions must not edit files listed in a task's scope without logging a request here first.

## Task board

| Task | Status | Owner (session) | File scope | Notes |
|---|---|---|---|---|
| T1 Repo review | done | 359e3f96 | `README.md`, `docs/repo-review.html` (generated), `data/repo-review.json` | Repo contained only `README.md` and one commit. See "Irregularities" below. |
| T2 Tournament data (Strip rooms, single-entry + separate section) | done | 359e3f96 | `data/tournaments.json`, `data/venues.json` | Official sources only; unverified rows left blank and flagged. |
| T3 Hotel data (resort fees, poker-room rates) | done | 359e3f96 | `data/hotels.json` | Nightly rates and walking times could not be verified from official sources; left blank. |
| T4 Site build (GitHub Pages) | in progress | 359e3f96 | `scripts/build.mjs`, `scripts/check.mjs`, `docs/**`, `data/questions.json`, `data/suggestions.json`, `data/flags.json` | Static site generated into `/docs`. |
| T5 Integration, verification, PR, merge, Pages deploy | pending | 359e3f96 | `COORDINATION.md` (log) | Runs after T4. |

Claim timestamp: 2026-11-16 (UTC). Claimed before any data commit.

## Log

- 2026-11-16 — 359e3f96 claimed T1–T5. Scope as above.
- 2026-11-16 — T1 done: repo reviewed (README only, one commit, no code, no license, no build). No other sessions active on this repo at claim time (no other branches on origin besides `main`).
- 2026-11-16 — T2 done. Sources: official Caesars, Wynn, Venetian, Bellagio and Golden Nugget pages/PDFs listed in `data/tournaments.json`. Verification: each row was checked against the schedule row and, for the Venetian and Wynn, the structure sheet (re-entry, add-on, flights). Third-party sites were used only to find conflicts, which are flagged.
- 2026-11-16 — T3 done. Resort-fee values only where an operator's own terms page was retrieved (Venetian, Wynn). Everything else blank and flagged.

## Irregularities / handoffs

- Repo review: repository has no application code, no LICENSE, and README is a single title line. Flagged.
- Several third-party sites disagree with official pages on buy-ins, resort fees and whether rooms are open. The official value is used; the conflict is listed on the "Flagged for Review" page.
- Bellagio Saturday PDF: file name says $1,000, heading says $1,100, body text says $600 buy-in. Left unresolved and flagged.
- Planet Hollywood and Resorts World are reported closed by trade press (not confirmed by an official source). They are excluded and flagged.

## Final integration (T5)

Pending. Will record: PR link, merge result, Pages deploy result.
