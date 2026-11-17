# Executive Summary — Las Vegas Strip poker research

> **Read the 2026-11-17 update at the bottom first.** The section below is the
> 2026-11-16 partial read; its counts (45 single-entry, 31 unverified) are superseded by the
> complete re-read (54 single-entry, 29 advantage, 11 continuations, 0 unverified).

**What this is.** A research site for live poker tournaments on and near the Las Vegas Strip. It separates single-entry events from re-entry, rebuy, and add-on events, and it flags every value that could not be confirmed from an official source.

## Key facts (verified from official sources)

- **Single-entry events:** 45 Venetian DeepStack Extravaganza IV events (Nov 16 to Dec 23, 2026) are verified single entry from their structure sheets. A further 31 Venetian events are listed on the official schedule but their structure sheets were not read, so they are unverified.
- **Biggest single-entry prize pools:** the $2,200 PokerAtlas Championship (#47, 1A on Dec 12, 10:10 AM) with a $1,000,000 guarantee; the $800 event (#26) and $1,100 event (#56) each with $500,000.
- **Best guarantee-to-buy-in ratio (calculation):** the $800 event (#26) at 625x and the $300 event #1 at 250x.
- **Not single entry:** Wynn's daily events, Caesars' daily events, and Bellagio's Friday and Sunday events allow re-entry, rebuys, add-ons, or purchased chips. They are in a separate section.
- **Start times:** the earliest verified single-entry start is 10:10 AM. No verified single-entry event starts at 8:00 AM, so the 8:00 AM all-day goal cannot be met from verified data.
- **Hotels:** only Wynn's $55 resort fee (plus tax) is confirmed from an official page. Room rates and walking times are not verified and are blank.

## Limits

- 31 Venetian events and 46 Wynn WPT rows still need their structure sheets read.
- Official resort-fee pages were not found for the Venetian, Palazzo, Bellagio, ARIA, or Caesars Palace.
- The Clark County tax rate (13.38%) is from third-party sources.
- Walking distance and room rates need a method that is not yet available (see Questions Q04 and Q12).

## Decisions needed from you

1. Confirm your trip dates, budget, and loyalty tiers (Questions Q01, Q02, Q13).
2. Approve or reject the site suggestions S1–S10. Nothing has been implemented.
3. Confirm the 8:00 AM goal or relax it (Question Q14).

## Where to look

- Dashboard and tables: https://karagemop466-tech.github.io/Poker5/site/ (this session's site; generated from `tools/build_site.py`).
- Irregularities and unverified items with source links: "Flagged for Review" on the site and `REPO_REVIEW.md`.

---

# Update — 2026-11-17 (session aecba91e, full re-read of the official sources)

**Supersedes the counts above** for the Venetian DeepStack Extravaganza IV. The figures in the
2026-11-16 section came from a partial read (45 single-entry / 31 unverified). Every one of the
37 structure sheets and all 94 schedule rows have now been read and re-read, so the classification
below is complete rather than partial.

Published here: <https://karagemop466-tech.github.io/Poker5/site-aecba91e/> (source: `site-aecba91e/`,
built from `data/aecba91e/`).

## Verified facts

- **94 schedule rows**, Events #1–#64, Nov 16 – Dec 23, 2026, transcribed from the Venetian's own
  DSE page and then re-read a second time from the same page and diffed row for row
  (`node scripts/verify_transcription_aecba91e.mjs` — the build aborts if the two readings disagree).
- **54 rows pass the single-entry test** as published on the Rules page: it is the only scheduled start
  for that event number, its structure sheet was read in full, and the sheet prints no re-entry, re-buy
  or add-on provision. The build aborts if any row labelled single-entry turns out to have a sibling start.
- **29 rows sit in the Advantage section** instead: 13 multi-flight rows (Events #1, #7, #19, #26,
  #47, #49, #56, #59), the two fee-discount flights (#56 Day 1A/1B, $40 off before the start; #59,
  $20 off), and Events #18 / #58, whose sheet prints "All subsequent buy in's after the initial buy
  in will be $200" — official text that acknowledges further buy-ins.
- **11 rows are Day 2 / Day 3 restarts or final tables**, kept out of every entry count.
- **0 rows are unverified**: all 37 structure sheets were read. Sheets 36 and 37 needed a retry.
- **No sheet in the series prints an entry cap**, and none uses the words "single entry",
  "no re-entry", "no re-buy" or "no add-on". The label therefore names its own basis instead of
  claiming a statement that does not exist (Flagged R-F01…R-F13, Open question Q3).
- **Exact entry economics** per event from the sheets: e.g. $300 → $58 withheld → $242 to the pool;
  $600 → $90 → $510; $800 → $110 → $690; $1,100 → $140 → $960; $2,200 → $225 → $1,975.
  Payout is 12.5% of the field (15% on both seniors events); satellites pay seats, not cash.
- **The 8:00 AM goal cannot be met from this schedule.** The earliest printed start in the whole
  series is 9:10 AM (Event #46 satellite, Dec 12), then 10:10 AM. No event starts at 8:00 or 9:00.
- **The largest guarantee you can enter once** is $75,000 — Event #36 ($800 PKO, Dec 9) and Event #52
  ($1,100 PKO, Dec 15). Both pay bounties out of that number. The largest guarantee on a single-entry
  event with no bounty element is $40,000 (#24 and #32 seniors $600, #28 $600, #39 $800 LIPS Ladies).
  Every bigger guarantee in the series — $500,000 (#26, #56), $1,000,000 (#47), $150,000 (#59),
  $300,000 (#49) — belongs to a multi-flight event, which is why those rows sit in the Advantage
  section and not in the single-entry list.

## Hotel side — still the weak half, and now stated as such

- No dated official room rate exists in any source read by any session for the assumed window; the
  rate log holds six dated records captured by prior sessions, each shown with its own date and
  occupancy instead of being merged into one flat number.
- Resort fee is official for three properties only: Venetian and Palazzo $55 + tax, Wynn/Encore
  $55 + tax per offer terms (another official Wynn offer says $45 — offer-specific, flagged), Resorts
  World $55 waived on "All Resort, No Fees". Bellagio, Cosmopolitan, Park MGM, ARIA and Vdara are
  **blank, not zero**.
- **No Strip property publishes walking minutes**, so the ≤30-minute rule can only be satisfied for
  The Venetian's own poker room (same building, 0 minutes). Every other hotel↔venue pair is blank or
  an explicitly third-party estimate, with map links so the walk can be timed and recorded.
- Room tax 13.38% is used by the true-cost formula but rests on a 2021-dated Clark County hearing
  PDF read by a prior session — flagged (R-F09, Q6), not presented as confirmed.

## Cost model

`total = Σ(entries × entry fee) + nights × (room rate + resort fee + room tax on the rate + parking ÷ nights)`.
Any missing input makes that half of the total read "unknown" rather than zero — visible on the
Trip cost page. The page is prefilled with the labelled assumption window (Dec 3 → Dec 7, 4 nights);
the dates were never supplied by the user and nothing treats them as decided (Q1).

## What still needs a human or the property

Q1 trip dates · Q2 nightly budget and quality floor · Q5 whether a 9:10/10:10 start is acceptable ·
Q10 which hotel wins when cost and the walk conflict — plus a written single-entry statement (Q3/Q4)
and a measured walk time (Q7/Q8) which only the guest can produce.
