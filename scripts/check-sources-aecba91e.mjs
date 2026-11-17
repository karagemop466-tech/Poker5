#!/usr/bin/env node
// Source monitor for the aecba91e dataset.
//  - fetches every URL in data/aecba91e/sources.json
//  - compares the body hash with the stored snapshot in data/aecba91e/snapshots.json
//  - appends one row per change to data/aecba91e/change-log.json (status: changed | unreachable | ok)
//  - never deletes a snapshot on failure: an unreachable page keeps the last known body
// A "changed" entry is what makes the build mark the affected rows, so a stale figure is visible
// rather than silently trusted. Network failures are recorded, never treated as "no change".
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';

const D = join(process.cwd(), 'data/aecba91e');
const read = (f, fb) => (existsSync(join(D, f)) ? JSON.parse(readFileSync(join(D, f), 'utf8')) : fb);
const ledger = read('sources.json', { urls: [] });
const snaps = read('snapshots.json', { urls: {} });
const log = read('change-log.json', []);
const TODAY = new Date().toISOString().slice(0, 10);
const UA = 'Poker5-source-monitor/1.0 (research dashboard; contact: repo maintainer)';
const TIMEOUT = 30_000;

const sha = (buf) => createHash('sha256').update(buf).digest('hex');
async function grab(url) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT);
  try {
    const res = await fetch(url, { signal: ctrl.signal, redirect: 'follow', headers: { 'user-agent': UA, accept: '*/*' } });
    const body = Buffer.from(await res.arrayBuffer());
    return { status: res.status, body, ok: res.ok };
  } finally { clearTimeout(t); }
}

let changed = 0, unreachable = 0, ok = 0;
for (const entry of ledger.urls) {
  const url = entry.url;
  let res = null, err = '';
  for (let attempt = 0; attempt < 3 && !(res && res.ok); attempt++) {
    try { res = await grab(url); if (!res.ok) err = `HTTP ${res.status}`; }
    catch (e) { err = e.name === 'AbortError' ? 'timeout' : String(e.message || e).slice(0, 120); res = null; }
    if (!(res && res.ok)) await new Promise((r) => setTimeout(r, 2000 * (attempt + 1)));
  }
  const prev = snaps.urls[url];
  if (!res || !res.ok) {
    unreachable++;
    log.push({ checked_at: new Date().toISOString(), url, status: 'unreachable', detail: err || 'fetch failed', retries: 3 });
    continue;
  }
  const h = sha(res.body);
  if (!prev) { snaps.urls[url] = { sha256: h, first_seen: TODAY, last_seen: TODAY, bytes: res.body.length, status: res.status }; ok++; continue; }
  if (prev.sha256 === h) { prev.last_seen = TODAY; prev.status = res.status; ok++; continue; }
  changed++;
  log.push({ checked_at: new Date().toISOString(), url, status: 'changed', detail: `body hash ${prev.sha256.slice(0, 12)} -> ${h.slice(0, 12)} (${res.body.length} bytes, was ${prev.bytes})` });
  snaps.urls[url] = { ...prev, sha256: h, last_seen: TODAY, bytes: res.body.length, status: res.status };
}

snaps.updated = TODAY;
log.push({ checked_at: new Date().toISOString(), url: '(run summary)', status: changed || unreachable ? 'attention' : 'clean', detail: `${ledger.urls.length} urls · ${changed} changed · ${unreachable} unreachable · ${ok} unchanged` });
writeFileSync(join(D, 'snapshots.json'), JSON.stringify(snaps, null, 1) + '\n');
writeFileSync(join(D, 'change-log.json'), JSON.stringify(log.slice(-500), null, 1) + '\n');
console.log(`monitor: ${ledger.urls.length} urls · ${changed} changed · ${unreachable} unreachable · ${ok} unchanged/baselined`);
if (unreachable > ledger.urls.length / 2) { console.error('more than half the sources were unreachable — not trusting this run'); process.exit(1); }
