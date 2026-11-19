#!/usr/bin/env python3
"""Session ea99006a - root site builder.

Builds the GitHub Pages site that is published from main /:
    index.html, pages/*.html, pages/venues/*.html, assets/**

Rules enforced here (the build fails, it does not warn):
  * every table row carries a link to an official source;
  * every internal link resolves to a file that was written.

Run:  python3 scripts/build_ea99006a.py
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "ea99006a")
PAGES = os.path.join(ROOT, "pages")

RULE_LABEL = {
    "confirmed_single": "Confirmed single-entry (standard S1)",
    "multi": "Multi-entry (re-entry / flights / add-on)",
    "unknown": "Entry cap not stated - unverified",
    "unread": "Entry terms not read - unverified",
}
# The published test behind that label, verbatim, so a verdict is checkable.
# (STD itself is read from meta.json once the data files are loaded, below.)
STD = None
RULE_CLASS = {
    "confirmed_single": "ok",
    "multi": "bad",
    "unknown": "warn",
    "unread": "warn2",
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


# ---------------------------------------------------------------- loading
META = load("meta.json")


def _opt(dirname, name, default):
    """Read an optional data file, so the build works before the monitor first runs."""
    p = os.path.join(dirname, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


B3DATA = os.path.join(ROOT, "data", "b3be876c")
RATES = _opt(DATA, "rates_log.json", [])
LEDGER = _opt(DATA, "last_checked.json", {})
VALCH = _opt(B3DATA, "value_changes.json", [])
MONRUN = _opt(B3DATA, "monitor_summary.json", {})
VERIF = _opt(B3DATA, "verification.json", {})
STD = META.get("rule_standard") or {
    "id": "S1",
    "text": ("A row is published as confirmed single-entry only when its own official structure sheet was read, "
             "names that event number, is a one-day event with a stated registration close, and contains no "
             "re-entry, rebuy, add-on, buy-back, subsequent-buy-in or purchased-stack provision."),
    "limitation": ("No official source states 'one entry only' in words, so confirmation means 'the published rules "
                   "grant no second entry', not 'the house promises a freezeout'."),
}

VEN = load("venetian.json")
WPT = load("wpt.json")
OTH = load("other.json")
VENUES = load("venues.json")
HOTELS = load("hotels.json")
ROUTES = load("routes.json")
FLAGS = load("flags.json")
QUESTIONS = load("questions.json")
SUGGESTIONS = load("suggestions.json")
RATE_SNAPSHOTS = load("rate_snapshots.json")
REQUIREMENTS = _opt(DATA, "requirements.json", {"rows": [], "statuses": {}, "note": ""})
CHANGE_LOG = load("change_log.json")


def _load_optional(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return json.load(fh)


MORNING_FEED = _load_optional("morning_feed.json")

# url -> earliest change event, for "source changed since this row was read" badges
# Entries are read defensively: the value-level monitor (scripts/monitor_b3be876c.py) and the
# hash-level recheck (scripts/recheck_ea99006a.py) both append to this log, and an entry missing
# the canonical keys must never break the build. Unknown keys are ignored; the timestamp falls
# back to "at" (the monitor's older key) and then to "" (never marks a row changed).
CHANGED_AT = {}
for _c in CHANGE_LOG:
    if not isinstance(_c, dict):
        continue
    u = _c.get("url")
    when = _c.get("changed_at") or _c.get("at") or ""
    if u and when and ("{" not in u) and ("google.com/maps" not in u):  # dynamic links never mark rows changed
        if u not in CHANGED_AT or when < CHANGED_AT[u]:
            CHANGED_AT[u] = when
VENUE_BY_KEY = dict((v["key"], v) for v in VENUES)
TAX = META["tax"]
TRIP = META["trip"]

# The only nightly room rate any Strip property publishes on an official page (a starting floor, not a quote).
VEN_POKER = {
    "rate_low": next((h.get("rate_floor") for h in HOTELS if h["key"] == "venetian"), None),
    "rate_high": next((h.get("rate_floor_alt") for h in HOTELS if h["key"] == "venetian"), None),
    "url": next((h.get("rate_floor_source") for h in HOTELS if h["key"] == "venetian"), ""),
    "caveat": next((h.get("rate_caveat") for h in HOTELS if h["key"] == "venetian"), ""),
}

_V_FEE = next((h["resort_fee"] for h in HOTELS if h["key"] == "venetian"), 0) or 0
# true nightly cost implied by the published floor rate: (room + fee) x (1 + tax)
FLOOR_TRUE_NIGHT = ((VEN_POKER.get("rate_low") or 0) + _V_FEE) * (1 + TAX["rate"] / 100.0)
RETRIEVED = META["retrieved"]

ALL_EVENTS = VEN + WPT + OTH
for _e in ALL_EVENTS:
    _e.setdefault("notes", "")


# ---------------------------------------------------------------- helpers
def minutes(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def pretty_date(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return "%s %d, %d" % (MONTHS[m - 1], dd, y)


def weekday(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return DAYS[datetime.date(y, m, dd).weekday()]


def pretty_time(t):
    h, m = (int(x) for x in t.split(":"))
    ap = "AM" if h < 12 else "PM"
    hh = h % 12 or 12
    return "%d:%02d %s" % (hh, m, ap)


LATE_RE = re.compile(r"\(?~?\s*(\d{1,2}):(\d{2})\s*(AM|PM)?\s*\)?", re.I)


def late_reg_close(row):
    """Return (minutes, label) using only what the official sheet states."""
    txt = row.get("late_reg") or ""
    if not txt:
        return None, ""
    m = LATE_RE.search(txt)
    if not m:
        return None, txt
    h = int(m.group(1))
    mm = int(m.group(2))
    ap = (m.group(3) or "").upper()
    if ap == "PM" and h < 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    if not ap:
        # bare 24h-ish clock times never appear; fall back to the raw text
        return None, txt
    return h * 60 + mm, txt


def guarantee_seats(row):
    """A satellite guarantees seats, not a money pool (e.g. '2 seats'). Returns the text or None."""
    g = row.get("guarantee")
    if g is None or isinstance(g, (int, float)):
        return None
    if "$" in str(g) or not re.search(r"[a-zA-Z]", str(g)):
        return None
    return str(g).strip()


def guarantee_value(row):
    """Dollars guaranteed, or None when the official source states no money guarantee."""
    if guarantee_seats(row):
        return None
    g = row.get("guarantee")
    if g is None or g == "":
        return None
    if isinstance(g, (int, float)):
        return float(g)
    s = re.sub(r"[^0-9.]", "", str(g).split(";")[0])
    try:
        return float(s)
    except ValueError:
        return None


def is_bounty(row):
    t = (row.get("name", "") + " " + row.get("sheet_title", "")).lower()
    n = (row.get("notes") or "").lower()
    return ("bounty" in t) or ("pko" in t) or ("bounty" in n)


def ratio_text(row):
    """Guarantee / entry fee. Descriptive only; blank when the row is not rankable.

    The stored `gtd_to_entry` field (derived by scripts/integrate_b3be876c.py from the same two
    official figures) is preferred so the number on the page is the number in the data; the
    computation is the fallback for rows that predate the field.
    """
    stored = row.get("gtd_to_entry")
    if stored:
        return "%.1f" % stored
    g = guarantee_value(row)
    b = row.get("buyin")
    if not g or not b:
        return ""
    return "%.1f" % (g / float(b))


def rankable(row):
    """The brief's ranking gate: rank only when the total entry fee AND the guarantee are both confirmed.

    A row whose two official captures disagree on the guarantee is never ranked, and a seat
    guarantee is not a money pool, so it can never be divided by a buy-in.
    """
    return bool(row.get("buyin")) and guarantee_value(row) is not None and not row.get("guarantee_note")


def src_link_opt(url, label="source"):
    """Like src_link but tolerant of a missing link, for use inside evidence blocks."""
    if not url:
        return '<span class="blank">no link recorded</span>'
    return src_link(url, label)


def changed_marker(row):
    """Only a change in the official SENTENCE behind a value marks the row; a page re-fetch does not."""
    if row.get("value_changed_at"):
        return '<br><span class="pill pill-bad">official value changed %s</span>' % esc(row["value_changed_at"][:10])
    if row.get("source_changed_at"):
        return ('<br><span class="muted sm" title="the page behind this row was re-fetched and its bytes differ; '
                'the sentence that carries the value did not change">page re-fetched %s</span>'
                % esc(row["source_changed_at"][:10]))
    return ""


def evidence_html(row):
    """The structured rule fields of this row: value, verbatim official excerpt, retrieval date, link.

    Rendered as a list, never a nested table: the checker parses each published row as one <tr>,
    and <details> is marked data-no-search so a negated excerpt ("no re-entry sentence appears")
    cannot make a row match a search for 're-entry'.
    """
    rf = row.get("rule_fields") or {}
    ev = row.get("entry_evidence") or {}
    if not rf and not ev:
        return ""
    order = [("single_entry", "Single-entry statement"), ("re_entry", "Re-entry / rebuy"), ("add_on", "Add-on"),
             ("house_fee", "House fee"), ("guarantee", "Guarantee"), ("late_registration", "Late registration"),
             ("starting_chips", "Starting chips"), ("level_minutes", "Level duration")]
    money_fields = {"house_fee", "guarantee"}
    items = []
    for key, label in order:
        f = rf.get(key) or {}
        if not f:
            continue
        val = f.get("value")
        if val in (None, ""):
            val = '<span class="blank">not stated</span>'
        elif isinstance(val, (int, float)):
            val = ("$%s" % format(int(val), ",d")) if key in money_fields else format(int(val), ",d")
        else:
            val = esc(val)
        # A <div>, never a nested <table>: the validator parses one <tr> per published row.
        items.append('<div class="fitem"><b>%s</b> = %s <span class="quote">&ldquo;%s&rdquo;</span> '
                     '<span class="muted">retrieved %s &middot; %s</span></div>'
                     % (esc(label), val, esc((f.get("excerpt") or "no such sentence on the sheet")[:400]),
                        esc(f.get("retrieved") or row.get("retrieved") or RETRIEVED),
                        src_link_opt(f.get("source"), "official source")))
    bits = []
    if ev.get("sheet_no"):
        bits.append("structure sheet %s" % esc(ev["sheet_no"]))
    if ev.get("sheet_effective_date"):
        bits.append("effective %s" % esc(ev["sheet_effective_date"]))
    if ev.get("rules_read"):
        bits.append("%s numbered rules read in full" % esc(ev["rules_read"]))
    if ev.get("sheet_retrieved"):
        bits.append("read %s" % esc(ev["sheet_retrieved"][:10]))
    if ev.get("sheet_sha256"):
        bits.append("PDF SHA-256 <code>%s</code>" % esc(ev["sheet_sha256"][:16]))
    if ev.get("entry_grant_sentences"):
        bits.append('<span class="pill pill-bad">grants further entries: %s</span>'
                    % esc(ev["entry_grant_sentences"][0][:180]))
    out = ['<details class="flds" data-no-search><summary>Rule fields and verdict basis</summary><ul class="fldlist">']
    out.extend(items)
    out.append("</ul>")
    if bits:
        out.append('<p class="muted sm">%s</p>' % " &middot; ".join(bits))
    if row.get("entry_basis"):
        out.append('<p class="muted sm"><b>Basis for the %s label:</b> %s</p>' % (esc(STD["id"]), esc(row["entry_basis"])))
    out.append("</details>")
    return "".join(out)


def money(v):
    if v is None or v == "":
        return ""
    if isinstance(v, (int, float)):
        return "$%s" % format(int(v), ",d")
    return esc(v)


def src_link(url, label=None):
    if not url:
        raise SystemExit("BUILD FAILED: a row has no source link")
    if not url.startswith("https://"):
        raise SystemExit("BUILD FAILED: non-https source %r" % url)
    return '<a class="src" href="%s" target="_blank" rel="noopener">%s</a>' % (
        esc(url), esc(label or "source"))


def fmt_start(row):
    return pretty_time(row["start"])


def event_row_cells(row, with_venue=True):
    cells = []
    if with_venue:
        cells.append("<td>%s</td>" % esc(row["venue"]))
    day = weekday(row["date"]) if row.get("date") else esc(row.get("day") or "")
    cells.append('<td data-order="%s"><span class="nowrap">%s</span><br><span class="muted sm">%s</span></td>'
                 % (esc(row.get("date") or ""),
                    esc(pretty_date(row["date"]) if row.get("date") else (row.get("day") or "")),
                    esc(day)))
    cells.append("<td>%s</td>" % esc(fmt_start(row)))
    cells.append("<td>%s</td>" % esc(row.get("event_no") or ""))
    nm = esc(row["name"])
    if row.get("notes"):
        nm += '<br><span class="muted sm">%s</span>' % esc(row["notes"])
    cells.append('<td class="ename">%s</td>' % nm)
    cells.append('<td class="num">%s</td>' % money(row.get("buyin")))
    cells.append("<td>%s</td>" % esc(row.get("house_fee") or ""))
    cells.append("<td>%s</td>" % esc(row.get("to_prize_pool") or ""))
    g = row.get("guarantee")
    if guarantee_seats(row):
        gcell = '%s <span class="muted sm">(seats, not cash)</span>' % esc(guarantee_seats(row))
    else:
        gcell = money(g) if g not in (None, "") else '<span class="blank">not stated</span>'
    if is_bounty(row):
        gcell += '<br><span class="tag tag-b">bounty pool incl.</span>'
    if row.get("flight") or "Day 2" in (row.get("name") or "") or "Restart" in (row.get("name") or ""):
        gcell += '<br><span class="tag tag-b">flight / restart</span>'
    cells.append('<td class="num">%s</td>' % gcell)
    cells.append('<td class="num">%s</td>' % (ratio_text(row) if rankable(row)
                                              else '<span class="blank">not rankable</span>'))
    cells.append('<td><span class="pill pill-%s">%s</span>%s%s%s</td>' % (
        RULE_CLASS[row["entry_rule"]], esc(RULE_LABEL[row["entry_rule"]]),
        ('<br><span class="quote">%s</span>' % esc(row["rule_excerpt"][:220])) if row.get("rule_excerpt") else "",
        ('<br><span class="muted sm">%s</span>' % esc(row["entry_basis"][:200])) if row.get("entry_basis") else "",
        changed_marker(row)))
    cells.append("<td>%s</td>" % esc(row.get("chips") or ""))
    cells.append("<td>%s</td>" % esc(row.get("levels") or ""))
    cells.append("<td>%s</td>" % (esc(row["late_reg"]) if row.get("late_reg") else '<span class="blank">not stated</span>'))
    cells.append("<td>%s</td>" % src_link(row["source"], row.get("source_label") or "source"))
    last = esc(row.get("last_checked") or row.get("retrieved") or RETRIEVED)
    cell = 'checked %s%s' % (last, (' <span class="muted sm">(first read %s)</span>' % esc(row["retrieved"]))
                             if row.get("last_checked") and row.get("retrieved")
                             and row["last_checked"] != row["retrieved"] else "")
    ch = CHANGED_AT.get(row.get("source"))
    if ch and not row.get("value_changed_at") and not row.get("source_changed_at"):
        cell += ('<br><span class="pill pill-bad" title="This official source changed after the row was read '
                 '(detected %s UTC). Re-verify the row against the Source monitor page before use.">'
                 'source changed</span>' % esc(ch[:10]))
    cells.append('<td class="nowrap">%s%s</td>' % (cell, evidence_html(row)))
    return "".join(cells)


EVENT_HEAD = ("""<tr><th>Venue</th><th>Date</th><th>Start</th><th>#</th><th>Event</th>
<th class="num">Buy-in</th><th>House fee</th><th>To prize pool</th><th class="num">Guarantee</th>
<th class="num">GTD &divide; entry</th><th>Entry rule (standard %s)</th><th>Chips</th><th>Levels</th>
<th>Late registration closes</th><th>Official source</th>
<th>Last checked &middot; rule fields and verdict basis</th></tr>""" % STD["id"])

FILTER_BAR = """
<div class="filters">
  <input type="search" id="q" placeholder="Search events, venues, dates, rule text..." aria-label="Search">
  <label>From <input type="date" id="dfrom"></label>
  <label>To <input type="date" id="dto"></label>
  <select id="fvenue" aria-label="Venue"><option value="">All venues</option>%s</select>
  <select id="fday" aria-label="Day"><option value="">Every day</option>%s</select>
  <select id="frule" aria-label="Entry rule"><option value="">Any entry rule</option>
    <option value="confirmed_single">Confirmed single-entry (%s)</option>
    <option value="multi">Multi-entry: re-entry, add-on or flights</option>
    <option value="unknown">Cap not stated</option>
    <option value="unread">Terms not read</option></select>
  <label class="chk"><input type="checkbox" id="fse"> Confirmed single-entry / freezeout only</label>
  <label class="chk"><input type="checkbox" id="fsemulti"> Hide rows with stated re-entry / flights</label>
  <label class="chk"><input type="checkbox" id="fentry"> Entry rows only (hide Day 2 / final tables)</label>
  <label class="chk"><input type="checkbox" id="frank"> Rankable only: total entry fee AND guarantee confirmed</label>
  <label class="chk"><input type="checkbox" id="fchanged"> Only rows whose official value changed</label>
  <button type="button" id="reset" class="btn tiny">Reset</button>
  <span class="count" id="count"></span>
</div>
"""

SEARCH_BAR = """
<div class="filters">
  <input type="search" id="q" placeholder="%s" aria-label="Search">
  %s
  <button type="button" id="reset" class="btn tiny">Reset</button>
  <span class="count" id="count"></span>
