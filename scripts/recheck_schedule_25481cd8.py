#!/usr/bin/env python3
"""Line-by-line diff of the official Venetian DSE IV schedule (transcribed in
data/ea99006a/official_schedule_2026-11-19.tsv) against the stored rows in
data/ea99006a/venetian.json. Writes data/ea99006a/schedule_recheck.json.

Compared per row: date, start time (24h), event number, event name (case-folded,
text after the first ' - ' descriptor removed on both sides), buy-in, guarantee
and the structure-sheet number in the stored source link.
A row with any mismatch is reported, never silently corrected.
"""
import json, re, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
TSV = ROOT / "data/ea99006a/official_schedule_2026-11-19.tsv"
VEN = ROOT / "data/ea99006a/venetian.json"
OUT = ROOT / "data/ea99006a/schedule_recheck.json"
CHECKED = "2026-11-19"


def to24(t):
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", t.strip(), re.I)
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return f"{h:02d}:{mi:02d}"


def money(s):
    s = str(s).replace(",", "")
    return float(re.sub(r"[^\d.]", "", s)) if re.search(r"\d", s) else None


def official_buyin(name):
    m = re.search(r"\$([\d,]+)", name)
    return float(m.group(1).replace(",", "")) if m else None


def official_gtd(name):
    if re.search(r"\$1 Mill GTD", name):
        return 1_000_000.0
    m = re.search(r"\$([\d,.]+)(K?) GTD", name)
    if not m:
        return None  # satellites: "2 seats", no $ guarantee
    v = float(m.group(1).replace(",", ""))
    return v * 1000 if m.group(2) == "K" else v


def base(name):
    return re.sub(r"\s+", " ", name.split(" - ")[0]).strip().lower()


def main():
    off = []
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        d, t, ev, name, sheet = line.split("\t")
        off.append(dict(date=d, start=to24(t), event_no=ev, name=name, sheet=sheet))
    ven = json.loads(VEN.read_text(encoding="utf-8"))
    if len(off) != len(ven):
        print(f"ROW COUNT DIFFERS: official {len(off)} vs stored {len(ven)}")
        sys.exit(1)
    rows, mism = [], 0
    for i, (o, s) in enumerate(zip(off, ven)):
        diffs = {}
        if o["date"] != s["date"]:
            diffs["date"] = [o["date"], s["date"]]
        if o["start"] != s["start"]:
            diffs["start"] = [o["start"], s["start"]]
        if str(o["event_no"]) != str(s["event_no"]):
            diffs["event_no"] = [o["event_no"], s["event_no"]]
        if base(o["name"]) != base(s["name"]):
            diffs["name"] = [o["name"], s["name"]]
        if official_buyin(o["name"]) != money(s["buyin"]):
            diffs["buyin"] = [official_buyin(o["name"]), s["buyin"]]
        og = official_gtd(o["name"])
        if og is not None and og != money(s["guarantee"]):
            diffs["guarantee"] = [og, s["guarantee"]]
        m = re.search(r"structure_(\d+)\.pdf", s.get("source", ""))
        if not m or m.group(1) != o["sheet"]:
            diffs["structure_sheet"] = [o["sheet"], m.group(1) if m else None]
        mism += bool(diffs)
        rows.append(dict(index=i, date=o["date"], start=o["start"], event_no=o["event_no"],
                         official_name=o["name"], stored_name=s["name"],
                         result="match" if not diffs else "mismatch", diffs=diffs))
    out = dict(
        checked_on=CHECKED,
        official_source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
        method="4 fetch chunks read 2026-11-19; transcription in official_schedule_2026-11-19.tsv; this script diffs it against venetian.json",
        rows_compared=len(rows), mismatches=mism, rows=rows,
    )
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"rows compared: {len(rows)}  mismatches: {mism}")
    for r in rows:
        if r["diffs"]:
            print(r["index"], r["date"], r["diffs"])
    sys.exit(1 if mism else 0)


if __name__ == "__main__":
    main()
