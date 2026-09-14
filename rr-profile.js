/* shared by reporter.html and every /reporter/<slug>/ page */

/* hrefFor turns a row label into a link: teams and players deep-link into
   their ranking pages with the current period carried along. */
function bars(map, limit, hrefFor) {
  const rows = Object.entries(map || {}).sort((a, b) => b[1] - a[1]).slice(0, limit);
  if (!rows.length) return '<div class="hint">Nothing tracked yet.</div>';
  const peak = rows[0][1];
  return rows.map(([k, v]) => {
    const label = hrefFor
      ? '<a href="' + hrefFor(k) + '">' + esc(k) + '</a>'
      : esc(k);
    return '<div class="bd-row"><span class="lbl">' + label + '</span>' +
      '<span class="bar" style="width:' + Math.max(4, v / peak * 90) + 'px"></span>' +
      '<span class="v">' + num(v) + '</span></div>';
  }).join("");
}

/* Cross-links to other reporters: colleagues at the same outlet, then the
   reporters ranked immediately around this one. Useful for readers and it
   gives the 300 static pages real internal linking. */
function relatedReporters(r) {
  const ranked = RR.reporters;                 // already sorted by total
  const idx = ranked.findIndex(x => x.id === r.id);
  const link = x => '<a href="' + reporterHref(x) + '">' + esc(x.name) + '</a>' +
    '<span class="ro">' + num(x.total) + '</span>';

  const colleagues = r.outlet && r.outlet !== "Unknown"
    ? ranked.filter(x => x.outlet === r.outlet && x.id !== r.id).slice(0, 6) : [];
  const nearby = idx >= 0
    ? ranked.slice(Math.max(0, idx - 3), idx).concat(ranked.slice(idx + 1, idx + 4)) : [];

  let html = "";
  if (colleagues.length) {
    html += '<div class="section"><h2>Also at ' + esc(r.outlet) + '</h2><div class="related">' +
      colleagues.map(link).join("") + '</div></div>';
  }
  if (nearby.length) {
    html += '<div class="section"><h2>Ranked nearby</h2><div class="related">' +
      nearby.map(link).join("") + '</div></div>';
  }
  return html;
}

function monthlyChart(r) {
  const m = {};
  for (const [d, c] of Object.entries(r.byDate || {})) {
    const k = d.slice(0, 7);
    m[k] = (m[k] || 0) + c;
  }
  const keys = Object.keys(m).sort();
  if (!keys.length) return '<div class="chart-empty">No dated activity.</div>';
  const start = keys[0], end = keys[keys.length - 1];
  const all = [];
  let [y, mo] = start.split("-").map(Number);
  const [ey, emo] = end.split("-").map(Number);
  while (y < ey || (y === ey && mo <= emo)) {
    all.push(String(y) + "-" + String(mo).padStart(2, "0"));
    mo++; if (mo > 12) { mo = 1; y++; }
  }
  const peak = Math.max(...all.map(k => m[k] || 0)) || 1;
  const W = 960, H = 170, pad = 18;
  const bw = (W - pad * 2) / all.length;
  const rects = all.map((k, i) => {
    const v = m[k] || 0;
    const h = (H - pad * 2) * (v / peak);
    return '<rect x="' + (pad + i * bw).toFixed(1) + '" y="' + (H - pad - h).toFixed(1) +
      '" width="' + Math.max(1, bw - 1).toFixed(1) + '" height="' + h.toFixed(1) + '"><title>' +
      k + ': ' + num(v) + '</title></rect>';
  }).join("");
  const labels = all.map((k, i) => (k.endsWith("-01") && all.length < 200) || i === 0 || i === all.length - 1
    ? '<text x="' + (pad + i * bw).toFixed(1) + '" y="' + (H - 4) + '">' + k.slice(0, 4) + '</text>' : "").join("");
  return '<svg class="spark-big" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none">' +
    rects + labels + '</svg>';
}

function activeRange(r) {
  const keys = Object.keys(r.byDate || {}).sort();
  if (!keys.length) return "-";
  const f = new Date(keys[0]), l = new Date(keys[keys.length - 1]);
  const o = { month: "short", year: "numeric" };
  return f.toLocaleDateString("en-US", o) + " - " + l.toLocaleDateString("en-US", o);
}

function render() {
  // Static pages under /reporter/<slug>/ set RR_FIXED_ID. The query-string
  // version stays as the fallback for reporters outside the generated set.
  const id = (typeof RR_FIXED_ID !== "undefined")
    ? RR_FIXED_ID
    : new URLSearchParams(location.search).get("r");
  const r = id ? reporterById(id) : null;
  const app = document.getElementById("app");

  if (!r) {
    app.innerHTML = '<div class="empty">Reporter not found. ' +
      '<a href="index.html">Back to the leaderboard</a>.</div>';
    return;
  }

  document.title = r.name + " - NBA rumor mentions and coverage | HoopsMatic";
  const md = document.querySelector('meta[name="description"]');
  if (md) md.setAttribute("content", r.name + " of " + r.outlet + " has " + num(r.total) +
    " mentions in the HoopsHype NBA rumors archive. Teams covered, players covered and activity by month.");
  document.getElementById("phead").innerHTML =
    '<a class="back" href="' + BASE + 'index.html">&larr; All reporters</a>' +
    '<h1>' + esc(r.name) + '</h1>' +
    '<div class="esub">' + esc(r.outlet) + '</div>';

  const rank = reporterStats(0).findIndex(x => x.id === r.id) + 1;
  const last90 = getFilteredCount(r.byDate, 90);

  app.innerHTML =
    '<div class="stat-cards four">' +
      '<div class="stat-card"><div class="lbl">Mentions</div><div class="num">' + num(r.total) + '</div></div>' +
      '<div class="stat-card"><div class="lbl">All-time rank</div><div class="num">' + (rank || "-") + '</div></div>' +
      '<div class="stat-card"><div class="lbl">Last 3 months</div><div class="num">' + num(last90) + '</div></div>' +
      '<div class="stat-card"><div class="lbl">Active</div><div class="num" style="font-size:.95rem">' + esc(activeRange(r)) + '</div></div>' +
    '</div>' +
    '<div class="section"><h2>Mentions by month</h2><div class="hint">Every dated mention in the archive.</div>' +
      monthlyChart(r) + '</div>' +
    '<div class="breakdown">' +
      '<div class="section"><h2>Teams covered</h2>' + bars(r.byTeam, 12, t => teamHref(t, 0)) + '</div>' +
      '<div class="section"><h2>Players covered</h2>' + bars(r.byPlayer, 12, p => playerHref(p, 0)) + '</div>' +
    '</div>' +
    '<div class="breakdown">' +
      '<div class="section"><h2>Topics</h2>' + bars(r.byTopic, 8) + '</div>' +
      '<div class="section"><h2>Agents mentioned</h2>' + bars(r.byAgent, 8) + '</div>' +
    '</div>' +
    relatedReporters(r);
}

bootPage(render);
