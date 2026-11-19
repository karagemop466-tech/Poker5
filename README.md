# Poker5 — Las Vegas Strip poker-trip research dashboard

**Published dashboard:** <https://karagemop466-tech.github.io/Poker5/>

Poker5 organizes official Las Vegas tournament schedules, structure sheets, hotel terms, dated rate observations, walking-route evidence, and open questions. It is a research aid, not a booking quote or a guarantee that an event is a freezeout.

## Evidence standard and current snapshot

The canonical site is generated from `data/ea99006a/` by `scripts/build_ea99006a.py`. The current Venetian capture records 94 schedule rows and all 37 linked structure sheets read; 53 rows meet the site's published **S1, “confirmed single-entry (standard S1)”** test, and 41 are classified as multi-entry. S1 means the event-specific official sheet was read and no listed term grants another entry; **no Venetian sheet explicitly promises one entry only**, so the label is not a house guarantee. See the [Sources & method](https://karagemop466-tech.github.io/Poker5/pages/method.html), [Verification](https://karagemop466-tech.github.io/Poker5/pages/verification.html), and [Flagged for review](https://karagemop466-tech.github.io/Poker5/pages/flagged-review.html) pages.

Every published table row is required by the checker to link to an official source. Unknown or conflicting values remain blank or are labeled for review. Derived calculations (for example, nightly averages and schedule-fit indicators) are identified as derived; guaranteed-pool-to-entry-fee ratios are descriptive arithmetic, not a forecast. Structure-sheet evidence, retrieval dates, last-checked dates, and value-change marks are exposed on the relevant pages.

Data is time-sensitive. The repository's latest checked-in official-source capture is timestamped **2026-11-19**; scheduled jobs can fail or encounter inaccessible sources. The value-level monitor ledger currently says that no live value-level run has been recorded, so the absence of a changed-value badge does **not** mean a value was re-checked and found unchanged. A successful offline ledger check validates the stored record, not that a source is unchanged today. Reconfirm event terms, hotel inventory, and cancellation policies with the official source before payment or play.

## Published pages

- [Executive summary](https://karagemop466-tech.github.io/Poker5/pages/executive-summary.html)
- [Tournaments](https://karagemop466-tech.github.io/Poker5/pages/tournaments.html) — search, date, venue, entry-rule, rankability, and changed-value filters
- [Daily schedule](https://karagemop466-tech.github.io/Poker5/pages/schedule.html) — primary event and conditional fallback; inferred finish times are not presented as verified
- [Hotels and dated rates](https://karagemop466-tech.github.io/Poker5/pages/hotels.html) — itemized terms and dated observations; missing quote components stay blank
- [Walking routes](https://karagemop466-tech.github.io/Poker5/pages/routes.html) — the 30-minute filter only applies where route evidence is recorded
- [Trip planner](https://karagemop466-tech.github.io/Poker5/pages/planner.html) — does not claim a complete trip total without a date-matched, itemized hotel quote
- [Questions / missing information](https://karagemop466-tech.github.io/Poker5/pages/questions.html)
- [Suggestions](https://karagemop466-tech.github.io/Poker5/pages/suggestions.html)
- [Flagged for review](https://karagemop466-tech.github.io/Poker5/pages/flagged-review.html)
- [Source-change monitor](https://karagemop466-tech.github.io/Poker5/pages/monitor.html)

## Build and monitoring architecture

There are multiple historical research snapshots in this repository. **Only the `ea99006a` builder publishes the root GitHub Pages dashboard.** The separate `c6087e2c` morning job captures the official Venetian schedule and its structure sheets in a research ledger; it is capture/validation only and must not rebuild or commit the root site.

```
Official sources
  ├─ .github/workflows/daily-scrape.yml
  │    scripts/scrape_251c122f.py → data/c6087e2c/ capture + cross-check
  │    (does not publish the root site)
  └─ .github/workflows/recheck-ea99006a.yml (13:00 and 19:00 UTC daily)
       scripts/recheck_ea99006a.py + scripts/monitor_b3be876c.py
       → value-level monitor and dated observations
       → scripts/integrate_b3be876c.py re-derives data/ea99006a records
       → scripts/build_ea99006a.py → index.html and pages/**
       → scripts/check_ea99006a.py validates rows, official links and internal links
```

`quality.yml` rebuilds the canonical site and checks that committed output matches the builder. The morning scrape and the canonical publisher are distinct because an earlier dual-publisher setup could overwrite the site with a different dataset.

## Local checks

```sh
npm run check
node --check assets/app.js
python3 scripts/build_ea99006a.py
python3 scripts/check_ea99006a.py
python3 scripts/check_root_site.py
python3 scripts/crosscheck_251c122f.py
python3 scripts/recheck_ea99006a.py --offline
python3 scripts/scrape_251c122f.py --self-test
```

The live scrape runs in GitHub Actions, not from the sandbox. `--offline` checks only the saved monitoring ledger and performs no network request.

## Repository notes

`docs/`, `site/`, `site-*`, `dashboard-*`, `planner-*`, and earlier data snapshots are retained research/output from prior sessions; they are not the canonical root publisher. `COORDINATION.md` is the shared task board and records scopes, verification, and unresolved issues.

Poker5 is independent and is not affiliated with any casino, poker room, or hotel. Gambling involves risk. Must be 21+. If gambling is a problem, call 1-800-522-4700.
