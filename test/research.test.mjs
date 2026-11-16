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