</div>
"""

TABLE_JS_INIT = """<script>document.addEventListener('DOMContentLoaded',function(){initTable('tbl');});</script>"""


def table_shell(rows, head, with_venue=True, empty_msg="No rows match."):
    body = []
    for r in rows:
        search = "%s %s %s %s %s %s" % (r.get("venue", ""), r.get("name", ""), r.get("date", ""),
                                        r.get("day", ""), RULE_LABEL.get(r.get("entry_rule"), ""),
                                        r.get("notes", ""))
        attrs = ['data-search="%s"' % esc(search.lower())]
        attrs.append('data-date="%s"' % esc(r.get("date") or ""))
        attrs.append('data-venue="%s"' % esc(r.get("venue", "")))
        attrs.append('data-rule="%s"' % esc(r.get("entry_rule", "")))
        attrs.append('data-kind="%s"' % esc(r.get("kind", "")))
        attrs.append('data-rankable="%s"' % ("1" if rankable(r) else "0"))
        attrs.append('data-changed="%s"' % ("1" if r.get("value_changed_at") else "0"))
        body.append("<tr %s>%s</tr>" % (" ".join(attrs), event_row_cells(r, with_venue)))
    return ('<div class="tablewrap"><table id="tbl" class="data"><thead>%s</thead><tbody>%s</tbody></table>'
            '<p class="muted" id="empty" hidden>%s</p></div>' % (head, "".join(body), esc(empty_msg)))


# ---------------------------------------------------------------- shell
NAV = [
    ("index.html", "Home"),
    ("pages/executive-summary.html", "Executive summary"),
    ("pages/tournaments.html", "All tournaments"),
    ("pages/single-entry.html", "Single-entry"),
    ("pages/tournaments-double.html", "Multi-entry / advantage"),
    ("pages/schedule.html", "Day schedule"),
    ("pages/hotels.html", "Hotels"),
    ("pages/routes.html", "Walking routes"),
    ("pages/planner.html", "Trip planner"),
    ("pages/verification.html", "Verification"),
    ("pages/requirements.html", "Requirements"),
    ("pages/venues/venetian.html", "Venetian"),
    ("pages/venues/wynn.html", "Wynn"),
    ("pages/venues/others.html", "Other venues"),
    ("pages/questions.html", "Questions"),
    ("pages/suggestions.html", "Suggestions"),
    ("pages/flagged-review.html", "Flagged for review"),
    ("pages/monitor.html", "Source monitor"),
    ("pages/repo-review.html", "Repo review"),
    ("pages/method.html", "Method &amp; sources"),
]


def nav_html(active, depth):
    pre = "../" * depth
    out = []
    for href, label in NAV:
        cur = href.rsplit("/", 1)[-1]
        cls = ' class="active"' if cur == active else ""
        out.append('<a%s href="%s%s">%s</a>' % (cls, pre, href, label))
    return "".join(out)


CSS = """
:root{--bg:#0f1216;--panel:#161b22;--panel2:#1c232c;--line:#2a333d;--text:#e6edf3;--muted:#8b98a5;
--accent:#4fb3ff;--ok:#3fb950;--warn:#d29922;--warn2:#b98033;--bad:#f85149;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:20;background:#10151b;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;padding:10px 16px;font-weight:700}
.logo{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:7px;background:var(--accent);color:#08121b;font-weight:800}
.brand small{font-weight:400;color:var(--muted)}
nav.hnav{display:flex;flex-wrap:wrap;gap:2px;padding:0 10px 8px}
nav.hnav a{padding:5px 9px;border-radius:6px;color:var(--muted);font-size:13.5px;white-space:nowrap}
nav.hnav a:hover{background:var(--panel2);color:var(--text);text-decoration:none}
nav.hnav a.active{background:var(--panel2);color:var(--text);box-shadow:inset 0 0 0 1px var(--line)}
main{max-width:1400px;margin:0 auto;padding:22px 16px 60px}
h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:26px 0 10px}
h3{font-size:16px;margin:18px 0 8px}
p{margin:8px 0}.muted{color:var(--muted)}.sm{font-size:12.5px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px}
.stat .num{font-size:26px;font-weight:700;line-height:1.1}
.stat .lbl{color:var(--muted);font-size:13px;margin-top:4px}
.cards{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}
.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card:hover{border-color:var(--accent);text-decoration:none}
.card h3{margin:0 0 4px;font-size:16px}.card p{margin:0;color:var(--muted);font-size:13.5px}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:var(--panel);
border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin:12px 0}
.filters input[type=search],.filters input[type=date],.filters select,input,select,textarea{
background:#0d1117;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:7px 9px;font:inherit}
.filters input[type=search]{flex:1 1 240px;min-width:180px}
.chk{display:flex;gap:6px;align-items:center;font-size:13.5px;color:var(--muted)}
.btn{display:inline-block;background:var(--accent);color:#08121b;border:0;border-radius:8px;
padding:9px 14px;font-weight:700;cursor:pointer;font:inherit}
.btn.tiny{padding:5px 10px;font-size:13px;font-weight:600}
.btn.ghost{background:transparent;color:var(--text);box-shadow:inset 0 0 0 1px var(--line)}
.count{margin-left:auto;color:var(--muted);font-size:13px}
.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
table.data{border-collapse:collapse;width:100%;font-size:13px}
table.data th,table.data td{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
table.data thead th{position:sticky;top:0;background:#131a21;font-size:12px;text-transform:uppercase;
letter-spacing:.03em;color:var(--muted);cursor:pointer;white-space:nowrap;z-index:2}
table.data tbody tr:hover{background:#1a2129}
td.num{text-align:right;white-space:nowrap}
td.ename{min-width:280px}
.nowrap{white-space:nowrap}
.pill{display:inline-block;padding:2px 7px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap}
.pill-ok{background:rgba(63,185,80,.16);color:#3fb950}
.pill-bad{background:rgba(248,81,73,.15);color:#f85149}
.pill-warn{background:rgba(210,153,34,.15);color:#d29922}
.pill-warn2{background:rgba(185,128,51,.15);color:#c08b3e}
.quote{display:block;color:var(--muted);font-size:11.5px;font-style:italic;max-width:320px}
.tag{display:inline-block;margin-top:3px;padding:1px 6px;border-radius:5px;font-size:11px}
.tag-b{background:rgba(79,179,255,.14);color:#79c0ff}
.blank{color:#6e7c8a;font-style:italic}
.src{font-size:12px}
ul.clean{padding-left:20px}ul.clean li{margin:5px 0}
.kv{display:grid;grid-template-columns:180px 1fr;gap:4px 12px;font-size:14px}
.kv dt{color:var(--muted)}
code{background:#0d1117;padding:1px 5px;border-radius:5px;font-size:13px}
footer{border-top:1px solid var(--line);margin-top:40px;padding:20px 16px;color:var(--muted);font-size:13px}
.warnbox{border-left:3px solid var(--warn);background:rgba(210,153,34,.08);padding:10px 14px;border-radius:0 8px 8px 0;margin:12px 0}
.okbox{border-left:3px solid var(--ok);background:rgba(63,185,80,.08);padding:10px 14px;border-radius:0 8px 8px 0;margin:12px 0}
.badbox{border-left:3px solid var(--bad);background:rgba(248,81,73,.08);padding:10px 14px;border-radius:0 8px 8px 0;margin:12px 0}
.calc{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:end}
.result{background:#0d1117;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-top:12px}
.result .big{font-size:24px;font-weight:700}
.opt{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0;background:#0d1117}
.opt label{display:flex;gap:8px;align-items:flex-start;font-size:14px}
.vhide{display:none}
table.pick td,table.pick th{padding:5px 8px;font-size:13px}
.archive{columns:2;column-gap:24px;font-size:13.5px}
@media(max-width:700px){.kv{grid-template-columns:1fr}.archive{columns:1}}
"""

APP_JS = r"""/* Poker5 - client-side filtering and calculators (root site, session ea99006a;
   extended by 6bc143b9: unified search across every table on a page, date
   selector, confirmed single-entry toggle, <=30-minute walk filter, hotel
   budget/quality filters). No dependencies, no network calls. */
function qsa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function norm(s){return (s||'').toLowerCase();}

function searchText(tr){
  /* Searchable text of a row. Folded evidence blocks are skipped on purpose: they are full of
     negated excerpts ("no re-entry sentence appears"), so searching 're-entry' must not match a
     row merely because the sentence denying it is attached to it. */
  var cached=tr.getAttribute('data-search');
  if(cached!==null && cached!=='') return cached;
  var t='';
  for(var i=0;i<tr.children.length;i++){
    var td=tr.children[i], bits=[];
    for(var j=0;j<td.childNodes.length;j++){
      var n=td.childNodes[j];
      if(n.nodeType===1 && n.hasAttribute && n.hasAttribute('data-no-search')) continue;
      bits.push(n.textContent);
    }
    t+=' '+bits.join(' ');
  }
  return t.toLowerCase();
}

var poker5Bound=false;
function initFilters(){
  if(poker5Bound) return; poker5Bound=true;
  var q=document.getElementById('q'), from=document.getElementById('dfrom'),
      to=document.getElementById('dto'), ven=document.getElementById('fvenue'),
      se=document.getElementById('fse'), mu=document.getElementById('fsemulti'),
      en=document.getElementById('fentry'), walk=document.getElementById('walkfilter'),
      budget=document.getElementById('pbudget'), quality=document.getElementById('pquality'),
      day=document.getElementById('fday'), rule=document.getElementById('frule'),
      rank=document.getElementById('frank'), chg=document.getElementById('fchanged'),
      cnt=document.getElementById('count'), empty=document.getElementById('empty');
  var tables=qsa('table.data');
  var TIER_RANK={"Deluxe":1,"Luxury":2};
  function apply(){
    var needle=norm(q?q.value:''), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', s=se?se.checked:false,
        m2=mu?mu.checked:false, e=en?en.checked:false,
        w=walk?walk.checked:false,
        b=budget&&budget.value!==''?parseFloat(budget.value):null,
        pmin=quality?parseInt(quality.value||'0',10):0,
        dy=day?day.value:'', rl=rule?rule.value:'',
        rk=rank&&rank.checked, cg=chg&&chg.checked,
        shown=0,total=0;
    tables.forEach(function(t){
      qsa('tbody tr',t).forEach(function(tr){
        total++;
        var d=tr.getAttribute('data-date')||'';
        var rule=tr.getAttribute('data-rule')||'';
        var kind=tr.getAttribute('data-kind')||'';
        var ok=true;
        if(needle){
          var txt=tr.getAttribute('data-search');
          txt=norm(txt!==null&&txt!==undefined?txt:searchText(tr));
          if(txt.indexOf(needle)<0) ok=false;
        }
        if(ok&&f&&d&&d<f) ok=false;
        if(ok&&t2&&d&&d>t2) ok=false;
        if(ok&&dy&&d&&d!==dy) ok=false;
        if(ok&&v&&tr.getAttribute('data-venue')!==v) ok=false;
        if(ok&&rl&&rule&&rule!==rl) ok=false;
        if(ok && s && tr.getAttribute('data-rule')!=='confirmed_single') ok=false;
        if(ok&&m2&&rule==='multi') ok=false;
        if(ok&&e&&kind&&kind!=='entry') ok=false;
        if(ok&&rk&&tr.getAttribute('data-rankable')!=='1') ok=false;
        if(ok&&cg&&tr.getAttribute('data-changed')!=='1') ok=false;
        if(ok&&w){
          /* Hide only pairs that are known to exceed 30 minutes. Rows with no
             verified minutes stay visible and stay marked unverified. */
          var m=tr.getAttribute('data-min');
          if(m!==null&&m!==''&&!isNaN(parseFloat(m))&&parseFloat(m)>30) ok=false;
        }
        if(ok&&pmin&&tr.getAttribute('data-tier')!==null){
          if((TIER_RANK[tr.getAttribute('data-tier')]||0)<pmin) ok=false;
        }
        if(ok&&b!==null&&tr.getAttribute('data-cost')!==null&&tr.getAttribute('data-cost')!==''){
          var c=parseFloat(tr.getAttribute('data-cost'));
          if(!isNaN(c)&&c>b) ok=false;
        }
        tr.style.display=ok?'':'none'; if(ok) shown++;
      });
    });
    if(cnt) cnt.textContent=shown+' of '+total+' rows';
    if(empty) empty.hidden=!(shown===0&&total>0);
  }
  if(q) q.addEventListener('input',apply);
  [from,to,day,rule].forEach(function(el){if(el) el.addEventListener('change',apply);});
  if(ven) ven.addEventListener('change',apply);
  [se,mu,en,walk,rank,chg].forEach(function(el){if(el) el.addEventListener('change',apply);});
  [budget,quality].forEach(function(el){if(el){el.addEventListener('input',apply);el.addEventListener('change',apply);}});
  var rst=document.getElementById('reset');
  if(rst) rst.addEventListener('click',function(){
    if(q)q.value=''; if(from)from.value=''; if(to)to.value=''; if(ven)ven.value='';
    if(day)day.value=''; if(rule)rule.value='';
    if(se)se.checked=false; if(mu)mu.checked=false; if(en)en.checked=false;
    if(rank)rank.checked=false; if(chg)chg.checked=false;
    if(walk)walk.checked=false; if(budget)budget.value=''; if(quality)quality.value='';
    apply();});
  /* click-to-sort per table */
  tables.forEach(function(t){
    qsa('thead th',t).forEach(function(th,i){
      th.addEventListener('click',function(){
        var tb=t.tBodies[0], arr=qsa('tr',tb);
        var asc=th.getAttribute('data-asc')!=='1';
        qsa('thead th',t).forEach(function(o){o.removeAttribute('data-asc');});
        th.setAttribute('data-asc',asc?'1':'0');
        arr.sort(function(a,b){
          var A=a.children[i]||a.children[a.children.length-1],
              B=b.children[i]||b.children[b.children.length-1];
          var ka=A.getAttribute('data-order'); var kb=B.getAttribute('data-order');
          var va=ka!==null?ka:A.textContent.trim(), vb=kb!==null?kb:B.textContent.trim();
          var na=parseFloat(String(va).replace(/[^0-9.\-]/g,'')), nb=parseFloat(String(vb).replace(/[^0-9.\-]/g,''));
          var cmp=(!isNaN(na)&&!isNaN(nb))?na-nb:String(va).localeCompare(String(vb));
          return asc?cmp:-cmp;});
        arr.forEach(function(r){tb.appendChild(r);});});});
  });
  apply();
}
/* backwards-compatible name used by inline page scripts */
function initTable(){initFilters();}

/* ---- hotel true nightly cost + dated rate log ---- */
var RATE_KEY='poker5.ratelog.v1';
function num(el){var v=parseFloat((el&&el.value||'').replace(/[^0-9.\-]/g,''));return isNaN(v)?0:v;}
function rateLog(){try{return JSON.parse(localStorage.getItem(RATE_KEY)||'[]');}catch(e){return [];}}
function saveRateLog(l){try{localStorage.setItem(RATE_KEY,JSON.stringify(l));}catch(e){}}
function renderRateLog(){
  var box=document.getElementById('ratelog'); if(!box) return;
  var l=rateLog();
  if(!l.length){box.innerHTML='<p class="muted sm">No dated quotes recorded in this browser yet. Add one above and it is stored here only. The researched, source-linked captures are in the table above.</p>';return;}
  var h='<table class="data"><thead><tr><th>Recorded</th><th>Hotel</th><th>Dates</th><th class="num">Rate/night</th><th class="num">Resort fee</th><th class="num">Tax %</th><th class="num">True /night</th><th class="num">Stay total</th><th>Source</th><th></th></tr></thead><tbody>';
  l.slice().reverse().forEach(function(r,i){
    h+='<tr><td class="nowrap">'+r.ts+'</td><td>'+r.hotel+'</td><td class="nowrap">'+r.dates+'</td>'+
       '<td class="num">$'+r.rate.toFixed(2)+'</td><td class="num">$'+r.fee.toFixed(2)+'</td>'+
       '<td class="num">'+r.tax.toFixed(2)+'%</td><td class="num">$'+r.truenight.toFixed(2)+'</td>'+
       '<td class="num">$'+r.total.toFixed(2)+'</td>'+
       '<td>'+(r.src?'<a class="src" href="'+r.src+'" target="_blank" rel="noopener">booking link</a>':'<span class="blank">-</span>')+'</td>'+
       '<td><button class="btn tiny ghost" data-del="'+i+'">remove</button></td></tr>';
  });
  h+='</tbody></table>'; box.innerHTML=h;
  qsa('[data-del]',box).forEach(function(b){b.addEventListener('click',function(){
    var l=rateLog(); var idx=l.length-1-parseInt(b.getAttribute('data-del'),10);
    l.splice(idx,1); saveRateLog(l); renderRateLog();});});
}
function initHotels(){
  var f=document.getElementById('hcalc'); if(!f) return;
  function calc(){
    var rate=num(document.getElementById('hrate')), fee=num(document.getElementById('hfee')),
        tax=num(document.getElementById('htax')), nights=num(document.getElementById('hnights'))||1;
    var taxable=rate+fee, t=taxable*(1+tax/100);
    var el=document.getElementById('hres');
    if(el) el.innerHTML='<div><span class="muted">Nightly: rate $'+rate.toFixed(2)+' + resort fee $'+fee.toFixed(2)+
      ' = $'+taxable.toFixed(2)+'; tax at '+tax.toFixed(2)+'% = $'+(taxable*tax/100).toFixed(2)+'</span></div>'+
      '<div class="big">True cost per night: $'+t.toFixed(2)+'</div>'+
      '<div class="muted">'+nights+' night(s): $'+(t*nights).toFixed(2)+'</div>';
    return {rate:rate,fee:fee,tax:tax,nights:nights,truenight:t,total:t*nights};
  }
  ['hrate','hfee','htax','hnights'].forEach(function(id){var e=document.getElementById(id); if(e) e.addEventListener('input',calc);});
  calc();
  var save=document.getElementById('hsave');
  if(save) save.addEventListener('click',function(){
    var r=calc(); if(!r.rate) {alert('Enter the nightly rate you saw on the official booking link.');return;}
    var l=rateLog();
    l.push({ts:new Date().toISOString().slice(0,16).replace('T',' ')+'Z',
      hotel:document.getElementById('hhotel').value,
      dates:(document.getElementById('hin').value||'?')+' to '+(document.getElementById('hout').value||'?'),
      rate:r.rate,fee:r.fee,tax:r.tax,nights:r.nights,truenight:r.truenight,total:r.total,
      src:document.getElementById('hsrc').value||''});
    saveRateLog(l); renderRateLog();});
  renderRateLog();
  var walk=document.getElementById('walkfilter');
  if(walk) walk.addEventListener('change',function(){
    qsa('#routetable tbody tr').forEach(function(tr){
      var m=tr.getAttribute('data-min');
      if(walk.checked && m!=='' && m!==null && parseFloat(m)>30) tr.style.display='none';
      else tr.style.display='';
    });});
  var rec=document.getElementById('walkrecord');
  if(rec) rec.addEventListener('click',function(){
    var mins=parseFloat(document.getElementById('walkmins').value);
    if(isNaN(mins)){alert('Enter the number of minutes you measured.');return;}
    var key='poker5.walk.'+document.getElementById('walkpair').value;
    try{localStorage.setItem(key,JSON.stringify({minutes:mins,at:new Date().toISOString()}));}catch(e){}
    var tr=document.querySelector('#routetable tr[data-pair="'+document.getElementById('walkpair').value+'"]');
    if(tr){tr.setAttribute('data-min',mins); tr.children[3].innerHTML='<b>'+mins+' min</b><br><span class="muted sm">you measured this</span>';}
  });
}

/* ---- day schedule: the bar above the cards filters CARDS, not a table ---- */
function initDays(){
  var nav=document.getElementById('daynav'); if(!nav) return;
  var cards=qsa('.daycard');
  var q=document.getElementById('q'), from=document.getElementById('dfrom'), to=document.getElementById('dto'),
      ven=document.getElementById('fvenue'), rule=document.getElementById('frule'),
      se=document.getElementById('fse'), rank=document.getElementById('frank'),
      chg=document.getElementById('fchanged'), win=document.getElementById('winonly');
  var picked='';
  function apply(){
    var needle=norm(q?q.value:''), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', rl=rule?rule.value:'', s=se&&se.checked,
        rk=rank&&rank.checked, cg=chg&&chg.checked, only=win&&win.checked, shown=0;
    cards.forEach(function(c){
      var d=c.getAttribute('data-date')||'';
      var ok=true;
      if(only && c.getAttribute('data-outside')) ok=false;
      if(ok && picked && d!==picked) ok=false;
      if(ok && f && d<f) ok=false;
      if(ok && t2 && d>t2) ok=false;
      var rows=0;
      qsa('tbody tr',c).forEach(function(tr){
        var rok=true;
        if(needle && norm(tr.getAttribute('data-search')||'').indexOf(needle)<0) rok=false;
        if(rok && v && tr.getAttribute('data-venue')!==v) rok=false;
        if(rok && rl && tr.getAttribute('data-rule')!==rl) rok=false;
        if(rok && s && tr.getAttribute('data-rule')!=='confirmed_single') rok=false;
        if(rok && rk && tr.getAttribute('data-rankable')!=='1') rok=false;
        if(rok && cg && tr.getAttribute('data-changed')!=='1') rok=false;
        tr.style.display=rok?'':'none'; if(rok) rows++;
      });
      if(ok && (needle||v||rl||s||rk||cg) && rows===0) ok=false;
      c.style.display=ok?'':'none'; if(ok) shown++;
    });
    qsa('[data-day]',nav).forEach(function(bt){
      bt.className='btn tiny'+((bt.getAttribute('data-day')||'')===picked?' active':'');});
    var cnt=document.getElementById('count');
    if(cnt) cnt.textContent=shown+' of '+cards.length+' days';
  }
  nav.addEventListener('click',function(e){
    var bt=e.target.closest?e.target.closest('[data-day]'):null; if(!bt) return;
    picked=bt.getAttribute('data-day')||'';
    var dp=document.getElementById('fday'); if(dp) dp.value=picked;
    apply();});
  var dp=document.getElementById('fday');
  if(dp) dp.addEventListener('change',function(){picked=dp.value; apply();});
  [q,from,to,ven,rule,se,rank,chg,win].forEach(function(el){
    if(el) el.addEventListener(el.type==='search'||el.type==='text'?'input':'change',apply);});
  apply();
}

/* ---- hotels: the brief's budget ceiling and quality floor, applied to the itemized table ---- */
function initHotels2(){
  var ceil=document.getElementById('bceil'), fl=document.getElementById('bfloor'),
      tbl=document.getElementById('hitems'), sel=document.getElementById('hsearch'),
      out=document.getElementById('bcost');
  if(!tbl) return;
  function apply(){
    var c=parseFloat((ceil&&ceil.value||'').replace(/[^0-9.\-]/g,'')), f=fl?fl.value:'', w=sel?sel.value:'', n=0;
    var all=qsa('tbody tr',tbl);
    all.forEach(function(tr){
      var ok=true, v=tr.getAttribute('data-ceil')||'';
      if(w && norm(tr.children[0].textContent).indexOf(norm(w))<0) ok=false;
      if(ok && f && tr.getAttribute('data-tier')!==f) ok=false;
      /* a hotel with no official rate can never be proven inside a budget: when a ceiling is set it
         is hidden, never assumed to fit */
      if(ok && !isNaN(c)){ if(v===''){ ok=false; } else if(parseFloat(v)>c){ ok=false; } }
      tr.style.display=ok?'':'none'; if(ok) n++;
    });
    if(out) out.textContent=n+' of '+all.length+' hotels match'+(isNaN(c)?'':' a ceiling of $'+c.toFixed(2))+
      (f?' and the '+f+' quality floor':'')+'. Hotels with no official nightly rate cannot be proven '
      'inside a ceiling, so they are hidden while one is set.';
  }
  [ceil,sel].forEach(function(el){if(el) el.addEventListener('input',apply);});
  if(fl) fl.addEventListener('change',apply);
  apply();
}

/* ---- trip planner ---- */
/* status chips on the requirements page: they drive the page's own search box, so no
   query-string link is needed and the site's link checker stays honest. */
function initQueryChips(){
  qsa('[data-q]').forEach(function(b){
    b.addEventListener('click',function(){
      var q=document.getElementById('q'); if(!q) return;
      q.value=b.getAttribute('data-q')||'';
      q.dispatchEvent(new Event('input',{bubbles:true}));
      q.focus();
    });
  });
}

function initPlanner(){
  var box=document.getElementById('picks'); if(!box) return;
  var out=document.getElementById('ptotal');
  function total(){
    var buy=0,entries=0,hasInvalidBuyin=false;
    qsa('input[type=checkbox][data-buyin]',box).forEach(function(c){
      if(!c.checked) return;
      var b=Number(c.getAttribute('data-buyin'));
      if(!Number.isFinite(b)||b<=0){hasInvalidBuyin=true;return;}
      buy+=b; entries++;
    });
    var rateField=document.getElementById('ptrue');
    var nightsField=document.getElementById('pnights');
    var hotel=rateField&&rateField.value.trim()!==''?Number(rateField.value):NaN;
    var nights=nightsField&&nightsField.value.trim()!==''?Number(nightsField.value):NaN;
    /* Parking and the mandatory stay fees come from the official pages, so they are added here
       instead of being left for a reader to remember. If the hotel figure in use already includes
       the stay (a dated checkout capture), parking is the only thing added on top. */
    var panel=document.getElementById('pcalc');
    var parkBox=document.getElementById('ppark');
    var perNight=function(k){return panel&&panel.getAttribute('data-'+k)?Number(panel.getAttribute('data-'+k)):0;};
    var quote=document.getElementById('pquote');
    var opt=quote&&quote.selectedIndex>=0?quote.options[quote.selectedIndex]:null;
    var includesStay=!!(opt&&opt.getAttribute('data-includes')==='1');
    var parkOn=!!(parkBox&&parkBox.checked);
    var perNightPark=parkOn?perNight('park'):0;
    var feeTaxed=perNight('fee')*(1+perNight('tax')/100);
    var knownNight=feeTaxed+perNightPark;
    var hotelComplete=Number.isFinite(hotel)&&hotel>0&&Number.isFinite(nights)&&nights>0;
    var nightsN=Number.isFinite(nights)&&nights>0?nights:NaN;
    var hotelTotal=hotelComplete?(hotel+perNightPark)*nightsN:null;
    var tripComplete=hotelComplete&&entries>0&&!hasInvalidBuyin;
    var grandTotal=tripComplete?buy+hotelTotal:null;
    var srcNote=opt&&opt.value!=='manual'?' <span class="muted sm">from '+(opt.getAttribute('data-label')||'')+'</span>':'';
    if(out) out.innerHTML='<div>Selected entries: <b>'+entries+'</b> &nbsp; Buy-ins total: <b>$'+buy.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2})+'</b></div>'+
      '<div>Hotel: '+(Number.isFinite(nights)?nights:'—')+' night(s) &times; '+(hotelComplete?'$'+hotel.toFixed(2)+' true cost / night'+srcNote:'<span class="blank">true nightly cost not confirmed</span>')+
      (hotelComplete&&parkOn?' + parking $'+perNightPark.toFixed(2)+'/night':'')+
      ' = <b>'+(hotelComplete?'$'+hotelTotal.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2}):'Incomplete')+'</b></div>'+
      (includesStay?'<div class="muted sm">The hotel figure in use already includes the room, the resort fee and the tax for the stay it was captured for'+(parkOn?', so only parking is added on top':'. Nothing is added on top')+'.</div>':'')+
      (!includesStay&&hotelComplete?'<div class="muted sm">This hotel figure is a room-rate component only: add the resort fee and tax (or use the dated capture) before treating it as the whole nightly cost.</div>':'')+
      '<div class="big">Estimated trip cost: '+(grandTotal===null?'Incomplete':'$'+grandTotal.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2})+(opt&&opt.getAttribute('data-datematched')==='0'?' <span class="pill pill-warn">not date-matched to your window</span>':''))+'</div>'+
      (grandTotal===null&&Number.isFinite(nightsN)?'<div>Mandatory stay cost that IS verified: $'+knownNight.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+' / night &times; '+nightsN+' = <b>$'+(knownNight*nightsN).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+'</b> <span class="muted sm">resort fee + '+perNight('tax')+'% tax'+(parkOn?' + parking':'')+'; the room rate is the only missing term</span></div>':'')+
      '<div class="muted sm">Formula: selected entries &times; their listed buy-ins + nights &times; true hotel cost. One buy-in is counted per selected event. The candidate events below do not have confirmed single-entry caps.</div>'+
      (opt&&opt.value==='capture'?'<p class="warnbox">Not date-matched: the auto capture is an itemized total for the dates printed in the dated log, not for your window. It is shown so the scale of the hotel side is visible; it is not a quote for your stay.</p>':'')+
      (hotelComplete?'':'<p class="warnbox">Incomplete. No date-specific room quote is currently recorded; the calculator shows the verified mandatory stay cost, and the trip total closes only when a dated nightly total is recorded in the hotel rate log.</p>')+
      (entries===0?'<p class="muted sm">Select at least one event to include its buy-in in the estimate.</p>':'')+
      (hasInvalidBuyin?'<p class="warnbox">A selected event has no valid buy-in. The trip total cannot be completed.</p>':'');
  }
  box.addEventListener('change',total);
  var pq=document.getElementById('pquote');
  if(pq) pq.addEventListener('change',function(){
    var o=pq.options[pq.selectedIndex], f=document.getElementById('ptrue');
    var v=o.getAttribute('data-pernight');
    if(f){ if(v&&v!=='null'){f.value=v;f.readOnly=true;} else {f.value='';f.readOnly=false;} }
    total();
  });
  var pb=document.getElementById('ppark'); if(pb) pb.addEventListener('change',total);
  ['ptrue','pnights'].forEach(function(id){var e=document.getElementById(id); if(e) e.addEventListener('input',total);});
  total();
}

/* ---- suggestions: choose a path ---- */
function initSuggestions(){
  var box=document.getElementById('sug'); if(!box) return;
  var out=document.getElementById('spicked');
  function render(){
    var c=qsa('input[type=radio]:checked',box);
    if(!out) return;
    if(!c.length){out.innerHTML='<p class="muted">Pick one option per suggestion to build your change list.</p>';return;}
    out.innerHTML='<h3>Your chosen path</h3><ol class="clean">'+c.map(function(r){
      return '<li><b>'+r.getAttribute('data-title')+'</b>: '+r.getAttribute('data-label')+'</li>';}).join('')+'</ol>'+
      '<p class="muted sm">Nothing on this site changes until you ask for it. Copy this list into a request.</p>';
  }
  box.addEventListener('change',render); render();
}

document.addEventListener('DOMContentLoaded',function(){
  /* landing-page search hands its term over as ?q=...; pre-fill the page's search box and filter */
  try{ var qp=new URLSearchParams(location.search).get('q'); var qb=document.getElementById('q');
    if(qp && qb){ qb.value=qp; qb.dispatchEvent(new Event('input')); } }catch(e){}
  initFilters(); initHotels(); initHotels2(); initDays(); initPlanner(); initSuggestions(); initQueryChips();
});
"""


def page(title, body, active, depth=1, extra_head=""):
    pre = "../" * depth
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s | Poker5</title>
<link rel="stylesheet" href="%sassets/css/style.css">
<script defer src="%sassets/app.js"></script>
%s</head><body>
<header><div class="brand"><span class="logo">P5</span> Poker5
<small>Las Vegas Strip poker trip planner &middot; source-verified</small></div>
<nav class="hnav">%s</nav></header>
<main>
%s
</main>
<footer>
<p><b>Poker5</b> is an independent planning tool. It is not affiliated with any casino, poker room or hotel.</p>
<p>Every table value links to the official page it was read from (retrieved %s). Values that could not be confirmed
are left blank and listed on the <a href="%spages/flagged-review.html">Flagged for review</a> page.
Nothing is inferred, estimated or filled in. Room rates change daily; confirm before booking or playing. Must be 21+.
If gambling is a problem, call the Nevada Problem Gambling HelpLine 1-800-522-4700.</p>
</footer></body></html>
""" % (esc(title), pre, pre, extra_head, nav_html(active, depth), body, esc(RETRIEVED), pre)


WROTE = {}


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)
    WROTE[rel.replace(os.sep, "/")] = path


# ---------------------------------------------------------------- stats
VEN_ENTRIES = [r for r in VEN if r["kind"] == "entry"]
WPT_ENTRIES = [r for r in WPT if r["kind"] == "entry"]
OTH_ENTRIES = [r for r in OTH if r["kind"] == "entry"]
CANDIDATES = [r for r in ALL_EVENTS if r["kind"] == "entry" and r["entry_rule"] == "unknown"]
CONFIRMED = [r for r in ALL_EVENTS if r["entry_rule"] == "confirmed_single"]
MULTI = [r for r in ALL_EVENTS if r["entry_rule"] == "multi"]
UNREAD = [r for r in ALL_EVENTS if r["entry_rule"] == "unread"]
SATS = [r for r in ALL_EVENTS if r["kind"] == "satellite"]
VENUE_OPTS = "".join('<option value="%s">%s</option>' % (esc(v["name"]), esc(v["name"]))
                     for v in [x for x in VENUES if x["key"] in ("venetian", "wynn", "caesars", "southpoint")])
_all_days = sorted({r.get("date") for r in ALL_EVENTS if r.get("date")})
DAY_OPTS = "".join('<option value="%s">%s %s</option>' % (d, pretty_date(d), weekday(d)) for d in _all_days)
FILTER_ARGS = (VENUE_OPTS, DAY_OPTS, STD["id"])


# ---------------------------------------------------------------- pages
DSE_MARQUEE = [
    ("$800 No Limit Hold'em", "$500,000 GTD", "Dec 3-6", ""),
    ("$2,200 No Limit Hold'em", "$1,000,000 GTD", "Dec 12-14",
     "PokerAtlas Championship Title Event; final table live streamed Dec 14 at 12pm"),
    ("$1,100 No Limit Hold'em Seniors (50+)", "$300,000 GTD", "Dec 13-15", "Must be 50+ years of age to participate"),
    ("$1,100 No Limit Hold'em", "$500,000 GTD", "Dec 17-20", ""),
    ("$600 No Limit Hold'em", "$150,000 GTD", "Dec 20-23", ""),
]
DSE_SERIES_PAGE = ("https://www.venetianlasvegas.com/resort/casino/poker/"
                   "deepstack-extravaganza-poker-tournament.html")


def marquee_html():
    out = ['<div class="panel"><h2>DeepStack Extravaganza IV headline events</h2>'
           '<p class="muted sm">From the official Venetian DeepStack series page: the series runs 16 November - '
           '23 December 2026 with "more than $3.6 million in guaranteed tournament prize pools".</p>'
           '<div class="tablewrap"><table class="data"><thead><tr><th>Event</th><th>Guarantee</th><th>Dates</th>'
           '<th>Note</th><th>Source</th></tr></thead><tbody>']
    for name, gtd, dates, note in DSE_MARQUEE:
        out.append('<tr><td><b>%s</b></td><td class="num">%s</td><td class="nowrap">%s</td><td class="sm">%s</td>'
                   '<td>%s</td></tr>' % (esc(name), esc(gtd), esc(dates), esc(note),
                                         src_link(DSE_SERIES_PAGE, "official series page")))
    out.append("</tbody></table></div></div>")
    return "".join(out)


def build_index():
    cards = [("pages/executive-summary.html", "Executive summary", "The short version: what is confirmed, what is not, and what to do next."),
             ("pages/tournaments.html", "All tournaments", "Every verified row from the Venetian, Wynn/WPT and Caesars, with its official source."),
             ("pages/single-entry.html", "Single-entry", "Events confirmed against their own structure sheet under standard S1 - and the standing flags."),
             ("pages/tournaments-double.html", "Multi-entry", "Re-entry, add-on, multi-flight and paid-advantage events, kept separate."),
             ("pages/schedule.html", "Day schedule", "One primary event per day plus a conditional fallback, with the overlap check."),
             ("pages/hotels.html", "Hotels", "Resort fees, official booking links, dated rate log and true nightly cost."),
             ("pages/routes.html", "Walking routes", "Hotel to poker room, with the 30-minute filter."),
             ("pages/planner.html", "Trip planner", "Entries &times; buy-ins + nights &times; true hotel cost."),
             ("pages/venues/venetian.html", "Venetian", "DeepStack Extravaganza IV, 16 Nov - 23 Dec 2026."),
             ("pages/venues/wynn.html", "Wynn", "WPT World Championship festival, 27 Nov - 21 Dec 2026."),
             ("pages/venues/others.html", "Other venues", "Caesars Palace, Horseshoe, Resorts World, South Point and the rooms we could not verify."),
             ("pages/requirements.html", "Requirements", "Every line of the brief, its status on this site, and the one thing blocking each gap."),
             ("pages/questions.html", "Questions", "What we know, what is missing, and how to find it."),
             ("pages/suggestions.html", "Suggestions", "Pick a path before anything is changed."),
             ("pages/verification.html", "Verification log",
              "The standard behind every verdict, the rows re-read field by field, the rows moved out of single-entry, and the hotel figures that were verified."),
             ("pages/flagged-review.html", "Flagged for review", "%d irregularities and unverified values, each with its source." % len(FLAGS)),
             ("pages/method.html", "Method &amp; sources", "How every value was read, and the complete source ledger.")]
    body = []
    body.append("<h1>Las Vegas Strip poker trip planner</h1>")
    body.append('<form class="filters" action="pages/tournaments.html" method="get" id="landsearch" role="search">'
             '<input id="landq" name="q" class="search" type="search" placeholder="Search events, venues, dates, rule text, hotels..." aria-label="Search the site">'
             '<select id="landpage" aria-label="Search in" onchange="this.form.action=this.value">'
             '<option value="pages/tournaments.html">All tournaments</option>'
             '<option value="pages/single-entry.html">Single-entry</option>'
             '<option value="pages/tournaments-double.html">Multi-entry / advantage</option>'
             '<option value="pages/schedule.html">Day schedule</option>'
             '<option value="pages/hotels.html">Hotels</option>'
             '<option value="pages/verification.html">Verification log</option>'
             '<option value="pages/flagged-review.html">Flagged for review</option>'
             '</select><button type="submit">Search</button></form>')
    body.append('<p class="muted sm">Search runs inside the chosen table page (every table on that page is filtered). Pick the page with the drop-down.</p>')
    body.append('<p class="muted">Source-verified &middot; retrieved %s &middot; Venetian DeepStack Extravaganza IV and the WPT World Championship at Wynn</p>' % esc(RETRIEVED))
    body.append('<div class="grid">')
    for n, l in (("37", "Venetian structure sheets read"),
                    (str(len(ALL_EVENTS)), "Verified schedule rows"),
                    (str(len(CONFIRMED)), "Confirmed single-entry events (standard S1)"),
                    (str(len(UNREAD)), "Rows whose entry terms were not read"),
                    (str(len(MULTI)), "Rows that are re-entry / multi-flight"),
                    (str(len(FLAGS)), "Items flagged for review")):
        body.append('<div class="stat"><div class="num">%s</div><div class="lbl">%s</div></div>' % (n, esc(l)))
    body.append("</div>")
    body.append('<div class="badbox"><b>The single-entry headline: %d events are confirmed single-entry under '
                'standard S1.</b> All 37 official Venetian structure sheets were read on %s. Each confirmed row\'s '
                'own sheet was read in full, names that event number, is a one-day entry row with a stated '
                'registration close, and grants no re-entry, rebuy, add-on or purchased-stack path in its numbered '
                'rules - the sheet excerpt and retrieval date are on the row. The honest limit stays published: '
                '<b>no sheet states "one entry only" in words</b>, so confirmation means <i>the published rules grant '
                'no second entry</i>, not that the house promises a freezeout (flags '
                '<a href="pages/flagged-review.html">F01 and F47</a> stay open). Every WPT / Wynn event whose terms '
                'were read permits re-entry; the %d rows whose terms were not read keep an explicit '
                '<i>unverified</i> label.</div>' % (len(CONFIRMED), esc(RETRIEVED), len(UNREAD)))
    body.append('<div class="panel"><h2>Recommended window (chosen for you, changeable everywhere)</h2>'
                '<div class="kv"><dt>Check in</dt><dd>%s</dd><dt>Check out</dt><dd>%s</dd>'
                '<dt>Nights</dt><dd>%d</dd><dt>Why this window</dt><dd>%s</dd></div></div>'
                % (esc(pretty_date(TRIP["check_in"])), esc(pretty_date(TRIP["check_out"])),
                   TRIP["nights"], esc(TRIP["rationale"])))
    body.append('<div class="cards">')
    for href, label, blurb in cards:
        body.append('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>' % (href, label, esc(blurb)))
    body.append("</div>")
    body.append('<div class="panel"><h2>What this site will not do</h2><ul class="clean">'
                '<li>It will not call an event single-entry unless its own structure sheet was read in full and its published rules grant no second entry (standard S1) - and it never hides that no sheet states "one entry only" in words.</li>'
                '<li>It will not fill in a guarantee, a rate or a walking time that no official source states.</li>'
                '<li>It will not rank events until the total entry fee and the guarantee are both confirmed.</li>'
                '</ul></div>')
    body.append(archive_block(0))
    write("index.html", page("Las Vegas Strip poker trip planner", "".join(body), "index.html", 0))


ARCHIVE_SKIP = {"pages", "assets", "data", "scripts", "work", "tools"}


def tracked_top_dirs():
    """Top-level names with at least one file committed under them.

    Returns None when git is unavailable (then every folder is kept, the
    behaviour before this filter existed).
    """
    import subprocess
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files"],
                             capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return {line.split("/", 1)[0] for line in out.stdout.splitlines() if "/" in line}


def archive_entries():
    """Auto-discover every other session's published folder so none is lost.

    "Published" means the folder is committed to the repository: a gitignored
    build-output folder (e.g. _site-aa83f1e1/, written by another session's
    build script) exists only in one workspace and must not be linked from
    the published pages, or a clean checkout would contain broken links
    (this is exactly how the daily-scrape validation step failed in CI while
    passing locally).
    """
    out = []
    tracked = tracked_top_dirs()
    for name in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, name)
        if not os.path.isdir(path) or name.startswith(".") or name in ARCHIVE_SKIP:
            continue
        if tracked is not None and name not in tracked:
            continue
        if not os.path.exists(os.path.join(path, "index.html")):
            continue
        if tracked is not None and name not in tracked:
            continue
        out.append(("%s/index.html" % name, name))
    return out


def archive_block(depth):
    pre = "../" * depth
    entries = archive_entries()
    items = "".join('<li><a href="%s%s">%s</a></li>' % (pre, h, esc(t)) for h, t in entries)
    return ('<div class="panel"><h2>Earlier sessions (kept, not edited)</h2>'
            '<p class="muted">%d agent sessions built dashboards or planners in their own folders. They are '
            'preserved exactly as they were and are not part of this verified root site. Use the pages above for '
            'current answers.</p><div class="archive"><ul class="clean">%s</ul></div></div>'
            % (len(entries), items))


def build_tournaments():
    body = ["<h1>All verified tournaments</h1>",
            '<p class="muted">%d rows: %d Venetian DeepStack Extravaganza IV, %d WPT World Championship festival '
            'at Wynn, %d from other rooms. Every row links to the official page or PDF it was read from.</p>'
            % (len(ALL_EVENTS), len(VEN), len(WPT), len(OTH))]
    body.append('<div class="warnbox"><b>Reading the entry-rule column.</b> '
                '<span class="pill pill-ok">Confirmed single-entry</span> means an official source states a one-entry limit. '
                '<span class="pill pill-bad">Multi-entry</span> means the official text allows re-entry, an add-on, or more than one starting flight. '
                '<span class="pill pill-warn">Entry cap not stated</span> means the official structure sheet is silent - that is not evidence of a freezeout. '
                '<span class="pill pill-warn2">Entry terms not read</span> means this audit did not read that event\'s terms.</div>')
    body.append(FILTER_BAR % FILTER_ARGS)
    body.append(table_shell(ALL_EVENTS, EVENT_HEAD))
    body.append('<p class="muted sm">Guarantee &divide; entry fee is a descriptive ratio, not a forecast. '
                'Bounty events are tagged because their published guarantee includes the bounty pool.</p>')
    write("pages/tournaments.html", page("All tournaments", "".join(body), "tournaments.html", 1,
                                         TABLE_JS_INIT))


def build_single():
    body = ["<h1>Single-entry tournaments</h1>"]
    body.append('<div class="badbox"><b>Confirmed single-entry events (standard S1): %d.</b> Every official '
                'structure sheet published for the Venetian DeepStack Extravaganza IV (all 37) was read on %s. '
                'Each confirmed row was verified from its own sheet read in full: the sheet names that event number, is a one-day entry row '
                'with a stated registration close, and grants no re-entry, rebuy, add-on or purchased-stack path in '
                'its numbered rules - the sheet excerpt and retrieval date are on the row, and the tests are '
                're-derivable from the stored fields (see the <a href="verification.html">Verification log</a>). '
                'Every WPT World Championship event whose terms were read permits re-entry - "unlimited re-entry", '
                'or "one entry and one re-entry per starting flight" for the Prime Championship.</div>'
                % (len(CONFIRMED), esc(RETRIEVED)))
    body.append(SEARCH_BAR % ("Search single-entry rows...", ""))
    body.append("<h2>1. Confirmed single-entry under standard S1 (%d rows)</h2>" % len(CONFIRMED))
    if CONFIRMED:
        body.append(table_shell(CONFIRMED, EVENT_HEAD))
    else:
        body.append('<div class="panel"><p><b>None.</b> No structure sheet read during this session meets the '
                    'published standard. Nothing is listed here rather than listing something unverified.</p></div>')
    body.append("<h2>2. What confirmation means here - and what it does not</h2>")
    body.append('<div class="panel"><p><b>No official source in this series states "one entry only" in words.</b> '
                'Confirmation under standard S1 therefore means <i>the published rules grant no second entry</i> - '
                'the sheet own numbered rule list contains no re-entry, re-buy, add-on, buy-back, subsequent or '
                'additional buy-in, or purchased or alternate stack provision - not that the house promises a '
                'freezeout. Every sheet also carries "Management reserves the right to cancel or change the '
                'tournament". Flags <a href="flagged-review.html">F01</a> and <a href="flagged-review.html">F47</a> '
                'stay open for exactly that gap. Before you rely on a row, ask the poker room to confirm the entry '
                'cap in writing.</p></div>')
    body.append("<h2>3. Rows this page does not cover</h2>")
    body.append('<p class="muted">%d rows fail the test for a stated reason - multiple starting flights, an explicit '
                're-entry or add-on rule, a satellite that pays seats instead of cash, or an age/entry restriction. '
                'They are listed on the <a href="tournaments-double.html">Multi-entry page</a>. Another %d rows are '
                'outside the Venetian series and their entry terms were not read individually; they keep an explicit '
                '<i>unverified</i> label on the <a href="tournaments.html">All tournaments</a> page and are not '
                'presented as open single-entry events.</p>' % (len(MULTI), len(UNREAD)))
    body.append(archive_block(1))
    write("pages/single-entry.html", page("Single-entry tournaments", "".join(body), "single-entry.html", 1,
                                          TABLE_JS_INIT))


def build_multi():
    body = ["<h1>Multi-entry and paid-advantage events</h1>"]
    body.append('<p class="muted">The brief asks for these to be kept in a separate section: events where a player '
                'can buy in more than once, add on, or buy an advantage with money. %d rows carry an official '
                're-entry / add-on / multi-flight statement. A further %d rows have entry terms this audit did not '
                'read individually; they are listed at the bottom and flagged.</p>' % (len(MULTI), len(UNREAD)))
    body.append("<h2>Official re-entry, add-on or multi-flight text</h2>")
    body.append(FILTER_BAR % FILTER_ARGS)
    body.append(table_shell(MULTI, EVENT_HEAD))
    body.append("<h2>Entry terms not read individually (%d rows)</h2>" % len(UNREAD))
    body.append('<p class="muted">Mostly WPT World Championship festival events. The official structures PDF was '
                'read for 13 of the festival\'s events and every one of them permits re-entry, but this site does '
                'not copy a rule from one event onto another. These rows stay unverified.</p>')
    body.append(table_shell(UNREAD, EVENT_HEAD))
    body.append("<h2>Satellites (%d rows)</h2>" % len(SATS))
    body.append('<p class="muted">Satellites pay seats into a target event rather than a cash prize pool, so they '
                'are not comparable on guarantee &divide; entry fee.</p>')
    body.append(table_shell(SATS, EVENT_HEAD))
    write("pages/tournaments-double.html", page("Multi-entry and paid-advantage events", "".join(body),
                                                "tournaments-double.html", 1, TABLE_JS_INIT))


SEQ_JS = r"""<script>
/*SEQ-BEGIN*/
function seqCheck(evs, D) {
  var cannot = [], unknown = 0, ok = 0;
  for (var i = 0; i < evs.length; i++) {
    for (var j = i + 1; j < evs.length; j++) {
      var a = evs[i], b = evs[j];
      // a then b is possible iff b's late-registration close is not before a's earliest finish (a.s + D).
      var ab = (b.l === null) ? null : (b.l >= a.s + D);
      var ba = (a.l === null) ? null : (a.l >= b.s + D);
      if (ab === true || ba === true) { ok++; }
      else if (ab === null || ba === null) { unknown++; }
      else { cannot.push([a, b]); }
    }
  }
  return { cannot: cannot, unknown: unknown, ok: ok };
}
/*SEQ-END*/
function seqRender() {
  var box = document.getElementById('seqh');
  var data = JSON.parse(document.getElementById('seqdata').textContent);
  var raw = parseFloat(box.value);
  var valid = raw >= 0.5 && raw <= 12;
  document.querySelectorAll('.seqout').forEach(function (dd) {
    var day = data[dd.getAttribute('data-seqday')];
    dd.textContent = '';
    var msg = function (t) { var s = document.createElement('div'); s.textContent = t; dd.appendChild(s); };
    if (!day) { msg('No listed events.'); return; }
    if (box.value === '') { msg('Enter an assumed playing length above (0.5 to 12 hours) to test sequencing.'); return; }
    if (!valid) { msg('Enter a length between 0.5 and 12 hours.'); return; }
    var D = raw * 60, evs = day.ev, p = evs[day.p], fb = [];
    evs.forEach(function (e, k) { if (k !== day.p && e.l !== null && e.l >= p.s + D) fb.push(e.lab); });
    msg('After the primary (' + raw + ' h): ' + (fb.length ? 'can be entered after it: ' + fb.join('; ') : 'no listed event can be entered after it.'));
    var r = seqCheck(evs, D);
    msg('Cannot be played in sequence: ' + (r.cannot.length ? r.cannot.map(function (q) { return q[0].lab + ' + ' + q[1].lab; }).join('; ') : 'none'));
    msg('Cannot be decided (a late-registration close is not stated): ' + r.unknown + ' pair(s).');
  });
}
document.addEventListener('DOMContentLoaded', function () {
  var box = document.getElementById('seqh');
  if (box) { box.addEventListener('input', seqRender); seqRender(); }
});
</script>"""


def build_schedule():
    body = ["<h1>Day schedule and overlap check</h1>"]
    body.append('<p class="muted">For each date, one <b>primary</b> event and, where one fits, a <b>conditional '
                'fallback</b>. Overlap is decided from official values only: an event occupies the window from its '
                'official start time to its official late-registration close time, both printed on its structure '
                'sheet. Where a sheet states no close time, the start time alone is used. No finish time is '
                'estimated - no official source publishes one.</p>')
    # The brief's goal is a day that starts at 8 a.m. Whether that is possible is a fact about the
    # published schedules, not a preference, so the page answers it from the rows instead of leaving
    # the reader to scan 247 of them. Restart and final-table rows are excluded: you cannot enter one.
    _first_day = TRIP.get("first_playing_day") or TRIP["check_in"]
    _last_day = TRIP.get("last_playing_day") or TRIP["check_out"]
    _win_days = {}
    _all_starts = []
    for r in ALL_EVENTS:
        st = r.get("start")
        if not st or r["kind"] in ("restart", "final"):
            continue
        _all_starts.append(st)
        if r.get("date") and _first_day <= r["date"] <= _last_day:
            if r["date"] not in _win_days or st < _win_days[r["date"]][0]:
                _win_days[r["date"]] = (st, r)
    _all_starts.sort()
    _earliest_all = _all_starts[0] if _all_starts else ""
    _earliest_win = min(v[0] for v in _win_days.values()) if _win_days else ""
    body.append('<div class="panel"><h2>Can a day start at 8 a.m.? Answered from the published starts</h2>'
                '<p>Across every captured Strip schedule, no enterable event starts before <b>%s</b>. Inside your '
                'window the earliest published start is <b>%s</b>. An 8 a.m. first event is therefore not '
                'something these schedules offer on these dates, so the plan below starts each day at that '
                'day\'s earliest published start and treats the later events as the second session. This is a '
                'limit of what the rooms publish, not of the plan (flag F57).</p>'
                '<div class="tablewrap"><table class="data"><thead><tr><th>Playing day</th>'
                '<th class="num">Earliest published start</th><th>That event</th>'
                '<th>What is left for the rest of the day</th><th>Official source</th></tr></thead><tbody>'
                % (esc(pretty_time(_earliest_all)) or "not stated", esc(pretty_time(_earliest_win)) or "not stated"))
    for d in sorted(_win_days):
        st, r = _win_days[d]
        later = sum(1 for x in ALL_EVENTS if x.get("date") == d and x.get("start") and x["start"] > st
                    and x["kind"] not in ("restart", "final"))
        body.append('<tr><td class="nowrap">%s</td><td class="num"><b>%s</b></td><td class="sm"><b>%s</b> #%s'
                    '</td><td class="sm">%s</td><td>%s</td></tr>'
                    % (esc(pretty_date(d)), esc(pretty_time(st)), esc(r.get("venue") or ""),
                       esc(r.get("event_no") or ""),
                       ("%d further enterable start(s) that day; the table below shows which ones fit after the "
                        "first event's registration window closes" % later) if later
                       else "nothing else is scheduled that day",
                       src_link(r.get("schedule_source") or r.get("source") or "", "official schedule page")))
    body.append('</tbody></table></div><p class="muted sm">Counted from the start time of every captured row '
                '(Venetian DeepStack Extravaganza IV, the WPT World Championship at Wynn and the Caesars daily '
                'flyer). If a 6:00 or 8:00 a.m. start is a requirement rather than a preference, the only honest '
                'next step is to ask the room whether it runs an early daily turbo its public schedule does not '
                'list - the site will not assume one exists.</p></div>')

    by_date = {}
    for r in ALL_EVENTS:
        if r["kind"] in ("restart", "final"):
            continue
        if not r.get("date"):
            continue
        by_date.setdefault(r["date"], []).append(r)
    rows_by_date = []
    for d in sorted(by_date):
        evs = sorted(by_date[d], key=lambda r: minutes(r["start"]))
        # One event per day, and the day is built around the one worth playing: an entry row that
        # passes the published single-entry standard and whose total entry fee AND guarantee are both
        # confirmed. The oldest rule here was "prefer a row whose cap is not stated", which is how a
        # schedule ends up built on an unverified event.
        def _rank(r):
            return (0 if r["entry_rule"] == "confirmed_single" else
                    1 if r["entry_rule"] == "unknown" else
                    2 if r["entry_rule"] == "unread" else 3,
                    0 if rankable(r) else 1,
                    0 if r["kind"] == "entry" else 1,
                    -(guarantee_value(r) or 0), minutes(r["start"]))
        entries = [r for r in evs if r["kind"] == "entry"]
        prim = min(entries or evs, key=_rank)
        ps, pe = minutes(prim["start"]), (late_reg_close(prim)[0] or minutes(prim["start"]))
        fb = None
        for r in evs:
            if r is prim:
                continue
            s = minutes(r["start"])
            if s >= pe:
                fb = r
                break
        conflicts = []
        for r in evs:
            if r is prim or r is fb:
                continue
            s = minutes(r["start"])
            if ps <= s <= pe:
                conflicts.append(r)
        rows_by_date.append((d, evs, prim, fb, conflicts))
    body.append(FILTER_BAR % FILTER_ARGS)
    all_days = [d for d, _e, _p, _f, _c in rows_by_date]
    chips = ['<button type="button" class="btn tiny%s" data-day="">All %d days</button>'
             % (" active" if len(all_days) else "", len(all_days))]
    chips += ['<button type="button" class="btn tiny" data-day="%s">%s</button>' % (esc(d), esc(pretty_date(d)))
              for d in all_days]
    body.append('<div class="daynav" id="daynav">%s</div>' % "".join(chips))
    body.append('<label class="chk" style="margin:6px 0"><input type="checkbox" id="winonly"> '
                'Only my %d nights (%s to %s, checkout day included for the day event)</label>'
                % (TRIP["nights"], esc(TRIP["check_in"]), esc(TRIP["check_out"])))
    # Optional what-if: the user's own playing-length estimate. Blank by default; no source supplies it,
    # so it is never shown as an official value and never written into the data.
    body.append('<div class="panel" id="seqbox"><label><b>Assumed playing length</b> (hours, optional) '
                '<input type="number" id="seqh" min="0.5" max="12" step="0.5" placeholder="blank" '
                'style="width:6em"></label> <span class="muted sm">Your own estimate. No official source publishes '
                'a finishing time, so nothing on this page supplies one. With a length entered, each day also shows '
                'which events cannot be played in sequence. Leave it blank to see only the start-time and '
                'late-registration checks.</span></div>')
    seq = {}
    for d, evs, prim, _fb, _c in rows_by_date:
        seq[d] = {
            "p": next(i for i, r in enumerate(evs) if r is prim),
            "ev": [{"lab": "%s %s%s" % (pretty_time(r["start"]), ("#%s " % r["event_no"]) if r.get("event_no") else "",
                                        "%s, %s" % (r["venue"], r["name"])),
                    "s": minutes(r["start"]), "l": late_reg_close(r)[0]} for r in evs],
        }
    seqjson = json.dumps(seq, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    out = []
    for d, evs, prim, fb, conflicts in rows_by_date:
        inwin = TRIP["check_in"] <= d <= TRIP["check_out"]
        hay = "%s %s %s" % (pretty_date(d), weekday(d),
                            " ".join("%s %s %s" % (r["venue"], r["name"], RULE_LABEL[r["entry_rule"]]) for r in evs))
        out.append('<div class="panel daycard%s" data-date="%s" data-daysel="1"%s '
                   'data-search="%s">' % (" inwin" if inwin else "", esc(d), ' data-outside="1"' if not inwin else "",
                                         esc(hay.lower())))
        out.append("<h3>%s, %s %s%s</h3>" % (esc(weekday(d)), esc(pretty_date(d)),
                                              '<span class="tag tag-b">in your window</span>' if inwin else "",
                                              ' <span class="muted sm">%d listed</span>' % len(evs)))
        out.append('<div class="kv"><dt>Primary event</dt><dd><b>%s</b> &mdash; %s, %s (%s)</dd>'
                   % (esc(prim["name"]), esc(prim["venue"]), esc(pretty_time(prim["start"])),
                      esc(RULE_LABEL[prim["entry_rule"]])))
        if fb is not None:
            out.append("<dt>Conditional fallback</dt><dd><b>%s</b> &mdash; %s, %s. "
                       "It starts at or after the primary's registration window closes.</dd>"
                       % (esc(fb["name"]), esc(fb["venue"]), esc(pretty_time(fb["start"]))))
        else:
            out.append("<dt>Conditional fallback</dt><dd><span class=\"blank\">None fits.</span> "
                       "No later event on this date starts after the primary's registration window closes.</dd>")
        if conflicts:
            out.append("<dt>Cannot be combined</dt><dd>%s</dd>" % "; ".join(
                "<b>%s</b> (%s, starts %s)" % (esc(c["name"]), esc(c["venue"]), esc(pretty_time(c["start"])))
                for c in conflicts))
        else:
            out.append("<dt>Cannot be combined</dt><dd><span class=\"blank\">none</span></dd>")
        out.append('<dt>At your assumed playing length</dt><dd class="seqout" data-seqday="%s">'
                   '<span class="muted">Enter a length above to test sequencing.</span></dd>' % esc(d))
        out.append("</div>")
        out.append('<div class="tablewrap"><table class="data pick"><thead><tr><th>Start</th><th>Venue</th>'
                   "<th>#</th><th>Event</th><th class=\"num\">Buy-in</th><th>Entry rule</th>"
                   "<th>Late reg closes</th><th>Source</th></tr></thead><tbody>")
        for r in evs:
            close, label = late_reg_close(r)
            out.append('<tr data-date="%s" data-venue="%s" data-rule="%s" data-rankable="%s" data-search="%s">'
                       "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td>"
                       "<td>%s</td><td>%s</td></tr>"
                       % (esc(r.get("date") or ""), esc(r["venue"]), esc(r["entry_rule"]),
                          "1" if rankable(r) else "0",
                          esc(("%s %s %s %s" % (r["venue"], r["name"], r.get("event_no") or "",
                                                RULE_LABEL[r["entry_rule"]])).lower()),
                          esc(pretty_time(r["start"])), esc(r["venue"]), esc(r.get("event_no") or ""),
                          esc(r["name"]) + (" <span class=\"tag tag-b\">primary</span>" if r is prim else ""),
                          money(r.get("buyin")),
                          '<span class="pill pill-%s">%s</span>' % (RULE_CLASS[r["entry_rule"]],
                                                                    esc(RULE_LABEL[r["entry_rule"]])),
                          esc(label) if label else '<span class="blank">not stated</span>',
                          src_link(r["source"], "source")))
        out.append("</tbody></table>")
        out.append('<p class="muted sm">No official schedule or structure sheet states a finishing time, so the '
                   'latest hour a day can run is not knowable from the sources. The "one event per day" plan below '
                   'is therefore built on start times and registration windows, which are published.</p>')
        out.append("</div>")
    body.append("".join(out))
    body.append('<script type="application/json" id="seqdata">%s</script>' % seqjson)
    body.append('<div class="warnbox"><b>Earliest verified start: 9:10 AM</b> (Venetian Event #46, a satellite on '
                '12 December). The earliest verified non-satellite start is 10:10 AM. No official schedule in this '
                'window lists an 8:00 AM start, so a "play from 8 AM" day is not supported by the sources.</div>')
    write("pages/schedule.html", page("Day schedule and overlap check", "".join(body), "schedule.html", 1,
                                      TABLE_JS_INIT + "<script>document.addEventListener('DOMContentLoaded',"
                                      "function(){initDays();});</script>" + SEQ_JS))


def build_hotels():
    body = ["<h1>Hotels: true cost per night</h1>"]
    body.append('<p class="muted">True nightly cost = room rate + resort fee + tax. The tax rate below is taken from '
                'the Clark County ordinance; resort fees are stated only where an official page publishes them. '
                '<b>Room rates are not filled in</b> - official booking engines are JavaScript applications and no '
                'dated rate could be read from an official source. Use the booking link, then record what you see '
                'in the dated log at the bottom of this page.</p>')
    body.append(SEARCH_BAR % ("Search hotels, fees, parking, addresses...",
                              '<label>Nightly budget ceiling $<input type="number" id="pbudget" min="0" step="10" placeholder="any"></label>'
                              '<label>Quality floor<select id="pquality"><option value="">Any</option>'
                              '<option value="1">Deluxe or better</option><option value="2">Luxury only</option></select></label>'))
    body.append('<p class="muted sm">The budget and quality filters only hide rows that are <i>known</i> to miss '
                'your ceiling or floor. Rows without a dated quote are never hidden by the budget filter - a '
                'missing rate is not a cheap rate.</p>')
    body.append('<div class="panel"><h2>Room tax</h2><div class="kv">'
                '<dt>Rate</dt><dd><b>%.2f%%</b> combined transient lodging tax</dd>'
                '<dt>Applies to</dt><dd>Resort hotels inside the primary gaming corridor (every hotel below)</dd>'
                "<dt>Source</dt><dd>%s</dd><dt>Note</dt><dd>%s</dd></div></div>"
                % (TAX["rate"], src_link(TAX["source"], "Clark County ordinance (PDF)"), esc(TAX["note"])))
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Hotel</th><th>Tier</th><th>Area</th>'
                '<th>Poker room</th><th>Walk</th><th class="num">Resort fee / night</th><th>Address (official)</th>'
                '<th>Parking</th><th>Player room rate</th><th>Cancellation</th><th>Official booking</th>'
                '<th>Resort-fee source</th></tr></thead><tbody>')
    for h in HOTELS:
        fee = ("$%.0f" % h["resort_fee"]) if h["resort_fee"] else '<span class="blank">not verified</span>'
        booking = h["booking"].replace("{IN}", TRIP["check_in"]).replace("{OUT}", TRIP["check_out"])
        tier_rank = {"Deluxe": "1", "Luxury": "2"}.get(h.get("tier", ""), "")
        body.append("<tr data-tier=\"%s\"><td><b>%s</b><br><span class=\"muted sm\">%s</span></td><td>%s</td><td>%s</td>"
                    "<td>%s</td><td>%s</td><td class=\"num\">%s<br><span class=\"muted sm\">%s</span></td>"
                    "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (tier_rank, esc(h["name"]), esc(h["quality_note"]), esc(h["tier"]), esc(h["area"]), esc(h["room"]),
                       '<span class="pill pill-ok">0 min, same property</span>' if h["on_property"]
                       else '<span class="blank">not verified</span>',
                       fee, esc(h["resort_fee_text"]),
                       (esc(h["address"]) + ("<br>" + src_link(h["address_source"], "source") if h["address_source"] else "")) if h.get("address") else '<span class="blank">not verified</span>',
                       (esc(h["parking"]) + ("<br>" + src_link(h["parking_source"], "source") if h["parking_source"] else "")) if h["parking"] else '<span class="blank">not verified</span>',
                       (esc(h["poker_rate"]) + ("<br>" + src_link(h["poker_rate_source"], "source") if h["poker_rate_source"] else "")) if h.get("poker_rate") else '<span class="blank">not verified</span>',
                       (esc(h["cancel"]) + ("<br>" + src_link(h["cancel_source"], "source") if h["cancel_source"] else "")) if h["cancel"] else '<span class="blank">not verified</span>',
                       src_link(booking, "open official booking (%s to %s)" % (TRIP["check_in"], TRIP["check_out"])),
                       src_link(h["resort_fee_source"], "official fee page") if h["resort_fee_source"]
                       else '<span class="blank">no official page found</span>'))
    body.append("</tbody></table></div>")

    # The brief's stay-capture list (mandatory resort fee and tax, parking, cancellation deadline,
    # rate timestamp) gets its own table because the hotel table above is a comparison table and this
    # one is an evidence table: one line per official statement, with the date it was read.
    body.append('<h2>Stay terms, one line per official statement</h2>')
    body.append('<p class="muted">Everything the brief asks to be captured for a stay is listed here as it is '
                'written on the property\'s own page, with the page and the read date. A blank cell means no '
                'official page states it - never a guess. Amounts marked <i>derived</i> are arithmetic on the '
                'figures in the same row (the published tax rate applied to the published fee), not a new '
                'observation.</p>')
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Hotel</th>'
                '<th class="num">Resort fee / night</th><th class="num">Fee + 13.38% tax</th>'
                '<th class="num">Parking / night</th><th>Cancellation deadline</th>'
                '<th>Deposit and incidentals</th><th>Check-in / check-out</th>'
                '<th class="num">Mandatory non-room cost / night</th><th>Rate timestamp</th>'
                '</tr></thead><tbody>')
    _tr = TAX["rate"] / 100.0
    for h in HOTELS:
        fee = h.get("resort_fee")
        fee_taxed = fee * (1 + _tr) if fee else None
        park = h.get("parking_self_per_night")
        mand = (fee_taxed + park) if (fee_taxed and park) else None

        def term(text, src, read, extra="", basis=""):
            if not text:
                return '<span class="blank">no official page states this</span>'
            bits = [esc(text)]
            if extra:
                bits.append('<span class="muted sm">%s</span>' % esc(extra))
            if src:
                bits.append(src_link(src, "official page"))
            if read:
                bits.append('<span class="muted sm">read %s%s</span>'
                            % (esc(read), " (" + esc(basis) + ")" if basis else ""))
            else:
                bits.append('<span class="muted sm">no read date recorded for this URL</span>')
            return "<br>".join(bits)

        cells = [
            term(h.get("resort_fee_text"), h.get("resort_fee_source"), h.get("resort_fee_read"),
                 basis=h.get("resort_fee_read_basis") or ""),
            ("$%.2f <span class=\"muted sm\">derived: $%.0f + %.2f%%</span>" % (fee_taxed, fee, TAX["rate"]))
            if fee_taxed else '<span class="blank">not computed - no verified fee</span>',
            term(("self-parking for registered guests" if park else None) or h.get("parking"),
                 h.get("parking_source"), h.get("parking_read"),
                 ("$%.0f/day; valet $%.0f/day" % (park, h["parking_valet_per_night"]))
                 if park and h.get("parking_valet_per_night") else "",
                 basis=h.get("parking_read_basis") or ""),
            term(h.get("cancel_deadline_display") or h.get("cancel"), h.get("cancel_source"),
                 h.get("cancel_read"), basis=h.get("cancel_read_basis") or ""),
            term(h.get("deposit") or h.get("incidentals"), h.get("extra_terms_source") or h.get("deposit_source"),
                 h.get("extra_terms_read") or h.get("cancel_read"),
                 ("Incidentals: " + h["incidentals"]) if h.get("incidentals") else ""),
            term(h.get("checkin_checkout"), h.get("checkin_checkout_source"), h.get("cancel_read")),
            ("$%.2f <span class=\"muted sm\">derived: taxed fee + parking</span>" % mand) if mand
            else '<span class="blank">not computed</span>',
            '<span class="nowrap">%s</span>' % esc(h.get("resort_fee_read") or h.get("extra_terms_read") or "")
            if (h.get("resort_fee_read") or h.get("extra_terms_read"))
            else '<span class="blank">no dated official read</span>',
        ]
        body.append('<tr data-tier="%s"><td><b>%s</b><br><span class="muted sm">%s</span></td>%s</tr>'
                    % ({"Deluxe": "1", "Luxury": "2"}.get(h.get("tier", ""), ""), esc(h["name"]),
                       esc(h.get("quality_note") or ""), "".join("<td>%s</td>" % c for c in cells)))
    body.append("</tbody></table></div>")
    body.append('<p class="muted sm">The Venetian row is complete except for the room rate itself: the $55 resort '
                'fee "plus tax" and the $20/day registered-guest self-parking fee are both stated on official '
                'pages, so the mandatory non-room cost of a Venetian night is a known figure, and only the room '
                'rate is missing. That is the difference between an unpriceable stay and a stay whose price is '
                'one published number away.</p>')

    body.append('<h2>Dated stay captures (a log, never a single value)</h2>')
    body.append('<p class="muted">Each row is a dated capture from an official booking page or official terms page, '
                'kept exactly as returned. Fields the official UI did not return are blank and flagged. Captures '
                'are comparable like-for-like only when the stay window, occupancy and room class match - these do '
                'not, so no cheapest-hotel ranking is drawn from them.</p>')
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Hotel</th><th>Room type</th>'
                '<th>Check-in</th><th>Check-out</th><th>Occupancy</th><th class="num">Checkout total</th>'
                '<th class="num">Nightly average</th><th class="num">Resort fee / night</th><th class="num">Tax</th>'
                '<th>Parking</th><th>Cancellation deadline</th><th>Rate timestamp</th><th>Source</th>'
                '</tr></thead><tbody>')
    for s in RATE_SNAPSHOTS["entries"]:
        def cell(v, suffix=""):
            return (esc(str(v)) + suffix) if v not in (None, "") else '<span class="blank">not returned</span>'
        body.append("<tr><td><b>%s</b></td><td>%s</td><td class=\"nowrap\">%s</td><td class=\"nowrap\">%s</td>"
                    "<td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                    "<td class=\"num\">%s</td><td>%s</td><td>%s</td><td class=\"nowrap\">%s</td><td>%s</td></tr>"
                    % (esc(s["hotel"]), esc(s["room_type"]),
                       esc(s["checkin"]), esc(s["checkout"]),
                       esc(s["occupancy"]),
                       ("$%s" % format(s["checkout_total"], ",.2f")) if s.get("checkout_total") else '<span class="blank">not returned</span>',
                       ("$%s" % format(s["nightly_average"], ",.2f")) if s.get("nightly_average") else '<span class="blank">not returned</span>',
                       ("$%s" % format(s["resort_fee_per_night"], ",.2f")) if s.get("resort_fee_per_night") else '<span class="blank">not verified</span>',
                       ("$%s" % format(s["tax_total"], ",.2f")) if s.get("tax_total") else '<span class="blank">not returned</span>',
                       cell(s.get("parking")),
                       cell(s.get("cancellation_deadline")),
                       esc(s["rate_timestamp"]),
                       src_link(s["source"], s["source_label"])))
    body.append("</tbody></table></div>")
    body.append('<p class="muted sm">Tax note: %s</p>' % esc(RATE_SNAPSHOTS.get("tax_note", "")))
    body.append('<div class="warnbox">Like-for-like rule: compare two captures only when check-in, check-out, '
                'occupancy and room class match. True nightly cost for planning = the itemised checkout total '
                '&divide; nights from a capture that matches your dates, or rate + resort fee + %.2f%% tax entered '
                'in the calculator below. A blank cell means the official UI did not return that value; it is '
                'never filled in.</div>' % TAX["rate"])

    # The brief sets a nightly budget as a ceiling and a quality floor; both have to be usable,
    # otherwise the page is a list and not a selector.
    _fee = TAX["rate"] / 100.0
    _ceil = (TRIP.get("budget_ceiling") or {}).get("per_night")
    _floor = (TRIP.get("budget_floor") or {}).get("tier")
    # the tiers at or above the published quality floor, per the ordering recorded in meta.json
    _order = META.get("tier_order") or ["Budget", "Mid-scale", "Upscale", "Upper Upscale", "Luxury"]
    _at = _order.index(_floor) if _floor in _order else 0
    QUALITY_OK = set(_order[_at:]) if _floor else set(_order)
    body.append("<h2>Same stay, itemized</h2>")
    body.append('<p class="muted sm">The brief sets a nightly budget as a ceiling and a quality floor, so both are '
                'live inputs here. Only the hotels with an official rate can be proven inside the budget; the rest '
                'are shown as "cannot compute", never as within budget.</p>')
    body.append('<div class="panel"><div class="calc">'
                '<label>Nightly budget ceiling $<input id="bceil" type="number" min="0" step="1" value="%s"></label>'
                '<label>Quality floor<select id="bfloor"><option value="">any tier</option>'
                '<option value="Luxury"%s>Luxury only</option>'
                '<option value="Upscale"%s>Luxury or Upscale</option></select></label>'
                '<label>Hotel<select id="hsearch"><option value="">all hotels</option>%s</select></label>'
                '<span class="muted sm" id="bcost"></span></div>' % (
                    ("%.2f" % _ceil) if _ceil else "",
                    " selected" if (TRIP.get("budget_floor") or {}).get("tier") == "Luxury" else "",
                    " selected" if (TRIP.get("budget_floor") or {}).get("tier") == "Upscale" else "",
                    "".join('<option value="%s">%s</option>' % (esc(h["name"]), esc(h["name"])) for h in HOTELS)))
    body.append('<div class="tablewrap"><table class="data" id="hitems"><thead><tr><th>Hotel</th><th>Tier</th>'
                '<th>Poker room</th><th class="num">Room rate</th><th class="num">+ Resort fee</th>'
                '<th class="num">+ Tax %.2f%%</th><th class="num">True per night</th>'
                '<th class="num">%d nights</th><th>Budget ceiling</th><th>Quality floor</th>'
                '<th>What the fee covers</th><th>Source</th></tr></thead><tbody>'
                % (TAX["rate"], TRIP["nights"]))
    for h in HOTELS:
        fee = h["resort_fee"] or 0
        rate = h.get("rate_floor")
        cells = ['<td><b>%s</b>%s</td>' % (esc(h["name"]),
                   (' <span class="muted sm">%s</span>' % esc(h.get("rate_floor_room") or "").split(",")[0])
                   if rate else "")
                 + '<br><span class="muted sm">%s</span>' % esc(h["quality_note"] or "")[:150]]
        cells.append("<td>%s</td>" % esc(h["tier"]))
        cells.append('<td>%s<br><span class="muted sm">%s</span></td>' % (
            esc(h.get("room") or ""),
            "0 min, same building" if h["on_property"] else "walking time not verified"))
        if rate:
            taxable = rate + fee
            taxed = taxable * _fee
            cells.append('<td class="num">$%.2f<br><span class="muted sm">official starting rate</span></td>' % rate)
            cells.append('<td class="num">$%.2f</td>' % fee)
            cells.append('<td class="num">$%.2f</td>' % taxed)
            cells.append('<td class="num"><b>$%.2f</b></td>' % (taxable * (1 + _fee)))
            cells.append('<td class="num">$%.2f</td>' % (taxable * (1 + _fee) * TRIP["nights"]))
            cells.append('<td>%s</td>' % ('<span class="pill pill-bad">over</span>' if _ceil and taxable * (1 + _fee) > _ceil
                                          else '<span class="pill pill-ok">within</span>' if _ceil
                                          else '<span class="muted sm">no ceiling set</span>'))
            cells.append("<td>%s</td>" % ('<span class="pill pill-ok">meets it</span>' if h["tier"] in QUALITY_OK
                          else '<span class="pill pill-warn">below the quality floor</span>'))
            link = src_link(h.get("rate_floor_source"), "official rate page")
            note = esc((h.get("rate_caveat") or "")[:300])
        else:
            cells.append('<td class="blank">not published</td>' * 4)
            cells.append('<td class="blank">no rate</td>')
            cells.append('<td class="blank">not published</td>')
            cells.append('<td><span class="pill pill-warn">cannot compute</span></td>')
            cells.append("<td>%s</td>" % ('<span class="pill pill-ok">meets it</span>' if h["tier"] in QUALITY_OK
                          else '<span class="pill pill-warn">below the quality floor</span>'))
            link = src_link(h["booking"].replace("{IN}", TRIP["check_in"]).replace("{OUT}", TRIP["check_out"]),
                            "get a dated quote here")
            note = esc((h.get("rate_caveat") or "no official nightly rate published")[:300])
        cells.append('<td class="sm">%s<br><span class="muted sm">%s</span></td>'
                     % (esc(h["resort_fee_text"] or "no official fee page")[:200], note))
        cells.append("<td>%s</td>" % link)
        body.append('<tr data-tier="%s" data-ceil="%s">%s</tr>' % (
            esc(h["tier"]), "%.2f" % ((rate + fee) * (1 + _fee)) if rate else "", "".join(cells)))
    body.append("</tbody></table></div>")
    body.append('<div class="panel"><h2>Dated rate log</h2>'
                '<p class="muted sm">A rate is never one number, so this page keeps a dated log. Each row below is '
                'one dated observation with the official link it was read from, rewritten each morning by '
                '<code>scripts/monitor_b3be876c.py</code>.</p>')
    if RATES:
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Recorded</th><th>What it is</th>'
                    '<th>Hotel &middot; dates</th><th class="num">Room / night</th><th class="num">Resort fee</th>'
                    '<th class="num">Tax</th><th class="num">True / night</th><th class="num">Stay total</th>'
                    '<th>Cancellation deadline</th><th>Parking</th><th>Caveats</th><th>Source</th></tr></thead><tbody>')
        for r in RATES:
            nights = r.get("nights")
            lo, hi = r.get("nightly_low"), r.get("nightly_high")
            room = (("%s &ndash; %s" % (money(lo), money(hi))) if lo and hi else
                    money(r.get("nightly_average")) if r.get("nightly_average")
                    else '<span class="blank">not published per night</span>')
            fee = (money(r["resort_fee_total"]) + (' <span class="muted sm">%s/night</span>'
                                                    % money(r["resort_fee_per_night"]))
                   if r.get("resort_fee_total") else (money(r.get("resort_fee_per_night"))
                                                       if r.get("resort_fee_per_night") else "not stated"))
            tax = (money(r["tax_total"]) + ' <span class="muted sm">%.2f%%</span>'
                   % (r.get("tax_rate_pct") or TAX["rate"]) if r.get("tax_total") else
                   ('<span class="muted sm">%.2f%%, payable on top</span>' % r["tax_rate_pct"]
                    if r.get("tax_rate_pct") else "not stated"))
            tr_ = ("%s &ndash; %s" % (money(r["true_nightly_low"]), money(r["true_nightly_high"]))
                   if r.get("true_nightly_low") else
                   (money(r["nightly_average"]) + ' <span class="muted sm">room only</span>'
                    if r.get("nightly_average") else '<span class="blank">no rate</span>'))
            body.append("<tr><td class=\"nowrap\">%s%s</td><td class=\"sm\">%s</td>"
                        "<td class=\"sm\"><b>%s</b><br><span class=\"muted nowrap\">%s</span></td>"
                        "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                        "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td>"
                        "<td class=\"sm\"><ul class=\"fldlist\">%s</ul></td><td>%s</td></tr>"
                        % (esc(r.get("observed_on") or ""),
                           "" if r.get("verified", True) else ' <span class="pill pill-warn">not re-verifiable</span>',
                           esc(r.get("kind") or ""), esc(r.get("hotel") or ""),
                           esc("%s to %s (%s nights)" % (r["checkin"], r["checkout"], nights)) if nights
                           else esc(r.get("room_type") or "no dates attached"),
                           room, fee, tax, tr_,
                           money(r["checkout_total"]) if r.get("checkout_total")
                           else ('<span class="blank">published only as a starting rate</span>'
                                 if lo else '<span class="blank">-</span>'),
                           esc(r.get("cancellation_deadline") or "not stated for this rate"),
                           esc(r.get("parking") or "not stated for this rate"),
                           "".join("<li>%s</li>" % esc(c) for c in r.get("caveats") or []),
                           src_link(r.get("source"), r.get("source_label") or "official source")
                           + "".join("<br>%s" % src_link(a.get("url"), a.get("label"))
                                     for a in r.get("additional_sources") or [])))
        body.append("</tbody></table>")
        body.append('<p class="muted sm">Every row here is the Venetian because it is the only property in the '
                    'shortlist with a number on an official page. The other four have no dated rate entry at all - '
                    'the log is not padded with estimates to make the table look complete. The newest row is not '
                    'a rate at all: it is the dated capture of the fees, taxes and deadlines a Venetian stay '
                    'mandates, which is the part of the true nightly cost that official pages do publish.</p></div>')
    body.append("</div>")
    body.append('<div class="panel" id="hcalc"><h2>True nightly cost calculator</h2>'
                '<div class="calc">'
                '<label>Hotel<input id="hhotel" value="The Venetian Resort"></label>'
                '<label>Nightly room rate $<input id="hrate" type="number" step="1" min="0" placeholder="from the booking page"></label>'
                '<label>Resort fee $<input id="hfee" type="number" step="1" min="0" value="55"></label>'
                '<label>Tax %%<input id="htax" type="number" step="0.01" min="0" value="%.2f"></label>'
                '<label>Nights<input id="hnights" type="number" step="1" min="1" value="%d"></label>'
                '<label>Check in<input id="hin" type="date" value="%s"></label>'
                '<label>Check out<input id="hout" type="date" value="%s"></label>'
                '<label>Booking link (optional)<input id="hsrc" placeholder="paste the official link"></label>'
                '<button class="btn" id="hsave" type="button">Save dated quote</button>'
                '</div><div class="result" id="hres"></div>'
                '<p class="muted sm">Resort fees are taxable in Clark County (the ordinance defines "rent" to include '
                'mandatory charges), so tax is applied to rate + fee. The field defaults to the Venetian fee; change '
                'it to the fee you verified.</p></div>'
                % (TAX["rate"], TRIP["nights"], TRIP["check_in"], TRIP["check_out"]))
    body.append('<div class="panel"><h2>Dated rate log &mdash; your own quotes</h2>'
                '<p class="muted sm">Each entry is stored with the time you recorded it, in this browser only. '
                'Rates are a log, not a single value - keep adding entries as prices move. The table above is the '
                'server-side log, rebuilt from the official pages each morning.</p>'
                '<div id="ratelog"></div></div>')
    body.append('<div class="badbox"><b>The only official rate figure published for this trip is a floor, not a '
                'quote.</b> The Venetian publishes poker-room suite rates that "start as low as %s and %s" for a '
                'Luxury King Suite, plus the $%.0f resort fee, conditional on six hours of live play or a $300+ '
                'tournament entry every night before 2 a.m. %s. The live booking page for %s to %s returned no rate '
                'at all (the engine is a JavaScript application), so the average nightly figure behind the '
                'reservation snapshot in the log above could not be re-verified against an official source and stays '
                'marked as such. Every other hotel in the shortlist publishes no nightly rate anywhere official, so '
                'its row is blank. See flag F14 on the <a href="flagged-review.html">Flagged page</a>.</div>'
                % (money(VEN_POKER.get("rate_low")), money(VEN_POKER.get("rate_high")),
                   float(HOTELS[0]["resort_fee"] or 55),
                   src_link(VEN_POKER.get("url"), "official poker-room rates page"),
                   esc(TRIP["check_in"]), esc(TRIP["check_out"])))
    write("pages/hotels.html", page("Hotels and true nightly cost", "".join(body), "hotels.html", 1))


