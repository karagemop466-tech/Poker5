// Static site generator for GitHub Pages (no dependencies).
// Reads /data/*.json and writes /docs/*.html. Run: node scripts/build.mjs
import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = join(root, "data");
const outDir = join(root, "docs");
const load = (f) => JSON.parse(readFileSync(join(dataDir, f), "utf8"));

const T = load("tournaments.json");
const H = load("hotels.json");
const V = load("venues.json");
const Q = load("questions.json");
const S = load("suggestions.json");
const F = load("flags.json");
const R = load("repo-review.json");

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const BLANK = `<span class="blank">Unverified: left blank</span>`;
const cell = (v) => (v === "" || v === null || v === undefined ? BLANK : esc(v));
const srcs = (arr) =>
  arr && arr.length
    ? arr.map((s) => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>`).join("<br>")
    : `<span class="blank">No source</span>`;
const money = (n) => (n === null || n === undefined ? "" : "$" + Number(n).toLocaleString("en-US"));
const dayName = (iso) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return "";
  return new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric", timeZone: "UTC" });
};

const NAV = [
  ["index.html", "Home"],
  ["single-entry.html", "Single-entry"],
  ["separate-section.html", "Separate section"],
  ["schedule.html", "Schedule"],
  ["hotels.html", "Hotels"],
  ["venues.html", "Venues"],
  ["analysis.html", "Analysis"],
  ["questions.html", "Questions"],
  ["suggestions.html", "Suggestions"],
  ["flagged.html", "Flagged for Review"],
  ["repo-review.html", "Repo review"],
];

function layout(file, title, body) {
  const nav = NAV.map(([href, label]) => `<a href="${href}"${href === file ? ' class="active"' : ""}>${esc(label)}</a>`).join("");
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | Las Vegas Strip Poker Planner</title>
<style>
:root{--ink:#1d2430;--muted:#5b6575;--line:#dfe4ec;--bg:#f7f9fc;--accent:#1f5fbf;--warn:#b25000;--ok:#1b7f4b}
*{box-sizing:border-box}
body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
header{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2}
header .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:8px 18px;padding:12px 0}
header h1{font-size:17px;margin:0 12px 0 0}
nav a{color:var(--muted);text-decoration:none;padding:4px 8px;border-radius:6px;font-size:14px}
nav a:hover,nav a.active{background:#e8f0fc;color:var(--accent)}
main{max-width:1200px;margin:0 auto;padding:24px 20px 60px}
h2{font-size:22px;margin:28px 0 10px}
h3{font-size:17px;margin:20px 0 8px}
p,li{max-width:900px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;color:inherit}
.card b{display:block;font-size:24px;color:var(--accent)}
.card span{color:var(--muted);font-size:13px}
.note{background:#fff8ec;border:1px solid #f1d7a8;border-radius:8px;padding:10px 14px;margin:12px 0;max-width:1000px}
.note.ok{background:#eef9f2;border-color:#bfe5cd}
.table-wrap{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f1f5fb;font-weight:600;position:sticky;top:0}
tr:last-child td{border-bottom:none}
td a{color:var(--accent)}
.blank{color:var(--warn);font-style:italic}
.tag{display:inline-block;font-size:12px;padding:1px 7px;border-radius:999px;background:#eef2f7;color:var(--muted)}
.tag.ok{background:#e4f5ec;color:var(--ok)}
.tag.warn{background:#fff0e0;color:var(--warn)}
.small{font-size:13px;color:var(--muted)}
footer{max-width:1200px;margin:0 auto;padding:0 20px 30px;color:var(--muted);font-size:13px}
</style>
</head>
<body>
<header><div class="wrap" style="max-width:1200px;margin:0 auto;padding:12px 20px;display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center">
<h1>Las Vegas Strip Poker Planner</h1><nav>${nav}</nav></div></header>
<main>
${body}
</main>
<footer>Data verified against official operator pages and PDFs on ${esc(T.last_verified)}. Blank fields are values that could not be confirmed from an official source. This is planning information, not a booking or travel guarantee. Confirm times, buy-ins and rates with each room before you go.</footer>
</body>
</html>
`;
}

