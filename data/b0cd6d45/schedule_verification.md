# Venetian DeepStack Extravaganza IV: line-by-line schedule verification (b0cd6d45)

**Official source (read 2026-11-17, all four chunks):** https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html

**Captured file compared:** `data/c6087e2c/venetian_dse_2026.psv` (94 rows)

## Method

- Each captured row was compared with the official table row for the same date, start time and event number. Compared fields: date, start time, event number, event name, buy-in, guarantee, and the structure-sheet PDF number linked on that row.
- The official page was read with `fetch_page` (chunks 0-3, the last at `hasMore: false`). Rows were read line by line from the official text.
- Name differences that are only typography are treated as matches: `(1-Day)` vs `(1Day)`, `$1M` vs `$1 Mill`, and the official typo `No LImit`.
- Result: 94 of 94 rows match on every compared field. Two rows (Event #47 Day 2 and Day 3 restarts) had shortened names in the capture and were corrected to the official row text.
- The `--feed` presence check in `scripts/recheck_sources.py` was rewritten to use the same normalisation so the scheduled run does not report false "not found" rows. It has not yet run against the live page; run it from the Actions tab after merge.

## What was not verified here

- Structure-sheet rule text (single-entry, re-entry, add-on, late-registration close, starting stack) was not re-read in this session. Those values remain as recorded by session 3c49aaec (37 sheets read 2026-11-17).
- Event durations and finish times are not on the official schedule and remain unverified.
- The official page is the only source checked here; the structure-sheet PDFs are not re-downloaded.

## Row-by-row result

| # | Date | Start | Event # | Official name (as captured) | Buy-in | Guarantee | Sheet | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | Mon Nov 16 | 11:10 | 1 | $300 No Limit Hold'em 1A $75K GTD | 300 | 75000 | 10 | Match |
| 2 | Mon Nov 16 | 17:10 | 1 | $300 No Limit Hold'em 1B $75K GTD | 300 | 75000 | 9 | Match |
| 3 | Tue Nov 17 | 11:10 | 1 | $300 No Limit Hold'em 1C $75K GTD | 300 | 75000 | 10 | Match |
| 4 | Tue Nov 17 | 17:10 | 1 | $300 No Limit Hold'em 1D $75K GTD | 300 | 75000 | 9 | Match |
| 5 | Wed Nov 18 | 11:10 | 2 | $300 No Limit Hold'em $10K GTD (1-Day) | 300 | 10000 | 5 | Match |
| 6 | Wed Nov 18 | 12:00 | 1 | $300 No Limit Hold'em Day 2 Restart | - | - | 10 | Match (restart row) |
| 7 | Thu Nov 19 | 10:10 | 3 | $200 NLH RaceDay Stack (1-Day); race to finish before the Race | 200 | - | 18 | Match |
| 8 | Fri Nov 20 | 10:10 | 4 | $200 NLH RaceDay Stack (1-Day); race to finish before the Race | 200 | - | 18 | Match |
| 9 | Sat Nov 21 | 10:10 | 5 | $200 NLH RaceDay Stack (1-Day); race to finish before the Race | 200 | - | 18 | Match |
| 10 | Sun Nov 22 | 11:10 | 6 | $200 No Limit Hold'em (1-Day) | 200 | - | 29 | Match |
| 11 | Mon Nov 23 | 11:10 | 7 | $400 No Limit Hold'em 1A $75K GTD | 400 | 75000 | 2 | Match |
| 12 | Mon Nov 23 | 17:10 | 8 | $200 No Limit Hold'em $8K GTD (1-Day), Progressive Knock-Out Bounty (PKO) | 200 | 8000 | 30 | Match |
| 13 | Tue Nov 24 | 11:10 | 7 | $400 No Limit Hold'em 1B $75K GTD | 400 | 75000 | 2 | Match |
| 14 | Tue Nov 24 | 17:10 | 9 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 15 | Wed Nov 25 | 11:00 | 7 | $400 No Limit Hold'em Day 2 Restart | - | - | 2 | Match (restart row) |
| 16 | Wed Nov 25 | 11:10 | 10 | $400 No Limit Hold'em $15K GTD (1-Day) | 400 | 15000 | 6 | Match |
| 17 | Wed Nov 25 | 17:10 | 11 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 18 | Thu Nov 26 | 11:10 | 12 | $300 No Limit Hold'em $10K GTD (1-Day) | 300 | 10000 | 5 | Match |
| 19 | Thu Nov 26 | 17:10 | 13 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 20 | Fri Nov 27 | 11:10 | 14 | $600 No Limit Hold'em $30K GTD (1-Day) | 600 | 30000 | 7 | Match |
| 21 | Fri Nov 27 | 17:10 | 15 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 22 | Sat Nov 28 | 11:10 | 16 | $600 No Limit Hold'em Bounty $30K GTD (1-Day) | 600 | 30000 | 11 | Match |
| 23 | Sat Nov 28 | 12:10 | 17 | $400 Pot Limit Omaha Bounty $15K GTD (1-Day) | 400 | 15000 | 26 | Match |
| 24 | Sat Nov 28 | 17:10 | 18 | $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1-Day) | 200 | 20000 | 8 | Match |
| 25 | Sun Nov 29 | 11:10 | 19 | $400 No Limit Hold'em 1A $75K GTD | 400 | 75000 | 3 | Match |
| 26 | Sun Nov 29 | 12:10 | 20 | $300 Pot Limit Omaha $10K GTD (1-Day), Double Board Bomb Pot | 300 | 10000 | 22 | Match |
| 27 | Sun Nov 29 | 17:10 | 21 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 28 | Mon Nov 30 | 11:10 | 19 | $400 No Limit Hold'em 1B $75K GTD | 400 | 75000 | 3 | Match |
| 29 | Mon Nov 30 | 17:10 | 22 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 30 | Tue Dec 01 | 11:10 | 19 | $400 No Limit Hold'em 1C $75K GTD | 400 | 75000 | 3 | Match |
| 31 | Tue Dec 01 | 17:10 | 23 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 32 | Wed Dec 02 | 10:10 | 24 | $600 No Limit Hold'em Seniors $40K GTD (1-Day), 50+ only | 600 | 40000 | 17 | Match |
| 33 | Wed Dec 02 | 11:00 | 19 | $400 No Limit Hold'em Day 2 Restart | - | - | 3 | Match (restart row) |
| 34 | Wed Dec 02 | 17:10 | 25 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 35 | Thu Dec 03 | 11:10 | 26 | $800 No Limit Hold'em 1A $500K GTD | 800 | 500000 | 12 | Match |
| 36 | Thu Dec 03 | 12:10 | 27 | $600 BIG O $25K GTD (1-Day) | 600 | 25000 | 28 | Match |
| 37 | Thu Dec 03 | 17:10 | 26 | $800 No Limit Hold'em 1B $500K GTD | 800 | 500000 | 13 | Match |
| 38 | Fri Dec 04 | 11:10 | 26 | $800 No Limit Hold'em 1C $500K GTD | 800 | 500000 | 12 | Match |
| 39 | Fri Dec 04 | 17:10 | 26 | $800 No Limit Hold'em 1D $500K GTD | 800 | 500000 | 13 | Match |
| 40 | Sat Dec 05 | 11:10 | 26 | $800 No Limit Hold'em 1E $500K GTD | 800 | 500000 | 12 | Match |
| 41 | Sat Dec 05 | 17:10 | 26 | $800 No Limit Hold'em 1F (Turbo) $500K GTD | 800 | 500000 | 14 | Match |
| 42 | Sun Dec 06 | 11:10 | 28 | $600 No Limit Hold'em $40K GTD (1-Day) | 600 | 40000 | 7 | Match |
| 43 | Sun Dec 06 | 12:00 | 26 | $800 No Limit Hold'em Day 2 Restart | - | - | 12 | Match (restart row) |
| 44 | Sun Dec 06 | 17:10 | 29 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 45 | Mon Dec 07 | 11:10 | 30 | $600 No Limit Hold'em Bounty $40K GTD (1-Day) | 600 | 40000 | 11 | Match |
| 46 | Mon Dec 07 | 17:10 | 31 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 47 | Tue Dec 08 | 10:10 | 32 | $600 No Limit Hold'em Seniors $40K GTD (1-Day), 50+ only | 600 | 40000 | 17 | Match |
| 48 | Tue Dec 08 | 16:10 | 33 | $100 NLH LIPS Ladies Milestone Satellite (1-Day) | 100 | - | 19 | Match |
| 49 | Tue Dec 08 | 17:10 | 34 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 50 | Wed Dec 09 | 10:10 | 35 | $600 NLH LIPS Poker Jingle Tag Team $10K GTD (1-Day) | 600 | 10000 | 31 | Match |
| 51 | Wed Dec 09 | 11:10 | 36 | $800 No Limit Hold'em Bounty $75K GTD (1-Day) | 800 | 75000 | 16 | Match |
| 52 | Wed Dec 09 | 16:10 | 37 | $100 NLH LIPS Ladies Milestone Satellite (1-Day) | 100 | - | 19 | Match |
| 53 | Wed Dec 09 | 17:10 | 38 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 54 | Thu Dec 10 | 10:10 | 39 | $800 No Limit Hold'em LIPS Ladies $40K GTD (2-Day), Women in Poker main event | 800 | 40000 | 32 | Match |
| 55 | Thu Dec 10 | 12:10 | 40 | $600 Pot Limit Omaha Bounty $25K GTD (1-Day) | 600 | 25000 | 27 | Match |
| 56 | Thu Dec 10 | 16:10 | 41 | $260 NLH Milestone Satellite (1-Day) | 260 | - | 24 | Match |
| 57 | Thu Dec 10 | 17:10 | 42 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 58 | Fri Dec 11 | 10:00 | 39 | $800 No Limit Hold'em LIPS Ladies Day 2 Restart | - | - | 32 | Match (restart row) |
| 59 | Fri Dec 11 | 11:10 | 43 | $600 No Limit Hold'em LIPS $30K GTD (1-Day), KINGS and QUEENS Bounty | 600 | 30000 | 33 | Match |
| 60 | Fri Dec 11 | 16:10 | 44 | $260 NLH Milestone Satellite (1-Day) | 260 | - | 24 | Match |
| 61 | Fri Dec 11 | 19:00 | 39 | $800 No Limit Hold'em LIPS Ladies Final Table | - | - | 32 | Match (restart row) |
| 62 | Fri Dec 11 | 20:10 | 45 | $260 NLH Turbo Milestone Satellite (1-Day) | 260 | - | 25 | Match |
| 63 | Sat Dec 12 | 09:10 | 46 | $260 NLH Turbo Milestone Satellite (1-Day) | 260 | - | 25 | Match |
| 64 | Sat Dec 12 | 10:10 | 47 | $2,200 No Limit Hold'em 1A $1M GTD, PokerAtlas Championship title event | 2200 | 1000000 | 21 | Match |
| 65 | Sat Dec 12 | 12:10 | 48 | $260 NLH Turbo Milestone Satellite (1-Day) | 260 | - | 25 | Match |
| 66 | Sat Dec 12 | 18:10 | 47 | $2,200 No Limit Hold'em 1B $1M GTD, PokerAtlas Championship title event | 2200 | 1000000 | 37 | Match |
| 67 | Sun Dec 13 | 10:10 | 49 | $1,100 No Limit Hold'em Seniors 1A $300K GTD | 1100 | 300000 | 20 | Match |
| 68 | Sun Dec 13 | 13:00 | 47 | $2,200 NLH PokerAtlas Championship Title Event Day 2 Restart (play down to final 7; streamed final table) | - | - | 21 | Match (name corrected to official row text) |
| 69 | Sun Dec 13 | 17:10 | 50 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 70 | Mon Dec 14 | 10:10 | 49 | $1,100 No Limit Hold'em Seniors 1B $300K GTD | 1100 | 300000 | 20 | Match |
| 71 | Mon Dec 14 | 11:00 | 47 | $2,200 NLH PokerAtlas Championship Title Event Day 3 Restart (streamed final table) | - | - | 21 | Match (name corrected to official row text) |
| 72 | Mon Dec 14 | 17:10 | 51 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 73 | Tue Dec 15 | 10:00 | 49 | $1,100 No Limit Hold'em Seniors Day 2 Restart | - | - | 20 | Match (restart row) |
| 74 | Tue Dec 15 | 11:10 | 52 | $1,100 No Limit Hold'em $75K GTD (1-Day), Progressive Knock-Out Bounty (PKO) | 1100 | 75000 | 34 | Match |
| 75 | Tue Dec 15 | 17:10 | 53 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 76 | Wed Dec 16 | 11:10 | 54 | $600 No Limit Hold'em Bounty $50K GTD (1-Day) | 600 | 50000 | 11 | Match |
| 77 | Wed Dec 16 | 17:10 | 55 | $300 No Limit Hold'em Bounty $15K GTD (1-Day) | 300 | 15000 | 15 | Match |
| 78 | Thu Dec 17 | 10:10 | 56 | $1,100 No Limit Hold'em 1A $500K GTD | 1100 | 500000 | 35 | Match |
| 79 | Thu Dec 17 | 12:10 | 57 | $600 Pot Limit Omaha $25K GTD (1-Day), Double Board Bomb Pot | 600 | 25000 | 23 | Match |
| 80 | Thu Dec 17 | 18:10 | 56 | $1,100 No Limit Hold'em 1B $500K GTD | 1100 | 500000 | 36 | Match |
| 81 | Fri Dec 18 | 10:10 | 56 | $1,100 No Limit Hold'em 1C $500K GTD | 1100 | 500000 | 35 | Match |
| 82 | Fri Dec 18 | 18:10 | 56 | $1,100 No Limit Hold'em 1D $500K GTD | 1100 | 500000 | 36 | Match |
| 83 | Sat Dec 19 | 10:10 | 56 | $1,100 No Limit Hold'em 1E $500K GTD | 1100 | 500000 | 35 | Match |
| 84 | Sat Dec 19 | 17:10 | 58 | $200 NLH PokerAtlas Valuetown Bounty $20K GTD (1-Day) | 200 | 20000 | 8 | Match |
| 85 | Sun Dec 20 | 11:00 | 56 | $1,100 No Limit Hold'em Day 2 Restart | - | - | 35 | Match (restart row) |
| 86 | Sun Dec 20 | 11:10 | 59 | $600 No Limit Hold'em 1A $150K GTD | 600 | 150000 | 4 | Match |
| 87 | Sun Dec 20 | 17:10 | 60 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 88 | Mon Dec 21 | 11:10 | 59 | $600 No Limit Hold'em 1B $150K GTD | 600 | 150000 | 4 | Match |
| 89 | Mon Dec 21 | 17:10 | 61 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 90 | Tue Dec 22 | 11:10 | 59 | $600 No Limit Hold'em 1C $150K GTD | 600 | 150000 | 4 | Match |
| 91 | Tue Dec 22 | 17:10 | 62 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |
| 92 | Wed Dec 23 | 11:00 | 59 | $600 No Limit Hold'em Day 2 Restart | - | - | 4 | Match (restart row) |
| 93 | Wed Dec 23 | 11:10 | 63 | $600 No Limit Hold'em $30K GTD (1-Day) | 600 | 30000 | 7 | Match |
| 94 | Wed Dec 23 | 17:10 | 64 | $200 No Limit Hold'em Bounty $8K GTD (1-Day) | 200 | 8000 | 1 | Match |

## Irregularities

- Event #47 restarts (Dec 13, Dec 14): capture shortened the name (dropped "PokerAtlas Championship Title Event"). Corrected in the capture; recorded as a transcription fix, not a value change.
- Official page typo "No LImit" in the names of events #2, #10 and #12, and "(1Day)" vs "(1-Day)" labels throughout: typography only.
- Seniors events #24, #32, #49 carry "Must be 50+" on the official row; the age rule is kept in the captured notes and is not an entry-cap or re-entry rule.
- Structure sheet 27 (Event #40): the capture note says the re-entry/add-on rule is not stated on the sheet; this was not re-read here.

