import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFile, readdir } from 'node:fs/promises';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// Regression tests for the published root site (session 6bc143b9).
// They read the generated pages exactly as a visitor receives them.

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

async function page(rel) {
  return readFile(join(ROOT, rel), 'utf8');
}

async function walkHtml(dir, out = []) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) await walkHtml(p, out);
    else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}

test('every page that contains a table also contains the search box', async () => {
  const files = await walkHtml(join(ROOT, 'pages'));
  files.push(join(ROOT, 'index.html'));
  const missing = [];
  for (const f of files) {
    const t = await readFile(f, 'utf8');
    if (/<table/.test(t) && !t.includes('id="q"')) missing.push(f);
  }
  assert.deepEqual(missing, [], 'table page without a search box');
});

test('event tables expose the date selector and confirmed single-entry toggle', async () => {
  const t = await page('pages/tournaments.html');
  assert.match(t, /id="dfrom"/);
  assert.match(t, /id="dto"/);
  assert.match(t, /id="fse"/);
  assert.match(t, /Confirmed single-entry \/ freezeout only/);
});

test('hotels page publishes the dated stay capture log with the required columns', async () => {
  const t = await page('pages/hotels.html');
  for (const col of ['Checkout total', 'Nightly average', 'Resort fee / night', 'Tax',
                     'Parking', 'Cancellation deadline', 'Rate timestamp']) {
    assert.ok(t.includes(col), `missing capture column: ${col}`);
  }
  assert.match(t, /Dated stay captures/);
  assert.match(t, /id="pbudget"/);
  assert.match(t, /id="pquality"/);
});

test('planner keeps the incomplete-without-quote semantics and adds budget/quality controls', async () => {
  const [planner, script] = await Promise.all([
    page('pages/planner.html'),
    page('assets/app.js'),
  ]);
  assert.match(planner, /placeholder="no date-specific quote recorded"/);
  assert.doesNotMatch(planner, /id="ptrue"[^>]*value="0"/);
  assert.match(planner, /id="pbudget"/);
  assert.match(planner, /id="pquality"/);
  assert.match(planner, /quote needed/);
  assert.match(script, /grandTotal=tripComplete\?/);
});

test('routes page keeps the honest 30-minute filter', async () => {
  const [routes, script] = await Promise.all([
    page('pages/routes.html'),
    page('assets/app.js'),
  ]);
  assert.match(routes, /id="walkfilter"/);
  assert.match(script, /data-min/);
});

test('monitor page carries the per-room morning feed', async () => {
  const t = await page('pages/monitor.html');
  assert.match(t, /Morning room feed/);
  assert.match(t, /Venetian Poker Room/);
});

test('retired generator pages redirect instead of contradicting the site', async () => {
  for (const [rel, target] of [
    ['pages/qa.html', 'questions.html'],
    ['pages/flagged.html', 'flagged-review.html'],
    ['pages/multientry.html', 'tournaments-double.html'],
    ['pages/sources.html', 'method.html'],
  ]) {
    const t = await page(rel);
    assert.match(t, new RegExp(`url=${target}`), rel);
  }
});

test('rows whose official source changed carry a visible badge', async () => {
  const t = await page('pages/tournaments.html');
  // the DSE schedule and several room pages changed after rows were read
  assert.ok(t.includes('source changed') || t.includes('Last checked'),
    'expected a last-checked column and, where applicable, changed badges');
  const monitor = await page('pages/monitor.html');
  assert.match(monitor, /Changes detected|No change has been detected yet/);
});

