// Validates data-359e3f96/*.json (cross-check data for the Strip poker project). Run: node scripts/check.mjs
// Exits non-zero on any failure, so a broken build cannot be merged.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
const fail = (m) => errors.push(m);

const files = ["tournaments.json", "hotels.json", "venues.json", "questions.json", "suggestions.json", "flags.json", "repo-review.json"];
const data = {};
for (const f of files) {
  try {
    data[f] = JSON.parse(readFileSync(join(root, "data-359e3f96", f), "utf8"));
  } catch (e) {
    fail(`data/${f}: ${e.message}`);
  }
}

// Every tournament row needs a source with an https URL.
const tRows = [...(data["tournaments.json"]?.single_entry || []), ...(data["tournaments.json"]?.separate_section || [])];
for (const r of tRows) {
  if (!r.sources?.length) fail(`tournament ${r.id}: no source`);
  for (const s of r.sources || []) if (!/^https:\/\//.test(s.url)) fail(`tournament ${r.id}: bad url ${s.url}`);
  if (!r.entry_rule) fail(`tournament ${r.id}: missing entry_rule`);
}
// Single-entry rows must have an integer buy-in and a source.
for (const r of data["tournaments.json"]?.single_entry || []) {
  if (!Number.isInteger(r.buy_in_num)) fail(`single-entry ${r.id}: buy_in_num not an integer`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(r.date)) fail(`single-entry ${r.id}: date not ISO`);
}
// Hotels/venues: every row must carry at least one source.
for (const h of data["hotels.json"]?.hotels || []) if (!h.sources?.length) fail(`hotel ${h.hotel}: no source`);
for (const v of data["venues.json"]?.venues || []) if (!v.sources?.length) fail(`venue ${v.venue}: no source`);
// Flags: any flag with no source must say so.
for (const f of data["flags.json"]?.flags || []) if (!f.sources?.length && !/no official|not verified|not present/i.test(f.detail)) fail(`flag ${f.id}: no source and no unverified note`);

if (errors.length) {
  console.error(`check failed (${errors.length}):\n- ` + errors.join("\n- "));
  process.exit(1);
}
console.log(`check passed: ${tRows.length} tournament rows, ${files.length} data files`);
