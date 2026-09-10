const NBA_TEAMS = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", 
    "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", 
    "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
    "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat", 
    "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", 
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns",
    "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", 
    "Toronto Raptors", "Utah Jazz", "Washington Wizards"
];

const TEAM_SHORT_TO_FULL = {
    "Hawks": "Atlanta Hawks", "Celtics": "Boston Celtics", "Nets": "Brooklyn Nets",
    "Hornets": "Charlotte Hornets", "Bulls": "Chicago Bulls", "Cavaliers": "Cleveland Cavaliers",
    "Mavericks": "Dallas Mavericks", "Nuggets": "Denver Nuggets", "Pistons": "Detroit Pistons",
    "Warriors": "Golden State Warriors", "Rockets": "Houston Rockets", "Pacers": "Indiana Pacers",
    "Clippers": "Los Angeles Clippers", "Lakers": "Los Angeles Lakers", "Grizzlies": "Memphis Grizzlies",
    "Heat": "Miami Heat", "Bucks": "Milwaukee Bucks", "Timberwolves": "Minnesota Timberwolves",
    "Pelicans": "New Orleans Pelicans", "Knicks": "New York Knicks", "Thunder": "Oklahoma City Thunder",
    "Magic": "Orlando Magic", "76ers": "Philadelphia 76ers", "Sixers": "Philadelphia 76ers",
    "Suns": "Phoenix Suns", "Trail Blazers": "Portland Trail Blazers", "Blazers": "Portland Trail Blazers",
    "Kings": "Sacramento Kings", "Spurs": "San Antonio Spurs", "Raptors": "Toronto Raptors", 
    "Jazz": "Utah Jazz", "Wizards": "Washington Wizards"
};

const TEAM_ABBREV = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS"
};

// Non-players to exclude
const NON_PLAYERS = new Set([
    "team usa", "usa basketball", "g league", "nba", "all-star", "hall of fame", 
    "olympics", "fiba", "eurobasket", "world cup", "summer league", "social media",
    "free agency", "trade", "draft", "new orleans hornets", "training camp",
    "two-way contracts", "two-way contract", "salary cap", "load management",
    "drew league", "real madrid", "charlotte bobcats",
    // Commissioners/Executives/Owners
    "david stern", "adam silver", "billy hunter", "mark cuban", "mat ishbia",
    "james dolan", "jeanie buss", "mikhail prokhorov", "robert sarver",
    "billy king", "david griffin", "donnie nelson", "mitch kupchak", "neil olshey",
    "nico harrison", "jon horst", "sean marks", "lawrence frank",
    // Coaches
    "doc rivers", "brad stevens", "gregg popovich", "brett brown", "rick carlisle",
    "erik spoelstra", "phil jackson", "mike d'antoni", "dwane casey", "frank vogel",
    "steve kerr", "tyronn lue", "tom thibodeau", "mike budenholzer", "nick nurse",
    "quin snyder", "monty williams", "jason kidd", "ime udoka", "jb bickerstaff",
    "mark daigneault", "doug christie", "scott brooks", "steve nash",
    "pat riley", "david blatt", "jordi fernandez", "mike brown",
    "billy donovan", "chris finch", "david fizdale", "darvin ham",
    "igor kokoskov", "jacque vaughn", "jeff van gundy", "joe mazzulla",
    "kenny atkinson", "stephen silas", "jj redick",
    // GMs/Executives  
    "bob myers", "sam presti", "daryl morey", "masai ujiri", "rob pelinka",
    "james jones", "koby altman",
    // Reporters (not players)
    "shams charania",
    // Other non-players
    "donald trump",
    // Agents
    "mark bartelstein", "rich paul", "jeff schwartz", "aaron mintz", "bill duffy",
    "leon rose", "dan fegan", "arn tellem", "aaron goodwin", "happy walters"
].map(s => s.toLowerCase()));