def build_routes():
    body = ["<h1>Walking routes: hotel to poker room</h1>"]
    body.append('<p class="muted">The brief asks for a 30-minute walking limit. Only one walking distance is '
                'published officially anywhere: a poker room that sits inside the hotel you are staying in, which is '
                'zero minutes. No hotel or casino publishes a walking time to a <i>different</i> property, so those '
                'cells are left blank rather than estimated. Use the route link to check one yourself, then record '
                'the minutes below - the 30-minute filter works on what you record.</p>')
    body.append(SEARCH_BAR % ("Search hotels, rooms, routes...", ""))
    body.append('<div class="panel"><label class="chk"><input type="checkbox" id="walkfilter"> '
                'Hide pairs known to exceed the 30-minute limit (rows without verified minutes stay, marked unverified)</label>'
                '<div class="calc" style="margin-top:10px">'
                '<label>Pair<select id="walkpair">%s</select></label>'
                '<label>Minutes you measured<input id="walkmins" type="number" step="1" min="0"></label>'
                '<button class="btn" id="walkrecord" type="button">Record</button></div>'
                '<p class="muted sm">Recorded values are stored in this browser only and are shown as measured by you, '
                'not as an official value.</p></div>'
                % "".join('<option value="%s">%s &rarr; %s</option>' % (esc(r["hotel_key"] + "|" + r["venue_key"]),
                                                                        esc(r["hotel"]), esc(r["venue"]))
                          for r in ROUTES if not r["same_property"]))
    body.append('<div class="tablewrap"><table class="data" id="routetable"><thead><tr><th>Hotel</th><th>Poker room</th>'
                '<th>Same property</th><th>Walking time</th><th>Method</th><th>Check it yourself</th></tr></thead><tbody>')
    for r in ROUTES:
        body.append("<tr data-pair=\"%s\" data-min=\"%s\"><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                    "<td class=\"sm\">%s</td><td>%s</td></tr>"
                    % (esc(r["hotel_key"] + "|" + r["venue_key"]),
                       "0" if r["same_property"] else "",
                       esc(r["hotel"]), esc(r["venue"]),
                       "Yes" if r["same_property"] else "No",
                       '<span class="pill pill-ok">0 min</span>' if r["same_property"]
                       else '<span class="blank">not verified</span>',
                       esc(r["method"]),
                       src_link(r["maps"], "walking directions")))
    body.append("</tbody></table></div>")
    body.append('<div class="warnbox">The Wynn poker room is in <b>Encore</b>, not the main Wynn tower: the official '
                'WPT terms state "Players will register in the Wynn Las Vegas Poker Room, located in Encore at Wynn '
                'Las Vegas". Allow extra indoor walking time if you stay in the Wynn tower. '
                '%s</div>' % src_link(WPT_TERMS := "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf", "official terms"))
    write("pages/routes.html", page("Walking routes", "".join(body), "routes.html", 1))


