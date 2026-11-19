# Executive summary — Las Vegas Strip poker trip (merged dataset, re-verified 2026-11-19)

Generated from `data/bdcaf0bf/` — the merged, re-checked output of the two earlier
captures (`data/c6087e2c/` from the Venetian scrape, `data/ea99006a/` from the
WPT / other-rooms ledger) plus this session's own re-read of every official page.
The live site is the authoritative version: every figure here is reproduced there
with its source link.

An earlier version of this file reported one session's numbers (94 rows, 55
confirmed single-entry). Those numbers are still true *of that dataset*; the
merged dataset below is what the published site now uses.

## The plan the evidence supports

A Strip poker trip **Sun Dec 6 – Sun Dec 13, 2026** (7 nights, computed from the
official rows rather than typed in), based at **The Venetian / The Palazzo**,
playing the **53** events in the merged schedule whose own structure sheet was read
and shows no re-entry, rebuy, add-on or purchased-chip language — **20** of those
inside the chosen week, of which **12** also have both a published buy-in and a
published guarantee and can therefore be ranked. One primary event per day, a
second event on **16** of the **35** scheduled venue-days, always conditional on
having already busted out of the first.

## Verified facts

| Fact | Value | Source |
|---|---|---|
| Schedule rows in the merged dataset | 247 | `data/bdcaf0bf/events.json`, one official URL per row |
| Venetian DeepStack Extravaganza IV rows / structure sheets read in full | 94 / 37 of 37 | [official schedule page](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) |
| Events with an official **one-entry / no-re-entry / freezeout statement** | **0** | none found on any sheet or room page |
| Events where the sheet was read and contains **no re-entry language** | 53 | each row prints the excerpt it was read from |
| Events excluded for **paid re-entry, add-on, extra flights or a membership-priced first buy-in** | 75 | each row quotes the sentence that excluded it |
| Continuation rows (Day 2 restart, streamed final table) | 35 | not purchasable entries |
| Rows whose entry terms are **not published** at all | 84 | left blank and flagged |
| Rows the two earlier sessions classified differently | 14 | both verdicts and both excerpts published |
| Rankable events (buy-in **and** guarantee both published) | 41 | value = guarantee ÷ buy-in, descriptive only |
| Satellite rows kept out of the ranking | 32 | their prize is an entry seat |
| Best published guarantee per entry | $800 bounty, $75K GTD on 9 Dec — 93.8× | structure sheet 19 |
| Venetian mandatory resort fee | $55 + tax | [resort-fee page](https://www.venetianlasvegas.com/resort/resort-fee.html), re-read 2026-11-19 |
| Venetian poker-suite rates published by the property | from $119 (6 h cash) / $209 ($300+ tournament per night) | [official poker-rate page](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) — a published floor, not a quote |
| Venetian parking | $20/day hotel guest, $25 non-guest Fri–Sun, $40 valet, **free with 3 h+ of play** | [player parking](https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html) |
| Wynn / Encore resort fee, deposit and cancellation | $55 + tax, one night of room + tax deposit, 72-hour cancellation | [terms &amp; conditions 849338](https://www.wynnlasvegas.com/terms-and-conditions/849338) — published inside an offer whose stay window closed 2025-06-30, so applicability is flagged |
| Caesars Palace resort fee | **no single value**: $45–$60 + tax, waived for Diamond / Seven Stars | [Caesars corporate disclaimer](https://www.caesars.com/corporate/disclaimer) |
| Room tax | 13.38% = 12.5% + 0.88% (resort hotel inside the primary gaming corridor); the same ordinance puts a separately stated facility fee inside the taxable "rent" | [Clark County ordinance](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf) |
| Earliest start published anywhere on the Strip in this window | 10:10 AM (Venetian RaceDay Stack); the Horseshoe 9:00 AM claim could not be reproduced on a current official page | official schedule pages |
| Hotels with a verified route to a poker room | 1 of 5 (The Venetian / Palazzo → the room on Palazzo level 2, indoors, 0 min) | property directions pages |
| Official URLs tracked, and how many an automated re-check saw change | 101 tracked, 8 changed | [Source monitor](https://karagemop466-tech.github.io/Poker5/pages/monitor.html) |
| Review items published (blanks, gaps, disagreements, source oddities) | 38 | [Flagged for review](https://karagemop466-tech.github.io/Poker5/pages/flagged-review.html) |

## The single-entry standard, stated exactly

A row is listed as satisfying the policy only when its **own** structure sheet was
read in full, that sheet's event-number list includes the event, the format is one
day, and the text contains no re-entry, rebuy, add-on, double-entry, alternate-stack
or purchased-chip language. The label on those rows reads **"sheet read — no
re-entry language"**, never "guaranteed freezeout": the absence of a rule is not a
rule, and no source in this window states a one-entry limit for any Venetian event.
Where a source *does* publish paid re-entry, an add-on, a purchased stack, extra
flights or a membership-priced first buy-in, the event is moved to the
**Advantage / multi-entry** page with the sentence that caused it, and it is
excluded from the ranking and from the day plan. Satellites and tag-team events are
labelled separately and are not ranked, because their entry does not behave like a
single-player freezeout entry.

## Ranking rule

An event is ranked only when both its total entry fee and its guarantee are
confirmed from the official sheet, and no unresolved guarantee conflict is
attached to the row. The number published is **guarantee ÷ buy-in**, described as a
ratio, never as an expected return: field size, which decides whether a guarantee
is even reached, is not published in advance. Bounty events are ranked in their own
block because part of their guarantee is paid by knockout.

## What is deliberately blank

* **Dated room rates** for every hotel — the official booking engines need
  JavaScript and no official page states a rate for these dates. Rates are kept as
  a **dated log** (`data/bdcaf0bf/rates_log.json`) so a checkout total can be
  compared like-for-like; the trip calculator prints *Incomplete* instead of
  substituting a guess.
* **Off-property walking minutes** — no casino, hotel or county page publishes
  them. Only the same-complex route is verified as inside the 30-minute limit;
  every other pair keeps a Google Maps link so a reader can check it in seconds.
* **Finishing times** — not published. A duration is derived only from a sheet's own
  level count × level length plus three 15-minute breaks (89 of 247 rows can be
  derived at all), and it is labelled as arithmetic, not as a schedule.
* **Maximum-entry limits** — no sheet states a number, so `max_entries` is blank
  with the sentence "no maximum-entry number appears on the sheet".
* **Caesars Palace / Horseshoe resort fee**, **Bellagio / MGM Grand / ARIA**
  tournament rows and hotel terms for these dates, **South Point** structure
  sheets: no retrievable official page.

## Open decisions (the full list is on the site's Questions page)

1. Your exact dates, nightly ceiling and quality floor. The site fixes an explicit
   working assumption — a true nightly ceiling of **$250** derived from the
   property's own published rate floor plus its $55 fee at 13.38% — and labels it as
   an assumption, not a source claim. No quality floor is applied at all, because no
   official page publishes a comparable hotel quality rating.
2. Whether a satellite seat counts as an acceptable route into a main event.
3. Whether a hotel whose resort fee is published only as a range is acceptable.
4. Whether an 8:00 AM start is required at all: nothing on the Strip publishes one.
5. Whether a mapping service may be used as a walking-time source, or the walk has
   to be timed by hand.

## Where to look

* Site: https://karagemop466-tech.github.io/Poker5/
* Single-entry list and the rule: https://karagemop466-tech.github.io/Poker5/pages/single-entry.html
* What was excluded and why: https://karagemop466-tech.github.io/Poker5/pages/tournaments-double.html
* Day plan: https://karagemop466-tech.github.io/Poker5/pages/schedule.html
* Hotels and true cost: https://karagemop466-tech.github.io/Poker5/pages/hotels.html
* Flagged for review: https://karagemop466-tech.github.io/Poker5/pages/flagged-review.html
* Repo review: https://karagemop466-tech.github.io/Poker5/pages/repo-review.html

Confirm the schedule, the structure sheet and the hotel cancellation deadline on
the property's own page on the same day you pay: reconfirm before booking anything.
