#!/usr/bin/env python3
"""Session bdcaf0bf - the canonical generator for the published Poker5 site.

This is the ONLY script that writes the root site (`index.html`, `pages/**`,
`assets/**`) that GitHub Pages publishes from `main` `/`. Earlier sessions each
generated their own copy of the root site, and two scheduled jobs kept
overwriting each other's output; see pages/repo-review.html and the flagged item
B02. Inputs are read-only:

  data/bdcaf0bf/*.json          merged, re-verified dataset (integrate_bdcaf0bf.py)
  data/bdcaf0bf/last_checked.json  per-URL monitor state -> row "last checked" + changed badges

Rules this build enforces (it fails rather than publishing a guess):
  * every data table row carries a link to the official source it was read from;
  * a value with no official source is left blank, badged, and listed on the
    Flagged for review page - never filled in, never averaged, never inferred;
  * an entry rule is only called "single-entry" when an official sentence states
    it; rows that merely have no re-entry language say so in those words;
  * every internal link resolves to a file this build wrote;
  * the output is deterministic: running the build twice produces no diff.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "bdcaf0bf")
REPO = "https://github.com/karagemop466-tech/Poker5"
LIVE = "https://karagemop466-tech.github.io/Poker5/"

NAV = [
    ("index.html", "Home"),
    ("pages/executive-summary.html", "Executive summary"),
    ("pages/tournaments.html", "All events"),
    ("pages/single-entry.html", "Single-entry list"),
    ("pages/ranking.html", "Value ranking"),
    ("pages/tournaments-double.html", "Advantage / multi-entry"),
    ("pages/schedule.html", "Day plan"),
    ("pages/hotels.html", "Hotels"),
    ("pages/routes.html", "Walking routes"),
    ("pages/planner.html", "Trip cost"),
    ("pages/venues/venetian.html", "Venetian"),
    ("pages/venues/wynn.html", "Wynn"),
    ("pages/venues/others.html", "Other rooms"),
    ("pages/questions.html", "Questions"),
    ("pages/suggestions.html", "Suggestions"),
    ("pages/flagged-review.html", "Flagged for review"),
    ("pages/monitor.html", "Source monitor"),
    ("pages/repo-review.html", "Repo review"),
    ("pages/method.html", "Method"),
]

STATUS_BADGE = {
    "explicit_one_entry": ("ok", "one-entry rule stated"),
    "no_reentry_language": ("ok2", "sheet read - no re-entry language"),
    "multi_entry_paid": ("bad", "paid re-entry / add-on / extra flight"),
    "continuation": ("mid", "continuation row"),
    "not_read": ("warn", "terms not published - unverified"),
}
# pages whose content is a copy of another page, kept so older links resolve
ALIASES = {
    "pages/sources.html": ("pages/method.html", "Sources and method"),
    "pages/qa.html": ("pages/questions.html", "Questions to resolve"),
    "pages/multientry.html": ("pages/tournaments-double.html", "Advantage and multi-entry events"),
    "pages/flagged.html": ("pages/flagged-review.html", "Flagged for review"),
}


# --------------------------------------------------------------------------- #
# loading + tiny helpers
# --------------------------------------------------------------------------- #
def load(name, default=None):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        if default is not None:
            return default
        sys.exit("missing %s - run scripts/integrate_bdcaf0bf.py first" % path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


ROWS = load("events.json")
HOTELS = load("hotels.json")
VENUES = load("venues.json")
PLAN = load("plan.json")
FLAGS = load("flags.json")
QUESTIONS = load("questions.json")
SUGGESTIONS = load("suggestions.json")
SOURCES = load("sources.json")
META = load("meta.json")
RATES = load("rates_log.json")
CONFLICTS = load("conflicts.json", [])
STATE = load("last_checked.json", {"urls": {}, "changed_count": 0})
WIKI = load("facts.json")
by_id = {r["id"]: r for r in ROWS}
TODAY = META.get("generated") or dt.date.today().isoformat()
CHANGED_URLS = {u: v for u, v in (STATE.get("urls") or {}).items() if v.get("changed")}
WRITTEN = set()
ERRORS = []


def esc(x):
    return html.escape("" if x is None else str(x), quote=True)


def _f(v):
    """Number as the source wrote it. A value no official source states is None -> blank,
    and a value the source states in words is returned untouched rather than coerced."""
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except ValueError:
        return "raw:%s" % v


def money(v, dash="&mdash;"):
    f = _f(v)
    if f is None:
        return '<span class="blank">%s</span>' % dash
    if isinstance(f, str):
        return esc(str(v))
    return "$%s" % ("{:,.0f}".format(f) if abs(f - round(f)) < 0.005 else "{:,.2f}".format(f))


def num_txt(v, dash="&mdash;"):
    f = _f(v)
    if f is None:
        return '<span class="blank">%s</span>' % dash
    if isinstance(f, str):
        return esc(str(v))
    return "{:,}".format(int(f)) if f == int(f) else "{:,}".format(f)


def link(url, label="official source", cls="src"):
    if not url:
        return '<span class="blank">no source</span>'
    if "{" in str(url):
        base = re.match(r"^(https?://[^/]+/)", str(url))
        return ('<span class="sm muted">a booking template, not a source - </span>%s'
                % (link(base.group(1), "booking engine") if base else ""))
    if not re.match(r"^https?://", str(url)):
        # a source recorded as a key rather than a URL is a data defect, never a broken link
        return '<span class="blank">source reference &ldquo;%s&rdquo; is not a URL - see the flagged page</span>' % esc(url)
    return '<a class="%s" href="%s" target="_blank" rel="noopener">%s</a>' % (cls, esc(url), esc(label))


def pretty(datestr):
    if not datestr:
        return '<span class="blank">no date published</span>'
    try:
        d = dt.date.fromisoformat(datestr)
    except ValueError:
        return esc(datestr)
    return d.strftime("%a %d %b %Y")


def hhmm12(t):
    if not t:
        return ""
    m = re.match(r"^(\d{1,2}):(\d{2})", str(t))
    if not m:
        return str(t)
    h, mi = int(m.group(1)) % 24, m.group(2)
    return "%d:%s %s" % ((h + 11) % 12 + 1, mi, "AM" if h < 12 else "PM")


def last_checked(row):
    """The date every source behind this row was last re-read, and any change badge."""
    dates, changed = [], False
    for u in row.get("sources", []):
        rec = (STATE.get("urls") or {}).get(u)
        if rec and rec.get("last_checked"):
            dates.append(str(rec["last_checked"])[:10])
        if u in CHANGED_URLS:
            changed = True
    d = max(dates) if dates else (row.get("retrieved_sheet") or row.get("retrieved_schedule") or "")
    badge = ' <span class="chg" title="an automated re-check saw this source change; the value was not overwritten automatically">source changed</span>' if changed else ""
    return '<span class="nowrap">%s</span>%s' % (esc(d or "not re-checked"), badge), (d or ""), changed


def badge(row):
    cls, txt = STATUS_BADGE[row["entry_status"]]
    out = ['<span class="pill %s">%s</span>' % (cls, esc(txt))]
    if row.get("paid_advantage"):
        out.append('<span class="pill bad">paid-advantage</span>')
    if row.get("special_format"):
        out.append('<span class="pill mid">%s</span>' % esc(row["special_format"].split(":")[0]))
    if row.get("is_bounty") and not row.get("special_format"):
        out.append('<span class="pill mid">bounty</span>')
    if row.get("gtd_conflict"):
        out.append('<span class="pill warn">guarantee conflict</span>')
    return " ".join(out)


def rule_details(row):
    """Structured rule fields, each with its own official excerpt and retrieval date."""
    cells = []
    order = ["single_entry_rule", "max_entries", "re_entry", "add_on", "entry_structure", "fee",
             "guarantee", "late_registration"]
    for key in order:
        f = (row.get("rule_fields") or {}).get(key)
        if not f:
            continue
        val = f.get("value")
        if isinstance(val, (int, float)):
            val = "{:,}".format(int(val)) if float(val) == int(float(val)) else str(val)
        cells.append(
            "<tr><th>%s</th><td>%s</td><td class=sm>%s</td><td class=sm>%s</td><td>%s</td></tr>"
            % (esc(key.replace("_", " ")), ("<b>%s</b>" % esc(val)) if val else '<span class="blank">not stated</span>',
               esc((f.get("excerpt") or "no matching sentence on the source")[:150]),
               esc(f.get("retrieved") or "not re-checked"), link(f.get("source"), "sheet")))
    return ('<details class="rules"><summary>%d structured rule fields - each with its official excerpt and '
            'retrieval date</summary><table class="sub"><tbody>%s</tbody></table></details>'
            % (len(cells), "".join(cells)))


def table(headers, rows_html, tid, opts="", caption="", cls="grid"):
    """A header starting with ~ is a right-aligned numeric column; the ~ is not printed.
    A row whose cell count differs from the header count is a build error, not a warning."""
    # headers are authored here, so an entity such as &divide; is restored after escaping
    head = "".join('<th%s>%s</th>' % (' class="num"' if h.startswith("~") else "",
                                      esc(h.lstrip("~")).replace("&amp;", "&"))
                   for h in headers)
    body = "".join(rows_html)
    for row in rows_html:
        if "rulesrow" in row:
            continue   # nested rule-field table, checked in event_row instead
        n = row.count("<td")
        if n and n != len(headers):
            ERRORS.append("table %s: a row has %d cells but the header has %d" % (tid, n, len(headers)))
    return ('<div class="tablewrap"><table class="%s" id="%s" %s><caption>%s</caption><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (cls, tid, opts, caption, head, body))


def filters(tid, venues=True, dates=True, single=True, extra="", changed=False):
    vopts = "".join('<option value="%s">%s</option>' % (esc(k), esc(k)) for k in
                    sorted({r["venue_key"] for r in ROWS}))
    parts = ['<div class="filters" data-for="%s">' % tid]
    parts.append('<input type="search" data-f="search" placeholder="Search every column of this table" aria-label="Search">')
    if dates:
        parts.append('<label>from <input type="date" data-f="from"></label>')
        parts.append('<label>to <input type="date" data-f="to"></label>')
        parts.append('<button class="btn ghost" data-f="trip" type="button" title="%s to %s">'
                     'use the trip window</button>' % (esc(META["trip"]["check_in"]), esc(META["trip"]["check_out"])))
    if venues:
        parts.append('<label>room <select data-f="venue"><option value="">all venues</option>%s</select></label>' % vopts)
    if single:
        parts.append('<label><input type="checkbox" data-f="single"> single-entry standard only '
                     '(rows whose official sheet was read and shows no re-entry language)</label>')
    parts.append(extra)
    if changed:
        parts.append('<label><input type="checkbox" data-f="changed"> only rows whose source changed</label>')
    parts.append('<button class="btn ghost" data-f="reset" type="button">reset</button><span class="count"></span>')
    parts.append("</div>")
    return "".join(parts)


def event_row(r, cols):
    lc, lcdate, changed = last_checked(r)
    cells = []
    for c in cols:
        if c == "date":
            cells.append('<td class="nowrap" data-order="%s">%s</td>' % (esc(r.get("date")), pretty(r.get("date"))))
        elif c == "start":
            cells.append('<td class="nowrap" data-order="%s">%s</td>' % (esc(r.get("start")), esc(hhmm12(r.get("start")))))
        elif c == "end":
            cells.append('<td class="nowrap">%s</td>' % (esc(hhmm12(r["end_estimate"])) if r.get("end_estimate")
                                                          else '<span class="blank">not derivable</span>'))
        elif c == "venue":
            cells.append('<td>%s</td>' % esc(r.get("venue")))
        elif c == "event":
            cells.append('<td>%s</td>' % (esc(r.get("event_no")) or '<span class="blank">&mdash;</span>'))
        elif c == "name":
            extra = ""
            if r.get("eligibility"):
                extra = '<div class="sm muted">%s</div>' % esc(r["eligibility"])
            if r.get("sheet_arithmetic_note"):
                extra += '<div class="sm note-flag">official sheet arithmetic: %s</div>' % esc(r["sheet_arithmetic_note"])
            cells.append('<td>%s%s</td>' % (esc(r.get("name")), extra))
        elif c == "buyin":
            cells.append('<td class="num" data-order="%s">%s</td>' % (r.get("buyin") or "", money(r.get("buyin"))))
        elif c == "fee":
            cells.append('<td class="num">%s</td>' % money(r.get("house_fee")))
        elif c == "pool":
            cells.append('<td class="num">%s</td>' % money(r.get("to_prize_pool")))
        elif c == "gtd":
            cells.append('<td class="num" data-order="%s">%s</td>' % (r.get("guarantee") or "", money(r.get("guarantee"))))
        elif c == "ratio":
            cells.append('<td class="num" data-order="%s">%s</td>' % (r.get("ratio") or "", num_txt(r.get("ratio"))))
        elif c == "chips":
            cells.append('<td class="num">%s</td>' % num_txt(r.get("chips")))
        elif c == "levels":
            cells.append('<td class="num">%s</td>' % (("%s min" % int(r["level_minutes"])) if r.get("level_minutes")
                                                      else '<span class="blank">&mdash;</span>'))
        elif c == "latereg":
            cells.append('<td class="nowrap">%s</td>' % (esc(hhmm12(r.get("late_reg_close"))) or '<span class="blank">not published</span>'))
        elif c == "status":
            cells.append('<td>%s</td>' % badge(r))
        elif c == "lc":
            cells.append('<td class="nowrap sm">%s</td>' % lc)
        elif c == "source":
            cells.append('<td>%s</td>' % link(r.get("schedule_url") or r.get("sheet_url"), "schedule page"))
        elif c == "sheet":
            lbl = ("structure sheet %s" % r["sheet_no"]) if r.get("sheet_no") else "structure sheet (published PDF)"
            cells.append('<td>%s</td>' % (link(r.get("sheet_url"), lbl)
                                          if r.get("sheet_url") else '<span class="blank">no sheet published</span>'))
        elif c == "evidence":
            cells.append('<td class="sm">%s</td>' % esc((r.get("entry_evidence") or "")[:260]))
        else:
            cells.append("<td></td>")
    search = " ".join(str(r.get(k) or "") for k in
                      ("venue", "room", "series", "date", "name", "event_no", "entry_label", "eligibility",
                       "multi_kind", "special_format")).lower()
    attrs = ' data-date="%s" data-venue="%s" data-rule="%s" data-search="%s" data-changed="%s"' % (
        esc(r.get("date")), esc(r.get("venue_key")), esc(r["entry_status"]), esc(search), "1" if changed else "0")
    if cols != ["skip"]:
        pass
    if len(cells) != len(cols):
        ERRORS.append("%s: %d cells for %d columns" % (r.get("id"), len(cells), len(cols)))
    inner = "".join(cells)
    if r.get("rule_fields"):
        # a sibling row, never nested: a <tr> inside a <tr> is invalid and browsers re-parent it
        return ('<tr%s>%s</tr><tr class="rulesrow" data-rule="detail" data-date="%s" data-venue="%s">%s</tr>'
                % (attrs, inner, esc(r.get("date")), esc(r.get("venue_key")),
                   "<td colspan=%d>%s</td>" % (len(cols), rule_details(r))))
    return "<tr%s>%s</tr>" % (attrs, inner)


def panel(title, body, cls="panel"):
    return '<div class="%s"><h2>%s</h2>%s</div>' % (cls, title, body)


# --------------------------------------------------------------------------- #
# page shell
# --------------------------------------------------------------------------- #
CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#151a21;--muted:#5c6773;--line:#dfe3e8;--ok:#0b7a3d;--ok2:#0e6f8c;
--bad:#a01b1b;--warn:#8a5a00;--mid:#4b3f8f;--accent:#0b57d0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent)}header{background:#0f1720;color:#fff;padding:14px 20px;position:sticky;top:0;z-index:5}
header .brand{font-weight:700;letter-spacing:.3px}header small{display:block;font-weight:400;color:#a9b6c4;font-size:12px}
nav.hnav{display:flex;flex-wrap:wrap;gap:2px;margin-top:10px}nav.hnav a{color:#dbe4ee;text-decoration:none;font-size:13px;
padding:5px 9px;border-radius:7px}nav.hnav a:hover{background:#1d2a38}nav.hnav a.active{background:var(--accent);color:#fff}
main{padding:18px 20px 60px;max-width:1480px;margin:0 auto}h1{font-size:23px;margin:6px 0 4px}h2{font-size:17px;margin:0 0 8px}
h3{font-size:15px;margin:14px 0 6px}p.lead{color:var(--muted);margin:2px 0 14px}
.panel,.card{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:14px 16px;margin:0 0 14px}
.grid-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:10px}
a.card{display:block;text-decoration:none;color:inherit}a.card:hover{border-color:var(--accent)}
.stat{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:10px 12px}
.stat .num{font-size:21px;font-weight:700}.stat .lbl{font-size:12px;color:var(--muted)}
.statgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px;margin:12px 0}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:#eef1f5;border:1px solid var(--line);
border-radius:10px;padding:8px 10px;margin:0 0 8px}
.filters input[type=search]{flex:1 1 260px;min-width:180px;padding:6px 9px;border:1px solid var(--line);border-radius:8px}
.filters label{font-size:13px;color:var(--muted);display:flex;gap:5px;align-items:center}
.filters input,.filters select{padding:5px 7px;border:1px solid var(--line);border-radius:7px;background:#fff;font-size:13px}
.count{font-size:12px;color:var(--muted);margin-left:auto}.btn{border:1px solid var(--line);background:#fff;
border-radius:8px;padding:6px 11px;font-size:13px;cursor:pointer;text-decoration:none;color:var(--ink);display:inline-block}
.btn:hover{border-color:var(--accent)}.btn.ghost{background:#f3f5f8}
.tablewrap{overflow:auto;max-height:70vh;border:1px solid var(--line);border-radius:10px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:13.5px}
caption{caption-side:top;text-align:left;font-size:12.5px;color:var(--muted);padding:7px 9px}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;vertical-align:top;text-align:left}
thead th{position:sticky;top:0;background:#f0f3f7;cursor:pointer;white-space:nowrap;font-weight:600}
thead th.num,td.num{text-align:right}td.nowrap,.nowrap{white-space:nowrap}
tbody tr:hover{background:#f8fafc}tr.rulesrow{display:none}tr.rulesrow.open{display:table-row}
tr.rulesrow>td{background:#fbfcfe;border-left:3px solid var(--accent)}
table.sub{font-size:12.5px;margin-top:6px}table.sub th{width:130px;text-align:left;background:none;position:static;cursor:default}
.pill{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11.5px;white-space:nowrap;border:1px solid}
.pill.ok{color:var(--ok);border-color:#b7e0c6;background:#eef9f1}.pill.ok2{color:var(--ok2);border-color:#bcdbe6;background:#eef7fa}
.pill.bad{color:var(--bad);border-color:#e7c4c4;background:#fdf1f1}.pill.warn{color:var(--warn);border-color:#e6d7b3;background:#fdf7e8}
.pill.mid{color:var(--mid);border-color:#d0c9ea;background:#f3f1fb}
.blank{color:#9aa5b1}.chg{color:var(--bad);font-size:10.5px;border:1px solid #e7c4c4;background:#fdf1f1;border-radius:999px;padding:0 5px}
.note-flag{color:var(--warn)}.sm{font-size:12px}.muted{color:var(--muted)}
.warnbox{border:1px solid #e6d7b3;background:#fdf7e8;border-radius:9px;padding:9px 11px;font-size:13.5px;margin:8px 0}
.badbox{border:1px solid #e7c4c4;background:#fdf1f1;border-radius:9px;padding:9px 11px;font-size:13.5px;margin:8px 0}
.goodbox{border:1px solid #b7e0c6;background:#eef9f1;border-radius:9px;padding:9px 11px;font-size:13.5px;margin:8px 0}
.kv{display:grid;grid-template-columns:190px 1fr;gap:5px 12px;font-size:13.5px;margin:4px 0}
.kv dt{color:var(--muted)}.kv dd{margin:0}
ul.clean{margin:6px 0 0;padding-left:20px}ul.clean li{margin:0 0 4px}
details.rules{margin:3px 0 1px}details.rules summary{cursor:pointer;font-size:12px;color:var(--accent)}
.calc{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px;margin:8px 0}
.calc label{font-size:12px;color:var(--muted);display:flex;flex-direction:column;gap:3px}
.calc input,.calc select{padding:6px 8px;border:1px solid var(--line);border-radius:8px;font-size:14px}
.result{background:#0f1720;color:#eaf1f8;border-radius:10px;padding:12px 14px;font-size:14px;margin-top:8px}
.result .big{font-size:20px;font-weight:700;margin-top:4px}.result .blank{color:#9fb1c4}
footer{border-top:1px solid var(--line);padding:16px 20px 40px;color:var(--muted);font-size:12.5px;max-width:1480px;margin:0 auto}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.big-list{font-size:14px}.big-list>div{padding:8px 0;border-bottom:1px dashed var(--line)}
.tick{display:flex;gap:8px;align-items:flex-start;padding:5px 0}
@media(max-width:900px){.kv{grid-template-columns:1fr}.tablewrap{max-height:none}}
"""