// ---- Analysis numbers (computed from official figures in tournaments.json) ----
const single = T.single_entry.map((r) => ({
  ...r,
  ratio: r.guarantee_num && r.buy_in_num ? r.guarantee_num / r.buy_in_num : null,
  share: r.pool_num && r.buy_in_num ? r.pool_num / r.buy_in_num : null,
}));
const byGTD = [...single].sort((a, b) => (b.guarantee_num || 0) - (a.guarantee_num || 0) || a.buy_in_num - b.buy_in_num);
const earliest = [...single].sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time))[0];
const sepCount = T.separate_section.length;
const unverCount = T.unverified.length;
const hotelVerified = H.hotels.filter((h) => h.resort_fee_status.startsWith("Verified")).length;
const closedVenues = V.venues.filter((v) => /closed/i.test(v.status)).length;
const earliestRaceDay = [...single].filter((r) => r.time === "10:10 AM").map((r) => r.date);

// ---- Pages ----
const pages = {};

pages["index.html"] = layout("index.html", "Home", `
<h2>Executive summary</h2>
<div class="note ok"><b>Bottom line.</b> Only the Venetian (Palazzo) runs single-entry events that can be verified from official documents in this window. ${single.length} single-entry events are listed (Nov 18 to Dec 7, 2026). Caesars Palace, Wynn and Bellagio events all allow re-entry, rebuy or an add-on, so they are in the separate section. ARIA and Horseshoe publish no schedule, and Planet Hollywood and Resorts World are reported closed.</div>
<div class="cards">
  <a class="card" href="single-entry.html"><b>${single.length}</b><span>Single-entry events (official)</span></a>
  <a class="card" href="separate-section.html"><b>${sepCount}</b><span>Re-entry, rebuy, add-on or multi-flight rows (separate)</span></a>
  <a class="card" href="flagged.html"><b>${unverCount}</b><span>Unverified events not classified</span></a>
  <a class="card" href="hotels.html"><b>${hotelVerified} of ${H.hotels.length}</b><span>Hotels with an official resort fee on file</span></a>
  <a class="card" href="venues.html"><b>${closedVenues}</b><span>Strip rooms reported closed (excluded)</span></a>
</div>
<h3>Key findings</h3>
<ul>
<li><b>Best single-entry value.</b> The $600 events on Dec 6 (Event 28) and Dec 7 (Event 30) carry $40,000 guarantees. Event 14 (Nov 27) carries $30,000. Prize pool share of buy-in is 85% for the $600 events (official structure sheet: $510 of $600).</li>
<li><b>An all-day plan from 8 AM is not possible with single-entry events alone.</b> The earliest verified single-entry start is 10:10 AM (RaceDay stack, Nov 19 to 21). Single-entry starts are at 10:10 AM (RaceDay), 11:10 AM and 5:10 PM. Most days have one or two events.</li>
<li><b>Re-entry is common on the Strip.</b> Caesars Palace (all four dailies), Wynn (all dailies), and Bellagio (all three weeklies) allow re-entry, rebuy or add-ons. They are kept in the separate section so you can decide.</li>
<li><b>Poker-suite rate at the Venetian.</b> The official rate starts at "as low as $119 (Venetian) and $209 (Palazzo)", but it requires a $300+ tournament buy-in or 6 hours of live cash play each night. Single-entry events at $300 or more are listed on the Schedule page.</li>
<li><b>Hotel costs are only partly verifiable.</b> The Venetian/Palazzo and Wynn resort fee is $55 plus tax per night on official terms. Nightly rates and walking times are blank because they could not be confirmed from official sources.</li>
<li><b>Planet Hollywood and Resorts World</b> are reported closed (trade press and PokerAtlas). Official confirmation was not found, so both are excluded and flagged.</li>
</ul>
<h3>How to use this site</h3>
<ul>
<li>Start with <a href="single-entry.html">Single-entry</a> for the clean entry list.</li>
<li>Use <a href="separate-section.html">Separate section</a> if you are willing to pay for re-entry or add-ons.</li>
<li>Use <a href="schedule.html">Schedule</a> to plan a day.</li>
<li>Review <a href="questions.html">Questions</a> and <a href="suggestions.html">Suggestions</a> before any decision. Review <a href="flagged.html">Flagged for Review</a> for anything unverified.</li>
</ul>
<p class="small">Every row in the main tables links to an official source. Values that could not be confirmed are left blank and flagged. Last verified ${esc(T.last_verified)}.</p>
`);

