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
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "ea99006a")
PAGES = os.path.join(ROOT, "pages")

RULE_LABEL = {
    "confirmed_single": "Confirmed single-entry",
    "multi": "Multi-entry (re-entry / flights / add-on)",
    "unknown": "Entry cap not stated - unverified",
    "unread": "Entry terms not read - unverified",
}
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
VEN = load("venetian.json")
WPT = load("wpt.json")
OTH = load("other.json")
VENUES = load("venues.json")
HOTELS = load("hotels.json")
ROUTES = load("routes.json")
FLAGS = load("flags.json")
QUESTIONS = load("questions.json")
SUGGESTIONS = load("suggestions.json")
VENUE_BY_KEY = dict((v["key"], v) for v in VENUES)
TAX = META["tax"]
TRIP = META["trip"]
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


def guarantee_value(row):
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
    g = guarantee_value(row)
    b = row.get("buyin")
    if not g or not b:
        return ""
    return "%.1f" % (g / float(b))


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
    gcell = money(g) if g not in (None, "") else '<span class="blank">not stated</span>'
    if is_bounty(row):
        gcell += '<br><span class="tag tag-b">bounty incl.</span>'
    cells.append('<td class="num">%s</td>' % gcell)
    cells.append('<td class="num">%s</td>' % (ratio_text(row) or '<span class="blank">-</span>'))
    cells.append('<td><span class="pill pill-%s">%s</span>%s</td>' % (
        RULE_CLASS[row["entry_rule"]], esc(RULE_LABEL[row["entry_rule"]]),
        ('<br><span class="quote">%s</span>' % esc(row["rule_excerpt"][:220])) if row.get("rule_excerpt") else ""))
    cells.append("<td>%s</td>" % esc(row.get("chips") or ""))
    cells.append("<td>%s</td>" % esc(row.get("levels") or ""))
    cells.append("<td>%s</td>" % (esc(row["late_reg"]) if row.get("late_reg") else '<span class="blank">not stated</span>'))
    cells.append("<td>%s</td>" % src_link(row["source"], row.get("source_label") or "source"))
    cells.append('<td class="nowrap">%s</td>' % esc(row.get("retrieved") or RETRIEVED))
    return "".join(cells)


EVENT_HEAD = ("""<tr><th>Venue</th><th>Date</th><th>Start</th><th>#</th><th>Event</th>
<th class="num">Buy-in</th><th>House fee</th><th>To prize pool</th><th class="num">Guarantee</th>
<th class="num">GTD &divide; entry</th><th>Entry rule (official text)</th><th>Chips</th><th>Levels</th>
<th>Late registration closes</th><th>Official source</th><th>Last checked</th></tr>""")

FILTER_BAR = """
<div class="filters">
  <input type="search" id="q" placeholder="Search events, venues, dates, rules..." aria-label="Search">
  <label>From <input type="date" id="dfrom"></label>
  <label>To <input type="date" id="dto"></label>
  <select id="fvenue" aria-label="Venue"><option value="">All venues</option>%s</select>
  <label class="chk"><input type="checkbox" id="fse"> Single-entry / no re-entry text only</label>
  <label class="chk"><input type="checkbox" id="fentry"> Entry rows only (hide Day 2 / final tables)</label>
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

APP_JS = r"""
/* Poker5 - session ea99006a. Client-side filtering and calculators. */
function qsa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function norm(s){return (s||'').toLowerCase();}

