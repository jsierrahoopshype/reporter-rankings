#!/usr/bin/env node
/**
 * build_reporter_pages.js — writes a real page per reporter at /reporter/<slug>/.
 *
 * Why Node rather than Python: the curation that decides who is a reporter, how
 * aliases merge and what the display name is lives in rr-core.js. Reimplementing
 * that in another language would guarantee the static pages and the live site
 * drift apart. This loads rr-core.js itself, so there is exactly one source of
 * truth.
 *
 * Each page carries prerendered, crawlable facts in the HTML (name, outlet,
 * mentions, rank, top teams and players, active range) and then hydrates with
 * the same profile script reporter.html uses, so the interactive view is
 * identical. Reporters outside the generated set keep working through
 * reporter.html?r=<slug>.
 *
 * Usage: node build_reporter_pages.js [count]
 */

const fs = require("fs");
const path = require("path");
const vm = require("vm");

// How many pages to write. Read from rr-core.js below unless overridden on the
// command line, so STATIC_PAGE_COUNT is the single source of truth: the site's
// links and the generated directories are always the same set.
const COUNT_OVERRIDE = process.argv[2] ? parseInt(process.argv[2], 10) : null;
const SITE = "https://jsierrahoopshype.github.io/reporter-rankings";
const OUT_DIR = "reporter";

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const num = n => (n || 0).toLocaleString("en-US");

// ---------------------------------------------------------------- load data
const sandbox = {
  console,
  window: {},
  document: { querySelectorAll: () => [], querySelector: () => null,
              getElementById: () => null, addEventListener: () => {},
              createElement: () => ({}), head: { appendChild: () => {} } },
  location: { pathname: "/", search: "", href: SITE },
  history: { replaceState: () => {} },
  URL, URLSearchParams,
};
vm.createContext(sandbox);

for (const f of ["reporter_data.js", "rr-core.js"]) {
  if (!fs.existsSync(f)) {
    console.error(`ERROR: ${f} not found. Run this from the repo root, after the data build.`);
    process.exit(1);
  }
  vm.runInContext(fs.readFileSync(f, "utf8"), sandbox, { filename: f });
}

const COUNT = COUNT_OVERRIDE || vm.runInContext(
  'typeof STATIC_PAGE_COUNT !== "undefined" ? STATIC_PAGE_COUNT : 500', sandbox);
console.log(`Generating the top ${COUNT} reporter pages` +
  (COUNT_OVERRIDE ? " (command-line override)" : " (from STATIC_PAGE_COUNT in rr-core.js)"));

if (!vm.runInContext("buildData()", sandbox)) {
  console.error("ERROR: buildData() failed — reporter_data.js may be empty.");
  process.exit(1);
}

const reporters = vm.runInContext(
  "JSON.stringify(RR.reporters.map(r => ({id:r.id,name:r.name,outlet:r.outlet,total:r.total," +
  "byTeam:r.byTeam,byPlayer:r.byPlayer,byDate:r.byDate})))", sandbox);
const all = JSON.parse(reporters).sort((a, b) => b.total - a.total);
const meta = JSON.parse(vm.runInContext("JSON.stringify(RR.meta)", sandbox));

if (!fs.existsSync("rr-profile.js")) {
  console.error("ERROR: rr-profile.js not found. It ships alongside reporter.html.");
  process.exit(1);
}

// --------------------------------------------------------------- page parts
function topList(map, limit) {
  return Object.entries(map || {}).sort((a, b) => b[1] - a[1]).slice(0, limit);
}

function activeRange(byDate) {
  const keys = Object.keys(byDate || {}).sort();
  if (!keys.length) return null;
  const fmt = d => new Date(d).toLocaleDateString("en-US", { month: "long", year: "numeric" });
  return { from: fmt(keys[0]), to: fmt(keys[keys.length - 1]) };
}

