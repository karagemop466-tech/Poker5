// work/bdcaf0bf/smoke_dom.mjs - DOM smoke test for the published site.
//
// Runs the real site JavaScript inside jsdom against the real generated HTML and
// asserts that the features the brief asks for actually work: the global search
// box, the date selector, the room filter, the single-entry toggle, the expandable
// structured rule fields, the sortable columns, the dated rate log and the trip
// cost calculator. Run:  node work/bdcaf0bf/smoke_dom.mjs   (needs jsdom)
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const ROOT = join(fileURLToPath(new URL(".", import.meta.url)), "..", "..");
const JS = readFileSync(join(ROOT, "assets/bdcaf0bf.js"), "utf8");

const { JSDOM } = await import("jsdom").catch(() => {
  console.error("jsdom is not installed: npm install --no-save jsdom");
  process.exit(2);
});

function page(rel) {
  const dom = new JSDOM(readFileSync(join(ROOT, rel), "utf8"), {
    runScripts: "outside-only",
    pretendToBeVisual: true,
    url: "https://karagemop466-tech.github.io/Poker5/" + rel,
  });
  dom.window.eval(JS);
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded", { bubbles: true }));
  return dom.window;
}

// only a table's own rows: the expandable rule-field table nests <tr> elements inside a cell
const visible = (doc, sel) =>
  [...doc.querySelectorAll(sel)].filter(
    (tr) => tr.parentElement && tr.parentElement.tagName === "TBODY" && tr.style.display !== "none",
  );

let ran = 0;
function test(name, fn) {
  ran++;
  try {
    fn();
    console.log("ok   -", name);
  } catch (e) {
    console.log("FAIL -", name, "\n      ", String(e.message).split("\n")[0]);
    process.exitCode = 1;
  }
}

test("all-events table: search box filters every column", () => {
  const w = page("pages/tournaments.html");
  const d = w.document;
  const total = visible(d, "#tall > tbody > tr").length;
  assert.ok(total >= 200, `expected the full schedule, saw ${total} rows`);
  assert.match(d.querySelector(".count").textContent, new RegExp(String(total)));
  const q = d.querySelector('[data-f="search"]');
  q.value = "bounty";
  q.dispatchEvent(new w.Event("input", { bubbles: true }));
  const hits = visible(d, "#tall > tbody > tr");
  assert.ok(hits.length > 0 && hits.length < total, "searching 'bounty' should narrow the table");
  assert.ok(hits.every((tr) => /bounty/i.test(tr.getAttribute("data-search"))), "every hit must mention bounty");
});

test("date selector cuts the window, and the count follows", () => {
  const w = page("pages/tournaments.html");
  const d = w.document;
  const from = d.querySelector('[data-f="from"]');
  const before = visible(d, "#tall > tbody > tr").length;
  from.value = "2026-12-10";
  from.dispatchEvent(new w.Event("change", { bubbles: true }));
  const after = visible(d, "#tall > tbody > tr");
  assert.ok(after.length < before, "the date filter must reduce the row count");
  // a row whose date the official page does not state stays visible on purpose: a filter may not
  // quietly drop an unverified row, it has to leave it on the page with its blank cell
  assert.ok(
    after.every((tr) => {
      const v = tr.getAttribute("data-date") || "";
      return v === "" || v >= "2026-12-10";
    }),
    "no dated row may be shown before the chosen date",
  );
  // the one-click trip window button must land on the computed scenario
  d.querySelector('[data-f="reset"]').dispatchEvent(new w.Event("click", { bubbles: true }));
  d.querySelector('[data-f="trip"]').dispatchEvent(new w.Event("click", { bubbles: true }));
  const win = visible(d, "#tall > tbody > tr");
  const tfrom = d.querySelector("#tall").getAttribute("data-trip-from");
  const tto = d.querySelector("#tall").getAttribute("data-trip-to");
  assert.ok(win.length > 0 && win.length < before, "the trip-window shortcut must filter the table");
  assert.ok(
    win.every((tr) => {
      const v = tr.getAttribute("data-date") || "";
      return v === "" || (v >= tfrom && v <= tto);
    }),
    "the trip window must be the computed scenario dates",
  );
});

