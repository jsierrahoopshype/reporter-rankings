"""
Reporter Rankings Data Processor
Extracts reporter statistics from the HoopsHype Rumors Archive.

This script:
1. Loads rumors from your archive JSON
2. Extracts reporter names from text/outlet
3. Categorizes rumors by topic
4. Detects breaking news (first to report)
5. Outputs data for the Reporter Rankings tool
"""

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# =============================================
# REPORTER DETECTION
# =============================================

# Known reporters with their outlets and tier
# Tier 1: Major national insiders
# Tier 2: National reporters/analysts
# Tier 3: Beat writers/regional
KNOWN_REPORTERS = {
    # Tier 1 - Major Insiders
    "shams charania": {"name": "Shams Charania", "outlet": "ESPN", "tier": 1, "patterns": ["shams", "charania", "@shaborz"]},
    "adrian wojnarowski": {"name": "Adrian Wojnarowski", "outlet": "ESPN (Retired)", "tier": 1, "patterns": ["woj", "wojnarowski", "@wojespn"]},
    "marc stein": {"name": "Marc Stein", "outlet": "The Stein Line", "tier": 1, "patterns": ["marc stein", "stein:", "@thesteinline"]},
    "jake fischer": {"name": "Jake Fischer", "outlet": "Yahoo Sports", "tier": 1, "patterns": ["jake fischer", "fischer:", "@jakelfischer"]},
    "chris haynes": {"name": "Chris Haynes", "outlet": "Bleacher Report", "tier": 1, "patterns": ["chris haynes", "haynes:", "@chrisbhaynes"]},
    
    # Tier 2 - National Reporters
    "brian windhorst": {"name": "Brian Windhorst", "outlet": "ESPN", "tier": 2, "patterns": ["windhorst", "@windhorstespn"]},
    "bobby marks": {"name": "Bobby Marks", "outlet": "ESPN", "tier": 2, "patterns": ["bobby marks", "@bobbymarks42"]},
    "kevin oconnor": {"name": "Kevin O'Connor", "outlet": "The Ringer", "tier": 2, "patterns": ["kevin o'connor", "koc", "@kevinoconnornba"]},
    "sam amick": {"name": "Sam Amick", "outlet": "The Athletic", "tier": 2, "patterns": ["sam amick", "amick:", "@samamick"]},
    "michael scotto": {"name": "Michael Scotto", "outlet": "HoopsHype", "tier": 2, "patterns": ["michael scotto", "scotto:", "@mikescotto"]},
    "alex kennedy": {"name": "Alex Kennedy", "outlet": "HoopsHype", "tier": 2, "patterns": ["alex kennedy", "@alexkennedynba"]},
    "eric pincus": {"name": "Eric Pincus", "outlet": "Bleacher Report", "tier": 2, "patterns": ["eric pincus", "pincus:", "@ericpincus"]},
    "marc spears": {"name": "Marc Spears", "outlet": "Andscape", "tier": 2, "patterns": ["marc spears", "spears:", "@marcjspears"]},
    "tim bontemps": {"name": "Tim Bontemps", "outlet": "ESPN", "tier": 2, "patterns": ["tim bontemps", "bontemps:", "@taborsky"]},
    "zach lowe": {"name": "Zach Lowe", "outlet": "ESPN", "tier": 2, "patterns": ["zach lowe", "@zachlowe_nba"]},
    "tim macmahon": {"name": "Tim MacMahon", "outlet": "ESPN", "tier": 2, "patterns": ["tim macmahon", "macmahon:"]},
    "ramona shelburne": {"name": "Ramona Shelburne", "outlet": "ESPN", "tier": 2, "patterns": ["ramona shelburne", "shelburne:"]},
    "dave mcmenamin": {"name": "Dave McMenamin", "outlet": "ESPN", "tier": 2, "patterns": ["dave mcmenamin", "mcmenamin:"]},
    "chris mannix": {"name": "Chris Mannix", "outlet": "Sports Illustrated", "tier": 2, "patterns": ["chris mannix", "mannix:"]},
    "anthony slater": {"name": "Anthony Slater", "outlet": "The Athletic", "tier": 2, "patterns": ["anthony slater", "slater:"]},
    "john hollinger": {"name": "John Hollinger", "outlet": "The Athletic", "tier": 2, "patterns": ["john hollinger", "hollinger:"]},
    "sam vecenie": {"name": "Sam Vecenie", "outlet": "The Athletic", "tier": 2, "patterns": ["sam vecenie", "vecenie:"]},
    
    # Tier 3 - Beat Writers
    "mark medina": {"name": "Mark Medina", "outlet": "NBA.com", "tier": 3, "patterns": ["mark medina", "medina:", "@markg_medina"]},
    "chris kirschner": {"name": "Chris Kirschner", "outlet": "The Athletic", "tier": 3, "patterns": ["chris kirschner", "kirschner:"]},
    "jon krawczynski": {"name": "Jon Krawczynski", "outlet": "The Athletic", "tier": 3, "patterns": ["jon krawczynski", "krawczynski:"]},
    "jason jones": {"name": "Jason Jones", "outlet": "The Athletic", "tier": 3, "patterns": ["jason jones"]},
    "jake weingarten": {"name": "Jake Weingarten", "outlet": "StockRisers", "tier": 3, "patterns": ["jake weingarten", "@jweingarten"]},
    "evan sidery": {"name": "Evan Sidery", "outlet": "NBA Analysis", "tier": 3, "patterns": ["evan sidery", "@evansidery"]},
    "marc berman": {"name": "Marc Berman", "outlet": "NY Post", "tier": 3, "patterns": ["marc berman", "berman:"]},
    "fred katz": {"name": "Fred Katz", "outlet": "The Athletic", "tier": 3, "patterns": ["fred katz", "katz:"]},
    "kyle neubeck": {"name": "Kyle Neubeck", "outlet": "PhillyVoice", "tier": 3, "patterns": ["kyle neubeck", "neubeck:"]},
    "will guillory": {"name": "Will Guillory", "outlet": "The Athletic", "tier": 3, "patterns": ["will guillory", "guillory:"]},
    "jovan buha": {"name": "Jovan Buha", "outlet": "The Athletic", "tier": 3, "patterns": ["jovan buha", "buha:"]},
    "dan woike": {"name": "Dan Woike", "outlet": "LA Times", "tier": 3, "patterns": ["dan woike", "woike:"]},
    "kurt helin": {"name": "Kurt Helin", "outlet": "NBC Sports", "tier": 3, "patterns": ["kurt helin", "helin:"]},
}

