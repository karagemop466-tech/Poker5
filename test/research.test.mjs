import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { events, hotels, lastVerified, roomTax, routes } from '../site-src/data.mjs';

const statuses = ['single', 'multi', 'unknown', 'restricted'];
const validHttps = (value) => {
  const url = new URL(value);
  return url.protocol === 'https:';
};

test('research snapshot has the verified date and expected coverage', () => {
  assert.equal(lastVerified, 'November 16, 2026');
  assert.equal(events.length, 11);
  assert.equal(hotels.length, 4);
  assert.equal(routes.length, 4);
  assert.equal(roomTax.rate, '13.38%');
});

test('strict primary list stays empty until one-entry-overall is verified', () => {
  assert.equal(events.filter((event) => event.status === 'single').length, 0);
  assert.deepEqual(
    events.reduce((counts, event) => {
      counts[event.status] = (counts[event.status] ?? 0) + 1;
      return counts;
    }, {}),
    { multi: 4, unknown: 6, restricted: 1 },
  );
});

test('event records have unique IDs, complete evidence, and valid status values', () => {
  assert.equal(new Set(events.map((event) => event.id)).size, events.length);
  for (const event of events) {
    assert.ok(event.id && event.title && event.venue && event.date, `missing event basics: ${event.id}`);
    assert.ok(statuses.includes(event.status), `invalid status for ${event.id}`);
    assert.ok(event.statusLabel && event.rule && event.caveat, `missing rule explanation: ${event.id}`);
    assert.ok(event.sources.length > 0, `missing sources: ${event.id}`);
    for (const source of event.sources) {
      assert.ok(source.label, `missing source label: ${event.id}`);
      assert.ok(validHttps(source.url), `source must use https: ${event.id} ${source.url}`);
    }
  }
});

test('confirmed multiple-entry records explicitly describe a second bullet', () => {
  const evidenceTerms = /re-?entry|rebuys?|add-on|entries maximum|four entries|one entry and one/i;
  const multiple = events.filter((event) => event.status === 'multi');
  assert.equal(multiple.length, 4);
  for (const event of multiple) {
    assert.match(`${event.rule} ${event.statusLabel}`, evidenceTerms, event.id);
  }
  const wynnDaily = events.find((event) => event.id === 'wynn-daily-tournaments');
  assert.match(wynnDaily.rule, /Friday noon.*unlimited.*rebuys/i);
  assert.match(wynnDaily.rule, /re-entry is not allowed/i);
});

test('unverified and restricted findings are not presented as open single-entry events', () => {
  for (const event of events.filter((item) => item.status === 'unknown')) {
    assert.match(`${event.rule} ${event.caveat}`, /not verified|not establish|not.*cap|not.*terms|do not state|silent|unverified|not available/i, event.id);
  }
  const restricted = events.find((event) => event.status === 'restricted');
  assert.match(restricted.rule, /not a generally open tournament/i);
});

test('hotel, tax, route and quote source links are secure and present', () => {
  for (const hotel of hotels) {
    assert.ok(hotel.name && hotel.room && hotel.size && hotel.sample, `incomplete hotel: ${hotel.id}`);
    assert.ok(validHttps(hotel.booking), `invalid hotel room link: ${hotel.id}`);
    assert.ok(hotel.sources.length > 0, `missing hotel sources: ${hotel.id}`);
    for (const source of hotel.sources) assert.ok(validHttps(source.url), `${hotel.id}: ${source.url}`);
  }
  assert.ok(hotels.find((hotel) => hotel.id === 'encore').sources.some((source) => source.url.includes('reservations.wynnlasvegas.com')));
  assert.ok(hotels.find((hotel) => hotel.id === 'venetian').sources.some((source) => source.url.includes('arrival_date=2026-12-03')));
  assert.ok(validHttps(roomTax.source));
  for (const route of routes) {
    assert.ok(route.from && route.to && route.distance && route.time && route.note);
    assert.ok(validHttps(route.source.url));
  }
});

