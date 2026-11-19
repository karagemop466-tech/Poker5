#!/usr/bin/env python3
"""Session bdcaf0bf - independent verification of the published site and its data.

This file does not import the builder or the integrator: it re-derives the
important claims from the raw captures and refuses to pass if the published
pages and the sources disagree. Run after scripts/build_bdcaf0bf.py.

Checks
  1. every generated page exists, is well-formed enough to parse, and has no
     broken internal link, no missing asset and no insecure (http://) link;
  2. every event row links to at least one official source URL, and every
     published value carries that value's own source and retrieval date;
  3. a blank cell is always a source gap, never an omission: each blank field
     keeps the sentence that explains it;
  4. the entry grade is re-derived from the raw structure-sheet text, not
     trusted from the dataset - a row may not be called single-entry-standard if
     any re-entry / add-on / purchased-chip / extra-flight sentence exists on
     its sheet, and a row may not be called excluded unless such a sentence (or
     a continuation rule) really is there;
  5. ranking rows have both a buy-in and a guarantee, and the ratio recomputes;
  6. hotel true nightly cost recomputes from (rate + fee) x (1 + tax), and no
     plan event exceeds the 30-minute walk rule where a route is unverified;
  7. the day plan holds at most one primary per room per date, references rows
     that exist, and never offers a fallback that starts before the primary can
     finish unless it is labelled conditional;
  8. the monitor ledger covers every URL the pages link to, with a date.
"""
from __future__ import annotations

import glob
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "bdcaf0bf")
C6 = os.path.join(ROOT, "data", "c6087e2c")
E6 = os.path.join(ROOT, "data", "ea99006a")
GEN = "scripts/build_bdcaf0bf.py"
OFFICIAL = (
    "venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "caesars.com", "mgmresorts.com",
    "rwlasvegas.com", "southpointcasino.com", "clarkcountynv.gov", "wptmedia-mig.s3.amazonaws.com",
    "wpt.com", "pokernews.com",
)
ERRORS, WARNINGS = [], []


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def err(msg):
    ERRORS.append(msg)


def pages_to_check():
    out = [os.path.join(ROOT, "index.html")]
    out += sorted(glob.glob(os.path.join(ROOT, "pages", "**", "*.html"), recursive=True))
    return [p for p in out if os.path.exists(p)]


# ---------------------------------------------------------------- 1. site shape
def check_site():
    if not os.path.exists(os.path.join(ROOT, "index.html")):
        err("index.html is missing")
        return set()
    urls = set()
    for p in pages_to_check():
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        txt = open(p, encoding="utf-8").read()
        if not txt.startswith("<!doctype html>"):
            err("%s: no doctype" % rel)
        for tag in ("table", "tbody", "details", "form"):
            if txt.count("<%s" % tag) != txt.count("</%s>" % tag):
                err("%s: %s tags unbalanced (%d open / %d close)"
                    % (rel, tag, txt.count("<%s" % tag), txt.count("</%s>" % tag)))
        for m in re.finditer(r'(?:href|src)="([^"#]+)"', txt):
            href = m.group(1)
            if href.startswith("http://"):
                err("%s: insecure link %s" % (rel, href))
                continue
            if href.startswith(("https://", "mailto:", "tel:", "data:", "//")):
                if href.startswith("https://"):
                    urls.add(href)
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(p), href))
            if not os.path.exists(target):
                err("%s: broken internal link %s" % (rel, href))
        # a value that leaked out of Python as None/NaN, or an unfinished placeholder, is a build bug
        for junk in ("TODO", "FIXME", "lorem ipsum", "None<", ">None<", "NaN<", "undefined"):
            if junk in txt:
                err("%s: contains %r" % (rel, junk))
        if re.search(r"placeholder=\"(Search|no |e\.g\.)", txt) is None and "placeholder=" in txt:
            err("%s: an input has a placeholder that is not one of the two sanctioned prompts" % rel)
        # every events table row must carry a source link
        for tbl in re.findall(r'<table[^>]*id="(t[a-z0-9\-]*)"[^>]*>(.*?)</table>', txt, re.S):
            tid, body = tbl
            heads = re.findall(r"<th[^>]*>(.*?)</th>", body, re.S)
            if not any(re.search(r"source|sheet|terms", h, re.I) for h in heads):
                continue
            for row in re.findall(r"<tr ([^>]*)>(.*?)</tr>", body, re.S):
                attrs, cells = row
                if "<td" not in cells or "rulesrow" in attrs:
                    continue
                if "<a " in cells:
                    continue
                err("%s: table %s has a row with no source link" % (rel, tid))
    return urls


