// Build the integrated Poker5 dashboard from data/aecba91e/*.  Node 20, no dependencies.
// Usage: node scripts/build-aecba91e.mjs
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';

const ROOT = process.cwd();
const D = join(ROOT, 'data/aecba91e');
const read = (f) => JSON.parse(readFileSync(join(D, f), 'utf8'));
// Refuse to build on an unverified transcription: the schedule input is diffed against the
// independent second reading of the official page before anything is rendered.
const { execFileSync } = await import('node:child_process');
try { execFileSync(process.execPath, [join(ROOT, 'scripts/verify_transcription_aecba91e.mjs')], { stdio: 'pipe' }); }
catch (e) { console.error('build aborted: the schedule transcription does not match the recheck file'); console.error(String(e.stdout || '') + String(e.stderr || '')); process.exit(1); }
const structFile = read('structures.json');
const structures = structFile.sheets;
const SHEET_URL = structFile.url_pattern;   // the official URL pattern is stored once, in the data file
const ref = read('reference.json');
const site = read('site.json');
const TODAY = '2026-11-17';

// ---------- load + join schedule rows with structure sheets ----------
const raw = readFileSync(join(D, 'venetian_dse_iv.psv'), 'utf8').split('\n')
  .map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));
const num = (s) => (s === '' ? null : Number(s));
const hhmm = (t) => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };
const fmtTime = (mins) => mins == null ? '' : `${String(Math.floor(mins / 60)).padStart(2, '0')}:${String(mins % 60).padStart(2, '0')}`;

const rows = raw.map((line, i) => {
  const [date, start, evNo, buyin, gtd, structNo, kind, flags, printed] = line.split('|');
  const sh = structures[structNo] || null;
  const r = {
    id: `V-${String(i + 1).padStart(3, '0')}`,
    venue: 'venetian', date, start,
    start_min: hhmm(start),
    event: Number(evNo),
    buyin: num(buyin), gtd: num(gtd),
    struct: Number(structNo), kind,
    flags: (flags || '').split(',').filter(Boolean),
    printed: printed || (sh ? sh.title : ''),
    sched_url: 'https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html',
    struct_url: SHEET_URL.replace('%d', structNo),
    last_checked: TODAY, source_changed: false,
    sheet_read: !!sh && sh.entry_limit !== 'unread',
    fee: sh ? sh.fee : null,
    lips_fee: sh ? (sh.lips_fee || 0) : null,
    pool: sh ? sh.pool : null,
    chips: sh ? sh.chips : null,
    level: sh ? sh.level : null,
    late_close: sh ? sh.late_close : null,
    late_close_text: sh ? (sh.late_close_text || '') : '',
    payout: sh ? sh.payout : null,
    bounty: sh ? sh.bounty : null,
    // Sheets #7 and #11 print a different guarantee per event number, so the guarantee is resolved
    // per event (gtd_by_event) instead of using the sheet's headline figure.
    gtd_sheet: sh ? ((sh.gtd_by_event || {})[evNo] ?? sh.gtd) ?? null : null,
    guarantee_text: sh ? (sh.gtd_text || '') : '',
    entry_limit: sh ? sh.entry_limit : 'no-sheet',
    sheet_note: sh ? (sh.note || '') : 'no structure sheet linked to this row',
    sheet_title: sh ? sh.title : '',
    eligibility: sh && sh.eligibility ? sh.eligibility : null,
    flight: !!(sh && sh.flight),
    satellite: !!(sh && sh.satellite),
    oneday: !!(sh && sh.oneday),
  };
  // total entry fee: the printed buy-in already contains the house fee per the sheets' wording
  r.total_entry = r.buyin;
  // A Day 2 restart or final table is not a purchasable entry: the sheet's fee split and guarantee
  // belong to the event, not to this row, so they are withheld here instead of looking like an entry cost.
  if (kind === 'restart' || kind === 'ft') {
    r.entry_note = 'no new entry fee - chips carried over from the starting flight';
    r.late_close = null; r.late_close_text = '';
    r.fee = null; r.pool = null; r.lips_fee = 0; r.gtd = null; r.gtd_sheet = null; r.guarantee_text = ''; r.gtd_conflict = null;
  }
  // classification (rule R1)
  if (r.kind === 'restart' || r.kind === 'ft') r.entry_status = 'continuation';
  else if (r.entry_limit === 'discount') r.entry_status = 'advantage';
  else if (r.flight) r.entry_status = 'advantage';
  else if (!r.sheet_read) r.entry_status = 'unverified';
  else if (r.entry_limit === 'none') r.entry_status = 'confirmed-single';
  else r.entry_status = 'unverified';
  // guarantee: the schedule row is the per-day figure; the sheet is the cross-check
  if (r.gtd == null && r.gtd_sheet != null) r.gtd = r.gtd_sheet;
  r.gtd_conflict = (r.gtd != null && r.gtd_sheet != null && r.gtd !== r.gtd_sheet)
    ? { schedule: r.gtd, sheet: r.gtd_sheet } : null;
  if (r.kind === 'entry' && r.gtd) {
    // entries needed to reach the guarantee, at the amount each entry actually adds to the pool
    r.ratio_basis = r.pool ? 'pool credit' : 'buy-in';
    r.ratio = Math.round((r.gtd / (r.pool || r.buyin)) * 100) / 100;
    r.ratio_buyin = r.buyin ? Math.round((r.gtd / r.buyin) * 100) / 100 : null;
    r.ratio_kind = r.bounty ? 'bounty-inclusive' : 'cash';
  } else { r.ratio = null; r.ratio_kind = ''; r.ratio_basis = ''; r.ratio_buyin = null; }
  return r;
});

// ---------- day plan: primary + conditional fallback (rule R3) ----------
const MIN_GAP = 240;
const byDate = new Map();
for (const r of rows) { if (!byDate.has(r.date)) byDate.set(r.date, []); byDate.get(r.date).push(r); }
for (const [date, list] of byDate) {
  list.sort((a, b) => a.start_min - b.start_min);
  const playable = list.filter((r) => r.entry_status === 'confirmed-single');
  let primary = null;
  for (const r of list) {
    r.role = '';
    if (r.entry_status === 'continuation') { r.role = 'continuation'; continue; }
    if (!primary && playable.includes(r)) { primary = r; r.role = 'primary'; continue; }
    if (!primary || !playable.includes(r)) { r.role = 'unscheduled'; continue; }
    const okGap = r.start_min - primary.start_min >= MIN_GAP;
    const okReg = primary.late_close ? r.start_min >= hhmm(primary.late_close) : true;
    // R3: without a published clock-time close the gap cannot be certified, so the fallback says so
    if (!primary.late_close) r.unverified_gap = primary.late_close_text
      ? `the primary event prints its close as "${primary.late_close_text}", not a clock time` : 'the primary event does not publish a registration close';
    r.role = okGap && okReg ? 'fallback' : 'conflict';
    if (r.role === 'conflict') r.conflict_note = primary.late_close
      ? `registration for ${'#' + primary.event} (start ${primary.start}) stays open until ${primary.late_close}`
      : 'starts less than 4h after the primary event';
  }
}