test('Pages excludes repository-only notes and test tooling from the published root', async () => {
  const config = await readFile(new URL('../_config.yml', import.meta.url), 'utf8');
  for (const item of ['COORDINATION.md', 'README.md', 'package.json', 'scripts/', 'test/', 'serve.mjs', 'site-src/']) {
    assert.ok(config.includes(item), `GitHub Pages should exclude ${item}`);
  }
});

test('trip calculator keeps unknown hotel costs incomplete and labels the auto-selected dates as a scenario', async () => {
  const [planner, script] = await Promise.all([
    readFile(new URL('../pages/planner.html', import.meta.url), 'utf8'),
    readFile(new URL('../assets/app.js', import.meta.url), 'utf8'),
  ]);
  assert.match(planner, /Estimated trip cost =/);
  assert.match(planner, /placeholder="no date-specific quote recorded"/);
  assert.doesNotMatch(planner, /id="ptrue"[^>]*value="0"/);
  assert.doesNotMatch(planner, /id="nights"[^>]*value="7"/);
  assert.doesNotMatch(planner, /<option[^>]+data-rate=/);
  assert.match(planner, /automatically selected research scenario, not confirmed travel dates/i);
  assert.match(planner, /not verified for every hotel/i);
  assert.match(script, /hotelComplete/);
  assert.match(script, /hotelTotal=hotelComplete\?/);
  assert.match(script, /grandTotal=tripComplete\?/);
  assert.match(script, /No date-specific room quote is currently recorded/);
  assert.match(script, /One buy-in is counted per selected event/);
});

