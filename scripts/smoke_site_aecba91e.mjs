#!/usr/bin/env node
// Behaviour smoke test for site-aecba91e/ — runs the real assets/js/app.js against the built pages
// in jsdom and asserts the filters, the sort and the trip-cost arithmetic actually work.
// Requires the optional dev dependency `jsdom`; prints SKIP and exits 0 when it is absent so the
// gate never fails for a missing test dependency.
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = process.cwd();
const SITE = join(ROOT, 'site-aecba91e');
if (!existsSync(join(ROOT, 'node_modules/jsdom'))) {
  console.log('SKIP: jsdom not installed (npm i --no-save jsdom) — behaviour test not run');
  process.exit(0);
}
const { JSDOM, VirtualConsole } = await import('jsdom');
const fail = [];
const ok = (name, cond, extra = '') => { console.log(`${cond ? 'ok  ' : 'FAIL'}  ${name}${extra ? ` — ${extra}` : ''}`); if (!cond) fail.push(name); };

const load = async (file) => {
  const html = readFileSync(join(SITE, file), 'utf8');
  const vc = new VirtualConsole();
  // the harness serves from a stub origin, so relative <script>/<link> fetches always fail here;
  // the page under test is inlined instead, and a real browser resolves those paths normally.
  vc.on('jsdomError', (e) => { if (!/Could not load (link|script)/.test(e.message)) fail.push(`${file} console error: ${e.message}`); });
  const dom = new JSDOM(html, {
    runScripts: 'dangerously', url: 'http://localhost/', pretendToBeVisual: true, virtualConsole: vc,
  });
  // inline the app so the test does not depend on file:// script loading
  const app = readFileSync(join(ROOT, 'assets/js/app.js'), 'utf8');
  dom.window.eval(app);
  await new Promise((r) => setTimeout(r, 30));
  return dom.window.document;
};
const visible = (doc) => [...doc.querySelectorAll('tr[data-status],tr[data-date]')].filter((t) => !t.hidden && t.offsetParent !== false);
const countText = (doc) => (doc.querySelector('[data-count]')?.textContent || '').trim();

// ---------- filters on the tournaments page ----------
{
  const doc = await load('pages/tournaments.html');
  const total = doc.querySelectorAll('tr[data-status],tr[data-date]').length;
  ok('tournaments: every row is rendered', total === 94, `${total} rows`);
  ok('tournaments: counter hides the 11 continuations by default', countText(doc) === `83 of ${total} rows shown`, countText(doc));

  const contHidden = [...doc.querySelectorAll('tr[data-status="continuation"]')].every((t) => t.hidden);
  ok('tournaments: continuation rows hidden by default', contHidden);
  doc.querySelector('[data-hide-cont]').checked = false;
  doc.querySelector('[data-hide-cont]').dispatchEvent(new doc.defaultView.Event('change', { bubbles: true }));
  const contShown = [...doc.querySelectorAll('tr[data-status="continuation"]')].filter((t) => !t.hidden).length;
  ok('tournaments: un-hiding shows all 11 continuation rows', contShown === 11, `${contShown} shown`);

  doc.querySelector('[data-only-confirmed]').checked = true;
  doc.querySelector('[data-only-confirmed]').dispatchEvent(new doc.defaultView.Event('change', { bubbles: true }));
  const vis = [...doc.querySelectorAll('tr[data-status]')].filter((t) => !t.hidden);
  ok('tournaments: confirmed-only leaves 54 rows', vis.length === 54, `${vis.length} visible`);
  ok('tournaments: confirmed-only shows nothing else', vis.every((t) => t.dataset.status === 'confirmed-single'));

  doc.querySelector('[data-only-confirmed]').checked = false;
  doc.querySelector('[data-only-confirmed]').dispatchEvent(new doc.defaultView.Event('change', { bubbles: true }));
  const q = doc.querySelector('[data-q]');
  q.value = 'turbo milestone satellite';
  q.dispatchEvent(new doc.defaultView.Event('input', { bubbles: true }));
  const sat = [...doc.querySelectorAll('tr[data-status]')].filter((t) => !t.hidden);
  ok('search: text filter narrows to matching rows', sat.length === 3 && sat.every((t) => /satellite/i.test(t.textContent)), `${sat.length} rows`);
  q.value = ''; q.dispatchEvent(new doc.defaultView.Event('input', { bubbles: true }));

  const from = doc.querySelector('[data-from]'), to = doc.querySelector('[data-to]');
  from.value = '2026-12-11'; to.value = '2026-12-14';
  to.dispatchEvent(new doc.defaultView.Event('change', { bubbles: true }));
  const inRange = [...doc.querySelectorAll('tr[data-date]')].filter((t) => !t.hidden);
  ok('date range: only rows inside the window stay visible',
    inRange.length > 0 && inRange.every((t) => t.dataset.date >= '2026-12-11' && t.dataset.date <= '2026-12-14'), `${inRange.length} rows`);
  from.value = ''; to.value = ''; to.dispatchEvent(new doc.defaultView.Event('change', { bubbles: true }));

  const th = [...doc.querySelectorAll('th[data-sort]')].find((h) => Number(h.dataset.sort) === 5);
  th.dispatchEvent(new doc.defaultView.MouseEvent('click', { bubbles: true }));
  const buys = [...doc.querySelectorAll('tr[data-date]')].map((t) => Number(t.children[5].dataset.v));
  ok('sort: clicking Buy-in orders the table ascending', buys.every((v, i) => i === 0 || buys[i - 1] <= v), buys.slice(0, 4).join(','));
  th.dispatchEvent(new doc.defaultView.MouseEvent('click', { bubbles: true }));
  const desc = [...doc.querySelectorAll('tr[data-date]')].map((t) => Number(t.children[5].dataset.v));
  ok('sort: clicking again reverses', desc.every((v, i) => i === 0 || desc[i - 1] >= v), desc.slice(0, 4).join(','));
}