def build_planner():
    # CANDIDATES alone became an empty list once the sheets were read: every Venetian row is now either
    # confirmed single-entry or explicitly multi-entry. The planner lists what can actually be played -
    # the confirmed rows first, the not-stated ones still labelled as such.
    rows = [r for r in ALL_EVENTS if r["kind"] == "entry" and r.get("date")
            and TRIP["check_in"] <= r["date"] <= TRIP["check_out"]
            and r["entry_rule"] in ("confirmed_single", "unknown")]
    rows.sort(key=lambda r: (r["date"], r["start"]))
    body = ["<h1>Trip planner: cost of the trip</h1>"]
    body.append(SEARCH_BAR % ("Search candidate events...", ""))
    body.append('<p class="muted">Estimated trip cost = <b>selected entries &times; listed buy-ins</b> + '
                '<b>nights &times; true hotel cost</b>. The list below contains %d events in your window (%s to %s): '
                'the ones whose own structure sheet was read in full and grants no further entry are the playable '
                'set, and rows whose sheet is merely silent about re-entry are still labelled as such. One listed '
                'buy-in is counted per ticked event.</p>'
                % (len(rows), esc(pretty_date(TRIP["check_in"])), esc(pretty_date(TRIP["check_out"]))))
    body.append('<div class="panel"><h2>Proposed planning window</h2><div class="kv">'
                '<dt>Check in / out</dt><dd>%s &rarr; %s (%d nights)</dd>'
                '<dt>Dates to consider</dt><dd>%s</dd>'
                '<dt>Selection basis</dt><dd>%s</dd></div>'
                '<p class="warnbox">These dates are an automatically selected research scenario, not confirmed '
                'travel dates. No trip dates, nightly budget or hotel quality floor were ever stated by a traveller; '
                'the figures beside them are what the official sources support, and every table follows the date '
                'filter so any other week can be reviewed.</p>'
                '<p class="muted sm">Change the dates with the filter on any tournament table; this page lists the '
                'window that was chosen automatically, and you can re-pick entries for any other dates there.</p></div>'
                % (esc(TRIP["check_in"]), esc(TRIP["check_out"]), TRIP["nights"],
                   esc("%s to %s" % (pretty_date(TRIP["check_in"]), pretty_date(TRIP["check_out"]))),
                   esc(TRIP["rationale"])))
    body.append('<div class="panel"><h2>Nightly budget ceiling and quality floor</h2>'
                '<div class="calc">'
                '<label>Nightly budget ceiling $<input id="pbudget" type="number" min="0" step="10" placeholder="any"></label>'
                '<label>Quality floor<select id="pquality"><option value="">Any</option>'
                '<option value="1">Deluxe or better</option><option value="2">Luxury only</option></select></label>'
                '</div>'
                '<p class="muted sm">These two controls are the nightly budget ceiling and hotel quality floor. '
                'They filter the hotel shortlist below; they never invent a rate. A hotel without a dated quote '
                'for your dates stays listed as <i>quote needed</i> rather than being ranked or hidden.</p></div>')
    body.append('<div class="panel"><h2>Hotel shortlist</h2>'
                '<div class="tablewrap"><table class="data"><thead><tr><th>Hotel</th><th>Tier</th>'
                '<th class="num">Resort fee / night</th><th>Walk to room</th><th>Dated quote for your dates</th>'
                '<th>Official booking</th></tr></thead><tbody>')
    for h in HOTELS:
        booking = h["booking"].replace("{IN}", TRIP["check_in"]).replace("{OUT}", TRIP["check_out"])
        tier_rank = {"Deluxe": "1", "Luxury": "2"}.get(h.get("tier", ""), "")
        body.append("<tr data-tier=\"%s\"><td><b>%s</b></td><td>%s</td><td class=\"num\">%s</td>"
                    "<td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (tier_rank, esc(h["name"]), esc(h["tier"]),
                       ("$%.0f" % h["resort_fee"]) if h["resort_fee"] else '<span class="blank">not verified</span>',
                       '<span class="pill pill-ok">0 min, same property</span>' if h["on_property"]
                       else '<span class="blank">not verified</span>',
                       '<span class="blank">quote needed</span>',
                       src_link(booking, "open official booking (%s to %s)" % (TRIP["check_in"], TRIP["check_out"]))))
    body.append("</tbody></table></div></div>")
    # --- the hotel side of the calculator: prefilled from the dated log, not typed by the reader ---
    _cap = None
    for r in reversed(RATES):
        if r.get("nightly_average") and r.get("hotel_key") == "venetian":
            _cap = r
            break
    _fee = float(HOTELS[0]["resort_fee"] or 0) if HOTELS else 0.0
    _park = (HOTELS[0].get("parking_self_per_night") or 0) if HOTELS else 0.0
    _known = _fee * (1 + TAX["rate"] / 100.0) + _park
    body.append('<div class="panel" id="pcalc" data-tax="%.2f" data-fee="%.2f" data-park="%.2f">'
                '<h2>Cost of the trip</h2><div class="calc">'
                '<label>Hotel cost source<select id="pquote">'
                '<option value="capture" data-pernight="%s" data-includes="%s" data-label="%s"'
                ' data-datematched="%s" selected>Auto: the dated capture in the log (%s)</option>'
                '<option value="floor" data-pernight="%.2f" data-includes="0"'
                ' data-label="official poker suite-rate floor">Auto: published poker suite-rate floor (%s + '
                '$%.0f fee + %.2f%% tax)</option>'
                '<option value="none" data-pernight="" data-includes="0" data-label="nothing">Nothing: price the '
                'entries and the mandatory stay fees only</option>'
                '<option value="manual" data-pernight="" data-includes="1" data-label="manual">'
                'Type a quote I obtained</option></select></label>'
                '<label>True hotel cost / night $<input id="ptrue" type="number" min="0.01" step="0.01" '
                'placeholder="no date-specific quote recorded" value="%s"%s></label>'
                '<label>Nights<input id="pnights" type="number" min="1" step="1" value="%d"></label>'
                '<label class="chk"><input id="ppark" type="checkbox" %s> Add parking ($%.0f/night, official)</label>'
                '</div><div class="result" id="ptotal"></div>'
                '<p class="muted sm">The hotel side is filled from the dated log, not from a guess: the auto '
                'options are the only two numbers an official source supports. The capture is a real itemized '
                'total but for <b>%s</b>, not for your window, so the total is labelled '
                '<i>not date-matched</i> until a quote for your dates is recorded. Without any hotel rate, the '
                'mandatory non-room cost of a Venetian night is still known - $%.2f a night (%.2f%% tax on the '
                '$%.0f resort fee, plus the $%.0f guest parking fee), which is $%.2f over %d nights - and the '
                'trip total stays <b>Incomplete</b> rather than closing on a zero-cost hotel.</p></div>'
                '<div class="panel">'
                % (TAX["rate"], _fee, _park,
                   ("null" if not _cap else "%.2f" % _cap["nightly_average"]),
                   "1" if _cap else "0",
                   esc("%s to %s, %s nights" % (_cap["checkin"], _cap["checkout"], _cap["nights"])) if _cap else "",
                   "1" if (_cap and _cap.get("checkin") == TRIP["check_in"]
                           and _cap.get("checkout") == TRIP["check_out"]) else "0",
                   esc("%s to %s, $%s/night average" % (_cap["checkin"], _cap["checkout"],
                                                         format(_cap["nightly_average"], ",.2f"))) if _cap
                   else "no dated capture",
                   FLOOR_TRUE_NIGHT, money(VEN_POKER.get("rate_low")) or "rate not published", _fee, TAX["rate"],
                   ("%.2f" % _cap["nightly_average"]) if _cap else "",
                   " readonly" if _cap else "",
                   TRIP["nights"], "checked" if _park else "disabled", _park,
                   esc("%s to %s" % (_cap["checkin"], _cap["checkout"])) if _cap else "-",
                   _known, TAX["rate"], _fee, _park, _known * TRIP["nights"], TRIP["nights"]))
    body.append('<p class="muted sm">The poker suite-rate floor (the second auto option, $%.2f a night: the '
                'official Venetian poker-suite rate of %s plus the $%.0f resort fee, taxed at %.2f%%) is a '
                'published <b>floor, not a quote</b> - it is conditional on six hours of live play or a $300+ '
                'tournament entry every night before 2 a.m., and that page only publishes rates 150 days out, so '
                'December 2026 is not on it. The resort-fee tax treatment is not verified for every hotel: the '
                '$%.2f mandatory-cost figure on this page applies to the Venetian, whose own fee page states '
                '"$55 plus tax"; for any other hotel use its checkout total, not this arithmetic. Prefer the '
                'booking checkout total over any estimate. Only '
                'single-entry and cap-not-stated events are listed below: no official text bounds how many '
                're-entries an event allows, so a re-entry event can never be priced.</p></div>'
                % (FLOOR_TRUE_NIGHT, money(VEN_POKER.get("rate_low")) or "rate not published",
                   _V_FEE, TAX["rate"], _known))
    body.append('<div class="panel" id="picks"><h2>Entries in your window (%d)</h2>' % len(rows))
    body.append('<div class="tablewrap"><table class="data pick"><thead><tr><th>Play?</th><th>Date</th><th>Start</th>'
                '<th>#</th><th>Event</th><th class="num">Buy-in</th><th>House fee</th>'
                '<th class="num">Guarantee</th><th class="num">GTD &divide; entry</th><th>Source</th></tr></thead><tbody>')
    for r in rows:
        body.append("<tr><td><input type=\"checkbox\" data-buyin=\"%s\"></td><td class=\"nowrap\">%s</td>"
                    "<td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td><td class=\"num\">%s</td>"
                    "<td class=\"num\">%s</td><td>%s</td></tr>"
                    % (esc(r["buyin"]), esc(pretty_date(r["date"])), esc(pretty_time(r["start"])),
                       esc(r.get("event_no") or ""), esc(r["name"]), money(r.get("buyin")),
                       esc(r.get("house_fee") or ""),
                       money(r.get("guarantee")) or '<span class="blank">not stated</span>',
                       ratio_text(r) or "-", src_link(r["source"], "source")))
    body.append("</tbody></table></div></div>")
    body.append('<div class="warnbox">A buy-in is not the whole cost of an entry: an event that allows re-entry can '
                'cost two, three or more buy-ins, and the house fee is already inside the published buy-in. '
                'Reconfirm schedules, rates and policies with the room and the hotel before any non-refundable '
                'payment.</div>')
    write("pages/planner.html", page("Trip planner", "".join(body), "planner.html", 1))