# Topic detection keywords
TOPIC_KEYWORDS = {
    "trade": [
        "trade", "traded", "trading", "deal", "swap", "move", "acquire", "acquisition",
        "package", "destination", "interested in", "pursuing", "target", "on the block",
        "available", "shopping", "exploring trades", "trade talks", "trade discussions"
    ],
    "injury": [
        "injury", "injured", "hurt", "out", "miss", "sidelined", "rehab", "surgery",
        "sprain", "strain", "tear", "fracture", "concussion", "return", "recovery",
        "day-to-day", "questionable", "doubtful", "ruled out", "dnp", "rest"
    ],
    "contract": [
        "contract", "extension", "sign", "signing", "free agent", "free agency",
        "max", "deal", "years", "million", "salary", "option", "decline", "accept",
        "negotiate", "offer", "restricted", "unrestricted", "rfa", "ufa"
    ],
    "frontoffice": [
        "coach", "coaching", "fired", "hire", "gm", "general manager", "president",
        "front office", "executive", "owner", "ownership", "management", "staff",
        "assistant", "interim", "promote", "demote", "search"
    ],
    "draft": [
        "draft", "pick", "lottery", "prospect", "mock", "workout", "combine",
        "rookie", "selection", "projected", "tank", "tanking"
    ]
}


def extract_reporter(text: str, outlet: str = "") -> Optional[Dict]:
    """
    Extract reporter name from rumor text or outlet.
    Returns reporter dict or None if not found.
    """
    text_lower = text.lower()
    outlet_lower = outlet.lower()
    
    # First, check for "Reporter Name:" pattern at the start
    colon_match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*:', text)
    if colon_match:
        potential_name = colon_match.group(1).lower()
        for key, reporter in KNOWN_REPORTERS.items():
            if potential_name in key or key in potential_name:
                return reporter
    
    # Check all known reporter patterns
    for key, reporter in KNOWN_REPORTERS.items():
        for pattern in reporter["patterns"]:
            if pattern in text_lower or pattern in outlet_lower:
                return reporter
    
    # Check outlet field for organization matches
    outlet_mappings = {
        "espn": "ESPN",
        "the athletic": "The Athletic",
        "athletic": "The Athletic", 
        "bleacher report": "Bleacher Report",
        "yahoo": "Yahoo Sports",
        "hoopshype": "HoopsHype",
        "nba.com": "NBA.com",
        "ny post": "NY Post",
        "andscape": "Andscape",
        "the ringer": "The Ringer",
        "si.com": "Sports Illustrated",
        "sports illustrated": "Sports Illustrated",
    }
    
    for pattern, org_name in outlet_mappings.items():
        if pattern in outlet_lower:
            # Return generic outlet entry if no specific reporter found
            return {
                "name": org_name,
                "outlet": org_name,
                "tier": 3,
                "patterns": []
            }
    
    return None


