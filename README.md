# NBA Reporter Rankings

**Live Demo:** [jsierrahoopshype.github.io/reporter-rankings](https://jsierrahoopshype.github.io/reporter-rankings/)

A comprehensive tool tracking NBA reporters and their coverage patterns, built on top of the HoopsHype Rumors Archive (624,000+ rumors).

---

## Features

| Feature | Description |
|---------|-------------|
| **Most Active Reporters** | Leaderboard ranked by total rumors reported |
| **Breaking News Leaders** | Who breaks stories first |
| **Topic Specialists** | Leaders in Trade, Injury, Contract, Front Office coverage |
| **Reporter Profiles** | Click any reporter for detailed stats and recent rumors |
| **Who Covers Who Matrix** | Reporter × Team coverage heatmap |
| **Historical Comparison** | Compare trade deadline periods year-over-year |

---

## How It Works

1. **GitHub Actions** runs every 6 hours
2. Fetches latest data from the [HoopsHype Rumors Archive](https://github.com/jsierrahoopshype/hoopshype-rumors)
3. Processes archive to extract reporter statistics
4. Generates `reporter_data.js` for the frontend
5. Deploys to GitHub Pages automatically

---

## Files

```
reporter-rankings/
├── index.html              # Main UI
├── reporter_data.js        # Generated data (auto-updated)
├── reporter_data.json      # Raw JSON version
├── process_archive.py      # Data processor script
├── last_updated.txt        # Timestamp of last update
└── .github/
    └── workflows/
        └── update-rankings.yml  # Automation workflow
```

---

## Reporters Tracked

### Tier 1 - Major Insiders
- Shams Charania (ESPN)
- Adrian Wojnarowski (ESPN - Retired)
- Marc Stein (The Stein Line)
- Jake Fischer (Yahoo Sports)
- Chris Haynes (Bleacher Report)

### Tier 2 - National Reporters
- Brian Windhorst, Bobby Marks, Tim Bontemps (ESPN)
- Sam Amick, Anthony Slater, John Hollinger (The Athletic)
- Michael Scotto, Alex Kennedy (HoopsHype)
- Kevin O'Connor (The Ringer)
- Eric Pincus (Bleacher Report)
- Marc Spears (Andscape)
- And 20+ more...

### Tier 3 - Beat Writers
- Regional reporters and team-specific beat writers

---

## Embed on HoopsHype

```html
<iframe 
  src="https://jsierrahoopshype.github.io/reporter-rankings/" 
  width="100%" 
  height="900" 
  frameborder="0"
  style="border: none; max-width: 1400px;"
></iframe>
```

---

## Manual Update

To manually trigger an update:

1. Go to **Actions** tab
2. Select **Update Reporter Rankings**
3. Click **Run workflow**

---

## Local Development

```bash
# Clone the repo
git clone https://github.com/jsierrahoopshype/reporter-rankings.git
cd reporter-rankings

# Process local archive data
python3 process_archive.py path/to/archive.json -o reporter_data.js

# Serve locally
python3 -m http.server 8000
# Open http://localhost:8000
```

---

## Data Source

This tool is powered by the **HoopsHype Rumors Archive**:
- 624,000+ NBA rumors
- 15 years of coverage (2010-present)
- Auto-updated 4x daily

Archive repo: [github.com/jsierrahoopshype/hoopshype-rumors](https://github.com/jsierrahoopshype/hoopshype-rumors)

---

## License

Internal tool for HoopsHype. All rights reserved.