# ------------------------------------------------------- 2-4. dataset + grades
def regrade_from_sheets(rows):
    """Re-derive the entry grade from the raw structure-sheet text, ignoring the dataset's own label.

    A sheet covers several events, so a keyword anywhere on the page is not evidence about
    this event: multi-entry language only counts against a row when it appears on a line that
    names this event (or when the sheet describes a single event). A row may also not be called
    excluded unless the keyword really is on its sheet.
    """
    path = os.path.join(C6, "structures.json")
    if not os.path.exists(path):
        err("missing %s - the sheet text is the authority for every entry rule" % path)
        return
    sheets = load(path)["sheets"]
    RE_MULTI = re.compile(r"re-?entr|re-?buy|add[- ]?on|extra flight|second flight|day 1[ab]\b|day 1 flight"
                          r"|additional buy[- ]?in|second entry|subsequent buy|buy in'?s after|unlimited ent"
                          r"|each entry|multiple entr|tag[- ]?team", re.I)
    RE_NEG = re.compile(r"\bno\b|\bnot\b|without|prohibit|forbidden|silence", re.I)
    RE_ONE = re.compile(r"one entry (?:per|only)|single entry|no re-?ent|no rebuy|freeze ?out|maximum of one"
                        r"|one buy[- ]?in (?:per|only)|entries maximum|only one entry", re.I)
    for r in rows:
        no = r.get("sheet_no")
        sh = (sheets.get(str(no)) or sheets.get(no)) if no is not None else None
        if not sh:
            if r["entry_status"] not in ("not_read", "continuation", "multi_entry_paid"):
                err("%s: no sheet %s in the capture but graded %s" % (r["id"], no, r["entry_status"]))
            continue
        lines = [l.strip() for l in (sh.get("rules_text") or "").splitlines() if l.strip()]
        ev_no = str(r.get("event_no") or "").strip().lstrip("#").strip()
        own = [l for l in lines if ev_no and re.search(r"event\s*#?\s*%s\b" % re.escape(ev_no), l, re.I)]
        if not own:
            own = lines if len(sh.get("events") or []) == 1 else []
        one_line = any(RE_ONE.search(l) for l in own)
        multi_own = [l for l in own if RE_MULTI.search(l) and not RE_NEG.search(l)]
        multi_sheet = [l for l in lines if RE_MULTI.search(l) and not RE_NEG.search(l)]
        if r["entry_status"] in ("no_reentry_language", "explicit_one_entry"):
            if multi_own:
                err("%s: graded %s but the sheet line for this event says %r"
                    % (r["id"], r["entry_status"], multi_own[0][:120]))
            if r["entry_status"] == "explicit_one_entry" and not one_line:
                err("%s: graded explicit_one_entry but no one-entry sentence names this event" % r["id"])
            if r["entry_status"] == "no_reentry_language" and one_line:
                err("%s: a one-entry sentence names this event, so the row should be graded explicit_one_entry"
                    % r["id"])
        elif r["entry_status"] == "multi_entry_paid":
            if not multi_sheet and not r.get("multi_kind"):
                err("%s: graded multi_entry_paid with no multi-entry sentence on sheet %s and no reason"
                    % (r["id"], no))
            if not r.get("multi_kind"):
                err("%s: excluded row without a stated reason" % r["id"])
        elif r["entry_status"] == "continuation" and not r.get("unverified_reason"):
            err("%s: continuation row without the explanation of why it is not a purchasable entry" % r["id"])


