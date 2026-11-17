# Executive summary — Las Vegas Strip poker trip (as of the 2026-11-17 capture)

Generated from `data/c6087e2c/events_verified.json`. Every figure below is
reproduced on the live site with its source link; the site is the authoritative
version.

## The plan the evidence supports

A Strip poker trip between **Mon Nov 16, 2026** and **Wed Dec 23, 2026**, built on
the **55** Venetian DeepStack Extravaganza IV rows that pass the single-entry test,
with a second event on **11 of the 38** scheduled days, and hotel nights whose
resort fee and tax are official while the nightly room rate is read from the
official booking page for the chosen dates.

## Verified facts

| Fact | Value | Source |
|---|---|---|
| Scheduled rows read from the official Venetian page | 94 | [DSE IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) |
| Distinct structure-sheet PDFs downloaded and read | 37 of 37 | links stored per row in `structures.json` |
| Confirmed single-entry rows | 55 | each row links its sheet |
| Multi-flight / multi-entry rows | 28 | separate section |
| Restart rows (Day 2 / Day 3 / final table) | 11 | shown as continuations |
| Official source disagreements published | 3 guarantee conflicts | shown on the row and on Flagged |
| Hotel resort fees confirmed | Venetian/Palazzo $55, Wynn/Encore $55, Bellagio $55, ARIA $55, MGM Grand $50 | each hotel's own page |
| Room tax | 13.38% (resort hotel in the primary gaming corridor) | [Clark County ordinance](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf) |
| Earliest official tournament start on the Strip | 9:00 AM (Horseshoe, 6 daily events) | [Caesars official page](https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip) |
| Venetian's earliest full-tournament start | 10:10 AM | official schedule |

## What is confirmed single-entry

A row earns that label only when its **own** structure sheet was read, the sheet's
event-number list includes that event, the format is one day, and the text contains
no re-entry, rebuy, add-on, double-entry, alternate-stack or purchased-chip
language. The standard is published on the site's Sources & method page so it can
be challenged.

## What is deliberately blank

* **Room rates** — dynamic; stored as a dated log of booking-page snapshots, never
  as one fixed value.
* **Off-property walking times** — no casino publishes one; only on-property routes
  (0 minutes) pass the 30-minute filter.
* **Finishing times** — not published; the site derives a playing-day length from
  each sheet's late-registration level count and labels it as derived.
* **Caesars Palace / Horseshoe resort fees** — no official page found.
* **Bellagio, MGM Grand, ARIA tournament rows** — the official material is undated,
  stale, or absent.

## Open decisions (full list on the site's Questions page)

1. Trip dates, nights and party size.
2. A nightly cap and a hotel quality standard (no official quality score exists).
3. Whether a named map service may be used as the walking-time source.
4. Whether booking rates are read by hand (dated log) or linked out.

## Where to look

* Site: https://karagemop466-tech.github.io/Poker5/
* Flagged for review: https://karagemop466-tech.github.io/Poker5/pages/flagged.html
* Questions: https://karagemop466-tech.github.io/Poker5/pages/qa.html
* Suggestions: https://karagemop466-tech.github.io/Poker5/pages/suggestions.html
