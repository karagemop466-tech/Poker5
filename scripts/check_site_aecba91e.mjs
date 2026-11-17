#!/usr/bin/env node
// Gate for site-aecba91e/. Exit 1 on any of:
//  - an internal link or asset that does not exist in the repo,
//  - a '#anchor' that is not present on the target page,
//  - an external URL that is not recorded in data/aecba91e/sources.json,
//  - a factual table row with no source link (rows may opt out with data-nosrc="1" and must then say why on the page),
//  - a data-table with no rows, or a rendered row count that disagrees with data/aecba91e/events.json,
//  - placeholder text (TODO / TBD / lorem / undefined / NaN / [object).
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { dirname, join, relative, normalize } from 'node:path';

const ROOT = process.cwd();
const SITE = join(ROOT, 'site-aecba91e');
const fail = [];
const warn = [];
const read = (p) => readFileSync(p, 'utf8');
const walk = (dir, acc = []) => {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) walk(p, acc); else if (p.endsWith('.html')) acc.push(p);
  }
  return acc;
};

const files = walk(SITE).sort();
if (!files.length) { console.error('no pages found - run: node scripts/build-aecba91e.mjs'); process.exit(1); }

const ledger = JSON.parse(read(join(ROOT, 'data/aecba91e/sources.json')));
const allowed = new Set(ledger.urls.map((u) => u.url.replace(/\/$/, '')));
// rows that publish a value taken from a source; questions and change-log rows are exempt
const FACTUAL = new Set(['confirmed-single', 'advantage', 'unverified', 'continuation', 'hotel', 'route', 'rate', 'venue']);
const unesc = (u) => u.replace(/&amp;/g, '&').replace(/&#38;/g, '&');
// A URL is checked for shape as well as ledger membership: the ledger is generated from the same
// value the page prints, so a broken template would otherwise validate itself.
const TEMPLATE = /%[sd]|\{|\}|undefined|NaN/i;
const OFFICIAL = /^https:\/\/([a-z0-9.-]+\.)?(venetianlasvegas\.com|wynnlasvegas\.com|encorewynn\.com|mgmresorts\.com|aria\.com|vdara\.com|cosmopolitanlasvegas\.com|caesars\.com|caesarspalace\.com|horseshelaslvegas\.com|planetwoodhollywood\.com|goldennugget\.com|rgren\.com|resorts-world\.lasvegas\.com|rwlasvegas\.com|clarkcountynv\.gov|nevada\.gov)(\/|$)/i;
const TOOL = /^https:\/\/(www\.)?(google\.com\/maps|maps\.apple\.com)\//i;
// a third-party page is only ever cited as "not official", and only on those two pages
const THIRD_PARTY = /casinocompassapp\.com/i;
const THIRD_PARTY_PAGES = /pages\/(flagged|sources)\.html$/;

let externalCount = 0;
const externals = new Set();
for (const path of files) {
  const html = read(path);
  const dir = dirname(path);
  const rel = relative(ROOT, path);
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));

  for (const m of html.matchAll(/(?:^|[\s<])(?:href|src)="([^"]+)"/g)) {
    const u = m[1];
    if (/^(mailto:|tel:)/.test(u)) continue;
    if (/^https?:/.test(u)) {
      externals.add(unesc(u));
      externalCount++;
      const isGithub = /github\.com/.test(u);                       // repo self-links, not data sources
      if (TEMPLATE.test(u)) fail.push(`${rel}: URL still contains an unresolved template or empty value: ${u}`);
      else if (!isGithub && THIRD_PARTY.test(u) && THIRD_PARTY_PAGES.test(rel)) { /* cited as third-party, and the page says so */ }
      else if (!isGithub && !TOOL.test(u) && !OFFICIAL.test(u)) fail.push(`${rel}: link is neither an official domain nor a map tool: ${u}`);
      if (!isGithub && !allowed.has(unesc(u).replace(/\/$/, ''))) fail.push(`${rel}: external URL missing from data/aecba91e/sources.json: ${unesc(u)}`);
      continue;
    }
    if (u.startsWith('#')) { if (!ids.has(u.slice(1))) fail.push(`${rel}: missing anchor ${u}`); continue; }
    const [filePart, frag] = u.split('#');
    const target = normalize(join(dir, filePart));
    if (!existsSync(target)) { fail.push(`${rel}: broken internal link ${u}`); continue; }
    if (frag && /\.html$/i.test(filePart) && !new RegExp(`id="${frag}"`).test(read(target))) fail.push(`${rel}: anchor #${frag} not found in ${filePart}`);
  }

  // factual rows must cite something
  for (const tr of html.matchAll(/<tr\s+([^>]*?)>([\s\S]*?)<\/tr>/g)) {
    const attrs = tr[1];
    const st = (attrs.match(/data-status="([^"]+)"/) || [])[1];
    if (!st || !FACTUAL.has(st)) continue;
    if (/data-nosrc="1"/.test(attrs)) continue;
    if (!/href="https?:/.test(tr[2])) fail.push(`${rel}: ${st} row without a source link: ${tr[2].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 70)}`);
  }

  // tables marked data-table must hold at least one data row
  for (const t of html.matchAll(/<table[^>]*data-table[^>]*>([\s\S]*?)<\/table>/g)) {
    const dataRows = (t[1].match(/<tr[^>]*data-(?:status|date|venue|hotel)=/g) || []).length;
    if (!dataRows) fail.push(`${rel}: data-table element with no rows`);
  }

  const ph = html.match(/TODO|TBD|lorem|undefined|NaN|\[object object/gi);
  if (ph) fail.push(`${rel}: placeholder text present (${[...new Set(ph)].join(', ')})`);
}

// an event labelled single-entry must not have a second start on the schedule
{
  const ev = JSON.parse(read(join(ROOT, 'data/aecba91e/events.json')));
  const starts = new Map();
  for (const r of ev.rows) if (r.kind === 'entry') starts.set(r.event, (starts.get(r.event) || 0) + 1);
  for (const r of ev.rows) if (r.entry_status === 'confirmed-single' && starts.get(r.event) !== 1) fail.push(`${r.id}: single-entry label on event #${r.event}, which has ${starts.get(r.event)} starts`);
}

// counts must agree with the dataset
const ev = JSON.parse(read(join(ROOT, 'data/aecba91e/events.json')));
const tourneys = read(join(SITE, 'pages/tournaments.html'));
const rendered = (tourneys.match(/<tr[^>]+data-date=/g) || []).length;
if (rendered !== ev.rows.length) fail.push(`pages/tournaments.html renders ${rendered} rows, events.json has ${ev.rows.length}`);
for (const r of ev.rows) {
  if (!/venetianlasvegas\.com/.test(r.sched_url || '')) fail.push(`${r.id}: schedule source is not an official domain`);
  if (!/^https:\/\/www\.venetianlasvegas\.com\/content\/dam\/.+-structure_\d+\.pdf$/.test(r.struct_url || '')) fail.push(`${r.id}: structure-sheet link is not a numbered official PDF: ${r.struct_url}`);
  if (r.entry_status === 'confirmed-single' && !(r.fee > 0)) fail.push(`${r.id}: confirmed row without a printed house fee`);
  if (r.entry_status === 'confirmed-single' && !r.late_close && !r.late_close_text) fail.push(`${r.id}: confirmed row with no registration close of any kind`);
}
// every page must be reachable: from the landing page, or from the venues index it links to
const corpus = files.map(read).join('\n');
for (const path of files) {
  const rel = relative(SITE, path);
  if (rel === 'index.html') continue;
  const name = rel.split('/').pop();
  if (!corpus.includes(`href="${name}"`) && !corpus.includes(`href="./${name}"`)) fail.push(`${rel} is not linked from any page`);
}

console.log(`checked ${files.length} pages · ${externalCount} external links, ${externals.size} distinct URLs, ${ledger.urls.length} in the ledger · ${ev.rows.length} dataset rows, ${rendered} rendered`);
for (const w of warn) console.log('warn:', w);
if (fail.length) { console.error(`FAIL (${fail.length})`); for (const msg of [...new Set(fail)]) console.error(' -', msg); process.exit(1); }
console.log('OK: links, anchors, ledger coverage, row sourcing, row counts and placeholders all pass.');