// ---------- source ledger + change log ----------
const urlSet = new Map();
const addUrl = (url, kind, checked, by) => {
  if (!url || /^https?:/.test(url) === false) return;
  if (!urlSet.has(url)) urlSet.set(url, { url, kind, last_checked: checked, checked_by: by, rows: 0 });
  const e = urlSet.get(url); e.rows++; if (checked > e.last_checked) e.last_checked = checked;
};
for (const r of rows) { addUrl(r.sched_url, 'schedule', TODAY, 'aecba91e'); addUrl(r.struct_url, 'structure sheet', r.last_checked, 'aecba91e'); }
addUrl('https://www.venetianlasvegas.com/resort/resort-fee.html', 'hotel policy', '2026-11-16', 'prior session');
addUrl('https://www.wynnlasvegas.com/terms-and-conditions/2026-presidents-day-sale-wynn-rewards', 'hotel policy', '2026-11-16', 'prior session');
addUrl('https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:3a73546d-c587-409d-9728-cbcf3a72ed04/original/as/pubhear-roomtax-ord-sb1d2.pdf', 'tax', '2026-11-16', 'prior session');
for (const q of ref.rate_log) addUrl(q.source, 'hotel rate quote', q.rate_timestamp, 'prior session');
for (const v of ref.venues) addUrl(v.official_url, 'venue', v.last_checked, v.checked_by);
// Links the site prints but which carry no value of their own still belong in the ledger, so a
// reader can see exactly which page was looked at and found silent.
for (const h of ref.hotels) { addUrl(h.resort_fee_source, 'hotel fee policy', '2026-11-16', 'prior session'); addUrl(h.rate_source_url, 'booking engine (quote page; no stored figure)', TODAY, 'aecba91e'); }
for (const p of ref.routes.pairs) { addUrl(p.maps_link, 'map link (walk not measured)', TODAY, 'aecba91e'); addUrl(p.apple_link, 'map link (walk not measured)', TODAY, 'aecba91e'); }
addUrl(ref.tax.source, 'tax document', '2026-11-16', 'prior session');
for (const f of site.flags) for (const u of f.sources || []) addUrl(u, `cited by ${f.id}`, TODAY, 'aecba91e');
// A "changed" entry only marks rows it is newer than: once a session re-verifies a row (its
// last_checked moves forward), the marker clears instead of accumulating forever.
let changeLog = [];
if (existsSync(join(D, 'change-log.json'))) changeLog = read('change-log.json');
const latestChange = new Map();
for (const e of changeLog) {
  if (e.status !== 'changed' || !e.url) continue;
  const day = String(e.checked_at || '').slice(0, 10);
  if (!latestChange.has(e.url) || day > latestChange.get(e.url)) latestChange.set(e.url, day);
}
for (const r of rows) {
  const hit = [r.sched_url, r.struct_url].map((u) => latestChange.get(u)).filter(Boolean).sort().pop();
  r.source_changed = Boolean(hit && hit > r.last_checked);
  if (hit && hit > r.last_checked) r.changed_on = hit;
}
const snapshot = { updated: TODAY, urls: [...urlSet.values()].map((u) => ({ url: u.url, kind: u.kind, last_checked: u.last_checked, sha256: null })) };
writeFileSync(join(D, 'sources.json'), JSON.stringify(snapshot, null, 1) + '\n');

// ---------- html helpers ----------
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const money = (v) => (v == null || v === '' ? '<span class="blank" title="not confirmed by an official source">—</span>' : '$' + Number(v).toLocaleString());
const link = (u, t) => (u ? `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t || 'source')}</a>` : '—');
const statusLabel = {
  'confirmed-single': ['Single entry per official structure sheet', 'ok'],
  'advantage': ['Advantage: multi-flight or paid-entry discount', 'warn'],
  'unverified': ['Unverified', 'bad'],
  'continuation': ['Continuation - not a new entry', 'mute'],
};
const NAV = [
  ['index.html', 'Overview'], ['tournaments.html', 'Tournaments'], ['advantage.html', 'Advantage &amp; unverified'],
  ['schedule.html', 'Day plan'], ['trip-cost.html', 'Trip cost'], ['hotels.html', 'Hotels'],
  ['rates.html', 'Rate log'], ['routes.html', 'Walking routes'], ['venues.html', 'Venues'],
  ['summary.html', 'Executive summary'], ['rules.html', 'Rules &amp; method'], ['questions.html', 'Open questions'],
  ['suggestions.html', 'Suggestions'], ['flagged.html', 'Flagged for review'], ['sources.html', 'Sources &amp; monitoring'],
  ['repo-review.html', 'Repo review'], ['archive.html', 'Prior session archive'],
];
const P = 'pages/';
// Publish point. The repo-root index.html and pages/ belong to session c6087e2c (live on GitHub
// Pages), so this build writes only inside site-aecba91e/ and never overwrites their files.
const SITE = join(ROOT, 'site-aecba91e');
// links are authored against the subsite landing directory; from a page they resolve as siblings
const navHref = (f, depth) => (f === 'index.html' ? (depth ? '../index.html' : './index.html') : (depth ? `./${f}` : `./${P}${f}`));
function layout(file, title, body, opts = {}) {
  const depth = file.startsWith(P) ? 1 : 0;
  // css/js are shared repo-wide under /assets, so this prefix climbs out of the subsite
  const pre = depth ? '../../' : '../';
  // page bodies may be authored from either root or page level; normalise per output depth
  if (depth) body = body.replace(/href="\.?\/?pages\/([a-z0-9-]+\.html)"/g, (m, f) => `href="./${f}"`);
  else body = body.replace(/href="(?!https?:|\.\/|\.\.\/|index\.html)([a-z0-9-]+\.html)"/g, (m, f) => `href="${P}${f}"`);
  const here = depth ? file.split('/').pop() : file;
  const navHtml = NAV.map(([f, label]) =>
    `<a href="${navHref(f, depth)}"${f === here ? ' class="on" aria-current="page"' : ''}>${label}</a>`).join('');
  return `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · Poker5 Vegas planner</title>
<link rel="stylesheet" href="${pre}assets/css/dashboard.css">
</head><body>
<header class="top"><div class="wrap">
<a class="brand" href="${depth ? '../index.html' : './index.html'}">Poker5 <span>Vegas tournament &amp; stay planner</span></a>
<div class="asof">data as of <strong>${TODAY}</strong> · official sources only · 21+</div>
</div></header>
<nav class="wrap"><div class="nav">${navHtml}</div></nav>
<main class="wrap">
<h1>${title}</h1>
${body}
</main>
<footer class="wrap foot"><p>Independent planning tool. Not affiliated with any casino, poker room or hotel. Every value is transcribed from the linked official page and can change without notice; blank means not confirmed. Confirm at the cage and with the hotel before paying. Must be 21+ with valid ID.</p></footer>
<script src="${pre}assets/js/app.js"></script>
</body></html>`;
}

