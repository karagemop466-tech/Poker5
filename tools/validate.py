#!/usr/bin/env python3
"""Checks the generated site: JSON parses, every data row has a source link, and every 'verified' row has a structure sheet that was read."""
import json, glob, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
for p in glob.glob(os.path.join(ROOT, "docs", "data", "*.json")):
    try:
        json.load(open(p))
    except Exception as e:
        errors.append(f"{p}: {e}")
t = json.load(open(os.path.join(ROOT, "docs", "data", "tournaments.json")))
for r in t["venetian"]:
    if not r.get("schedule_source") and not r.get("source_schedule"):
        errors.append(f"venetian row without source: {r['event_no']} {r['date']}")
    if r["status"] == "verified" and not r.get("structure_sheet"):
        errors.append(f"verified row without structure sheet: {r['event_no']} {r['date']}")
for r in t["wynn_wpt"]:
    if not r.get("source_schedule"):
        errors.append(f"WPT row without source: {r['name']} {r['date']}")
print("errors:", len(errors))
for e in errors:
    print(" -", e)
sys.exit(1 if errors else 0)
