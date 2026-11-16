# COORDINATION.md — shared task board

Branch: `arena/581fea93-poker5` (single session; this session is the only active agent on this branch)
Session ID: `581fea93`

| Task | Status | Owner session | Files touched |
|---|---|---|---|
| Repo review (README/git state, irregularities) | done | 581fea93 | COORDINATION.md, docs/sources.html |
| Tournament research — Venetian DeepStack Extravaganza IV (Strip) | done (see log) | 581fea93 | tools/data.py |
| Tournament research — Wynn WPT World Championship festival | done (see log) | 581fea93 | tools/data.py |
| Hotel research — resort fees (Venetian, Wynn, ARIA) | partial, flagged | 581fea93 | tools/data.py |
| Analysis, executive summary, questions, suggestions, flagged-for-review | done | 581fea93 | tools/build.py, docs/*.html |
| Site build (GitHub Pages, /docs) + link check | done | 581fea93 | tools/build.py, docs/ |
| Integration: merge to main, PR, Pages deploy | in progress | 581fea93 | — |

## Log

- 2026-11-16 — Session 581fea93 claimed all tasks above (single active session on this branch; no other session claims found in repo).
- Repo state at start: only `README.md` ("# Poker5"); no COORDINATION.md; no site; no data.
- Sources used (all fetched 2026-11-16):
  - Venetian DeepStack Extravaganza IV schedule — https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
  - Venetian structure sheets — https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/ (dse_nov_2026-structure_N.pdf)
  - Venetian resort fee — https://www.venetianlasvegas.com/resort/resort-fee.html
  - Wynn WPT World Championship schedule PDF — https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf
  - Wynn WPT structures PDF — https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf
  - WPT official event page — https://www.worldpokertour.com/event/main-tour-wpt-world-championship-at-wynn-las-vegas-season-2026
  - Wynn poker room page — https://www.wynnlasvegas.com/casino/poker
  - Wynn resort fee terms — https://www.wynnlasvegas.com/terms-and-conditions/850257
  - WSOP official schedule — https://www.wsop.com/schedule/
- Verification performed: every single-entry Venetian row cross-checked against the official schedule AND (where reviewed) the structure sheet's event-number list; prize-pool shares taken from structure sheets.
- Irregularities: see docs/flagged.html.
- GitHub Pages: Pages already existed on main with source path `/` (root). The session token could not change the source to `/docs` (HTTP 403). Root `index.html` redirects to `docs/index.html`, so the site is served from the existing setting. Live URL: https://karagemop466-tech.github.io/Poker5/

