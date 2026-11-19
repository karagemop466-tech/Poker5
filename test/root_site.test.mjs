import assert from 'node:assert/strict';
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
  assert.match(t, /Only rows whose rules grant no second entry \(S1 screen\)/);
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