def detect_topic(text: str, tags: List[str] = None) -> str:
    """Detect the primary topic of a rumor."""
    text_lower = text.lower()
    tags_lower = [t.lower() for t in (tags or [])]
    
    scores = defaultdict(int)
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                scores[topic] += 1
            for tag in tags_lower:
                if keyword in tag:
                    scores[topic] += 2  # Tags are more reliable
    
    # Check tags for direct topic matches
    if "trade" in tags_lower or "trades" in tags_lower:
        scores["trade"] += 5
    if "injuries" in tags_lower or "injury" in tags_lower:
        scores["injury"] += 5
    
    if not scores:
        return "general"
    
    return max(scores, key=scores.get)


def extract_players(tags: List[str]) -> List[str]:
    """Extract player names from tags."""
    # Filter out team names and topic tags
    excluded = {
        "trade", "trades", "injuries", "injury", "contract", "free agency",
        "draft", "coaching", "front office", "rumors"
    }
    
    teams = {
        "atlanta hawks", "boston celtics", "brooklyn nets", "charlotte hornets",
        "chicago bulls", "cleveland cavaliers", "dallas mavericks", "denver nuggets",
        "detroit pistons", "golden state warriors", "houston rockets", "indiana pacers",
        "los angeles clippers", "los angeles lakers", "memphis grizzlies", "miami heat",
        "milwaukee bucks", "minnesota timberwolves", "new orleans pelicans", "new york knicks",
        "oklahoma city thunder", "orlando magic", "philadelphia 76ers", "phoenix suns",
        "portland trail blazers", "sacramento kings", "san antonio spurs", "toronto raptors",
        "utah jazz", "washington wizards"
    }
    
    players = []
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower not in excluded and tag_lower not in teams:
            # Check if it looks like a name (has space, proper case in original)
            if " " in tag and tag[0].isupper():
                players.append(tag)
    
    return players


def extract_teams(tags: List[str]) -> List[str]:
    """Extract team names from tags."""
    team_names = {
        "atlanta hawks": "Hawks", "boston celtics": "Celtics", "brooklyn nets": "Nets",
        "charlotte hornets": "Hornets", "chicago bulls": "Bulls", "cleveland cavaliers": "Cavaliers",
        "dallas mavericks": "Mavericks", "denver nuggets": "Nuggets", "detroit pistons": "Pistons",
        "golden state warriors": "Warriors", "houston rockets": "Rockets", "indiana pacers": "Pacers",
        "los angeles clippers": "Clippers", "los angeles lakers": "Lakers", "memphis grizzlies": "Grizzlies",
        "miami heat": "Heat", "milwaukee bucks": "Bucks", "minnesota timberwolves": "Timberwolves",
        "new orleans pelicans": "Pelicans", "new york knicks": "Knicks", "oklahoma city thunder": "Thunder",
        "orlando magic": "Magic", "philadelphia 76ers": "76ers", "phoenix suns": "Suns",
        "portland trail blazers": "Trail Blazers", "sacramento kings": "Kings", "san antonio spurs": "Spurs",
        "toronto raptors": "Raptors", "utah jazz": "Jazz", "washington wizards": "Wizards"
    }
    
    short_names = {v.lower(): v for v in team_names.values()}
    
    teams = []
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in team_names:
            teams.append(team_names[tag_lower])
        elif tag_lower in short_names:
            teams.append(short_names[tag_lower])
    
    return teams


def detect_breaking_news(rumors: List[Dict]) -> Dict[str, List[int]]:
    """
    Detect which rumors were 'breaking news' - first to report a story.
    Groups rumors by player+date and marks the earliest as breaking.
    """
    # Group rumors by player + date
    groups = defaultdict(list)
    
    for i, rumor in enumerate(rumors):
        for player in rumor.get("players", []):
            key = f"{player}:{rumor.get('date', '')}"
            groups[key].append(i)
    
    breaking_indices = set()
    
    for key, indices in groups.items():
        if len(indices) > 1:  # Multiple reports about same player on same day
            # The first one (by archive order, assuming chronological) is breaking
            breaking_indices.add(indices[0])
    
    return breaking_indices


