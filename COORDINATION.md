# COORDINATION.md — Shared task board

Repo: karagemop466-tech/Poker5 · Session branch: `arena/359e3f96-poker5` (base `0ba2e55`, `main`)

Note on process: this session is pinned to the single branch above, so the `session-<id>/<task>` branches described in the brief are not used. All tasks below are owned by session `359e3f96`. Other sessions must not edit files listed in a task's scope without logging a request here first.

## Task board

| Task | Status | Owner (session) | File scope | Notes |
|---|---|---|---|---|
| T1 Repo review | done | 359e3f96 | `README.md`, `data/repo-review.json`, `docs/repo-review.html` (generated) | Repo contained only `README.md` (one line) and one commit. No LICENSE, no code. |
| T2 Tournament data (Strip rooms) | in progress (partial) | 359e3f96 | `data/tournaments.json`, `data/venues.json` | Venetian rows checked against schedule and structure sheets for 11 of 20 events. Single-entry status is inferred from absence of re-entry or add-on terms. Not confirmed by an official 'single-entry' statement. Horseshoe, ARIA, Planet Hollywood and Resorts World not classified (see venues). Remaining Venetian structure sheets, and Wynn WPT events, are in the unverified table. |
| T3 Hotel data (resort fees, poker-room rates) | in progress (partial) | 359e3f96 | `data/hotels.json` | Resort fees verified only for Venetian/Palazzo and Wynn. Caesars, MGM (Bellagio, ARIA) and Horseshoe official resort-fee pages not found. Nightly rates and walking times not verified; left blank. |
| T4 Site build (GitHub Pages) | in progress | 359e3f96 | `scripts/build.mjs`, `scripts/check.mjs`, `docs/**`, `data/questions.json`, `data/suggestions.json`, `data/flags.json` | Build (11 pages) and check (no broken rows) pass locally. Not yet deployed. |
| T5 Integration, verification, PR, merge, Pages deploy | pending | 359e3f96 | `COORDINATION.md` (log) | Runs after T4 is merged to `main`. |

Claim timestamp: 2026-11-16 (UTC). Claimed before any data commit.

## Log

- 2026-11-16 — 359e3f96 claimed T1–T5. Scope as above.
- 2026-11-16 — T1 done: repo reviewed (README only, one commit, no code, no LICENSE, no build). No other sessions active on this repo at claim time (no other branches on origin besides `main`).
- 2026-11-16 — T2 partial. Corrected status: an earlier entry called this done; it is not. Sources: official Caesars, Wynn, Venetian, Bellagio and Golden Nugget pages/PDFs listed in `data/tournaments.json`. Single-entry status for the Venetian rows is inferred from the structure sheets (no re-entry, rebuy or add-on listed). This is flagged (F06).
- 2026-11-16 — T3 partial. Corrected status: an earlier entry called this done; it is not. Resort fees only where an operator's own terms page was retrieved (Venetian/Palazzo, Wynn). Everything else blank and flagged.
- 2026-11-16 — T4 build: static site generated into `/docs` from `/data` (11 pages). `scripts/check.mjs` passes (33 tournament rows, every data row linked to an official source).
- Correction (2026-11-16): an earlier draft of the hotel and venue data contained contact details, a promotional code, room-location labels and some URLs that could not be traced to a retrieved source. These were removed. Only sourced values remain.

## Irregularities / handoffs

- Repo review: repository has no application code, no LICENSE, and README is a single title line. Flagged.
- Several third-party sites disagree with official pages on buy-ins, resort fees and whether rooms are open. The official value is used; the conflict is listed on the "Flagged for Review" page.
- Bellagio Saturday PDF: file name says $1,000, heading says $1,100, body text says $600 buy-in. Left unresolved and flagged.
- Planet Hollywood and Resorts World are reported closed by trade press (not confirmed by an official source). They are excluded and flagged.
- Venetian single-entry status is inferred (F06). Official confirmation of single-entry terms was not found.
- Caesars Palace daily events allow re-entry for a fee in the first break. They are in the separate section, so they are not single-entry.

## Final integration (T5)

Pending. Will record: PR link, merge result, Pages deploy result.