function initTable(id){
  var t=document.getElementById(id); if(!t) return;
  var rows=qsa('tbody tr',t);
  var q=document.getElementById('q'), from=document.getElementById('dfrom'),
      to=document.getElementById('dto'), ven=document.getElementById('fvenue'),
      se=document.getElementById('fse'), en=document.getElementById('fentry'),
      cnt=document.getElementById('count'), empty=document.getElementById('empty');
  function apply(){
    var needle=norm(q?q.value:''), f=from?from.value:'', t2=to?to.value:'',
        v=ven?ven.value:'', s=se?se.checked:false, e=en?en.checked:false, shown=0;
    rows.forEach(function(tr){
      var d=tr.getAttribute('data-date')||'';
      var ok=true;
      if(needle && norm(tr.getAttribute('data-search')).indexOf(needle)<0) ok=false;
      if(ok && f && d && d<f) ok=false;
      if(ok && t2 && d && d>t2) ok=false;
      if(ok && v && tr.getAttribute('data-venue')!==v) ok=false;
      if(ok && s && tr.getAttribute('data-rule')!=='unknown' && tr.getAttribute('data-rule')!=='confirmed_single') ok=false;
      if(ok && e && tr.getAttribute('data-kind')!=='entry') ok=false;
      tr.style.display=ok?'':'none'; if(ok) shown++;
    });
    if(cnt) cnt.textContent=shown+' of '+rows.length+' rows';
    if(empty) empty.hidden=!(shown===0);
  }
  if(q) q.addEventListener('input',apply);
  [from,to].forEach(function(el){if(el) el.addEventListener('change',apply);});
  if(ven) ven.addEventListener('change',apply);
  [se,en].forEach(function(el){if(el) el.addEventListener('change',apply);});
  var rst=document.getElementById('reset');
  if(rst) rst.addEventListener('click',function(){
    if(q)q.value=''; if(from)from.value=''; if(to)to.value=''; if(ven)ven.value='';
    if(se)se.checked=false; if(en)en.checked=false; apply();});
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
  apply();
}

