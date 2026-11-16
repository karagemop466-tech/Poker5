# Hotel Data — Las Vegas Strip (source of truth)

**Research date:** 2026-11-16. Scope: hotels within walking distance (≤ 30 minutes / ~1.5 miles) of the Strip poker tournament venues (Venetian, Wynn, Caesars, Horseshoe, ARIA, Bellagio, MGM Grand).
**True cost per night formula:** Base room rate + nightly resort fee + 13.38% Clark County room tax (applied to room rate AND resort fee) + daily self-parking (if charged to hotel guests).
**Priority:** Cost and quality higher than distance, but distance must be ≤ 30 minutes walking.
**Verification rule:** Resort fees verified where possible from official sources. Future (Nov/Dec 2026) room rates are date-dependent and were not consistently bookable from official sources; sample rates are flagged and attributed to source.

## Walking-distance hotel table

| # | Hotel | Tier / Quality | Approx. distance to Venetian | Walk time to Venetian | Resort fee / night (+ tax) | Self-parking / day (hotel guests) | Sample base rate (sample only — unverified) | True cost / night (formula) | Source | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| H1 | The Venetian / The Palazzo | Luxury (hosts DeepStack Extravaganza) | 0 mi (at venue) | 0 min | $55 + tax (~$62.36) | $20/day | $200–$600 (avg range, varies by date) | Base + $62.36 + tax + $20 | [Venetian hotel terms (official)](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) | Resort fee verified official; rate range third-party (unverified) |
| H2 | Wynn Las Vegas / Encore | Luxury (hosts WPT World Championship) | 0.5 mi | 10–15 min | $55 + tax (~$62.36) | Free (registered guests) | $176–$3,291 (sample dates Nov–Dec 2026) | Base + $62.36 + tax + $0 | [Wynn terms (official)](https://www.visitwynn.com/tc/index.cfm?term_id=850250) | Resort fee verified official; sample rates third-party (unverified) |
| H3 | ARIA Resort & Casino | Luxury | ~0.5 mi | ~10 min | $55 + tax (~$62.36) | $20/day | $82–$146 (all-in sample, Nov) | Base + $62.36 + tax + $20 | [ARIA review/terms (hoteltiplasvegas, Oct 2026)](https://hoteltiplasvegas.com/aria-las-vegas-review/) / [ARIA poker official](https://aria.mgmresorts.com/en/casino/poker.html) | Resort fee third-party (unverified against official); official ARIA page confirms poker room only |
| H4 | Bellagio | Luxury | ~0.9 mi | 18–25 min | $55 + tax (~$62.36) | $20/day | — | Base + $62.36 + tax + $20 | [Las Vegas resort fees list (lasvegasjaunt, Nov 2026)](https://www.lasvegasjaunt.com/resort-fees/) | Resort fee third-party (unverified); official Bellagio page confirms poker room only |
| H5 | Caesars Palace | Upscale-luxury | ~0.7 mi | ~14 min | $54.95 + tax (~$62.30) | Paid (free for Caesars Rewards Platinum+) | $99–$149 weeknights / $350–$450 weekends (sample) | Base + $62.30 + tax + parking | [Caesars Palace prices 2026 (lasvegaswonders)](https://lasvegaswonders.com/caesars-palace-prices/) / [Caesars official](https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip) | Resort fee third-party (unverified vs official); rates sample |
| H6 | MGM Grand | Large resort | ~1.2 mi | ~22–25 min | $50 + tax (~$56.69) | $20/day (unverified) | — | Base + $56.69 + tax + $20 | [Unleash Vegas Wynn guide (lists MGM $50)] / [PokerAtlas MGM (third-party)] | Resort fee third-party (unverified); official MGM page returns 500 |
| H7 | The Cosmopolitan | Upscale-luxury | ~0.8 mi | ~16 min | $55 + tax (~$62.36) | — | — | Base + $62.36 + tax | [Las Vegas resort fees list (lasvegasjaunt, Nov 2026)](https://www.lasvegasjaunt.com/resort-fees/) | Resort fee third-party (unverified) |

## How true cost is calculated (example)
Clark County room tax = 13.38% (applied to base rate + resort fee).
Example — Wynn at $176 base (sample Dec 17/22/23 2026):
- Base room: $176.00
- Resort fee: $55.00
- Subtotal: $231.00
- Tax 13.38%: $30.91
- Parking: $0 (free for registered guests)
- **True cost/night ≈ $261.91**

Example — Venetian at $200 base (sample):
- Base room: $200.00
- Resort fee: $55.00
- Subtotal: $255.00
- Tax 13.38%: $34.12
- Parking: $20.00
- **True cost/night ≈ $309.12**

## Notes
- Wynn/Encore and Venetian are AT their respective tournament venues (distance 0–0.5 mi) — best for an all-day playing schedule.
- Caesars Palace is ~0.7 mi (~14 min) from Venetian and on the same Center Strip corridor; Caesars Rewards Diamond/Seven Stars waive resort fee.
- MGM Grand official site (mgmgrandlasvegas.com) returned HTTP 500; its fee/parking are from third-party sources and unverified.
- Room rates change daily with demand and were not reliably bookable from official sources for Nov/Dec 2026 — treat all sample rates as unverified placeholders; user must confirm on official booking sites.
- Resort fees are mandatory and cannot be opted out (except loyalty-tier waivers at Caesars/MGM properties).