// Excluded "reporters" (PR accounts, teams, players, non-reporters)
const EXCLUDED_REPORTERS = new Set([
    // PR accounts
    "@mrbuckbucknba", "@nbapr", "@ohnohedidnt24", "@hornetspr", "@espnstatsinfo",
    "@trailblazerspr", "@trailblazerpr", "@pelicansnba", "@magic_pr", "@fullcourtpass",
    "@kingjames", "@nba__courtside", "@hellowelcomepod", "@wwe",
    "mrbuckbucknba", "nbapr", "ohnohedidnt24", "hornetspr", "espnstatsinfo",
    "trailblazerspr", "trailblazerpr", "pelicansnba", "magic_pr", "fullcourtpass",
    "mavs pr", "grizzlies pr", "timberwolves pr", "heat centel", "hawks pr",
    // Teams listed as reporters
    "atlanta hawks", "chicago bulls", "indiana pacers", "milwaukee bucks",
    "utah jazz", "miami heat",
    // Players listed as reporters
    "carmelo anthony", "chris paul", "dwight howard", "giannis antetokounmpo",
    "dwyane wade", "bradley beal", "magic johnson", "isaiah thomas", "john wall",
    "damian lillard", "cade cunningham", "tyrese haliburton", "tyrese maxey",
    "austin reaves", "ben simmons", "norman powell",
    "kobe bryant", "kevin love", "rudy gobert", "donovan mitchell", "trae young",
    "kevin durant", "joel embiid", "draymond green", "kyrie irving", "steve nash",
    "pau gasol", "andre iguodala", "kyle kuzma",
    "ricky rubio", "patrick beverley", "ja morant", "jamal crawford",
    // Coaches/Others
    "steve kerr", "mat ishbia", "kevin hart", "doug christie", "training camp",
    // Non-reporter accounts
    "underdog nba", "pels film room", "rich paul", "@pelsfilmroom", "pelsfilmroom",
    // Generic
    "social media", "unknown", "n/a", "clutch points"
].map(s => s.toLowerCase()));

// Excluded outlets
const EXCLUDED_OUTLETS = new Set([
    "youtube", "reddit", "twitter", "x.com", "instagram", "facebook", 
    "tiktok", "threads", "unknown", "@kcjhoop"
].map(s => s.toLowerCase()));

// Handle to reporter name mapping
const HANDLE_TO_NAME = {
    "kcjhoop": "K.C. Johnson"
};

// Name corrections for misspellings and variations
const NAME_CORRECTIONS = {
    "shams charnia": "Shams Charania",
    "dave mcmenanim": "Dave McMenamin",
    "omari sanfoka": "Omari Sanfoka II",
    "omari sankofa ii": "Omari Sanfoka II",
    "omari sankofa": "Omari Sanfoka II"
};

// Reporter to outlet mapping
const REPORTER_TO_OUTLET = {
    "jorge sierra": "HoopsHype",
    "michael scotto": "HoopsHype",
    "anthony slater": "ESPN",
    "law murray": "The Athletic",
    "brandon rahbar": "Daily Thunder",
    "duane rankin": "Arizona Republic",
    "mike curtis": "Dallas Morning News",
    "jason beede": "Orlando Sentinel",
    "austin krell": "Sports Illustrated",
    "dan woike": "The Athletic",
    "joel lorenzi": "The Athletic",
    "justin russo": "Russo Writes Substack",
    "bennett durando": "The Denver Post",
    "chris haynes": "NBA on Prime",
    "sean highkin": "Rose Garden Report",
    "tim macmahon": "ESPN",
    "grant afseth": "Dallas Hoops Journal",
    "tim bontemps": "ESPN",
    "nick depaula": "Freelance",
    "bobby marks": "ESPN",
    "kellan olson": "Arizona Sports",
    "adam aaronson": "The Philly Voice",
    "joey linn": "Freelance",
    "tony east": "Forbes Sports",
    "khobi price": "The California Post",
    "damichael cole": "Memphis Commercial Appeal",
    "keerthika uthayakumar": "Freelance",
    "marc j. spears": "Andscape",
    "kc johnson": "Chicago Sports Network",
    "k.c. johnson": "Chicago Sports Network",
    "josh robbins": "The Athletic",
    "brian lewis": "New York Post",
    "dustin dopirak": "Indianapolis Star",
    "sean cunningham": "NBC Sacramento",
    "stefan bondy": "New York Post",
    "tim reynolds": "The Associated Press",
    "ohm youngmisuk": "ESPN",
    "rod boone": "Charlotte Observer",
    "michael grange": "Sportsnet",
    "maxime aubin": "L'Equipe",
    "omari sanfoka ii": "Detroit Free Press",
    "jake fischer": "The Stein Line",
    "jeff mcdonald": "San Antonio Express-News",
    "sam amick": "The Athletic",
    "brad rowland": "FanSided",
    "jay king": "The Athletic",
    "derek bodner": "PHLY Sports",
    "danny cunningham": "The Inside Shot",
    "kris pursiainen": "ClutchPoints",
    "chris fedor": "Cleveland Plain Dealer",
    "ramona shelburne": "ESPN",
    "andy larsen": "Salt Lake Tribune",
    "keith smith": "Spotrac",
    "michael c. wright": "ESPN",
    "clemente almanza": "The Thunder Wire",
    "dan weiss": "FanDuel Sports",
    "tom orsborne": "San Antonio Express-News",
    "bobby manning": "CLNS",
    "scott agness": "Fieldhouse Files",
    "gerald bourguet": "Suns After Dark",
    "erik slater": "ClutchPoints",
    "mike trudell": "Spectrum SportsNet",
    "vinny benedetto": "Denver Gazette",
    "james ham": "ESPN1320"
};