/* ---- hotel true nightly cost + dated rate log ---- */
var RATE_KEY='poker5.ratelog.v1';
function num(el){var v=parseFloat((el&&el.value||'').replace(/[^0-9.\-]/g,''));return isNaN(v)?0:v;}
function rateLog(){try{return JSON.parse(localStorage.getItem(RATE_KEY)||'[]');}catch(e){return [];}}
function saveRateLog(l){try{localStorage.setItem(RATE_KEY,JSON.stringify(l));}catch(e){}}
function renderRateLog(){
  var box=document.getElementById('ratelog'); if(!box) return;
  var l=rateLog();
  if(!l.length){box.innerHTML='<p class="muted sm">No dated quotes recorded yet. Add one above and it is stored in this browser only.</p>';return;}
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
      tr.style.display=(walk.checked && (m===''||m===null))?'':'';
      if(walk.checked && m!==''){ if(parseFloat(m)>30) tr.style.display='none'; }
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

/* ---- trip planner ---- */
function initPlanner(){
  var box=document.getElementById('picks'); if(!box) return;
  var out=document.getElementById('ptotal');
  function total(){
    var buy=0,n=0;
    qsa('input[type=checkbox][data-buyin]',box).forEach(function(c){
      if(!c.checked) return; var b=parseFloat(c.getAttribute('data-buyin'))||0;
      var times=parseInt((document.getElementById('mult')||{}).value||'1',10);
      buy+=b*times; n+=times;});
    var hotel=parseFloat((document.getElementById('ptrue')||{}).value||'');
    var nights=parseFloat((document.getElementById('pnights')||{}).value||'0');
    var known=!isNaN(hotel)&&hotel>0;
    var h=known?hotel*nights:0, t=buy+h;
    var html='<div>Entries: <b>'+n+'</b> &nbsp; Buy-ins total: <b>$'+buy.toLocaleString(undefined,{maximumFractionDigits:0})+'</b></div>';
    if(known){
      html+='<div>Hotel: '+nights+' night(s) &times; $'+hotel.toFixed(2)+' true cost = <b>$'+h.toLocaleString(undefined,{maximumFractionDigits:0})+'</b></div>'+
        '<div class="big">Estimated trip cost: $'+t.toLocaleString(undefined,{maximumFractionDigits:0})+'</div>';
    }else{
      html+='<div>Hotel: <b>Incomplete</b> - no date-specific room quote is currently recorded. Enter the true '+
        'nightly hotel cost from the hotels page to complete the total.</div>'+
        '<div class="big">Estimated trip cost: Incomplete</div>';
    }
    html+='<div class="muted sm">Entries &times; buy-ins + nights &times; true hotel cost. Multi-entry events can '+
      'cost several buy-ins; the multiplier above models that. Whether the resort fee is included in the tax base '+
      'remains unverified - confirm on the folio.</div>';
    if(out) out.innerHTML=html;
  }
  box.addEventListener('change',total);
  ['mult','ptrue','pnights'].forEach(function(id){var e=document.getElementById(id); if(e) e.addEventListener('input',total);});
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
  initHotels(); initPlanner(); initSuggestions();
});
"""


def page(title, body, active, depth=1, extra_head=""):
    pre = "../" * depth
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s | Poker5</title>
<link rel="stylesheet" href="%sassets/css/style.css">
<script src="%sassets/app.js"></script>
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
             ("pages/single-entry.html", "Single-entry", "Events with no re-entry, rebuy or add-on text - and why none is confirmed."),
             ("pages/tournaments-double.html", "Multi-entry", "Re-entry, add-on, multi-flight and paid-advantage events, kept separate."),
             ("pages/schedule.html", "Day schedule", "One primary event per day plus a conditional fallback, with the overlap check."),
             ("pages/hotels.html", "Hotels", "Resort fees, official booking links, dated rate log and true nightly cost."),
             ("pages/routes.html", "Walking routes", "Hotel to poker room, with the 30-minute filter."),
             ("pages/planner.html", "Trip planner", "Entries &times; buy-ins + nights &times; true hotel cost."),
             ("pages/venues/venetian.html", "Venetian", "DeepStack Extravaganza IV, 16 Nov - 23 Dec 2026."),
             ("pages/venues/wynn.html", "Wynn", "WPT World Championship festival, 27 Nov - 21 Dec 2026."),
             ("pages/venues/others.html", "Other venues", "Caesars Palace, Horseshoe, Resorts World, South Point and the rooms we could not verify."),
             ("pages/questions.html", "Questions", "What we know, what is missing, and how to find it."),
             ("pages/suggestions.html", "Suggestions", "Pick a path before anything is changed."),
             ("pages/flagged-review.html", "Flagged for review", "%d irregularities and unverified values, each with its source." % len(FLAGS)),
             ("pages/method.html", "Method &amp; sources", "How every value was read, and the complete source ledger.")]
    body = []
    body.append("<h1>Las Vegas Strip poker trip planner</h1>")
    body.append('<p class="muted">Source-verified &middot; retrieved %s &middot; Venetian DeepStack Extravaganza IV and the WPT World Championship at Wynn</p>' % esc(RETRIEVED))
    body.append('<div class="grid">')
    for n, l in (("37", "Venetian structure sheets read"),
                    (str(len(ALL_EVENTS)), "Verified schedule rows"),
                    (str(len(CONFIRMED)), "Confirmed single-entry events"),
                    (str(len(CANDIDATES)), "Rows with no re-entry text"),
                    (str(len(MULTI)), "Rows that are re-entry / multi-flight"),
                    (str(len(FLAGS)), "Items flagged for review")):
        body.append('<div class="stat"><div class="num">%s</div><div class="lbl">%s</div></div>' % (n, esc(l)))
    body.append("</div>")
    body.append('<div class="badbox"><b>The single-entry headline: zero events are confirmed as one-entry.</b> '
                'All 37 official Venetian structure sheets were read on %s. None contains a one-entry, no-re-entry or '
                'freezeout statement, and every WPT / Wynn event whose terms were read permits re-entry. '
                'An event is therefore never labelled "single-entry" on this site. The '
                '<a href="pages/single-entry.html">Single-entry</a> page lists the %d events whose sheet shows no '
                're-entry, rebuy or add-on text - they are the closest thing available, and they stay labelled '
                '<i>entry cap not stated</i>.</div>' % (esc(RETRIEVED), len(CANDIDATES)))
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
                '<li>It will not call an event single-entry unless an official source says so.</li>'
                '<li>It will not fill in a guarantee, a rate or a walking time that no official source states.</li>'
                '<li>It will not rank events until the total entry fee and the guarantee are both confirmed.</li>'
                '</ul></div>')
    body.append(archive_block(0))
    write("index.html", page("Las Vegas Strip poker trip planner", "".join(body), "index.html", 0))


ARCHIVE_SKIP = {"pages", "assets", "data", "scripts", "work", "tools"}


def archive_entries():
    """Auto-discover every other session's published folder so none is lost."""
    out = []
    for name in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, name)
        if not os.path.isdir(path) or name.startswith(".") or name in ARCHIVE_SKIP:
            continue
        if not os.path.exists(os.path.join(path, "index.html")):
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
    body.append(FILTER_BAR % VENUE_OPTS)
    body.append(table_shell(ALL_EVENTS, EVENT_HEAD))
    body.append('<p class="muted sm">Guarantee &divide; entry fee is a descriptive ratio, not a forecast. '
                'Bounty events are tagged because their published guarantee includes the bounty pool.</p>')
    write("pages/tournaments.html", page("All tournaments", "".join(body), "tournaments.html", 1,
                                         TABLE_JS_INIT))