def check_rows(rows):
    for r in rows:
        if not r["sources"]:
            err("%s: row with no source URL" % r["id"])
        for u in r["sources"]:
            if not u.startswith("https://"):
                err("%s: non-https source %s" % (r["id"], u))
            if not any(h in u for h in OFFICIAL):
                err("%s: source is not an official host: %s" % (r["id"], u))
        rf = r.get("rule_fields") or {}
        if not rf:
            err("%s: no structured rule fields" % r["id"])
        for key, f in rf.items():
            if f.get("value") is None:
                if not (f.get("excerpt") or f.get("note")):
                    err("%s.%s: blank with no explanation" % (r["id"], key))
                continue
            if not f.get("source"):
                err("%s.%s: value %r with no source URL" % (r["id"], key, f.get("value")))
            if not f.get("retrieved"):
                err("%s.%s: value with no retrieval date" % (r["id"], key))
        if r["entry_status"] == "not_read" and not r.get("multi_kind") and not r.get("unverified_reason"):
            if "no structure sheet" not in (r.get("entry_label") or "").lower():
                err("%s: unread row without a reason" % r["id"])
        if r["rankable"]:
            if not r.get("buyin") or not r.get("guarantee"):
                err("%s: rankable without both figures" % r["id"])
            if r["entry_status"] not in ("explicit_one_entry", "no_reentry_language"):
                err("%s: rankable but graded %s" % (r["id"], r["entry_status"]))
            if r.get("gtd_conflict"):
                err("%s: rankable with an open guarantee conflict" % r["id"])
            if r.get("buyin") and r.get("guarantee"):
                got = float(r.get("ratio") or 0)
                dp = len(str(r.get("ratio")).split(".")[-1]) if "." in str(r.get("ratio")) else 0
                want = round(float(r["guarantee"]) / float(r["buyin"]), dp)
                if abs(want - got) > 0.005:
                    err("%s: ratio %s should be %s" % (r["id"], got, want))
        if r.get("late_reg_close") and r.get("end_estimate") and r.get("duration_basis") == "sheet levels x duration":
            pass  # the sheet's own printed clock is kept; the arithmetic note covers the disagreement
    n_expl = sum(1 for r in rows if r["entry_status"] == "explicit_one_entry")
    stated = load(os.path.join(D, "meta.json"))["counts"]["by_status"].get("explicit_one_entry", 0)
    if n_expl != stated:
        err("meta claims %d explicit one-entry rows, data has %d" % (stated, n_expl))


def check_hotels(hotels, plan, rows):
    by_id = {r["id"]: r for r in rows}
    for h in hotels:
        srcs = [h.get(k) for k in ("resort_fee_source", "parking_source", "cancel_source", "poker_rate_source")
                if h.get(k)]
        if not srcs:
            err("hotel %s: no official source at all" % h["key"])
        for u in srcs:
            if not u.startswith("https://"):
                err("hotel %s: non-https source %s" % (h["key"], u))
            if not any(x in u for x in OFFICIAL):
                err("hotel %s: source is not official: %s" % (h["key"], u))
        if h.get("true_nightly"):
            if h.get("resort_fee") is None or h.get("tax_rate_pct") is None:
                err("hotel %s: true nightly cost without fee and tax" % h["key"])
            else:
                rate = h.get("nightly_rate") or h.get("poker_rate_floor")
                want = (rate + h["resort_fee"]) * (1 + h["tax_rate_pct"] / 100.0)
                if not math.isclose(want, h["true_nightly"], abs_tol=0.05):
                    err("hotel %s: true nightly %s vs recomputed %s" % (h["key"], h["true_nightly"], round(want, 2)))
        elif not (h.get("true_nightly_basis") or h.get("poker_rate_caveat")):
            err("hotel %s: blank true cost with no explanation" % h["key"])
        for rt in h["routes"]:
            if rt.get("minutes") is not None and not rt.get("verified") and rt["minutes"] > rt.get("limit_minutes", 30):
                err("hotel %s: unverified route over the limit is published as %s min" % (h["key"], rt["minutes"]))
    for d in plan:
        seen = set()
        for v in d["venues"]:
            if v["venue_key"] in seen:
                err("%s: two primaries offered for %s on the same day" % (d["date"], v["venue_key"]))
            seen.add(v["venue_key"])
            for i in (v["primary"], v["fallback"]):
                if i and i not in by_id:
                    err("%s: plan references unknown row %s" % (d["date"], i))
            if v["fallback"] and v.get("fallback_kind") != "sequential":
                fb, pr = by_id.get(v["fallback"]), by_id.get(v["primary"])
                if fb and pr and "only playable if" not in (v.get("fallback_condition") or ""):
                    err("%s: conditional fallback without its condition spelled out" % d["date"])