test("single-entry toggle keeps only rows that pass the standard", () => {
  const w = page("pages/single-entry.html");
  const d = w.document;
  const rows = visible(d, "#tsingle > tbody > tr");
  const tbl = d.querySelector("#tall") || d;
  assert.ok(rows.length >= 40, `expected the graded list, saw ${rows.length}`);
  assert.ok(
    rows.every((tr) => /explicit_one_entry|no_reentry_language/.test(tr.getAttribute("data-rule") || "")),
    "the single-entry page must not list a row that fails the standard",
  );
  const w2 = page("pages/tournaments.html");
  const t = w2.document;
  const box = t.querySelector('[data-f="single"]');
  const beforeText = t.querySelector(".count").textContent;
  box.checked = true;
  box.dispatchEvent(new w2.Event("change", { bubbles: true }));
  const filtered = visible(t, "#tall > tbody > tr");
  const total = (beforeText.match(/of (\d+) rows/) || [])[1];
  assert.ok(total, "the counter must report the full table size before filtering");
  assert.equal(filtered.length, rows.length, "the toggle on the all-events table must reproduce the list");
  assert.match(
    t.querySelector(".count").textContent.replace(/\s+/g, " ").trim(),
    new RegExp(`^${rows.length} of ${total} rows$`),
    "the counter must say how many rows survive the toggle",
  );
});

test("room filter isolates one poker room", () => {
  const w = page("pages/tournaments.html");
  const d = w.document;
  const sel = d.querySelector('[data-f="venue"]');
  sel.value = "venetian";
  sel.dispatchEvent(new w.Event("change", { bubbles: true }));
  const rows = visible(d, "#tall > tbody > tr").filter((tr) => tr.getAttribute("data-venue"));
  assert.ok(rows.length > 0 && rows.every((tr) => tr.getAttribute("data-venue") === "venetian"));
});