test('quality workflow regenerates with the canonical builder and checks drift', async () => {
  const t = await readFile(join(ROOT, '.github/workflows/quality.yml'), 'utf8');
  assert.match(t, /build_ea99006a\.py/);
  assert.match(t, /check_ea99006a\.py/);
  assert.match(t, /git diff --exit-code/);
  const scrape = await readFile(join(ROOT, '.github/workflows/daily-scrape.yml'), 'utf8');
  assert.doesNotMatch(scrape, /build_c6087e2c\.py[\s\S]*index\.html pages\//);
  assert.match(scrape, /git add data\/c6087e2c\/$/m);
});

// Session d615f79e: the optional assumed-playing-length check on the day schedule.
// A pair cannot be played in sequence only when neither order is possible; a missing
// late-registration close is undecidable, never impossible.
test('schedule: assumed-length sequencing check is optional and correct on known cases', async () => {
  const t = await page('pages/schedule.html');
  assert.match(t, /id="seqh"/);
  assert.match(t, /id="seqdata"/);
  const m = t.match(/\/\*SEQ-BEGIN\*\/([\s\S]*?)\/\*SEQ-END\*\//);
  assert.ok(m, 'seqCheck block is present');
  const seqCheck = new Function(m[1] + '; return seqCheck;')();
  const A = { s: 600, l: 660 };   // starts 10:00, registration closes 11:00
  const B = { s: 610, l: 700 };   // starts 10:10, registration closes 11:40
  assert.equal(seqCheck([A, B], 180).cannot.length, 1, '3 h play: A cannot be finished before B closes, nor B before A');
  assert.equal(seqCheck([A, B], 60).cannot.length, 0, '1 h play: B can be entered at 11:00 after A');
  const C = { s: 720, l: null };  // no late-registration close stated
  const r = seqCheck([A, C], 60);
  assert.equal(r.cannot.length, 0, 'an unstated close is never treated as impossible');
  assert.equal(r.unknown, 1);
});

/* ---- session 0fd4c550: the guards this session added, tested the way a visitor is affected ---- */

async function json(rel) {
  return JSON.parse(await page(rel));
}

test('the trip window is arithmetically a real 7-night stay', async () => {
  const meta = await json('data/ea99006a/meta.json');
  const t = meta.trip;
  const nights = (new Date(t.check_out) - new Date(t.check_in)) / 86400000;
  assert.equal(nights, t.nights, 'check_out must be check_in + nights, not the last playing day');
  assert.equal(t.last_playing_day, new Date(new Date(t.check_out) - 86400000).toISOString().slice(0, 10),
    'the last playing day is the day before checkout');
  assert.match(t.rationale, /7 nights, so the seven full playing days run/,
    'the rationale must name both the stay and the playing days');
});

test('the scheduled generator reproduces the committed records (no silent revert on the next run)', () => {
  // recheck-ea99006a.yml runs scripts/integrate_b3be876c.py and commits whatever it changes, so the
  // generator has to carry every published correction. The guard restores the tree when it finishes.
  execFileSync('python3', ['scripts/check_idempotency_0fd4c550.py'], { cwd: ROOT, stdio: 'pipe' });
});

test('the recommended window matches the live official read field by field', async () => {
  const v = await json('data/ea99006a/window_verification_0fd4c550.json');
  assert.ok(v.rows_on_page >= 28, 'the window read must cover the schedule rows for the stay');
  assert.equal(v.rows_differing, 0, 'a value disagreement must be resolved before publishing');
  assert.equal(v.rows_matched, v.rows_on_page);
  const html = await page('pages/verification.html');
  assert.match(html, /Recommended window, re-read from the live page/);
  assert.match(html, /window_live_2026-11-19_0fd4c550\.tsv/);
});

test('every captured stay term on a hotel row has its official page and read date', async () => {
  const hotels = await json('data/ea99006a/hotels.json');
  for (const h of hotels) {
    for (const [field, srcField, dateField] of [
      ['resort_fee_text', 'resort_fee_source', 'resort_fee_read'],
      ['parking', 'parking_source', 'parking_read'],
      ['cancel', 'cancel_source', 'cancel_read'],
    ]) {
      if (!h[field]) continue;
      assert.match(h[srcField] || '', /^https:\/\//, `${h.key}.${srcField} must be an official https page`);
      assert.match(h[dateField] || '', /^\d{4}-\d{2}-\d{2}$/, `${h.key}.${dateField} must be a read date`);
    }
  }
  const ven = hotels.find((h) => h.key === 'venetian');
  assert.equal(ven.parking_self_per_night, 20, 'the published guest parking fee is part of the true cost');
  assert.equal(ven.cancel_hours, 24, 'the refundable rate carries its own cancellation deadline');
  assert.match(ven.checkin_checkout, /Check-out time is 11:00 a\.m\./, 'checkout hour drives the day plan');
});

test('the guaranteed-pool ratio is stored per row and matches the two published figures', async () => {
  const rows = await json('data/ea99006a/venetian.json');
  let stored = 0;
  for (const r of rows) {
    if (r.gtd_to_entry == null) continue;
    stored += 1;
    const g = parseFloat(String(r.guarantee).replace(/,/g, ''));
    assert.ok(Number.isFinite(g) && r.buyin > 0, 'a stored ratio needs both figures');
    assert.equal(r.gtd_to_entry, Math.round((g / r.buyin) * 10) / 10, `${r.date} #${r.event_no} ratio`);
    assert.match(r.gtd_to_entry_note, /descriptive/, 'the ratio must say it is not a forecast');
  }
  assert.ok(stored > 60, 'most rows must carry the ratio, not just a few');
});

test('the brief is traced requirement by requirement, and the gaps name their blocker', async () => {
  const req = await json('data/ea99006a/requirements.json');
  const allowed = Object.keys(req.statuses);
  assert.ok(req.rows.length >= 35, 'the register must cover the whole brief');
  for (const r of req.rows) {
    assert.ok(allowed.includes(r.status), `${r.id} has an undefined status`);
    assert.match(r.evidence, /^https:\/\/[^"]+$/, `${r.id} needs a link a reader can check`);
    assert.ok(r.where && r.note, `${r.id} must say where it lives and what limits it`);
  }
  const html = await page('pages/requirements.html');
  assert.match(html, /Requirements: what was asked, what is on the site, what is blocked/);
  assert.match(html, /id="q"/, 'the register is searchable like every other table');
  assert.match(html, /data-q="blocked on an official source"/, 'a reader can filter to what is blocked');
});

test('the planner prefills the hotel side from the dated log instead of asking for input', async () => {
  const html = await page('pages/planner.html');
  assert.match(html, /<select id="pquote"/);
  assert.match(html, /data-datematched="0"/, 'the logged capture must be labelled not date-matched');
  assert.doesNotMatch(html, /id="ptrue"[^>]*value="0"/, 'a zero hotel cost is never presented as a quote');
  assert.match(html, /data-park="20\.00"/, 'parking comes from the official page, with the fee in the markup');
  const script = await page('assets/app.js');
  assert.match(script, /data-datematched/);
  assert.match(script, /Mandatory stay cost that IS verified/);
});

test('the 8 a.m. question is answered from the published starts, not left to the reader', async () => {
  const html = await page('pages/schedule.html');
  assert.match(html, /Can a day start at 8 a\.m\.\? Answered from the published starts/);
  assert.match(html, /no enterable event starts before <b>9:10 AM<\/b>/);
  const flags = await json('data/ea99006a/flags.json');
  assert.ok(flags.some((f) => f.id === 'F57' && /8 a\.m\./.test(f.detail)), 'F57 records the limit');
  assert.ok(flags.some((f) => f.id === 'F58' && /28 of 28 matched/.test(f.detail)), 'F58 records the re-read');
});

test('both hotel filter bars read one tier ranking, and the selects match it', async () => {
  // The quality floor was once stored as a name in one table and a number in another, so "Luxury only"
  // hid the Luxury rows. The generator now writes one rank everywhere, and the selects offer those
  // same numbers; if the two drift, a floor silently hides hotels that meet it.
  const html = await page('pages/hotels.html');
  const ranks = [...html.matchAll(/data-tier="([^"]*)" data-tier-rank="([^"]*)"/g)];
  assert.ok(ranks.length >= 10, 'every hotel row must carry its rank beside its name');
  const order = ['Budget', 'Mid-scale', 'Upscale', 'Upper upscale', 'Deluxe', 'Luxury'];
  for (const [, name, rank] of ranks) {
    if (rank === '') continue;
    const want = order.findIndex((t) => t.toLowerCase() === name.toLowerCase());
    assert.equal(want, Number(rank), `rank for "${name}"`);
  }
  const opts = [...html.matchAll(/<option value="(\d+)">([^<]+)<\/option>/g)].map((m) => [Number(m[1]), m[2]]);
  assert.ok(opts.some(([v, l]) => l === 'Luxury only' && v === order.indexOf('Luxury')), 'Luxury-only floor value');
  assert.ok(opts.some(([v, l]) => l === 'Deluxe or better' && v === order.indexOf('Deluxe')), 'Deluxe floor value');
  // one owner per table: the itemized table declares it, so the page-wide bar cannot reset it
  assert.match(html, /<table class="data" id="hitems" data-owned="hotels">/);
  const script = await page('assets/app.js');
  assert.match(script, /t\.hasAttribute\('data-owned'\)/);
  assert.match(script, /var cs=\[num\(ceil\),num\(gb\)\][\s\S]{0,80}Math\.min/, 'the stricter ceiling wins');
  // a row with no verified tier must never be hidden by a floor, like a row with no verified walk time
  assert.match(script, /if\(tk!==null&&tk<pmin\) ok=false;/);
});