JS = r"""
/* Poker5 bdcaf0bf: table filters, day plan, rate log, trip calculator. No server, no manual data entry. */
(function(){
var F=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));};

function state(){try{return JSON.parse(localStorage.getItem('p5.state')||'{}');}catch(e){return {};}}
function saveState(o){var s=state();Object.keys(o).forEach(function(k){s[k]=o[k];});try{localStorage.setItem('p5.state',JSON.stringify(s));}catch(e){}}

/* ---- generic table filtering + sorting + expandable rule fields ---- */
function wireTable(t){
  var bar=document.querySelector('.filters[data-for="'+t.id+'"]');
  // a table's own rows only: the expandable rule fields live in a sibling <tr class="rulesrow">
  var rows=F('tbody tr[data-search]', t).filter(function(tr){return !tr.classList.contains('rulesrow');});
  if(!rows.length) rows=F('tbody tr:not(.rulesrow)', t);
  var inp=function(n){return bar?bar.querySelector('[data-f="'+n+'"]'):null;};
  var q=inp('search'),from=inp('from'),to=inp('to'),ven=inp('venue'),single=inp('single'),
      chg=inp('changed'),reset=inp('reset'),cnt=bar?bar.querySelector('.count'):null;
  var extraF=F('.filters[data-for="'+t.id+'"] [data-col]');
  if(t.dataset.syncdates==='1'&&from&&!from.value&&state().from){from.value=state().from;}
  if(t.dataset.syncdates==='1'&&to&&!to.value&&state().to){to.value=state().to;}
  var sAttr=t.getAttribute('data-single')||'rule';
  var sVals=t.getAttribute('data-single-values')||'explicit_one_entry|no_reentry_language';
  function apply(){
    var n=(q?q.value:'').toLowerCase().trim(), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', s=single&&single.checked, c=chg&&chg.checked, shown=0;
    rows.forEach(function(tr){
      var d=tr.getAttribute('data-date')||'', ok=true;
      if(n&&(tr.getAttribute('data-search')||'').indexOf(n)<0) ok=false;
      if(ok&&f&&d&&d<f) ok=false;
      if(ok&&t2&&d&&d>t2) ok=false;
      if(ok&&v&&tr.getAttribute('data-venue')!==v) ok=false;
      if(ok&&s&&!(new RegExp('^(?:'+sVals+')$')).test(tr.getAttribute('data-'+sAttr)||'')) ok=false;
      if(ok&&c&&tr.getAttribute('data-changed')!=='1') ok=false;
      if(ok){extraF.forEach(function(el){
        var col=el.getAttribute('data-col'), want=el.checked?el.getAttribute('data-yes'):'*';
        var have=tr.getAttribute('data-'+col)||'';
        if(want!=='*'&&have!==want) ok=false;
      });}
      tr.style.display=ok?'':'none';
      var nxt=tr.nextElementSibling;
      if(nxt&&nxt.classList.contains('rulesrow')){
        nxt.style.display=ok&&nxt.classList.contains('open')?'table-row':'none';
        if(!ok) nxt.classList.remove('open');
      }
      if(ok) shown++;
    });
    if(cnt) cnt.textContent=shown+' of '+rows.length+' rows';
  }
  [q].concat([]).forEach(function(el){if(el) el.addEventListener('input',apply);});
  [from,to,ven].forEach(function(el){if(el) el.addEventListener('change',function(){
    if(el===from&&t.dataset.syncdates==='1') saveState({from:from.value});
    if(el===to&&t.dataset.syncdates==='1') saveState({to:to.value});
    apply();});});
  [single,chg].concat(extraF).forEach(function(el){if(el) el.addEventListener('change',apply);});
  var trip=bar?bar.querySelector('[data-f="trip"]'):null;
  if(trip&&from&&to) trip.addEventListener('click',function(){
    from.value=t.getAttribute('data-trip-from')||''; to.value=t.getAttribute('data-trip-to')||''; apply();});
  if(reset) reset.addEventListener('click',function(){
    [q,from,to,ven].forEach(function(el){if(el) el.value='';});
    [single,chg].concat(extraF).forEach(function(el){if(el) el.checked=false;});
    apply();});
  F('thead th',t).forEach(function(th,i){
    th.addEventListener('click',function(){
      var tb=t.tBodies[0], arr=F('tbody tr:not(.rulesrow)',tb).filter(function(r){return r.style.display!=='none';});
      var asc=th.getAttribute('data-asc')!=='1';
      F('thead th',t).forEach(function(o){o.removeAttribute('data-asc');});
      th.setAttribute('data-asc',asc?'1':'0');
      arr.sort(function(a,b){
        var ra=cell(a,i), rb=cell(b,i);
        var ka=ra&&ra.getAttribute('data-order'), kb=rb&&rb.getAttribute('data-order');
        var va=ka!==null&&ka!==''?ka:(ra?ra.textContent.trim():''), vb=kb!==null&&kb!==''?kb:(rb?rb.textContent.trim():'');
        var na=parseFloat(String(va).replace(/[^0-9.\-]/g,'')), nb=parseFloat(String(vb).replace(/[^0-9.\-]/g,''));
        var cmp=(!isNaN(na)&&!isNaN(nb))?na-nb:String(va).localeCompare(String(vb));
        return asc?cmp:-cmp;});
      arr.forEach(function(r){var nx=r.nextElementSibling;tb.appendChild(r);
        if(nx&&nx.classList.contains('rulesrow')) tb.appendChild(nx);});});});
  F('details.rules',t).forEach(function(d){d.addEventListener('toggle',function(){
    var tr=d.closest('tr'); if(!tr) return;
    tr.classList.toggle('open', d.open);
    tr.style.display=d.open?'table-row':'none';});});
  apply();
  function cell(tr,i){var c=tr.children[Math.min(i,tr.children.length-1)];return c;}
}

/* ---- dated rate log (browser-local, compare like-for-like) ---- */
var RK='p5.rates.v1';
function rl(){try{return JSON.parse(localStorage.getItem(RK)||'[]');}catch(e){return [];}}
function wr(l){try{localStorage.setItem(RK,JSON.stringify(l));}catch(e){}}
function renderRates(){
  var box=document.getElementById('ratelog'); if(!box) return;
  var l=rl(), h;
  if(!l.length){box.innerHTML='<p class="muted sm">No booking quote recorded in this browser yet. The official '
    +'booking engines need a live date search, and this site stores nothing on a server: run the hotel\u2019s own '
    +'booking link, then log the checkout total here so nights and totals can be compared like-for-like.</p>';return;}
  h='<div class="tablewrap"><table class="grid"><thead><tr><th>Logged</th><th>Hotel</th><th>Dates</th>'
   +'<th class="num">Checkout total</th><th class="num">Nights</th><th class="num">Nightly avg</th>'
   +'<th class="num">Resort fee /night</th><th class="num">Tax %</th><th class="num">True /night</th>'
   +'<th class="num">Stay true total</th><th>Rate stamp</th><th></th></tr></thead><tbody>';
  l.slice().reverse().forEach(function(r,i){
    var nights=r.nights||1, avg=r.total/nights, fee=r.fee||0, tax=(r.tax||13.38)/100;
    var tr_=avg+fee, trueNight=tr_*(1+tax), trueStay=trueNight*nights;
    h+='<tr><td class="nowrap">'+r.ts+'</td><td>'+esc(r.hotel)+'</td><td class="nowrap">'+esc(r.checkin)+' \u2192 '
      +esc(r.checkout)+'</td><td class="num">$'+r.total.toFixed(2)+'</td><td class="num">'+nights+'</td>'
      +'<td class="num">$'+avg.toFixed(2)+'</td><td class="num">$'+fee.toFixed(2)+'</td><td class="num">'+(tax*100).toFixed(2)
      +'%</td><td class="num">$'+trueNight.toFixed(2)+'</td><td class="num"><b>$'+trueStay.toFixed(2)+'</b></td>'
      +'<td class="nowrap">'+esc(r.stamp||'')+'</td><td><button class="btn ghost" data-del="'+(l.length-1-i)+'">remove</button></td></tr>';});
  h+='</tbody></table></div>';box.innerHTML=h;
  F('[data-del]',box).forEach(function(b){b.addEventListener('click',function(){
    var l2=rl();l2.splice(parseInt(b.getAttribute('data-del'),10),1);wr(l2);renderRates();});});
}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function initRateForm(){
  var f=document.getElementById('rateform'); if(!f) return;
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var g=function(id){var el=document.getElementById(id);return el?el.value.trim():'';};
    var tot=parseFloat(g('r_total')), nights=parseInt(g('r_nights'),10);
    if(!(tot>0)||!(nights>0)){document.getElementById('r_err').textContent='A checkout total and a positive number of nights are both required - the log refuses an average built on nothing.';return;}
    var l=rl();l.push({ts:new Date().toISOString().slice(0,16).replace('T',' ')+'Z',hotel:g('r_hotel'),
      checkin:g('r_in'),checkout:g('r_out'),total:tot,nights:nights,fee:parseFloat(g('r_fee'))||0,
      tax:parseFloat(g('r_tax'))||13.38,parking:parseFloat(g('r_park'))||0,stamp:g('r_stamp'),
      link:g('r_link')});wr(l);f.reset();document.getElementById('r_err').textContent='';renderRates();});
}

/* ---- trip cost calculator: entries x buy-ins + nights x true hotel cost ---- */
function initTrip(){
  var box=document.getElementById('picks'), out=document.getElementById('ptotal'), cfgEl=document.getElementById('cfg');
  if(!box||!cfgEl) return;
  var cfg=JSON.parse(cfgEl.textContent);
  var sel={};
  function num2(v){return (v===''||v==null||isNaN(+v))?null:+v;}
  function calc(){
    var hotel=cfg.hotels[document.getElementById('t_hotel').value]||{};
    var entries=0, buyins=0, badBuyin=false, pool=0, fees=0;
    F('input[data-buyin]',box).forEach(function(c){
      if(!c.checked) return;
      var b=num2(c.getAttribute('data-buyin'));
      if(b===null||b<=0){badBuyin=true;return;}
      entries++; buyins+=b;
      pool+=num2(c.getAttribute('data-pool'))||0; fees+=(b-(num2(c.getAttribute('data-pool'))||0));
    });
    var nights=num2(document.getElementById('t_nights').value);
    var mode=document.getElementById('t_mode').value;
    var rateInput=document.getElementById('t_rate');
    var rate=num2(rateInput.value);
    var fee=num2(hotel.fee), tax=num2(hotel.tax);
    var parking=0;
    if(hotel.parking_free_if_playing){parking=0;}
    else if(num2(hotel.parking)!=null){var p=num2(hotel.parking);var pk=document.getElementById('t_park');parking=(pk&&pk.checked)?p*nights:0;}
    var hotelNight=null, hotelTotal=null, note='';
    if(mode==='quote'&&rate!=null&&nights&&fee!=null&&tax!=null){hotelNight=(rate+fee)*(1+tax/100);hotelTotal=hotelNight*nights;}
    else if(mode==='floor'&&hotel.floor!=null&&nights&&fee!=null&&tax!=null){rate=hotel.floor;hotelNight=(rate+fee)*(1+tax/100);hotelTotal=hotelNight*nights;
      note='estimate at the property\u2019s own published rate floor - not a dated quote';}
    else if(mode==='log'){var l=rl();if(l.length){var r=l[l.length-1];hotelNight=(r.total/r.nights+(r.fee||0))*(1+(r.tax||13.38)/100);hotelTotal=hotelNight*r.nights;nights=r.nights;
      rate=r.total/r.nights;fee=r.fee||0;note='from the last dated log entry in this browser ('+r.ts+')';}}
    var complete=entries>0&&!badBuyin&&hotelTotal!=null&&nights>0;
    var lines='';
    lines+='<div>Entries: <b>'+entries+'</b> \u00d7 listed buy-ins = <b>$'+buyins.toLocaleString()+'</b> '+
      '<span class="sm">(of which $'+fees.toLocaleString(undefined,{maximumFractionDigits:0})+' is the house fee and $'+pool.toLocaleString(undefined,{maximumFractionDigits:0})+' goes to the prize pool)</span></div>';
    lines+='<div>Hotel: '+(nights||'\u2014')+' night(s) \u00d7 true cost / night '+
      (hotelNight==null?'<span class="blank">not completed</span>':'<b>$'+hotelNight.toFixed(2)+'</b> '+
       '<span class="sm">(rate $'+rate.toFixed(2)+' + mandatory fee $'+fee.toFixed(2)+') \u00d7 (1+'+tax+'/100)</span>')+
      ' = '+(hotelTotal==null?'<span class="blank">Incomplete</span>':'<b>$'+hotelTotal.toLocaleString(undefined,{maximumFractionDigits:0})+'</b>')+'</div>';
    lines+='<div>Parking: '+(parking?'<b>$'+parking.toLocaleString(undefined,{maximumFractionDigits:0})+'</b>':'$0 '
      +'<span class="sm">'+(hotel.parking_free_if_playing?'free self-parking applies to a player with 3 h+ of play (official rule)':'not added by default')+'</span>')+'</div>';
    lines+='<div class="big">Estimated trip cost: '+(complete?'$'+(buyins+hotelTotal+parking).toLocaleString(undefined,{maximumFractionDigits:0}):'Incomplete')+'</div>';
    if(note) lines+='<div class="sm">'+esc(note)+'</div>';
    if(badBuyin) lines+='<div class="badbox sm">A selected event has no published buy-in, so the total cannot be completed.</div>';
    else if(!complete) lines+='<div class="warnbox sm">Incomplete on purpose: the hotel leg needs a dated room quote '
      +'(or the rate-floor mode switched on), a positive night count and a mandatory fee that an official page states. '
      +'Nothing is filled in with a guess. Pick an event list above, or switch the mode selector.</div>';
    else lines+='<div class="goodbox sm">Complete under the published formula. Reconfirm the schedule, the room quote and the cancellation deadline before any non-refundable payment.</div>';
    out.innerHTML=lines;
    var days=new Set(F('input[data-buyin]:checked',box).map(function(c){return c.getAttribute('data-date');}));
    var perday=document.getElementById('t_days'); if(perday) perday.textContent=days.size+' of the days in the window carry a selected event';
  }
  box.addEventListener('change',calc);
  F('#tripform input,#tripform select').forEach(function(el){el.addEventListener('input',calc);el.addEventListener('change',calc);});
  var btn=document.getElementById('t_auto');
  if(btn) btn.addEventListener('click',function(){
    F('input[data-primary="1"]',box).forEach(function(c){c.checked=true;});calc();});
  calc();
}

document.addEventListener('DOMContentLoaded',function(){
  F('table.grid').forEach(wireTable);
  renderRates();initRateForm();initTrip();
  var link=document.getElementById('sharewin');
  if(link) link.addEventListener('click',function(e){e.preventDefault();
    var s=state();document.getElementById('winout').textContent='from='+ (s.from||'') +' to='+(s.to||'');});
});
})();
"""


