# Executive summary — Las Vegas Strip poker-trip research

**Evidence snapshot:** official-source records last checked/captured on **2026-11-19**. This is a snapshot, not a live booking quote. The public site is the detailed, source-linked version: <https://karagemop466-tech.github.io/Poker5/>.

## What the current evidence supports

The repository's automatically selected planning scenario is **check-in 2026-12-06, check-out 2026-12-13 (7 nights)**, giving seven playing dates, Dec 6–12. The selection was computed from the current Venetian schedule capture, not provided by a traveler. Its scenario inputs include 12 Venetian full-field entries with approximately **$335,000 in published guarantees**, plus 7 satellites into the $2,200 PokerAtlas Championship. These are schedule totals, not expected winnings and not a guarantee of playing all entries. The dashboard gives each day a primary event and a conditional fallback; finish times are not official, so the sequence is not represented as certain.

For this Venetian series, **94 scheduled rows** were captured and **37 of 37 linked structure sheets** were read. **53 rows meet the site's S1 rule-evidence test** and 41 are classified as multi-entry. Under S1, "confirmed single-entry" means the event's own sheet was read and no rule grants a repeat entry, rebuy, add-on, or additional buy-in, with multi-flight and restart formats excluded. **None of the sheets explicitly promises a one-entry maximum.** S1 is therefore an evidence-based classification, not a freezeout guarantee from the venue; this limitation remains flagged. Bounty, multi-flight, satellite, and other advantage/repeat-entry formats are separated rather than presented as ordinary single-entry recommendations.

## Comparison and ranking limits

The tournament tables expose buy-in, house fee / prize-pool share, published guarantee, start time, structure details, entry-rule basis, and source links where the official material provides them. An event is not ranked as a best-value pick unless its total entry fee and guarantee are both confirmed. The published guaranteed-pool ÷ entry-fee ratio is descriptive arithmetic only—not a forecast of returns or an estimate of a player's chance to win. Bounty and flight events are labeled separately because the guarantee does not describe their full prize mechanics or repeated-entry opportunities.

A date-matched, verified hotel quote is **not available for the selected stay**. The dated rate log contains observations for other date windows/occupancies and incomplete booking-engine results; they are not comparable to one another or to Dec 6–13 for two adults. What *is* now confirmed for the Venetian, each from the property's own page on 2026-11-19, is everything the stay adds around the room rate: the **$55 plus-tax resort fee**, **$20 per night registered-guest self-parking** ($40 valet, free for the day with 3+ hours of poker play), a **24-hour cancellation deadline** on the published refundable rate, the **first-night deposit** billed at confirmation, a **$150 per night incidental hold**, and **11:00 a.m. check-out** with 3:00 p.m. check-in. That is $82.36 of mandatory non-room cost per night ($576.51 over the 7-night scenario) — derived arithmetic on published figures, labelled as such. Only the room rate is missing, so no complete trip-cost total should be treated as known until an itemized quote for the actual dates exists; the calculator prefills the two numbers the official pages do support and stays Incomplete without them.

## Hotel and route evidence

