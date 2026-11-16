import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const siteRoot = path.join(repoRoot, 'planner-aa83f1e1');
const app = fs.readFileSync(path.join(siteRoot, 'assets/app.js'), 'utf8');
const pages = [
  ['dashboard', 'Plan the stay around the cards'],
  ['tournaments', 'The tournament slate'],
  ['hotels', 'Stay near the action'],
  ['analysis', 'The signal is clear'],
  ['qa', 'Straight answers'],
  ['suggestions', 'A plan that waits'],
  ['review', 'Open questions stay open'],
  ['publication', 'Publish only what the sources support']
];

async function render(page) {
  const elements = new Map();
  const element = (id) => {
    if (!elements.has(id)) {
      const defaultValue = ['venue-filter', 'status-filter'].includes(id) ? 'all' : '';
      elements.set(id, {
        id,
        value: defaultValue,
        innerHTML: '',
        textContent: '',
        addEventListener() {}
      });
    }
    return elements.get(id);
  };
  const document = {
    body: { dataset: { page, root: page === 'dashboard' ? '.' : '..' } },
    title: '',
    getElementById: element
  };
  const fetch = async (url) => {
    const value = String(url);
    const filename = value.endsWith('data/tournaments.json') ? 'tournaments.json' : 'hotels.json';
    const content = fs.readFileSync(path.join(siteRoot, 'data', filename), 'utf8');
    return { ok: true, async json() { return JSON.parse(content); } };
  };
  const context = vm.createContext({
    document, fetch, Intl, Date, Math, Object, String, Number, Array, Promise,
    Error, setTimeout, clearTimeout, console
  });
  vm.runInContext(app, context, { filename: 'assets/app.js' });
  for (let attempt = 0; attempt < 20 && !element('page-content').innerHTML; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 0));
  }
  return { html: element('page-content').innerHTML, title: document.title };
}

for (const [page, expected] of pages) {
  const result = await render(page);
  assert.ok(result.html.includes(expected), `${page} did not render its expected heading. Got: ${result.html.slice(0, 300)}`);
  assert.ok(result.title.includes('Felt & Stay'), `${page} did not set a page title.`);
  console.log(`Smoke render passed: ${page}`);
}