def build_single():
    body = ["<h1>Single-entry tournaments</h1>"]
    body.append('<div class="badbox"><b>Confirmed single-entry events: %d.</b> Every official structure sheet '
                'published for the Venetian DeepStack Extravaganza IV (all 37) was read on %s. Not one states a '
                'one-entry, no-re-entry or freezeout limit. Every WPT World Championship event whose terms were '
                'read states the opposite - "unlimited re-entry", or "one entry and one re-entry per starting flight" '
                'for the Prime Championship. Rather than relabel silence as confirmation, this page separates the two '
                'things the brief asks for: events that are confirmed, and events that simply show no paid-advantage '
                'text.</div>' % (len(CONFIRMED), esc(RETRIEVED)))
    body.append("<h2>1. Confirmed single-entry (freezeout)</h2>")
    if CONFIRMED:
        body.append(table_shell(CONFIRMED, EVENT_HEAD))
    else:
        body.append('<div class="panel"><p><b>None.</b> No official source read during this session states a '
                    'one-entry limit for any event in the window. Nothing is listed here rather than listing '
                    'something unverified.</p></div>')
    body.append("<h2>2. No re-entry, rebuy or add-on text on the official sheet (%d rows)</h2>" % len(CANDIDATES))
    body.append('<p class="muted">These are the closest candidates for a single-entry plan. The official structure '
                'sheet for each one was read and contains no re-entry, rebuy, add-on or paid-chip language. '
                '<b>Silence is not a one-entry promise</b>, so each row keeps the label "entry cap not stated". '
                'Before you rely on one, ask the poker room to confirm the entry cap in writing.</p>')
    body.append(FILTER_BAR % VENUE_OPTS)
    body.append(table_shell(CANDIDATES, EVENT_HEAD))
    body.append("<h2>3. Events excluded from a single-entry plan</h2>")
    body.append('<p class="muted">These rows fail the test for a stated reason: multiple starting flights, an '
                'explicit re-entry or add-on rule, a satellite that pays seats instead of cash, or an age/entry '
                'restriction. They are listed on the <a href="tournaments-double.html">Multi-entry page</a>.</p>')
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
    body.append(FILTER_BAR % VENUE_OPTS)
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


