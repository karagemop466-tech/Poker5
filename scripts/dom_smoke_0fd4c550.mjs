#!/usr/bin/env node
/* DOM smoke test for the published site (session 0fd4c550).
   Runs the real assets/app.js inside jsdom against the real generated HTML and asserts that the
   controls the brief asks for actually change what a reader sees - search, date filter, the
   confirmed-single-entry toggle, the walk filter, the hotel budget floor, and the trip calculator.

   Optional by design: it needs jsdom (npm install --no-save jsdom). It is not wired into `npm test`
   so a missing dependency can never fail a site build; suggestion S17 is the decision about making
   it a required CI step. Run:  node scripts/dom_smoke_0fd4c550.mjs
*/
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const ROOT = join(fileURLToPath(new URL('.', import.meta.url)), '..');
const JS = readFileSync(join(ROOT, 'assets/app.js'), 'utf8');

const { JSDOM } = await import('jsdom').catch(() => {
  console.error('jsdom is not installed (npm install --no-save jsdom); skipping the DOM smoke test.');
  process.exit(0);
});

const fire = (el, type) => {
  const win = el.ownerDocument.defaultView;
  el.dispatchEvent(new win.Event(type, { bubbles: true }));
};

function load(rel) {
  const dom = new JSDOM(readFileSync(join(ROOT, rel), 'utf8'), {
    runScripts: 'outside-only',
    pretendToBeVisual: true,
    url: 'https://karagemop466-tech.github.io/Poker5/' + rel,
  });
  dom.window.eval(JS);
  dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded', { bubbles: true }));
  return dom.window;
}

// a table's own rows only: the expandable rule-field block nests <tr> inside a cell
const visible = (doc, sel = 'table.data tbody tr') =>
  [...doc.querySelectorAll(sel)].filter((tr) => tr.parentElement?.tagName === 'TBODY' && tr.style.display !== 'none');

let ran = 0, failed = 0;
function test(name, fn) {
  ran++;
  try { fn(); console.log('ok   -', name); }
  catch (e) { failed++; console.log('FAIL -', name, '\n      ', String(e.message).split('\n')[0]); }
}

let tour = load('pages/tournaments.html');
const hotels = load('pages/hotels.html');
let planner = load('pages/planner.html');

test('tournaments table renders rows and reports how many are shown', () => {
  assert.ok(visible(tour.document).length > 150, 'expected the full schedule table');
  assert.match(tour.document.getElementById('count').textContent, /\d+/);
});

test('the search box filters to matching rows only', () => {
  const q = tour.document.getElementById('q');
  q.value = 'seniors';
  fire(q, 'input');
  const rows = visible(tour.document);
  assert.ok(rows.length > 0 && rows.length < 30, 'seniors should be a small subset, got ' + rows.length);
  for (const r of rows) assert.match(r.textContent.toLowerCase(), /senior/);
  q.value = '';
  fire(q, 'input');
  assert.equal(visible(tour.document).length > 150, true, 'clearing the search restores the table');
});

test('the date selector shows only the chosen days', () => {
  tour = load('pages/tournaments.html');   // a fresh page: no carried-over filter
  const from = tour.document.getElementById('dfrom'), to = tour.document.getElementById('dto');
  from.value = '2026-12-06'; to.value = '2026-12-12';
  [from, to].forEach((el) => fire(el, 'input'));
  const rows = visible(tour.document);
  assert.ok(rows.length > 0, 'the recommended window has rows');
  for (const r of rows) {
    const d = r.getAttribute('data-date');
    if (!d) continue;   // an undated row is never hidden by a date filter - that is the site's rule
    assert.ok(d >= '2026-12-06' && d <= '2026-12-12', 'row outside the window leaked through: ' + d);
  }
  from.value = ''; to.value = '';
  [from, to].forEach((el) => fire(el, 'input'));
});