pages["single-entry.html"] = layout("single-entry.html", "Single-entry", `
<h2>Single-entry tournaments (Las Vegas Strip)</h2>
<p>Each row is a Venetian event from the official schedule. Single-entry status is <b>inferred</b> from the structure sheet listing no re-entry, rebuy or add-on terms (see <a href="flagged.html">Flagged F06</a>). Events are sorted by date. Prize-pool share and guarantee-to-buy-in ratio are computed from official figures.</p>
<div class="note">Venetian Palazzo, Level 2 (Grand Canal Shoppes). Times are Pacific. Schedules change. Confirm each event with the room before you go.</div>
<div class="table-wrap"><table>
<tr><th>Date</th><th>Time</th><th>Venue</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Starting chips</th><th>Registration closes</th><th>Prize pool (official)</th><th>Guarantee ÷ buy-in</th><th>Entry rule</th><th>Sources</th></tr>
${single.map((r) => `<tr>
<td>${esc(dayName(r.date))}<br><span class="small">${esc(r.date)}</span></td>
<td>${esc(r.time)}</td>
<td>${esc(r.venue)}</td>
<td>${esc(r.event)}<br><span class="small">Event ${esc(r.event_no)}</span></td>
<td>${esc(r.buy_in)}</td>
<td>${cell(r.guarantee)}</td>
<td>${cell(r.chips)}</td>
<td>${cell(r.reg_closes)}</td>
<td>${cell(r.prize_pool)}</td>
<td>${r.ratio ? r.ratio.toFixed(1) + "×" : BLANK}</td>
<td>${esc(r.entry_rule)}</td>
<td>${srcs(r.sources)}</td>
</tr>`).join("\n")}
</table></div>
`);

pages["separate-section.html"] = layout("separate-section.html", "Separate section", `
<h2>Separate section: re-entry, rebuy, add-on and multi-flight</h2>
<div class="note"><b>Not single-entry.</b> Each row below lets you pay more to enter again, buy chips, or enter a flight. You asked for these to be kept apart. Compare them only if you accept the extra spend.</div>
<h3>Re-entry, rebuy and add-on events</h3>
<div class="table-wrap"><table>
<tr><th>Venue</th><th>Days / date</th><th>Time</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Prize pool (official)</th><th>Entry rule (why excluded)</th><th>Category</th><th>Sources</th></tr>
${T.separate_section.map((r) => `<tr>
<td>${esc(r.venue)}</td>
<td>${esc(r.date)}</td>
<td>${esc(r.time)}</td>
<td>${esc(r.event)}</td>
<td>${cell(r.buy_in)}</td>
<td>${cell(r.guarantee)}</td>
<td>${cell(r.prize_pool)}</td>
<td>${esc(r.entry_rule)}</td>
<td><span class="tag warn">${esc(r.category)}</span></td>
<td>${srcs(r.sources)}</td>
</tr>`).join("\n")}
</table></div>
<h3>Not yet classified (structure sheet not checked)</h3>
<p>These events appear on official schedules but their structure sheets were not opened, so their entry rule is unknown. They are not single-entry until checked.</p>
<div class="table-wrap"><table>
<tr><th>Venue</th><th>Date</th><th>Time</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Why unclassified</th><th>Source</th></tr>
${T.unverified.map((r) => { const src = /Venetian/.test(r.venue) ? [{label:"Venetian DeepStack schedule (official PDF)",url:"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"}] : [{label:"WPT World Championship schedule (official PDF)",url:"https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"}]; return `<tr><td>${esc(r.venue)}</td><td>${esc(r.date)}</td><td>${esc(r.time)}</td><td>${esc(r.event)}</td><td>${cell(r.buy_in)}</td><td>${cell(r.guarantee)}</td><td>${esc(r.reason)}</td><td>${srcs(src)}</td></tr>`; }).join("\n")}
</table></div>
<p class="small">Not included: ARIA and Horseshoe (no official schedule), Planet Hollywood and Resorts World (reported closed), Golden Nugget (downtown, series ended June 2026).</p>
`);

