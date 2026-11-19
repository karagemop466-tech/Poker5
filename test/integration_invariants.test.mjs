import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { cpSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

// These tests protect the two properties the scheduled re-derivation must always have.
// (1) The published trip window is arithmetically self-consistent, because the planner's cost is
//     "entries x buy-ins + nights x true hotel cost" and the schedule/planner lists are cut at the
//     last playing day. (2) Running scripts/integrate_b3be876c.py - which GitHub Actions runs twice
//     a day on main - is idempotent and never reverts a correction another session made to the
//     curated hotel notes, flags, questions or suggestions. Both properties were broken on
//     2026-11-19 and the regressions are recorded in COORDINATION.md (sessions 6bc143b9, 2b98a91f,
//     96160d8f and 188dc704); these tests are what keep them fixed.

const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const readJson = (rel) => JSON.parse(read(rel));
const days = (value) => Date.parse(`${value}T00:00:00Z`) / 86_400_000;

test('the published trip window is arithmetically self-consistent', () => {
  for (const rel of ['../data/ea99006a/meta.json', '../data/ea99006a/all.json']) {
    const trip = rel.endsWith('all.json') ? readJson(rel).trip : readJson(rel).trip;
    const nights = Math.round(days(trip.check_out) - days(trip.check_in));
    assert.ok(nights > 0, `${rel}: check-out must be after check-in`);
    assert.equal(trip.nights, nights, `${rel}: nights must equal check-out minus check-in`);
    const lastPlay = new Date(days(trip.check_out) * 86_400_000 - 86_400_000).toISOString().slice(0, 10);
    assert.equal(trip.last_play_day, lastPlay, `${rel}: the last playing day must be the day before check-out`);
    // The rationale is printed on the home page and the planner, so it has to quote *this* window.
    // Asserted without pinning the sentence, because the wording is corrected often: what must never
    // come back is a rationale that names a check-out date the arithmetic contradicts (the scheduled
    // run used to write "2026-12-06 to 2026-12-12 (7 nights)" and then list events to 12 December).
    assert.ok(trip.rationale.includes(trip.check_in), `${rel}: rationale must name the check-in date`);
    assert.ok(trip.rationale.includes(trip.check_out), `${rel}: rationale must name the check-out date`);
    assert.match(trip.rationale, new RegExp(`${trip.nights} nights`), `${rel}: rationale night count`);
    for (const iso of trip.rationale.match(/\d{4}-\d{2}-\d{2}/g) || []) {
      assert.ok(iso <= trip.check_out, `${rel}: rationale quotes ${iso}, after the traveller has left`);
    }
  }
});

test('event lists are cut at the last playing day, not at the hotel check-out day', () => {
  const trip = readJson('../data/ea99006a/meta.json').trip;
  const planner = read('../pages/planner.html');
  const venetian = readJson('../data/ea99006a/venetian.json');
  const MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'];
  const pretty = (iso) => `${MONTH[Number(iso.slice(5, 7)) - 1]} ${Number(iso.slice(8, 10))}, ${iso.slice(0, 4)}`;
  // Only the event table counts: other tables on the page (the dated rate log) hold stay dates.
  const table = planner.split('<table').filter((chunk) => /Buy-in/i.test(chunk)).join('<table');
  const cells = [...table.matchAll(/<td class="nowrap">([A-Z][a-z]+ \d{1,2}, \d{4})<\/td>/g)].map((m) => m[1]);
  assert.ok(cells.length > 0, 'the planner lists dated events');
  // The window must be meaningful: the check-out day does carry listed-class events.
  const onCheckout = venetian.filter((row) => row.kind === 'entry' && row.date === trip.check_out
    && ['confirmed_single', 'unknown'].includes(row.entry_rule));
  assert.ok(onCheckout.length > 0, 'the check-out day carries events, so cutting at it is a real decision');
  assert.ok(!cells.includes(pretty(trip.check_out)),
    'the event table must not list the check-out day as a playing day');
  // The last playing day must still be reachable: the schedule page lists it, the planner simply
  // has no full-field entry that day (its Dec 12 rows are satellites), which is a data fact, not a bug.
  const sched = read('../pages/schedule.html');
  assert.ok(sched.includes(pretty(trip.last_play_day)), 'the schedule must list the last playing day');
  assert.ok(!sched.includes(`${pretty(trip.check_out)}`)
    || sched.includes(pretty(trip.last_play_day)), 'the schedule page stays scoped to the playing days');
  for (const value of cells) {
    const iso = `${value.slice(-4)}-${String(MONTH.indexOf(value.split(' ')[0]) + 1).padStart(2, '0')}-${String(value.match(/\d+/)[0]).padStart(2, '0')}`;
    assert.ok(iso >= trip.check_in && iso <= trip.last_play_day, `planner lists ${value}, outside the window`);
  }
  assert.match(planner, /you check out [^)]*\)/, 'the planner names check-out as the stay end, not a playing day');
});