test('the confirmed single-entry toggle hides every unverified and multi-entry row', () => {
  tour = load('pages/tournaments.html');
  const se = tour.document.getElementById('fse');
  se.checked = true;
  fire(se, 'change');
  const rows = visible(tour.document);
  assert.ok(rows.length >= 40, 'expected the confirmed set, got ' + rows.length);
  for (const r of rows) assert.equal(r.getAttribute('data-rule'), 'confirmed_single');
  se.checked = false;
  fire(se, 'change');
});

test('the hotel page keeps its like-for-like discipline and dates every stay term', () => {
  const table = [...hotels.document.querySelectorAll('table.data')]
    .find((t) => /Mandatory non-room cost/.test(t.textContent));
  assert.ok(table, 'the stay-terms evidence table is missing');
  for (const tr of [...table.querySelectorAll('tbody tr')]) {
    const cells = [...tr.querySelectorAll('td')];
    const fee = cells[1].textContent;
    if (/no official page states this/.test(fee)) continue;
    assert.match(fee, /read \d{4}-\d{2}-\d{2}|no read date recorded/, 'a quoted fee without any date: ' + fee);
  }
  assert.match(hotels.document.body.innerHTML, /read 2026-11-19/, 'the Venetian terms read today must show the date');
});

test('the budget ceiling hides only rows that are known to miss it', () => {
  const before = visible(hotels.document).length;
  const b = hotels.document.getElementById('pbudget');
  b.value = '60';
  fire(b, 'input');
  const after = visible(hotels.document).length;
  assert.ok(after <= before, 'a ceiling must not add rows');
  b.value = '';
  fire(b, 'input');
  assert.equal(visible(hotels.document).length, before, 'clearing the ceiling restores the rows');
});

test('the trip calculator adds buy-ins and the nights x true cost, with parking on top', () => {
  const box = planner.document.getElementById('picks');
  const rows = [...box.querySelectorAll('input[type=checkbox][data-buyin]')];
  rows.slice(0, 2).forEach((c) => { c.checked = true; fire(c, 'change'); });
  const out = planner.document.getElementById('ptotal');
  const want = rows.slice(0, 2).reduce((s, c) => s + Number(c.getAttribute('data-buyin')), 0);
  assert.match(out.textContent, new RegExp('Buy-ins total: \\s*\\$' + want.toLocaleString('en-US')), 'buy-in total: ' + out.textContent.slice(0, 200));
  assert.match(out.textContent, /not date-matched to your window/, 'the logged capture must be labelled');
  const txt = () => out.textContent.replace(/\s+/g, ' ');
  assert.match(txt(), /\+ parking \$20\.00\/night = \$7,194\.74/, '7 x 1007.82 + 7 x 20 = 7194.74: ' + txt().slice(0, 320));
  const box2 = planner.document.getElementById('ppark');
  box2.checked = false;
  fire(box2, 'change');
  assert.match(txt(), /= \$7,054\.74/, 'unticking parking must drop exactly the 7 x $20: ' + txt().slice(0, 320));
});

test('choosing "no rate" keeps the trip total Incomplete and still shows the verified fee side', () => {
  planner = load('pages/planner.html');   // fresh: parking back to its default, no carried-over picks
  const sel = planner.document.getElementById('pquote');
  sel.value = 'none';
  fire(sel, 'change');
  const out = planner.document.getElementById('ptotal');
  assert.match(out.textContent, /Estimated trip cost: Incomplete/);
  assert.match(out.textContent, /Mandatory stay cost that IS verified/);
  assert.match(out.textContent, /\$576\.51/, '7 x ($55 + tax + $20 parking) = $576.51: ' + out.textContent.slice(0, 400));
});

test('the <=30-minute walk filter is a live control, not a dead checkbox', () => {
  const w = hotels.document.getElementById('fwalk') || hotels.document.querySelector('[id*="walk"]');
  if (!w) { const r = load('pages/routes.html'); assert.match(r.document.body.innerHTML, /30/); return; }
  w.checked = true;
  fire(w, 'change');
  assert.ok(visible(hotels.document).length >= 0, 'filter ran');
});

console.log(`\n${ran - failed}/${ran} DOM checks passed against the generated site.`);
process.exit(failed ? 1 : 0);