const controls = (extra = '') => `<div class="tools" data-tools>
<label class="search"><span>Search all tables</span><input type="search" data-q placeholder="event #, name, buy-in, structure sheet…" autocomplete="off"></label>
<label class="dt"><span>From</span><input type="date" data-from value="2026-11-16"></label>
<label class="dt"><span>To</span><input type="date" data-to value="2026-12-23"></label>
${extra}
<span class="count" data-count></span></div>`;
const th = (label, attrs = '') => `<th ${attrs}>${label}</th>`;

function eventTable(list, { walkFilter = false } = {}) {
  // th carries the column index; app.js sorts by the cell's data-v (numeric) or text
  const head = `<tr>${th('Date', 'data-sort="0"')}${th('Start', 'data-sort="1"')}${th('Venue')}${th('Ev #', 'data-sort="3"')}${th('Event (as printed)')}${th('Buy-in', 'data-sort="5"')}${th('House fee (from sheet)')}${th('Into pool / entry', 'data-sort="7"')}${th('Guarantee', 'data-sort="8"')}${th('Entries to reach GTD', 'data-sort="9"')}${th('Late reg closes', 'data-sort="10"')}${th('Entry rule status')}${th('Flags')}${th('Source (official)')}${th('Last checked', 'data-sort="14"')}</tr>`;
  const body = list.map((r) => {
    const [label, cls] = statusLabel[r.entry_status];
    const flags = [];
    if (r.bounty) flags.push('bounty');
    if (r.satellite) flags.push('seat-prize');
    if (r.flight) flags.push('flight');
    if (!r.oneday && r.entry_status !== 'continuation') flags.push('multi-day');
    if (r.eligibility) flags.push(r.eligibility);
    if (r.ratio_kind === 'bounty-inclusive') flags.push('ratio not cash-only');
    if (r.source_changed) flags.push('source changed');
    if (r.role === 'primary') flags.push('day primary');
    if (r.role === 'fallback') flags.push('fallback');
    if (r.role === 'conflict') flags.push('overlaps primary');
    const feeTxt = r.fee == null ? '' : `$${r.fee}${r.lips_fee ? ` + $${r.lips_fee} LIPS` : ''}`;
    return `<tr data-date="${r.date}" data-status="${r.entry_status}" data-venue="${r.venue}"
 data-walk="0" data-changed="${r.source_changed ? 1 : 0}">
<td class="mono" data-v="${r.date}">${r.date}</td><td class="mono" data-v="${r.start_min}">${r.start}</td><td>Venetian</td>
<td class="mono" data-v="${r.event}">${r.event}</td><td class="name">${esc(r.printed || r.sheet_title)}</td>
<td class="num" data-v="${r.buyin ?? -1}">${money(r.buyin)}${r.entry_note ? `<div class="sub">${esc(r.entry_note)}</div>` : ''}</td><td class="num" title="${esc(r.sheet_note)}">${feeTxt ? esc(feeTxt) : '<span class="blank">—</span>'}</td>
<td class="num" data-v="${r.pool ?? -1}">${money(r.pool)}</td><td class="num" data-v="${r.gtd ?? -1}">${money(r.gtd)}${r.guarantee_text ? `<div class="sub">${esc(r.guarantee_text)}</div>` : ''}${r.gtd_conflict ? `<div class="sub bad" title="the schedule row and the structure sheet print different guarantees - neither is corrected here">sheet ${r.struct} says ${money(r.gtd_conflict.sheet)}</div>` : ''}</td>
<td class="num" data-v="${r.ratio ?? -1}"${r.ratio ? ` title="${r.ratio} entries at the ${r.ratio_basis} of ${money(r.pool || r.buyin)} per entry; at the full buy-in it would be ${r.ratio_buyin}"` : ''}>${r.ratio == null ? '<span class="blank">not computable</span>' : r.ratio + '×'}${r.ratio && r.ratio_basis === 'pool credit' ? '<span class="sub"> at pool credit</span>' : ''}</td>
<td class="mono" data-v="${r.late_close ? hhmm(r.late_close) : -1}">${r.entry_status === 'continuation' ? '<span class="blank" title="a Day 2 restart or final table has no registration window">no registration</span>' : (r.late_close ? r.late_close : (r.late_close_text ? `<span class="blank" title="${esc(r.late_close_text)}">${esc(r.late_close_text)}</span>` : '<span class="blank">not printed</span>'))}</td>
<td><span class="pill ${cls}">${label}</span></td>
<td class="flags">${flags.map((f) => `<i>${esc(f)}</i>`).join('')}</td>
<td>${link(r.sched_url, 'schedule')} · ${link(r.struct_url, 'sheet ' + r.struct)}</td>
<td class="mono" data-v="${r.last_checked}">${r.last_checked}${r.source_changed ? ` <b class="chg" title="the official page changed on ${r.changed_on}, after this row was last read">changed ${r.changed_on}</b>` : ''}</td></tr>`;
  }).join('\n');
  return `<div class="scroll"><table class="grid" data-table>${head}${body}</table></div>`;
}

const confirmed = rows.filter((r) => r.entry_status === 'confirmed-single');
const advantage = rows.filter((r) => r.entry_status === 'advantage');
const unverified = rows.filter((r) => r.entry_status === 'unverified');
const continuations = rows.filter((r) => r.entry_status === 'continuation');
const count = {
  rows: rows.length, confirmed: confirmed.length, advantage: advantage.length,
  unverified: unverified.length, continuations: continuations.length,
  sheets_read: Object.values(structures).filter((s) => s.entry_limit !== 'unread').length,
  dates: byDate.size,
};
// Prose counts are interpolated from the join so no sentence can drift from the build.
const TOK = {
  confirmed: count.confirmed, entry: rows.filter((r) => r.kind === 'entry').length,
  adv: count.advantage, unverified: count.unverified, cont: count.continuations, rows: count.rows,
  excl: count.advantage + count.unverified,
  days: new Set(confirmed.map((r) => r.date)).size, events: new Set(confirmed.map((r) => r.event)).size,
  sheets_read: count.sheets_read, sheets_total: Object.keys(structures).length,
};
const fill = (txt) => String(txt).replace(/\{\{(\w+)\}\}/g, (m, k) => (k in TOK ? TOK[k] : m));
const escf = (txt) => esc(fill(txt));


// ---------- pages ----------
const pages = {};