// Schedule
const byDate = {};
for (const r of single) (byDate[r.date] ||= []).push(r);
const dates = Object.keys(byDate).sort();
const dayRows = dates.map((d) => {
  const evs = byDate[d].sort((a, b) => a.time.localeCompare(b.time));
  const total = evs.reduce((s, e) => s + (e.buy_in_num || 0), 0);
  return `<h3>${esc(dayName(d))} <span class="small">${esc(d)}</span></h3>
<div class="table-wrap"><table>
<tr><th>Start</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Registration closes</th><th>Source</th></tr>
${evs.map((e) => `<tr><td>${esc(e.time)}</td><td>${esc(e.event)} <span class="small">(Event ${esc(e.event_no)})</span></td><td>${esc(e.buy_in)}</td><td>${cell(e.guarantee)}</td><td>${cell(e.reg_closes)}</td><td>${srcs(e.sources.slice(0, 1))}</td></tr>`).join("\n")}
</table></div>
<p class="small">Total buy-ins if you enter every event this day: $${total.toLocaleString("en-US")} (excludes hotel, food and any rebuys).</p>`;
}).join("\n");

pages["schedule.html"] = layout("schedule.html", "Schedule", `
<h2>Single-entry schedule (Venetian, Nov 16 to Dec 9, 2026)</h2>
<div class="note"><b>8 AM all-day plan: not possible with single-entry events alone.</b> The earliest verified single-entry start is ${esc(earliest.time)} (${esc(earliest.event)}, ${esc(dayName(earliest.date))}), and the RaceDay stack (10:10 AM, Nov 19 to 21) is the only 10:10 AM start. Most other days start at 11:10 AM. Evening starts are at 5:10 PM.</div>
<p>To play more events on a single day, you would need to add re-entry or add-on events from the <a href="separate-section.html">Separate section</a>. Those include Caesars Palace at 10 AM, 2 PM, 6 PM and 9 PM daily; Wynn at noon and 6 PM; and Bellagio on Fridays, Saturdays and Sundays at 11 AM. Walking times between venues are not verified (see the <a href="flagged.html">Flagged</a> page).</p>
<h3>Walking-route checks (manual)</h3>
<p class="small">These links open a route in Google Maps for manual timing. They are not verified values.</p>
<ul class="small">
<li><a href="https://www.google.com/maps/dir/The+Venetian+Resort+Las+Vegas/Caesars+Palace+Las+Vegas" target="_blank" rel="noopener">Venetian to Caesars Palace</a></li>
<li><a href="https://www.google.com/maps/dir/The+Venetian+Resort+Las+Vegas/Wynn+Las+Vegas" target="_blank" rel="noopener">Venetian to Wynn Las Vegas</a></li>
<li><a href="https://www.google.com/maps/dir/The+Venetian+Resort+Las+Vegas/Bellagio+Las+Vegas" target="_blank" rel="noopener">Venetian to Bellagio</a></li>
</ul>
<h2>Day-by-day (single-entry)</h2>
${dayRows}
`);