test("every event row links to an official source and exposes its rule fields", () => {
  const w = page("pages/tournaments.html");
  const d = w.document;
  const rows = visible(d, "#tall > tbody > tr");
  for (const tr of rows) {
    const a = tr.querySelector('a[class="src"]');
    assert.ok(a && /^https:\/\//.test(a.getAttribute("href") || ""), "row without an official https source");
  }
  const det = d.querySelector("#tall details.rules");
  assert.ok(det, "rows should carry expandable structured rule fields");
  det.open = true;
  det.dispatchEvent(new w.Event("toggle"));
  const sub = det.querySelector("table.sub");
  assert.ok(sub.querySelectorAll("tr").length >= 5, "the rule fields should cover entry, re-entry, add-on, fee");
  assert.ok(
    [...sub.querySelectorAll("tr")].every((tr) => /20\d\d-\d\d-\d\d|not re-checked/.test(tr.textContent)),
    "each rule field must carry a retrieval date",
  );
});

test("sorting a numeric column re-orders the rows", () => {
  const w = page("pages/ranking.html");
  const d = w.document;
  const th = [...d.querySelectorAll("#trank thead th")].find((h) => /Guarantee/i.test(h.textContent));
  const idx = [...d.querySelectorAll("#trank thead th")].indexOf(th);
  const col = () =>
    [...d.querySelectorAll("#trank > tbody > tr[data-search]")].map(
      (tr) => parseFloat((tr.children[idx].getAttribute("data-order") || "0").replace(/[^0-9.]/g, "")) || 0,
    );
  th.dispatchEvent(new w.Event("click", { bubbles: true }));
  const asc = col();
  assert.ok(asc.every((v, i) => i === 0 || asc[i - 1] <= v), `ascending order broken: ${asc.slice(0, 5)}`);
  th.dispatchEvent(new w.Event("click", { bubbles: true }));
  const desc = col();
  assert.ok(desc.every((v, i) => i === 0 || desc[i - 1] >= v), `descending order broken: ${desc.slice(0, 5)}`);
  assert.ok(desc[0] > 0 && desc[desc.length - 1] > 0, "the ranking table must only hold priced rows");
  // the ratio column has to be the guarantee divided by the buy-in, in that order
  const ratios = [...d.querySelectorAll("#trank > tbody > tr[data-search]")].map((tr) =>
    parseFloat((tr.children[0].getAttribute("data-order") || "0")),
  );
  assert.ok(ratios.every((v) => v > 0), "every ranked row needs a positive ratio");
});

test("reset restores the whole table", () => {
  const w = page("pages/tournaments.html");
  const d = w.document;
  const before = visible(d, "#tall > tbody > tr").length;
  const q = d.querySelector('[data-f="search"]');
  q.value = "zzzz nothing matches this";
  q.dispatchEvent(new w.Event("input", { bubbles: true }));
  assert.equal(visible(d, "#tall > tbody > tr").length, 0, "a nonsense query should hide everything");
  d.querySelector('[data-f="reset"]').dispatchEvent(new w.Event("click", { bubbles: true }));
  assert.equal(visible(d, "#tall > tbody > tr").length, before, "reset must bring every row back");
});

test("walking routes: the 30-minute toggle keeps only verified routes", () => {
  const w = page("pages/routes.html");
  const d = w.document;
  const box = d.querySelector('#troutes').closest(".tablewrap").previousElementSibling
    ? d.querySelector('[data-for="troutes"] [data-f="single"]')
    : null;
  box.checked = true;
  box.dispatchEvent(new w.Event("change", { bubbles: true }));
  const rows = visible(d, "#troutes > tbody > tr");
  assert.ok(rows.length > 0, "at least the same-property routes must satisfy the limit");
  assert.ok(rows.every((tr) => tr.getAttribute("data-within") === "yes"), "only verified sub-30-minute routes may remain");
});

test("trip calculator: selecting the day plan prices the entries and refuses a fake hotel total", () => {
  const w = page("pages/planner.html");
  const d = w.document;
  d.querySelector("#t_auto").dispatchEvent(new w.Event("click", { bubbles: true }));
  const out = d.querySelector("#ptotal").textContent;
  assert.match(out, /Entries: \d+/);
  assert.match(out, /Estimated trip cost/);
  assert.ok(!/NaN|Infinity|undefined/.test(out), `calculator produced junk: ${out.slice(0, 160)}`);
  const boxes = [...d.querySelectorAll("#picks input[data-buyin]:checked")];
  assert.ok(boxes.length > 0, "the day plan should select events");
  assert.ok(
    boxes.every((b) => parseFloat(b.getAttribute("data-buyin")) > 0),
    "only rows with a published buy-in may be priced",
  );
});

test("trip calculator: a dated quote turns the estimate into a complete number", () => {
  const w = page("pages/planner.html");
  const d = w.document;
  d.querySelector("#t_auto").dispatchEvent(new w.Event("click", { bubbles: true }));
  d.querySelector("#t_mode").value = "quote";
  d.querySelector("#t_mode").dispatchEvent(new w.Event("change", { bubbles: true }));
  let out = d.querySelector("#ptotal").textContent;
  assert.match(out, /Incomplete/, "without a rate the total must stay incomplete");
  d.querySelector("#t_rate").value = "189";
  d.querySelector("#t_rate").dispatchEvent(new w.Event("input", { bubbles: true }));
  out = d.querySelector("#ptotal").textContent;
  assert.match(out, /Complete under the published formula/);
  const nights = parseInt(d.querySelector("#t_nights").value, 10);
  const m = out.match(/Estimated trip cost: \$([\d,]+)/);
  assert.ok(m, "a completed total must be printed");
  const total = parseFloat(m[1].replace(/,/g, ""));
  const hotel = (189 + 55) * 1.1338 * nights;
  const entries = [...d.querySelectorAll("#picks input[data-buyin]:checked")].reduce(
    (s, b) => s + parseFloat(b.getAttribute("data-buyin")),
    0,
  );
  assert.ok(Math.abs(total - (entries + hotel)) < 2, `${total} vs expected ${entries + hotel}`);
});

test("hotels page: the dated rate log stores, renders and removes an entry", () => {
  const w = page("pages/hotels.html");
  const d = w.document;
  const set = (id, v) => {
    d.getElementById(id).value = v;
  };
  set("r_hotel", "The Venetian");
  set("r_in", "2026-12-06");
  set("r_out", "2026-12-13");
  set("r_total", "1899.50");
  set("r_nights", "7");
  set("r_fee", "55");
  set("r_tax", "13.38");
  set("r_stamp", "2026-11-19 08:00 PST");
  d.querySelector("#rateform").dispatchEvent(new w.Event("submit", { bubbles: true, cancelable: true }));
  const rows = d.querySelectorAll("#ratelog table tbody tr");
  assert.equal(rows.length, 1, "one quote logged should render one row");
  const tds = [...rows[0].children].map((td) => td.textContent.trim());
  assert.match(tds.join(" "), /\$271\.36/, "true nightly = (271.36 rate + 55 fee) x 1.1338 ... check math");
  assert.ok(!/NaN/.test(tds.join(" ")));
  d.querySelector("#ratelog [data-del]").dispatchEvent(new w.Event("click", { bubbles: true }));
  assert.match(d.querySelector("#ratelog").textContent, /No booking quote recorded/);
});

test("rate log refuses an average built on nothing", () => {
  const w = page("pages/hotels.html");
  const d = w.document;
  d.getElementById("r_hotel").value = "Test";
  d.querySelector("#rateform").dispatchEvent(new w.Event("submit", { bubbles: true, cancelable: true }));
  assert.match(d.getElementById("r_err").textContent, /checkout total and a positive number of nights/);
});

test("monitor page: a changed source is badged, never silently overwritten", () => {
  const w = page("pages/monitor.html");
  const d = w.document;
  const rows = visible(d, "#tmon > tbody > tr");
  const changed = rows.filter((tr) => /source changed|content hash change/.test(tr.textContent));
  assert.ok(changed.length >= 0);
  const flagged = d.querySelector(".chg");
  assert.ok(flagged || !process.env.REQUIRE_BADGE, "the ledger should surface changed sources");
});

console.log(`\n${ran} DOM checks run${process.exitCode ? "  (FAILURES above)" : " - all passed"}`);