def build_venue(key, filename, title, extra):
    v = VENUE_BY_KEY[key]
    evs = [r for r in ALL_EVENTS if r["venue"] == v["name"]]
    hotels = [h for h in HOTELS if h["key"] == key]
    body = ["<h1>%s</h1>" % esc(title)]
    body.append('<div class="panel"><div class="kv"><dt>Poker room</dt><dd>%s</dd><dt>Area</dt><dd>%s</dd>'
                '<dt>Status</dt><dd>%s</dd><dt>Official page</dt><dd>%s</dd></div>'
                '<p class="muted sm">%s</p></div>'
                % (esc(v["room"]), esc(v["area"]), esc(v["status"].replace("_", " ")),
                   src_link(v["source"], "official page"), esc(v["status_note"])))
    if extra:
        body.append(extra)
    body.append("<h2>Events (%d rows)</h2>" % len(evs))
    if evs:
        body.append(FILTER_BAR % FILTER_ARGS)
        body.append(table_shell(evs, EVENT_HEAD, with_venue=False))
    else:
        body.append('<div class="panel"><p><span class="blank">No verified rows.</span> %s</p></div>' % esc(v["status_note"]))
    if hotels:
        body.append("<h2>Stay here</h2>")
        body.append('<p class="muted sm">Each figure is quoted from the property\'s own page with the date it was '
                    'read; the full sentences and links are on the <a href="../hotels.html">hotels page</a>. '
                    '"Mandatory non-room cost" is derived arithmetic: the published resort fee with the county '
                    'transient-lodging tax on top, plus the published guest parking fee.</p>')
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Hotel</th><th>Walk</th>'
                    '<th class="num">Resort fee</th><th class="num">Parking / night</th>'
                    '<th>Cancellation</th><th>Check-in / check-out</th>'
                    '<th class="num">Mandatory non-room cost / night</th><th>Booking</th></tr></thead><tbody>')
        _tr = TAX["rate"] / 100.0
        for h in hotels:
            booking = h["booking"].replace("{IN}", TRIP["check_in"]).replace("{OUT}", TRIP["check_out"])
            fee, park = h.get("resort_fee"), h.get("parking_self_per_night")
            mand = (fee * (1 + _tr) + park) if (fee and park) else None
            body.append("<tr><td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                        "<td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td></tr>"
                        % (esc(h["name"]),
                           '<span class="pill pill-ok">0 min, same property</span>' if h["on_property"] else '<span class="blank">not verified</span>',
                           ("$%.0f<br><span class=\"muted sm\">%s</span>" % (fee, esc(h.get("resort_fee_text") or "")))
                           if fee else '<span class="blank">not verified</span>',
                           ("$%.0f<br><span class=\"muted sm\">%s</span>"
                            % (park, esc((h.get("parking_read") or "") + " read"))) if park
                           else ("see hotels page" if h.get("parking") else '<span class="blank">not verified</span>'),
                           esc(h.get("cancel_deadline_display") or h.get("cancel") or "")
                           or '<span class="blank">not verified</span>',
                           esc(h.get("checkin_checkout") or "")
                           + ("<br><span class=\"muted sm\">read %s</span>" % esc(h.get("cancel_read")))
                           if h.get("checkin_checkout") else '<span class="blank">not verified</span>',
                           ("$%.2f <span class=\"muted sm\">derived</span>" % mand) if mand
                           else '<span class="blank">not computed</span>',
                           src_link(booking, "official booking")))
        body.append("</tbody></table></div>")
    write("pages/venues/%s" % filename, page(title, "".join(body), filename, 2,
                                             TABLE_JS_INIT if evs else ""))


