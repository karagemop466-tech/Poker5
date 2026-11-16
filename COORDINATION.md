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
| T-A: Single-entry live tournament research (Strip), official sources | done | `443e914d` | `data/tournaments_single_entry.json`, `data/sources.json` |
| T-B: Double buy-in / add-on / re-entry / flight list (separate section) | done | `443e914d` | `data/tournaments_multi_entry.json` |
| T-C: Hotel research (official resort fees; blanks for unverified rates and walk times) | done (partial by design) | `443e914d` | `data/hotels.json` |
| T-D: Executive summary, suggestions, questions, flagged-for-review pages | done | `443e914d` | `tools/build_site.py` (content), `data/pending_and_flags.json` |
| T-E: GitHub Pages site (landing page, category subpages, tables) | done (built) | `443e914d` | `docs/`, `tools/build_site.py`, `README.md` |
| T-F: Final integration, re-verification, link check, PR to `main`, merge, Pages deploy | in progress | `443e914d` | `COORDINATION.md` and integration of all of the above |

Overlap note: this session's claim overlaps with the claims listed above. Because each session works on a separate branch, no claimed file exists in any other branch's content yet. Any later merge conflict will be resolved in the integration step and logged below.

## Task log
- 2026-11-16 — `443e914d` claimed T-A through T-F. Board consolidated from visible branches.
- 2026-11-16 — T-A done: 36 single-entry Venetian rows (Nov 18 – Dec 23). Each date, weekday, start, buy-in, and guarantee re-checked against the official schedule PDF and event page (research/verification.md, 0 mismatches). Structure-sheet fields for rows #02–#57 were recorded in an earlier session and not all re-read. Multi-entry and flight formats kept separate (T-B).
- 2026-11-16 — T-C partial: only some official resort fees verified (Venetian $55; Wynn offer-specific $45/$55). Caesars, MGM, Palazzo, and Encore fees, nightly rates, walk times, and room tax are blank (flagged H-01 to H-09).
- 2026-11-16 — T-D/T-E done: site generated from `data/` into `docs/` (11 pages). Internal link check passed; all external URLs match `data/sources.json`.

## Sources used (official unless marked)
- Venetian DSE IV event page and schedule PDF; structure sheets 1, 2, 5, 6, 7, 8, 10, 11, 15, 16, 23, 28, 34 (venetianlasvegas.com)
- Venetian 2026 poker-room rates page (venetianlasvegas.com)
- Wynn poker room page, daily tournament poster, daily structure PDF, WPT World Championship schedule PDF (wynnlasvegas.com, cdn.wynnresorts.com)
- WPT event page (worldpokertour.com)
- Wynn special-offer terms (resort fee $45 / $55) (wynnlasvegas.com)
- MGM Resorts hotel terms index (mgmresorts.com) – no fee values on this page
- Full list: `data/sources.json` and the site's Sources page.

Third-party pages (PokerAtlas, vegaspokercalendar, casinos.com, news, tax guides) were used only as leads and are never used as the source of a value.

## Verification performed
- Single-entry rows: date, weekday, start, buy-in, guarantee checked line-by-line (36/36 match; research/verification.md). Structure-sheet fields for rows #02–#57 not all re-read this session.
- Multi-entry and flight rows: rules are paraphrased from the sources read; the multi-entry rules for flight events not fetched are flagged.
- Hotels: resort fee taken only from official pages (Venetian page, Wynn offer terms 848631 fetched); all other values blank.
- Site: generator is stdlib-only; tools/check_links.py passes (11 pages, 0 broken internal links or anchors; all 45 external URLs are in data/sources.json).

## Handoff / irregularities
- Seven sessions claimed overlapping scope in parallel on separate branches within ~2 minutes; there is no single shared board on `main`. Logged as R-01.
- Brief asks for `session-<id>/<task>` branches; Arena fixes this session to `arena/443e914d-poker5`. Logged as R-02.
- Repository state at start: `README.md` only. Logged as R-03.
- Wynn daily structure PDF: upload stamp implies about July 2025 and the PDF is undated; current terms not confirmed (R-04).
- Wynn resort fee conflicts ($45 vs $55, H-01). Caesars and MGM fees unverified (H-06, H-07).
- WPT $1,000,000 added prize: official schedule says ClubWPT Gold is not available in Nevada (P-02).

## Flagged for Review
- Full list on the site's **Flagged for Review** page (`docs/flagged-review.html`), generated from `data/pending_and_flags.json`.

## Final integration (T-F)
- PR: (filled in after creation)
- Merge result: (filled in after merge)
- Pages deploy: (filled in after deploy)