def build_schedule():
    body = ["<h1>Day schedule and overlap check</h1>"]
    body.append('<p class="muted">For each date, one <b>primary</b> event and, where one fits, a <b>conditional '
                'fallback</b>. Overlap is decided from official values only: an event occupies the window from its '
                'official start time to its official late-registration close time, both printed on its structure '
                'sheet. Where a sheet states no close time, the start time alone is used. No finish time is '
                'estimated - no official source publishes one.</p>')
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
        prim = None
        for r in evs:
            if r["entry_rule"] == "unknown" and r["kind"] == "entry":
                prim = r
                break
        if prim is None:
            for r in evs:
                if r["kind"] == "entry":
                    prim = r
                    break
        if prim is None:
            prim = evs[0]
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
    body.append(FILTER_BAR % VENUE_OPTS)
    out = []
    for d, evs, prim, fb, conflicts in rows_by_date:
        inwin = TRIP["check_in"] <= d <= TRIP["check_out"]
        out.append('<div class="panel %s" data-date="%s" data-venue="all" data-rule="all" data-kind="entry" '
                   'data-search="%s">' % ("" if inwin else "vhide", esc(d), esc(("%s %s" % (pretty_date(d), weekday(d))).lower())))
        out.append("<h3>%s, %s %s</h3>" % (esc(weekday(d)), esc(pretty_date(d)),
                                           '<span class="tag tag-b">in your window</span>' if inwin else ""))
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
        out.append("</div>")
        out.append('<div class="tablewrap"><table class="data pick"><thead><tr><th>Start</th><th>Venue</th>'
                   "<th>#</th><th>Event</th><th class=\"num\">Buy-in</th><th>Entry rule</th>"
                   "<th>Late reg closes</th><th>Source</th></tr></thead><tbody>")
        for r in evs:
            close, label = late_reg_close(r)
            out.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td>"
                       "<td>%s</td><td>%s</td></tr>"
                       % (esc(pretty_time(r["start"])), esc(r["venue"]), esc(r.get("event_no") or ""),
                          esc(r["name"]), money(r.get("buyin")),
                          '<span class="pill pill-%s">%s</span>' % (RULE_CLASS[r["entry_rule"]],
                                                                    esc(RULE_LABEL[r["entry_rule"]])),
                          esc(label) if label else '<span class="blank">not stated</span>',
                          src_link(r["source"], "source")))
        out.append("</tbody></table></div></div>")
    body.append("".join(out))
    body.append('<div class="warnbox"><b>Earliest verified start: 9:10 AM</b> (Venetian Event #46, a satellite on '
                '12 December). The earliest verified non-satellite start is 10:10 AM. No official schedule in this '
                'window lists an 8:00 AM start, so a "play from 8 AM" day is not supported by the sources.</div>')
    write("pages/schedule.html", page("Day schedule and overlap check", "".join(body), "schedule.html", 1,
                                      TABLE_JS_INIT))