// Outlet normalization
const OUTLET_NORMALIZE = {
    "espn.com": "ESPN", "ESPN.com": "ESPN",
    "hoopshype": "HoopsHype", "Hoopshype": "HoopsHype"
};

// =============================================
// STATE
// =============================================

let REPORTERS = [];
let OUTLETS = [];
let currentDays = 90; // Default to 3 months
let currentView = 'leaderboard';
let currentProfileId = null;

// =============================================
// HELPER FUNCTIONS
// =============================================


function getFilteredCount(byDate, days) {
    if (!byDate || Object.keys(byDate).length === 0) return 0;
    if (days === 0) return Object.values(byDate).reduce((sum, c) => sum + c, 0);
    
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffStr = cutoff.toISOString().split('T')[0];

    let total = 0;
    for (const [date, count] of Object.entries(byDate)) {
        if (date >= cutoffStr) total += count;
    }
    return total;
}

function getProportionalCount(totalCount, byDate, days) {
    if (days === 0) return totalCount;
    const allTimeTotal = Object.values(byDate || {}).reduce((sum, c) => sum + c, 0);
    if (allTimeTotal === 0) return 0;
    const filteredTotal = getFilteredCount(byDate, days);
    return Math.round(totalCount * (filteredTotal / allTimeTotal));
}

function isValidReporter(name) {
    if (!name) return false;
    const nameLower = name.toLowerCase().trim();
    if (EXCLUDED_REPORTERS.has(nameLower)) return false;
    if (nameLower.startsWith('@') && nameLower.length < 4) return false;
    for (const team of NBA_TEAMS) {
        if (nameLower === team.toLowerCase()) return false;
    }
    return true;
}

function isValidPlayer(name) {
    if (!name) return false;
    const nameLower = name.toLowerCase().trim();
    if (NON_PLAYERS.has(nameLower)) return false;
    // Don't check EXCLUDED_REPORTERS here - players like Damian Lillard should still appear as players
    for (const short of Object.keys(TEAM_SHORT_TO_FULL)) {
        if (nameLower === short.toLowerCase()) return false;
    }
    for (const team of NBA_TEAMS) {
        if (nameLower === team.toLowerCase()) return false;
    }
    return true;
}

function isValidOutlet(name) {
    if (!name) return false;
    return !EXCLUDED_OUTLETS.has(name.toLowerCase().trim());
}

function normalizeTeamName(team) {
    return TEAM_SHORT_TO_FULL[team] || team;
}

function normalizeOutletName(outlet) {
    if (!outlet) return outlet;
    const lower = outlet.toLowerCase();
    for (const [key, val] of Object.entries(OUTLET_NORMALIZE)) {
        if (key.toLowerCase() === lower) return val;
    }
    return outlet;
}

function normalizeReporterName(name) {
    if (!name) return name;
    const handle = name.replace('@', '').toLowerCase();
    if (HANDLE_TO_NAME[handle]) return HANDLE_TO_NAME[handle];
    
    const nameLower = name.toLowerCase();
    
    // Apply direct corrections
    if (NAME_CORRECTIONS[nameLower]) return NAME_CORRECTIONS[nameLower];
    
    // Pattern-based corrections
    if (nameLower.includes('scotto')) return 'Michael Scotto';
    if (nameLower.includes('woj')) return 'Adrian Wojnarowski';
    
    return name;
}