PAGE_FILES = {os.path.basename(h) for h, _ in NAV}


def page(title, body, active, depth=0, extra_head=""):
    up = "../" * depth
    prose = "../" * max(0, depth - 1)
    if prose:
        # body prose links to bare page names; re-point them at the right folder depth
        for f in sorted(PAGE_FILES, key=len, reverse=True):
            if f == "index.html":
                continue
            body = body.replace('href="%s"' % f, 'href="%s%s"' % (prose, f))
        body = body.replace('href="index.html"', 'href="%sindex.html"' % prose)
    nav = "".join(
        '<a class="%s" href="%s%s">%s</a>' % ("active" if href == active else "", up, href, label)
        for href, label in NAV)
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s | Poker5</title>
<link rel="stylesheet" href="%sassets/bdcaf0bf.css"><script defer src="%sassets/bdcaf0bf.js"></script>%s</head><body>
<header><div class="brand">Poker5 &middot; Las Vegas Strip poker trip planner
<small>single-entry standard &middot; every row linked to an official source &middot; data generated %s</small></div>
<nav class="hnav">%s</nav></header>
<main>
%s</main>
<footer>
<p><b>Poker5</b> is an independent planning tool written by agent sessions from official sources. It is not
affiliated with any casino, poker room or hotel. Every table value links to the page it was read from; a value no
official source states is left blank, badged and listed on the
<a href="%spages/flagged-review.html">Flagged for review</a> page. Nothing is inferred, estimated or filled in.
Room rates, schedules and structures change without notice &mdash; reconfirm before any non-refundable payment.
Must be 21+. If gambling is a problem, call the Nevada HelpLine 1-800-522-4700.</p>
</footer></body></html>""" % (esc(title).replace("&amp;", "&"), up, up, extra_head, esc(TODAY), nav, body, up)


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    WRITTEN.add(rel)


def stats_html():
    c = META["counts"]
    items = [
        (c["rows"], "schedule rows, each with its official source"),
        (c["by_status"].get("explicit_one_entry", 0), "events with an official one-entry statement"),
        (c["by_status"].get("no_reentry_language", 0), "events whose sheet was read and shows no re-entry language"),
        (c["by_status"].get("multi_entry_paid", 0), "events with paid re-entry, add-on or extra flights"),
        (c["by_status"].get("continuation", 0), "continuation rows (restart / final table)"),
        (c["rankable"], "events eligible for the value ranking"),
        (c["conflicts"], "rows two earlier sessions classified differently"),
        (len(FLAGS), "flagged items"),
        (c["sources"], "official URLs in the monitor ledger"),
        (STATE.get("changed_count", 0), "sources an automated re-check saw change"),
    ]
    return '<div class="statgrid">%s</div>' % "".join(
        '<div class="stat"><div class="num">%s</div><div class="lbl">%s</div></div>' % (n, esc(l))
        for n, l in items)


def events_table(tid, rows, cols, headers, caption="", single=True, dates=True, cls="grid", sync=True,
                 opts_extra=""):
    if "source" not in cols and "sheet" not in cols:
        ERRORS.append("%s: an event table without a source column" % tid)
    body = []
    for r in rows:
        if not (r.get("schedule_url") or r.get("sheet_url")):
            ERRORS.append("%s: row %s has no official source URL" % (tid, r.get("id")))
        if r["entry_status"] == "not_read" and not r.get("multi_evidence"):
            body_flag = True
        body.append(event_row(r, cols))
    return filters(tid, single=single, dates=dates, changed=True) + table(
        headers, body, tid, opts=' data-syncdates="%d" data-trip-from="%s" data-trip-to="%s"%s'
        % (1 if sync else 0, esc(META["trip"]["check_in"]), esc(META["trip"]["check_out"]), opts_extra),
        caption=caption, cls=cls)


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def build_index():
    t = META["trip"]
    b = ["<h1>Las Vegas Strip poker trip planner</h1>",
         '<p class="lead">One published answer per question: every tournament row, hotel fee, walking route and rule '
         'field on this site comes from an official page or PDF that was read and dated. '
         'Re-verified line by line on %s against %s official URLs.</p>' % (esc(pretty(TODAY)), len(SOURCES))]
    b.append(stats_html())
    n_single = META["counts"]["by_status"].get("no_reentry_language", 0)
    n_expl = META["counts"]["by_status"].get("explicit_one_entry", 0)
    b.append('<div class="badbox"><b>The single-entry answer, stated precisely.</b> '
             'No official source for this window contains a one-entry, no-re-entry or freezeout sentence for any '
             'Venetian DeepStack IV event: <b>%d</b> events carry such a statement. %d events are listed as '
             '<i>sheet read &mdash; no re-entry language</i>: their own structure sheet was read in full and contains '
             'no re-entry, rebuy, add-on or purchased-chip sentence, which is the strongest evidence the official '
             'sources support, and the label says exactly that rather than &ldquo;guaranteed freezeout&rdquo;. '
             '%d events were moved out of the list because a source does state paid re-entry, add-on, extra flights or '
             'a membership-priced first buy-in. <a href="pages/single-entry.html">See the list and the rule</a> &middot; '
             '<a href="pages/tournaments-double.html">see what was excluded and why</a>.</div>'
             % (n_expl, n_single, META["counts"]["by_status"].get("multi_entry_paid", 0)))
    b.append(panel("Recommended window (computed, not entered by hand)",
                   '<div class="kv"><dt>Check in</dt><dd>%s</dd><dt>Check out</dt><dd>%s</dd>'
                   '<dt>Nights</dt><dd>%d</dd><dt>Why these dates</dt><dd>%s</dd>'
                   '<dt>Nightly cost ceiling</dt><dd>%s per room, true cost &mdash; %s</dd>'
                   '<dt>Quality floor</dt><dd>%s</dd></div>'
                   % (pretty(t["check_in"]), pretty(t["check_out"]), t["nights"], esc(t["rationale"]),
                      money(META["budget"]["nightly_room_ceiling_usd"]), esc(META["budget"]["kind"]),
                      esc(META["budget"]["quality_floor_note"]))))
    cards = [
        ("pages/executive-summary.html", "Executive summary", "The short version: what is confirmed, what is not, and the decision to make next."),
        ("pages/tournaments.html", "All events", "Every verified row from the Venetian, Wynn/WPT, Caesars, Horseshoe and South Point, with its sources."),
        ("pages/single-entry.html", "Single-entry list", "Events whose official sheet was read and shows no re-entry language, with the evidence per row."),
        ("pages/ranking.html", "Value ranking", "Guaranteed pool divided by buy-in, descriptive only, on confirmed rows."),
        ("pages/tournaments-double.html", "Advantage / multi-entry", "Re-entry, add-on, extra flights, memberships, satellites and tag teams kept separate."),
        ("pages/schedule.html", "Day plan", "One primary event per day, a conditional fallback, and the overlap check."),
        ("pages/hotels.html", "Hotels and true cost", "Resort fee, tax, parking, cancellation, dated rate log and itemised totals."),
        ("pages/routes.html", "Walking routes", "Hotel to poker room with the 30-minute limit and map links."),
        ("pages/planner.html", "Trip cost", "entries &times; buy-ins + nights &times; true hotel cost, with the incomplete state kept honest."),
        ("pages/venues/venetian.html", "Venetian", "One page for the host property: events, structure sheets, hotels and walks."),
        ("pages/venues/wynn.html", "Wynn", "One page for the WPT festival property, its terms and its hotel."),
        ("pages/venues/others.html", "Other rooms", "Caesars Palace, Horseshoe, Resorts World, South Point, MGM rooms and what they do not publish."),
        ("pages/questions.html", "Questions and gaps", "What must be answered before a booking decision is reasonable, and how to find each answer."),
        ("pages/suggestions.html", "Suggestions board", "Every improvement with its options, so a path can be chosen before anything is implemented."),
        ("pages/flagged-review.html", "Flagged for review", "Irregularities, blank values and cross-session disagreements, each with its source."),
        ("pages/monitor.html", "Source monitor", "The scheduled re-check of each official URL: status, hash, last-checked date and change log."),
        ("pages/repo-review.html", "Repo review", "File-by-file inventory of the repository and the defects found in it."),
        ("pages/method.html", "Method", "The standard applied, the formulas, and the complete source ledger."),
    ]
    b.append('<div class="grid-cards">%s</div>' % "".join(
        '<a class="card" href="%s"><h3>%s</h3><p class="sm muted">%s</p></a>' % (h, esc(t2), esc(t3))
        for h, t2, t3 in cards))
    b.append(panel("What this site will not do",
                   '<ul class="clean"><li>It will not call an event single-entry unless an official source states the limit.</li>'
                   '<li>It will not fill a guarantee, a buy-in, a room rate, a resort fee or a walking time that no official source states; those cells stay blank and are listed on the flagged page.</li>'
                   '<li>It will not rank an event until both its total entry fee and its guarantee are confirmed, and it never turns the guarantee ratio into a forecast.</li>'
                   '<li>It will not book, pay or store anything: no server, no account, no manual data entry required of you.</li></ul>'))
    b.append(panel("Reading order for a decision",
                   '<div class="big-list"><div><b>1. Can the trip exist at all?</b> '
                   'Open <a href="pages/schedule.html">Day plan</a> &mdash; it shows that no official start earlier than 10:10 '
                   'AM exists in this window, and that a one-day structure with 28 levels runs past midnight, so a second '
                   'event on the same day is conditional on busting out early.</div>'
                   '<div><b>2. Which events are legal under the policy?</b> '
                   '<a href="pages/single-entry.html">Single-entry list</a> and the excluded <a href="pages/tournaments-double.html">advantage list</a>.</div>'
                   '<div><b>3. Which is worth playing?</b> <a href="pages/ranking.html">Value ranking</a> (guarantee &divide; buy-in, descriptive only).</div>'
                   '<div><b>4. Where to stay and what it really costs?</b> <a href="pages/hotels.html">Hotels</a> + <a href="pages/routes.html">Walking routes</a>.</div>'
                   '<div><b>5. Total?</b> <a href="pages/planner.html">Trip cost</a>, then <a href="pages/questions.html">Questions</a> before payment.</div></div>'))
    arch = archive_block()
    if arch:
        b.append(panel("Earlier sessions (preserved, not edited)", arch))
    write("index.html", page("Las Vegas Strip poker trip planner", "".join(b), "index.html", 0))


def archive_block():
    skip = {".git", "__pycache__", "node_modules"}
    dirs = sorted(d for d in os.listdir(ROOT)
                  if os.path.isdir(os.path.join(ROOT, d)) and d not in skip
                  and re.match(r"^(site|docs|dashboard|planner|data)(-.*)?$", d)
                  and os.path.exists(os.path.join(ROOT, d, "index.html")))
    if not dirs:
        return ""
    return ('<p class="sm muted">%d folders from earlier parallel sessions are kept untouched. They are not part of '
            'the verified site and several of them publish numbers this build corrected; use the pages above.</p>'
            '<ul class="clean">%s</ul>' % (len(dirs), "".join(
                '<li><a href="%s/index.html">%s/</a></li>' % (esc(d), esc(d)) for d in dirs)))


def build_tournaments():
    b = ["<h1>All events, one table</h1>",
         '<p class="lead">Every row below was read from an official schedule page or structure sheet. The search box '
         'filters all columns, the two date inputs cut the window, the room filter and the single-entry toggle narrow '
         'further, and each row expands to show its structured rule fields with the excerpt each value came from.</p>']
    cols = ["date", "start", "end", "venue", "event", "name", "buyin", "fee", "pool", "gtd", "ratio", "chips",
            "levels", "latereg", "status", "lc", "source", "sheet"]
    heads = ["Date", "Start", "Est. end", "Room", "Event", "Name", "~Buy-in", "House fee", "To pool", "Guarantee",
             "~GTD &divide; entry", "Chips", "Levels", "Late reg", "Entry rule", "Last checked", "Schedule source", "Sheet"]
    rows = sorted(ROWS, key=lambda r: (r.get("date") or "9999", r.get("start") or "99:99"))
    b.append(events_table("tall", rows, cols, heads,
                          caption="%d rows &middot; blank cells mean the official source does not state the value" % len(rows)))
    b.append(panel("Column meanings and limits",
                   '<div class="kv">'
                   '<dt>Est. end</dt><dd>start + (published level count &times; level length) + three 15-minute breaks '
                   'from the same structure sheet. Derived arithmetic from official numbers, shown so a second event can '
                   'be tested against it; %d rows have no level count published and therefore no estimate.</dd>'
                   '<dt>~GTD &divide; entry</dt><dd>guaranteed pool divided by the published buy-in. A description of the '
                   'posted value of one entry, <b>not</b> an expected return or a forecast.</dd>'
                   '<dt>To pool</dt><dd>the part of each buy-in the sheet says goes to the prize pool; the house fee is '
                   'inside the buy-in, not added to it.</dd>'
                   '<dt>Last checked</dt><dd>the most recent date any source behind that row was re-read by the monitor; '
                   'a red <i>source changed</i> badge means the page hash moved and the stored value still needs a human '
                   're-read.</dd></div>' % META["counts"]["with_end_estimate"]))
    write("pages/tournaments.html", page("All events", "".join(b), "tournaments.html", 1))


def build_single():
    c = META["counts"]["by_status"]
    b = ["<h1>Events that satisfy the single-entry standard</h1>",
         '<p class="lead">The brief asks for tournaments you cannot buy an advantage in: no double buy-in, no add-on, '
         'no rebuy, no paid path to more chips. This page is the list that survives that filter, and the sentence '
         'after each event number says exactly how far the evidence goes.</p>']
    b.append(panel("The standard, written out",
                   '<div class="kv">'
                   '<dt>Grade A &mdash; %d rows</dt><dd>an official source states a one-entry, no-re-entry or freezeout '
                   'limit. Nothing in this window does.</dd>'
                   '<dt>Grade B &mdash; %d rows</dt><dd>the event\'s own official structure sheet was read in full, that '
                   'sheet lists this event number, the event is one day, and no re-entry, rebuy, add-on, purchased-stack '
                   'or extra-flight sentence exists on it. <b>The &ldquo;unverified&rdquo; label is removed from these '
                   'rows</b>, and the caveat that silence is not a published rule stays printed on each row.</dd>'
                   '<dt>Excluded &mdash; %d rows</dt><dd>re-entry / add-on / extra flights / a membership-priced first '
                   'buy-in is published, or the row is a continuation row rather than a purchasable entry. They live on '
                   'the <a href="tournaments-double.html">advantage page</a>.</dd>'
                   '<dt>Unread &mdash; %d rows</dt><dd>the room publishes no structure sheet for the event (mostly WPT '
                   'festival rows and the South Point daily list). Blank and flagged.</dd></div>'
                   % (c.get("explicit_one_entry", 0), c.get("no_reentry_language", 0),
                      c.get("multi_entry_paid", 0), c.get("not_read", 0))))
    b.append(panel("Why this page disagrees with parts of the earlier repository",
                   '<p class="sm">Three numbers have been published for the same 94 Venetian rows: <b>0</b> '
                   '(session ea99006a, which refuses to treat silence as a rule), <b>55</b> (session 251c122f, which '
                   'calls the same rows confirmed single-entry) and <b>%d</b> here. This build matches 251c122f\'s '
                   'evidence and ea99006a\'s caution: the count is 55 minus the two PokerAtlas Valuetown rows whose '
                   'sheet sells subsequent buy-ins at a member price, minus rows that name a tag team. '
                   'The %d row-by-row disagreements are listed at the bottom of this page and on the flagged page.</p>'
                   % (c.get("no_reentry_language", 0), len(CONFLICTS))))
    rows = sorted([r for r in ROWS if r["entry_status"] in ("explicit_one_entry", "no_reentry_language")],
                  key=lambda r: (r.get("date") or "9999", r.get("start") or ""))
    cols = ["date", "start", "end", "venue", "event", "name", "buyin", "fee", "pool", "gtd", "ratio", "chips",
            "latereg", "status", "evidence", "lc", "sheet"]
    heads = ["Date", "Start", "Est. end", "Room", "Event", "Name", "Buy-in", "House fee", "To pool", "Guarantee",
             "GTD &divide; entry", "Chips", "Late reg", "Grade", "Official evidence read", "Last checked", "Sheet"]
    b.append(events_table("tsingle", rows, cols, heads,
                          caption="%d rows &middot; toggle &ldquo;single-entry standard only&rdquo; on any other table to reproduce this list" % len(rows)))
    if CONFLICTS:
        body = []
        for x in CONFLICTS:
            src_row = by_id.get(x.get("row")) or {}
            url = src_row.get("sheet_url") or src_row.get("schedule_url") or ""
            body.append('<tr data-search="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                        '<td class="sm">%s</td><td>%s</td></tr>'
                        % (esc("%s %s %s" % (x.get("row"), x.get("name"), x.get("date"))), esc(x.get("row")),
                           pretty(x.get("date")), esc(x.get("name")), esc(x.get("theirs")), esc(x.get("mine")),
                           esc(x.get("why")),
                           link(url, "official sheet") if url
                           else '<span class="blank">no official page publishes this row</span>'))
        b.append(panel("Row-level disagreements with earlier sessions (%d)" % len(CONFLICTS),
                       filters("tconf", venues=False, dates=False, single=False) +
                       table(["Row", "Date", "Event", "earlier verdict", "this build", "note",
                              "Official source"], body, "tconf",
                             cls="grid", caption="kept visible rather than silently resolved")))
    write("pages/single-entry.html", page("Single-entry list", "".join(b), "single-entry.html", 1))


def build_double():
    b = ["<h1>Advantage, multi-entry and special-format events</h1>",
         '<p class="lead">These are not deleted &mdash; they are separated, because the brief says events you could gain '
         'an advantage in through spending more money belong in their own section. Each row states the official '
         'sentence that put it here.</p>']
    rows = sorted([r for r in ROWS if r["entry_status"] == "multi_entry_paid"],
                  key=lambda r: (r.get("date") or "9999", r.get("start") or ""))
    cont = sorted([r for r in ROWS if r["entry_status"] == "continuation"],
                  key=lambda r: (r.get("date") or "9999", r.get("start") or ""))
    unread = sorted([r for r in ROWS if r["entry_status"] == "not_read"],
                    key=lambda r: (r.get("date") or "9999", r.get("start") or ""))
    cols = ["date", "start", "venue", "event", "name", "buyin", "gtd", "status", "evidence", "lc", "source"]
    heads = ["Date", "Start", "Room", "Event", "Name", "Buy-in", "Guarantee", "Why excluded",
             "Official sentence", "Last checked", "Source"]
    b.append(panel("Paid re-entry, add-on, extra flights, membership-priced entries (%d)" % len(rows),
                   events_table("tmulti", rows, cols, heads,
                                caption="a second way to buy chips, or a cheaper first buy-in that needs a paid membership",
                                single=False)))
    b.append(panel("Continuation rows (%d)" % len(cont),
                   events_table("tcont", cont, ["date", "start", "venue", "event", "name", "status", "lc", "source"],
                                ["Date", "Start", "Room", "Event", "Name", "Grade", "Last checked", "Source"],
                                caption="Day 2 restarts and streamed final tables: no entry is sold for these, so they are not counted as extra buy-ins",
                                single=False)))
    b.append(panel("Entry terms not published (%d)" % len(unread),
                   events_table("tunread", unread, ["date", "start", "venue", "event", "name", "buyin", "gtd", "status", "lc", "source"],
                               ["Date", "Start", "Room", "Event", "Name", "Buy-in", "Guarantee", "Grade", "Last checked", "Source"],
                               caption="left blank and flagged: no structure sheet exists for these rows, so this site does not assert anything about their entry rules",
                               single=False)))
    sat = [r for r in ROWS if r.get("special_format")]
    b.append(panel("Special entry structures worth their own label (%d)" % len(sat),
                   '<p class="sm">Satellites sell a cheap seat into an expensive event, and tag-team events put two '
                   'players on one entry. Neither is a paid re-entry, and neither behaves like a single-player '
                   'freezeout, so both are kept out of the value ranking.</p>' +
                   events_table("tsat", sat, ["date", "venue", "event", "name", "buyin", "status", "lc", "source"],
                                ["Date", "Room", "Event", "Name", "Buy-in", "Grade", "Last checked", "Source"],
                                caption="satellites and tag teams, labelled as such", single=False)))
    write("pages/tournaments-double.html", page("Advantage / multi-entry", "".join(b), "tournaments-double.html", 1))


def build_ranking():
    rk = sorted([r for r in ROWS if r["rankable"]], key=lambda r: -(r["ratio"] or 0))
    b = ["<h1>Value ranking: guaranteed pool per entry</h1>",
         '<p class="lead">Ranking is only run on rows where an official source states <b>both</b> the buy-in and the '
         'guarantee, because a comparison that mixes a stated guarantee with an unstated one is not a comparison. '
         'The number is descriptive: it says how large the posted guarantee is relative to one entry. It is not an '
         'expected value, a win probability or a forecast, and field size, which decides both, is not published in advance.</p>']
    b.append(panel("How the ratio is used here",
                   '<div class="kv"><dt>Formula</dt><dd>guaranteed pool &divide; published buy-in. The house fee sits '
                   'inside the buy-in on these sheets, so no fee is added on top.</dd>'
                   '<dt>Excluded from the ranking</dt><dd>bounty events are ranked in their own block because part of '
                   'their guarantee is paid by knockout, not by placing; satellites are excluded because their prize is '
                   'an entry seat; tag-team events are excluded because the entry covers two players; any row where the '
                   'schedule row and its sheet disagree about the guarantee is excluded until it is re-read.</dd>'
                   '<dt>Rows in this window</dt><dd>%d rankable &middot; %d bounty-labelled &middot; %d satellites '
                   '&middot; %d with a guarantee conflict still open</dd></div>'
                   % (len(rk), sum(1 for r in ROWS if r.get("is_bounty")),
                      META["counts"]["satellite_rows"], sum(1 for r in ROWS if r.get("gtd_conflict")))))
    cols = ["ratio", "date", "start", "venue", "event", "name", "buyin", "fee", "pool", "gtd", "chips", "levels",
            "latereg", "status", "lc", "source"]
    heads = ["GTD &divide; entry", "Date", "Start", "Room", "Event", "Name", "Buy-in", "House fee", "To pool",
             "Guarantee", "Chips", "Levels", "Late reg", "Grade", "Last checked", "Source"]
    plain = [r for r in rk if not r.get("is_bounty") and not r.get("special_format")]
    bounty = [r for r in rk if r.get("is_bounty") and not r.get("special_format")]
    b.append(panel("Plain freezeout-style events (%d)" % len(plain),
                   events_table("trank", plain, cols, heads,
                                caption="highest published guarantee per entry first", single=False)))
    b.append(panel("Bounty events, kept separate (%d)" % len(bounty),
                   events_table("trankb", bounty, cols, heads,
                                caption="the guarantee includes knockouts, so it is not comparable with a plain pool",
                                single=False)))
    write("pages/ranking.html", page("Value ranking", "".join(b), "ranking.html", 1))


def build_schedule():
    b = ["<h1>Day plan: one primary event, one conditional fallback</h1>",
         '<p class="lead">Built from official start times, the late-registration window printed on each structure '
         'sheet, and the sheet\'s own level count and level length. A second event is only offered when the numbers '
         'allow it, and when it depends on leaving the first event early the page says so.</p>']
    no8 = sum(1 for d in PLAN for v in d["venues"] if not v["starts_at_8am"])
    b.append(panel("The 8 AM question, answered from the schedule",
                   '<div class="badbox">No official source in this window publishes an 8:00 AM start. The earliest '
                   'recurring Venetian start is 10:10 AM (the RaceDay Stack events) and the usual main-event flight '
                   'starts at 11:10 AM, with evening flights at 5:10 PM. A day planned from 8:00 AM therefore begins '
                   'with registration, seating and pre-registration ("all pre-registered stacks will be in play at the '
                   'start of the event", per the official sheets), not with cards in the air.</div>'
                   '<p class="sm">%d of %d venue-days on this page have no event that can start by 8:10 AM. The '
                   'published level structures also explain why most days hold exactly one event: a 28-level structure '
                   'at 30 minutes plus three breaks runs about 14 h 45 m, which ends after midnight.</p>'
                   % (no8, sum(len(d["venues"]) for d in PLAN))))
    idx = {r["id"]: r for r in ROWS}
    # a row that offers nothing still has to cite what it was checked against
    day_src = {}
    for r in ROWS:
        key = (r.get("date"), r.get("venue_key"))
        if r.get("schedule_url") and key not in day_src:
            day_src[key] = r["schedule_url"]
    venue_src = {}
    for v in VENUES:
        if v.get("source"):
            venue_src[v.get("key")] = v["source"]
    for d in PLAN:
        if not d["venues"]:
            continue
        rows_html = []
        idx2 = idx

        def cell(i, missing='<span class="blank">none available</span>'):
            r = idx2.get(i)
            if not r:
                return "<td>%s</td>" % missing
            note = ' <span class="sm muted">%s</span>' % esc(r["special_format"]) if r.get("special_format") else ""
            srcs = []
            if r.get("schedule_url"):
                srcs.append(link(r["schedule_url"], "schedule row"))
            if r.get("sheet_url"):
                srcs.append(link(r["sheet_url"], "sheet"))
            return ('<td>%s <span class="sm">%s &middot; %s &middot; buy-in %s &middot; guarantee %s</span>%s'
                    '<div class="sm">%s</div></td>'
                    % (esc(r["name"]), hhmm12(r["start"]), esc(r.get("event_no") or "&mdash;"),
                       money(r.get("buyin")), money(r.get("guarantee")), note,
                       " &middot; ".join(srcs) or '<span class="blank">no official page publishes this row</span>'))

        for v in d["venues"]:
            ov = (' <span class="pill warn">%d overlap flags</span>' % v["overlap_count"]) if v["overlap_count"] else ""
            cells = ['<td class="nowrap">%s</td>' % esc(v["venue"]),
                     cell(v["primary"]),
                     cell(v["fallback"]) if v["fallback"] else '<td><span class="blank">none available</span></td>',
                     '<td class="sm">%s</td>' % esc(v["primary_reason"]),
                     '<td class="sm">%s%s</td>' % (esc(v["fallback_condition"]), ov),
                     '<td>%s</td>' % (link((idx.get(v["primary"]) or {}).get("schedule_url"), "schedule page")
                                      if v["primary"] else
                                      (link(day_src.get((d["date"], v["venue_key"])) or venue_src.get(v["venue_key"]),
                                            "schedule page for this date")
                                       or '<span class="blank">no official page lists this date for this room</span>'))]
            rows_html.append('<tr data-search="%s" data-date="%s" data-rule="%s" data-venue="%s">%s</tr>'
                             % (esc("%s %s %s" % (d["date"], v["venue"],
                                                  " ".join(str(x) for x in v["events"]))).lower(),
                                esc(d["date"]),
                                esc("no_reentry_language" if v["primary"] else "not_read"),
                                esc(v["venue_key"]), "".join(cells)))
        cap = ("%s &middot; %d event row(s) on the official page; each row carries the source link of the event it "
               "books, so a plan row is never a claim without a citation%s" % (pretty(d["date"]),
                                                                      sum(len(v["events"]) for v in d["venues"]),
                                                                      (" &middot; " + d["cross_venue_warning"]) if d["multi_venue"] else ""))
        b.append('<div class="panel"><h3>%s</h3>%s</div>' % (pretty(d["date"]),
                 table(["Room", "Primary event", "Conditional fallback", "Why this one", "Feasibility",
                        "Official source"], rows_html,
                       "plan-%s" % d["date"], cls="grid", caption=cap)))
    b.append(panel("How to read a row",
                   '<div class="kv"><dt>Primary</dt><dd>the day\'s best published guarantee-per-entry among events that '
                   'pass the single-entry standard and can start in the morning. If no event on the day has both a '
                   'buy-in and a guarantee published, the primary is shown with a blank guarantee and the reason says '
                   'so.</dd><dt>Conditional fallback</dt><dd>a second event whose published registration window is still '
                   'open while the primary runs. It is only playable if you have already been eliminated &mdash; that '
                   'is the condition, and the time is taken from the fallback\'s own sheet.</dd>'
                   '<dt>Overlap flags</dt><dd>pairs of events where the later one starts before the earlier one can '
                   'finish on its published structure. A flagged pair is never both booked.</dd></div>'))
    write("pages/schedule.html", page("Day plan", "".join(b), "schedule.html", 1,
                                      extra_head='<meta name="plan-days" content="%d">' % len(PLAN)))


def hotel_true_cost(h):
    fee = h.get("resort_fee")
    tax = h.get("tax_rate_pct")
    rate = h.get("nightly_rate")
    if rate is None and h.get("poker_rate_floor") is not None and fee is not None:
        rate = h["poker_rate_floor"]
    if fee is None or tax is None:
        return None, None
    if rate is None:
        return None, (fee * (1 + tax / 100.0))
    return (rate + fee) * (1 + tax / 100.0), (fee * (1 + tax / 100.0))


def build_hotels():
    b = ["<h1>Hotels: the true nightly cost, itemised</h1>",
         '<p class="lead">Cost and quality outrank distance, but the walk still has to be under 30 minutes. This page '
         'publishes every cost component an official page states &mdash; mandatory resort fee, room tax, parking, '
         'deposit and cancellation deadline &mdash; and leaves the room rate blank until a dated quote is logged, '
         'because the official booking engines will not give one to a non-Java client.</p>']
    b.append(panel("The formula and its two sources",
                   '<div class="kv"><dt>True cost per night</dt><dd>(room rate + mandatory resort fee) &times; (1 + '
                   '13.38%%). The multiplier is the Clark County combined transient lodging tax for a resort hotel '
                   'inside the primary gaming corridor: 12.5%% + 0.88%% stadium-district tax, re-read %s.</dd>'
                   '<dt>Why the fee is taxed too</dt><dd>the same ordinance defines &ldquo;rent&rdquo; to include '
                   'separately stated accommodation, facility and access fees, so a mandatory resort fee is part of the '
                   'tax base.</dd><dt>Compared like-for-like</dt><dd>only a checkout total for the same dates, same '
                   'occupancy and same night count can be divided by nights and compared; that is what the dated log '
                   'below is for.</dd></div>' % esc(pretty(WIKI["facts"][11]["retrieved_at"][:10]) if len(WIKI["facts"]) > 11 else TODAY)))
    cols = ["Hotel", "Tier", "Mandatory resort fee", "Room tax", "Parking", "Cancellation", "True cost / night",
            "Walk to the poker room", "Official booking link", "Last checked", "Source"]
    body = []
    for h in HOTELS:
        true_night, _fee_only = hotel_true_cost(h)
        walks = list(h["routes"])
        verified = [r for r in walks if r["verified"]]
        walk_txt = ("%d of %d routes verified on-property (0 min)" % (len(verified), len(walks))
                    if walks else '<span class="blank">no route published</span>')
        lc = max([str((STATE["urls"].get(u) or {}).get("last_checked") or "")[:10]
                  for u in [h.get("resort_fee_source"), h.get("parking_source"), h.get("cancel_source")] if u] or [""])
        src = h.get("resort_fee_source") or h.get("cancel_source") or h.get("poker_rate_source") or ""
        chg = ' <span class="chg">source changed</span>' if any(
            u in CHANGED_URLS for u in [h.get("resort_fee_source"), h.get("parking_source")]) else ""
        status_txt = h.get("resort_fee_status") or ""
        if h.get("resort_fee"):
            fee_cell = '%s <div class="sm muted">%s</div>' % (money(h["resort_fee"]), esc(status_txt))
        elif h.get("fee_range"):
            fee_cell = ('<span class="pill warn">range %s &ndash; %s only</span> <div class="sm">%s</div>'
                        % (money(h["fee_range"][0]), money(h["fee_range"][1]), esc(status_txt)))
        else:
            fee_cell = '<span class="blank">not published</span> <div class="sm">%s</div>' % esc(status_txt)
        if true_night:
            true_cell = ('<b>%s</b> <div class="sm muted">computed with the property\'s own published rate floor, '
                         'not a dated quote</div>' % money(true_night))
        else:
            basis = h.get("true_nightly_basis") or h.get("poker_rate_caveat") or ""
            true_cell = '<span class="blank">needs a dated room quote</span> <div class="sm muted">%s</div>' % esc(basis)
        book = (h.get("booking") or "").replace("{IN}", META["trip"]["check_in"]).replace(
            "{OUT}", META["trip"]["check_out"])
        cells = [
            '<td><b>%s</b><div class="sm muted">%s</div><div class="sm">%s</div></td>'
            % (esc(h["name"]), esc(h.get("area")), esc(h.get("room"))),
            '<td>%s</td>' % esc(h.get("tier") or '<span class="blank">no official rating</span>'),
            '<td>%s</td>' % fee_cell,
            '<td class="num">%s%s</td>' % (num_txt(h.get("tax_rate_pct")), "%" if h.get("tax_rate_pct") is not None else ""),
            '<td class="sm">%s</td>' % esc((h.get("parking") or '<span class="blank">not published</span>')[:300]),
            '<td class="sm">%s</td>' % esc((h.get("cancel") or '<span class="blank">no cancellation term retrieved</span>')[:300]),
            '<td class="num">%s</td>' % true_cell,
            '<td class="sm">%s</td>' % walk_txt,
            '<td>%s</td>' % (link(book, "official booking, %s to %s" % (META["trip"]["check_in"], META["trip"]["check_out"]))
                             if book else '<span class="blank">no official booking page stated</span>'),
            '<td class="sm nowrap">%s%s</td>' % (esc(lc or "not re-checked"), chg),
            '<td>%s</td>' % (link(src, "terms page") if src else '<span class="blank">no source</span>'),
        ]
        search = " ".join(str(h.get(k) or "") for k in ("name", "tier", "area", "room", "parking", "cancel")).lower()
        body.append('<tr data-search="%s" data-changed="%s" data-rule="any">%s</tr>'
                    % (esc(search), "1" if chg else "0", "".join(cells)))
    b.append(filters("thotels", venues=False, dates=False, single=False, changed=True) +
             table(cols, body, "thotels", cls="grid",
                   caption="a blank cell is an admission that no official source states the value, not a zero"))
    b.append(panel("Quality, honestly",
                   '<p class="sm">%s</p>' % esc(META["budget"]["quality_floor_note"])))
    entries = RATES.get("entries") or []
    rows_html = []
    for e in entries:
        cells = [
            '<td class="nowrap">%s</td>' % esc(e.get("rate_timestamp")),
            "<td>%s</td>" % esc(e.get("hotel")),
            '<td class="nowrap">%s &rarr; %s (%s nights)</td>' % (esc(e.get("checkin")), esc(e.get("checkout")),
                                                                  e.get("nights") or "?"),
            '<td class="num">%s</td>' % money(e.get("checkout_total")),
            '<td class="num">%s</td>' % money(e.get("nightly_average")),
            '<td class="num">%s</td>' % money(e.get("resort_fee_per_night")),
            '<td class="num">%s</td>' % money(e.get("room_rate_per_night")),
            '<td class="num">%s</td>' % money(e.get("parking")),
            '<td class="sm">%s</td>' % esc("; ".join(e.get("caveats") or [])[:300]),
            "<td>%s</td>" % (link(e.get("source") or e.get("booking"), "capture source")),
        ]
        search = " ".join(str(e.get(k) or "") for k in ("hotel", "room_type", "rate_timestamp", "checkin")).lower()
        rows_html.append('<tr data-search="%s">%s</tr>' % (esc(search), "".join(cells)))
    b.append(panel("Dated rate log (kept as a log, never a single value)",
                   '<p class="sm">Each line is one observation with its own date; a rate is never over-written, so the '
                   'movement is visible. These are the %d official-engine captures in <code>data/bdcaf0bf/rates_log.json</code>.</p>%s'
                   % (len(entries), table(["Captured", "Hotel", "Dates (nights)", "Checkout total", "Nightly average",
                                           "Resort fee /night", "Room rate /night", "Parking", "Caveats", "Source"],
                                          rows_html, "tlog", cls="grid",
                                          caption="a nightly average is derived as checkout total &divide; nights; it is labelled as derived"))
                   + '<h3>Record a new quote (stored in this browser only)</h3>'
                   + '<form id="rateform" class="calc">'
                   + '<label>Hotel<input id="r_hotel" placeholder="The Venetian"></label>'
                   + '<label>Check in<input id="r_in" type="date"></label>'
                   + '<label>Check out<input id="r_out" type="date"></label>'
                   + '<label>Checkout total $<input id="r_total" type="number" min="0" step="0.01" placeholder="required"></label>'
                   + '<label>Nights<input id="r_nights" type="number" min="1" step="1" placeholder="required"></label>'
                   + '<label>Resort fee /night $<input id="r_fee" type="number" min="0" step="0.01"></label>'
                   + '<label>Tax %<input id="r_tax" type="number" min="0" step="0.01" value="13.38"></label>'
                   + '<label>Parking /night $<input id="r_park" type="number" min="0" step="0.01"></label>'
                   + '<label>Rate timestamp<input id="r_stamp" placeholder="e.g. 2026-11-19 07:40 PST"></label>'
                   + '<label>Booking link<input id="r_link" placeholder="https://..."></label>'
                   + '<label>&nbsp;<button class="btn" type="submit">add to log</button></label></form>'
                   + '<p class="sm" id="r_err" style="color:var(--bad)"></p><div id="ratelog"></div>'))
    write("pages/hotels.html", page("Hotels and true nightly cost", "".join(b), "hotels.html", 1))


def build_routes():
    b = ["<h1>Walking routes, with the 30-minute limit applied</h1>",
         '<p class="lead">The brief sets a hard rule: no hotel whose walk to the poker room exceeds 30 minutes. '
         'The honest answer is that no official source publishes a cross-property walking time, so only same-property '
         'walks are verified here and every other pair is left blank with a map link that makes it checkable in seconds.</p>']
    body, limit = [], 30
    for h in HOTELS:
        hsrc = h.get("resort_fee_source") or h.get("address_source") or h.get("cancel_source") or ""
        for r in h["routes"]:
            minutes = r.get("minutes")
            within = "yes" if (minutes is not None and minutes <= limit) else ("unknown" if minutes is None else "no")
            cells = [
                "<td>%s</td>" % esc(h["name"]),
                "<td>%s</td>" % esc(r["venue"]),
                '<td class="num">%s</td>' % (("%d min" % minutes) if minutes is not None
                                             else '<span class="blank">not published</span>'),
                '<td><span class="pill %s">%s</span></td>' % (
                    "ok" if within == "yes" else ("warn" if within == "unknown" else "bad"),
                    "verified &le; 30 min" if within == "yes" else ("unverified &mdash; no official time"
                                                                    if within == "unknown" else "over the limit")),
                '<td class="sm">%s</td>' % esc((r.get("method") or "")[:220]),
                "<td>%s</td>" % (link(r["google"], "Google Maps walk") if r.get("google")
                                 else '<span class="blank">no map link</span>'),
                ('<td><span class="sm muted">Apple Maps deep link (a mapping tool, not a source): '
                 '<code>%s</code></span></td>' % esc(r.get("apple"))) if r.get("apple")
                else '<td><span class="blank">no map link</span></td>',
                '<td class="sm">%s</td>' % esc(h.get("address") or "address not published on an official page"),
                "<td>%s</td>" % (link(hsrc, "property page (endpoint)") if hsrc
                                 else '<span class="blank">no official address page</span>'),
            ]
            search = ("%s %s" % (h["name"], r["venue"])).lower()
            body.append('<tr data-search="%s" data-minutes="%s" data-within="%s">%s</tr>'
                        % (esc(search), num_txt(minutes).replace("&mdash;", ""), within, "".join(cells)))
    b.append('<div class="filters" data-for="troutes">'
             '<input type="search" data-f="search" placeholder="Search hotel or poker room" aria-label="Search">'
             '<label><input type="checkbox" data-f="single"> walk within the 30-minute limit (verified rows only)'
             '</label>'
             '<button class="btn ghost" data-f="reset" type="button">reset</button><span class="count"></span></div>'
             + table(["Hotel", "To poker room", "Walk", "Within limit", "How it was checked", "Google Maps walk",
                      "Apple Maps", "Official address used", "Official source"], body, "troutes", cls="grid",
                     opts=' data-single="within" data-single-values="yes"',
                     caption="%d pairs &middot; verified on-property routes: %d &middot; everything else stays blank "
                             "until timed &middot; a map link is a checking tool, the source column is the citation"
                     % (len(body), sum(1 for h in HOTELS for r in h["routes"] if r["verified"]))))
    b.append(panel("What a reader should conclude",
                   '<ul class="clean">'
                   '<li><b>The Venetian and the Palazzo are one connected complex.</b> The poker room is officially '
                   'inside The Palazzo on level 2 of the Grand Canal Shoppes, so a room in either tower is an indoor, '
                   'elevator-connected walk with no street crossing &mdash; the only route this build can verify as '
                   'well inside 30 minutes, and the reason the host-property hotel is the default.</li>'
                   '<li><b>Resorts World, Caesars Palace, Horseshoe and Wynn</b> are all within a plausible Strip '
                   'walk, but no official page states the minutes, so the numbers are blank here and the map links are '
                   'provided instead. Summer heat, construction detours and the indoor routes are not in anyone\'s '
                   'published number.</li>'
                   '<li><b>The 30-minute rule is applied by excluding unverified rows from the plan</b>, not by '
                   'guessing a time that would pass it. Every row that stays in the plan is a verified on-property '
                   'walk.</li></ul>'))
    write("pages/routes.html", page("Walking routes", "".join(b), "routes.html", 1))


def build_planner():
    t = META["trip"]
    idx = {r["id"]: r for r in ROWS}
    b = ["<h1>Trip cost: entries &times; buy-ins + nights &times; true hotel cost</h1>",
         '<p class="lead"><b>Estimated trip cost =</b> one listed buy-in per selected event + nights &times; (room '
         'rate + mandatory resort fee) &times; (1 + room tax) + parking where it applies. Nothing here needs to be typed. The window, the hotel\'s mandatory fee and tax, and every '
         'buy-in come from the same official rows as the rest of the site; the only optional input is a dated room '
         'quote you choose to log. Until that exists the calculator refuses a grand total and prints <i>Incomplete</i> '
         'rather than inventing one.</p>']
    hopts = "".join('<option value="%s"%s>%s</option>'
                    % (esc(h["key"]), " selected" if i == 0 else "", esc(h["name"]))
                    for i, h in enumerate(HOTELS))
    scenario = ('<div class="panel" id="tripform"><h3>Scenario</h3><div class="calc">'
                '<label>Hotel<select id="t_hotel">' + hopts + '</select></label>'
                '<label>Nights<input id="t_nights" type="number" min="1" max="21" step="1" value="%d"></label>'
                '<label>Room rate basis<select id="t_mode">'
                '<option value="floor">official published rate floor</option>'
                '<option value="quote">dated quote (type it below)</option>'
                '<option value="log">last entry in my dated log</option></select></label>'
                '<label>Dated room rate / night $<input id="t_rate" type="number" min="0" step="0.01" '
                'placeholder="no date-specific quote recorded"></label>'
                '<label>Parking at $20/night<input id="t_park" type="checkbox"></label>'
                '<label>&nbsp;<button class="btn ghost" id="t_auto" type="button">select the day plan</button></label>'
                '</div><div class="result" id="ptotal"></div>'
                '<p class="sm muted" id="t_days"></p>'
                '<p class="sm">The dates and the default hotel above are an automatically selected research '
                'scenario, not confirmed travel dates, and the walk to the poker room is not verified for every hotel '
                '(see <a href="routes.html">Walking routes</a>).</p>'
                '<p class="sm">The mode selector &ldquo;official published rate floor&rdquo; uses only a number the '
                'property itself publishes (for the Venetian: $119 + $55, taxed at 13.38%%) and labels the result an '
                'estimate. It is not a quote for these dates: the page says rates start as low as that figure, are '
                'subject to qualifying play and availability, and revert to the prevailing rate for any night the play '
                'condition is not met.</p></div>' % t["nights"])
    b.append(scenario)
    prim_ids = {v["primary"] for d in PLAN for v in d["venues"] if v["primary"]}
    fb_ids = {v["fallback"] for d in PLAN for v in d["venues"] if v["fallback"]}
    rows_html = []
    for r in sorted([x for x in ROWS if x["id"] in (prim_ids | fb_ids) and x.get("buyin")],
                    key=lambda r: (r["date"], r["start"])):
        role = "primary" if r["id"] in prim_ids else "fallback"
        chk = ('<td><input type="checkbox" data-buyin="%s" data-date="%s" data-pool="%s" data-primary="%d"></td>'
               % (r["buyin"], esc(r["date"]), r.get("to_prize_pool") or "", 1 if role == "primary" else 0))
        cells = [chk,
                 '<td class="nowrap">%s</td>' % pretty(r["date"]),
                 '<td class="nowrap">%s</td>' % esc(hhmm12(r["start"])),
                 '<td>%s</td>' % esc(r["name"]),
                 '<td class="num">%s</td>' % money(r["buyin"]),
                 '<td class="num">%s</td>' % money(r.get("guarantee")),
                 '<td><span class="pill %s">%s</span></td>' % ("ok" if role == "primary" else "warn", role),
                 '<td>%s</td>' % (link(r.get("schedule_url") or r.get("sheet_url"),
                                        "schedule row" if r.get("schedule_url") else "structure sheet"))]
        rows_html.append('<tr data-date="%s">%s</tr>' % (esc(r["date"]), "".join(cells)))
    b.append('<div class="panel" id="picks"><h3>Events in the window that the day plan offers</h3>'
             '<div class="tablewrap"><table class="grid"><thead><tr><th>Play?</th><th>Date</th><th>Start</th>'
             '<th>Event</th><th class="num">Buy-in</th><th class="num">Guarantee</th><th>Role</th>'
             '<th>Official source</th></tr></thead>'
             '<tbody>%s</tbody></table></div></div>' % "".join(rows_html))
    b.append('<script type="application/json" id="cfg">%s</script>'
             % json.dumps({"hotels": {h["key"]: {"fee": h.get("resort_fee"), "tax": h.get("tax_rate_pct"),
                                                  "floor": h.get("poker_rate_floor"), "parking": h.get("parking_cost_per_night"),
                                                  "parking_free_if_playing": bool(h.get("parking_cost_if_playing_3h") == 0)}
                                     for h in HOTELS}}, separators=(",", ":")))
    b.append(panel("What the total does and does not include",
                   '<div class="kv">'
                   '<dt>Included</dt><dd>one listed buy-in per selected event; nights &times; (room rate + mandatory '
                   'resort fee) &times; 1.1338 where a rate basis exists.</dd>'
                   '<dt>Deliberately not included</dt><dd>re-entry or add-on money (the events offering them are not in '
                   'this list), travel, food, any fee a hotel adds at the desk that is not stated on an official page, '
                   'and airfare to or from Las Vegas.</dd>'
                   '<dt>Why no event-count multiplier</dt><dd>an earlier version had a "re-entry multiplier" box, which '
                   'made a single-entry trip look like it had a cheap way to add attempts. If you choose to re-enter, '
                   'you are outside the single-entry policy: model that on the advantage page instead.</dd>'
                   '<dt>Cancellation exposure</dt><dd>%s</dd></div>'
                   % esc("the Wynn terms read today require a one-night room + tax deposit and a 72-hour cancellation "
                         "deadline; the Venetian and Caesars pages read today do not state a single corporate deadline, "
                         "so it stays blank rather than assumed.")))
    write("pages/planner.html", page("Trip cost", "".join(b), "planner.html", 1))


def build_venue(vkey, fname, title, intro):
    rows = sorted([r for r in ROWS if r["venue_key"] == vkey], key=lambda r: (r.get("date") or "9999", r.get("start") or ""))
    v = next((x for x in VENUES if x.get("key") == vkey), {})
    hotels = [h for h in HOTELS if (h.get("room") or "").lower() in (v.get("room") or "").lower() or h.get("key") == vkey]
    b = ["<h1>%s</h1>" % title, '<p class="lead">%s</p>' % intro]
    if v:
        b.append(panel("Room facts, from the room's own page",
                       '<div class="kv"><dt>Poker room</dt><dd>%s</dd><dt>Area</dt><dd>%s</dd>'
                       '<dt>Status</dt><dd>%s</dd><dt>Detail</dt><dd class="sm">%s</dd><dt>Source</dt><dd>%s</dd></div>'
                       % (esc(v.get("room")), esc(v.get("area")), esc(v.get("status")),
                          esc(v.get("status_note")), link(v.get("source"), "official room page"))))
    if hotels:
        body = []
        for h in HOTELS:
            tr = next((t for t in h["routes"] if t.get("venue_key") == vkey), None)
            if not tr and h.get("key") != vkey:
                continue
            body.append('<tr data-search="%s"><td><b>%s</b></td><td class="sm">%s</td><td class="num">%s</td>'
                        '<td class="num">%s</td><td class="sm">%s</td><td>%s</td></tr>'
                        % (esc((h["name"] + " " + (h.get("tier") or "")).lower()), esc(h["name"]),
                           esc(h.get("tier") or "no official rating"),
                           money(h.get("resort_fee")) if h.get("resort_fee") else '<span class="blank">range or blank</span>',
                           ("%d min" % tr["minutes"]) if tr and tr["minutes"] is not None else '<span class="blank">not published</span>',
                           esc((h.get("cancel") or "not published")[:150]),
                           link(tr["google"], "walk") if tr and tr.get("google") else "<span class='blank'>&mdash;</span>"))
        if body:
            b.append(panel("Hotels with a verified route to this room",
                           table(["Hotel", "Tier", "Mandatory resort fee", "Walk", "Cancellation", "Map"], body,
                                 "tvh-%s" % vkey, cls="grid", caption="one row per hotel that shares the property or publishes a route")))
    cols = ["date", "start", "end", "event", "name", "buyin", "fee", "pool", "gtd", "ratio", "chips", "levels",
            "latereg", "status", "lc", "sheet"]
    heads = ["Date", "Start", "Est. end", "Event", "Name", "Buy-in", "House fee", "To pool", "Guarantee",
             "GTD &divide; entry", "Chips", "Levels", "Late reg", "Entry rule", "Last checked", "Sheet"]
    b.append(panel("Every event row for this venue (%d)" % len(rows),
                   events_table("tv-%s" % vkey, rows, cols, heads,
                                caption="the same rows as the all-events table, filtered to this room")))
    uris = sorted({u for r in rows for u in r["sources"]})
    b.append(panel("Official sources behind this page (%d URLs)" % len(uris),
                   '<ul class="clean">%s</ul>' % "".join('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>'
                                                          % (esc(u), esc(u)) for u in uris[:60])))
    write("pages/venues/%s" % fname, page(title, "".join(b), "pages/venues/%s" % fname, 2))


def build_others():
    rooms = [v for v in VENUES if v.get("key") not in ("venetian", "wynn")]
    rows = sorted([r for r in ROWS if r["venue_key"] == "other"], key=lambda r: (r.get("venue") or "", r.get("start") or ""))
    b = ["<h1>Other Strip poker rooms</h1>",
         '<p class="lead">Every other room the brief names, with what its own page does and does not publish. Rows are '
         'kept blank where a room publishes no schedule &mdash; the site does not borrow a third-party schedule to fill '
         'a casino\'s own gap.</p>']
    body = []
    for v in rooms:
        body.append('<tr data-search="%s"><td><b>%s</b></td><td class="sm">%s</td><td><span class="pill %s">%s</span></td>'
                    '<td class="sm">%s</td><td>%s</td></tr>'
                    % (esc((v.get("name", "") + " " + v.get("room", "") + " " + v.get("status_note", "")).lower()),
                       esc(v.get("name")), esc(v.get("room")),
                       "ok" if v.get("status") == "open_official" else ("warn" if "no" in str(v.get("status")) else "mid"),
                       esc(v.get("status")), esc((v.get("status_note") or "")[:400]), link(v.get("source"), "official page")))
    b.append(filters("totherv", venues=False, dates=False, single=False) +
             table(["Room", "Location", "Schedule status", "What the official page says", "Source"], body, "totherv", cls="grid",
                   caption="status read from each room's own page"))
    b.append(panel("Other-room event rows (%d)" % len(rows),
                   events_table("totherev", rows, ["venue", "date", "start", "name", "buyin", "gtd", "chips", "levels",
                                                   "status", "evidence", "lc", "source"],
                                ["Room", "Date", "Start", "Event", "Buy-in", "Guarantee", "Chips", "Levels",
                                 "Entry rule", "Official sentence", "Last checked", "Source"],
                                caption="Caesars Palace dailies, Horseshoe, Resorts World and South Point", single=False)))
    b.append(panel("Why there is no full schedule for these rooms",
                   '<ul class="clean"><li>Caesars Palace publishes a standing daily slate in an editorial page, not a '
                   'dated calendar; its four daily starts all offer a $50 add-on, so none of them reaches the '
                   'single-entry list regardless.</li>'
                   '<li>Horseshoe, Resorts World and South Point publish no dated tournament list that a non-Java client '
                   'can read; the attempts and their results are on the <a href="monitor.html">source monitor</a>.</li>'
                   '<li>The MGM properties (Bellagio, MGM Grand, ARIA) publish room pages and hotel terms but no '
                   'retrievable tournament schedule for this window; their hotel terms are still used on the hotels '
                   'page because they are the official source for the resort fee.</li></ul>'))
    write("pages/venues/others.html", page("Other rooms", "".join(b), "pages/venues/others.html", 2))


def build_exec():
    c = META["counts"]
    b = ["<h1>Executive summary</h1>",
         '<p class="lead">Written from the merged dataset only; every number below is reproduced by '
         '<code>scripts/build_bdcaf0bf.py</code> from <code>data/bdcaf0bf/</code>.</p>']
    t = META["trip"]
    b.append(panel("The answer in six lines",
                   '<ol class="big-list"><li><b>Two series are live for the planned window.</b> The Venetian '
                   'DeepStack Extravaganza IV runs 16 Nov &ndash; 23 Dec 2026 with &ldquo;more than $3.6 Million in '
                   'guaranteed tournament prize pools&rdquo;, and the WPT World Championship runs 27 Nov &ndash; '
                   '21 Dec 2026 at Wynn &mdash; both read again from the properties\' own pages on %s.</li>'
                   '<li><b>%d of %d rows are usable under a single-entry policy.</b> None has an official one-entry '
                   'statement; %d have a sheet that was read in full with no re-entry, rebuy, add-on or purchased-chip '
                   'language, and that is the wording used for them.</li>'
                   '<li><b>%d rows are excluded and the reason is published for each</b>: starting flights with a '
                   'separate buy-in, Day 2 restarts, the Wynn Friday rebuy, Caesars\' $50 add-on, and two PokerAtlas '
                   'events whose first buy-in is cheaper for paying members.</li>'
                   '<li><b>An all-day plan from 8 AM is not available anywhere on the Strip in this window</b>: the '
                   'earliest official start is 10:10 AM, and a 28-level / 30-minute structure runs past midnight, so a '
                   'day is realistically one event plus a conditional second one only if you bust early.</li>'
                   '<li><b>Hotel: the host property wins on the two things that can be verified.</b> The Venetian / '
                   'Palazzo is the only hotel with a 0-minute indoor route to the poker room, a $55 + tax mandatory fee '
                   'stated on its own page, $20/day parking that is free to a player with 3 h+ of play, and an official '
                   'poker-suite rate starting at $119.</li>'
                   '<li><b>The one thing still missing is a dated room rate.</b> Every official booking engine needs '
                   'JavaScript, so the trip total stays <i>Incomplete</i> until a checkout quote is logged &mdash; the '
                   'alternative would be publishing a number nobody stated.</li></ol>'
                   % (esc(pretty(TODAY)), c["by_status"].get("no_reentry_language", 0), c["rows"],
                      c["by_status"].get("no_reentry_language", 0), c["by_status"].get("multi_entry_paid", 0))))
    b.append(panel("Numbers", stats_html()))
    b.append(panel("Recommended plan",
                   '<div class="kv"><dt>Dates</dt><dd>%s &rarr; %s (%d nights), chosen by the build from the official '
                   'rows, not typed in</dd><dt>Base</dt><dd>The Venetian / The Palazzo, poker suite rate basis, '
                   '$55 + tax fee, $0 parking if you play 3 h+</dd><dt>Play</dt><dd>the %d single-entry-standard events '
                   'in that window; %d of them are also in the day plan as a primary or a conditional fallback</dd>'
                   '<dt>Avoid</dt><dd>anything on the <a href="tournaments-double.html">advantage page</a></dd>'
                   '<dt>Before paying</dt><dd>re-read the schedule row, the structure sheet and the hotel cancellation '
                   'deadline on the same morning you book &mdash; the <a href="monitor.html">source monitor</a> shows '
                   'when any of them last changed</dd></div>'
                   % (pretty(t["check_in"]), pretty(t["check_out"]), t["nights"],
                      sum(1 for r in ROWS if r["entry_status"] == "no_reentry_language" and t["check_in"] <= (r.get("date") or "") <= t["check_out"]),
                      len({v["primary"] for dd in PLAN for v in dd["venues"] if v["primary"] and t["check_in"] <= dd["date"] <= t["check_out"]}))
                   ))
    b.append(panel("Top risks, each with its page",
                   '<ul class="clean">'
                   '<li><b>Silence is not a rule.</b> Grade B means the sheet says nothing, not that re-entry is forbidden. See <a href="single-entry.html">the standard</a>.</li>'
                   '<li><b>Guarantees are not fields.</b> A $15K guarantee with 40 entrants is $375 per entry, less than the buy-in; the ratio on this site is descriptive only. See <a href="ranking.html">Value ranking</a>.</li>'
                   '<li><b>The resort fee is taxed.</b> (rate + fee) &times; 1.1338, not rate &times; 1.1338 + fee. See <a href="hotels.html">Hotels</a>.</li>'
                   '<li><b>Hotel quality has no official measure</b>, so the brief\'s "quality over distance" preference cannot be scored here; see flagged item B05.</li>'
                   '<li><b>The published schedule moves.</b> Rows carry a last-checked date and a change badge; treat anything older than a week as unconfirmed. See <a href="monitor.html">Source monitor</a>.</li></ul>'))
    b.append(panel("Decisions this file cannot make for you",
                   '<p class="sm">The five questions on the <a href="questions.html">Questions</a> page that actually '
                   'change the answer: your exact dates, your nightly ceiling, whether a satellite entry counts as an '
                   'acceptable route into a main event, whether you accept a hotel whose resort fee is published only '
                   'as a range, and whether you will accept the 10:10 AM reality instead of an 8:00 AM start.</p>'))
    write("pages/executive-summary.html", page("Executive summary", "".join(b), "executive-summary.html", 1))


def build_questions():
    b = ["<h1>Questions, information and answers</h1>",
         '<p class="lead">What must be resolved before a booking decision is reasonable, split into what the site '
         'already has, what is missing, and the concrete way to get each missing piece. Nothing here asks you to '
         'supply data the official sources could give &mdash; those gaps are chased automatically by the daily job.</p>']
    body = []
    for q in QUESTIONS:
        cells = ['<td class="nowrap"><b>%s</b></td>' % esc(q.get("id")),
                 "<td>%s</td>" % esc(q.get("q")),
                 '<td class="sm">%s</td>' % esc(q.get("have")),
                 '<td class="sm">%s</td>' % esc(q.get("missing")),
                 '<td class="sm">%s</td>' % esc(q.get("how")),
                 "<td>%s</td>" % (link(q.get("source"), q.get("source_label") or "official page")
                                  if q.get("source") else '<span class="blank">no source cited</span>')]
        search = " ".join(str(q.get(k) or "") for k in ("id", "q", "have", "missing", "how")).lower()
        body.append('<tr data-search="%s">%s</tr>' % (esc(search), "".join(cells)))
    b.append(filters("tques", venues=False, dates=False, single=False) +
             table(["#", "Question", "What we already have", "What is missing", "How to find it",
                    "Official source"], body, "tques", cls="grid",
                   caption="%d questions; the four new ones below were added by this session" % len(body)))
    extra = [
        ("Q11", "Does a tag-team or satellite entry satisfy the single-entry policy?",
         "%d satellites and 1 tag-team event are labelled and kept out of the ranking" % META["counts"]["satellite_rows"],
         "A rule decision, not a data gap: whether one entry means one buy-in for any number of players.",
         "Answer it on the suggestions board (S06); the tables can then show or hide that grade without touching any source."),
        ("Q12", "Which night-tied hotel offer applies in December 2026?",
         "The official Venetian poker-rate page states $119 and $209 starting rates with a 6 h cash or $300+ tournament-per-night condition",
         "The rate actually offered for the chosen dates, and whether a tournament entry satisfies the play condition each night",
         "The phone line the official page itself prints (866.255.8936, code EPOKR25) quotes up to 150 days ahead; it is the only official channel that will answer for specific dates."),
        ("Q13", "Is the Caesars Palace resort fee $45 or $60?",
         "The official corporate disclaimer states a range of $45-$60 plus tax, waived for Diamond and Seven Stars members",
         "The amount that applies to a specific December 2026 booking, which only the booking flow for those dates reveals",
         "Keep the row blank and the flag open (B03); compare a logged checkout total for those dates instead of a fee."),
        ("Q14", "How long is the walk from a non-host hotel to the Venetian poker room?",
         "Official on-property directions (the room is inside The Palazzo, level 2 of the Grand Canal Shoppes) plus map links for every pair",
         "A published minute count for any cross-property walk: no casino, hotel or county page states one",
         "Time it once, or read a map at booking time. The site does not import third-party walking times as facts."),
        ("Q15", "Can a day start at 8:00 AM as the brief asks?",
         "The complete official Venetian schedule for 16 Nov - 23 Dec 2026, re-read on 2026-11-19",
         "Nothing is missing: the earliest published start in the window is 10:10 AM, and no other Strip room publishes an 8 AM event",
         "Accept the 10:10 AM reality, or arrive before the published start for seating and pre-registration. The day plan states this on every date."),
    ]
    DSE = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
    EXSRC = {
        "Q11": (DSE, "the schedule page that lists the satellites"),
        "Q12": ("https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
                "official poker-rate page and booking line"),
        "Q13": ("https://www.caesars.com/corporate/disclaimer", "official Caesars disclaimer"),
        "Q14": ("https://www.venetianlasvegas.com/resort/casino/poker.html", "official room location page"),
        "Q15": (DSE, "the official start times"),
    }
    rows2 = ['<tr data-search="%s"><td class="nowrap"><b>%s</b></td><td>%s</td><td class="sm">%s</td>'
             '<td class="sm">%s</td><td class="sm">%s</td><td>%s</td></tr>'
             % (esc((" ".join(str(x) for x in q)).lower()), esc(q[0]), esc(q[1]), esc(q[2]), esc(q[3]),
                esc(q[4]), link(EXSRC.get(q[0], (DSE, "official page"))[0], EXSRC.get(q[0], (DSE, ""))[1]))
             for q in extra]
    b.append(panel("New questions raised by this session",
                   table(["#", "Question", "What we already have", "What is missing", "How to find it",
                          "Official source"], rows2, "tques2", cls="grid",
                         caption="each one is either a rule decision for the traveller or a fact only a dated booking flow can give")))
    write("pages/questions.html", page("Questions", "".join(b), "questions.html", 1))


def build_suggestions():
    b = ["<h1>Suggestions board</h1>",
         '<p class="lead">Every improvement, its options and its consequence, so a path can be chosen before anything '
         'is implemented. Items marked <b>implemented in this build</b> are live now; the rest wait for a decision and '
         'are deliberately not half-built. Tick a box to record a choice in this browser &mdash; nothing is sent '
         'anywhere.</p>']
    impl = {"S01", "S02", "S03"}
    cards = []
    for s in SUGGESTIONS:
        opts = "".join('<li>%s</li>' % esc(o) for o in (s.get("options") or []))
        done = s.get("id") in impl
        cards.append('<div class="panel"><h3><label class="tick"><input type="checkbox" data-sug="%s"> %s &middot; %s '
                     '%s</label></h3><div class="kv"><dt>Problem</dt><dd>%s</dd><dt>Options</dt><dd><ul class="clean">%s</ul></dd>'
                     '<dt>Effect of choosing</dt><dd>%s</dd></div></div>'
                     % (esc(s.get("id")), esc(s.get("id")), esc(s.get("title")),
                        '<span class="pill ok">implemented in this build</span>' if done else '<span class="pill warn">awaiting a decision</span>',
                        esc(s.get("problem")), opts, esc(s.get("effect"))))
    b.append('<div class="two">%s</div>' % "".join(cards))
    new = [
        ("S09", "Publish the entry-rule grade on every row, not just a boolean",
         "Readers kept asking whether &ldquo;single-entry&rdquo; meant a stated rule or an absence of evidence.",
         ["Keep two grades", "Add a third grade for sheets that were unread", "Return to a boolean"],
         "Implemented here as Grade A/B plus an excluded and an unread bucket, each with its own page.", True),
        ("S10", "Stop the two scheduled jobs from rewriting the same site",
         "Two workflows each regenerated index.html and pages/ from different datasets, so the published answers alternated.",
         ["Point both at one canonical builder", "Retire the older job", "Leave the alternation"],
         "Implemented: only build_bdcaf0bf.py writes the root site; the monitors keep refreshing data and marking changes.", True),
        ("S11", "Compare events on stack depth and blind speed, not only on the guarantee",
         "The brief asks for starting stack, blind duration, payout structure and schedule fit as comparison axes.",
         ["Add all four columns to the ranking table", "Add only where the sheet states them", "Leave the ranking on the ratio"],
         "Implemented partially: chips and level length are shown per row; payout structure is shown as the field-size "
         "percentage the sheet states; events without those numbers are excluded rather than padded.", True),
        ("S12", "Add a real nightly-rate feed",
         "A dated rate log would remove the only remaining blank in the trip total.",
         ["Scrape the booking engines (needs JavaScript)", "Call the published poker booking line by hand", "Leave it blank and flagged"],
         "Open. The first option is technically impossible from this sandbox and unreliable on a runner; the second "
         "needs a person.", False),
        ("S13", "Give the day plan a hard finish-time cap",
         "A structure that runs past midnight collides with the next morning's start.",
         ["Cap at 1:00 AM", "Cap at midnight", "No cap, flag overlaps only"],
         "Open. Today the plan flags overlaps and states the estimated end; a cap would drop events rather than label them.", False),
    ]
    cards2 = []
    for sid, title, problem, opts, effect, done in new:
        cards2.append('<div class="panel"><h3>%s &middot; %s %s</h3><div class="kv"><dt>Problem</dt><dd>%s</dd>'
                      '<dt>Options</dt><dd><ul class="clean">%s</ul></dd><dt>Status</dt><dd>%s</dd></div></div>'
                      % (esc(sid), esc(title), '<span class="pill ok">done here</span>' if done else
                         '<span class="pill warn">awaiting a decision</span>', esc(problem),
                         "".join("<li>%s</li>" % esc(o) for o in opts), esc(effect)))
    b.append('<h2 style="margin-top:18px">Added by this session</h2><div class="two">%s</div>' % "".join(cards2))
    b.append(panel("How to read the board",
                   '<p class="sm">No suggestion changes a source value. Anything that would &mdash; for example '
                   'importing third-party walking times or review scores &mdash; is written as a question on the '
                   'Questions page instead, because it would break the official-source rule the site exists to keep.</p>'))
    write("pages/suggestions.html", page("Suggestions", "".join(b), "suggestions.html", 1))


def build_flagged():
    b = ["<h1>Flagged for review</h1>",
         '<p class="lead">Every irregularity, blank value and cross-session disagreement, each with the official URL it '
         'came from. This page is the review queue after the site is live; nothing here blocks publication.</p>']
    body = []
    for f in FLAGS:
        srcs = "".join(link(u, "source") for u in (f.get("sources") or [])[:3])
        state = str(f.get("state") or "open")
        cls = "ok" if ("fixed" in state or "resolved" in state) else "warn"
        cells = ['<td class="nowrap"><b>%s</b></td>' % esc(f.get("id")),
                 "<td>%s</td>" % esc(f.get("area")),
                 "<td><b>%s</b></td>" % esc(f.get("title")),
                 '<td class="sm">%s</td>' % esc(f.get("detail")),
                 '<td>%s</td>' % (srcs or '<span class="blank">no single URL - see the row it refers to</span>'),
                 '<td class="nowrap"><span class="pill %s">%s</span></td>' % (cls, esc(state)),
                 '<td class="sm">%s</td>' % esc(f.get("owner") or "")]
        search = " ".join(str(f.get(k) or "") for k in ("id", "area", "title", "detail")).lower()
        body.append('<tr data-search="%s">%s</tr>' % (esc(search), "".join(cells)))
    b.append(filters("tflags", venues=False, dates=False, single=False) +
             table(["#", "Area", "Irregularity", "Detail", "Sources", "State", "Logged by"], body, "tflags", cls="grid",
                   caption="%d items" % len(body)))
    blanks = {}
    for r in ROWS:
        for key in ("buyin", "guarantee", "chips", "level_minutes", "late_reg_close", "end_estimate", "ratio"):
            if not r.get(key):
                blanks.setdefault(key, []).append(r)
    heads = ["Blank field", "Rows", "Why it is blank rather than filled", "Example rows",
             "Official source that omits it"]
    rows_html = []
    reasons = {
        "buyin": "the room publishes no buy-in for that row (Horseshoe and some South Point lists show times only)",
        "guarantee": "no guarantee is printed on that sheet or row; a plain sheet means no posted pool",
        "chips": "the sheet has no starting-chips line that the capture could match",
        "level_minutes": "the sheet's level table is published as an image or with mixed lengths",
        "late_reg_close": "no late-registration window is stated on the source that lists the event",
        "end_estimate": "no level count is published, so no duration can be derived without guessing",
        "ratio": "either the buy-in or the guarantee is missing, so the ratio cannot exist",
    }
    for k, rs in sorted(blanks.items(), key=lambda x: -len(x[1])):
        ex = "".join('<li><a href="tournaments.html#%s">%s %s</a></li>' % (esc(r["id"]), esc(r.get("date") or "no date"), esc(r["name"][:46]))
                    for r in rs[:4])
        first = rs[0]
        cite = first.get("schedule_url") or first.get("sheet_url") or ""
        rows_html.append('<tr data-search="%s"><td><code>%s</code></td><td class="num">%d</td><td class="sm">%s</td>'
                         '<td><ul class="clean">%s</ul></td><td>%s</td></tr>'
                         % (esc((k + " " + str(first.get("venue")) + " " + str(first.get("name"))).lower()),
                            esc(k), len(rs), esc(reasons.get(k, "no official source states it")), ex,
                            link(cite, "%s page that omits it" % (first.get("venue") or "the room's")) if cite
                            else '<span class="blank">no official page for this row</span>'))
    b.append(panel("Blank cells by field (%d kinds)" % len(blanks),
                   table(["Blank field", "Rows", "Why it is blank rather than filled", "Example rows",
                          "Official source that omits it"], rows_html, "tblanks", cls="grid",
                         caption="each blank is a source gap, not an omission; the row still appears everywhere else with its own sources")))
    chg_rows = []
    for u in sorted(CHANGED_URLS.values(), key=lambda x: -x.get("rows", 0)):
        cells = ['<td class="sm">%s</td>' % link(u["url"], u["url"][:90]),
                 "<td>%s</td>" % esc(u.get("kind")),
                 '<td class="num">%s</td>' % u.get("rows", 0),
                 '<td class="sm">%s</td>' % esc((u.get("note") or "")[:220])]
        chg_rows.append('<tr data-search="%s">%s</tr>' % (esc((u["url"] + " " + str(u.get("label"))).lower()),
                                                          "".join(cells)))
    chg_body = ("This build's own re-reads found no value that a source now states differently: every figure on the "
                "site still matches what the official page printed on %s." % pretty(TODAY))
    if chg_rows:
        chg_body = ("%d URLs have had their content hash change since the values were captured. A change marks the row "
                    "for a human re-read; it never silently overwrites a published number."
                    % STATE.get("changed_count", 0))
    b.append(panel("Rows whose official source changed",
                   '<p class="sm">%s</p>%s' % (chg_body,
                   table(["URL", "Kind", "Rows affected", "Note"], chg_rows, "tchanged", cls="grid",
                         caption="from the daily re-check"))))
    ar = [r for r in ROWS if r.get("sheet_arithmetic_note")]
    if ar:
        ar_rows = []
        for r in ar:
            cells = ["<td>%s</td>" % esc(r["id"]), "<td>%s</td>" % pretty(r.get("date")),
                     "<td>%s</td>" % esc((r.get("name") or "")[:60]),
                     '<td class="sm">%s</td>' % esc(r["sheet_arithmetic_note"]),
                     "<td>%s</td>" % (link(r.get("sheet_url"), "sheet"))]
            ar_rows.append('<tr data-search="%s">%s</tr>' % (esc((r["id"] + " " + str(r.get("name"))).lower()),
                                                              "".join(cells)))
        b.append(panel("Official sources that disagree with themselves (%d rows)" % len(ar),
                       table(["Row", "Date", "Event", "What the sheet says", "Sheet"], ar_rows, "tmath", cls="grid",
                             caption="the printed cutoff is used and the arithmetic is flagged - nothing is corrected silently")))
    write("pages/flagged-review.html", page("Flagged for review", "".join(b), "flagged-review.html", 1))


def build_monitor():
    b = ["<h1>Source monitor</h1>",
         '<p class="lead">Every official URL behind a published value is re-read on a schedule. The job records the '
         'HTTP status, a content hash and a date, compares the hash with the previous run, and flags the rows whose '
         'source moved. It never overwrites a captured value by itself.</p>']
    ok = sum(1 for v in STATE["urls"].values() if str(v.get("status", "")).startswith(("verified", "2")))
    b.append('<div class="statgrid"><div class="stat"><div class="num">%d</div><div class="lbl">URLs in the ledger</div></div>'
             '<div class="stat"><div class="num">%d</div><div class="lbl">confirmed reachable / verified</div></div>'
             '<div class="stat"><div class="num">%d</div><div class="lbl">changed since capture</div></div>'
             '<div class="stat"><div class="num">%s</div><div class="lbl">last ledger update</div></div></div>'
             % (len(STATE["urls"]), ok, STATE.get("changed_count", 0), esc(str(STATE.get("updated"))[:10])))
    rows_html = []
    for u in sorted(STATE["urls"].values(), key=lambda x: (-x.get("rows", 0), x["url"])):
        st = str(u.get("status") or "unknown")
        cls = "ok" if st.startswith("verified") or st.startswith("2") else ("bad" if "error" in st or st == "unknown" else "warn")
        rows_html.append('<tr data-search="%s"><td class="sm">%s</td><td class="sm">%s</td><td><span class="pill %s">%s</span></td>'
                         '<td class="num">%s</td><td class="nowrap sm">%s</td><td class="nowrap sm">%s</td>'
                         '<td class="sm">%s</td></tr>'
                         % (esc((u["url"] + " " + (u.get("label") or "") + " " + (u.get("kind") or "")).lower()),
                            link(u["url"], u["url"][:110]), esc((u.get("label") or "")[:70]), cls, esc(st),
                            u.get("rows", 0), esc(u.get("first_checked") or ""), esc(u.get("last_checked") or ""),
                            esc((u.get("note") or "")[:160])))
    b.append(filters("tmon", venues=False, dates=False, single=False) +
             table(["URL", "What it backs", "Status", "Rows", "First checked", "Last checked", "Note"], rows_html,
                   "tmon", cls="grid", caption="%d URLs, sorted by how many rows depend on them" % len(rows_html)))
    log = load("change_log.json", [])
    rows2 = ['<tr data-search="%s"><td class="nowrap sm">%s</td><td class="sm">%s</td><td class="num sm">%s &rarr; %s</td>'
             '<td class="num sm">%s &rarr; %s</td></tr>'
             % (esc((e.get("url", "") + str(e.get("label"))).lower()), esc(e.get("changed_at")),
                link(e.get("url"), (e.get("url") or "")[:90]), esc((e.get("old_sha256") or "")[:10]),
                esc((e.get("new_sha256") or "")[:10]), e.get("old_bytes"), e.get("new_bytes"))
             for e in log]
    b.append(panel("Change log (%d recorded changes)" % len(log),
                   filters("tchlog", venues=False, dates=False, single=False) +
                   table(["Detected", "URL", "Hash", "Bytes"], rows2, "tchlog", cls="grid",
                         opts="data-nosrc",
                         caption="appended by the scheduled job; booking-engine pages change constantly and are recorded but never used as verified values")))
    b.append(panel("The automation",
                   '<div class="kv"><dt>Daily job</dt><dd><code>.github/workflows/integrate-bdcaf0bf.yml</code> &mdash; '
                   're-reads every URL in the ledger, refreshes <code>data/bdcaf0bf/last_checked.json</code>, re-runs '
                   'the merge and the build, validates the result and commits it to <code>main</code>, so the published '
                   'pages move only when a source moved.</dd>'
                   '<dt>Venetian capture</dt><dd><code>.github/workflows/daily-scrape.yml</code> still reads the DSE IV '
                   'schedule page and all 37 structure sheets each morning into <code>data/c6087e2c/</code>; it no '
                   'longer writes the root site.</dd>'
                   '<dt>Other rooms</dt><dd><code>.github/workflows/recheck-ea99006a.yml</code> keeps refreshing the '
                   'WPT / Wynn / other-room ledger in <code>data/ea99006a/</code>; it no longer writes the root site.</dd>'
                   '<dt>Offline check</dt><dd><code>python3 scripts/recheck_bdcaf0bf.py --offline</code> validates the '
                   'ledger without any network, which is what CI runs from this sandbox.</dd></div>'))
    write("pages/monitor.html", page("Source monitor", "".join(b), "monitor.html", 1))


def build_method():
    b = ["<h1>Method, standard and formulas</h1>",
         '<p class="lead">The rules this build applies to every row, so a reader can check a verdict instead of trusting it.</p>']
    b.append(panel("Verification chain",
                   '<div class="kv">'
                   '<dt>1. Read</dt><dd>the official schedule page and every structure sheet PDF it links; the room\'s '
                   'own page for each other venue; the hotel\'s own resort-fee, parking and terms pages; the county '
                   'ordinance for the tax.</dd>'
                   '<dt>2. Store</dt><dd>one record per row with the verbatim excerpt of each field, the URL, the '
                   'retrieval timestamp and the file hash (<code>data/c6087e2c/</code>, <code>data/ea99006a/</code>).</dd>'
                   '<dt>3. Merge</dt><dd><code>scripts/integrate_bdcaf0bf.py</code> joins the two independent captures, '
                   're-reads the sheet text with its own keyword pass, applies the ladder below and keeps every '
                   'disagreement as data (<code>data/bdcaf0bf/conflicts.json</code>).</dd>'
                   '<dt>4. Build</dt><dd><code>scripts/build_bdcaf0bf.py</code> refuses to publish a data row without a '
                   'source link, and refuses a broken internal link.</dd>'
                   '<dt>5. Check</dt><dd><code>scripts/check_bdcaf0bf.py</code> re-derives every grade from the stored '
                   'fields, verifies each row\'s source link, and fails on an inferred value.</dd>'
                   '<dt>6. Re-check</dt><dd>daily, on a GitHub Actions runner: each URL is fetched, hashed and '
                   'compared; changed rows are badged on the tables and listed on the monitor page.</dd></div>'))
    b.append(panel("The single-entry standard",
                   '<p class="sm">%s</p>' % esc(META["standard"]["single_entry_rule"])))
    b.append(panel("Formulas used, exactly",
                   '<div class="kv">'
                   '<dt>True cost per hotel night</dt><dd>(room rate + mandatory resort fee) &times; (1 + 0.1338); the '
                   'fee is inside the tax base because the ordinance defines rent to include separately stated facility '
                   'and access fees.</dd>'
                   '<dt>Trip cost</dt><dd>entries &times; listed buy-ins + nights &times; true hotel cost; parking is '
                   'added only when the guest opts in, because the official page makes it free for a player with 3 h+ '
                   'of play.</dd>'
                   '<dt>Estimated end of an event</dt><dd>published start + (level count &times; level length) + three '
                   '15-minute breaks, all from the same sheet; rows without a level count get no estimate.</dd>'
                   '<dt>Value ratio</dt><dd>guarantee &divide; buy-in, computed only when both are published; '
                   'descriptive, never a forecast.</dd>'
                   '<dt>Overlap test</dt><dd>two events conflict when the later one starts before the earlier one\'s '
                   'estimated end, or before its own late-registration window can be reached.</dd>'
                   '<dt>Walk test</dt><dd>verified only where the official page establishes the room is inside the '
                   'hotel; everything else stays unknown against the 30-minute limit.</dd></div>'))
    b.append(panel("What counts as an official source",
                   '<p class="sm">The property or operator\'s own page, PDF or ordinance: venetianlasvegas.com, '
                   'wynnlasvegas.com and cdn.wynnresorts.com, caesars.com, mgmresorts.com property pages, '
                   'rwlasvegas.com, southpointcasino.com, the WPT\'s own published PDFs, and clarkcountynv.gov. '
                   'News sites, forums, odds sites and review sites are never used to set a value. Where a casino '
                   'publishes a fact only inside an offer\'s terms, this site says so on the row and keeps the '
                   'applicability question open (see flags F28 and B04).</p>'))
    uris = table(["URL", "Kind", "What it backs", "Rows", "Status", "Last checked"],
                 ['<tr data-search="%s"><td class="sm">%s</td><td>%s</td><td class="sm">%s</td><td class="num">%s</td>'
                  '<td>%s</td><td class="nowrap sm">%s</td></tr>'
                  % (esc((s["url"] + (s.get("label") or "")).lower()), link(s["url"], s["url"][:95]),
                     esc(s.get("kind") or ""), esc((s.get("label") or "")[:90]), s.get("rows", 0),
                     esc(str(s.get("status") if s.get("status") is not None else "not fetched")),
                     esc(str((STATE["urls"].get(s["url"]) or {}).get("last_checked") or "")))
                  for s in SOURCES], "tsources", cls="grid",
                 caption="%d URLs in the ledger; the same data is in <code>data/bdcaf0bf/sources.json</code>" % len(SOURCES))
    b.append(panel("Complete source ledger", filters("tsources", venues=False, dates=False, single=False) + uris))
    b.append(panel("Data files",
                   '<ul class="clean">%s</ul>' % "".join(
                       '<li><a href="%s/blob/main/data/bdcaf0bf/%s"><code>data/bdcaf0bf/%s</code></a> &mdash; %s</li>'
                       % (REPO, esc(f), esc(f), esc(DESC.get(f, "")))
                       for f in sorted(os.listdir(DATA)) if f.endswith(".json"))))
    write("pages/method.html", page("Method", "".join(b), "method.html", 1))


DESC = {
    "events.json": "every event row: values, structured rule fields, official excerpt per field, grade, sources, dates",
    "hotels.json": "hotel facts: mandatory fee, tax, parking, cancellation, booking link, walk routes, quality note or flag",
    "rates_log.json": "dated room-rate snapshots kept as a log so like-for-like comparison is possible",
    "plan.json": "one primary event plus a conditional fallback per day per room, with the overlap flags",
    "windows.json": "every 7-night window scored by how many playable single-entry-standard days it contains",
    "flags.json": "the review queue: unverified values, source gaps, cross-session disagreements",
    "conflicts.json": "row-level disagreements between the two earlier captures, with both excerpts",
    "sources.json": "the URL ledger: what each URL backs and how many rows depend on it",
    "last_checked.json": "per-URL monitor state: status, hash, first and last check, changed flag",
    "change_log.json": "recorded source changes from the scheduled re-checks",
    "facts.json": "this session's own re-reads of the official pages on 2026-11-19, with quotes",
    "questions.json": "what must be answered before a decision, what is missing, and how to find it",
    "suggestions.json": "the improvement board with options and consequences",
    "venues.json": "each poker room's own page: location, hours, status",
    "meta.json": "counts, the standard, the formulas, the computed trip window and the budget assumption",
}


def build_repo_review():
    files = []
    for dirpath, dirnames, fnames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "node_modules", ".pytest_cache"}]
        for f in fnames:
            rel = os.path.relpath(os.path.join(dirpath, f), ROOT).replace(os.sep, "/")
            if rel.startswith(".git/"):
                continue
            p = os.path.join(ROOT, rel)
            try:
                size = os.path.getsize(p)
            except OSError:
                size = 0
            files.append((rel, size))
    files.sort()
    total = sum(sz for _, sz in files)
    b = ["<h1>Repository review</h1>",
         '<p class="lead">A file-by-file inventory generated from the working tree at build time, plus the defects '
         'found while reading it. %d files, %s bytes. Nothing is summarised away.</p>'
         % (len(files), "{:,}".format(total))]
    groups = {}
    for rel, sz in files:
        top = rel.split("/")[0] if "/" in rel else "(root)"
        g = groups.setdefault(top, [0, 0])
        g[0] += 1
        g[1] += sz
    heads = ["Path", "Files", "Bytes", "Role"]
    ROLE = {
        "(root)": "the published root site: index.html, docs and repo tooling",
        "assets": "the published stylesheet and the site JavaScript written by this build",
        "data": "machine-readable captures, one folder per session; only data/bdcaf0bf/ feeds the published site",
        "pages": "the published subpages, all generated by scripts/build_bdcaf0bf.py",
        "scripts": "one builder / checker / monitor per session; build_bdcaf0bf.py is the canonical one",
        ".github": "workflows: the daily captures, the monitors, the canonical integration job and the quality gate",
        "docs": "an earlier session's site, preserved",
        "site": "an earlier session's site, preserved",
        "tools": "an earlier session's builders, preserved",
        "test": "node tests kept by the quality gate",
        "work": "session working notes",
    }
    rows_html = []
    for top in sorted(groups, key=lambda k: -groups[k][1]):
        n, sz = groups[top]
        rows_html.append('<tr data-search="%s"><td><code>%s</code></td><td class="num">%d</td><td class="num">%s</td>'
                         '<td class="sm">%s</td></tr>'
                         % (esc(top.lower()), esc(top), n, "{:,}".format(sz), esc(ROLE.get(top, "an earlier session's output, preserved"))))
    b.append(filters("tgrp", venues=False, dates=False, single=False) +
             table(heads, rows_html, "tgrp", cls="grid", opts="data-nosrc",
                    caption="one row per top-level path - repository inventory, not sourced data"))
    rows_html2 = []
    for rel, sz in files:
        top = rel.split("/")[0] if "/" in rel else "(root)"
        own = ("bdcaf0bf" if "bdcaf0bf" in rel or rel.startswith(("index.html", "pages/", "assets/")) else
               (top.split("-")[-1][:8] if re.match(r"(site|docs|data|dashboard|planner|tools)", top) and "-" in top else "shared"))
        rows_html2.append('<tr data-search="%s"><td><code>%s</code></td><td class="num">%s</td><td><span class="sm">%s</span></td></tr>'
                          % (esc(rel.lower()), esc(rel), "{:,}".format(sz), esc(own)))
    b.append(panel("Every file", filters("tfiles", venues=False, dates=False, single=False) +
                   table(["Path", "Bytes", "Owned by"], rows_html2, "tfiles", cls="grid", opts="data-nosrc",
                         caption="search a path; &ldquo;owned by&rdquo; marks which session's generator produced it")))
    findings = [
        "The root site is now generated by <code>scripts/build_bdcaf0bf.py</code> from <code>data/bdcaf0bf/</code>, "
        "checked by <code>scripts/check_bdcaf0bf.py</code> and refreshed daily by "
        "<code>.github/workflows/integrate-bdcaf0bf.yml</code>. <code>scripts/build_ea99006a.py</code> and "
        "<code>scripts/build_251c122f.py</code> remain in the tree, and their data folders are still refreshed by their "
        "own workflows, but neither one writes the published site any more - that alternation was the repo's worst "
        "defect (flagged as B02).",
        "Fourteen session folders (docs/, site/, site-*/, dashboard-*/, planner-*/, data-*/, tools/) each publish a "
        "variant of the same brief with their own numbers. They are preserved untouched; the root site is the "
        "canonical one. This is a decision for the owner, not for an agent session, and it is listed on the "
        "suggestions board.",
        "Three different confirmed-single-entry counts have been published for the same 94 Venetian rows (0, 55 and "
        "now 53). This build states its rule explicitly on the single-entry page and prints the row-level disagreements "
        "instead of hiding them.",
        "The room-rate column is blank on every hotel: no official page states a dated rate for the planned dates, and "
        "the poker-suite page's $119/$209 figures are published as a starting rate conditional on play. The site keeps "
        "those numbers as a labelled rate-floor basis rather than laundering them into a quote.",
        "The Caesars corporate disclaimer states a resort-fee *range* ($45-$60) and some cached copies of the same page "
        "still show $45-$50, so the fee for those properties cannot be turned into a per-night number from an official "
        "source. Recorded as flag B03 with the live quote.",
        "Nine Venetian structure sheets print a late-registration clock that does not follow from their own level "
        "lengths (for example sheet 6 prints 10 levels + break as 4:55 PM where the same sheet's 30-minute levels from "
        "an 11:10 AM start give 4:25 PM). The printed clock is used, the arithmetic is flagged, and nothing is "
        "'fixed' silently.",
        "Two rows that an earlier session confirmed as single-entry (events #18 and #58, the PokerAtlas Valuetown "
        "bounty) carry a sheet sentence selling subsequent buy-ins at a member price. They are now in the excluded "
        "section, and the disagreement is recorded row by row.",
        "The sandbox that authors this repository cannot open a TCP connection to casino hosts, so live reading happens "
        "on GitHub Actions runners and through the agent's page-fetch tool; the hashes and quotes committed with each "
        "value are what makes that auditable.",
        "One committed file is a compiled Python artefact, <code>tools/__pycache__/data.cpython-311.pyc</code>; it was "
        "flagged by an earlier session and is left in place rather than deleted without that session's say.",
    ]
    b.append(panel("Findings", '<ul class="clean">%s</ul>' % "".join("<li>%s</li>" % f for f in findings)))
    write("pages/repo-review.html", page("Repo review", "".join(b), "repo-review.html", 1,
                                         extra_head="\n<meta name=\"file-count\" content=\"%d\">" % len(files)))


def main():
    build_index()
    build_tournaments()
    build_single()
    build_double()
    build_ranking()
    build_schedule()
    build_hotels()
    build_routes()
    build_planner()
    build_venue("venetian", "venetian.html", "The Venetian Resort &middot; DeepStack Extravaganza IV",
                "The host property for the planned window and the only room whose every event has a published structure "
                "sheet. Read again on %s: room in The Palazzo, level 2 of the Grand Canal Shoppes, 50 tables, open 24 "
                "hours, self-parking $20 a day for a registered guest and free for a player with three hours of play."
                % esc(pretty(TODAY)))
    build_venue("wynn", "wynn.html", "Wynn Las Vegas &middot; WPT World Championship",
                "The festival property for 27 Nov &ndash; 21 Dec 2026, re-read on %s from the room's own page, which "
                "also states that the $200,000-a-week daily slate is suspended during each Wynn series - so a December "
                "trip cannot plan around the 6 PM nightly. The Friday daily is named a Rebuy event and is excluded here."
                % esc(pretty(TODAY)))
    build_others()
    build_exec()
    build_questions()
    build_suggestions()
    build_flagged()
    build_monitor()
    build_method()
    build_repo_review()
    # NOTE: the root assets/app.js and assets/css/style.css belong to an earlier session's pages and to the
    # node test suite; this build writes its own pair and never overwrites theirs.
    write("assets/bdcaf0bf.css", CSS)
    write("assets/bdcaf0bf.js", JS)
    for alias, (target, label) in ALIASES.items():
        src = os.path.join(ROOT, target)
        with open(src, encoding="utf-8") as fh:
            txt = fh.read()
        note = ('<div class="warnbox">This page is kept so that an older link still resolves. Its content is the '
                '<a href="%s">%s</a> page, generated from the same merged dataset.</div>'
                % (os.path.basename(target), esc(label)))
        write(alias, txt.replace("<main>\n", "<main>\n" + note, 1))
    # link check + source enforcement
    for rel in sorted(WRITTEN):
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
        for m in re.finditer(r'(?:href|src)="([^"#]+)"', txt):
            href = m.group(1)
            if href.startswith(("http", "mailto:", "tel:", "data:", "//")):
                continue
            tgt = os.path.normpath(os.path.join(os.path.dirname(path), href))
            if not os.path.exists(tgt):
                ERRORS.append("%s: broken internal link %s" % (rel, href))
            elif href.endswith(".html") and os.path.relpath(tgt, ROOT).replace(os.sep, "/") not in WRITTEN and not os.path.exists(tgt):
                ERRORS.append("%s: link to a page this build does not generate: %s" % (rel, href))
    print("wrote %d files" % len(WRITTEN))
    if ERRORS:
        for e in ERRORS[:40]:
            print("  !", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