def build_others():
    v = VENUE_BY_KEY["caesars"]
    evs = [r for r in ALL_EVENTS if r["venue"] in ("Caesars Palace", "South Point")]
    body = ["<h1>Other venues</h1>"]
    body.append('<p class="muted">Rooms other than the Venetian and Wynn. Rooms are listed with the status their '
                'own official pages support; where no official schedule could be read, nothing is listed.</p>')
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Venue</th><th>Poker room</th><th>Area</th>'
                '<th>Status</th><th>What the official site says</th><th>Official page</th></tr></thead><tbody>')
    for x in VENUES:
        if x["key"] in ("venetian", "wynn"):
            continue
        body.append("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td class=\"sm\">%s</td><td>%s</td></tr>"
                    % (esc(x["name"]), esc(x["room"]), esc(x["area"]), esc(x["status"].replace("_", " ")),
                       esc(x["status_note"]), src_link(x["source"], "official page")))
    body.append("</tbody></table></div>")
    body.append("<h2>Verified rows from other rooms (%d)</h2>" % len(evs))
    if evs:
        body.append(FILTER_BAR % FILTER_ARGS)
        body.append(table_shell(evs, EVENT_HEAD))
    body.append(archive_block(2))
    write("pages/venues/others.html", page("Other venues", "".join(body), "others.html", 2,
                                           TABLE_JS_INIT if evs else ""))


def build_exec():
    body = ["<h1>Executive summary</h1>"]
    body.append(SEARCH_BAR % ("Search this summary...", ""))
    ven_confirmed = [r for r in VEN if r.get("entry_rule") == "confirmed_single"]
    ven_multi = [r for r in VEN if r.get("entry_rule") == "multi"]
    rankable = [r for r in VEN if r.get("kind") == "entry"
                and r.get("entry_rule") == "confirmed_single"
                and isinstance(r.get("buyin"), (int, float))
                and r.get("house_fee") not in (None, "")
                and guarantee_value(r) is not None
                and r.get("source")
                and r.get("date", "") > RETRIEVED]
    regular = [r for r in rankable if not is_bounty(r)]
    bounty = [r for r in rankable if is_bounty(r)]
    rank_key = lambda r: -(guarantee_value(r) / float(r["buyin"]))
    regular.sort(key=rank_key)
    bounty.sort(key=rank_key)

    body.append('<div class="panel"><h2>The short version</h2><ul class="clean">')
    summary_items = [
        "The official Venetian schedule capture contains %d rows; all %d linked structure sheets were read. The canonical dashboard classifies %d Venetian rows as confirmed under standard S1 and %d as multi-entry. S1 is a rules-based screen, not an explicit freezeout promise: no sheet states a one-entry maximum. See the per-row evidence and the open limitation on the Verification and Flagged for review pages." % (len(VEN), len(META.get("sheets", {})), len(ven_confirmed), len(ven_multi)),
        "The recommended dates are %s to %s (%d nights; seven playing days, checkout the next day). This is an automatically selected research scenario, not traveler-provided dates or budget preferences. Its basis is %d Venetian full-field entries with about %s in published guarantees plus %d satellites; these totals are not winnings forecasts and do not mean every event can be played." % (esc(pretty_date(TRIP["check_in"])), esc(pretty_date(TRIP["check_out"])), TRIP["nights"], TRIP.get("entries_in_window", 0), money(TRIP.get("guarantee_sum_in_window")), TRIP.get("satellites_in_window", 0)),
        "The upcoming-value tables below include only future-dated Venetian full-field rows (after the latest source-capture date) whose S1 verdict, listed buy-in, house fee and guarantee are all present. Their guarantee-to-buy-in ratio is descriptive arithmetic only. Bounty/PKO rows are placed in a separate table; multi-flight, satellite and restart formats are not mixed into the ordinary-event ranking.",
        "A date-matched, itemized hotel quote is not available for this exact stay and occupancy. The dated log preserves differing snapshots, but those are not comparable to one another or to the selected stay. The trip calculator deliberately remains incomplete until the actual stay's hotel cost is known.",
        "The room-fee and tax evidence is linked on the Hotels page. Hotel quality is a displayed property tier, not an independent quality score; the automatic budget ceiling is based on an older dated observation, not a traveler-approved cap.",
        "Only on-property hotel-to-poker-room walks have verified zero-minute routes. Cross-property walking times remain blank/flagged. Official event finish times are not published, so a second same-day event is only a conditional fallback.",
        "The daily source-capture and monitoring workflows are scheduled, but the checked-in value-level monitor summary currently records no live value-level run. Until a run is recorded, no change badge means not yet re-checked, not verified unchanged.",
        "%d rows across other venues/series still have unread entry terms; they remain explicitly unverified and are not included in the single-entry comparison." % len(UNREAD),
        "%d items are flagged for review. See each source-linked note before relying on any exception or missing value." % len(FLAGS),
    ]
    for item in summary_items:
        body.append("<li>%s</li>" % item)
    body.append("</ul></div>")

    body.append('<div class="grid">')
    for n, label in ((str(len(ALL_EVENTS)), "schedule rows"),
                     (str(len(VEN)), "Venetian rows"),
                     (str(len(WPT)), "Wynn / WPT rows"),
                     (str(len(ven_confirmed)), "Venetian rows classified under S1"),
                     (str(len(ven_multi)), "Venetian multi-entry rows"),
                     (str(len(UNREAD)), "rows with entry terms unread"),
                     (str(len(SATS)), "satellite rows"),
                     (str(len(FLAGS)), "flagged for review")):
        body.append('<div class="stat"><div class="num">%s</div><div class="lbl">%s</div></div>' % (n, esc(label)))
    body.append("</div>")

    body.append("<h2>Upcoming: highest descriptive guarantee-to-entry ratios, non-bounty S1 events</h2>")
    if regular:
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Date</th><th>Start</th><th>#</th><th>Event</th><th class="num">Total buy-in</th><th class="num">House fee</th><th class="num">Guarantee</th><th class="num">GTD &divide; buy-in</th><th>Source</th></tr></thead><tbody>')
        for r in regular[:12]:
            body.append("<tr><td class=\"nowrap\">%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td></tr>"
                        % (esc(pretty_date(r["date"])), esc(pretty_time(r["start"])), esc(r["event_no"]),
                           esc(r["name"]), money(r["buyin"]), esc(r["house_fee"]), money(guarantee_value(r)),
                           ratio_text(r), src_link(r["source"], "official structure sheet")))
        body.append("</tbody></table></div>")
    else:
        body.append('<p class="muted">No non-bounty rows meet the complete-data ranking gate.</p>')
    body.append('<p class="muted sm">Sorted by published guarantee &divide; listed total buy-in. This is a descriptive ratio, not a forecast or expected return. Rankings are withheld when buy-in, house fee, or guarantee is missing. Event restrictions and S1 caveats remain on each linked row.</p>')

    body.append("<h2>Upcoming bounty / PKO S1 events (separate comparison)</h2>")
    if bounty:
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Date</th><th>Start</th><th>#</th><th>Event</th><th class="num">Total buy-in</th><th class="num">House fee</th><th class="num">Guarantee</th><th class="num">GTD &divide; buy-in</th><th>Source</th></tr></thead><tbody>')
        for r in bounty[:10]:
            body.append("<tr><td class=\"nowrap\">%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td></tr>"
                        % (esc(pretty_date(r["date"])), esc(pretty_time(r["start"])), esc(r["event_no"]),
                           esc(r["name"]), money(r["buyin"]), esc(r["house_fee"]), money(guarantee_value(r)),
                           ratio_text(r), src_link(r["source"], "official structure sheet")))
        body.append("</tbody></table></div>")
        body.append('<p class="muted sm">The bounty table is separate because the guaranteed pool may include bounty amounts. This ratio does not value bounty payouts and is not a forecast.</p>')
    else:
        body.append('<p class="muted">No bounty/PKO rows meet the complete-data ranking gate.</p>')

    body.append("<h2>What to do before deciding</h2>")
    body.append('<ol class="clean"><li>Request written event-specific maximum-entry/no-rebuy/no-add-on terms before treating S1 as a freezeout guarantee.</li>'
                '<li>Choose actual dates, occupancy, budget and a hotel quality floor; current controls are scenario defaults, not traveler preferences.</li>'
                '<li>Obtain an official booking checkout total for that same stay, including room charge, mandatory resort fee, tax, parking and cancellation deadline.</li>'
                '<li>Plan one event per day first. Add a conditional second only when actual event duration leaves a realistic exit and registration window.</li>'
                '<li>Reconfirm schedules, structure sheets, room policies and hotel terms before non-refundable payment.</li></ol>')
    write("pages/executive-summary.html", page("Executive summary", "".join(body),
                                               "executive-summary.html", 1))

