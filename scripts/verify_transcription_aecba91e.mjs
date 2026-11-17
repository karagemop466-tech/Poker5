#!/usr/bin/env node
// Row-by-row diff between the transcription used to build the site (venetian_dse_iv.psv) and the
// independent re-read of the official schedule page (official_recheck_2026-11-17.psv).
// Both files were written from the same official page at different times by the same session; a
// mismatch means one of the two transcriptions is wrong, so the build must not be trusted.
// Usage: node scripts/verify_transcription_aecba91e.mjs
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const D = join(process.cwd(), 'data/aecba91e');
const load = (f) => readFileSync(join(D, f), 'utf8').split('\n').map((l) => l.trim())
  .filter((l) => l && !l.startsWith('#')).map((l) => l.split('|'));

const psv = load('venetian_dse_iv.psv');      // date|start|ev|buyin|gtd|sheet|kind|flags|label
const chk = load('official_recheck_2026-11-17.psv'); // date|start|ev|sheet|kind|gtd
const KIND = { entry: 'e', restart: 'd2', ft: 'ft' };
const key = (r) => `${r[0]}|${r[1]}|${r[2]}`;
const bad = [];

if (psv.length !== chk.length) bad.push(`row count differs: transcription ${psv.length} vs recheck ${chk.length}`);
const byKey = new Map(chk.map((r) => [key(r), r]));
for (const r of psv) {
  const [date, start, ev, buyin, gtd, sheet, kind] = r;
  const c = byKey.get(`${date}|${start}|${ev}`);
  if (!c) { bad.push(`transcription row ${date} ${start} #${ev} is not on the official page as re-read`); continue; }
  if (String(sheet) !== c[3]) bad.push(`${date} #${ev}: structure sheet ${sheet} vs recheck ${c[3]}`);
  if (KIND[kind] !== c[4]) bad.push(`${date} #${ev}: kind ${kind}(${KIND[kind]}) vs recheck ${c[4]}`);
  if (c[4] === 'e' && (gtd || '') !== (c[5] || '')) bad.push(`${date} #${ev}: guarantee ${gtd || 'blank'} vs recheck ${c[5] || 'blank'}`);
  if (c[4] === 'e' && !(Number(buyin) > 0)) bad.push(`${date} #${ev}: entry row without a buy-in`);
}
for (const c of chk) if (!psv.some((r) => key(r) === key(c))) bad.push(`official row ${c[0]} ${c[1]} #${c[2]} is missing from the transcription`);

const events = new Set(psv.map((r) => Number(r[2])));
const missing = [...Array(64).keys()].map((i) => i + 1).filter((n) => !events.has(n));
if (missing.length) bad.push(`event numbers absent from the transcription: ${missing.join(', ')}`);

console.log(`compared ${psv.length} transcribed rows against ${chk.length} re-read rows · ${events.size} distinct event numbers (#1-#64${missing.length ? `, missing ${missing.join(',')}` : ', complete'})`);
if (bad.length) { console.error(`MISMATCH (${bad.length})`); bad.forEach((b) => console.error(' -', b)); process.exit(1); }
console.log('OK: the two independent readings of the official page agree row for row.');
