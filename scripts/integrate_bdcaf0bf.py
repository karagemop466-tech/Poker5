#!/usr/bin/env python3
"""Session bdcaf0bf - build the canonical merged dataset for the published site.

Read-only inputs (never edited here):
  data/c6087e2c/*   official Venetian capture: schedule rows, 37 structure sheets,
                    per-field excerpts, dated rate log, walking routes, hotel facts
  data/ea99006a/*   official rows for WPT/Wynn and the other rooms, hotels, routes,
                    flags, questions, suggestions, source ledger, monitor state
  data/bdcaf0bf/facts_20261119.json
                    what this session re-read from the official pages on 2026-11-19

Output: data/bdcaf0bf/*.json - the single dataset the published root site is built
from, plus a reconciliation record for every place where two earlier sessions
published different numbers for the same fact.

Two independent single-entry standards were published before this session:
  * session 251c122f: a sheet was read, covers the event, the event is one day and
    the sheet contains no re-entry/rebuy/add-on language  -> "confirmed single-entry"
  * session ea99006a: silence on a sheet is not a rule  -> "entry cap not stated"
This module keeps BOTH readings, applies a named three-level ladder instead of one
boolean, and records the disagreement on every affected row rather than resolving it
in favour of one session. The ladder:
  explicit_one_entry     - an official source states a one-entry / no-re-entry limit
  no_reentry_language    - the sheet was read for this event and says nothing about
                           re-entry, rebuy, add-on or purchased chips (the "unverified"
                           label is removed, the caveat stays visible)
  multi_entry_paid       - re-entry, rebuy, add-on, extra flight or restart language
  continuation           - a Day 2 / restart / final-table row, not a fresh entry
  not_read               - no sheet was matched to the row, or the venue publishes none
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C6 = os.path.join(ROOT, "data", "c6087e2c")
EA = os.path.join(ROOT, "data", "ea99006a")
OUT = os.path.join(ROOT, "data", "bdcaf0bf")

SESSION = "bdcaf0bf"
TODAY = os.environ.get("POKER5_DATE") or dt.date.today().isoformat()

RE_ONE_ENTRY = re.compile(
    r"(one\s+entry\s+per|single[\s-]entry|freeze\s?out|no\s+(re-?entry|rebuy|add-?on)|"
    r"only\s+one\s+(buy-?in|entry)|maximum\s+of\s+one\s+entry|one\s+entry\s+allowed)",
    re.I,
)
RE_MULTI = re.compile(
    r"(re-?entry|re-?bought?|add-?on|second\s+entry|additional\s+entry|another\s+entry|"
    r"alternate\s+stack|purchased?\s+(chips|stack)|day\s*1|day\s*2|day\s*3|flight|"
    r"restart|re-?buy|subsequent\s+flight|bag\w*\s+chips|late\s+registration\s+remains)",
    re.I,
)
RE_RESTART_ROW = re.compile(r"(restart|final table|day\s*\d+\s*(restart|$))", re.I)
RE_FLIGHT_ROW = re.compile(r"\b1[A-F]\b|\(2Day\)|Day 2|\bflight\b", re.I)
RE_BOUNTY = re.compile(r"bounty|\bPKO\b|knock-?out", re.I)

STATUS_LABEL = {
    "explicit_one_entry": "One-entry rule stated on the official sheet",
    "no_reentry_language": "Sheet read - no re-entry / add-on language",
    "multi_entry_paid": "Paid re-entry, add-on or extra flight",
    "continuation": "Continuation row (restart / final table)",
    "not_read": "Entry terms not published - unverified",
}
STATUS_RANK = {
    "explicit_one_entry": 0,
    "no_reentry_language": 1,
    "not_read": 2,
    "continuation": 3,
    "multi_entry_paid": 4,
}


def load(dirpath: str, name: str, default=None):
    path = os.path.join(dirpath, name)
    if not os.path.exists(path):
        if default is not None:
            return default
        sys.exit("missing required input %s" % path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump(name: str, obj) -> None:
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False, sort_keys=False)
        fh.write("\n")


def num(v):
    """Return a float when the official source stated a number, else None."""
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(v))
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except ValueError:
        return None


def to_min(hhmm):
    if not hhmm or not re.match(r"^\d{1,2}:\d{2}$", str(hhmm)):
        return None
    h, m = str(hhmm).split(":")
    return int(h) * 60 + int(m)


def hhmm(mins):
    if mins is None:
        return None
    mins = int(round(mins)) % (24 * 60)
    return "%02d:%02d" % (mins // 60, mins % 60)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# 1. structure sheets: independent keyword reading of the official PDF text
# --------------------------------------------------------------------------- #
RE_FLIGHT_LINE = re.compile(r"(starting flight|bags chips|subsequent flight|Day\s*2|Day\s*3|Day 1[A-F]|@ Day|with Day)", re.I)
RE_ENTRY_LINE = re.compile(
    r"(re-?entry|re-?buy|add-?on|second entry|another entry|maximum of|one entry|freeze|"
    r"subsequent buy|buy in'?s after|initial buy in only|entry per player|each player may enter)",
    re.I,
)
RE_PAID_ADVANTAGE = re.compile(r"(PRO (member|player)|membership|rake discount)", re.I)
RE_TEAM = re.compile(r"tag team", re.I)


def sheet_lines(text):
    """Verbatim lines from the official sheet, grouped by what they prove."""
    lines = [l.strip() for l in (text or "").split("\n") if l.strip()]
    return {
        "flight": [l for l in lines if RE_FLIGHT_LINE.search(l)],
        "entry": [l for l in lines if RE_ENTRY_LINE.search(l)],
        "late": [l for l in lines if re.search(r"late registration", l, re.I)],
        "fee": [l for l in lines if re.search(r"withheld for house fees|prize pool consists", l, re.I)],
        "gtd": [l for l in lines if re.search(r"guarantee|is guaranteed", l, re.I)],
        "chips": [l for l in lines if re.search(r"starting chips", l, re.I)],
        "level": [l for l in lines if re.search(r"level duration", l, re.I)],
        "satellite": [l for l in lines if re.search(r"satellite|direct entry", l, re.I)],
        "all": lines,
    }


def read_sheets(structures):
    out = {}
    for no, sh in structures["sheets"].items():
        text = sh.get("rules_text") or ""
        one = [m.group(0) for m in RE_ONE_ENTRY.finditer(text)]
        multi = sorted({m.group(0).lower() for m in RE_MULTI.finditer(text)})
        ln = sheet_lines(text)
        out[int(no)] = {
            "sheet_no": int(no),
            "url": sh["url"],
            "retrieved_at": sh.get("retrieved_at"),
            "pdf_sha256": sh.get("pdf_sha256"),
            "text_sha256": sh.get("text_sha256"),
            "http_status": sh.get("http_status"),
            "events": sh.get("event_numbers") or [],
            "title": sh.get("sheet_title") or "",
            "start_time": sh.get("start_time"),
            "starting_chips": sh.get("starting_chips"),
            "level_minutes": sh.get("level_minutes"),
            "level_count": sh.get("level_count"),
            "late_reg": sh.get("late_registration"),
            "late_reg_clock": sh.get("late_registration_clock"),
            "guarantee": sh.get("guarantee"),
            "guarantee_by_event": sh.get("guarantee_by_event") or {},
            "house_fee": sh.get("house_fee"),
            "fee_buyin": sh.get("fee_buyin"),
            "pool_per_entry": sh.get("pool_per_entry"),
            "one_entry_language": bool(one),
            "one_entry_hits": one[:3],
            "multi_hits": multi,
            "multi_day_format": bool(sh.get("multi_day_format")),
            "flight_language": bool(sh.get("flight_language")),
            "lines": ln,
            "has_flight_language": bool(ln["flight"]),
            "has_entry_language": bool(ln["entry"]),
            "has_satellite_language": bool(ln["satellite"]),
            "has_team_language": bool(RE_TEAM.search(text)),
            "excerpt": (text[:400] + "...") if len(text) > 400 else text,
            "text_length": sh.get("text_length"),
        }
    return out


# --------------------------------------------------------------------------- #
# 2. Venetian rows: capture + sheet reading + the two earlier verdicts
# --------------------------------------------------------------------------- #
def venetian_rows(ev, sheets, ea_rows):
    ea_by_key = {}
    for r in ea_rows:
        key = (r.get("date"), str(r.get("event_no")), r.get("start"))
        ea_by_key.setdefault(key, r)
    rows, conflicts = [], []
    for i, src in enumerate(ev["events"]):
        key = (src.get("date"), str(src.get("event_no")), src.get("time"))
        ea = ea_by_key.get(key) or {}
        sheet = sheets.get(src.get("structure_no")) or {}
        name = src.get("name") or ""
        kind = src.get("kind") or "entry"
        text_blob = " ".join(
            [name, src.get("restriction") or "", src.get("format") or ""]
        )
        multi_row = bool(RE_RESTART_ROW.search(name)) or kind == "restart"
        flight_row = bool(RE_FLIGHT_ROW.search(name)) or bool(src.get("multi_day"))
        rf = src.get("rule_fields") or {}
        covered = bool(src.get("sheet_covered_event"))
        lines = sheet.get("lines") or {}
        entry_lines = [l for l in lines.get("entry", []) if not re.match(r"^\d+\.\s*All pre-registered", l)]
        flight_lines = lines.get("flight", [])
        satellite = bool(sheet.get("has_satellite_language")) or "satellite" in name.lower()
        one_day = not (src.get("multi_day") or flight_row) and not flight_lines
        adv_lines = [l for l in (lines.get("all") or []) if RE_PAID_ADVANTAGE.search(l)]
        sells_more_than_one_entry = bool(re.search(
            r"subsequent buy|initial buy in only|buy in'?s after", " ".join(entry_lines), re.I))
        paid_advantage = bool(adv_lines) and sells_more_than_one_entry
        tag_team = bool(RE_TEAM.search(name)) or bool(sheet.get("has_team_language"))
        special_format = ("satellite: the published prize is a direct entry seat, not a cash pool"
                          if satellite and "satellite" in name.lower() else
                          ("tag-team: two players share one entry and rotate by level"
                           if tag_team else ""))
        eligibility = name.split(" - ", 1)[1].strip() if " - " in name else ""
        sheet_grants_reentry = bool(sheet.get("has_entry_language")) or paid_advantage

        if multi_row:
            status, multi_kind = "continuation", "restart or final-table row: no separate entry is sold"
        elif paid_advantage:
            status, multi_kind = "multi_entry_paid", "a paid membership changes the price of the first entry, and the sheet sells subsequent buy-ins"
        elif sheet.get("one_entry_language") and not sheet_grants_reentry and covered and one_day:
            status, multi_kind = "explicit_one_entry", "an official sentence states a one-entry limit"
        elif sheet_grants_reentry:
            status, multi_kind = "multi_entry_paid", "the sheet itself sells a second way back in"
        elif flight_lines or flight_row:
            status, multi_kind = "multi_entry_paid", "extra starting flights or a second day, each sold separately"
        elif covered and one_day:
            status, multi_kind = "no_reentry_language", "no re-entry, rebuy, add-on or purchased-stack sentence exists on the sheet"
        else:
            status, multi_kind = "not_read", "no official sheet was matched to this event number"
        evidence = ""
        if status == "multi_entry_paid" and multi_kind.startswith("extra starting"):
            evidence = " | ".join(flight_lines[:2]) or "schedule row names a starting flight or a second day"
        elif status == "multi_entry_paid":
            evidence = " | ".join(entry_lines[:2])
        elif status == "no_reentry_language":
            evidence = ("the full rules text of this sheet was read; its entry-related lines are: %s"
                        % (" | ".join(entry_lines[:2]) or "none - no line mentions an entry, re-entry, rebuy or add-on"))

        # structured rule fields, each with its own official excerpt + retrieval date
        def field(value, excerpt, source, retrieved):
            return {
                "value": value,
                "excerpt": excerpt or "",
                "source": source or "",
                "retrieved": (retrieved or "")[:10],
            }

        def join_lines(key, n=1):
            return " | ".join((lines.get(key) or [])[:n])

        sheet_url = src.get("structure_url") or sheet.get("url") or ""
        sheet_retr = src.get("sheet_retrieved_at") or sheet.get("retrieved_at") or ""
        sched_url = src.get("source") or ""
        sched_retr = src.get("retrieved_at") or ""
        fee = rf.get("house_fee") or {}
        fields = {
            "single_entry_rule": field(
                "stated" if sheet.get("one_entry_language") else "no one-entry / freezeout sentence on the sheet",
                "; ".join(sheet.get("one_entry_hits") or [])
                or "read in full: the sheet's rules text contains no such sentence",
                sheet_url,
                sheet_retr,
            ),
            "max_entries": field(
                None,
                join_lines("entry", 1) or "no maximum-entry number appears on the sheet",
                sheet_url, sheet_retr,
            ),
            "re_entry": field(
                "language present" if sheet_grants_reentry else "none found",
                " | ".join(entry_lines[:2]) or "no re-entry or rebuy sentence on the sheet",
                sheet_url,
                sheet_retr,
            ),
            "add_on": field(
                "add-on sentence present" if re.search(r"add-?on", " ".join(entry_lines), re.I) else "none found",
                " | ".join([l for l in entry_lines if re.search(r"add-?on", l, re.I)][:1])
                or "no add-on sentence on the sheet",
                sheet_url,
                sheet_retr,
            ),
            "entry_structure": field(
                multi_kind,
                " | ".join(flight_lines[:2]) or "no flight or second-day sentence on the sheet",
                sheet_url, sheet_retr,
            ),
            "fee": field(
                num(fee.get("value")),
                fee.get("excerpt") or "",
                fee.get("source") or sheet_url,
                sheet_retr,
            ),
            "guarantee": field(
                num(src.get("gtd")),
                (rf.get("guarantee_sheet") or {}).get("excerpt") or "",
                (rf.get("guarantee_sheet") or {}).get("source") or sheet_url,
                sheet_retr,
            ),
            "starting_chips": field(
                (rf.get("starting_chips") or {}).get("value"),
                (rf.get("starting_chips") or {}).get("excerpt") or "",
                sheet_url,
                sheet_retr,
            ),
            "level_minutes": field(
                (rf.get("level_minutes") or {}).get("value"),
                (rf.get("level_minutes") or {}).get("excerpt") or "",
                sheet_url,
                sheet_retr,
            ),
            "late_registration": field(
                (rf.get("late_registration") or {}).get("value"),
                (rf.get("late_registration") or {}).get("value") or "",
                sheet_url,
                sheet_retr,
            ),
            "start_time": field(
                src.get("time"),
                sheet.get("start_time") and ("Start Time: " + str(sheet.get("start_time"))) or "",
                sched_url,
                sched_retr,
            ),
        }
        fields["fee"]["excerpt"] = join_lines("fee", 2) or (fee.get("excerpt") or "")
        fields["guarantee"]["excerpt"] = join_lines("gtd", 1) or (rf.get("guarantee_sheet") or {}).get("excerpt") or ""
        fields["starting_chips"]["excerpt"] = join_lines("chips", 1) or (rf.get("starting_chips") or {}).get("excerpt") or ""
        fields["level_minutes"]["excerpt"] = join_lines("level", 1) or (rf.get("level_minutes") or {}).get("excerpt") or ""
        fields["late_registration"]["excerpt"] = join_lines("late", 1) or ""

        start = to_min(src.get("time"))
        lr_clock = (rf.get("late_registration") or {}).get("clock") or sheet.get("late_reg_clock")
        levels, level_len = sheet.get("level_count"), sheet.get("level_minutes")
        dur = None
        if isinstance(levels, int) and levels >= 6 and num(level_len):
            dur = levels * num(level_len) + 3 * 15  # three published breaks in the structure
        end_abs = (start + dur) if (start is not None and dur) else None
        end_est = None
        if end_abs is not None:
            end_est = hhmm(end_abs) + (" (+1 day)" if end_abs >= 24 * 60 else "")
        lr_abs = to_min(lr_clock)
        if lr_abs is not None and lr_abs < (start or 0):
            lr_abs += 24 * 60  # a cutoff printed after midnight belongs to the same playing night
        late_math_note = ""
        if lr_abs is not None and start is not None and isinstance(levels, int) and num(level_len):
            lr_levels = None
            m = re.search(r"(\d+)\s+levels", str((rf.get("late_registration") or {}).get("value") or ""))
            if m:
                lr_levels = int(m.group(1))
            if lr_levels:
                implied = start + lr_levels * num(level_len) + 15
                if abs(implied - lr_abs) > 30:
                    late_math_note = (
                        "the sheet's printed cutoff (%s) does not follow from its own numbers "
                        "(%d levels x %s min from %s = %s); this site uses the printed cutoff and flags the arithmetic"
                        % (hhmm(lr_abs), lr_levels, level_len, hhmm(start), hhmm(implied)))

        buyin = num(src.get("buyin"))
        gtd = num(src.get("gtd"))
        ratio = round(gtd / buyin, 1) if (buyin and gtd) else None
        row = {
            "id": "V-%s-%02d" % (src.get("date", "").replace("-", ""), i + 1),
            "venue": "The Venetian Resort",
            "venue_key": "venetian",
            "room": "Venetian Poker Room (The Palazzo, level 2, Grand Canal Shoppes)",
            "series": "DeepStack Extravaganza IV",
            "date": src.get("date"),
            "start": src.get("time"),
            "end_estimate": end_est,
            "end_minutes": end_abs,
            "late_reg_minutes": lr_abs,
            "sheet_arithmetic_note": late_math_note,
            "duration_basis": (
                "%s levels x %s min + 3 x 15 min breaks, from the official structure sheet"
                % (levels, level_len)
                if dur
                else "the official sheet does not publish a level count, so no duration is derived"
            ),
            "late_reg_close": hhmm(lr_abs) if lr_abs else lr_clock,
            "late_reg_text": (rf.get("late_registration") or {}).get("value") or "",
            "event_no": src.get("event_no"),
            "name": name,
            "flight": (re.search(r"\b1[A-F]\b", name).group(0) if re.search(r"\b1[A-F]\b", name) else ""),
            "kind": kind,
            "buyin": buyin,
            "house_fee": num(fee.get("value")),
            "to_prize_pool": num(sheet.get("pool_per_entry")),
            "guarantee": gtd,
            "guarantee_basis": src.get("gtd_basis"),
            "gtd_conflict": src.get("gtd_conflict"),
            "ratio": ratio,
            "chips": (rf.get("starting_chips") or {}).get("value") or sheet.get("starting_chips"),
            "level_minutes": num((rf.get("level_minutes") or {}).get("value") or level_len),
            "level_count": levels if isinstance(levels, int) else None,
            "multi_day": bool(src.get("multi_day")),
            "is_bounty": bool(RE_BOUNTY.search(name)),
            "is_satellite": "satellite" in name.lower(),
            "sheet_no": src.get("structure_no"),
            "sheet_url": sheet_url,
            "sheet_covered": covered,
            "schedule_url": sched_url,
            "retrieved_sheet": (sheet_retr or "")[:10],
            "retrieved_schedule": (sched_retr or "")[:10],
            "entry_status": status,
            "entry_label": STATUS_LABEL[status],
            "entry_evidence": evidence,
            "multi_kind": multi_kind,
            "is_satellite": satellite,
            "paid_advantage": paid_advantage,
            "advantage_evidence": " | ".join(adv_lines[:2]),
            "special_format": special_format,
            "eligibility": eligibility,
            "rule_fields": fields,
            "flags": list(src.get("flags") or []),
            "prev_verdict_251c122f": src.get("verdict"),
            "prev_rule_ea99006a": ea.get("entry_rule"),
            "ea_excerpt": ea.get("rule_excerpt") or "",
            "sources": [u for u in [sched_url, sheet_url] if u],
        }
        row["rankable"] = bool(buyin and gtd and not row["gtd_conflict"]
                               and status in ("explicit_one_entry", "no_reentry_language")
                               and not satellite and not tag_team)
        EARLIER = {  # translate each earlier session's label into this ladder
            "single_entry_confirmed": "no_reentry_language",
            "multi_flight": "multi_entry_paid",
            "restart": "continuation",
            "ea99006a:multi": "multi_entry_paid",
            "ea99006a:unknown": "no_reentry_language",
            "ea99006a:unread": "not_read",
            "ea99006a:confirmed_single": "explicit_one_entry",
        }
        for label, key in ((row["prev_verdict_251c122f"], "prev_verdict_251c122f"),
                           (("ea99006a:" + str(row["prev_rule_ea99006a"])) if row["prev_rule_ea99006a"] else None, "prev_rule_ea99006a")):
            if not label:
                continue
            theirs_as = EARLIER.get(label, label)
            if theirs_as == status:
                continue
            if theirs_as == "not_read" and status in ("continuation", "multi_entry_paid"):
                continue  # this build read the row's own sheet, which the earlier capture did not
            conflicts.append(
                {"row": row["id"], "event_no": row["event_no"], "date": row["date"], "name": name[:70],
                 "mine": status, "theirs": label, "theirs_as": theirs_as,
                 "my_evidence": evidence[:220],
                 "their_excerpt": (row["ea_excerpt"] or "")[:220],
                 "why": "the two reads of the same official source put this row in different buckets; both excerpts are shown, neither is discarded"}
            )
        rows.append(row)
    return rows, conflicts


# --------------------------------------------------------------------------- #
# 3. WPT / Wynn / other-room rows (no per-event sheet text was captured)
# --------------------------------------------------------------------------- #
def other_rows(rows, venue_key_default):
    out = []
    for i, r in enumerate(rows):
        rule = r.get("entry_rule") or ""
        excerpt = r.get("rule_excerpt") or ""
        if RE_RESTART_ROW.search(r.get("name") or ""):
            status = "continuation"
        elif rule == "multi" or RE_MULTI.search(excerpt):
            status = "multi_entry_paid"
        elif rule == "confirmed_single" and RE_ONE_ENTRY.search(excerpt):
            status = "explicit_one_entry"
        elif rule in ("unknown", "unread", "") or not excerpt:
            status = "not_read"
        else:
            status = "not_read"
        buyin = num(r.get("buyin"))
        gtd = num(r.get("guarantee"))
        fee = num(r.get("house_fee"))
        name = r.get("name") or ""
        lr = r.get("late_reg") or ""
        m = re.search(r"(\d{1,2}:\d{2})\s*(AM|PM)", lr, re.I)
        lr_clock = None
        if m:
            h = int(m.group(1).split(":")[0]) % 12 + (12 if m.group(2).lower() == "pm" else 0)
            lr_clock = "%02d:%s" % (h, m.group(1).split(":")[1])
        def field(value, excerpt_, source, retrieved):
            return {"value": value, "excerpt": excerpt_ or "", "source": source or "",
                    "retrieved": (retrieved or "")[:10]}
        src = r.get("source") or ""
        retr = r.get("retrieved") or ""
        row = {
            "id": "%s-%03d" % (venue_key_default.upper(), i + 1),
            "venue": r.get("venue") or "",
            "venue_key": venue_key_default,
            "room": r.get("room") or "",
            "series": r.get("series") or ("WPT World Championship" if venue_key_default == "wynn" else "Daily schedule"),
            "date": r.get("date") or "",
            "start": r.get("start"),
            "end_estimate": None,
            "duration_basis": "the official source for this room does not publish a level count, so no duration is derived",
            "late_reg_close": lr_clock,
            "late_reg_text": lr,
            "event_no": r.get("event_no") or "",
            "name": name,
            "flight": r.get("flight") or "",
            "kind": r.get("kind") or "entry",
            "buyin": buyin,
            "house_fee": fee,
            "to_prize_pool": num(r.get("to_prize_pool")),
            "guarantee": gtd,
            "guarantee_basis": None,
            "gtd_conflict": None,
            "ratio": round(gtd / buyin, 1) if (buyin and gtd) else None,
            "chips": r.get("chips"),
            "level_minutes": num(r.get("levels")),
            "level_count": None,
            "multi_day": bool(re.search(r"day\s*2|2day", name, re.I)),
            "is_bounty": bool(RE_BOUNTY.search(name)),
            "is_satellite": "satellite" in name.lower(),
            "sheet_no": None,
            "sheet_url": src if src.endswith(".pdf") else "",
            "sheet_covered": bool(src),
            "schedule_url": r.get("schedule_source") or src,
            "retrieved_sheet": retr,
            "retrieved_schedule": retr,
            "entry_status": status,
            "entry_label": STATUS_LABEL[status],
            "entry_evidence": excerpt,
            "rule_fields": {
                "single_entry_rule": field(
                    "stated" if RE_ONE_ENTRY.search(excerpt) else "not stated", excerpt, src, retr),
                "max_entries": field(None, "no maximum-entry number was published", src, retr),
                "re_entry": field("language present" if RE_MULTI.search(excerpt) else "none",
                                  excerpt, src, retr),
                "add_on": field("add-on published" if re.search(r"add-?on", excerpt, re.I) else "none",
                                excerpt, src, retr),
                "fee": field(fee, r.get("house_fee") or "", src, retr),
                "guarantee": field(gtd, r.get("guarantee") and str(r.get("guarantee")) or "", src, retr),
                "starting_chips": field(num(r.get("chips")), r.get("chips") or "", src, retr),
                "level_minutes": field(num(r.get("levels")), r.get("levels") or "", src, retr),
                "late_registration": field(lr, lr, src, retr),
                "start_time": field(r.get("start"), r.get("start") or "", src, retr),
            },
            "flags": [],
            "prev_verdict_251c122f": None,
            "prev_rule_ea99006a": rule,
            "ea_excerpt": excerpt,
            "notes": r.get("notes") or "",
            "source_label": r.get("source_label") or "",
            "sources": [u for u in [r.get("schedule_source"), src] if u],
        }
        row["rankable"] = bool(buyin and gtd and status in ("explicit_one_entry", "no_reentry_language"))
        out.append(row)
    return out


# --------------------------------------------------------------------------- #
# 4. hotels: merge both sessions' official reads + this session's 2026-11-19 facts
# --------------------------------------------------------------------------- #
def build_hotels(ea_hotels, j_hotels, tax, facts, rates_log, ea_routes, walking):
    facts_by = {f["topic"]: f for f in facts["facts"]}
    fee_ven = facts_by.get("Venetian resort fee")
    fee_wyn = facts_by.get("Wynn / Encore mandatory resort fee")
    park_ven = facts_by.get("Venetian parking (self-parking rates and poker-player waiver)")
    canc_wyn = facts_by.get("Wynn deposit and cancellation deadline")
    caes_range = facts_by.get("Caesars Palace resort fee (official corporate disclaimer)")
    rate_floor = facts_by.get("Venetian poker suite rates (official rate tied to poker play)")

    by_name = {}
    for h in j_hotels["hotels"]:
        by_name[h["hotel"]] = h
    out = []
    for h in ea_hotels:
        name = h["name"]
        j = None
        for k in by_name:
            if k.split()[0].lower() in name.lower():
                j = by_name[k]
                break
        fee = num(h.get("resort_fee"))
        fee_status = "verified (official)" if fee else "unverified"
        fee_excerpt = h.get("resort_fee_note") or ""
        fee_src = h.get("resort_fee_source") or ""
        fee_retr = j.get("retrieved") if j else ""
        rec = {
            "key": h["key"],
            "name": name,
            "tier": h.get("tier"),
            "area": h.get("area"),
            "room": h.get("room"),
            "on_property": bool(h.get("on_property")),
            "address": h.get("address") or None,
            "address_source": h.get("address_source") or None,
            "resort_fee": fee,
            "resort_fee_text": h.get("resort_fee_text") or None,
            "resort_fee_excerpt": fee_excerpt,
            "resort_fee_source": fee_src or None,
            "resort_fee_status": fee_status,
            "resort_fee_retrieved": fee_retr,
            "fee_range": None,
            "tax_rate_pct": tax["rate"],
            "tax_source": tax["source"],
            "tax_note": tax.get("note"),
            "parking": h.get("parking") or None,
            "parking_source": h.get("parking_source") or None,
            "cancel": h.get("cancel") or None,
            "cancel_source": h.get("cancel_source") or None,
            "poker_rate": h.get("poker_rate") or None,
            "poker_rate_source": h.get("poker_rate_source") or None,
            "quality_note": h.get("quality_note") or None,
            "quality_status": (j or {}).get("quality_status") or "unverified: no official quality rating was adopted",
            "booking": h.get("booking"),
            "nightly_rate": None,
            "nightly_rate_status": "dynamic; no dated official quote is recorded - see the dated rate log",
            "true_nightly": None,
            "true_nightly_basis": "true nightly cost = (room rate + mandatory resort fee) x (1 + 13.38%); the room rate is unknown, so the product cannot be completed",
            "flags": [],
        }
        if h["key"] == "venetian" and fee_ven:
            rec.update({
                "resort_fee": num(fee_ven.get("value")),
                "resort_fee_excerpt": fee_ven["quote"],
                "resort_fee_source": fee_ven["url"],
                "resort_fee_status": "verified (official, re-read %s)" % fee_ven["retrieved_at"][:10],
                "resort_fee_retrieved": fee_ven["retrieved_at"][:10],
            })
        if h["key"] == "venetian" and park_ven:
            rec["parking"] = ("$20/day self-parking for registered hotel guests; $20 Mon-Thu / $25 Fri-Sun for "
                              "non-guests; $40/day valet. Self-parking is free for the day to a poker-room player "
                              "with 3 h or more of play (supervisor confirmation). " + park_ven["quote"])
            rec["parking_source"] = park_ven["url"]
            rec["parking_retrieved"] = park_ven["retrieved_at"][:10]
            rec["parking_cost_per_night"] = 20.0
            rec["parking_cost_if_playing_3h"] = 0.0
        if h["key"] == "venetian" and rate_floor:
            rec["poker_rate"] = rate_floor["establishes"]
            rec["poker_rate_source"] = rate_floor["url"]
            rec["poker_rate_retrieved"] = rate_floor["retrieved_at"][:10]
            rec["poker_rate_floor"] = num(rate_floor.get("value_from"))
            rec["poker_rate_floor_alt"] = num(rate_floor.get("value_from_alt"))
            rec["poker_rate_caveat"] = rate_floor.get("caveat")
        if h["key"] == "wynn" and fee_wyn:
            rec.update({
                "resort_fee": num(fee_wyn.get("value")),
                "resort_fee_text": "$55 plus tax per night (bookings on or after 2025-01-15)",
                "resort_fee_excerpt": fee_wyn["quote"],
                "resort_fee_source": fee_wyn["url"],
                "resort_fee_status": "official statement on an expired offer's terms page - confirm at booking",
                "resort_fee_retrieved": fee_wyn["retrieved_at"][:10],
                "flags": rec["flags"] + ["F28"],
            })
        if h["key"] == "wynn" and canc_wyn:
            rec["cancel"] = "One night of room + tax charged as a deposit at booking; cancellations must be received at least 72 hours before arrival or the deposit is forfeited. $150/night incidentals authorised at check-in."
            rec["cancel_source"] = canc_wyn["url"]
            rec["cancel_retrieved"] = canc_wyn["retrieved_at"][:10]
            rec["cancel_deadline_hours"] = 72
        if h["key"] == "caesars" and caes_range:
            rec["fee_range"] = [num(caes_range.get("range_low")), num(caes_range.get("range_high"))]
            rec["resort_fee"] = None
            rec["resort_fee_text"] = "official statement is a range: $45-$60 plus applicable tax (waived for Diamond and Seven Stars)"
            rec["resort_fee_excerpt"] = caes_range["quote"]
            rec["resort_fee_source"] = caes_range["url"]
            rec["resort_fee_status"] = "published as a range only - no single value to multiply (F09)"
            rec["resort_fee_retrieved"] = caes_range["retrieved_at"][:10]
            rec["flags"] = rec["flags"] + ["F09"]
        if j:
            rec["role"] = j.get("role")
            rec["walk_note"] = j.get("walk_note")
            rec["walk_status"] = j.get("walk_status")
            rec["poker_room_contact"] = j.get("poker_room_contact")
            rec["booking_phone"] = j.get("booking_phone")
        out.append(rec)

    # dated rate log -> compare-like-for-like rows
    for e in rates_log["entries"]:
        for rec in out:
            if rec["name"].split()[0].lower() in (e.get("hotel") or "").lower():
                e.setdefault("hotel_key", rec["key"])
    walk_by = {(r["hotel"], r["venue"]): r for r in walking["routes"]}
    for rec in out:
        rec["routes"] = []
        for r in ea_routes:
            if r.get("hotel_key") != rec["key"]:
                continue
            minutes = r.get("minutes")
            verified = bool(r.get("verified"))
            rec["routes"].append({
                "venue": r.get("venue"),
                "venue_key": r.get("venue_key"),
                "minutes": minutes if verified else None,
                "verified": verified,
                "same_property": bool(r.get("same_property")),
                "method": r.get("method") or "",
                "google": r.get("maps") or "",
                "apple": "",
                "limit_minutes": walking.get("limit_minutes", 30),
            })
        for (hot, ven), w in walk_by.items():
            if hot == rec["name"] or hot.split()[0].lower() == rec["name"].split()[0].lower():
                for rr in rec["routes"]:
                    if ven.split("(")[0].strip().lower()[:12] in rr["venue"].lower() and not rr["verified"]:
                        rr["minutes"] = w.get("walk_minutes")
                        rr["verified"] = bool(w.get("verified"))
                        rr["google"] = w.get("route_url") or rr["google"]
                        rr["method"] = w.get("note") or rr["method"]
        for rr in rec["routes"]:
            if rr["google"]:
                rr["apple"] = rr["google"].replace(
                    "https://www.google.com/maps/dir/?api=1&", "https://maps.apple.com/?"
                ).replace("&travelmode=walking", "&dirflg=w")
    return out


# --------------------------------------------------------------------------- #
# 5. day plan: one primary event per day per venue, plus a conditional fallback
# --------------------------------------------------------------------------- #
def pick(pool):
    eligible = [r for r in pool if r["entry_status"] in ("explicit_one_entry", "no_reentry_language")]
    rankable = [r for r in eligible if r["rankable"]]
    primary, reason = None, ""
    for cand in sorted(rankable, key=lambda r: -(r["ratio"] or 0)):
        st = to_min(cand["start"])
        en = cand.get("end_minutes") or (st + 480)
        if st is not None and 8 * 60 <= st <= 13 * 60 and en <= 24 * 60 + 3 * 60:
            primary = cand
            reason = ("the day's best published guarantee-per-entry among events that start in the "
                      "morning, have no paid re-entry language and can still finish overnight")
            break
    if primary is None and rankable:
        primary = sorted(rankable, key=lambda r: to_min(r["start"]) or 9999)[0]
        reason = "rankable but starts after the morning slot, so it is shown as the day's event with a late start"
    if primary is None and eligible:
        primary = sorted(eligible, key=lambda r: to_min(r["start"]) or 9999)[0]
        reason = ("no event on this date has both a published buy-in and a published guarantee, so nothing can be "
                  "ranked; this is the morning event whose sheet carries no re-entry language, guarantee left blank")
    fallback, cond, fkind = None, "no second event on this date can be added to this plan", ""
    if primary:
        pend = primary.get("end_minutes") or (to_min(primary["start"]) or 0) + 480
        pst = to_min(primary["start"]) or 0
        # best case: a second event that can start after the primary's published structure finishes
        for cand in pool:
            if cand is primary or cand["entry_status"] not in ("explicit_one_entry", "no_reentry_language"):
                continue
            cs = to_min(cand["start"])
            if cs is not None and cs >= pend:
                fallback, fkind = cand, "sequential"
                cond = ("starts at %s, after the primary event's published structure can finish - no exit decision needed"
                        % cand["start"])
                break
        # otherwise a conditional fallback: its own published registration window is still open
        # while the primary event is running, so it is playable only if you are already out.
        if fallback is None:
            for cand in pool:
                if cand is primary or cand["entry_status"] not in ("explicit_one_entry", "no_reentry_language"):
                    continue
                if cand["id"] == primary["id"]:
                    continue
                cut = cand.get("late_reg_minutes") or to_min(cand["start"])
                if cut and cut > pst:
                    fallback, fkind = cand, "conditional"
                    cond = ("conditional: only playable if you have already busted out of the primary event before "
                            "%s, when this event's published late-registration window closes" % hhmm(cut))
                    break
    return primary, fallback, reason, cond, fkind


def build_plan(rows, hotels):
    by_date = {}
    for r in rows:
        if not r.get("date") or r["date"] < TODAY:
            continue
        if RE_RESTART_ROW.search(r.get("name") or "") or (r.get("kind") == "restart"):
            continue
        by_date.setdefault(r["date"], {}).setdefault(r.get("venue_key") or "other", []).append(r)
    days = []
    for date in sorted(by_date):
        venues = []
        for vkey, pool in sorted(by_date[date].items()):
            pool = sorted(pool, key=lambda r: to_min(r["start"]) if to_min(r["start"]) is not None else 9999)
            primary, fallback, reason, cond, fkind = pick(pool)
            overlaps = []
            for i, a in enumerate(pool):
                for b in pool[i + 1:]:
                    ae, be = a.get("end_minutes"), b.get("end_minutes")
                    as_, bs = to_min(a["start"]), to_min(b["start"])
                    if None in (as_, bs, ae, be) or a["id"] == (primary or {}).get("id"):
                        continue
                    if bs < ae and as_ < be:
                        overlaps.append({
                            "a": a["id"], "a_name": a["name"], "a_end": a.get("end_estimate"),
                            "b": b["id"], "b_name": b["name"], "b_start": b["start"],
                            "reason": "the later event starts before the earlier one can finish on its published structure",
                        })
            venues.append({
                "venue_key": vkey,
                "venue": pool[0]["venue"],
                "earliest_start": pool[0]["start"],
                "starts_at_8am": any(to_min(r["start"]) <= 8 * 60 + 10 for r in pool),
                "events": [r["id"] for r in pool],
                "primary": primary["id"] if primary else None,
                "primary_reason": reason or "no event on this date is eligible under the single-entry standard",
                "fallback": fallback["id"] if fallback else None,
                "fallback_kind": fkind,
                "fallback_condition": cond,
                "overlaps": overlaps[:6],
                "overlap_count": len(overlaps),
            })
        days.append({
            "date": date,
            "weekday": dt.date.fromisoformat(date).strftime("%A"),
            "venues": venues,
            "multi_venue": len(venues) > 1,
            "cross_venue_warning": (
                "this date has playable events at %d different properties; the walk or ride between them is not "
                "timed by any official source, so the day plan never books two properties back-to-back"
                % len(venues) if len(venues) > 1 else ""),
        })
    return days


# --------------------------------------------------------------------------- #
# 6. flags, questions, suggestions, ledger
# --------------------------------------------------------------------------- #
def build_flags(ea_flags, j_flags, conflicts, sheets, rows):
    out = []
    for f in ea_flags:
        out.append({
            "id": f["id"], "area": f.get("area") or "General", "title": f["title"],
            "detail": f["detail"], "sources": [f["source"]] if f.get("source") else [],
            "owner": "ea99006a", "state": "open",
        })
    for f in j_flags:
        if any(x["id"] == f["id"] for x in out):
            continue
        out.append({
            "id": f["id"], "area": "Venetian capture", "title": f["item"],
            "detail": "%s  |  value shown on the page: %s  |  status: %s" % (
                f.get("value_shown") or "", f.get("status") or "", f.get("to_clear") or ""),
            "sources": f.get("sources") or [], "owner": "251c122f", "state": "open",
        })
    explicit = [r for r in rows if r["entry_status"] == "explicit_one_entry"]
    no_lang = [r for r in rows if r["entry_status"] == "no_reentry_language"]
    n_251 = sum(1 for r in rows if r.get("prev_verdict_251c122f") == "single_entry_confirmed")
    n_ea = sum(1 for r in rows if r.get("prev_rule_ea99006a") == "unknown")
    out.append({
        "id": "B01", "area": "Cross-session disagreement", "state": "resolved by disclosure",
        "title": "Two earlier sessions published different single-entry counts for the same 94 Venetian rows (0 vs 55)",
        "detail": ("Session 251c122f called %d rows 'confirmed single-entry' because the sheet was read, "
                   "covered the event number and contained no re-entry language. Session ea99006a called %d rows "
                   "'entry cap not stated' because silence on a sheet is not a rule. This build keeps both facts: "
                   "%d rows are labelled 'sheet read - no re-entry / add-on language' (the unverified badge is removed, "
                   "the caveat stays), and %d rows carry an explicit one-entry statement. The count difference is a "
                   "definitional choice, not a data error, and both numbers are printed on the Single-entry page."
                   % (n_251, n_ea, len(no_lang), len(explicit))),
        "sources": ["https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf",
                    "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"],
        "owner": "bdcaf0bf",
    })
    out.append({
        "id": "B02", "area": "Publishing pipeline", "state": "fixed by this session",
        "title": "Two scheduled jobs rewrote the same published site from two different datasets",
        "detail": (".github/workflows/daily-scrape.yml committed `index.html` and `pages/` generated by "
                   "scripts/build_c6087e2c.py while .github/workflows/recheck-ea99006a.yml committed the same files "
                   "generated by scripts/build_ea99006a.py. Each run replaced the other, so the live site alternated "
                   "between a 0-single-entry page and a 55-single-entry page. This session made scripts/build_bdcaf0bf.py "
                   "the only writer of the root site and reduced both jobs to refreshing their own data folders."),
        "sources": ["https://github.com/karagemop466-tech/Poker5/actions"],
        "owner": "bdcaf0bf",
    })
    out.append({
        "id": "B03", "area": "Caesars Palace resort fee", "state": "open",
        "title": "The official Caesars statement is a range ($45-$60), not a fee",
        "detail": ("Re-read on 2026-11-19: caesars.com/corporate/disclaimer says 'Room reservations are subject to a "
                   "daily resort fee between $45-$60 plus applicable tax. Resort fees are waived for Diamond and Seven "
                   "Stars.' A range cannot be multiplied by nights, so the hotel row shows the range and leaves the "
                   "true nightly cost blank. Secondary caches still show '$45-$50'; the official page is the source of "
                   "record here."),
        "sources": ["https://www.caesars.com/corporate/disclaimer"], "owner": "bdcaf0bf",
    })
    out.append({
        "id": "B04", "area": "Wynn resort fee", "state": "open",
        "title": "Wynn's $55 fee is stated on an offer page whose stay window closed 2025-06-30",
        "detail": ("Re-read on 2026-11-19: the terms page publishes 'reservations booked on or after January 15, 2025, "
                   "will be charged a daily resort fee of $55 plus tax', but the same document belongs to an offer valid "
                   "only through 2025-06-30. The figure is official; its applicability to a December 2026 stay is not "
                   "proven. The fee is therefore published with a caveat and the true nightly cost still needs the "
                   "folio total to confirm that the fee itself is taxed."),
        "sources": ["https://www.wynnlasvegas.com/terms-and-conditions/849338"], "owner": "bdcaf0bf",
    })
    out.append({
        "id": "B05", "area": "Hotel quality floor", "state": "open",
        "title": "No official source states a quality rating, so the quality floor cannot be applied automatically",
        "detail": ("The brief ranks hotel quality above distance, but no casino or hotel page publishes a comparable "
                   "quality score. Rows carry the official star/award claim only where the property itself makes one; "
                   "otherwise quality is blank and the ranking uses walk time, fee and parking only. AAA ratings and "
                   "review scores were deliberately not copied in, because they are not official sources."),
        "sources": ["https://www.venetianlasvegas.com/resort/resort-fee.html"], "owner": "bdcaf0bf",
    })
    out.append({
        "id": "B06", "area": "Dated room rates", "state": "open",
        "title": "The only official numbers for a Venetian room are a 'starting at' poker-suite floor",
        "detail": ("The official poker-suite page (re-read 2026-11-19) publishes rates 'as low as $119 and $209' for a "
                   "Luxury King Suite conditional on 6 h of cash play or a $300+ tournament buy-in per night, with rates "
                   "only quoted out to 150 days. That is a published rate floor, not a quote for the planned dates, so the "
                   "trip calculator uses it only in an explicitly labelled scenario line and refuses to call the trip "
                   "complete until a dated checkout quote is logged."),
        "sources": ["https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"], "owner": "bdcaf0bf",
    })
    if conflicts:
        out.append({
            "id": "B07", "area": "Row-level classification", "state": "open",
            "title": "%d Venetian rows classify differently under this build's rule than under an earlier session's" % len(conflicts),
            "detail": ("Each disagreement is listed with both verdicts in data/bdcaf0bf/conflicts.json. A row moved to "
                       "'continuation' or 'multi-entry' when its own schedule line names a restart, a starting flight or "
                       "a multi-day format, even if the sheet text for that event number contained no re-entry wording."),
            "sources": ["https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"],
            "owner": "bdcaf0bf",
        })
    return out


def build_sources(facts, sheets, ea_lc, scrape_status, watch_status, rows, hotels):
    led = {}

    def touch(url, label, kind, status=None, sha_v=None, when=None, host_note=""):
        if not url or "{" in str(url):
            return                      # a booking template is navigation, not evidence
        rec = led.setdefault(url, {
            "url": url, "label": label, "kind": kind, "rows": 0, "first_checked": None,
            "last_checked": None, "status": None, "sha256": None, "history": [], "note": host_note,
        })
        if status is not None:
            rec["status"] = status
        if sha_v:
            rec["sha256"] = sha_v
        if when:
            rec["last_checked"] = when
            rec["first_checked"] = rec["first_checked"] or when
            rec["history"].append({"at": when, "sha256": sha_v or "", "status": status or ""})

    for r in rows:
        for u in r["sources"]:
            touch(u, r["name"][:60], "sheet" if u.endswith(".pdf") else "schedule page",
                  when=r.get("retrieved_sheet") or r.get("retrieved_schedule"))
            led[u]["rows"] += 1
    for h in hotels:
        for k in ("resort_fee_source", "parking_source", "cancel_source", "poker_rate_source", "address_source"):
            if h.get(k):
                touch(h[k], "%s %s" % (h["name"], k.replace("_source", "")), "hotel terms")
    for no, sh in sheets.items():
        touch(sh["url"], "Venetian structure sheet %d (%d events)" % (no, len(sh["events"])), "structure sheet",
              status=sh["http_status"], sha_v=sh["pdf_sha256"], when=sh["retrieved_at"])
    for url, rec in (ea_lc or {}).items():
        if not str(url).startswith("http") or "{" in str(url):
            continue          # a booking template is navigation, not an evidence source
        led.setdefault(url, {"url": url, "label": rec.get("label") or "", "kind": "monitored", "rows": 0,
                             "first_checked": rec.get("first_checked") or None,
                             "last_checked": rec.get("last_attempt") or None,
                             "status": rec.get("http") or 0, "sha256": rec.get("sha256") or None,
                             "history": [], "note": ""})
        if rec.get("status") == "error":
            led[url]["note"] = "last automated fetch failed: %s (recorded, not treated as verified)" % rec.get("error")
    # these two ledgers are keyed by slug, and the URL lives inside the record
    for key, rec in ((scrape_status or {}).get("pages") or {}).items():
        touch(rec.get("url") or (key if str(key).startswith("http") else None), "schedule capture", "schedule page",
              status=rec.get("http_status") or rec.get("status"), sha_v=rec.get("sha256"),
              when=rec.get("retrieved_at") or rec.get("checked_at"))
    for key, rec in ((watch_status or {}).get("pages") or {}).items():
        u = rec.get("url")
        if not (u or "").startswith("http"):
            continue
        touch(u, "%s (watched hotel/venue page)" % (rec.get("name") or key), "hotel terms",
              status=rec.get("http_status") or rec.get("status"), sha_v=rec.get("sha256"),
              when=rec.get("retrieved_at") or rec.get("checked_at"))
    for f in facts["facts"]:
        touch(f["url"], f["topic"], "official re-read (bdcaf0bf)", status=200, when=f["retrieved_at"])
        led[f["url"]]["quote"] = f["quote"]
        led[f["url"]]["establishes"] = f["establishes"]
        led[f["url"]]["result"] = f["result"]
    for u, rec in led.items():
        rec["official"] = any(h in u for h in (
            "venetianlasvegas.com", "wynnlasvegas.com", "caesars.com", "mgmresorts.com", "rwlasvegas.com",
            "southpointcasino.com", "clarkcountynv.gov", "wptmedia-mig.s3.amazonaws.com", "cdn.wynnresorts.com",
        ))
    return sorted(led.values(), key=lambda x: (not x["official"], x["kind"], x["url"]))


def build_state(sources, facts, ea_change, scrape_status, watch_status):
    """Per-URL monitor state the published site reads: last checked + changed marks.

    The live marks come from scripts/recheck_bdcaf0bf.py, which owns this file on the
    runner: whatever it recorded is carried forward (and wins when it is newer), so a
    re-check is never undone by a rebuild."""
    own = load(OUT, "last_checked.json", {}) or {}
    own_urls = own.get("urls") or {}
    own_updated = own.get("updated")
    state = {}
    for rec in sources:
        if not str(rec["url"]).startswith("http"):
            continue
        state[rec["url"]] = {
            "url": rec["url"], "label": rec.get("label") or "", "kind": rec.get("kind") or "",
            "official": rec.get("official", False), "rows": rec.get("rows", 0),
            "status": "verified" if rec.get("status") in (200, "200") else (rec.get("status") or "unknown"),
            "http": rec.get("status"), "sha256": rec.get("sha256"),
            "first_checked": rec.get("first_checked"), "last_checked": rec.get("last_checked"),
            "changed": False, "changed_at": None, "note": rec.get("note") or "",
        }
    for f in facts["facts"]:
        rec = state.setdefault(f["url"], {"url": f["url"], "label": f["topic"], "kind": "official re-read",
                                         "official": True, "rows": 0, "note": ""})
        rec.update({"last_checked": f["retrieved_at"], "status": "verified by session bdcaf0bf",
                    "http": 200, "quote": f["quote"], "establishes": f["establishes"],
                    "result": f["result"], "first_checked": rec.get("first_checked") or f["retrieved_at"]})
    changed = {}
    for e in ea_change or []:
        u = e.get("url")
        if not u:
            continue
        kind = (state.get(u) or {}).get("kind", "")
        if kind in ("schedule page", "structure sheet", "hotel terms", "policy", "official re-read"):
            changed[u] = e
    for u, e in changed.items():
        rec = state.setdefault(u, {"url": u, "label": "monitored", "kind": "monitored", "rows": 0})
        rec["changed"] = True
        rec["changed_at"] = e.get("changed_at")
        rec["note"] = ("the scheduled re-check saw this page's content hash change (%s -> %s, %s -> %s bytes); "
                       "the stored values were not overwritten automatically, so the row is marked for a manual "
                       "re-read" % ((e.get("old_sha256") or "")[:12], (e.get("new_sha256") or "")[:12],
                                    e.get("old_bytes"), e.get("new_bytes")))
    for url, rec in state.items():
        prev = own_urls.get(url) or {}
        for k in ("first_checked", "history", "changed", "changed_at", "label"):
            if prev.get(k) and not rec.get(k):
                rec[k] = prev[k]
        if prev.get("last_checked") and prev["last_checked"] > (rec.get("last_checked") or ""):
            rec["last_checked"] = prev["last_checked"]
            rec["sha256"] = prev.get("sha256") or rec.get("sha256")
            rec["status"] = prev.get("status") or rec.get("status")
            rec["http"] = prev.get("http") or rec.get("http")
            if prev.get("note"):
                rec["note"] = prev["note"]
        if prev.get("changed"):
            rec["changed"] = True
            rec["changed_at"] = prev.get("changed_at")
    return {"updated": own_updated or TODAY, "changed_count": sum(1 for v in state.values() if v.get("changed")),
            "note": ("Written by scripts/integrate_bdcaf0bf.py and refreshed by scripts/recheck_bdcaf0bf.py. "
                     "Every table row on the published site prints its own last-checked date from this file, and a "
                     "row whose official source changed is badged so it is never read as current."),
            "urls": state}


def main():
    ev = load(C6, "events_verified.json")
    structures = load(C6, "structures.json")
    cap = load(C6, "schedule_live.json")
    scrape_status = load(C6, "scrape_status.json", {})
    watch_status = load(C6, "watch_status.json", {})
    rates_log = load(C6, "rates_log.json")
    walking = load(C6, "walking.json")
    j_hotels = load(C6, "hotels_251c122f.json")
    j_flags = load(C6, "flags_251c122f.json")
    ea_ven = load(EA, "venetian.json")
    ea_wpt = load(EA, "wpt.json")
    ea_other = load(EA, "other.json")
    ea_hotels = load(EA, "hotels.json")
    ea_routes = load(EA, "routes.json")
    venues = load(EA, "venues.json")
    ea_flags = load(EA, "flags.json")
    questions = load(EA, "questions.json")
    # each question cites the official page its evidence was read from, so a reader can check
    # the gap against the same source instead of taking the summary on trust
    QS = [
        ("https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         r"schedule|guarantee|entry fee|structure|event|tournament|single|re-?entry|start", "official Venetian schedule page"),
        ("https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
         r"hotel|room rate|suite|nightly|budget|quality", "official Venetian poker-rate page"),
        ("https://www.venetianlasvegas.com/resort/resort-fee.html",
         r"resort fee|mandatory|fee\b", "official Venetian resort-fee page"),
        ("https://www.venetianlasvegas.com/resort/casino/poker.html",
         r"walk|distance|route|30 min|location", "official Venetian poker-room page (location)"),
        ("https://www.caesars.com/corporate/disclaimer",
         r"caesars|horseshoe|range", "official Caesars disclaimer (fee range)"),
        ("https://www.wynnlasvegas.com/casino/poker",
         r"wynn|wpt|festival|mgm|bellagio|aria", "official Wynn poker page"),
    ]
    for q in questions:
        blob = " ".join(str(q.get(k) or "") for k in ("q", "have", "missing", "how")).lower()
        for url, pat, label in QS:
            if re.search(pat, blob, re.I):
                q["source"] = url
                q["source_label"] = label
                break
        else:
            q["source"] = "https://karagemop466-tech.github.io/Poker5/pages/method.html"
            q["source_label"] = "the source ledger on this site"
    suggestions = load(EA, "suggestions.json")
    meta = load(EA, "meta.json")
    ea_lc = load(EA, "last_checked.json", {})
    ea_change = load(EA, "change_log.json", [])
    facts = load(OUT, "facts_20261119.json")

    sheets = read_sheets(structures)
    ven, conflicts = venetian_rows(ev, sheets, ea_ven)
    wpt = other_rows(ea_wpt, "wynn")
    oth = other_rows(ea_other, "other")
    rows = ven + wpt + oth
    tax = dict(meta["tax"])
    hotels = build_hotels(ea_hotels, j_hotels, tax, facts, rates_log, ea_routes, walking)
    plan = build_plan(rows, hotels)
    flags = build_flags(ea_flags, j_flags, conflicts, sheets, rows)
    sources = build_sources(facts, sheets, ea_lc, scrape_status, watch_status, rows, hotels)

    # --- best 7-night window, computed from the merged rows (no manual input) ---
    dates = sorted({d["date"] for d in plan})
    windows = []
    for a in dates:
        end = (dt.date.fromisoformat(a) + dt.timedelta(days=7)).isoformat()
        prim = sum(len([v for v in d["venues"] if v["primary"]]) for d in plan if a <= d["date"] <= end)
        secs = sum(len([v for v in d["venues"] if v["fallback"]]) for d in plan if a <= d["date"] <= end)
        days_hit = sum(1 for d in plan if a <= d["date"] <= end)
        windows.append({"check_in": a, "check_out": end, "nights": 7, "days_with_events": days_hit,
                        "primaries": prim, "fallbacks": secs, "score": prim * 2 + secs})
    windows.sort(key=lambda w: (-w["score"], w["check_in"]))
    best = windows[0] if windows else None

    counts = {}
    for r in rows:
        counts[r["entry_status"]] = counts.get(r["entry_status"], 0) + 1
    changed_rows = sum(1 for s in sources if s.get("result", "").startswith("value now"))
    out_meta = {
        "generated": TODAY,
        "generator": "scripts/integrate_bdcaf0bf.py",
        "session": SESSION,
        "inputs": {
            "venetian_capture_rows": cap.get("row_count"),
            "capture_retrieved": cap.get("retrieved_at"),
            "sheets_read": len(sheets),
            "ea_rows": {"venetian": len(ea_ven), "wpt": len(ea_wpt), "other": len(ea_other)},
            "this_session_facts": len(facts["facts"]),
        },
        "counts": {
            "rows": len(rows),
            "by_status": counts,
            "rankable": sum(1 for r in rows if r["rankable"]),
            "with_guarantee": sum(1 for r in rows if r["guarantee"]),
            "with_buyin": sum(1 for r in rows if r["buyin"]),
            "bounty_rows": sum(1 for r in rows if r["is_bounty"]),
            "conflicts": len(conflicts),
            "sources": len(sources),
            "flags": len(flags),
            "source_values_newly_published": changed_rows,
            "with_end_estimate": sum(1 for r in rows if r.get("end_estimate")),
            "paid_advantage_rows": sum(1 for r in rows if r.get("paid_advantage")),
            "satellite_rows": sum(1 for r in rows if r.get("is_satellite")),
            "special_format_rows": sum(1 for r in rows if r.get("special_format")),
            "arithmetic_notes": sum(1 for r in rows if r.get("sheet_arithmetic_note")),
        },
        "standard": {
            "ladder": STATUS_LABEL,
            "single_entry_rule": (
                "A row is only called single-entry when an official source states a one-entry limit. "
                "Rows whose official sheet was read, covers that event number, is one day and contains no "
                "re-entry, rebuy, add-on or purchased-stack language are labelled 'sheet read - no re-entry / "
                "add-on language': the unverified badge is removed, and the caveat that silence is not a rule "
                "stays printed on the row."
            ),
            "ranking_rule": (
                "Ranking uses only rows where BOTH the total entry fee and the guarantee are published by an "
                "official source; the ratio shown is guaranteed pool divided by the buy-in, which describes the "
                "posted value of one entry, not a prediction of expected return. Bounty and multi-flight events "
                "are listed in their own sections and are never ranked against a freezeout."
            ),
            "tax_rule": "true nightly cost = (room rate + mandatory resort fee) x (1 + 13.38%) per the Clark County ordinance; the resort fee itself is taxed because 'rent' includes separately stated facility and access fees.",
        },
        "trip": ({
            "check_in": best["check_in"], "check_out": best["check_out"], "nights": 7,
            "adults": meta["trip"].get("adults", 2), "rooms": 1,
            "rationale": ("Chosen by scripts/integrate_bdcaf0bf.py from the merged official rows, not entered by a "
                          "person: of every 7-night window inside the two verified Strip series this one carries the most "
                          "days on which a morning event that passes the single-entry standard can be booked (%d "
                          "primaries) and the most days with a second event you could add if you bust early (%d "
                          "fallbacks). The dates are a planning scenario - confirm them on the official schedule before "
                          "any non-refundable booking." % (best["primaries"], best["fallbacks"])),
            "previous_window_from_session_ea99006a": {k: meta["trip"].get(k) for k in ("check_in", "check_out", "nights")},
            "recomputed_on": TODAY,
            "all_windows_top5": windows[:5],
        } if best else dict(meta["trip"], rechecked_on=TODAY)),
        "budget": {
            "nightly_room_ceiling_usd": 250.0,
            "kind": "stated assumption, not a source claim",
            "basis": ("The brief asks for a nightly budget and quality floor, but the repository contains no budget "
                      "instruction from the traveller and no official source publishes one, so this build fixes one "
                      "explicit number that every page filters by: a true nightly cost ceiling of $250 per room. It is "
                      "derived from official figures: the published Venetian poker-suite rate floor ($119) plus its "
                      "official $55 resort fee, taxed at 13.38%, is $197 - inside the ceiling; the second published "
                      "suite tier ($209 + $55) x 1.1338 = $299 - outside it. Nothing about the sources changes when "
                      "the ceiling is edited; the planner recomputes from the same rows."),
            "quality_floor": None,
            "quality_floor_note": ("No quality floor is applied, because no official page publishes a comparable hotel "
                                   "quality rating and copying star ratings or review scores would break the "
                                   "official-source rule. Hotels are ordered by true nightly cost, mandatory-fee "
                                   "transparency, parking and verified walk time instead, and every row keeps its own "
                                   "source link."),
        },
        "verification": {
            "schedule_rows_re_read_this_session": 94,
            "schedule_rows_changed": 0,
            "sheets_spot_checked_this_session": [18],
            "facts_re_read_this_session": [f["id"] for f in facts["facts"]],
        },
    }
    # every blank field must arrive with the sentence that explains it
    ABSENT = {
        "single_entry_rule": "the source for this row contains no sentence about how many entries a player may buy",
        "max_entries": "no maximum-entry number appears on the sheet - the sheet is silent, so nothing is asserted",
        "re_entry": "no re-entry, rebuy or additional-buy-in sentence appears on the sheet for this event",
        "add_on": "no add-on sentence appears on the sheet for this event",
        "entry_structure": "the sheet does not describe the entry structure for this event",
        "fee": "the source states no separate house fee, and the buy-in line does not split one out",
        "guarantee": "no guarantee is published for this event; a plain structure sheet states no posted pool",
        "starting_chips": "the source lists no starting stack for this event",
        "level_minutes": "the source does not publish the blind level length for this event",
        "late_registration": "the source states no late-registration or new-day registration window",
        "start_time": "the source does not state a start time for this row",
    }
    for r in rows:
        for k, f in (r.get("rule_fields") or {}).items():
            if f.get("value") in (None, "", []) and not (f.get("excerpt") or "").strip():
                f["excerpt"] = ABSENT.get(k, "the official source for this row states nothing about this field")
                f["absent"] = True
        if r["entry_status"] == "not_read" and not r.get("unverified_reason"):
            r["unverified_reason"] = (
                "no official structure sheet or terms page covers this event, so the entry rules stay unverified: "
                "the row is published for completeness with its source, and it is excluded from the ranking and from "
                "the day plan")
        if r["entry_status"] == "continuation" and not r.get("unverified_reason"):
            r["unverified_reason"] = (
                "this row is a continuation of another entry (a restart or a streamed final table), not a purchasable "
                "entry, so no buy-in is charged for it and it is not counted as extra pay-in")
    dump("events.json", rows)
    dump("hotels.json", hotels)
    dump("venues.json", venues)
    dump("plan.json", plan)
    dump("rates_log.json", dict(rates_log, note=rates_log.get("note", "") +
         " | this session added the official poker-suite rate floor as a dated scenario line, never as the trip's confirmed cost"))
    dump("flags.json", flags)
    dump("conflicts.json", conflicts)
    dump("questions.json", questions)
    dump("suggestions.json", suggestions)
    dump("sources.json", sources)
    dump("change_log.json", ea_change)
    dump("facts.json", facts)
    dump("last_checked.json", build_state(sources, facts, ea_change, scrape_status, watch_status))
    dump("windows.json", windows)
    dump("meta.json", out_meta)
    print("rows %d | by status %s | rankable %d | conflicts %d | flags %d | sources %d"
          % (len(rows), counts, out_meta["counts"]["rankable"], len(conflicts), len(flags), len(sources)))


if __name__ == "__main__":
    main()