// Hotels
pages["hotels.html"] = layout("hotels.html", "Hotels", `
<h2>Hotels near the tournament rooms</h2>
<div class="note"><b>True cost per night is not calculable yet.</b> Nightly rates are dynamic and walking times are not verifiable from official sources. Resort fees are filled only where the operator's own terms were retrieved.</div>
<div class="table-wrap"><table>
<tr><th>Hotel</th><th>Poker room location</th><th>Nightly rate</th><th>Resort fee (per night)</th><th>Resort fee status</th><th>True cost per night</th><th>Walking minutes to poker room</th><th>Poker-room rate (official)</th><th>Sources</th><th>Flag</th></tr>
${H.hotels.map((h) => `<tr>
<td>${esc(h.hotel)}</td>
<td>${esc(h.poker_room_location)}</td>
<td>${cell(h.nightly_rate)}</td>
<td>${cell(h.resort_fee)}</td>
<td><span class="tag ${h.resort_fee_status.startsWith("Verified") ? "ok" : "warn"}">${esc(h.resort_fee_status)}</span></td>
<td>${cell(h.true_cost_per_night)}</td>
<td>${cell(h.walking_minutes_to_poker_room)}</td>
<td>${h.poker_rate ? esc(h.poker_rate) + `<br><span class="small">${esc(h.poker_rate_status)}</span>` : BLANK}</td>
<td>${srcs(h.sources)}</td>
<td class="small">${esc(h.flag)}</td>
</tr>`).join("\n")}
</table></div>
`);

pages["venues.html"] = layout("venues.html", "Venues", `
<h2>Las Vegas Strip poker rooms: status</h2>
<div class="table-wrap"><table>
<tr><th>Venue</th><th>On the Strip</th><th>Status</th><th>Tournament status</th><th>Sources</th><th>Flag</th></tr>
${V.venues.map((v) => `<tr><td>${esc(v.venue)}</td><td>${esc(v.strip)}</td><td>${esc(v.status)}</td><td>${esc(v.tournament_status)}</td><td>${srcs(v.sources)}</td><td class="small">${esc(v.flag)}</td></tr>`).join("\n")}
</table></div>
`);

pages["analysis.html"] = layout("analysis.html", "Analysis", `
<h2>Analysis of single-entry events</h2>
<p>Ratios are computed from the official figures in the tables (guarantee ÷ buy-in, and prize pool ÷ buy-in from each structure sheet). They are arithmetic, not forecasts.</p>
<h3>Ranked by guarantee</h3>
<div class="table-wrap"><table>
<tr><th>#</th><th>Date</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Guarantee ÷ buy-in</th><th>Prize pool share of buy-in</th><th>Source</th></tr>
${byGTD.map((r, i) => `<tr><td>${i + 1}</td><td>${esc(dayName(r.date))}</td><td>${esc(r.event)} <span class="small">(Event ${esc(r.event_no)})</span></td><td>${esc(r.buy_in)}</td><td>${cell(r.guarantee)}</td><td>${r.ratio ? r.ratio.toFixed(1) + "×" : BLANK}</td><td>${r.share ? (r.share * 100).toFixed(1) + "%" : BLANK}</td><td>${srcs(r.sources.slice(0, 1))}</td></tr>`).join("\n")}
</table></div>
<h3>Findings</h3>
<ul>
<li>Best guarantee per dollar: the $600 events (Dec 6 and Dec 7, $40,000 each) at about 66.7×. The Nov 27 $600 event ($30,000) is about 50×.</li>
<li>The $200 bounty events list an $8,000 guarantee (40× ratio). The schedule says that guarantee includes the bounties.</li>
<li>Prize pool share is highest on the $600 events (85%) and the $400 event (83.75%). The $200 events are 80% to 82.5%.</li>
<li>Multi-flight events (Venetian Event 7, $75,000 guarantee) are not in the single-entry list, because one flight can be entered more than once. They are in the separate section.</li>
<li>The Venetian's poker suite requires a $300+ buy-in each night, so a $300+ single-entry event meets that condition. Events at $300 or more are: Events 2, 10, 12, 14, 16, 28 and 30.</li>
</ul>
<h3>Limits of this analysis</h3>
<ul>
<li>Guarantees and buy-ins are official, but actual prize pools depend on the number of entries.</li>
<li>Field sizes are not verified from official sources, so expected value and return on investment are not calculated.</li>
<li>Hotel costs, walking times and the true cost per night are not included (see <a href="questions.html">Questions</a>).</li>
</ul>
`);