function prose(r, rank) {
  const teams = topList(r.byTeam, 3).map(t => t[0]);
  const players = topList(r.byPlayer, 3).map(p => p[0]);
  const range = activeRange(r.byDate);
  const bits = [];

  bits.push(`<p><strong>${esc(r.name)}</strong>${r.outlet && r.outlet !== "Unknown"
    ? ` of ${esc(r.outlet)}` : ""} has ${num(r.total)} attributed mentions in the HoopsHype NBA
    rumors archive, ranking ${rank} among all cited reporters.</p>`);

  if (range) {
    bits.push(`<p>Archived items credited to ${esc(r.name)} run from ${esc(range.from)}
      to ${esc(range.to)}.</p>`);
  }
  if (teams.length) {
    bits.push(`<p>Most-covered teams: ${teams.map(esc).join(", ")}.</p>`);
  }
  if (players.length) {
    bits.push(`<p>Most-covered players: ${players.map(esc).join(", ")}.</p>`);
  }
  bits.push(`<p>These counts measure citations, not scoops. A mention means an archived
    item was attributed to this reporter; it does not establish who reported it first.</p>`);
  return bits.join("\n    ");
}

function page(r, rank) {
  const outlet = r.outlet && r.outlet !== "Unknown" ? r.outlet : "";
  const title = `${r.name} — NBA rumor mentions and coverage | HoopsMatic`;
  const desc = `${r.name}${outlet ? ` of ${outlet}` : ""} has ${num(r.total)} attributed ` +
    `mentions in the HoopsHype NBA rumors archive. Teams covered, players covered and ` +
    `month-by-month activity.`;

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${SITE}/reporter/${r.id}/">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="HoopsMatic">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${SITE}/reporter/${r.id}/">
<meta name="twitter:card" content="summary">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../rr-styles.css">
</head>
<body>
<div class="container">

  <div id="nav" data-active="index.html"></div>

  <div id="phead" class="phead">
    <a class="back" href="../../index.html">&larr; All reporters</a>
    <h1>${esc(r.name)}</h1>
    <div class="esub">${esc(outlet || "Outlet unknown")}</div>
  </div>

  <div id="app"><div class="loading">Loading full profile...</div></div>

  <div class="seo">
    ${prose(r, rank)}
  </div>

  <div class="foot" id="foot"></div>
</div>

<script>const RR_FIXED_ID = ${JSON.stringify(r.id)};</script>
<script src="../../reporter_data.js"></script>
<script src="../../rr-core.js"></script>
<script src="../../rr-profile.js"></script>
</body>
</html>
`;
}

// ------------------------------------------------------------------- write
const chosen = all.slice(0, COUNT);
fs.mkdirSync(OUT_DIR, { recursive: true });

// Rewrite a file only when its contents actually change. Most of the tail is
// static from one day to the next, and rewriting every page on every build
// would add megabytes to the repo daily for no reason.
let written = 0, unchanged = 0;
const keep = new Set();
chosen.forEach((r, i) => {
  if (!r.id) return;
  keep.add(r.id);
  const dir = path.join(OUT_DIR, r.id);
  const file = path.join(dir, "index.html");
  const html = page(r, i + 1);
  if (fs.existsSync(file) && fs.readFileSync(file, "utf8") === html) { unchanged++; return; }
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(file, html, "utf8");
  written++;
});

// Drop pages for reporters who fell out of the top slice, so no orphan URLs.
let pruned = 0;
for (const entry of fs.readdirSync(OUT_DIR)) {
  if (!keep.has(entry)) {
    fs.rmSync(path.join(OUT_DIR, entry), { recursive: true, force: true });
    pruned++;
  }
}

const core = ["", "teams.html", "players.html", "outlets.html", "heatmap.html"];
const urls = core.map(u => `${SITE}/${u}`)
  .concat(chosen.map(r => `${SITE}/reporter/${r.id}/`));
fs.writeFileSync("sitemap.xml",
  '<?xml version="1.0" encoding="UTF-8"?>\n' +
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  urls.map(u => `  <url><loc>${u}</loc><changefreq>daily</changefreq></url>`).join("\n") +
  "\n</urlset>\n", "utf8");

console.log(`Reporter pages: ${written} written, ${unchanged} unchanged, ${pruned} pruned ` +
  `(top ${chosen.length} of ${all.length}, cutoff ${num(chosen[chosen.length - 1].total)} mentions)`);
console.log(`Wrote sitemap.xml with ${urls.length} URLs`);
console.log(`Data generated ${meta.generated || "unknown"}`);