def build_hotels():
    body = ["<h1>Hotels: true cost per night</h1>"]
    body.append('<p class="muted">True nightly cost = room rate + resort fee + tax. The tax rate below is taken from '
                'the Clark County ordinance; resort fees are stated only where an official page publishes them. '
                '<b>Room rates are not filled in</b> - official booking engines are JavaScript applications and no '
                'dated rate could be read from an official source. Use the booking link, then record what you see '
                'in the dated log at the bottom of this page.</p>')
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
        body.append("<tr><td><b>%s</b><br><span class=\"muted sm\">%s</span></td><td>%s</td><td>%s</td>"
                    "<td>%s</td><td>%s</td><td class=\"num\">%s<br><span class=\"muted sm\">%s</span></td>"
                    "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (esc(h["name"]), esc(h["quality_note"]), esc(h["tier"]), esc(h["area"]), esc(h["room"]),
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
    body.append('<div class="panel"><h2>Dated rate log</h2>'
                '<p class="muted sm">Each entry is stored with the time you recorded it, in this browser only. '
                'Rates are a log, not a single value - keep adding entries as prices move.</p>'
                '<div id="ratelog"></div></div>')
    body.append('<div class="warnbox">No dated nightly rate was captured from an official source during this session '
                '(booking engines require JavaScript). Every rate field above is blank on purpose. '
                'See flag F14 on the <a href="flagged-review.html">Flagged page</a>.</div>')
    write("pages/hotels.html", page("Hotels and true nightly cost", "".join(body), "hotels.html", 1))


def build_routes():
    body = ["<h1>Walking routes: hotel to poker room</h1>"]
    body.append('<p class="muted">The brief asks for a 30-minute walking limit. Only one walking distance is '
                'published officially anywhere: a poker room that sits inside the hotel you are staying in, which is '
                'zero minutes. No hotel or casino publishes a walking time to a <i>different</i> property, so those '
                'cells are left blank rather than estimated. Use the route link to check one yourself, then record '
                'the minutes below - the 30-minute filter works on what you record.</p>')
    body.append('<div class="panel"><label class="chk"><input type="checkbox" id="walkfilter"> '
                'Show only pairs at or under 30 minutes</label>'
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
    rows = [r for r in CANDIDATES if r.get("date") and TRIP["check_in"] <= r["date"] <= TRIP["check_out"]]
    rows.sort(key=lambda r: (r["date"], r["start"]))
    body = ["<h1>Trip planner: cost of the trip</h1>"]
    body.append('<p class="muted">Estimated trip cost = <b>entries &times; buy-ins</b> + <b>nights &times; true hotel '
                'cost</b>. The list below is pre-loaded with the %d events in your window (%s to %s) whose official '
                'sheet shows no re-entry, rebuy or add-on text. Tick the ones you would play.</p>'
                % (len(rows), esc(pretty_date(TRIP["check_in"])), esc(pretty_date(TRIP["check_out"]))))
    body.append('<div class="panel"><h2>Your window</h2><div class="kv">'
                '<dt>Check in / out</dt><dd>%s &rarr; %s (%d nights)</dd>'
                '<dt>Dates you can play</dt><dd>%s</dd>'
                '<dt>Why</dt><dd>%s</dd></div>'
                '<p class="muted sm">Change the dates with the filter on any tournament table; this page lists the '
                'window that was chosen automatically, and you can re-pick entries for any other dates there.</p></div>'
                % (esc(TRIP["check_in"]), esc(TRIP["check_out"]), TRIP["nights"],
                   esc("%s to %s" % (pretty_date(TRIP["check_in"]), pretty_date(TRIP["check_out"]))),
                   esc(TRIP["rationale"])))
    body.append('<div class="panel"><div class="calc">'
                '<label>Re-entry multiplier<input id="mult" type="number" min="1" max="10" step="1" value="1"></label>'
                '<label>True hotel cost / night $<input id="ptrue" type="number" min="0" step="1" placeholder="no date-specific quote recorded"></label>'
                '<label>Nights<input id="pnights" type="number" min="0" step="1" value="%d"></label>'
                '</div><div class="result" id="ptotal"></div>'
                '<p class="muted sm">Set the multiplier to 1 for a single-entry plan and to 2 or more for a '
                're-entry plan, so you can see both totals before you commit. Take the hotel figure from the '
                '<a href="hotels.html">hotels page</a>. No date-specific room quote is currently recorded for '
                'this stay, so the hotel and trip totals stay incomplete until you enter one. Whether the resort '
                'fee is included in the tax base remains unverified - confirm it on the folio before you pay.</p></div>' % TRIP["nights"])
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
        body.append(FILTER_BAR % VENUE_OPTS)
        body.append(table_shell(evs, EVENT_HEAD, with_venue=False))
    else:
        body.append('<div class="panel"><p><span class="blank">No verified rows.</span> %s</p></div>' % esc(v["status_note"]))
    if hotels:
        body.append("<h2>Stay here</h2>")
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Hotel</th><th>Walk</th>'
                    '<th class="num">Resort fee</th><th>Cancellation</th><th>Booking</th></tr></thead><tbody>')
        for h in hotels:
            booking = h["booking"].replace("{IN}", TRIP["check_in"]).replace("{OUT}", TRIP["check_out"])
            body.append("<tr><td>%s</td><td>%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td></tr>"
                        % (esc(h["name"]),
                           '<span class="pill pill-ok">0 min, same property</span>' if h["on_property"] else '<span class="blank">not verified</span>',
                           ("$%.0f" % h["resort_fee"]) if h["resort_fee"] else '<span class="blank">not verified</span>',
                           esc(h["cancel"]) or '<span class="blank">not verified</span>',
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
        body.append(FILTER_BAR % VENUE_OPTS)
        body.append(table_shell(evs, EVENT_HEAD))
    body.append(archive_block(2))
    write("pages/venues/others.html", page("Other venues", "".join(body), "others.html", 2,
                                           TABLE_JS_INIT if evs else ""))


def build_exec():
    cand = [r for r in CANDIDATES if r["venue"] == "The Venetian Resort"]
    body = ["<h1>Executive summary</h1>"]
    body.append('<div class="panel"><h2>The short version</h2><ul class="clean">')
    for item in (
        "Two Strip series are running and both are verified from official pages: the Venetian DeepStack "
        "Extravaganza IV (16 November - 23 December 2026) and the WPT World Championship festival at Wynn "
        "(27 November - 21 December 2026).",
        "<b>No event is confirmed as single-entry.</b> All 37 official Venetian structure sheets were read; "
        "none states a one-entry, no-re-entry or freezeout limit. Every WPT event whose terms were read permits "
        "re-entry, and the Prime Championship allows one entry plus one re-entry per flight.",
        "%d rows show no re-entry, rebuy or add-on text on their official sheet. They are the only sensible basis "
        "for a one-entry plan, and they stay labelled unverified until a room confirms the cap in writing." % len(CANDIDATES),
        "The recommended window is %s to %s (%d nights). It was chosen automatically: it sits inside both series "
        "and carries the most no-re-entry-text entries of any 7-night window in the Venetian series."
        % (pretty_date(TRIP["check_in"]), pretty_date(TRIP["check_out"]), TRIP["nights"]),
        "Hotel true nightly cost = rate + resort fee + tax at %.2f%%. Only two resort fees could be verified "
        "officially: the Venetian at $55 plus tax, and Resorts World at $55 per room per day (waived on the "
        "\"All Resort, No Fees\" offer through 28 December 2026). No nightly rate could be read from an official "
        "source, so no rate is filled in." % TAX["rate"],
        "No official schedule in this window lists an 8:00 AM start. The earliest verified start is 9:10 AM, and "
        "the earliest non-satellite start is 10:10 AM.",
        "Walking: only a poker room inside your own hotel is verifiable (0 minutes). No cross-property walking "
        "time is published officially, so none is estimated.",
        "%d items are flagged for review, each with its official source. None blocks publication." % len(FLAGS)):
        body.append("<li>%s</li>" % item)
    body.append("</ul></div>")
    body.append('<div class="grid">')
    for n, l in ((str(len(ALL_EVENTS)), "verified rows"), (str(len(VEN)), "Venetian rows"),
                 (str(len(WPT)), "Wynn / WPT rows"), (str(len(CONFIRMED)), "confirmed single-entry"),
                 (str(len(CANDIDATES)), "no re-entry text"), (str(len(MULTI)), "re-entry / multi-flight"),
                 (str(len(SATS)), "satellites"), (str(len(FLAGS)), "flagged for review")):
        body.append('<div class="stat"><div class="num">%s</div><div class="lbl">%s</div></div>' % (n, esc(l)))
    body.append("</div>")
    body.append(marquee_html())
    body.append("<h2>What to do first</h2>")
    body.append('<ol class="clean"><li>Fix your dates and your nightly budget. The site already assumes %s to %s; '
                'change it with the date filter.</li>'
                '<li>Ask the Venetian poker room to confirm, in writing, the entry cap for the events you want. '
                'Until then a one-entry plan rests on silence, not on a rule.</li>'
                '<li>Open the official booking links on the hotels page for your dates, read the itemised total, '
                'and record it in the dated rate log.</li>'
                '<li>Build the day plan from the schedule page: one primary event per day plus a fallback that '
                'starts after the first one\'s registration window closes.</li>'
                '<li>Reconfirm schedules, rates and policies before any non-refundable payment.</li></ol>'
                % (esc(TRIP["check_in"]), esc(TRIP["check_out"])))
    body.append("<h2>The strongest candidates (no re-entry text, Venetian only)</h2>")
    rows = sorted([r for r in cand if guarantee_value(r)], key=lambda r: -(guarantee_value(r) / float(r["buyin"])))[:12]
    if rows:
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Date</th><th>Start</th><th>#</th>'
                    '<th>Event</th><th class="num">Buy-in</th><th class="num">Guarantee</th>'
                    '<th class="num">GTD &divide; entry</th><th>Source</th></tr></thead><tbody>')
        for r in rows:
            body.append("<tr><td class=\"nowrap\">%s</td><td>%s</td><td>%s</td><td>%s</td><td class=\"num\">%s</td>"
                        "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td></tr>"
                        % (esc(pretty_date(r["date"])), esc(pretty_time(r["start"])), esc(r["event_no"]),
                           esc(r["name"]), money(r["buyin"]), money(r["guarantee"]), ratio_text(r),
                           src_link(r["source"], "sheet")))
        body.append("</tbody></table></div>")
        body.append('<p class="muted sm">Ranked by guarantee &divide; entry fee, which is a descriptive ratio, not a '
                    'forecast. Only events whose guarantee and buy-in are both officially confirmed are ranked. '
                    'Bounty events are tagged because their guarantee includes the bounty pool.</p>')
    write("pages/executive-summary.html", page("Executive summary", "".join(body),
                                               "executive-summary.html", 1))


def build_questions():
    body = ["<h1>Questions, answers and what is still missing</h1>"]
    body.append('<p class="muted">Ten questions that have to be answered before a decision is reasonable. For each: '
                'what the verified data already answers, what is still missing, and how to close the gap.</p>')
    for q in QUESTIONS:
        body.append('<div class="panel"><h3>%s. %s</h3><div class="kv">'
                    '<dt>What we have</dt><dd>%s</dd>'
                    '<dt>What is missing</dt><dd>%s</dd>'
                    '<dt>How to find it</dt><dd>%s</dd></div></div>'
                    % (esc(q["id"]), esc(q["q"]), esc(q["have"]), esc(q["missing"]), esc(q["how"])))
    write("pages/questions.html", page("Questions", "".join(body), "questions.html", 1))


def build_suggestions():
    body = ["<h1>Suggestions: choose a path before anything changes</h1>"]
    body.append('<p class="muted">Eight improvements, each with the options and what each one costs you. Pick one '
                'option per suggestion and the list at the bottom becomes your change request. Nothing on this site '
                'is altered until you ask for it.</p>')
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
    ledger = load("last_checked.json")
    changelog = load("change_log.json")
    body = ["<h1>Source monitor</h1>"]
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
    if changelog:
        body.append("<h2>Changes detected</h2>")
        body.append('<div class="tablewrap"><table class="data"><thead><tr><th>Detected at (UTC)</th>'
                    '<th>What it backs</th><th>Old hash</th><th>New hash</th><th>Size</th>'
                    '<th>Link</th></tr></thead><tbody>')
        for c in reversed(changelog[-200:]):
            body.append('<tr><td class="nowrap">%s</td><td>%s</td><td><code>%s</code></td>'
                        '<td><code>%s</code></td><td>%s</td><td>%s</td></tr>'
                        % (esc(c["changed_at"]), esc(c.get("label") or ""),
                           esc(c["old_sha256"][:12]), esc(c["new_sha256"][:12]),
                           esc("%s to %s bytes" % (c.get("old_bytes"), c.get("new_bytes"))),
                           src_link(c["url"], "open")))
        body.append("</tbody></table></div>")
    else:
        body.append('<div class="okbox">No change has been detected yet. The monitor records the first set of '
                    'hashes on its first scheduled run and compares from then on.</div>')
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
    build_questions()
    build_suggestions()
    build_flagged()
    build_monitor()
    build_repo_review()
    build_method()
    write("assets/css/style.css", CSS)
    write("assets/app.js", APP_JS)
    print("wrote %d files" % len(WROTE))
    for k in sorted(WROTE):
        print("  %s" % k)


if __name__ == "__main__":
    main()