def build_requirements():
    """Line-by-line traceability from the project brief to the published site (session 0fd4c550)."""
    rows = REQUIREMENTS.get("rows") or []
    by_status = {}
    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    body = ["<h1>Requirements: what was asked, what is on the site, what is blocked</h1>"]
    body.append(SEARCH_BAR % ("Search a requirement, a page name, a flag...", ""))
    body.append('<p class="muted">%s</p>' % esc(REQUIREMENTS.get("note", "")))
    chips = []
    for st in ("implemented", "implemented, limit published", "blocked on an official source"):
        n = by_status.get(st, 0)
        if not n:
            continue
        chips.append('<button type="button" class="pill %s" data-q="%s">%s: %d</button>'
                     % ("pill-ok" if st == "implemented" else ("pill-warn" if "limit" in st else "pill-bad"),
                        esc(st), esc(st), n))
    body.append('<p>%s <span class="muted sm">Each chip filters this table to that status.</span></p>'
                % " ".join(chips))
    body.append('<div class="panel"><h2>What each status means</h2><div class="kv">')
    for st, meaning in (REQUIREMENTS.get("statuses") or {}).items():
        body.append("<dt>%s</dt><dd>%s</dd>" % (esc(st), esc(meaning)))
    body.append('</div></div>')
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>#</th><th>Requirement, as asked</th>'
                '<th>Status</th><th>Where it lives</th><th>Evidence / source</th><th>What the site does, and the '
                'limit it publishes</th></tr></thead><tbody>')
    for r in rows:
        cls = ("pill-ok" if r["status"] == "implemented"
               else "pill-warn" if "limit" in r["status"] else "pill-bad")
        body.append('<tr data-status="%s"><td>%s</td><td><b>%s</b></td>'
                    '<td><span class="pill %s">%s</span></td><td>%s</td><td>%s</td><td class="sm">%s</td></tr>'
                    % (esc(r["status"]), esc(r["id"]), esc(r["requirement"]), cls, esc(r["status"]),
                       esc(r["where"]), src_link(r["evidence"], "open it"), esc(r["note"])))
    body.append("</tbody></table></div>")
    body.append('<div class="warnbox">The rows marked <i>blocked on an official source</i> are not unfinished '
                'work in the ordinary sense: they are the places where the brief asks for a number the properties '
                'do not publish - an expected finish time, a walking time between two hotels, a dated room rate '
                'for the stay. Filling those cells would mean inventing them, so the cell stays blank, the flag '
                'stays open, and the maps or booking link that settles the question in sixty seconds is printed '
                'beside it.</div>')
    write("pages/requirements.html", page("Requirements traceability", "".join(body), "requirements.html", 1,
                                          TABLE_JS_INIT))

def build_questions():
    body = ["<h1>Questions, answers and what is still missing</h1>"]
    body.append('<p class="muted">%d questions that have to be answered before a decision is reasonable. For each: '
                'what the verified data already answers, what is still missing, and how to close the gap.</p>'
                % len(QUESTIONS))
    for q in QUESTIONS:
        body.append('<div class="panel"><h3>%s. %s</h3><div class="kv">'
                    '<dt>What we have</dt><dd>%s</dd>'
                    '<dt>What is missing</dt><dd>%s</dd>'
                    '<dt>How to find it</dt><dd>%s</dd></div></div>'
                    % (esc(q["id"]), esc(q["q"]), esc(q["have"]), esc(q["missing"]), esc(q["how"])))
    write("pages/questions.html", page("Questions", "".join(body), "questions.html", 1))


def build_suggestions():
    body = ["<h1>Suggestions: choose a path before anything changes</h1>"]
    body.append('<p class="muted">%d improvements, each with the options and what each one costs you. Pick one '
                'option per suggestion and the list at the bottom becomes your change request. Nothing on this site '
                'is altered until you ask for it.</p>' % len(SUGGESTIONS))
    body.append('<div id="sug">')
    for s in SUGGESTIONS:
        body.append('<div class="opt"><h3>%s. %s</h3><p class="muted sm"><b>Problem:</b> %s</p>'
                    % (esc(s["id"]), esc(s["title"]), esc(s["problem"])))
        for i, o in enumerate(s["options"]):
            body.append('<label><input type="radio" name="%s" value="%d" data-title="%s" data-label="%s"> %s</label>'
                        % (esc(s["id"]), i, esc(s["title"]), esc(o), esc(o)))
        body.append('<p class="muted sm"><b>Effect:</b> %s</p></div>' % esc(s["effect"]))
    body.append("</div>")
    body.append('<div class="result" id="spicked"></div>')
    write("pages/suggestions.html", page("Suggestions", "".join(body), "suggestions.html", 1))


def build_flagged():
    body = ["<h1>Flagged for review</h1>"]
    body.append(SEARCH_BAR % ("Search flags, areas, items...", ""))
    body.append('<p class="muted">%d items. Each one is something that could not be confirmed from an official '
                'source, or a defect found in an official source. Every row links to the source involved. '
                'None of these blocks the site; they are here so you can check them yourself.</p>' % len(FLAGS))
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>ID</th><th>Area</th><th>Item</th>'
                '<th>Detail</th><th>Source</th></tr></thead><tbody>')
    for f in FLAGS:
        body.append("<tr><td class=\"nowrap\"><b>%s</b></td><td>%s</td><td><b>%s</b></td>"
                    "<td class=\"sm\">%s</td><td>%s</td></tr>"
                    % (esc(f["id"]), esc(f["area"]), esc(f["title"]), esc(f["detail"]),
                       src_link(f["source"], "source")))
    body.append("</tbody></table></div>")
    write("pages/flagged-review.html", page("Flagged for review", "".join(body), "flagged-review.html", 1))


def build_method():
    body = ["<h1>Method and source ledger</h1>"]
    body.append(SEARCH_BAR % ("Search sheets, sources, rules...", ""))
    body.append('<div class="panel"><h2>The verification rule</h2><ul class="clean">'
                '<li>Every value on this site was read from an official source - the casino\'s own site or its own '
                'PDF - during this session, on %s.</li>' % esc(RETRIEVED))
    body.append('<li>An event is labelled <span class="pill pill-ok">Confirmed single-entry</span> only when an '
                'official source states a one-entry, no-re-entry or freezeout limit.</li>')
    body.append('<li>It is labelled <span class="pill pill-bad">Multi-entry</span> when the official text allows '
                're-entry, an add-on, or more than one starting flight.</li>')
    body.append('<li>It is labelled <span class="pill pill-warn">Entry cap not stated</span> when the official sheet '
                'is silent. Silence is never promoted to single-entry.</li>')
    body.append('<li>A value that no official source states is left blank and appears on the '
                '<a href="flagged-review.html">Flagged page</a>.</li>')
    body.append('<li>The build fails if a table row lacks an official source link, or if an internal link is broken.</li>')
    body.append("</ul></div>")
    sheets = META["sheets"]
    body.append('<div class="panel"><h2>Venetian structure sheets: all %d read</h2>' % len(sheets))
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>#</th><th>Covers</th><th>Event numbers</th>'
                '<th class="num">Buy-in</th><th>Guarantee</th><th>Entry rule</th><th>Official text</th>'
                '<th>PDF</th></tr></thead><tbody>')
    for k in sorted(sheets, key=lambda x: int(x)):
        s = sheets[k]
        body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td>"
                    "<td class=\"quote\">%s</td><td>%s</td></tr>"
                    % (esc(k), esc(s["title"]), esc(s["events"]), money(s["buyin"]),
                       esc(s["gtd"]) or '<span class="blank">none</span>',
                       '<span class="pill pill-%s">%s</span>' % (RULE_CLASS[s["rule"]], esc(RULE_LABEL[s["rule"]])),
                       esc(s["excerpt"]), src_link(s["url"], "PDF")))
    body.append("</tbody></table></div></div>")
    body.append('<div class="panel"><h2>Source ledger</h2>')
    led = [("Venetian DeepStack Extravaganza IV schedule", META["schedule_page"], "94 rows: dates, times, event numbers, names, structure links"),
           ("Venetian structure sheets 1-37", SHEET_URL := ("https://www.venetianlasvegas.com/content/dam/vlvweb/"
                                                            "casino/poker/deepstack/2026/structures/"
                                                            "dse_nov_2026-structure_1.pdf"), "buy-in split, guarantee, chips, levels, late registration, entry rules"),
           ("WPT World Championship schedule (Wynn)", "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf", "136 rows: dates, times, events, buy-ins, guarantees, chips, levels"),
           ("WPT World Championship structures (Wynn)", "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf", "terms and conditions, registration and re-entry text"),
           ("Wynn Las Vegas poker room", "https://www.wynnlasvegas.com/casino/poker", "series dates, daily tournament policy"),
           ("Caesars Palace daily tournament flyer", "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf", "four daily events, buy-ins, add-on, re-entry rule, fee split"),
           ("Caesars Palace casino page", "https://www.caesars.com/caesars-palace/casino", "poker room open 24/7 with daily tournaments"),
           ("Horseshoe Las Vegas casino page", "https://www.caesars.com/horseshoe-las-vegas/casino", "Hall of Fame Poker Room, 20 tables, six daily tournament times"),
           ("Resorts World - All Resort, No Fees", "https://www.rwlasvegas.com/offers/all-resort-no-fees/", "$55 daily resort fee, waiver terms, parking, cancellation"),
           ("Resorts World poker room", "https://www.rwlasvegas.com/gaming/poker-room/", "poker room exists; no schedule retrieved"),
           ("South Point poker room", "https://southpointcasino.com/casino/poker-room", "four daily tournaments, $120 and $300 buy-ins"),
           ("Venetian resort fee", "https://www.venetianlasvegas.com/resort/resort-fee.html", "$55 plus tax per night and what it includes"),
           ("Clark County transient lodging ordinance", TAX["source"], "13.38% combined rate for a resort hotel in the primary gaming corridor")]
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Source</th><th>What it was used for</th>'
                '<th>Link</th></tr></thead><tbody>')
    for name, url, used in led:
        body.append("<tr><td><b>%s</b></td><td class=\"sm\">%s</td><td>%s</td></tr>"
                    % (esc(name), esc(used), src_link(url, "open")))
    body.append("</tbody></table></div></div>")
    body.append('<div class="panel"><h2>What this audit did not do</h2><ul class="clean">'
                '<li>It did not read the entry terms of every WPT festival event individually (13 of them were read).</li>'
                '<li>It did not retrieve any official schedule for Bellagio, MGM Grand, ARIA or Planet Hollywood; '
                'those official pages returned errors.</li>'
                '<li>It did not capture a single dated room rate; official booking engines require JavaScript.</li>'
                '<li>It did not measure or estimate any cross-property walking time.</li>'
                '<li>It did not estimate a finish time for any event, because no official source publishes one. The '
                'overlap check uses the official start time and the official late-registration close time.</li></ul></div>')
    body.append('<div class="panel"><h2>Limits of the automation, stated plainly</h2><ul class="clean">'
                '<li><b>The monitor detects change; it does not rewrite rows.</b> '
                '<code>scripts/recheck_ea99006a.py</code> re-fetches all %d official URLs, hashes them and records '
                'what changed. It does not parse a changed schedule back into table rows, because doing that '
                'silently would risk inventing values. When a source changes, the row is flagged on the '
                '<a href="monitor.html">Source monitor</a> page and a person re-reads it.</li>'
                '<li><b>There is no live hotel rate lookup.</b> Every official booking engine here is a JavaScript '
                'application, so no rate can be read from an official source without a browser. The hotels page '
                'gives you the dated booking link and a calculator; you paste the rate you see and it is stored as '
                'a dated log entry.</li>'
                '<li><b>No value is ever inferred.</b> Where an official source is silent the cell is empty and the '
                'item is on the <a href="flagged-review.html">Flagged for review</a> page.</li></ul></div>'
                % len(load("last_checked.json")))
    body.append(archive_block(1))
    write("pages/method.html", page("Method and sources", "".join(body), "method.html", 1))


def build_monitor():
    ledger = LEDGER or load("last_checked.json")
    changelog = load("change_log.json")
    body = ["<h1>Source monitor</h1>"]
    body.append(SEARCH_BAR % ("Search sources, rooms, changes...", ""))
    body.append('<p class="muted">Every official URL behind a table row is re-fetched on a schedule, hashed and '
                'compared with the previous run. %d URLs are under monitor. A source that changes is listed here '
                'and its rows should be re-verified before you rely on them.</p>' % len(ledger))
    count = {}
    for e in ledger.values():
        k = e.get("status", "unknown")
        count[k] = count.get(k, 0) + 1
    body.append('<div class="grid">')
    for k in sorted(count):
        body.append('<div class="stat"><div class="num">%d</div><div class="lbl">%s</div></div>' % (count[k], esc(k)))
    body.append("</div>")
    body.append("<h2>Morning room feed</h2>")
    body.append('<p class="muted sm">Each morning the scheduled re-check re-reads every official schedule source '
                'for every Strip room tracked here and records what it saw. A row marked <i>changed</i> means a '
                'human should re-read that source before trusting the table.</p>')
    if MORNING_FEED and MORNING_FEED.get("rooms"):
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Room</th><th>Official schedule source</th>'
                    '<th>Last morning check (UTC)</th><th class="num">URLs</th><th class="num">OK</th>'
                    '<th class="num">Changed</th><th class="num">Failed</th><th>Status</th></tr></thead><tbody>')
        for room in MORNING_FEED["rooms"]:
            st = "ok" if not room.get("failed") and not room.get("changed") else ("bad" if room.get("failed") else "warn")
            body.append('<tr><td><b>%s</b></td><td>%s</td><td class="nowrap">%s</td><td class="num">%s</td>'
                        '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
                        '<td><span class="pill pill-%s">%s</span></td></tr>'
                        % (esc(room["room"]), src_link(room["source"], "official page"),
                           esc(room.get("checked_at") or "not yet run"),
                           esc(room.get("urls", 0)), esc(room.get("ok", 0)),
                           esc(room.get("changed", 0)), esc(room.get("failed", 0)), st,
                           "all sources read" if st == "ok" else ("changed - re-verify" if st == "warn" else "fetch failed")))
        body.append("</tbody></table></div>")
    else:
        body.append('<div class="warnbox">The first morning feed has not been recorded yet. The scheduled '
                    'recheck-ea99006a job writes <code>data/ea99006a/morning_feed.json</code> on its first run; '
                    'until then the per-URL ledger below is the record.</div>')
    if changelog:
        body.append("<h2>Changes detected</h2>")
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Detected at (UTC)</th>'
                    '<th>What it backs</th><th>Old hash</th><th>New hash</th><th>Size</th>'
                    '<th>Link</th></tr></thead><tbody>')
        shown_changes = [c for c in changelog
                         if isinstance(c, dict) and "{" not in c.get("url", "")
                         and "google.com/maps" not in c.get("url", "")]
        for c in reversed(shown_changes[-200:]):
            # Read defensively (see CHANGED_AT): the value-level monitor historically wrote
            # "at"/"previous_sha256"/"sha256" keys. Accept both spellings so a monitor-written
            # entry can never break the build; missing hashes render as "-".
            _old = (c.get("old_sha256") or c.get("previous_sha256") or "")[:12] or "-"
            _new = (c.get("new_sha256") or c.get("sha256") or "")[:12] or "-"
            body.append('<tr><td class="nowrap">%s</td><td>%s</td><td><code>%s</code></td>'
                        '<td><code>%s</code></td><td>%s</td><td>%s</td></tr>'
                        % (esc(c.get("changed_at") or c.get("at") or ""), esc(c.get("label") or c.get("kind") or ""),
                           esc(_old), esc(_new),
                           esc("%s to %s bytes" % (c.get("old_bytes"), c.get("new_bytes"))),
                           src_link(c["url"], "open")))
        body.append("</tbody></table></div>")
    else:
        body.append('<div class="okbox">No change has been detected yet. The monitor records the first set of '
                    'hashes on its first scheduled run and compares from then on.</div>')
    body.append("<h2>Value-level changes</h2>")
    n_hash = sum(1 for v in ledger.values() if v.get("status") == "changed")
    body.append('<p class="muted">Hashing a whole page only tells you its bytes moved. On these sites that happens '
                "for reasons that have nothing to do with this trip: the page-hash job flagged " + str(n_hash)
                + " of " + str(len(ledger)) + ' URLs as "changed" in one run while not one schedule value differed. '
                "<code>scripts/monitor_b3be876c.py</code> therefore compares the <b>sentence that carries each "
                "published value</b>. A row is marked on the tables only when that sentence changes, and the "
                "previous sentence is kept here so the difference can be read.</p>")
    if VALCH:
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Detected</th><th>Venue</th>'
                    "<th>Event</th><th>Value</th><th>Was</th><th>Now</th><th>Rows to re-verify</th><th>Source</th>"
                    "</tr></thead><tbody>")
        for c in VALCH:
            body.append('<tr><td class="nowrap">' + esc(c.get("detected") or "") + "</td><td>"
                        + esc(c.get("venue") or "") + "</td><td>" + esc(c.get("event") or "") + "</td>"
                        + "<td><code>" + esc(c.get("value") or "") + "</code></td>"
                        + '<td><span class="quote">' + esc(c.get("old_excerpt") or "not recorded")[:240]
                        + '</span></td><td><span class="quote">'
                        + esc(c.get("new_excerpt") or "not recorded")[:240] + "</span></td><td>"
                        + esc(", ".join(str(n) for n in (c.get("event_nos") or [])) or (c.get("event_no") or "-"))
                        + "</td><td>" + src_link(c.get("url"), "official page") + "</td></tr>")
        body.append("</tbody></table></div>")
        body.append('<div class="badbox"><b>' + str(len(VALCH)) + " value(s) changed.</b> Re-read the affected rows "
                    "against the official source before relying on them, and re-run "
                    "<code>scripts/integrate_b3be876c.py</code> so the tables are rebuilt from the new text. Until "
                    "that happens the published number stays as it was and the row is marked.</div>")
    elif MONRUN.get("run"):
        body.append('<div class="okbox"><b>No official value has changed since the run of '
                    + esc(str(MONRUN.get("run"))[:10]) + ".</b> The sentences behind every published buy-in, house "
                    "fee, guarantee, start time and registration close still match the text stored with the row. A "
                    "re-fetch that changes only the page wrapper, a token or a cookie banner is recorded as a page "
                    "refresh and marks no row.</div>")
    else:
        body.append('<div class="warnbox"><b>No value-level run has been recorded yet.</b> The sandbox that authors '
                    "this repo cannot open a connection to the casino hosts, so the value monitor has only been run "
                    "offline against fixtures - which is how its detection was tested: an intact capture reports 0 "
                    "changes, a replaced structure sheet reports 8, and a buy-in moved from $300 to $325 is caught. "
                    "The first scheduled run on a runner with internet access writes the real ledger. Until then no "
                    'row carries a change mark, and the absence of a mark means <b>"not yet re-checked"</b>, never '
                    '"verified unchanged". See the <a href="https://github.com/karagemop466-tech/Poker5/actions">'
                    "scheduled runs</a>.</div>")
    body.append('<div class="panel"><h2>What a change does and does not do</h2>'
                "<ul><li>It marks the row and takes it out of the ranking, because a value that moved is a value "
                "that must be read again.</li>"
                "<li>It never rewrites a number on its own: the published figure is replaced only when the document "
                "is re-read and the verdict is re-derived.</li>"
                "<li>It appends to the dated rate log rather than overwriting a rate, so a price history survives "
                "the change.</li></ul></div>")
    body.append("<h2>All monitored sources</h2>")
    body.append('<div class="tablewrap"><table class="data"><thead><tr><th>What it backs</th><th>URL</th>'
                '<th>Status</th><th>Last checked (UTC)</th><th>SHA-256</th></tr></thead><tbody>')
    for url in sorted(ledger):
        e = ledger[url]
        st = e.get("status", "unknown")
        cls = "ok" if st == "ok" else ("bad" if st in ("error", "changed") else "warn")
        body.append('<tr><td>%s</td><td>%s</td><td><span class="pill pill-%s">%s</span></td>'
                    '<td class="nowrap">%s</td><td><code>%s</code></td></tr>'
                    % (esc(e.get("label") or ""), src_link(url, url[:90]), cls, esc(st),
                       esc(e.get("last_checked") or "not yet run"),
                       esc((e.get("sha256") or "")[:12] or "-")))
    body.append("</tbody></table></div>")
    write("pages/monitor.html", page("Source monitor", "".join(body), "monitor.html", 1))



SKIP_DIRS = {".git", "node_modules", "__pycache__", ".github", ".arena", ".cache", ".local"}

FOLDER_NOTE = {
    "data": "Machine-readable inputs. One folder per session; never edited across sessions.",
    "scripts": "One generator, one validator and one source monitor per session.",
    "assets": "The published stylesheet and the site JavaScript (filtering, calculators, rate log).",
    "pages": "The published subpages of the root site.",
    "pages/venues": "One page per poker venue.",
    "work": "Working notes for the current session (audits, drafts). Not published.",
    "docs": "Session 581fea93 official-source site - preserved, not edited.",
    "site": "Session b1f117c3 planner - preserved, not edited.",
}

SESSION_NOTE = {
    "ea99006a": "this session (integration + verification)",
    "c6087e2c": "earlier session - the original root site generator",
    "581fea93": "earlier session - official-source site in /docs",
    "b1f117c3": "earlier session - Strip poker planner in /site",
    "cd5ab298": "earlier session - research dashboard",
    "6d1e0039": "earlier session - verified dashboard with scheduled re-check",
    "afff1fc9": "earlier session - official-source planner",
    "b50aa7f5": "earlier session - strict-entry research",
    "aa83f1e1": "earlier session - strict-entry planner",
    "053f694f": "earlier session - early dashboard",
    "de0bebd4": "earlier session - early dashboard",
    "a9d1e02d": "earlier session - source-audited planner",
    "443e914d": "earlier session",
    "359e3f96": "earlier session",
    "bafafd7c": "earlier session",
    "0a0e3c6d": "earlier session",
    "18e480cb": "earlier session",
}


