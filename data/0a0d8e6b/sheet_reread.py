"""Session 0a0d8e6b: structure-sheet re-read record + diff against data/ea99006a/venetian.json.

Every value in SHEETS was transcribed from the official sheet text fetched on 2026-11-19
(the fetch tool, URL pattern .../deepstack/2026/structures/dse_nov_2026-structure_<N>.pdf).
Nothing here is inferred: a field the sheet does not print is recorded as None.
Run: python3 data/0a0d8e6b/sheet_reread.py  (reads data/ea99006a/venetian.json, writes sheet_reread.json)
"""
import json, re, os, collections

BASE = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{}.pdf"
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

# sheet -> transcribed fields. events: event numbers printed on the sheet.
# gtd_by_event overrides guarantee when the sheet prints a different guarantee per event.
SHEETS = {
 1:  dict(title="$200 No Limit Hold'em Bounty (1Day)", events=[9,11,13,15,21,22,23,25,60,61,62,64], start={"*":"5:10 PM"}, chips=25000, level_min=30, late_reg="8 levels + Break (9:40 PM)", guarantee=8000, buyin=200, house_fee=40, prize_pool=160, bounty="$50 per elimination", entry_sentences=[], tda_reference=True, format="bounty"),
 5:  dict(title="$300 No Limit Hold'em (1Day)", events=[2,12], start={"*":"11:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (~ 4:55 PM)", guarantee=10000, buyin=300, house_fee=58, prize_pool=242, bounty=None, entry_sentences=[], tda_reference=True, format="NLH"),
 6:  dict(title="$400 No Limit Hold'em (1Day)", events=[10], start={"*":"11:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (~ 4:55 PM)", guarantee=15000, buyin=400, house_fee=65, prize_pool=335, bounty=None, entry_sentences=[], tda_reference=True, format="NLH"),
 7:  dict(title="$600 No Limit Hold'em (1Day)", events=[14,28,63], start={"*":"11:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (~ 4:55 PM)", guarantee=None, gtd_by_event={14:30000,63:30000,28:40000}, buyin=600, house_fee=90, prize_pool=510, bounty=None, entry_sentences=[], tda_reference=True, format="NLH"),
 11: dict(title="$600 No Limit Hold'em Bounty (1Day)", events=[16,30,54], start={"*":"11:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (4:55 PM)", guarantee=None, gtd_by_event={16:30000,30:40000,54:50000}, buyin=600, house_fee=90, prize_pool=510, bounty="$200 each elimination; $500 after money", entry_sentences=[], tda_reference=True, format="bounty"),
 15: dict(title="$300 No Limit Hold'em Bounty (1Day)", events=[29,31,34,38,42,50,51,53,55], start={"*":"5:10 PM"}, chips=25000, level_min=30, late_reg="8 levels + Break (9:40 PM)", guarantee=15000, buyin=300, house_fee=50, prize_pool=250, bounty="$100 per elimination", entry_sentences=[], tda_reference=True, format="bounty"),
 16: dict(title="$800 No Limit Hold'em Bounty (1Day)", events=[36], start={"*":"11:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (4:55 PM)", guarantee=75000, buyin=800, house_fee=100, prize_pool=700, bounty="$200; $500 after money", entry_sentences=[], tda_reference=True, format="bounty"),
 17: dict(title="$600 No Limit Hold'em Seniors (1Day), 50+ only", events=[24,32], start={"*":"10:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (~ 3:55 PM)", guarantee=40000, buyin=600, house_fee=90, prize_pool=510, bounty=None, entry_sentences=[], tda_reference=True, format="NLH"),
 18: dict(title="$200 No Limit Hold'em (1Day) RaceDay Stack", events=[3,4,5], start={"*":"10:10 AM"}, chips=30000, level_min="20/15", late_reg="6 levels + Break (~ 12:25 PM)", guarantee=None, buyin=200, house_fee=35, prize_pool=165, bounty=None, entry_sentences=[], tda_reference=True, format="NLH"),
 19: dict(title="$100 NLH LIPS Ladies (1Day), milestone satellite to Event #39", events=[33,37], start={"*":"4:10 PM"}, chips=20000, level_min=20, late_reg="6 levels + Break (~ 6:25 PM)", guarantee=None, buyin=100, house_fee=20, prize_pool=80, bounty=None, entry_sentences=[], tda_reference=True, format="satellite", seats="2 seats"),
 22: dict(title="$300 Pot Limit Omaha Double Board Bomb Pot (1Day)", events=[20], start={"*":"12:10 PM"}, chips=30000, level_min=30, late_reg="8 levels + break (~ 4:40 PM)", guarantee=10000, buyin=300, house_fee=58, prize_pool=242, bounty=None, entry_sentences=[], tda_reference=True, format="PLO"),
 23: dict(title="$600 Pot Limit Omaha Double Board Bomb Pot (1Day)", events=[57], start={"*":"12:10 PM"}, chips=30000, level_min=30, late_reg="8 levels + break (~ 4:40 PM)", guarantee=25000, buyin=600, house_fee=90, prize_pool=510, bounty=None, entry_sentences=[], tda_reference=True, format="PLO"),
 24: dict(title="$260 No Limit Hold'em (1Day), milestone satellite to Event #47", events=[41,44], start={"*":"4:10 PM"}, chips=20000, level_min=20, late_reg="6 levels + Break (~ 6:25 PM)", guarantee=None, buyin=260, house_fee=40, prize_pool=220, bounty=None, entry_sentences=[], tda_reference=True, format="satellite", seats="2 seats"),
 25: dict(title="$260 No Limit Hold'em Turbo (1Day), milestone satellite to Event #47", events=[45,46,48], start={45:"8:10 PM",46:"9:10 AM",48:"12:10 PM"}, chips=20000, level_min=15, late_reg="6 levels", guarantee=None, buyin=260, house_fee=35, prize_pool=225, bounty=None, entry_sentences=[], tda_reference=True, format="satellite", seats="2 seats"),
 26: dict(title="$400 Pot Limit Omaha Bounty (1Day)", events=[17], start={"*":"12:10 PM"}, chips=30000, level_min=30, late_reg="8 levels + break (~ 4:40 PM)", guarantee=15000, buyin=400, house_fee=60, prize_pool=340, bounty="$100 per elimination", entry_sentences=[], tda_reference=True, format="PLO"),
 27: dict(title="$600 Pot Limit Omaha Bounty (1Day)", events=[40], start={"*":"12:10 PM"}, chips=30000, level_min=30, late_reg="8 levels + break (~ 4:40 PM)", guarantee=25000, buyin=600, house_fee=90, prize_pool=510, bounty="$200 per elimination", entry_sentences=[], tda_reference=True, format="PLO"),
 28: dict(title="$600 BIG O (1Day)", events=[27], start={"*":"12:10 PM"}, chips=30000, level_min=30, late_reg="8 levels + break (~ 4:40 PM)", guarantee=25000, buyin=600, house_fee=90, prize_pool=510, bounty=None, entry_sentences=[], tda_reference=True, format="BIG O"),
 29: dict(title="$200 No Limit Hold'em (1Day)", events=[6], start={"*":"11:10 AM"}, chips=30000, level_min=30, late_reg="8 levels + Break (~ 3:40 PM)", guarantee=None, buyin=200, house_fee=40, prize_pool=160, bounty=None, entry_sentences=[], tda_reference=True, format="NLH"),
 30: dict(title="$200 No Limit Hold'em PKO Progressive Knock-Out Bounty (1Day)", events=[8], start={"*":"5:10 PM"}, chips=25000, level_min=30, late_reg="8 levels + Break (9:40 PM)", guarantee=8000, buyin=200, house_fee=40, prize_pool=160, bounty="$50 start, progressive split", entry_sentences=[], tda_reference=True, format="PKO"),
 31: dict(title="$600 No Limit Hold'em LIPS Poker Jingle Tag Team (1Day)", events=[35], start={"*":"10:10 AM"}, chips=40000, level_min=30, late_reg="8 levels + Break (~ 2:40 PM)", guarantee=10000, buyin=600, house_fee=80, prize_pool=510, bounty=None, entry_sentences=[], tda_reference=True, format="team", lips_flat_fee=10, team_rule="two-person teams rotate players every level; Female/Female or Female/Male"),
 33: dict(title="$600 No Limit Hold'em LIPS Kings and Queens Bounty (1Day)", events=[43], start={"*":"11:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (4:55 PM)", guarantee=30000, buyin=600, house_fee=80, prize_pool=510, bounty="$200 per elimination", entry_sentences=[], tda_reference=True, format="bounty", lips_flat_fee=10),
 34: dict(title="$1,100 No Limit Hold'em PKO Progressive Knock-Out Bounty (1Day)", events=[52], start={"*":"11:10 AM"}, chips=40000, level_min=30, late_reg="10 levels + Break (4:55 PM)", guarantee=75000, buyin=1100, house_fee=130, prize_pool=970, bounty="$200 start, progressive split", entry_sentences=[], tda_reference=True, format="PKO"),
}

def norm_time(t):
    """Return minutes after midnight for '11:10', '17:10', '5:10 PM', '09:10' etc."""
    m = re.match(r"\s*(\d{1,2}):(\d{2})\s*([AaPp][Mm])?\s*$", t or "")
    if not m:
        return (t or "").strip().upper()
    h, mi, ap = int(m.group(1)), int(m.group(2)), (m.group(3) or "").upper()
    if ap == "PM" and h != 12: h += 12
    if ap == "AM" and h == 12: h = 0
    if not ap and h < 7: h += 12  # bare evening times in the stored data (e.g. '17:10' is 24h, handled above)
    return h * 60 + mi

def main():
    rows = json.load(open(os.path.join(ROOT, "data/ea99006a/venetian.json")))
    diffs, checked = [], 0
    for r in rows:
        m = re.search(r"structure_(\d+)\.pdf", r.get("source", ""))
        if not m:
            continue
        sh = int(m.group(1))
        if sh not in SHEETS:
            continue
        s = SHEETS[sh]
        ev = int(r["event_no"]) if str(r.get("event_no", "")).isdigit() else None
        if ev is None or ev not in s["events"]:
            diffs.append(dict(event=r.get("event_no"), sheet=sh, field="event_no", stored=r.get("event_no"), sheet_value=s["events"], kind="event not printed on this sheet"))
            continue
        checked += 1
        def cmp(field, stored, sheet_val):
            if sheet_val is None:
                return
            if field == "start":
                ok = norm_time(stored) == norm_time(sheet_val)
            elif isinstance(sheet_val, str) and isinstance(stored, str):
                ok = re.sub(r"\s+", "", stored).lower() == re.sub(r"\s+", "", sheet_val).lower()
            else:
                ok = stored == sheet_val
            if not ok:
                diffs.append(dict(date=r.get("date"), event=ev, sheet=sh, field=field, stored=stored, sheet_value=sheet_val))
        st = s["start"].get(ev, s["start"].get("*"))
        cmp("start", r.get("start"), st if st is None else st)
        cmp("buyin", r.get("buyin"), s["buyin"])
        g = s.get("gtd_by_event", {}).get(ev, s.get("guarantee"))
        if g is not None:
            stored_g = r.get("guarantee")
            try: stored_g = int(str(stored_g).replace(",", "").replace("$", "")) if stored_g not in (None, "") else None
            except ValueError: pass
            cmp("guarantee", stored_g, g)
        cmp("chips", r.get("chips") and int(str(r.get("chips")).replace(",", "")), s["chips"])
        cmp("late_reg", r.get("late_reg"), s["late_reg"])
        hf = re.search(r"\$?([\d,]+)", str(r.get("house_fee") or ""))
        cmp("house_fee", int(hf.group(1).replace(",", "")) if hf else None, s["house_fee"])
        pp = re.search(r"\$([\d,]+) of every", str(r.get("to_prize_pool") or ""))
        cmp("prize_pool", int(pp.group(1).replace(",", "")) if pp else None, s["prize_pool"])
    out = dict(
        session="0a0d8e6b", retrieved="2026-11-19",
        method="Each sheet fetched from the official Venetian structure-sheet URL on 2026-11-19 and transcribed; the stored row fields are compared mechanically. Sheets not in SHEETS were not re-read in this session.",
        sheets_reread=sorted(SHEETS.keys()), sheets_not_reread=[n for n in range(1,38) if n not in SHEETS],
        rows_compared=checked, field_mismatches=len(diffs), mismatches=diffs,
        sheet_urls={str(n): BASE.format(n) for n in sorted(SHEETS)},
        sheets={str(n): {k: v for k, v in SHEETS[n].items()} for n in sorted(SHEETS)},
    )
    with open(os.path.join(os.path.dirname(__file__), "sheet_reread.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("rows compared", checked, "mismatches", len(diffs))
    for d in diffs: print(d)

if __name__ == "__main__":
    main()