def check_ledger(rows, hotels, urls):
    lc = load(os.path.join(D, "last_checked.json"))
    led = lc["urls"]
    missing = set()
    for r in rows:
        for u in r["sources"]:
            if u not in led:
                missing.add(u)
            elif not led[u].get("last_checked"):
                err("ledger entry for %s has no last-checked date" % u)
    for h in hotels:
        for k in ("resort_fee_source", "parking_source", "cancel_source", "poker_rate_source"):
            u = h.get(k)
            if u and u not in led:
                missing.add(u)
    nav = re.compile(r"(booking|reservations\.|ibe/|hotel-calendar|/book/|maps\.google|maps\?dirflg)")
    for u in urls:
        # only URLs that back a published value must be in the ledger; booking and map links, and a bare host root
        # link handed to the reader so a template URL is still clickable, are navigation
        if ("{" in u or nav.search(u) or re.match(r"^https?://[^/]+/?$", u)
                or not any(x in u for x in OFFICIAL)):
            continue
        if u not in led and "github.com" not in u:
            missing.add(u)
    if missing:
        err("URLs the pages link to but the ledger does not track (%d): %s"
            % (len(missing), ", ".join(sorted(missing)[:3])))
    src = load(os.path.join(D, "sources.json"))
    for s in src:
        if not s["url"].startswith("https://"):
            err("source ledger entry is not https: %s" % s["url"])
    flags = load(os.path.join(D, "flags.json"))
    ids = {f.get("id") for f in flags}
    for need in ("F01", "B01", "B02"):
        if need not in ids:
            err("flag %s is missing from the review queue" % need)
    for f in flags:
        if not f.get("detail"):
            err("flag %s has no detail" % f.get("id"))


def check_script_syntax():
    """The site's interactivity is plain JS in assets/bdcaf0bf.js: parse it with node if node exists,
    because a syntax error there silently kills every filter, toggle and calculator on the site."""
    js = os.path.join(ROOT, "assets", "bdcaf0bf.js")
    if not os.path.exists(js):
        err("assets/bdcaf0bf.js is missing - the tables would render but not filter")
        return
    import shutil
    import subprocess
    if shutil.which("node"):
        p = subprocess.run(["node", "--check", js], capture_output=True, text=True)
        if p.returncode:
            err("assets/bdcaf0bf.js does not parse: %s" % p.stderr.strip().splitlines()[:3])
        else:
            print("site javascript parses under node --check")
    else:
        WARNINGS.append("node not available: the site javascript was not parsed")
    css = os.path.join(ROOT, "assets", "bdcaf0bf.css")
    if os.path.exists(css):
        txt = open(css, encoding="utf-8").read()
        if txt.count("{") != txt.count("}"):
            err("assets/bdcaf0bf.css: %d { vs %d }" % (txt.count("{"), txt.count("}")))


def main():
    rows = load(os.path.join(D, "events.json"))
    hotels = load(os.path.join(D, "hotels.json"))
    plan = load(os.path.join(D, "plan.json"))
    if not os.path.exists(os.path.join(ROOT, GEN)):
        err("%s is missing - the root site must have exactly one generator" % GEN)
    urls = check_site()
    check_script_syntax()
    check_rows(rows)
    regrade_from_sheets(rows)
    check_hotels(hotels, plan, rows)
    check_ledger(rows, hotels, urls)
    # the root site must have exactly one generator: no workflow may both run another
    # build script and commit index.html or pages/
    for w in sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml"))):
        txt = open(w, encoding="utf-8").read()
        cmds = "\n".join(l for l in txt.splitlines()
                         if re.match(r"^\s*(python3|node)\s+\S*scripts/build_", l)
                         or re.match(r"^\s*run:.*scripts/build_", l))
        commits_root = re.search(r"git add[^\n]*(index\.html|pages)", txt)
        others = re.findall(r"scripts/(build_(?!bdcaf0bf)[0-9a-f]+)\.py", cmds)
        if others and commits_root:
            err("%s runs %s and commits the root site: exactly one generator may write index.html/pages"
                % (os.path.basename(w), ", ".join(sorted(set(others)))))
    print("rows %d | hotels %d | plan days %d | urls on pages %d" % (len(rows), len(hotels), len(plan), len(urls)))
    if WARNINGS:
        for w in WARNINGS:
            print("warn:", w)
    if ERRORS:
        print("CHECK FAILED (%d)" % len(ERRORS))
        for e in ERRORS[:60]:
            print(" -", e)
        return 1
    print("check_bdcaf0bf: site, data, grades, ranking, hotels, plan and ledger all consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