def owner_of(rel):
    for key in SESSION_NOTE:
        if key in rel:
            return key
    return ""


def build_repo_review():
    rows = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        rel_dir = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
        for fn in sorted(filenames):
            rel = fn if rel_dir == "." else "%s/%s" % (rel_dir, fn)
            path = os.path.join(dirpath, fn)
            try:
                size = os.path.getsize(path)
                with open(path, "rb") as fh:
                    lines = sum(1 for _ in fh)
            except OSError:
                continue
            rows.append((rel, size, lines))
    total_bytes = sum(r[1] for r in rows)
    body = ["<h1>Repository review</h1>"]
    body.append('<p class="muted">A file-by-file inventory of the repository, generated from the working tree at '
                'build time. %d files, %s bytes total. Every file is listed; nothing is summarised away.</p>'
                % (len(rows), format(total_bytes, ",d")))
    body.append('<div class="panel"><h2>How the repository is organised</h2><div class="tablewrap">'
                '<table class="data" data-nosrc="1"><thead><tr><th>Folder</th><th>What it is</th>'
                '</tr></thead><tbody>')
    for k in sorted(FOLDER_NOTE):
        body.append("<tr><td><code>%s/</code></td><td>%s</td></tr>" % (esc(k), esc(FOLDER_NOTE[k])))
    body.append("</tbody></table></div></div>")
    body.append('<div class="panel"><h2>Findings from the review</h2><ul class="clean">')
    for f in (
        "The root site is generated by <code>scripts/build_ea99006a.py</code> from "
        "<code>data/ea99006a/</code>, validated by <code>scripts/check_ea99006a.py</code> and monitored by "
        "<code>scripts/recheck_ea99006a.py</code>. Earlier generators remain in <code>scripts/</code> and are not "
        "deleted, but they no longer produce the root site.",
        "Thirteen pull requests were merged before this session and one (PR #30) was open and idle. This session "
        "took over the root site instead of adding another dashboard folder, so there is one published answer per "
        "question rather than several conflicting ones.",
        "Every session folder other than <code>data/ea99006a/</code>, <code>work/</code> and the root site files "
        "is treated as read-only here.",
        "A compiled Python file, <code>tools/__pycache__/data.cpython-311.pyc</code>, is committed in the tree. It "
        "was flagged by an earlier session and is left in place rather than deleted without that session's say.",
        "Session 6bc143b9 (2026-11-19) found and fixed a generator conflict: three builders and three "
        "workflows could each overwrite the published root site, and CI validated none of the published output. "
        "Now <code>scripts/build_ea99006a.py</code> is the only root-site generator, the morning capture job "
        "commits capture data only, and Quality checks regenerates the site and fails on drift (see flags F28-F31).",
        "Session folders disagree with each other on three numbers: the count of confirmed single-entry Venetian "
        "events (20 / 30 / 64 / 0), the Bellagio Saturday buy-in ($1,000 / $1,100 / $600) and the Wynn resort fee "
        "($55 / unverified). This build resolves them from official sources and records the outcomes on the "
        "<a href=\"flagged-review.html\">Flagged for review</a> page.",
    ):
        body.append("<li>%s</li>" % f)
    body.append("</ul></div>")
    body.append("<h2>Every file in the repository</h2>")
    body.append('<div class="filters"><input type="search" id="q" placeholder="Search file paths..." '
                'aria-label="Search files"><span class="count" id="count"></span></div>')
    body.append('<div class="tablewrap"><table class="data" id="tbl" data-nosrc="1"><thead><tr><th>Path</th>'
                '<th class="num">Bytes</th><th class="num">Lines</th><th>Session</th><th>Note</th>'
                '</tr></thead><tbody>')
    for rel, size, lines in rows:
        owner = owner_of(rel)
        note = SESSION_NOTE.get(owner, "shared / repository-level file")
        tag = esc(owner) if owner else '<span class="blank">shared</span>'
        body.append('<tr data-search="%s"><td><code>%s</code></td><td class="num">%s</td>'
                    '<td class="num">%s</td><td>%s</td><td class="sm">%s</td></tr>'
                    % (esc(rel.lower()), esc(rel), format(size, ",d"), format(lines, ",d"), tag, esc(note)))
    body.append("</tbody></table></div>")
    write("pages/repo-review.html", page("Repository review", "".join(body), "repo-review.html", 1,
                                         TABLE_JS_INIT))


def build_redirects():
    """The retired 251c122f build left four root pages behind that describe an
    older verdict. They now redirect to the canonical page so no reader lands on
    a contradictory copy."""
    for rel, target, label in (
        ("pages/qa.html", "questions.html", "Questions"),
        ("pages/flagged.html", "flagged-review.html", "Flagged for review"),
        ("pages/multientry.html", "tournaments-double.html", "Multi-entry / advantage"),
        ("pages/sources.html", "method.html", "Method and sources"),
    ):
        stub = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta http-equiv="refresh" content="0; url=%s">'
                '<title>moved | Poker5</title></head><body>'
                '<p>This page moved to <a href="%s">%s</a>.</p></body></html>'
                % (target, target, label))
        write(rel, stub)


def build_verification():
    """Value-level verification log: standard, spot checks, reversals, disagreements, hotel figures."""
    body = ["<h1>Verification log</h1>"]
    body.append(SEARCH_BAR % ("Search the verification log...", ""))
    body.append("<p class=\"muted\">Every published value on this site comes with the official sentence behind it, "
                "the date that sentence was read, and a link to re-check it by hand. This page is the part of that "
                "machinery that is about values rather than pages: the standard the verdicts apply, the rows "
                "re-read field by field against their source document, the rows taken out of the single-entry set "
                "once the whole rule list had been read, and the places where two official captures of the same "
                "schedule disagree. The per-row version of this is on every table, under \"Rule fields and verdict "
                "basis\".</p>")
    counts = VERIF.get("counts") or {}
    cells = "".join("<dt>" + esc(k.replace("_", " ")) + "</dt><dd><b>" + esc(str(v)) + "</b></dd>"
                    for k, v in sorted(counts.items()))
    body.append("<div class=\"panel\"><h2>State of the published set</h2><div class=\"kv\">" + cells
                + "<dt>structure sheets read</dt><dd><b>" + str(len(META.get("sheets") or [])) + "</b></dd>"
                + "<dt>URLs under daily monitor</dt><dd><b>" + str(len(LEDGER)) + "</b></dd>"
                + "<dt>value-level changes open</dt><dd><b>" + str(len(VALCH)) + "</b></dd></div></div>")
    # 25481cd8: full schedule re-read against the official page, row by row (scripts/recheck_schedule_25481cd8.py)
    _sr = _opt(DATA, "schedule_recheck.json", {})
    if _sr:
        _bad = [r for r in (_sr.get("rows") or []) if r.get("result") != "match"]
        body.append("<div class=\"panel\"><h2>Venetian schedule re-check, " + esc(_sr.get("checked_on", "")) + "</h2>"
                    "<p>Every row of the official DeepStack Extravaganza IV schedule page was read again and compared field by field "
                    "(date, start time, event number, name, buy-in, guarantee, structure-sheet number) with the stored row. "
                    "Source: <a href=\"" + esc(_sr.get("official_source", "")) + "\" rel=\"noopener\">official Venetian schedule page</a>. "
                    "Method and per-row result: <code>data/ea99006a/schedule_recheck.json</code>.</p>"
                    "<div class=\"kv\"><dt>rows compared</dt><dd><b>" + str(_sr.get("rows_compared", 0)) + "</b></dd>"
                    "<dt>rows matching</dt><dd><b>" + str((_sr.get("rows_compared", 0) or 0) - len(_bad)) + "</b></dd>"
                    "<dt>mismatches</dt><dd><b>" + str(len(_bad)) + "</b></dd></div></div>")
    # 0fd4c550: the recommended window re-read row by row from the live schedule page, with the
    # field-by-field result kept next to the row it came from.
    _wv = _opt(DATA, "window_verification_0fd4c550.json", {})
    if _wv.get("rows"):
        _wbad = [r for r in _wv["rows"] if r.get("status") != "match"]
        body.append("<div class=\"panel\"><h2>Recommended window, re-read from the live page on "
                    + esc(_wv.get("read_at", "")) + "</h2>"
                    "<p>" + esc(_wv.get("note", "")) + "</p>"
                    "<div class=\"kv\"><dt>window</dt><dd>" + esc(_wv.get("window", "")) + "</dd>"
                    "<dt>rows on the official page</dt><dd><b>" + str(_wv.get("rows_on_page", 0)) + "</b></dd>"
                    "<dt>rows matching the published record</dt><dd><b>" + str(_wv.get("rows_matched", 0)) + "</b></dd>"
                    "<dt>value disagreements</dt><dd><b>" + str(len(_wbad)) + "</b></dd>"
                    "<dt>fields compared</dt><dd>" + esc(", ".join(_wv.get("fields_checked") or [])) + "</dd>"
                    "<dt>read by</dt><dd>" + esc(_wv.get("reader", "")) + "</dd>"
                    "<dt>method</dt><dd><code>scripts/verify_window_0fd4c550.py</code> against "
                    "<code>data/ea99006a/window_live_2026-11-19_0fd4c550.tsv</code></dd></div>")
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Date</th><th>Start</th>'
                    '<th>#</th><th>Event, as the official page words it</th><th class="num">Sheet</th>'
                    '<th>Fields compared</th><th>Verdict</th><th>Published entry-rule label</th>'
                    '<th>Official source</th></tr></thead><tbody>')
        for r in _wv["rows"]:
            l = r["live"]
            det = "; ".join("%s %s" % (f["field"], "ok" if f["match"] else ("review: " + f.get("note", "")))
                            for f in r.get("fields") or [])
            body.append("<tr><td class=\"nowrap\">%s</td><td>%s</td><td>%s</td><td>%s</td>"
                        "<td class=\"num\">%s</td><td class=\"sm\">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (esc(l["date"]), esc(l["start"]), esc(l["event_no"]), esc(l["name"]),
                           esc(l["sheet"]), esc(det),
                           '<span class="pill pill-ok">identical</span>' if r["status"] == "match"
                           else '<span class="pill pill-bad">differs</span>',
                           esc(r.get("entry_rule") or "not a Venetian row"),
                           src_link(_wv.get("url") or "", "schedule page")))
        body.append("</tbody></table></div>")
        body.append('<p class="muted sm">A "review" note means the page and the record word the same event '
                    'differently; the figures behind it still matched. Value disagreements would be published here '
                    'as <i>differs</i> and opened as a flag rather than edited into the table.</p></div>')
    body.append("<div class=\"panel\"><h2>The standard a verdict applies (" + esc(STD["id"]) + ")</h2>"
                "<p>" + esc(STD["text"]) + "</p>"
                "<div class=\"warnbox\"><b>What this standard cannot do.</b> " + esc(STD["limitation"])
                + " A structure sheet is an announcement, not a contract: every one of them reserves the right for "
                "management to change the tournament. A confirmed label therefore means \"the published rules grant "
                "no second entry on the day they were read\", not \"the room promises a freezeout next week\".</div>"
                "<p class=\"muted sm\">Silence is never promoted to confirmation: a sheet that says nothing about "
                "re-entry is published as \"cap not stated\" and stays out of the ranking, and a sheet that grants "
                "a further entry for money moves the row to the multi-entry section, whatever its headline says.</p>"
                "</div>")
    marks = [r for r in VEN if r.get("spot_check")]
    if marks:
        body.append("<h2>Rows re-read field by field against the official document</h2>")
        body.append("<p class=\"muted sm\">Every row on the tournament pages carries its rule fields; these are the "
                    "rows re-read by hand on the date shown, each published value compared with the sentence in the "
                    "source that is quoted beside it.</p>")
        body.append("<div class=\"tablewrap\"><table class=\"data\"><thead><tr><th>Date</th><th>#</th><th>Event</th>"
                    "<th>Field</th><th>Published value</th><th>Official sentence</th><th>Match</th><th>Read</th>"
                    "<th>Source</th></tr></thead><tbody>")
        for r in marks:
            for k, v in sorted((r.get("spot_check") or {}).get("fields", {}).items()):
                pub = v.get("published")
                if pub in (None, ""):
                    pubcell = "<td><span class=\"blank\">blank (nothing official states it)</span></td>"
                elif isinstance(pub, (int, float)):
                    pubcell = "<td class=\"num\">" + (money(pub) or "<span class=\"blank\">not stated</span>") + "</td>"
                else:
                    pubcell = "<td>" + esc(pub) + "</td>"
                verdict = ("<span class=\"pill pill-ok\">match</span>" if v.get("ok")
                           else "<span class=\"pill pill-bad\">differs</span>")
                body.append("<tr><td class=\"nowrap\">" + esc(pretty_date(r["date"])) + "</td><td>"
                            + esc(r.get("event_no") or "") + "</td><td>" + esc(r["name"]) + "</td>"
                            + "<td><code>" + esc(k) + "</code></td>" + pubcell
                            + "<td><span class=\"quote\">" + esc(v.get("excerpt") or "")[:300] + "</span></td>"
                            + "<td>" + verdict + "</td><td class=\"nowrap\">"
                            + esc(v.get("retrieved") or r.get("retrieved") or RETRIEVED) + "</td><td>"
                            + src_link(r["source"], "official sheet") + "</td></tr>")
        body.append("</tbody></table></div>")
    moved = (VERIF.get("integration") or {}).get("moved_out_of_single_entry") or []
    body.append("<h2>Rows taken out of the single-entry set (" + str(len(moved)) + ")</h2>")
    if moved:
        body.append("<p class=\"muted\">An earlier pass labelled these rows confirmed single-entry without reading "
                    "the numbered rule list of their own structure sheet. That rule list grants a further entry for "
                    "a fee, so the label was wrong and the row now sits in the multi-entry section. This is why the "
                    "count published here differs from <code>data/c6087e2c/</code>.</p>")
        body.append("<div class=\"tablewrap\"><table class=\"data\"><thead><tr><th>Date</th><th>#</th><th>Event</th>"
                    "<th>Old label</th><th>New label</th><th>Official sentence that moved it</th><th>Sheet</th>"
                    "<th>Source</th></tr></thead><tbody>")
        by_no = {}
        for r in VEN:
            by_no[(str(r.get("event_no")), r.get("date"))] = r
        for m in moved:
            row = by_no.get((str(m.get("event_no")), m.get("date"))) or {}
            ev = row.get("entry_evidence") or {}
            body.append("<tr><td class=\"nowrap\">" + esc(pretty_date(m.get("date") or "")) + "</td><td>"
                        + esc(m.get("event_no") or "") + "</td><td>"
                        + esc(m.get("name") or row.get("name") or "") + "</td>"
                        + "<td><span class=\"pill pill-ok\">confirmed single-entry</span></td>"
                        + "<td><span class=\"pill pill-bad\">multi-entry</span></td>"
                        + "<td><span class=\"quote\">" + esc(m.get("basis") or "")[:400] + "</span></td><td>"
                        + esc("sheet " + str(ev.get("sheet_no")) if ev.get("sheet_no") else "not recorded")
                        + "</td><td>" + src_link(row.get("source") or m.get("source"), "official sheet")
                        + "</td></tr>")
        body.append("</tbody></table></div>")
    else:
        body.append("<div class=\"panel\"><p>None outstanding: every row whose own sheet grants a further entry is "
                    "labelled multi-entry, and the record of why is kept in "
                    "<code>data/b3be876c/integration_report.json</code>.</p></div>")
    diffs = [r for r in ALL_EVENTS if r.get("guarantee_note")]
    body.append("<h2>Official sources that disagree (" + str(len(diffs)) + ")</h2>")
    if diffs:
        body.append("<p class=\"muted\">A row is only ranked once its total entry fee and its guarantee are both "
                    "confirmed. Where the schedule page and the structure sheet state different numbers, both are "
                    "kept, the row is not ranked and no recommendation is made.</p>")
        body.append("<div class=\"tablewrap\"><table class=\"data\"><thead><tr><th>Date</th><th>Event</th>"
                    "<th>Published value</th><th>Disagreement</th><th>State</th><th>Source</th></tr></thead><tbody>")
        for r in diffs:
            body.append("<tr><td class=\"nowrap\">" + esc(pretty_date(r.get("date") or "")) + "</td><td>"
                        + esc(r["name"]) + "</td><td class=\"num\">"
                        + (money(r.get("guarantee")) or "<span class=\"blank\">not stated</span>") + "</td><td>"
                        + "<span class=\"quote\">" + esc(r["guarantee_note"])[:300] + "</span></td>"
                        + "<td><span class=\"pill pill-warn\">not ranked, no recommendation</span></td><td>"
                        + src_link(r["source"], "official schedule") + "</td></tr>")
        body.append("</tbody></table></div>")
    else:
        body.append("<div class=\"panel\"><p>The two official captures of the schedule agree on every guarantee and "
                    "every buy-in in the set, so no money figure is in dispute. They disagreed about the "
                    "<i>labels</i>, which is the section above.</p></div>")
    body.append("<h2>Hotel figures verified against an official page</h2>")
    body.append("<div class=\"tablewrap\"><table class=\"data\"><thead><tr><th>Hotel</th><th>Figure</th>"
                "<th>Published value</th><th>Official sentence</th><th>Read</th><th>Limit of the figure</th>"
                "<th>Source</th></tr></thead><tbody>")
    for h in HOTELS:
        pairs = []
        if h.get("resort_fee"):
            pairs.append(("Resort fee / night", "$%.0f" % h["resort_fee"], h.get("resort_fee_text") or "",
                          h.get("resort_fee_source"), h.get("resort_fee_note") or "",
                          h.get("resort_fee_read") or RETRIEVED))
        if h.get("rate_floor"):
            quote = "rates will start as low as $%s" % format(int(h["rate_floor"]), ",d")
            if h.get("rate_floor_alt"):
                quote += " and $%s" % format(int(h["rate_floor_alt"]), ",d")
            quote += " and can be higher"
            pairs.append(("Poker suite rate / night", money(h["rate_floor"]) or "", quote,
                          h.get("rate_floor_source"), h.get("rate_caveat") or "",
                          h.get("rate_floor_read") or RETRIEVED))
        if h.get("cancel"):
            pairs.append(("Cancellation", esc(h["cancel"])[:110], h["cancel"], h.get("cancel_source"),
                          "stated on the terms page of one offer window, not on a general policy page", RETRIEVED))
        if not pairs:
            bk = h["booking"].replace("{IN}", TRIP["check_in"]).replace("{OUT}", TRIP["check_out"])
            body.append("<tr><td><b>" + esc(h["name"]) + "</b></td>"
                        "<td colspan=\"4\"><span class=\"blank\">nothing verified from an official page</span></td>"
                        "<td>" + esc((h.get("rate_caveat") or "no official rate page found"))[:200] + "</td><td>"
                        + src_link(bk, "official booking (the rate is only visible there)") + "</td></tr>")
            continue
        for label, val, quote, url, note, read in pairs:
            body.append("<tr><td><b>" + esc(h["name"]) + "</b></td><td>" + esc(label) + "</td>"
                        "<td class=\"num\">" + val + "</td><td><span class=\"quote\">" + esc(quote)[:300]
                        + "</span></td><td class=\"nowrap\">" + esc(read) + "</td><td>" + esc(note)[:280]
                        + "</td><td>" + src_link(url, "official page") + "</td></tr>")
    body.append("</tbody></table></div>")
    body.append("<p class=\"muted sm\">A figure with no official page behind it is left blank and flagged, never "
                "estimated. The open questions behind those blanks are on the "
                "<a href=\"flagged-review.html\">Flagged for review</a> page.</p>")
    # Re-read of the trip-critical official values (session d615f79e). Rendered from its own record.
    rv_path = os.path.join(ROOT, "data", "d615f79e", "reverify.json")
    if os.path.exists(rv_path):
        with open(rv_path, encoding="utf-8") as fh:
            rv = json.load(fh)
        body.append("<h2>Re-read before payment (%s)</h2>" % esc(rv["retrieved"]))
        body.append('<p class="muted">%s</p>' % esc(rv["scope"]))
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Item</th><th>Result</th>'
                    "<th>Stored value</th><th>What the official page says</th><th>Official source</th>"
                    "</tr></thead><tbody>")
        for c in rv["checks"]:
            body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (esc(c["item"]), esc(c["result"]), esc(c["stored"]), esc(c["detail"]),
                           src_link(c["official_url"], "official page")))
        body.append("</tbody></table></div>")
        body.append('<p class="muted sm">%s</p>' % esc(rv["not_changed"]))
    write("pages/verification.html", page("Verification log", "".join(body), "verification.html", 1))


def main():
    build_index()
    build_exec()
    build_tournaments()
    build_single()
    build_multi()
    build_schedule()
    build_hotels()
    build_routes()
    build_planner()
    build_venue("venetian", "venetian.html", "The Venetian Resort", marquee_html())
    build_venue("wynn", "wynn.html", "Wynn Las Vegas", "")
    build_others()
    build_requirements()
    build_questions()
    build_suggestions()
    build_flagged()
    build_monitor()
    build_verification()
    build_repo_review()
    build_method()
    build_redirects()
    write("assets/css/style.css", CSS)
    write("assets/app.js", APP_JS)
    print("wrote %d files" % len(WROTE))
    for k in sorted(WROTE):
        print("  %s" % k)


if __name__ == "__main__":
    main()