function getReporterOutlet(name, defaultOutlet) {
    const nameLower = name.toLowerCase();
    if (REPORTER_TO_OUTLET[nameLower]) return REPORTER_TO_OUTLET[nameLower];
    return normalizeOutletName(defaultOutlet);
}
/* ==========================================================================
   Curation added after the HoopsMatic rebuild
   ========================================================================== */

// Accounts that are not reporters.
[
  "heat central", "heat centel", "@thenbabase", "thenbabase",
  "@thenbacentral", "thenbacentral", "@thenbahustle",
  "legion hoops", "@legionhoops", "legion sports",
  "aph00ps", "@aph00ps", "jaylen brown"
].forEach(n => EXCLUDED_REPORTERS.add(n.toLowerCase()));

// Names the archive credits like a reporter that are really media outlets.
// These get folded into the Outlets tab instead of being dropped.
const RECLASSIFY_AS_OUTLET = {
  "espncleveland": "ESPN Cleveland",
  "espn cleveland": "ESPN Cleveland",
  "twitter @espncleveland": "ESPN Cleveland",
  "siriusxmnba": "SiriusXM NBA Radio",
  "siriusxmsports": "SiriusXM NBA Radio",
  "sirius xm": "SiriusXM NBA Radio",
  "siriusxm": "SiriusXM NBA Radio",
  "sirius xmnba": "SiriusXM NBA Radio",
  "sirius xm nba": "SiriusXM NBA Radio",
  "siriusxm nba": "SiriusXM NBA Radio",
  "twitter @siriusxmnba": "SiriusXM NBA Radio"
};

// The archive writes the same account several ways ("@espncleveland",
// "Twitter @ESPNCleveland"), so match on the bare handle too.
function reclassifiedOutlet(name) {
  const n = (name || "").toLowerCase().trim();
  return RECLASSIFY_AS_OUTLET[n] || RECLASSIFY_AS_OUTLET[n.replace(/^@/, "")] || null;
}

// A bare Twitter handle is an account, not a media outlet. Jorge's ruling on
// "Twitter @KCJHoop" applies to the whole family of them (663 of them, ~16.6K
// mentions), except the handles remapped to a real outlet just above.
function rrOutletName(name) {
  return reclassifiedOutlet(name) || normalizeOutletName(name);
}
function rrValidOutlet(name) {
  if (!isValidOutlet(name)) return false;
  return !/^twitter\s*@/i.test(String(name).trim());
}

/* The blanket "any name containing Woj is Adrian Wojnarowski" rule also
   swallows Jakub Wojczynski (1 mention, a different person). Same shape of risk
   for any substring rule. Names listed here are never folded by those rules. */
const NEVER_MERGE = new Set(["jakub wojczynski"]);

const _normalizeReporterNameRaw = normalizeReporterName;
normalizeReporterName = function (name) {
  if (NEVER_MERGE.has((name || "").toLowerCase().trim())) return name;
  return _normalizeReporterNameRaw(name);
};

/* ==========================================================================
   Shared state + data build
   ========================================================================== */

const RR = {
  reporters: [],
  outlets: [],
  meta: {},
  days: 0,          // 0 = all time, the default everywhere now
  ready: false
};

const PERIODS = [
  { days: 0,   label: "All Time" },
  { days: 7,   label: "Week" },
  { days: 30,  label: "Month" },
  { days: 90,  label: "3 Mo" },
  { days: 180, label: "6 Mo" },
  { days: 365, label: "Year" }
];

/* ---- period in the URL ----------------------------------------------------
   ?period=7|30|90|180|365|all . Every nav link carries it, so switching pages
   keeps the filter and a filtered view can be pasted to someone else. */
function periodFromUrl() {
  const raw = new URLSearchParams(location.search).get("period");
  if (!raw) return 0;
  if (raw === "all") return 0;
  const n = parseInt(raw, 10);
  return PERIODS.some(p => p.days === n) ? n : 0;
}

function periodParam(days) { return days === 0 ? "all" : String(days); }

function setPeriodInUrl(days) {
  const u = new URL(location.href);
  u.searchParams.set("period", periodParam(days));
  history.replaceState(null, "", u);
  document.querySelectorAll("#nav a").forEach(a => {
    const t = new URL(a.getAttribute("href"), location.href);
    t.searchParams.set("period", periodParam(days));
    a.setAttribute("href", t.pathname.split("/").pop() + t.search);
  });
}

