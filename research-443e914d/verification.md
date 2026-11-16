# Verification log (this session)

Purpose: line-by-line check of each single-entry row against the official Venetian schedule PDF and DSE event page.
Method: date, weekday, start time, buy-in, and guaranteed amount compared to the official values read this session (schedule PDF chunks 0–1; DSE event page chunks 1–3). Sheet-level fields (house fee, chips, late-registration close) for rows #58, #60–62, #63, #64 were read from structure sheets 1, 7, and 8 and match the table.
Result: all 36 single-entry rows match

| Event | Date | Start | Buy-in | Guarantee | Check | Reference |
|---|---|---|---|---|---|---|
| #2 | Wed Nov 18 | 11:10 AM | $300 | $10,000 | match | schedule |
| #9 | Tue Nov 24 | 5:10 PM | $200 | $8,000 | match | schedule |
| #10 | Wed Nov 25 | 11:10 AM | $400 | $15,000 | match | schedule |
| #11 | Wed Nov 25 | 5:10 PM | $200 | $8,000 | match | schedule |
| #12 | Thu Nov 26 | 11:10 AM | $300 | $10,000 | match | schedule |
| #13 | Thu Nov 26 | 5:10 PM | $200 | $8,000 | match | schedule |
| #14 | Fri Nov 27 | 11:10 AM | $600 | $30,000 | match | schedule |
| #15 | Fri Nov 27 | 5:10 PM | $200 | $8,000 | match | schedule |
| #16 | Sat Nov 28 | 11:10 AM | $600 | $30,000 | match | schedule |
| #18 | Sat Nov 28 | 5:10 PM | $200 | $20,000 | match | schedule+page |
| #21 | Sun Nov 29 | 5:10 PM | $200 | $8,000 | match | schedule+page |
| #22 | Mon Nov 30 | 5:10 PM | $200 | $8,000 | match | schedule+page |
| #23 | Tue Dec 01 | 5:10 PM | $200 | $8,000 | match | schedule+page |
| #25 | Wed Dec 02 | 5:10 PM | $200 | $8,000 | match | schedule+page |
| #27 | Thu Dec 03 | 12:10 PM | $600 | $25,000 | match | schedule+page |
| #28 | Sun Dec 06 | 11:10 AM | $600 | $40,000 | match | schedule |
| #29 | Sun Dec 06 | 5:10 PM | $300 | $15,000 | match | schedule |
| #30 | Mon Dec 07 | 11:10 AM | $600 | $40,000 | match | schedule |
| #31 | Mon Dec 07 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #34 | Tue Dec 08 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #36 | Wed Dec 09 | 11:10 AM | $800 | $75,000 | match | page |
| #38 | Wed Dec 09 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #42 | Thu Dec 10 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #50 | Sun Dec 13 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #51 | Mon Dec 14 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #52 | Tue Dec 15 | 11:10 AM | $1,100 | $75,000 | match | schedule+page |
| #53 | Tue Dec 15 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #54 | Wed Dec 16 | 11:10 AM | $600 | $50,000 | match | schedule+page |
| #55 | Wed Dec 16 | 5:10 PM | $300 | $15,000 | match | schedule+page |
| #57 | Thu Dec 17 | 12:10 PM | $600 | $25,000 | match | schedule+page |
| #58 | Sat Dec 19 | 5:10 PM | $200 | $20,000 | match | page |
| #60 | Sun Dec 20 | 5:10 PM | $200 | $8,000 | match | schedule+page |
| #61 | Mon Dec 21 | 5:10 PM | $200 | $8,000 | match | schedule+page |
| #62 | Tue Dec 22 | 5:10 PM | $200 | $8,000 | match | schedule+page |
| #63 | Wed Dec 23 | 11:10 AM | $600 | $30,000 | match | schedule+page |
| #64 | Wed Dec 23 | 5:10 PM | $200 | $8,000 | match | schedule+page |

## Not verified in this session
- Structure-sheet fields for rows #02–#57 (house fee, chips, late-registration, bounty) were recorded in an earlier session. They are not re-read here.
- Structure sheets for flight/multi-day events linked from the event page were not fetched (see the multi-entry data file).
- Single-entry status of Venetian events without a fetched sheet is unconfirmed; those events are listed in the Flagged for Review page.
- Walking distances, nightly room rates, and room tax were not verified (see the hotel flags).