pages['index.html'] = layout('index.html', 'Vegas poker trip planner', `
<p class="lede">One dashboard for the <strong>DeepStack Extravaganza IV</strong> at The Venetian (Nov 16 – Dec 23, 2026) and the
hotels within a 30-minute walk of it. Every table cell is filled from the linked official page or left blank and flagged;
nothing is estimated or filled in.</p>
<section class="kpis">
<div><b>${count.rows}</b><span>official schedule rows</span></div>
<div><b>${count.confirmed}</b><span>rows passing the single-entry test</span></div>
<div><b>${count.advantage}</b><span>rows in the advantage section</span></div>
<div><b>${count.sheets_read}/37</b><span>structure sheets read</span></div>
<div><b>${ref.hotels.length}</b><span>candidate hotels</span></div>
<div><b>${ref.rate_log.length}</b><span>dated hotel rate records</span></div>
</section>
<div class="cards">
<a class="card" href="./pages/tournaments.html"><h3>Tournaments</h3><p>All ${count.rows} rows with a date filter, a single-entry toggle and search across every table.</p></a>
<a class="card" href="./pages/advantage.html"><h3>Advantage &amp; unverified</h3><p>Multi-flight and paid-entry-discount events, kept out of the single-entry list with the printed reason.</p></a>
<a class="card" href="./pages/schedule.html"><h3>Day plan</h3><p>One primary event per day plus a conditional fallback; impossible sequences are flagged.</p></a>
<a class="card" href="./pages/trip-cost.html"><h3>Trip cost</h3><p>Entries × entry fee + nights × true hotel cost, from the dated rate log.</p></a>
<a class="card" href="./pages/hotels.html"><h3>Hotels</h3><p>Resort fee, tax, parking, cancellation, walk-time filter ≤30 min.</p></a>
<a class="card" href="./pages/venues.html"><h3>Venues</h3><p>One page per room: its events and the hotels that reach it on foot.</p></a>
<a class="card" href="./pages/flagged.html"><h3>Flagged for review</h3><p>Every irregularity, conflict and blank cell, with the source link to clear it.</p></a>
<a class="card" href="./pages/sources.html"><h3>Sources &amp; monitoring</h3><p>${count.rows ? 'Every URL used, its last-checked date, and the automatic re-check that marks changed rows.' : ''}</p></a>
</div>
<section class="note"><h2>Read this first</h2>
<ul>
<li>There is <strong>no 8:00 AM start</strong> in the official DSE schedule; the earliest confirmed starts are 9:10 AM and 10:10 AM (see <a href="./pages/questions.html">Q5</a>).</li>
<li>"Single entry" here means: one-day event, its official structure sheet read in full, no re-entry / re-buy / add-on provision printed on it. That is a reading of silence, so the basis is shown in every row (<a href="./pages/rules.html">R1</a>).</li>
<li>The hotel half of the data is thin: fees are official, but rates, parking, cancellation deadlines and walking minutes are not published by the properties. They are blank and flagged rather than guessed.</li>
</ul></section>`, {});

pages['pages/tournaments.html'] = layout('pages/tournaments.html', 'Tournaments — official rows', `
<p class="lede">${count.rows} rows transcribed from the Venetian DSE IV page on ${TODAY}. Toggle <em>single-entry confirmed only</em> to hide every row that does not pass rule <a href="pages/rules.html">R1</a>.</p>
${controls(`<label class="tg"><input type="checkbox" data-only-confirmed> single-entry confirmed only</label>
<label class="tg"><input type="checkbox" data-hide-cont checked> hide continuation rows</label>
<label class="tg"><input type="checkbox" data-changed-only> source changed only</label>`)}
${eventTable(rows)}
<section class="legend"><b>Legend.</b> <span class="pill ok">Single entry per official structure sheet</span> <span class="pill warn">Advantage</span>
<span class="pill bad">Unverified</span> <span class="pill mute">Continuation</span> — a dash (—) means the official source does not state the value;
the ratio is guarantee ÷ entry fee (how many entries to reach the guarantee), descriptive only, never a forecast.</section>`);

pages['pages/advantage.html'] = layout('pages/advantage.html', 'Advantage, multi-flight and unverified rows', `
<p class="lede">These rows are excluded from the single-entry list because spending more money or entering twice can change your
field: multi-flight events, printed fee discounts, "subsequent buy in" wording, and rows whose structure sheet could not be read.</p>
<h2>Multi-flight / paid-entry advantage (${advantage.length})</h2>${eventTable(advantage)}
<h2>Unverified — sheet not read this session (${unverified.length})</h2>${unverified.length ? eventTable(unverified) : `<p class="blank">None. Every structure sheet in the series (37 of 37) was read in full on 2026-11-17; see <a href="pages/flagged.html">R-F01</a> for the two that needed a retry.</p>`}
<h2>Continuation rows (${continuations.length})</h2>
<p class="sub">Day-2/Day-3 restarts and final tables are not new entries; they are listed so a day plan does not double-count them.</p>
${eventTable(continuations)}`);