// ---------- walk filter on the hotels page ----------
{
  const doc = await load('pages/hotels.html');
  const walk = doc.querySelector('[data-walk30]');
  walk.checked = true; walk.dispatchEvent(new doc.defaultView.Event('change', { bubbles: true }));
  const shown = [...doc.querySelectorAll('tr[data-status="hotel"]')].filter((t) => !t.hidden);
  ok('hotels: ≤30 min filter keeps only the measured same-resort walk', shown.length === 1 && /Venetian/.test(shown[0].textContent), `${shown.length} of 10 hotels`);
  const blanks = [...doc.querySelectorAll('tr[data-status="hotel"]')].filter((t) => /blank/.test(t.textContent)).length;
  ok('hotels: unconfirmed fields stay visibly blank', blanks >= 5, `${blanks} rows carry a blank`);
}

// ---------- trip-cost calculator ----------
{
  const doc = await load('pages/trip-cost.html');
  const g = (sel) => doc.querySelector(sel);
  ok('calc: nights derived from the prefilled window', g('[data-nights]').value === '4', g('[data-nights]').value);
  const rows = () => [...doc.querySelectorAll('.erow')];
  ok('calc: two preselected entries', rows().length === 2, rows().length + ' rows');
  const feeSum = rows().reduce((a, r) => a + Number(r.dataset.fee) * (Number(r.querySelector('input').value) || 0), 0);
  const set = (sel, v) => { const el = g(sel); el.value = String(v); el.dispatchEvent(new doc.defaultView.Event('input', { bubbles: true })); };
  set('[data-rate]', 833.89); set('[data-fee]', 55); set('[data-tax]', 13.38); set('[data-park]', 40);
  const perNight = 833.89 + 55 + 833.89 * 0.1338 + 40 / 4;
  const expected = feeSum + perNight * 4;
  const totalTxt = g('[data-total]').textContent.replace(/[^0-9.]/g, '');
  ok('calc: total = entries × entry fee + nights × (rate + fee + tax + parking/n)',
    Math.abs(Number(totalTxt) - expected) < 0.05, `${totalTxt} vs ${expected.toFixed(2)}`);
  ok('calc: breakdown states the true nightly cost', /true cost \/ night/.test(g('[data-break]').textContent));
  set('[data-rate]', '');
  ok('calc: a blank rate makes the hotel half unknown, not zero', /unknown/i.test(g('[data-break]').textContent) && /unknown/i.test(g('[data-total]').textContent), g('[data-total]').textContent.trim());
  set('[data-rate]', 833.89);
  const before = rows().length;
  rows()[0].querySelector('button').click();
  ok('calc: an entry can be removed', rows().length === before - 1);
  const add = g('[data-entryadd]');
  add.selectedIndex = 3; add.dispatchEvent(new doc.defaultView.Event('change', { bubbles: true }));
  ok('calc: an entry can be added from the schedule', rows().length === before, rows().length + ' rows');
}

console.log(fail.length ? `\nFAIL (${fail.length}): ${fail.join(' | ')}` : '\nOK: filters, sort and the cost model behave as specified.');
process.exit(fail.length ? 1 : 0);