function periodLabel(days) {
  const p = PERIODS.find(p => p.days === days);
  return p ? p.label : "All Time";
}

function slugify(s) {
  return (s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function buildData() {
  if (typeof REPORTER_DATA === "undefined") return false;

  const reporterMap = {};
  const outletMap = {};

  function addOutlet(name, total, byDate) {
    const n = rrOutletName(name);
    if (!rrValidOutlet(n)) return;
    if (!outletMap[n]) outletMap[n] = { name: n, id: slugify(n), total: 0, byDate: {} };
    outletMap[n].total += total || 0;
    for (const [d, c] of Object.entries(byDate || {})) {
      outletMap[n].byDate[d] = (outletMap[n].byDate[d] || 0) + c;
    }
  }

  for (const r of (REPORTER_DATA.reporters || [])) {
    // Outlets misfiled as reporters move across wholesale.
    const asOutlet = reclassifiedOutlet(r.name);
    if (asOutlet) { addOutlet(asOutlet, r.total, r.by_date); continue; }

    if (!isValidReporter(r.name)) continue;

    const name = normalizeReporterName(r.name);
    const key = name.toLowerCase();

    if (!reporterMap[key]) {
      reporterMap[key] = {
        id: slugify(name),
        srcIds: [],
        name,
        outlet: getReporterOutlet(name, r.outlet),
        avatar: r.avatar || name.replace("@", "").substring(0, 2).toUpperCase(),
        total: 0, byTopic: {}, byPlayer: {}, byTeam: {}, byAgent: {}, byDate: {}
      };
    }
    const m = reporterMap[key];
    if (r.id) m.srcIds.push(r.id);   // merged aliases keep every source id
    m.total += r.total || 0;

    for (const [p, c] of Object.entries(r.by_player || {})) {
      if (isValidPlayer(p)) m.byPlayer[p] = (m.byPlayer[p] || 0) + c;
    }
    for (const [t, c] of Object.entries(r.by_team || {})) {
      const full = normalizeTeamName(t);
      if (NBA_TEAMS.includes(full)) m.byTeam[full] = (m.byTeam[full] || 0) + c;
    }
    for (const [a, c] of Object.entries(r.by_agent || {})) m.byAgent[a] = (m.byAgent[a] || 0) + c;
    for (const [d, c] of Object.entries(r.by_date || {})) m.byDate[d] = (m.byDate[d] || 0) + c;
    for (const [t, c] of Object.entries(r.by_topic || {})) m.byTopic[t] = (m.byTopic[t] || 0) + c;
  }

  for (const o of (REPORTER_DATA.outlets || [])) addOutlet(o.name, o.total, o.by_date);

  RR.reporters = Object.values(reporterMap);
  RR.outlets = Object.values(outletMap);
  RR.meta = {
    generated: REPORTER_DATA.generated_at || "",
    mentions: REPORTER_DATA.processed_rumors || 0
  };
  RR.ready = true;
  return true;
}

/* period-filtered views ---------------------------------------------------- */

function reporterStats(days) {
  return RR.reporters.map(r => {
    const filtered = getFilteredCount(r.byDate, days);
    let prev = 0;
    if (days > 0 && days <= 180) {
      const c1 = new Date(); c1.setDate(c1.getDate() - days);
      const c2 = new Date(); c2.setDate(c2.getDate() - days * 2);
      const s1 = c1.toISOString().split("T")[0], s2 = c2.toISOString().split("T")[0];
      for (const [d, c] of Object.entries(r.byDate || {})) if (d >= s2 && d < s1) prev += c;
    }
    return Object.assign({}, r, { filtered, prev, change: filtered - prev });
  }).filter(r => r.filtered > 0).sort((a, b) => b.filtered - a.filtered);
}

function outletStats(days) {
  return RR.outlets
    .map(o => Object.assign({}, o, { filtered: getFilteredCount(o.byDate, days) }))
    .filter(o => o.filtered > 0)
    .sort((a, b) => b.filtered - a.filtered);
}

function reporterById(id) {
  return RR.reporters.find(r => r.id === id) || null;
}

/* ==========================================================================
   Shared UI
   ========================================================================== */

const NAV = [
  { href: "index.html",   label: "Leaderboard" },
  { href: "teams.html",   label: "By Team" },
  { href: "players.html", label: "By Player" },
  { href: "outlets.html", label: "Outlets" },
  { href: "heatmap.html", label: "Heatmap" }
];

function renderNav(active) {
  return '<div class="tabs">' + NAV.map(n =>
    '<a href="' + n.href + '"' + (n.href === active ? ' class="active"' : '') + '>' + n.label + '</a>'
  ).join("") + '</div>';
}

function renderPeriodChips(days, onPick) {
  const host = document.getElementById("periods");
  if (!host) return;
  host.innerHTML = PERIODS.map(p =>
    '<button class="chip' + (p.days === days ? ' active' : '') + '" data-days="' + p.days + '">' + p.label + '</button>'
  ).join("");
  host.querySelectorAll("button").forEach(b => {
    b.onclick = () => onPick(parseInt(b.dataset.days, 10));
  });
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function num(n) { return (n || 0).toLocaleString("en-US"); }

function stamp() {
  if (!RR.meta.generated) return "";
  const d = new Date(RR.meta.generated);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function renderFoot() {
  const el = document.getElementById("foot");
  if (!el) return;
  el.innerHTML = "Built from the HoopsHype NBA Rumors archive &middot; " +
    num(RR.meta.mentions) + " attributed mentions &middot; updated " + esc(stamp());
}

/* Search across reporters, shared by every page. */
function wireSearch() {
  const input = document.querySelector(".esearch-global");
  const box = document.querySelector(".esearch-results");
  if (!input || !box) return;
  input.addEventListener("input", () => {
    const q = input.value.toLowerCase().trim();
    if (q.length < 2) { box.innerHTML = ""; box.style.display = "none"; return; }
    const days = RR.days || 0;
    const hits = RR.reporters
      .map(r => Object.assign({}, r, {
        shown: days === 0 ? r.total : getFilteredCount(r.byDate, days)
      }))
      .filter(r => r.name.toLowerCase().includes(q))
      .sort((a, b) => b.shown - a.shown).slice(0, 8);
    // never show a bare all-time number next to a page filtered to a week
    const suffix = days === 0 ? " all-time" : " in " + periodLabel(days).toLowerCase();
    box.innerHTML = hits.length
      ? hits.map(r => '<a href="reporter.html?r=' + encodeURIComponent(r.id) + '">' +
          '<span class="rn">' + esc(r.name) + '</span>' +
          '<span class="ro">' + esc(r.outlet) + '</span>' +
          '<span class="rc">' + num(r.shown) + suffix + '</span></a>').join("")
      : '<div class="nohit">No reporter found</div>';
    box.style.display = "block";
  });
  document.addEventListener("click", e => {
    if (!e.target.closest(".esearch-wrap")) box.style.display = "none";
  });
}

/* Load teams-data.js / players-data.js on demand. Only the page that needs
   the per-month detail pays for it. */
function loadDetail(file, globalName) {
  return new Promise((resolve, reject) => {
    if (window[globalName]) return resolve(window[globalName]);
    const s = document.createElement("script");
    s.src = file;
    s.onload = () => resolve(window[globalName] || {});
    s.onerror = () => reject(new Error("could not load " + file));
    document.head.appendChild(s);
  });
}

/* Real period count for one reporter/subject, summed from stored monthly
   buckets. No proportional estimation anywhere. */
function monthsInPeriod(days) {
  if (days === 0) return null;               // null = every month
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  return cutoff.toISOString().slice(0, 7);   // inclusive lower bound, YYYY-MM
}

function subjectCount(detail, reporter, subject, days) {
  let total = 0;
  const floor = monthsInPeriod(days);
  const ids = (reporter.srcIds && reporter.srcIds.length) ? reporter.srcIds : [reporter.id];
  for (const id of ids) {
    const months = (detail[id] || {})[subject];
    if (!months) continue;
    for (const [m, c] of Object.entries(months)) {
      if (floor === null || m >= floor) total += c;
    }
  }
  return total;
}

/* Every page calls this once. */
function bootPage(render) {
  const nav = document.getElementById("nav");
  if (nav) nav.innerHTML = renderNav(nav.dataset.active);
  RR.days = periodFromUrl();
  if (!buildData()) {
    const app = document.getElementById("app");
    if (app) app.innerHTML = '<div class="empty">Ranking data failed to load. Try a refresh.</div>';
    return;
  }
  wireSearch();
  renderFoot();
  render();
}