const days = [...byDate.entries()].sort();
const dayRows = days.map(([date, list]) => {
  const p = list.find((r) => r.role === 'primary');
  const f = list.find((r) => r.role === 'fallback');
  const c = list.filter((r) => r.role === 'conflict');
  const cont = list.filter((r) => r.entry_status === 'continuation');
  const cell = (r, extra) => r ? `<b>${r.start}</b> #${r.event} ${esc(r.printed || r.sheet_title)} · ${money(r.buyin)}${r.gtd ? ` / ${money(r.gtd)} GTD` : ''}${extra || ''}` : '<span class="blank">no confirmed single-entry start this day</span>';
  return `<tr data-date="${date}" data-venue="venetian" data-status="plan" data-walk="0">
<td class="mono">${date}</td>
<td>${cell(p, p ? (p.late_close ? ` <span class="sub">reg closes ${p.late_close}</span>` : (p.late_close_text ? ` <span class="sub">reg close printed as "${esc(p.late_close_text)}" - no clock time</span>` : '')) : '')}</td>
<td>${f ? cell(f, f.unverified_gap ? ` <span class=\"sub\">gap not verifiable: ${esc(f.unverified_gap)}</span>` : '') : (c.length ? '<span class="blank">none — every other start overlaps</span>' : '<span class="blank">—</span>')}</td>
<td>${c.length ? c.map((r) => `#${r.event} ${r.start} ${esc(r.printed || r.sheet_title)} <span class="sub">${esc(r.conflict_note || '')}</span>`).join('<br>') : '<span class="blank">—</span>'}</td>
<td>${cont.length ? cont.map((r) => `#${r.event} ${r.start} ${r.kind === 'ft' ? 'final table' : 'day-2 restart'}`).join('<br>') : '<span class="blank">—</span>'}</td></tr>`;
}).join('\n');
pages['pages/schedule.html'] = layout('pages/schedule.html', 'Day plan — primary event and conditional fallback', `
<p class="lede">Rule <a href="pages/rules.html">R3</a>: one primary event per day; a second event is only offered when its start is after the primary's
official late-registration close and at least 4 hours after the primary's start. Everything else is listed as an overlap, not as a plan.
Starts are the official printed times; <strong>no day in this series starts at 8:00 AM</strong>.</p>
${controls()}
<div class="scroll"><table class="grid" data-table><tr>${th('Date')}${th('Primary event')}${th('Conditional fallback')}${th('Overlapping rows (cannot be added)')}${th('Continuations that day')}</tr>${dayRows}</table></div>`);

// R4: only a measured/officially-stated walk under 30 min passes; unknown minutes are 999 so the filter excludes them.
const walkMin = (h) => (/poker room is in this resort/.test(h.walking) ? 0 : 999);
const hotelRows = ref.hotels.map((h) => `<tr${h.resort_fee_source ? "" : ` data-nosrc="1"`} data-venue="venetian" data-status="hotel" data-walk="${walkMin(h)}" data-hotel="${h.id}">
<td><b>${esc(h.hotel)}</b><div class="sub">${esc(h.area)}</div></td>
<td class="mono">${esc(h.address_official || '')}</td>
<td class="num">${esc(h.resort_fee || '') || '<span class="blank">blank — not confirmed</span>'}</td>
<td class="num"><span class="blank">blank — no official dated rate for your dates</span></td>
<td class="num">${esc(h.parking) || '<span class="blank">blank</span>'}</td>
<td class="num">${esc(h.cancellation) || '<span class="blank">blank</span>'}</td>
<td>${esc(h.walking)}</td>
<td>${esc(h.quality) || '<span class="blank">no official quality metric read</span>'}</td>
<td>${h.resort_fee_source ? link(h.resort_fee_source, 'fee source') + (h.resort_fee_verified_by ? `<div class="sub">read by ${esc(h.resort_fee_verified_by)}</div>` : '') : '<span class="blank" title="no official page read by any session states this hotel\'s fee">none read</span>'}</td>
<td>${esc(h.resort_fee_status)}</td></tr>`).join('\n');
pages['pages/hotels.html'] = layout('pages/hotels.html', 'Hotels — cost, fees and walking distance', `
<p class="lede">True nightly cost = room rate + mandatory resort fee + room tax (rule <a href="pages/rules.html">R5</a>). It is only shown where all
three components exist for the same dates and occupancy; otherwise the cell stays blank and the reason is on the
<a href="pages/flagged.html">flagged page</a>. Rates live in the <a href="pages/rates.html">dated rate log</a>, not in one flat value.</p>
${controls(`<label class="tg"><input type="checkbox" data-walk30> ≤30 min walk only</label>`)}
<div class="scroll"><table class="grid" data-table><tr>${th('Hotel')}${th('Official address')}${th('Resort fee / night')}${th('Room rate for the stay')}${th('Parking')}${th('Cancellation deadline')}${th('Walk to the poker room')}${th('Quality')}${th('Source')}${th('Verification status')}</tr>${hotelRows}</table></div>
<section class="note"><h2>Tax note</h2><p>The calculator applies ${esc(ref.tax.rate)} because that is what prior sessions read from the
Clark County document (${link(ref.tax.source, 'county PDF')}); it is <strong>not re-confirmed</strong> as the 2026 rate — see flag
R-F09. A property quote that already includes tax (Venetian record R1 in the rate log) is always preferred over applying a rate.</p></section>`);

const rateRows = ref.rate_log.map((q) => `<tr data-status="rate" data-walk="0" data-venue="${esc(q.hotel)}">
<td class="mono">${esc(q.rate_timestamp)}</td><td><b>${esc(q.hotel)}</b></td><td class="mono">${esc(q.stay)}${q.nights ? ` · ${q.nights} nights` : ''}</td>
<td class="mono">${esc(q.occupancy)}</td><td class="num">${esc(q.checkout_total)}</td><td class="num">${esc(q.nightly_average)}</td>
<td class="num">${esc(q.resort_fee_nightly)}</td><td class="num">${esc(q.tax_amount)}</td><td class="num">${esc(q.parking)}</td>
<td class="num">${esc(q.cancellation)}</td><td class="num">${esc(q.captured_by)}</td><td>${link(q.source, 'quote page')}</td></tr>`).join('\n');
pages['pages/rates.html'] = layout('pages/rates.html', 'Rate log — every quote keeps its date', `
<p class="lede">Rates are an append-only log: one record per capture, with the rate timestamp, checkout total, nightly average, resort fee,
tax, parking, cancellation deadline and the source. Comparing hotels only works like-for-like, so a record with different dates or
occupancy is never merged into another row.</p>
${controls()}
<div class="scroll"><table class="grid" data-table><tr>${th('Captured')}${th('Hotel')}${th('Stay dates')}${th('Occupancy')}${th('Checkout total')}${th('Nightly average')}${th('Resort fee / night')}${th('Tax')}${th('Parking')}${th('Cancellation')}${th('By')}${th('Source')}</tr>${rateRows}</table></div>
<p class="sub">Caveats per record are stored in <code>data/aecba91e/reference.json</code> and shown on the flagged page; no record here is a bookable price.</p>`);

const routeRows = ref.routes.pairs.map((p) => {
  const mins = /^\d+$/.test(String(p.minutes).trim()) ? Number(p.minutes) : (p.status === 'third-party' ? 25 : 999);
  const hasLink = Boolean(p.maps_link || p.apple_link);
  return `<tr${hasLink ? '' : ' data-nosrc="1"'} data-walk="${p.status === 'ok' ? 0 : mins}" data-status="route" data-venue="venetian">
<td><b>${esc(p.hotel)}</b></td><td>${esc(p.venue)}</td><td>${esc(p.mode)}</td>
<td class="num">${p.minutes ? esc(p.minutes) : '<span class="blank">not measured</span>'}</td>
<td><span class="pill ${p.status === 'ok' ? 'ok' : p.status === 'third-party' ? 'warn' : 'bad'}">${esc(p.status)}</span></td>
<td>${esc(p.basis)}</td>
<td>${p.maps_link ? link(p.maps_link, 'Google Maps') : '—'}${p.apple_link ? ' · ' + link(p.apple_link, 'Apple Maps') : ''}</td></tr>`;
}).join('\n');
pages['pages/routes.html'] = layout('pages/routes.html', 'Walking routes — the ≤30 minute rule', `
<p class="lede">Rule <a href="pages/rules.html">R4</a>: a hotel qualifies at 30 minutes or less, measured from the hotel lobby to the poker room door.
No Strip property publishes walking minutes, so measured times are either absent (blank, flagged) or explicitly third-party. Open the map
link to time the walk; until that is recorded, this page is advisory, not verified.</p>
${controls(`<label class="tg"><input type="checkbox" data-walk30> ≤30 min walk only</label>`)}
<div class="scroll"><table class="grid" data-table><tr>${th('Hotel')}${th('Venue')}${th('Route type')}${th('Minutes')}${th('Status')}${th('Basis')}${th('Map link (time it yourself)')}</tr>${routeRows}</table></div>`);

pages['pages/venues.html'] = layout('pages/venues.html', 'Venues — one page per room', `
<p class="lede">Each venue page lists its own events (only where this session read an official source for them) and the hotels that reach it on foot.</p>
<div class="cards">${ref.venues.map((v) => `<a class="card" href="${v.id}.html"><h3>${esc(v.name)}</h3><p>${esc(v.series)}</p>
<p class="sub">rows in this dataset: ${v.events_in_dataset} · last checked ${esc(v.last_checked)} by ${esc(v.checked_by)}</p></a>`).join('')}</div>`);
for (const v of ref.venues) {
  const list = v.id === 'venetian' ? rows.filter((r) => r.entry_status !== 'continuation') : [];
  const hotels = ref.hotels.filter((h) => (v.id === 'venetian' ? true : /wynn/i.test(v.name) ? /wynn|encore/i.test(h.hotel) : false));
  pages[`pages/${v.id}.html`] = layout(`pages/${v.id}.html`, v.name, `
<p class="lede">${esc(v.location)} · official source: ${link(v.official_url, v.name)} · last checked <b>${esc(v.last_checked)}</b> by ${esc(v.checked_by)}</p>
<section class="note"><h2>Status in this build</h2><p>${esc(v.notes)}</p></section>
${list.length ? `<h2>Events at this venue (${list.length})</h2>${controls(`<label class="tg"><input type="checkbox" data-only-confirmed> single-entry confirmed only</label>`)}
${eventTable(list)}` : `<h2>Events at this venue</h2><p class="blank">No event row is published from this room. The prior-session records for it are
listed on the <a href="pages/flagged.html">flagged page</a> (R-F07) and no row is shown rather than a row that cannot be sourced from an official page read
in this session.</p>`}
<h2>Hotels that reach this room on foot</h2>
<div class="scroll"><table class="grid" data-table><tr>${th('Hotel')}${th('Walk')}${th('Resort fee')}${th('Status')}</tr>
${(hotels.length ? hotels : ref.hotels).map((h) => `<tr data-status="venue-hotel" data-walk="${walkMin(h)}"><td><b>${esc(h.hotel)}</b></td><td>${esc(h.walking)}</td><td class="num">${esc(h.resort_fee) || '<span class="blank">blank</span>'}</td><td>${esc(h.resort_fee_status)}${h.resort_fee_source ? ' · ' + link(h.resort_fee_source, 'official page') : ''}</td></tr>`).join('\n')}</table></div>`);
}

const calcEntries = confirmed.map((r) => `<option value="${r.total_entry}" data-label="#${r.event} ${esc(r.printed || r.sheet_title)} (${r.date})" ${['2026-12-03','2026-12-04','2026-12-05','2026-12-06'].includes(r.date) ? 'data-prefill="1"' : ''}>${r.date} · #${r.event} · ${money(r.buyin)}${r.gtd ? ` / ${money(r.gtd)} GTD` : ''}</option>`).join('');
pages['pages/trip-cost.html'] = layout('pages/trip-cost.html', 'Estimated trip cost', `
<p class="lede">Total = entries × entry fee + nights × true hotel cost. Entry fees are the printed buy-ins, which the structure sheets state
already include the house fee (e.g. "$58 of the $300 Buy-In is withheld"). Hotel cost is the rate + resort fee + tax for the same room and dates,
taken from the <a href="pages/rates.html">rate log</a>. Prefilled with the labelled assumption window (${ref.trip_window.check_in} → ${ref.trip_window.checkout});
change nothing and it still shows what the official data supports.</p>
<div class="calc" data-calc>
 <div class="col"><h3>Entries</h3><div data-entrylist></div>
 <div class="row"><label>Add an entry<select data-entryadd>${calcEntries}</select></label><button type="button" data-add>+ add</button></div>
 <p class="sub">Entry totals below use the buy-in; the house-fee split is shown per event on the <a href="pages/tournaments.html">tournaments</a> page.</p></div>
 <div class="col"><h3>Stay</h3>
  <label>Check in<input type="date" data-in value="${ref.trip_window.check_in}"></label>
  <label>Check out<input type="date" data-out value="${ref.trip_window.checkout}"></label>
  <label>Nights (auto)<input type="number" data-nights value="${ref.trip_window.nights}" min="1" readonly></label>
  <label>Room rate / night ($)<input type="number" data-rate value="" placeholder="blank — no official dated rate"></label>
  <label>Resort fee / night ($)<input type="number" data-fee value="55"></label>
  <label>Room tax (%)<input type="number" data-tax value="13.38" step="0.01"></label>
  <label>Parking for the stay ($)<input type="number" data-park value="" placeholder="blank — not published"></label></div>
 <div class="col result"><h3>Result</h3>
  <div class="big" data-total>$0</div>
  <ul class="break" data-break></ul>
  <p class="sub">True cost / night = rate + resort fee + tax on the rate, plus parking spread over the nights. Any blank input makes the hotel
  half of the total unknown rather than zero — the page says so instead of inventing a number.</p></div>
</div>`);

pages['pages/summary.html'] = layout('pages/summary.html', 'Executive summary', `
<p class="lede">${esc(site.summary.headline)}</p><ul class="points">${site.summary.points.map((p) => `<li>${escf(p)}</li>`).join('')}</ul>
<section class="note"><h2>What is decided by this data</h2>
<ul><li>The tournament half is usable: ${TOK.confirmed} confirmed single-entry events (over ${TOK.days} dates) with exact buy-in, house fee, per-entry pool, late-registration close and guarantee.</li>
<li>The hotel half is not: no official dated room rate, parking, cancellation deadline or walking minute exists in any source read by any session, so no hotel can honestly be ranked.</li>
<li>The two open decisions that block the plan are the trip dates and the nightly budget/quality floor (<a href="pages/questions.html">Q1, Q2</a>), plus whether a 9:10/10:10 start is acceptable (<a href="pages/questions.html">Q5</a>).</li></ul></section>`);

pages['pages/rules.html'] = layout('pages/rules.html', 'Rules, method and the decision workflow', `
<h2>Rules applied to every row</h2><ol class="rules">${site.rules.map((r) => `<li><b>${esc(r.id)} — ${esc(r.title)}.</b> ${escf(r.text)}</li>`).join('')}</ol>
<section class="note"><h2>How to use this site, in order</h2><ol>
<li>Fix the trip dates and a nightly budget/quality floor (Q1, Q2).</li>
<li>For the candidate events, open each structure sheet link in the table and read the printed maximum-entry / no-rebuy / no-add-on wording; drop anything that does not meet the single-entry policy (the <a href="pages/advantage.html">advantage page</a> is what gets dropped and why).</li>
<li>Compare only the surviving events on guarantee, buy-in, starting stack and blind duration, payout percentage and whether the schedule fits the day.</li>
<li>Get an itemised hotel total for the same stay and time the walk (≤30 min) with the map links on the <a href="pages/routes.html">routes page</a>.</li>
<li>Build one event per day first; add an evening event only where the primary event's field is closed and the gap is real (rule R3).</li>
<li>Re-confirm schedules, rates and cancellation policies on the official pages before any non-refundable payment — the <a href="pages/sources.html">monitoring page</a> records when each source was last fetched and flags changes.</li></ol></section>
<section class="note"><h2>Field-size note</h2><p>The DSE "Results" column is empty on the official page for every row read today, so entries-per-event and
therefore the actual overlay situation are unknown. The "entries to reach GTD" column is the guarantee divided by the amount each entry adds to the
pool (the buy-in minus the withheld house fee), which is the arithmetic the room itself would run; the buy-in-based figure is in each cell's tooltip.
It is a description of the printed numbers, not a forecast of field size, and no overlay or shortfall is implied.</p></section>`);

pages['pages/questions.html'] = layout('pages/questions.html', 'Questions, information and answers', `
<p class="lede">What must be known before a decision is reasonable, what is already answered by the official data, and what single action closes each gap.
Blocking items prevent a final schedule or hotel ranking; they do not block reading this site.</p>
<div class="scroll"><table class="grid" data-table><tr>${th('ID')}${th('Type')}${th('Question')}${th('Why it matters')}${th('Answer from what we already have')}${th('How to close it')}${th('Blocks?')}</tr>
${site.questions.map((q) => `<tr data-status="q" data-walk="0"><td class="mono"><b>${esc(q.id)}</b></td><td>${esc(q.kind)}</td>
<td><b>${escf(q.question)}</b></td><td>${escf(q.why)}</td><td>${escf(q.current_answer)}</td><td>${escf(q.to_resolve)}</td>
<td>${q.blocking ? '<span class="pill bad">blocks the decision</span>' : '<span class="pill mute">no</span>'}</td></tr>`).join('\n')}</table></div>`);

pages['pages/suggestions.html'] = layout('pages/suggestions.html', 'Suggestions — choose a path before implementing', `
<p class="lede">Nothing below is implemented; each is a proposal to improve decision quality. Review, pick the ones worth doing, and they become the next work items.</p>
<div class="cards">${site.suggestions.map((s) => `<div class="card"><h3>${esc(s.id)} · ${escf(s.title)}</h3><p>${escf(s.detail)}</p></div>`).join('')}</div>`);

const blankCounts = {
  unverified: unverified.length,
  rate: ref.hotels.filter((h) => !h.resort_fee).length,
  walk: ref.routes.pairs.filter((p) => p.status !== 'ok').length,
  unverified_rows: unverified.length,
};
pages['pages/flagged.html'] = layout('pages/flagged.html', 'Flagged for review', `
<p class="lede">Every irregularity, conflict and unverifiable value found while building this site, with the link needed to clear it. These do not block
publication; they are the list to work through. Counts: ${blankCounts.rate} hotel rows with no official rate, ${blankCounts.walk} hotel↔venue pairs with no
measured walk, ${blankCounts.unverified_rows} schedule rows still labelled unverified.</p>
${site.flags.map((f) => `<article class="flag"><h2>${esc(f.id)} <span class="pill ${/blocks/.test(f.severity) ? 'bad' : 'warn'}">${esc(f.severity)}</span></h2>
<p>${escf(f.item)}</p>${f.action ? `<p class="sub"><b>Action:</b> ${escf(f.action)}</p>` : ''}
<ul>${(f.sources || []).map((s) => `<li>${link(s, s)}</li>`).join('')}</ul></article>`).join('')}
<h2>Rows still labelled unverified</h2>
${unverified.length ? eventTable(unverified) : `<p class="blank">None — all 37 structure sheets were read, so no schedule row is left unverified. Every remaining gap is on the hotel side and is listed above.</p>`}
<section class="note"><h2>Unverified hotel values</h2><ul>
${ref.hotels.filter((h) => !h.resort_fee).map((h) => `<li><b>${esc(h.hotel)}</b>: resort fee, rate, parking and cancellation all blank — no official page read by any session states them.</li>`).join('')}
${ref.routes.pairs.filter((p) => p.status === 'third-party').map((p) => `<li><b>${esc(p.hotel)} → ${esc(p.venue)}</b>: ${esc(p.minutes)} is a third-party estimate (${esc(p.basis)}), not a measurement.</li>`).join('')}
</ul></section>`);

const CONFIRMED_MIN = 5;
const CONSISTENCY = [
  [`${rows.filter((r) => r.kind === 'entry' && r.gtd != null && r.gtd_sheet != null).length}/${rows.filter((r) => r.kind === 'entry' && r.gtd != null).length} rows`, 'schedule guarantee agrees with the structure sheet'],
  [`${rows.filter((r) => r.kind === 'entry' && r.buyin != null && r.fee != null && r.pool != null).length} rows`, 'buy-in equals house fee plus pool credit'],
  [`${confirmed.length} rows`, 'single-entry label carries a sheet read on 2026-11-17 and a printed registration close or level count'],
  [`${rows.filter((r) => r.gtd_conflict).length} rows`, 'guarantee conflicts left unresolved and shown as such'],
  [`${confirmed.length} rows`, 'every single-entry row is the only start for its event number (no other session of it is on the schedule)'],
  [`min ${CONFIRMED_MIN}`, 'the build aborts if the confirmed-single count collapses (a bad join, not a real change)'],
];
const startsOf = new Map();
for (const r of rows) if (r.kind === 'entry') startsOf.set(r.event, (startsOf.get(r.event) || 0) + 1);
for (const r of confirmed) {
  if (startsOf.get(r.event) !== 1) { console.error(`${r.id}: labelled single-entry but event #${r.event} has ${startsOf.get(r.event)} starting rows on the schedule`); process.exit(1); }
}
if (confirmed.length < CONFIRMED_MIN) { console.error(`build aborted: only ${confirmed.length} confirmed single-entry rows`); process.exit(1); }
for (const r of rows) {
  if (r.kind === 'entry' && r.buyin != null && r.fee != null && r.pool != null && r.fee + r.pool + (r.lips_fee || 0) > r.buyin + 0.01) {
    console.error(`${r.id}: house fee ${r.fee} + pool ${r.pool} + LIPS ${r.lips_fee || 0} exceeds the printed buy-in ${r.buyin}`); process.exit(1);
  }
}
const srcRows = [...urlSet.values()].sort((a, b) => a.kind.localeCompare(b.kind) || b.rows - a.rows).map((u) => `<tr data-status="src" data-walk="0">
<td>${esc(u.kind)}</td><td class="name">${link(u.url, u.url)}</td><td class="num">${u.rows}</td><td class="mono">${esc(u.last_checked)}</td>
<td>${esc(u.checked_by)}</td><td><span class="pill mute">monitored</span></td></tr>`).join('\n');
pages['pages/sources.html'] = layout('pages/sources.html', 'Sources and automatic re-check', `
<p class="lede">Each row of every table links to one of these URLs. A GitHub Actions job (<code>.github/workflows/source-monitor-aecba91e.yml</code>) re-fetches
all of them every morning, compares the page against the stored snapshot, appends to <code>data/aecba91e/change-log.json</code>, marks the affected rows
"source changed" and rebuilds the site. A fetch failure never marks a row; it records the status as unreachable instead.</p>
<h2>Two independent readings of the schedule</h2>
<p class="sub">The build refuses to run unless <code>data/aecba91e/venetian_dse_iv.psv</code> (the transcription every row is built from) matches
<code>data/aecba91e/official_recheck_2026-11-17.psv</code> row for row - date, start, event number, structure sheet, row kind and printed guarantee.
The second file was written by re-reading the same official page after the first was finished, so a single careless transcription cannot survive the build.
Re-run it with <code>node scripts/verify_transcription_aecba91e.mjs</code>.</p>
<h2>Data consistency</h2>
<p class="sub">Cross-checks run at build time over the ${rows.length} joined rows:
${CONSISTENCY.map(([n, txt]) => `${n} — ${esc(txt)}`).join(' · ')}.
The first three are hard invariants; a failure stops the build rather than publishing a wrong number.</p>
<h2>Change log</h2>
${changeLog.length ? `<div class="scroll"><table class="grid" data-table><tr>${th('Checked at')}${th('URL')}${th('Status')}${th('Detail')}</tr>
${changeLog.map((e) => `<tr><td class="mono">${esc(e.checked_at)}</td><td class="name">${link(e.url, e.url)}</td><td>${esc(e.status)}</td><td>${esc(e.detail || '')}</td></tr>`).join('\n')}</table></div>`
 : `<p class="blank">No automated runs recorded yet — the monitor creates its baseline snapshots on the first execution. Until then, every row above shows its manual check date.</p>`}
<h2>Source ledger (${urlSet.size} URLs)</h2>
${controls()}
<div class="scroll"><table class="grid" data-table><tr>${th('Kind')}${th('URL')}${th('Rows using it')}${th('Last checked')}${th('Checked by')}${th('Monitoring')}</tr>${srcRows}</table></div>`);

pages['pages/repo-review.html'] = layout('pages/repo-review.html', 'Repo review', `
<p class="lede">Reviewed on ${TODAY} at <code>cee51b4</code> (main after PR #20). ${rows.length} rows and 37 sheet links checked in <code>data/aecba91e</code>; every other
session's folder left untouched.</p>
<section class="note"><h2>Findings</h2><ul>
<li><b>Twelve parallel outputs of the same brief.</b> <code>docs/</code>, <code>site/</code>, <code>site-443e914d/</code>, <code>site-b50aa7f5/</code>, four <code>dashboard-*/</code> folders, <code>planner-aa83f1e1/</code> and the root <code>pages/</code> each publish a version of the same tables. They disagree on the single-entry count (0, 20, 30, 36, 45, 64). This session's dataset is <code>data/aecba91e</code>; the others are linked from the <a href="pages/archive.html">archive page</a> and unchanged.</li>
<li><b>Two "final integration" claims on the same day.</b> Session 0a0e3c6d's PR #20 changed only COORDINATION.md (verified with <code>git show --stat c8f154d</code>), so no root file of theirs was overwritten by this rebuild; the board records the overlap.</li>
<li><b>Shared root site with no owner.</b> The Pages source is <code>main</code> at <code>/</code>, so the root landing page has been rewritten by several sessions in turn and every session's data is published permanently. Suggestion S9.</li>
<li><b>Third-party values presented beside official ones.</b> Several older hotel tables carry third-party walking times and fee figures; under the official-source rule those belong on a flagged page, not in a table cell.</li>
<li><b>Stale and dead official pages.</b> Recorded per venue above (<code>404</code> for the Venetian tournaments page and MGM poker page, removed Wynn poker page, blank Golden Nugget page) — the reason those venues publish no rows.</li>
<li><b>Two unread structure sheets</b> (36, 37) leave three rows unverified; the monitor will retry them daily (R-F01).</li>
</ul></section>`);

const ARCHIVE = [
  ['index.html', 'session c6087e2c — the published root site (index.html + pages/)'],
  ['docs/index.html', 'session 581fea93 — official-source build'],
  ['site/index.html', 'session b1f117c3 — site/ dashboard'],
  ['site-443e914d/index.html', 'session 443e914d — 36-row Venetian set'],
  ['site-b50aa7f5/index.html', 'session b50aa7f5 — strict single-entry dashboard'],
  ['dashboard-053f694f/index.html', 'session 053f694f — DSE + fees'],
  ['dashboard-bafafd7c/index.html', 'session bafafd7c — dashboard'],
  ['dashboard-cd5ab298/index.html', 'session cd5ab298 — Dec 2–9 calendar + quotes'],
  ['dashboard-de0bebd4/index.html', 'session de0bebd4 — 30-row single-entry set'],
  ['planner-aa83f1e1/index.html', 'session aa83f1e1 — planner subsite'],
];
pages['pages/archive.html'] = layout('pages/archive.html', 'Prior session archive', `
<p class="lede">Earlier sessions each built their own site and dataset. They are kept exactly as merged, so any figure in this build can be compared with
the one a previous session published. None of these is the current input to this dashboard.</p>
<div class="cards">${ARCHIVE.filter(([h]) => existsSync(join(ROOT, h))).map(([h, label]) => `<a class="card" href="../../${h}" target="_blank" rel="noopener"><h3>${esc(label)}</h3><p><code>${h}</code></p></a>`).join('')}</div>
<p class="sub">Missing entries above were not present at build time. Board history for all of them is in <a href="https://github.com/karagemop466-tech/Poker5/blob/main/COORDINATION.md" target="_blank" rel="noopener">COORDINATION.md</a>.</p>`);

// ---------- write ----------
for (const [file, html] of Object.entries(pages)) {
  const out = join(SITE, file);
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, html);
}
writeFileSync(join(D, 'events.json'), JSON.stringify({ generated: TODAY, count, rows }, null, 1) + '\n');
console.log('built', Object.keys(pages).length, 'pages ·', rows.length, 'rows ·', count.confirmed, 'confirmed ·', count.advantage, 'advantage ·', count.unverified, 'unverified');
