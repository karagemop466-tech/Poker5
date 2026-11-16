import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, '..');
const siteRoot = path.join(repoRoot, 'planner-aa83f1e1');
const output = path.join(repoRoot, '_site-aa83f1e1');
const fail = (message) => { throw new Error(message); };
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(siteRoot, relative), 'utf8'));
const near = (a, b, tolerance = 0.011) => Math.abs(a - b) <= tolerance;

function validateTournamentData(data) {
  const eventIds = new Set();
  const sourceIds = new Set(data.sources.map((source) => source.id));
  const venueIds = new Set(data.venues.map((venue) => venue.id));
  const count = { 'single-entry': 0, 'multiple-entry': 0, unconfirmed: 0, conflicting: 0 };
  if (data.meta.window.isUserSelected !== false) fail('The researched date window must remain labeled as not user-selected.');
  if (!data.meta.window.start || !data.meta.window.end) fail('Tournament window start/end are required.');
  if (!data.meta.strictSingleEntryDefinition) fail('Strict single-entry definition is missing.');

  for (const source of data.sources) {
    if (!source.id || !source.title || !source.checkedAt) fail(`Tournament source is missing an id/title/check date: ${JSON.stringify(source)}`);
    if (!/^https:\/\//.test(source.url)) fail(`Tournament source must use HTTPS: ${source.id}`);
  }
  for (const event of data.events) {
    if (eventIds.has(event.id)) fail(`Duplicate tournament event id: ${event.id}`);
    eventIds.add(event.id);
    if (!venueIds.has(event.venueId)) fail(`Unknown venue ${event.venueId} on ${event.id}`);
    if (!(event.entryStatus in count)) fail(`Invalid entryStatus on ${event.id}: ${event.entryStatus}`);
    count[event.entryStatus] += 1;
    if (!event.date || !event.title || !event.entryRule || !Array.isArray(event.sourceIds) || event.sourceIds.length === 0) {
      fail(`Event requires date/title/entry rule/source ids: ${event.id}`);
    }
    for (const id of event.sourceIds) if (!sourceIds.has(id)) fail(`Missing tournament source ${id} referenced by ${event.id}`);
    if (event.entryStatus === 'single-entry' && !/single|one\s+(total\s+)?entry|no\s+re-?entry/i.test(event.entryRule)) {
      fail(`Strict single-entry event needs an explicit rule: ${event.id}`);
    }
  }
  for (const event of data.outsideWindow || []) {
    for (const id of event.sourceIds || []) if (!sourceIds.has(id)) fail(`Missing source ${id} referenced by outside-window event ${event.title}`);
  }
  const summary = data.meta.summary;
  if (summary.confirmedStrictSingleEntryCount !== count['single-entry'] || summary.unconfirmedCount !== count.unconfirmed || summary.confirmedMultipleEntryCount !== count['multiple-entry'] || summary.conflictingOfficialListingsCount !== count.conflicting) {
    fail(`Tournament summary does not match records: ${JSON.stringify({ summary, count })}`);
  }
  if (data.meta.trackedListingCount !== data.events.length) fail('Tournament trackedListingCount does not match events length.');
}

function validateHotelData(data) {
  const sourceIds = new Set(data.sources.map((source) => source.id));
  if (data.meta.window.isUserSelected !== false) fail('Hotel dates must remain labeled as not user-selected.');
  for (const source of data.sources) {
    if (!source.id || !source.title || !source.checkedAt) fail(`Hotel source is missing an id/title/check date: ${JSON.stringify(source)}`);
    if (!/^https:\/\//.test(source.url)) fail(`Hotel source must use HTTPS: ${source.id}`);
  }
  for (const quote of data.quotes) {
    if (!quote.hotel || !quote.sourceIds?.length) fail(`Hotel quote lacks hotel/source ids: ${quote.hotel || 'unnamed'}`);
    for (const id of quote.sourceIds) if (!sourceIds.has(id)) fail(`Missing hotel source ${id} for ${quote.hotel}`);
    if (quote.quoteStatus === 'direct_quote_includes_fees_and_tax') {
      const sum = quote.roomSubtotalUsd + quote.resortFeeUsd + quote.taxUsd;
      if (!near(sum, quote.quotedTotalUsd)) fail(`${quote.hotel} quoted total does not equal the displayed components.`);
      if (!near(quote.quotedAllInPerNightUsd, quote.quotedTotalUsd / quote.nights)) fail(`${quote.hotel} all-in nightly quote calculation is inconsistent.`);
    }
    if (quote.quoteStatus === 'direct_nightly_rate_tax_excluded_total_not_returned') {
      if (quote.hotelQuotedTaxInclusiveTotalUsd !== null) fail(`${quote.hotel} tax-inclusive hotel total should remain null until directly quoted.`);
      if (!near(quote.preTaxStayCalculationUsd, quote.displayedAverageNightUsd * quote.nights)) fail(`${quote.hotel} pre-tax calculation is inconsistent.`);
      if (!near(quote.estimatedTaxUsd, quote.preTaxStayCalculationUsd * quote.taxRateUsedForEstimate)) fail(`${quote.hotel} estimated tax calculation is inconsistent.`);
      if (!near(quote.estimatedAllInStayUsd, quote.preTaxStayCalculationUsd + quote.estimatedTaxUsd)) fail(`${quote.hotel} estimated total is inconsistent.`);
    }
  }
  for (const fee of data.otherResortFees || []) for (const id of fee.sourceIds || []) if (!sourceIds.has(id)) fail(`Missing hotel source ${id} for fee record ${fee.hotel}`);
  if (!data.walking.every((item) => item.verification === 'third_party_estimate_only' && item.sourceId && sourceIds.has(item.sourceId))) fail('Walking evidence must remain identified as a third-party estimate with a source.');
}

function validateRepositoryLinks() {
  const htmlFiles = ['index.html', ...fs.readdirSync(path.join(siteRoot, 'pages')).filter((name) => name.endsWith('.html')).map((name) => `pages/${name}`)];
  const linkPattern = /\b(?:href|src)="([^"]+)"/g;
  for (const relativeFile of htmlFiles) {
    const html = fs.readFileSync(path.join(siteRoot, relativeFile), 'utf8');
    if (/\bid="[^"]+"[^>]*\bid="/.test(html)) fail(`Duplicate id attribute found in ${relativeFile}.`);
    for (const match of html.matchAll(linkPattern)) {
      const value = match[1];
      if (/^(?:https?:|mailto:|tel:|#|data:|javascript:)/i.test(value)) continue;
      const localPart = decodeURIComponent(value.split(/[?#]/, 1)[0]);
      const target = path.resolve(path.dirname(path.join(siteRoot, relativeFile)), localPart);
      if (!target.startsWith(`${siteRoot}${path.sep}`) && target !== siteRoot) fail(`Local link escapes the planner subsite in ${relativeFile}: ${value}`);
      if (!fs.existsSync(target)) fail(`Broken local link in ${relativeFile}: ${value}`);
    }
  }
  for (const page of Object.keys({
    dashboard: 1, tournaments: 1, hotels: 1, analysis: 1, qa: 1, suggestions: 1, review: 1, publication: 1
  })) {
    const target = page === 'dashboard' ? 'index.html' : `pages/${page === 'qa' ? 'qa' : page}.html`;
    if (!fs.existsSync(path.join(siteRoot, target))) fail(`Missing navigation target: ${target}`);
  }
}

function copyBundle() {
  fs.rmSync(output, { recursive: true, force: true });
  fs.mkdirSync(output, { recursive: true });
  for (const entry of ['index.html', 'pages', 'assets', 'data', 'research']) {
    const source = path.join(siteRoot, entry);
    if (!fs.existsSync(source)) fail(`Cannot build: missing ${entry}`);
    fs.cpSync(source, path.join(output, entry), { recursive: true });
  }
  fs.writeFileSync(path.join(output, '404.html'), `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found · Felt &amp; Stay</title><link rel="stylesheet" href="./assets/site.css"><body><main class="container page-wrap"><div class="page-head"><div class="eyebrow">404 · not in this hand</div><h1>That page isn't here.</h1><p class="lede">Return to the planner dashboard to continue.</p><a class="btn btn-green" href="./index.html">Back to dashboard</a></div></main></body></html>\n`);
}

try {
  const tournaments = readJson('data/tournaments.json');
  const hotels = readJson('data/hotels.json');
  validateTournamentData(tournaments);
  validateHotelData(hotels);
  validateRepositoryLinks();
  copyBundle();
  console.log(`Build checks passed. ${tournaments.events.length} tournament records, ${hotels.quotes.length} hotel quotes, and ${fs.readdirSync(path.join(siteRoot, 'pages')).length} pages copied to _site-aa83f1e1/.`);
} catch (error) {
  console.error(`Build failed: ${error.message}`);
  process.exitCode = 1;
}