def process_archive(archive_data: List[Dict]) -> Dict:
    """
    Process the full archive and generate reporter statistics.
    
    Args:
        archive_data: List of rumor objects from the archive
        
    Returns:
        Dict with reporters, rumors, and statistics
    """
    processed_rumors = []
    reporter_stats = defaultdict(lambda: {
        "total": 0,
        "by_topic": defaultdict(int),
        "by_player": defaultdict(int),
        "by_team": defaultdict(int),
        "by_date": defaultdict(int),
        "breaking": 0,
        "rumors": []
    })
    
    # First pass: process all rumors
    for i, rumor in enumerate(archive_data):
        text = rumor.get("text", "") or rumor.get("quote", "")
        outlet = rumor.get("outlet", "")
        tags = rumor.get("tags", [])
        date = rumor.get("date", "") or rumor.get("archive_date", "")
        
        # Extract reporter
        reporter = extract_reporter(text, outlet)
        if not reporter:
            continue
            
        reporter_key = reporter["name"].lower().replace(" ", "_")
        
        # Extract metadata
        topic = detect_topic(text, tags)
        players = extract_players(tags)
        teams = extract_teams(tags)
        
        processed_rumor = {
            "id": i,
            "reporter": reporter["name"],
            "reporter_key": reporter_key,
            "outlet": reporter["outlet"],
            "tier": reporter["tier"],
            "date": date,
            "text": text[:300] + "..." if len(text) > 300 else text,
            "topic": topic,
            "players": players,
            "teams": teams,
            "source_url": rumor.get("source_url", ""),
            "is_breaking": False  # Will be updated
        }
        
        processed_rumors.append(processed_rumor)
        
        # Update stats
        stats = reporter_stats[reporter_key]
        stats["name"] = reporter["name"]
        stats["outlet"] = reporter["outlet"]
        stats["tier"] = reporter["tier"]
        stats["total"] += 1
        stats["by_topic"][topic] += 1
        stats["by_date"][date] += 1
        
        for player in players:
            stats["by_player"][player] += 1
        for team in teams:
            stats["by_team"][team] += 1
        
        # Keep recent rumors for display
        if len(stats["rumors"]) < 20:
            stats["rumors"].append(processed_rumor)
    
    # Second pass: detect breaking news
    breaking_indices = detect_breaking_news(processed_rumors)
    for idx in breaking_indices:
        processed_rumors[idx]["is_breaking"] = True
        reporter_key = processed_rumors[idx]["reporter_key"]
        reporter_stats[reporter_key]["breaking"] += 1
    
    # Convert to final format
    reporters = []
    for key, stats in reporter_stats.items():
        reporters.append({
            "id": key,
            "name": stats["name"],
            "outlet": stats["outlet"],
            "tier": stats["tier"],
            "avatar": "".join([n[0] for n in stats["name"].split()[:2]]).upper(),
            "total": stats["total"],
            "breaking": stats["breaking"],
            "by_topic": dict(stats["by_topic"]),
            "by_player": dict(sorted(stats["by_player"].items(), key=lambda x: -x[1])[:20]),
            "by_team": dict(sorted(stats["by_team"].items(), key=lambda x: -x[1])),
            "by_date": dict(stats["by_date"]),
            "recent_rumors": stats["rumors"][:10]
        })
    
    # Sort by total
    reporters.sort(key=lambda x: -x["total"])
    
    return {
        "generated_at": datetime.now().isoformat(),
        "total_rumors": len(processed_rumors),
        "total_reporters": len(reporters),
        "reporters": reporters,
        "rumors": processed_rumors
    }


def generate_js_data(data: Dict, output_path: str = "reporter_data.js"):
    """Generate JavaScript file that can be loaded by the HTML tool."""
    
    js_content = f"""// Reporter Rankings Data
// Generated: {data['generated_at']}
// Total Rumors: {data['total_rumors']}
// Total Reporters: {data['total_reporters']}

const REPORTER_DATA = {json.dumps(data, indent=2)};

// Export for use in HTML
if (typeof window !== 'undefined') {{
    window.REPORTER_DATA = REPORTER_DATA;
}}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Generated {output_path}")
    print(f"  - {data['total_reporters']} reporters")
    print(f"  - {data['total_rumors']} rumors processed")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process HoopsHype Rumors Archive for Reporter Rankings')
    parser.add_argument('input', help='Path to archive JSON file')
    parser.add_argument('-o', '--output', default='reporter_data.js', help='Output JS file path')
    parser.add_argument('--json', action='store_true', help='Also output raw JSON')
    
    args = parser.parse_args()
    
    # Load archive
    print(f"Loading archive from {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        archive = json.load(f)
    
    print(f"Loaded {len(archive)} rumors")
    
    # Process
    print("Processing...")
    data = process_archive(archive)
    
    # Output
    generate_js_data(data, args.output)
    
    if args.json:
        json_path = args.output.replace('.js', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Also saved JSON to {json_path}")
    
    # Print summary
    print("\nTop 10 Reporters by Volume:")
    for i, r in enumerate(data['reporters'][:10], 1):
        print(f"  {i}. {r['name']} ({r['outlet']}) - {r['total']} rumors")


if __name__ == "__main__":
    main()