- Venetian official resort-fee terms state **$55 plus tax per night**; see the [official resort-fee page](https://www.venetianlasvegas.com/resort/resort-fee.html). The Venetian poker-suite page advertises starting rates, but these are conditional starting figures, not a quote for the selected dates.
- Wynn terms include a **$55 plus tax** resort fee for the cited offer terms; confirm the fee on the actual selected rate plan at the [official Wynn terms page](https://www.wynnlasvegas.com/terms-and-conditions/DK26WLV2).
- The current tax calculation uses **13.38%** from the linked [Clark County room-tax ordinance](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf). Confirm applicable tax and fee terms during booking.
- Hotel rate observations preserve stay dates, occupancy, checkout total, nightly average, resort fee, tax, parking, cancellation deadline, timestamp, source, and caveats. Missing fields remain blank. Like-for-like comparison requires the same stay, occupancy, and room class.
- The Requirements page maps every line of the brief to the control that implements it, with each gap's blocking source: <https://karagemop466-tech.github.io/Poker5/pages/requirements.html>.
- Only on-property hotel-to-room routes have confirmed zero-minute walk entries. Cross-property walking times are blank/flagged; the 30-minute filter does not convert an unverified route into a verified one.

The scheduled publisher is now guarded against silent regressions: `recheck-ea99006a` re-derives the published records through `scripts/integrate_b3be876c.py`, and that generator was not idempotent against the corrected data (it rewrote flag F47, questions Q01/Q11 and suggestions S10/S11, and wrote `trip.check_out` as the last playing day of a 7-night window). It now carries the corrected text, and `scripts/check_idempotency_0fd4c550.py` runs in CI to fail any scheduled change that is not a date. Published as flag F56.

**The 8 a.m. start the brief asks for does not exist in any published Strip schedule.** Counted from every captured row, the earliest enterable start anywhere in the three schedules is 09:10 (a Venetian satellite); inside the recommended window the earliest is 11:00 on 6-7 December and 09:10 on 12 December. Restart and final-table rows are excluded because they cannot be entered. The Day schedule page now states this day by day and plans from each day's earliest published start, and suggestions S15/S16 cover the two open choices (chase an unlisted early turbo by phone; whether parking belongs inside "true cost per night").

**The recommended window was re-read live and matches row for row.** On 2026-11-19 the 28 schedule rows for 6-13 December were read again from the official Venetian page and compared field by field (date, start, event number, event text, buy-in, guarantee, structure-sheet number) with the published record: 28 of 28 matched, 0 value disagreements (flag F58, method in `scripts/verify_window_0fd4c550.py`, transcription in `data/ea99006a/window_live_2026-11-19_0fd4c550.tsv`). Quality CI re-runs the comparison on every build.

## Monitoring and data-quality caveats

The latest stored schedule/sheet capture is dated 2026-11-19, but the checked-in value-level monitor summary records **no live value-level run yet**. Therefore, no changed-value badge means “not recorded as re-checked,” not “verified unchanged.” The legacy `data/c6087e2c/events_verified.json` snapshot also still marks events #18 and #58 as single-entry; its keyword-based check misses sheet 8's “subsequent buy in's” rule. The canonical dashboard correctly excludes both as multi-entry; the legacy discrepancy is published on Flagged for review and has been logged for repair.

## Questions that still prevent a firm decision

1. **Are any candidate Venetian events explicitly guaranteed to be freezeouts?** No sheet states a one-entry cap. Request a written event-number-specific policy from the tournament desk before relying on S1.
2. **What is the trip's actual budget and quality floor?** The displayed budget/quality settings are an automatic scenario based on repository evidence, not traveler preferences or an independent hotel rating. They must not be mistaken for a user-approved constraint.
3. **What are the true hotel totals for Dec 6–13 and the intended occupancy?** Obtain official booking checkout totals, nightly average, room charge, mandatory resort fee and tax, parking, and cancellation deadline; keep the timestamp and exact room class.
4. **Which off-property hotels are within a 30-minute walk?** No official walking times are currently verified for cross-property pairs. Check a chosen maps service from the official hotel address to the poker-room address and retain the route/date as evidence.
5. **Can two same-day events actually be played consecutively?** Official finish times are missing. Confirm actual elapsed duration and late-registration cutoffs with the room; until then evening entries are conditional fallbacks only.
6. **Which rankings are defensible?** Re-check total entry fee and guarantee for each candidate, including fee splits and whether bounty pools are additional, before comparing ratios.

## Suggested next steps

1. Ask the Venetian tournament desk for written one-entry/no-rebuy/no-add-on terms for specific candidate event numbers; attach the dated response to the row.
2. Choose the trip dates, occupancy, budget, and acceptable hotel tier as a planning scenario; compare only official booking quotes for the same stay and room class.
3. Keep one event per day as the baseline. Add a second only after the earlier event's plausible duration and exit time leave a realistic start window.
4. Record measured walking routes with the official property addresses and route timestamp; do not mark the 30-minute test passed without evidence.
5. Reconfirm schedule, structure sheets, rate plan, fees, parking, and cancellation policy immediately before any non-refundable booking.

## Official sources for manual review

- [Venetian DeepStack Extravaganza IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html)
- [Venetian 2026 structure sheets](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf) — each tournament row links its own sheet.
- [WPT World Championship 2026 schedule](https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf)
- [WPT World Championship structure sheet](https://wptmedia-mig.s3.amazonaws.com/wp-content/uploads/2026/11/WPT_World_Championship_Structures.pdf)
- [Venetian resort-fee terms](https://www.venetianlasvegas.com/resort/resort-fee.html)
- [Wynn offer terms](https://www.wynnlasvegas.com/terms-and-conditions/DK26WLV2)
- [Clark County room-tax ordinance](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf)

For detailed records, open the site's [questions](https://karagemop466-tech.github.io/Poker5/pages/questions.html), [suggestions](https://karagemop466-tech.github.io/Poker5/pages/suggestions.html), [hotels](https://karagemop466-tech.github.io/Poker5/pages/hotels.html), [routes](https://karagemop466-tech.github.io/Poker5/pages/routes.html), [verification log](https://karagemop466-tech.github.io/Poker5/pages/verification.html), and [flagged-for-review](https://karagemop466-tech.github.io/Poker5/pages/flagged-review.html) pages.
