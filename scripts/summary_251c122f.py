#!/usr/bin/env python3
"""Print a one-screen summary of the last official-source capture."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "c6087e2c")


def load(name, default=None):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    st = load("scrape_status.json", {}) or {}
    ev = load("events_verified.json", {}) or {}
    print("last scrape:", st.get("last_run"), "| rows:", st.get("schedule_rows"),
          "| sheets:", st.get("sheets_read"), "/", st.get("sheets_total"))
    for e in (st.get("errors") or [])[:10]:
        print("  error:", e)
    counts = (ev.get("counts") or {})
    print("verdicts:", json.dumps(counts.get("verdicts", {}), sort_keys=True))
    print("discrepancies:", len(ev.get("discrepancies") or []))
    for d in (ev.get("discrepancies") or [])[:15]:
        print("  !", d.get("kind"), d.get("date"), d.get("time"), d.get("event_no"))
    for k, s in (ev.get("sheets") or {}).items():
        print("  sheet {:>2}: events={} late={} lvl={} chips={} gtd={} fee={} multi={}".format(
            k, s.get("event_numbers"), s.get("late_registration_clock") or "-",
            s.get("level_minutes"), s.get("starting_chips"), s.get("guarantee"),
            s.get("house_fee"), s.get("adds_second_entry")))


if __name__ == "__main__":
    main()