test("the site's 'as of' date is a date an official source was really read", () => {
  const meta = readJson('../data/ea99006a/meta.json');
  const scrape = readJson('../data/c6087e2c/scrape_status.json');
  const ledger = readJson('../data/ea99006a/last_checked.json');
  const fetched = [];
  for (const record of Object.values(scrape.sources ?? {})) {
    if (record?.retrieved_at) fetched.push(String(record.retrieved_at).slice(0, 10));
  }
  for (const record of Object.values(ledger)) {
    if (record?.status === 'ok' && record.last_checked) fetched.push(String(record.last_checked).slice(0, 10));
  }
  assert.ok(fetched.length, 'at least one official fetch is recorded');
  assert.equal(meta.retrieved, fetched.sort().at(-1),
    'meta.retrieved must be the newest recorded official fetch, never the date the build ran');
});

test('a scheduled re-derivation run is idempotent and never reverts curated wording', () => {
  const scratch = mkdtempSync(join(tmpdir(), 'poker5-integrate-'));
  try {
    for (const dir of ['scripts', 'data/ea99006a', 'data/c6087e2c', 'data/b3be876c']) {
      cpSync(new URL(`../${dir}`, import.meta.url), join(scratch, dir), { recursive: true });
    }
    const run = () => execFileSync('python3', ['scripts/integrate_b3be876c.py'],
      { cwd: scratch, stdio: 'pipe', timeout: 120_000 });
    const snapshot = () => Object.fromEntries(['all.json', 'flags.json', 'hotels.json', 'meta.json',
      'other.json', 'questions.json', 'suggestions.json', 'venetian.json', 'wpt.json',
    ].map((name) => [name, readFileSync(join(scratch, 'data/ea99006a', name), 'utf8')]));

    const committed = snapshot();
    run();
    const afterFirst = snapshot();
    run();
    const afterSecond = snapshot();

    // Idempotence: a second run with the same capture must change nothing at all.
    assert.deepEqual(afterSecond, afterFirst,
      `a repeat run changed ${Object.keys(afterSecond).filter((k) => afterSecond[k] !== afterFirst[k])}`);
    // Curation: the records later sessions corrected must survive every run byte-for-byte.
    const curated = {
      'F47 flag title': JSON.parse(afterFirst['flags.json']).find((f) => f.id === 'F47').title,
      'F47 flag status': JSON.parse(afterFirst['flags.json']).find((f) => f.id === 'F47').status,
      'Q01 text': JSON.parse(afterFirst['questions.json']).find((q) => q.id === 'Q01').have,
      'Q11 text': JSON.parse(afterFirst['questions.json']).find((q) => q.id === 'Q11').have,
      'S10 options': JSON.stringify(JSON.parse(afterFirst['suggestions.json']).find((s) => s.id === 'S10').options),
      'S11 options': JSON.stringify(JSON.parse(afterFirst['suggestions.json']).find((s) => s.id === 'S11').options),
      'Wynn hotel note': JSON.parse(afterFirst['hotels.json']).find((h) => h.key === 'wynn').resort_fee_note,
    };
    const before = {
      'F47 flag title': JSON.parse(committed['flags.json']).find((f) => f.id === 'F47').title,
      'F47 flag status': JSON.parse(committed['flags.json']).find((f) => f.id === 'F47').status,
      'Q01 text': JSON.parse(committed['questions.json']).find((q) => q.id === 'Q01').have,
      'Q11 text': JSON.parse(committed['questions.json']).find((q) => q.id === 'Q11').have,
      'S10 options': JSON.stringify(JSON.parse(committed['suggestions.json']).find((s) => s.id === 'S10').options),
      'S11 options': JSON.stringify(JSON.parse(committed['suggestions.json']).find((s) => s.id === 'S11').options),
      'Wynn hotel note': JSON.parse(committed['hotels.json']).find((h) => h.key === 'wynn').resort_fee_note,
    };
    for (const [what, value] of Object.entries(curated)) {
      assert.equal(value, before[what], `the run reverted ${what}`);
    }
    // Only derived, evidence-backed fields may move: per-row dates and the run record.
    const changed = Object.keys(afterFirst).filter((k) => afterFirst[k] !== committed[k]);
    for (const name of changed) {
      if (name === 'all.json' || name === 'integration_report.json') continue;
      const beforeRows = JSON.parse(committed[name]);
      const afterRows = JSON.parse(afterFirst[name]);
      if (!Array.isArray(beforeRows)) continue;
      assert.equal(beforeRows.length, afterRows.length, `${name}: a run must not add or drop rows`);
      beforeRows.forEach((row, i) => {
        const now = afterRows[i];
        const strip = (o) => JSON.stringify(o, (key, value) =>
          (['retrieved', 'last_checked', 'sheet_retrieved', 'source_changed_at', 'read',
            'last_updated', 'address_read'].includes(key) ? undefined : value));
        assert.equal(strip(now), strip(row),
          `${name} row ${i}: only retrieval/last-checked stamps may move on a re-run`);
      });
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});