test('confirmed single-entry toggle excludes unverified and multi-entry rows', async () => {
  const [tournaments, script] = await Promise.all([
    readFile(new URL('../pages/tournaments.html', import.meta.url), 'utf8'),
    readFile(new URL('../assets/app.js', import.meta.url), 'utf8'),
  ]);
  assert.match(tournaments, /Only rows whose rules grant no second entry \(S1 screen\)/);
  assert.match(script, /if\(ok && s && tr\.getAttribute\('data-rule'\)!=='confirmed_single'\) ok=false;/);
  assert.doesNotMatch(script, /data-rule'\)!=='unknown'.*data-rule/);
});

test('legacy Venetian capture treats explicitly priced subsequent buy-ins as multi-entry', async () => {
  const [captureText, structuresText, mergeSource] = await Promise.all([
    readFile(new URL('../data/c6087e2c/events_verified.json', import.meta.url), 'utf8'),
    readFile(new URL('../data/c6087e2c/structures.json', import.meta.url), 'utf8'),
    readFile(new URL('../scripts/merge_251c122f.py', import.meta.url), 'utf8'),
  ]);
  const capture = JSON.parse(captureText);
  const structures = JSON.parse(structuresText);
  const affected = capture.events.filter((event) => [18, 58].includes(event.event_no));
  assert.equal(affected.length, 2);
  for (const event of affected) {
    assert.equal(event.verdict, 'adds_second_entry', `event #${event.event_no}`);
    assert.equal(event.single_entry_confirmed, false, `event #${event.event_no}`);
    assert.equal(event.structure_url, structures.sheets['8'].url);
    assert.equal(event.sheet_retrieved_at, structures.sheets['8'].retrieved_at);
    for (const field of Object.values(event.rule_fields)) {
      assert.equal(field.retrieved_at, structures.sheets['8'].retrieved_at);
    }
    assert.deepEqual(event.rule_fields.re_entry.excerpts, [
      "All subsequent buy in's after the initial buy in will be $200.",
    ]);
    assert.equal(event.rule_fields.re_entry.source, structures.sheets['8'].url);
  }
  assert.match(structures.sheets['8'].rules_text, /All subsequent buy in's after the initial buy in will be \$200/i);
  assert.match(mergeSource, /def sheet_grants_second_entry/);
  assert.match(mergeSource, /subsequent\|additional\|second/);
});

test('only the canonical source monitor rebuilds and commits the root site', async () => {
  const [capture, publisher] = await Promise.all([
    readFile(new URL('../.github/workflows/daily-scrape.yml', import.meta.url), 'utf8'),
    readFile(new URL('../.github/workflows/recheck-ea99006a.yml', import.meta.url), 'utf8'),
  ]);
  assert.ok(capture.includes('Commit the refreshed research capture only'));
  assert.ok(!capture.includes('python3 scripts/build_c6087e2c.py'));
  assert.ok(!capture.includes('git add data/c6087e2c/ index.html pages/'));
  assert.ok(publisher.includes('python3 scripts/build_ea99006a.py'));
  assert.ok(publisher.includes('git add data/ea99006a pages index.html assets'));
});

test('dashboard and ledger link to each other, publish correctly, and integrate from the root', async () => {
  const [dashboard, ledger, published, rootHome] = await Promise.all([
    readFile(new URL('../site-src/index.html', import.meta.url), 'utf8'),
    readFile(new URL('../site-src/sources.html', import.meta.url), 'utf8'),
    readFile(new URL('../site-b50aa7f5/index.html', import.meta.url), 'utf8'),
    readFile(new URL('../index.html', import.meta.url), 'utf8'),
  ]);
  assert.equal(published, dashboard);
  assert.match(rootHome, /href="site-b50aa7f5\/index\.html"/);
  assert.match(dashboard, /href="\.\/sources\.html"/);
  assert.match(dashboard, /src="\.\/app\.mjs"/);
  assert.match(dashboard, /href="\.\/styles\.css"/);
  assert.match(dashboard, /id="events"/);
  assert.match(dashboard, /PRIMARY LIST \/ SINGLE ENTRY OVERALL/);
  assert.match(dashboard, /id="stays"/);
  assert.match(ledger, /src="\.\/sources\.mjs"/);
  assert.match(ledger, /id="source-events"/);
  assert.match(ledger, /id="source-hotels"/);
  assert.match(ledger, /id="source-routes"/);
});

test('canonical executive summary uses current S1 verdicts, complete ranking gates, and honest monitor status', async () => {
  const [summary, meta] = await Promise.all([
    readFile(new URL('../pages/executive-summary.html', import.meta.url), 'utf8'),
    readFile(new URL('../data/ea99006a/meta.json', import.meta.url), 'utf8').then(JSON.parse),
  ]);
  assert.match(summary, /53 Venetian rows/);
  assert.match(summary, /41 as multi-entry/);
  assert.match(summary, /no sheet states a one-entry maximum/i);
  assert.match(summary, /Upcoming: highest descriptive guarantee-to-entry ratios, non-bounty S1 events/);
  assert.match(summary, /Upcoming bounty \/ PKO S1 events \(separate comparison\)/);
  assert.match(summary, /buy-in, house fee and guarantee are all present/i);
  assert.match(summary, /descriptive arithmetic only/i);
  assert.match(summary, /no live value-level run/i);
  assert.doesNotMatch(summary, /No event is confirmed as single-entry\./);
  assert.doesNotMatch(summary, /Every official URL behind a row is re-read twice daily/);
  assert.doesNotMatch(summary, /strongest candidates \(no re-entry text/);
  const tables = summary.split(/<h2>Upcoming(?: bounty \/ PKO)?/i).slice(1);
  const captureDate = Date.parse(`${meta.retrieved}T00:00:00Z`);
  for (const table of tables) {
    const nextSection = table.split('<h2>')[0];
    for (const match of nextSection.matchAll(/<tr><td class="nowrap">([^<]+)<\/td><td>[^<]*<\/td><td>([^<]+)<\/td>/g)) {
      assert.ok(Date.parse(match[1]) > captureDate, `past/current event #${match[2]} included in future ranking`);
    }
  }
});
