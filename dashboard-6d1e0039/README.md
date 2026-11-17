# dashboard-6d1e0039 — Strip poker & hotel dashboard (session 6d1e0039)

Static site, no build step at runtime. Regenerate with:

    python3 scripts/gen_6d1e0039_data.py     # data-6d1e0039/events.json (+ sources.json)
    python3 scripts/build_6d1e0039_site.py   # dashboard-6d1e0039/*.html

Scheduled source re-check: `scripts/recheck_6d1e0039.py` via
`.github/workflows/recheck-6d1e0039.yml` (every 6 hours). Results appear on `changes.html`.

Verification standard used here:
* every row links the official page/PDF it came from and carries a `last checked` date;
* a value the official source does not publish is rendered `blank`, never filled in;
* computed values (guarantee ÷ buy-in, fee, late-reg clock, estimated finish, trip totals)
  are labelled, and the inputs are all from official sources.

Open `index.html` for the executive summary, `flagged.html` for the twelve irregularities.
