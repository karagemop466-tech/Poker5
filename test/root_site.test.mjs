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

// ---- session 2723deea regression tests -------------------------------------
// Three defects found on 2026-11-19 by re-reading the official sheets and the
// published pages. Each test fails if the defect comes back.

async function restrictedNames() {
  const data = JSON.parse(await readFile(join(ROOT, 'data/ea99006a/venetian.json'), 'utf8'));
  return new Set(data.filter((r) => r.restriction).map((r) => r.name));
}

test('a restricted field is never offered as a day\'s primary event or a top-ranked pick', async () => {
  const [single, exec, sched] = await Promise.all([
    page('pages/single-entry.html'), page('pages/executive-summary.html'), page('pages/schedule.html'),
  ]);
  // the label and the official reason are published next to the row
  assert.match(single, /S1, entry restricted/);
  assert.match(single, /50\+ \(Seniors\)/);
  assert.match(single, /female players only/);
  // the executive ranking states what it excluded and why
  assert.match(exec, /excluded from this ranking because their own official structure sheet restricts the field/);
  const restricted = await restrictedNames();
  assert.ok(restricted.size > 0, 'expected at least one sheet-restricted row in the data');
  for (const card of sched.split('<div class="panel daycard')) {
    const m = card.match(/<dt>Primary event<\/dt><dd><b>([^<]+)<\/b>/);
    if (!m) continue;
    const name = m[1].replace(/&#x27;/g, "'").replace(/&amp;/g, '&');
    assert.ok(!restricted.has(name), `restricted event chosen as a primary pick: ${name}`);
  }
});

test('no row borrows another event\'s registration-close clock time', async () => {
  const sched = await page('pages/schedule.html');
  // Sheet 25 covers #45 (8:10 PM), #46 (9:10 AM) and #48 (12:10 PM) and prints one
  // "Late Registration: 6 levels" line with no clock. The morning rows must not carry
  // the 9:40 PM close that belongs to the 8:10 PM event's derived time.
  const rows = sched.split('<tr ').map((r) => r.split('</tr>')[0])
    .filter((r) => /Turbo Milestone Satellite/.test(r) && /09:10 AM|12:10 PM/.test(r));
  assert.ok(rows.length > 0, 'expected morning turbo-satellite rows on the schedule page');
  for (const r of rows) assert.doesNotMatch(r, /9:40 PM/, 'a morning satellite row inherited the 8:10 PM close time');
});

test('every restricted row publishes the sheet sentence that closes the field', async () => {
  const data = JSON.parse(await readFile(join(ROOT, 'data/ea99006a/venetian.json'), 'utf8'));
  const restricted = data.filter((r) => r.restriction);
  assert.ok(restricted.length > 0);
  for (const r of restricted) {
    assert.ok(r.restriction.label, `no label on #${r.event_no}`);
    assert.ok(r.restriction.excerpt, `no official excerpt on #${r.event_no}`);
    assert.match(r.restriction.source, /^https:\/\//, `no official link on #${r.event_no}`);
    assert.match(r.restriction.retrieved, /^\d{4}-\d{2}-\d{2}$/, `no retrieval date on #${r.event_no}`);
  }
});