pages["questions.html"] = layout("questions.html", "Questions", `
<h2>Questions to answer before deciding</h2>
<p>These are open items. Each one shows what we have, what is missing, and how to get it.</p>
<div class="table-wrap"><table>
<tr><th>ID</th><th>Question</th><th>What we have (verified)</th><th>What is missing</th><th>How to resolve</th></tr>
${Q.questions.map((q) => `<tr><td>${esc(q.id)}</td><td>${esc(q.question)}</td><td>${esc(q.have)}</td><td>${esc(q.missing)}</td><td>${esc(q.how)}</td></tr>`).join("\n")}
</table></div>
`);

pages["suggestions.html"] = layout("suggestions.html", "Suggestions", `
<h2>Suggestions for improving the site (for your decision)</h2>
<div class="note"><b>Nothing here has been implemented.</b> Choose an option for each suggestion (or reply with changes). Work starts only after you decide.</div>
<div class="table-wrap"><table>
<tr><th>ID</th><th>Suggestion</th><th>What it does</th><th>Benefit</th><th>Effort</th><th>Options</th><th>Your decision</th></tr>
${S.suggestions.map((s) => `<tr><td>${esc(s.id)}</td><td>${esc(s.title)}</td><td>${esc(s.what)}</td><td>${esc(s.benefit)}</td><td>${esc(s.effort)}</td><td>${s.options.map(esc).join(" / ")}</td><td class="blank">Awaiting decision</td></tr>`).join("\n")}
</table></div>
`);

pages["flagged.html"] = layout("flagged.html", "Flagged for Review", `
<h2>Flagged for Review</h2>
<p>These are irregularities, conflicts between sources, and items left unverified. They do not block the site from going live. Each item lists its sources so you can check them.</p>
<div class="table-wrap"><table>
<tr><th>ID</th><th>Severity</th><th>Item</th><th>Detail</th><th>Sources</th></tr>
${F.flags.map((f) => `<tr><td>${esc(f.id)}</td><td><span class="tag ${f.severity === "High" ? "warn" : f.severity === "Medium" ? "" : "ok"}">${esc(f.severity)}</span></td><td>${esc(f.item)}</td><td>${esc(f.detail)}</td><td>${f.sources.length ? srcs(f.sources) : `<span class="blank">No source</span>`}</td></tr>`).join("\n")}
</table></div>
`);

pages["repo-review.html"] = layout("repo-review.html", "Repo review", `
<h2>Repo review</h2>
<p>${esc(R.summary)}</p>
<div class="table-wrap"><table>
<tr><th>Item</th><th>Detail</th><th>Status</th></tr>
${R.findings.map((f) => `<tr><td>${esc(f.item)}</td><td>${esc(f.detail)}</td><td>${esc(f.status)}</td></tr>`).join("\n")}
</table></div>
<h3>Method</h3>
<ul>
<li>Official operator pages and PDFs were fetched directly. Third-party sites were used only to find conflicts, and each conflict is flagged.</li>
<li>Single-entry status was decided from the structure sheet (re-entry, rebuy, add-on or flight rules). If a sheet was not opened, the event is unclassified.</li>
<li>Blank fields are left blank. They are not inferred.</li>
<li>Coordination log and task board: <code>COORDINATION.md</code> in the repository root.</li>
</ul>
<p class="small">${esc(R.tool_check)}</p>
`);

// ---- Write ----
if (existsSync(outDir)) for (const f of readdirSync(outDir)) if (f.endsWith(".html")) rmSync(join(outDir, f));
mkdirSync(outDir, { recursive: true });
for (const [name, html] of Object.entries(pages)) writeFileSync(join(outDir, name), html);
writeFileSync(join(outDir, ".nojekyll"), "");
console.log(`Built ${Object.keys(pages).length} pages into docs/`);
