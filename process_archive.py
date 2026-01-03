"""
Reporter Rankings Data Processor v3
Extracts reporter statistics from the HoopsHype Rumors Archive.

Changes in v3:
- Separate outlets from reporters
- Resolve unknown Twitter handles
- Better date filtering
- More comprehensive reporter database
"""

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

# =============================================
# COMPREHENSIVE REPORTER DATABASE
# =============================================

REPORTERS_DB = {
    # ===================
    # TIER 1 - Major National Insiders
    # ===================
    "shams charania": {
        "name": "Shams Charania",
        "outlet": "ESPN",
        "tier": 1,
        "handles": ["shaborz", "shamscharania", "shaborz_"],
        "variations": ["shams", "charania"]
    },
    "adrian wojnarowski": {
        "name": "Adrian Wojnarowski",
        "outlet": "ESPN (Retired)",
        "tier": 1,
        "handles": ["wojespn", "wikihoops"],
        "variations": ["woj", "wojnarowski"]
    },
    "marc stein": {
        "name": "Marc Stein",
        "outlet": "The Stein Line",
        "tier": 1,
        "handles": ["thesteinline", "marcstein"],
        "variations": ["stein"]
    },
    "jake fischer": {
        "name": "Jake Fischer",
        "outlet": "Yahoo Sports",
        "tier": 1,
        "handles": ["jakelfischer", "jaborz_nba"],
        "variations": ["fischer"]
    },
    "chris haynes": {
        "name": "Chris Haynes",
        "outlet": "TNT/Bleacher Report",
        "tier": 1,
        "handles": ["chrisbhaynes"],
        "variations": ["haynes"]
    },
    
    # ===================
    # TIER 2 - National Reporters/Analysts
    # ===================
    "brian windhorst": {
        "name": "Brian Windhorst",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["windhorstespn"],
        "variations": ["windhorst"]
    },
    "bobby marks": {
        "name": "Bobby Marks",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["bobbymarks42"],
        "variations": ["marks"]
    },
    "tim bontemps": {
        "name": "Tim Bontemps",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["timbontemps"],
        "variations": ["bontemps"]
    },
    "ramona shelburne": {
        "name": "Ramona Shelburne",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["ramonashelburne"],
        "variations": ["shelburne"]
    },
    "dave mcmenamin": {
        "name": "Dave McMenamin",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["mcaborsky", "davemcmenamin"],
        "variations": ["mcmenamin"]
    },
    "zach lowe": {
        "name": "Zach Lowe",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["zachlowe_nba"],
        "variations": ["lowe"]
    },
    "tim macmahon": {
        "name": "Tim MacMahon",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["espn_macmahon"],
        "variations": ["macmahon"]
    },
    "andrew lopez": {
        "name": "Andrew Lopez",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["_andrew_lopez"],
        "variations": ["lopez"]
    },
    "kendra andrews": {
        "name": "Kendra Andrews",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["kaborz", "kendraandrews"],
        "variations": []
    },
    "ohm youngmisuk": {
        "name": "Ohm Youngmisuk",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["notoriousohm"],
        "variations": ["youngmisuk"]
    },
    "kevin pelton": {
        "name": "Kevin Pelton",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["kpelton"],
        "variations": ["pelton"]
    },
    "baxter holmes": {
        "name": "Baxter Holmes",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["baborz", "baxterholmes"],
        "variations": ["holmes"]
    },
    "michael scotto": {
        "name": "Michael Scotto",
        "outlet": "HoopsHype",
        "tier": 2,
        "handles": ["mikeascotto"],
        "variations": ["scotto"]
    },
    "jorge sierra": {
        "name": "Jorge Sierra",
        "outlet": "HoopsHype",
        "tier": 2,
        "handles": ["hoaborz", "jsiaborz", "jsierra"],
        "variations": ["sierra", "jorge"]
    },
    "alex kennedy": {
        "name": "Alex Kennedy",
        "outlet": "HoopsHype",
        "tier": 2,
        "handles": ["alexkennedynba"],
        "variations": ["kennedy"]
    },
    "sam amick": {
        "name": "Sam Amick",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["sam_amick", "saborz"],
        "variations": ["amick"]
    },
    "john hollinger": {
        "name": "John Hollinger",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["johnhollinger"],
        "variations": ["hollinger"]
    },
    "sam vecenie": {
        "name": "Sam Vecenie",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["samvecenie"],
        "variations": ["vecenie"]
    },
    "anthony slater": {
        "name": "Anthony Slater",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["anthonyslater"],
        "variations": ["slater"]
    },
    "joe vardon": {
        "name": "Joe Vardon",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["joevardon"],
        "variations": ["vardon"]
    },
    "jason jones": {
        "name": "Jason Jones",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["mr_jasonjones"],
        "variations": []
    },
    "david aldridge": {
        "name": "David Aldridge",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["davidaldridgedc"],
        "variations": ["aldridge"]
    },
    "marcus thompson": {
        "name": "Marcus Thompson II",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["thompsonscribe"],
        "variations": []
    },
    "jovan buha": {
        "name": "Jovan Buha",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["jovanbuha"],
        "variations": ["buha"]
    },
    "chris kirschner": {
        "name": "Chris Kirschner",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["chriskirschner"],
        "variations": ["kirschner"]
    },
    "tony jones": {
        "name": "Tony Jones",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["taborz", "taborz_"],
        "variations": []
    },
    "will guillory": {
        "name": "Will Guillory",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["willguillory"],
        "variations": ["guillory"]
    },
    "fred katz": {
        "name": "Fred Katz",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["fredkatz"],
        "variations": ["katz"]
    },
    "mike vorkunov": {
        "name": "Mike Vorkunov",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["mikevorkunov"],
        "variations": ["vorkunov"]
    },
    "darnell mayberry": {
        "name": "Darnell Mayberry",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["darnellmayberry"],
        "variations": ["mayberry"]
    },
    "kevin oconnor": {
        "name": "Kevin O'Connor",
        "outlet": "The Ringer",
        "tier": 2,
        "handles": ["kevinoconnornba"],
        "variations": ["koc", "o'connor", "oconnor"]
    },
    "bill simmons": {
        "name": "Bill Simmons",
        "outlet": "The Ringer",
        "tier": 2,
        "handles": ["billsimmons"],
        "variations": ["simmons"]
    },
    "eric pincus": {
        "name": "Eric Pincus",
        "outlet": "Bleacher Report",
        "tier": 2,
        "handles": ["ericpincus"],
        "variations": ["pincus"]
    },
    "marc spears": {
        "name": "Marc Spears",
        "outlet": "Andscape",
        "tier": 2,
        "handles": ["marcjspears"],
        "variations": ["spears"]
    },
    "dan woike": {
        "name": "Dan Woike",
        "outlet": "LA Times",
        "tier": 2,
        "handles": ["danwoikesports"],
        "variations": ["woike"]
    },
    "brad turner": {
        "name": "Brad Turner",
        "outlet": "LA Times",
        "tier": 2,
        "handles": ["bradturner"],
        "variations": ["turner"]
    },
    "chris mannix": {
        "name": "Chris Mannix",
        "outlet": "Sports Illustrated",
        "tier": 2,
        "handles": ["simannix"],
        "variations": ["mannix"]
    },
    "howard beck": {
        "name": "Howard Beck",
        "outlet": "Sports Illustrated",
        "tier": 2,
        "handles": ["howardbeck"],
        "variations": ["beck"]
    },
    "chris broussard": {
        "name": "Chris Broussard",
        "outlet": "Fox Sports",
        "tier": 2,
        "handles": ["chrisbroussard"],
        "variations": ["broussard"]
    },
    "ric bucher": {
        "name": "Ric Bucher",
        "outlet": "Fox Sports",
        "tier": 2,
        "handles": ["ricbucher"],
        "variations": ["bucher"]
    },
    "kurt helin": {
        "name": "Kurt Helin",
        "outlet": "NBC Sports",
        "tier": 2,
        "handles": ["basketballtalk"],
        "variations": ["helin"]
    },
    "tom haberstroh": {
        "name": "Tom Haberstroh",
        "outlet": "NBC Sports",
        "tier": 2,
        "handles": ["tomhaberstroh"],
        "variations": ["haberstroh"]
    },
    "jon krawczynski": {
        "name": "Jon Krawczynski",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["jonkrawczynski"],
        "variations": ["krawczynski"]
    },
    "james edwards iii": {
        "name": "James Edwards III",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["jedwardsiii"],
        "variations": ["edwards"]
    },
    
    # ===================
    # TIER 3 - Beat Writers & Regional Reporters
    # ===================
    "mark medina": {
        "name": "Mark Medina",
        "outlet": "NBA.com",
        "tier": 3,
        "handles": ["markg_medina"],
        "variations": ["medina"]
    },
    "marc berman": {
        "name": "Marc Berman",
        "outlet": "NY Post",
        "tier": 3,
        "handles": ["nyaborz", "marcberman"],
        "variations": ["berman"]
    },
    "stefan bondy": {
        "name": "Stefan Bondy",
        "outlet": "NY Daily News",
        "tier": 3,
        "handles": ["stefanbondy"],
        "variations": ["bondy"]
    },
    "ian begley": {
        "name": "Ian Begley",
        "outlet": "SNY",
        "tier": 3,
        "handles": ["iaborz", "ianbegley"],
        "variations": ["begley"]
    },
    "kyle neubeck": {
        "name": "Kyle Neubeck",
        "outlet": "PhillyVoice",
        "tier": 3,
        "handles": ["kyleneubeck"],
        "variations": ["neubeck"]
    },
    "keith pompey": {
        "name": "Keith Pompey",
        "outlet": "Philadelphia Inquirer",
        "tier": 3,
        "handles": ["pompeyonsixers"],
        "variations": ["pompey"]
    },
    "derek bodner": {
        "name": "Derek Bodner",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["derekbodnernba"],
        "variations": ["bodner"]
    },
    "monte poole": {
        "name": "Monte Poole",
        "outlet": "NBC Sports Bay Area",
        "tier": 3,
        "handles": ["montepoole"],
        "variations": ["poole"]
    },
    "jason dumas": {
        "name": "Jason Dumas",
        "outlet": "KRON4",
        "tier": 3,
        "handles": ["jaborz_", "jasondumas"],
        "variations": ["dumas"]
    },
    "ira winderman": {
        "name": "Ira Winderman",
        "outlet": "South Florida Sun-Sentinel",
        "tier": 3,
        "handles": ["irawinderman"],
        "variations": ["winderman"]
    },
    "barry jackson": {
        "name": "Barry Jackson",
        "outlet": "Miami Herald",
        "tier": 3,
        "handles": ["flaborzy", "barryjackson"],
        "variations": ["jackson"]
    },
    "anthony chiang": {
        "name": "Anthony Chiang",
        "outlet": "Miami Herald",
        "tier": 3,
        "handles": ["anthonychiang"],
        "variations": ["chiang"]
    },
    "brian lewis": {
        "name": "Brian Lewis",
        "outlet": "NY Post",
        "tier": 3,
        "handles": ["nyaborzy", "brianlewis"],
        "variations": ["lewis"]
    },
    "alex schiffer": {
        "name": "Alex Schiffer",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["alexschiffer"],
        "variations": ["schiffer"]
    },
    "k.c. johnson": {
        "name": "K.C. Johnson",
        "outlet": "NBC Sports Chicago",
        "tier": 3,
        "handles": ["kcjhoop"],
        "variations": ["johnson"]
    },
    "joe cowley": {
        "name": "Joe Cowley",
        "outlet": "Chicago Sun-Times",
        "tier": 3,
        "handles": ["joecowleyhoops"],
        "variations": ["cowley"]
    },
    "eric koreen": {
        "name": "Eric Koreen",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["ekoreen"],
        "variations": ["koreen"]
    },
    "blake murphy": {
        "name": "Blake Murphy",
        "outlet": "Sportsnet",
        "tier": 3,
        "handles": ["blakemurphy7"],
        "variations": ["murphy"]
    },
    "josh lewenberg": {
        "name": "Josh Lewenberg",
        "outlet": "TSN",
        "tier": 3,
        "handles": ["jaborz_", "jlew1050"],
        "variations": ["lewenberg"]
    },
    "rod beard": {
        "name": "Rod Beard",
        "outlet": "Detroit News",
        "tier": 3,
        "handles": ["daborz", "rodbeard"],
        "variations": ["beard"]
    },
    "chris fedor": {
        "name": "Chris Fedor",
        "outlet": "Cleveland.com",
        "tier": 3,
        "handles": ["chrisfedor"],
        "variations": ["fedor"]
    },
    "kelsey russo": {
        "name": "Kelsey Russo",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["kelseyrusso"],
        "variations": ["russo"]
    },
    "eric nehm": {
        "name": "Eric Nehm",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["eric_nehm"],
        "variations": ["nehm"]
    },
    "jim owczarski": {
        "name": "Jim Owczarski",
        "outlet": "Milwaukee Journal Sentinel",
        "tier": 3,
        "handles": ["jaborz", "jimowczarski"],
        "variations": ["owczarski"]
    },
    "dane moore": {
        "name": "Dane Moore",
        "outlet": "SKOR North",
        "tier": 3,
        "handles": ["daborz", "danemoore"],
        "variations": ["moore"]
    },
    "chris hine": {
        "name": "Chris Hine",
        "outlet": "Minneapolis Star Tribune",
        "tier": 3,
        "handles": ["chrishinemn"],
        "variations": ["hine"]
    },
    "drew hill": {
        "name": "Drew Hill",
        "outlet": "Daily Memphian",
        "tier": 3,
        "handles": ["drewhill_dm"],
        "variations": ["hill"]
    },
    "jonathan feigen": {
        "name": "Jonathan Feigen",
        "outlet": "Houston Chronicle",
        "tier": 3,
        "handles": ["jonathan_feigen"],
        "variations": ["feigen"]
    },
    "kelly iko": {
        "name": "Kelly Iko",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["kellyiko"],
        "variations": ["iko"]
    },
    "christian clark": {
        "name": "Christian Clark",
        "outlet": "NOLA.com",
        "tier": 3,
        "handles": ["claborz"],
        "variations": ["clark"]
    },
    "tom orsborn": {
        "name": "Tom Orsborn",
        "outlet": "San Antonio Express-News",
        "tier": 3,
        "handles": ["tom_orsborn"],
        "variations": ["orsborn"]
    },
    "joe mussatto": {
        "name": "Joe Mussatto",
        "outlet": "The Oklahoman",
        "tier": 3,
        "handles": ["joeaborz", "joemussatto"],
        "variations": ["mussatto"]
    },
    "callie caplan": {
        "name": "Callie Caplan",
        "outlet": "Dallas Morning News",
        "tier": 3,
        "handles": ["calliecaplan"],
        "variations": ["caplan"]
    },
    "brad townsend": {
        "name": "Brad Townsend",
        "outlet": "Dallas Morning News",
        "tier": 3,
        "handles": ["townborz", "btownsend"],
        "variations": ["townsend"]
    },
    "kevin chouinard": {
        "name": "Kevin Chouinard",
        "outlet": "Hawks.com",
        "tier": 3,
        "handles": ["kchouinard"],
        "variations": ["chouinard"]
    },
    "sarah spencer": {
        "name": "Sarah Spencer",
        "outlet": "Atlanta Journal-Constitution",
        "tier": 3,
        "handles": ["sarahkspencer"],
        "variations": ["spencer"]
    },
    "rick bonnell": {
        "name": "Rick Bonnell",
        "outlet": "Charlotte Observer",
        "tier": 3,
        "handles": ["rickbonnell"],
        "variations": ["bonnell"]
    },
    "rod boone": {
        "name": "Rod Boone",
        "outlet": "Charlotte Observer",
        "tier": 3,
        "handles": ["rodboone"],
        "variations": ["boone"]
    },
    "chase hughes": {
        "name": "Chase Hughes",
        "outlet": "NBC Sports Washington",
        "tier": 3,
        "handles": ["chaborz", "caborz"],
        "variations": ["hughes"]
    },
    "ava wallace": {
        "name": "Ava Wallace",
        "outlet": "Washington Post",
        "tier": 3,
        "handles": ["avawallace"],
        "variations": ["wallace"]
    },
    "andy larsen": {
        "name": "Andy Larsen",
        "outlet": "Salt Lake Tribune",
        "tier": 3,
        "handles": ["andyaborz", "andylarsen"],
        "variations": ["larsen"]
    },
    "aaron fentress": {
        "name": "Aaron Fentress",
        "outlet": "The Oregonian",
        "tier": 3,
        "handles": ["aaborz", "aaronfentress"],
        "variations": ["fentress"]
    },
    "sean highkin": {
        "name": "Sean Highkin",
        "outlet": "Rose Garden Report",
        "tier": 3,
        "handles": ["seanhighkin"],
        "variations": ["highkin"]
    },
    "brendan vogt": {
        "name": "Brendan Vogt",
        "outlet": "Denver Sports",
        "tier": 3,
        "handles": ["brendanvogt"],
        "variations": ["vogt"]
    },
    "bennett durando": {
        "name": "Bennett Durando",
        "outlet": "Denver Post",
        "tier": 3,
        "handles": ["bennettnba", "bennettdurando"],
        "variations": ["durando"]
    },
    "harrison wind": {
        "name": "Harrison Wind",
        "outlet": "DNVR",
        "tier": 3,
        "handles": ["harrisonwind"],
        "variations": ["wind"]
    },
    "mike singer": {
        "name": "Mike Singer",
        "outlet": "Denver Post",
        "tier": 3,
        "handles": ["msinger"],
        "variations": ["singer"]
    },
    "adam mares": {
        "name": "Adam Mares",
        "outlet": "DNVR",
        "tier": 3,
        "handles": ["adamaborz", "adammares"],
        "variations": ["mares"]
    },
    "stephen a. smith": {
        "name": "Stephen A. Smith",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["stephenasmith"],
        "variations": ["stephen a", "smith"]
    },
    "malika andrews": {
        "name": "Malika Andrews",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["malaborz", "maborz"],
        "variations": ["andrews"]
    },
    "kendrick perkins": {
        "name": "Kendrick Perkins",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["kendrickperkins"],
        "variations": ["perkins"]
    },
    "jonathan givony": {
        "name": "Jonathan Givony",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["draftexpress"],
        "variations": ["givony"]
    },
    "mike schmitz": {
        "name": "Mike Schmitz",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["mike_schmitz"],
        "variations": ["schmitz"]
    },
    "evan sidery": {
        "name": "Evan Sidery",
        "outlet": "Forbes",
        "tier": 3,
        "handles": ["evansidery"],
        "variations": ["sidery"]
    },
    "jake weingarten": {
        "name": "Jake Weingarten",
        "outlet": "StockRisers",
        "tier": 3,
        "handles": ["jweingarten"],
        "variations": ["weingarten"]
    },
    "brett siegel": {
        "name": "Brett Siegel",
        "outlet": "ClutchPoints",
        "tier": 3,
        "handles": ["brettsiegel_"],
        "variations": ["siegel"]
    },
    
    # ===================
    # Additional reporters seen in the data
    # ===================
    "mike curtis": {
        "name": "Mike Curtis",
        "outlet": "Baltimore Sun",
        "tier": 3,
        "handles": ["mikeacurtis2"],
        "variations": ["curtis"]
    },
    "jordan schultz": {
        "name": "Jordan Schultz",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["schulaborz_nba", "schultzreports"],
        "variations": ["schultz"]
    },
    "michael lee": {
        "name": "Michael Lee",
        "outlet": "The Washington Post",
        "tier": 3,
        "handles": ["maborz"],
        "variations": ["lee"]
    },
    "greg swartz": {
        "name": "Greg Swartz",
        "outlet": "Bleacher Report",
        "tier": 3,
        "handles": ["swaborz"],
        "variations": ["swartz"]
    },
    "chris milholen": {
        "name": "Chris Milholen",
        "outlet": "Locked On",
        "tier": 3,
        "handles": ["chrismilaborz"],
        "variations": ["milholen"]
    },
    "greg sylvander": {
        "name": "Greg Sylvander",
        "outlet": "Bally Sports",
        "tier": 3,
        "handles": ["gaborz", "graborz"],
        "variations": ["sylvander"]
    },
    "sam quinn": {
        "name": "Sam Quinn",
        "outlet": "CBS Sports",
        "tier": 3,
        "handles": ["samquinncbs"],
        "variations": ["quinn"]
    },
    "mark murphy": {
        "name": "Mark Murphy",
        "outlet": "Boston Herald",
        "tier": 3,
        "handles": ["muraborz", "muaborz"],
        "variations": []
    },
    "gary washburn": {
        "name": "Gary Washburn",
        "outlet": "Boston Globe",
        "tier": 3,
        "handles": ["gwashburnglobe"],
        "variations": ["washburn"]
    },
    "adam himmelsbach": {
        "name": "Adam Himmelsbach",
        "outlet": "Boston Globe",
        "tier": 3,
        "handles": ["adamhimmelsbach"],
        "variations": ["himmelsbach"]
    },
    "jay king": {
        "name": "Jay King",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["jaykingaborz", "jayking"],
        "variations": ["king"]
    },
    "kyle draper": {
        "name": "Kyle Draper",
        "outlet": "NBC Sports Boston",
        "tier": 3,
        "handles": ["draborz"],
        "variations": ["draper"]
    },
    "chris forsberg": {
        "name": "Chris Forsberg",
        "outlet": "NBC Sports Boston",
        "tier": 3,
        "handles": ["chrisforsberg_"],
        "variations": ["forsberg"]
    },
    "nick friedell": {
        "name": "Nick Friedell",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["nickfriedell"],
        "variations": ["friedell"]
    },
    "kayla johnson": {
        "name": "Kayla Johnson",
        "outlet": "Bleacher Report",
        "tier": 3,
        "handles": ["kaylaborz"],
        "variations": []
    },
    "nick wright": {
        "name": "Nick Wright",
        "outlet": "Fox Sports",
        "tier": 2,
        "handles": ["gaborzy"],
        "variations": ["wright"]
    },
    "vincent goodwill": {
        "name": "Vincent Goodwill",
        "outlet": "Yahoo Sports",
        "tier": 2,
        "handles": ["vaborz", "vincegoodwill"],
        "variations": ["goodwill"]
    },
    "chris herring": {
        "name": "Chris Herring",
        "outlet": "Sports Illustrated",
        "tier": 2,
        "handles": ["chrisaborz", "heraborz"],
        "variations": ["herring"]
    },
    "yaron weitzman": {
        "name": "Yaron Weitzman",
        "outlet": "Fox Sports",
        "tier": 2,
        "handles": ["yaronweitzman"],
        "variations": ["weitzman"]
    },
}

# Known outlets that should NOT be treated as reporters
OUTLET_NAMES = {
    "espn", "the athletic", "bleacher report", "yahoo sports", "nba.com",
    "cbs sports", "fox sports", "nbc sports", "sports illustrated",
    "the ringer", "hoopshype", "usa today", "associated press", "ap",
    "reuters", "new york times", "washington post", "los angeles times",
    "boston globe", "chicago tribune", "miami herald", "dallas morning news",
    "denver post", "philadelphia inquirer", "ny post", "new york post",
    "ny daily news", "san antonio express-news", "houston chronicle",
    "cleveland.com", "detroit news", "detroit free press", "milwaukee journal sentinel",
    "minneapolis star tribune", "salt lake tribune", "the oregonian",
    "sacramento bee", "arizona republic", "atlanta journal-constitution",
    "charlotte observer", "orlando sentinel", "tampa bay times",
    "south florida sun-sentinel", "basketnews", "eurohoops", "sportando",
    "slam", "slam online", "si.com", "youtube", "twitter", "x.com",
    "instagram", "facebook", "tiktok", "reddit", "threads",
    "sny", "tsn", "sportsnet", "msg", "bally sports",
    "nbc sports boston", "nbc sports chicago", "nbc sports philadelphia",
    "nbc sports bay area", "nbc sports washington", "spectrum sportsnet",
    "altitude sports", "bally sports southwest", "bally sports sun",
    "bally sports ohio", "bally sports indiana", "bally sports north",
    "bally sports wisconsin", "bally sports detroit", "bally sports southeast",
    "bally sports oklahoma", "root sports", "at&t sportsnet",
    "the athletic nba", "espn nba", "bleacher report nba"
}

# Build lookup indices
HANDLE_TO_REPORTER = {}
NAME_TO_REPORTER = {}

for key, data in REPORTERS_DB.items():
    NAME_TO_REPORTER[key] = data
    NAME_TO_REPORTER[data["name"].lower()] = data
    for handle in data.get("handles", []):
        HANDLE_TO_REPORTER[handle.lower()] = data


# =============================================
# TOPIC DETECTION
# =============================================

TOPIC_KEYWORDS = {
    "trade": [
        "trade", "traded", "trading", "deal", "swap", "move", "acquire", "acquisition",
        "package", "destination", "interested in", "pursuing", "target", "on the block",
        "available", "shopping", "exploring trades", "trade talks", "trade discussions",
        "trade deadline", "trade market", "trade value", "trade request"
    ],
    "injury": [
        "injury", "injured", "hurt", "out", "miss", "sidelined", "rehab", "surgery",
        "sprain", "strain", "tear", "fracture", "concussion", "return", "recovery",
        "day-to-day", "questionable", "doubtful", "ruled out", "dnp", "rest",
        "load management", "soreness", "inflammation", "ankle", "knee", "hamstring",
        "calf", "shoulder", "back", "hip", "wrist", "foot", "achilles"
    ],
    "contract": [
        "contract", "extension", "sign", "signing", "free agent", "free agency",
        "max", "deal", "years", "million", "salary", "option", "decline", "accept",
        "negotiate", "offer", "restricted", "unrestricted", "rfa", "ufa", "supermax",
        "player option", "team option", "buyout", "waive", "release"
    ],
    "frontoffice": [
        "coach", "coaching", "fired", "hire", "gm", "general manager", "president",
        "front office", "executive", "owner", "ownership", "management", "staff",
        "assistant", "interim", "promote", "search", "candidate", "head coach"
    ],
    "draft": [
        "draft", "pick", "lottery", "prospect", "mock", "workout", "combine",
        "rookie", "selection", "projected", "tank", "tanking", "draft night"
    ]
}


# =============================================
# EXTRACTION FUNCTIONS
# =============================================

def extract_handle_from_url(url: str) -> Optional[str]:
    """Extract Twitter/X handle from source URL."""
    if not url:
        return None
    
    # Match x.com/handle or twitter.com/handle
    match = re.search(r'(?:x\.com|twitter\.com)/([A-Za-z0-9_]+)', url)
    if match:
        handle = match.group(1).lower()
        # Skip common non-user paths
        if handle not in ['status', 'i', 'search', 'hashtag', 'home', 'explore', 'settings', 'messages']:
            return handle
    return None


def is_outlet_name(name: str) -> bool:
    """Check if a name is an outlet rather than a reporter."""
    name_lower = name.lower().strip()
    # Direct match
    if name_lower in OUTLET_NAMES:
        return True
    # Partial match for common patterns
    for outlet in OUTLET_NAMES:
        if outlet in name_lower or name_lower in outlet:
            return True
    return False


def extract_reporter_from_text_start(text: str) -> Optional[Dict]:
    """Extract reporter from 'Name Name:' pattern at start of text."""
    if not text:
        return None
    
    # Pattern: "First Last:" or "First Middle Last:" at the very start
    # Also handles "First Last II:" or "First Last Jr.:"
    match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-zA-Z]+(?:\s+(?:II|III|Jr\.?|Sr\.?))?)\s*:', text)
    if match:
        name = match.group(1).strip()
        name_lower = name.lower()
        
        # Check if this is an outlet, not a reporter
        if is_outlet_name(name_lower):
            return None
            
        # Check if this matches a known reporter
        if name_lower in NAME_TO_REPORTER:
            return NAME_TO_REPORTER[name_lower]
        
        # Try without middle initial
        name_parts = name_lower.split()
        if len(name_parts) >= 2:
            simple_name = f"{name_parts[0]} {name_parts[-1]}"
            if simple_name in NAME_TO_REPORTER:
                return NAME_TO_REPORTER[simple_name]
        
        # Return as a new reporter (will be added dynamically)
        return {
            "name": name,
            "outlet": "Unknown",
            "tier": 3,
            "handles": [],
            "variations": [],
            "_dynamic": True
        }
    
    return None


def extract_reporter_from_text_body(text: str) -> Optional[Dict]:
    """Extract reporter mentioned in text body."""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Patterns to look for
    patterns = [
        r'according to ([a-z]+(?:\s+[a-z]\.?)?\s+[a-z]+)',
        r'per ([a-z]+(?:\s+[a-z]\.?)?\s+[a-z]+)',
        r'([a-z]+\s+[a-z]+) reports that',
        r'([a-z]+\s+[a-z]+) reported that',
        r'([a-z]+\s+[a-z]+) says that',
        r'([a-z]+\s+[a-z]+) said that',
        r'source[s]? told ([a-z]+\s+[a-z]+)',
        r'source[s]? tell ([a-z]+\s+[a-z]+)',
        r'([a-z]+\s+[a-z]+) of espn',
        r'([a-z]+\s+[a-z]+) of the athletic',
        r'([a-z]+\s+[a-z]+) of yahoo',
        r'([a-z]+\s+[a-z]+) of bleacher report',
        r'([a-z]+\s+[a-z]+) of nba\.com',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            potential_name = match.group(1).strip()
            if is_outlet_name(potential_name):
                continue
            if potential_name in NAME_TO_REPORTER:
                return NAME_TO_REPORTER[potential_name]
    
    return None


def extract_reporter(rumor: Dict) -> Tuple[Optional[Dict], str, bool]:
    """
    Extract reporter from a rumor using multiple methods.
    Returns (reporter_dict, detection_method, is_outlet)
    """
    text = rumor.get("text", "") or ""
    source_url = rumor.get("source_url", "") or ""
    outlet = rumor.get("outlet", "") or ""
    
    # Method 1: Check for "Name Name:" at start of text
    reporter = extract_reporter_from_text_start(text)
    if reporter:
        return reporter, "text_start", False
    
    # Method 2: Extract handle from X/Twitter URL
    handle = extract_handle_from_url(source_url)
    if handle:
        if handle in HANDLE_TO_REPORTER:
            return HANDLE_TO_REPORTER[handle], "twitter_handle", False
        else:
            # Unknown handle - create dynamic entry
            return {
                "name": f"@{handle}",
                "outlet": "X/Twitter",
                "tier": 4,
                "handles": [handle],
                "variations": [],
                "_dynamic": True,
                "_handle": handle
            }, "unknown_handle", False
    
    # Method 3: Check for reporter mentioned in text body
    reporter = extract_reporter_from_text_body(text)
    if reporter:
        return reporter, "text_body", False
    
    # Method 4: Fall back to outlet (marked as outlet, not reporter)
    if outlet and outlet.lower() not in ['x.com', 'twitter.com', '']:
        return {
            "name": outlet,
            "outlet": outlet,
            "tier": 5,
            "handles": [],
            "variations": []
        }, "outlet_fallback", True
    
    return None, "none", False


def detect_topic(text: str, tags: List[str] = None) -> str:
    """Detect the primary topic of a rumor."""
    text_lower = (text or "").lower()
    tags_lower = [t.lower() for t in (tags or [])]
    
    scores = defaultdict(int)
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                scores[topic] += 1
            for tag in tags_lower:
                if keyword in tag:
                    scores[topic] += 2
    
    # Check tags for direct topic matches
    if "trade" in tags_lower or "trades" in tags_lower:
        scores["trade"] += 5
    if "injuries" in tags_lower or "injury" in tags_lower:
        scores["injury"] += 5
    if "free agency" in tags_lower:
        scores["contract"] += 5
    if "draft" in tags_lower:
        scores["draft"] += 5
    
    if not scores:
        return "general"
    
    return max(scores, key=scores.get)


def extract_teams(tags: List[str]) -> List[str]:
    """Extract team names from tags."""
    team_mappings = {
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
    
    short_to_full = {v.lower(): v for v in team_mappings.values()}
    
    teams = []
    for tag in (tags or []):
        tag_lower = tag.lower()
        if tag_lower in team_mappings:
            teams.append(team_mappings[tag_lower])
        elif tag_lower in short_to_full:
            teams.append(short_to_full[tag_lower])
    
    return list(set(teams))


def extract_players(tags: List[str]) -> List[str]:
    """Extract player names from tags."""
    excluded = {
        "trade", "trades", "injuries", "injury", "contract", "free agency",
        "draft", "coaching", "front office", "rumors", "nba", "statistics",
        "business", "media", "awards", "all-star"
    }
    
    team_names = {
        "atlanta hawks", "boston celtics", "brooklyn nets", "charlotte hornets",
        "chicago bulls", "cleveland cavaliers", "dallas mavericks", "denver nuggets",
        "detroit pistons", "golden state warriors", "houston rockets", "indiana pacers",
        "los angeles clippers", "los angeles lakers", "memphis grizzlies", "miami heat",
        "milwaukee bucks", "minnesota timberwolves", "new orleans pelicans", "new york knicks",
        "oklahoma city thunder", "orlando magic", "philadelphia 76ers", "phoenix suns",
        "portland trail blazers", "sacramento kings", "san antonio spurs", "toronto raptors",
        "utah jazz", "washington wizards", "hawks", "celtics", "nets", "hornets", "bulls",
        "cavaliers", "mavericks", "nuggets", "pistons", "warriors", "rockets", "pacers",
        "clippers", "lakers", "grizzlies", "heat", "bucks", "timberwolves", "pelicans",
        "knicks", "thunder", "magic", "76ers", "sixers", "suns", "trail blazers", "blazers",
        "kings", "spurs", "raptors", "jazz", "wizards"
    }
    
    players = []
    for tag in (tags or []):
        tag_lower = tag.lower()
        if tag_lower not in excluded and tag_lower not in team_names:
            if " " in tag and tag[0].isupper():
                players.append(tag)
    
    return players


# Agent names for tracking
AGENT_NAMES = {
    "aaron goodwin", "aaron klevan", "aaron mintz", "aaron reilly", "aaron turner",
    "adam godes", "adam pensack", "ademola okulaja", "adie von gontard", "adisa bakari",
    "aj vaynerchuk", "alberto ebanks", "aleksander raskovic", "alex saratsis", "alvaro tor",
    "amandeep dhesi", "andre buck", "andre colona", "andrew hoenig", "andrew lehman",
    "andrew morrison", "andrew vye", "andy bountogianis", "andy miller", "andy shiffman",
    "anthony coleman", "anthony fields", "ara vartanian", "arn tellem", "arturo ortega",
    "arturs kalnitis", "austin brown", "austin eastman", "austin walton", "aviad gronich",
    "aylton tesch", "bj armstrong", "bj bass", "barry bolahood", "bellonora mccallum",
    "ben pensack", "benji burke", "bernie lee", "bill duffy", "bill mccandless",
    "bill neff", "billy ceisler", "billy davis", "bobby petriella", "boris lelchitski",
    "bouna ndiaye", "brad ames", "brandon cavanaugh", "brandon grier", "brandon rosenthal",
    "brian dyke", "brian elfus", "brian jungreis", "buddy baker", "byron irvin",
    "calvin andrews", "cam brennick", "carmen wallace", "cervando tejeda", "chad speck",
    "chafie fields", "charles bonsignore", "charles briscoe", "charles grantham", "charles tucker",
    "chet ervin", "chris emens", "chris gaston", "chris luchey", "chris patrick",
    "chris warren", "christian dawkins", "cody castleman", "colin bryant", "corey barker",
    "corey marcum", "dan brinkley", "dan fegan", "dan tobin", "dana dotson",
    "daniel curtin", "daniel frank", "daniel green", "daniel harrison", "daniel hazan",
    "daniel moldovan", "daniel poneman", "danielle cantor", "danny servick", "darrell comer",
    "darren matsubara", "darren weiner", "dave spahn", "david bauman", "david carro",
    "david falk", "david gasman", "david hamilton", "david mondress",
    "david putterie", "deangelo simmons", "deddrick faison", "deirunas visockas", "derek jackson",
    "derek lafayette", "derek malloy", "derrick powell", "diana day", "diego arguelles",
    "dino pergola", "donald dell", "donte grant", "doug davis", "doug neustadt",
    "drew gross", "duncan lloyd", "dwayne washington", "dwon clifton", "ej kusnyer",
    "eddie grochowiak", "elias sbiet", "emilio duran", "eric fleisher", "erik kabe",
    "erika ruiz", "errol bennett", "fletcher cockrell", "francois nyman", "frank catapano",
    "gary durrant", "geoffrey mcguire", "george bass", "george david", "george langberg",
    "george roussakis", "george sfairopoulos", "gerald collier", "giovanni funiciello",
    "glenn schwartzman", "graham boone", "greer love", "greg lawrence", "gregory nunn",
    "guillermo bermejo", "gustavo monella", "guy zucker", "happy walters", "harrison gaines",
    "henry thomas", "herb rudoy", "hirant manakian", "holger geschwindner", "holman harley",
    "igor crespo", "isaiah garrett", "isiah turner", "jr hensley", "jaafar choufani",
    "james dunleavy", "jamie knox", "jan rohdewald", "janis porzingis", "jared karnes",
    "jared mucha", "jarinn akana", "jason elam", "jason glushon", "jason martin",
    "jason ranne", "javon phillips", "jay baptiste", "jay-z", "jeff austin",
    "jeff fried", "jeff schwartz", "jeff wechsler", "jelani floyd", "jenn carton",
    "jeremiah haylett", "jeremy medjana", "jerome stanley", "jerry dianis", "jerry hicks",
    "jessica holtz", "jim buckley", "jim tanner", "joby branion", "joe abunassar",
    "joe branch", "joe smith", "joel bell", "joel cornette", "joey pennavaria",
    "john baker", "john foster", "john hamilton", "john huizinga", "john noonan",
    "john spencer", "jordan cornish", "jordan gertler", "jose paris ramirez",
    "josh beauregard-bell", "josh goodwin", "josh hairston", "josh ketroser", "joshua ebrahim",
    "juan morrow", "juan perez", "justin haynes", "justin zanik", "kareem memarian",
    "kashif pratt", "keith glass", "keith kreiter", "kenge stevenson", "kenny grant",
    "kevin bradbury", "kevin poston", "kevin t. conner", "kieran piller",
    "kim grillier", "kurt schoeppler", "kyle mcalarney", "lance young", "larry fox",
    "lee melchioni", "leon rose", "lewis tucker", "lorenzo mccloud", "lucas newton",
    "makhtar ndiaye", "marc cornstein", "marc fleisher", "marcus monk", "mark bartelstein",
    "mark bryant", "mark mcneil", "mark termini", "marlon harrison", "matt bollero",
    "matt brown", "matt laczkowski", "matt ranker", "matt ward", "matthew babcock",
    "maurizio balducci", "max ergul", "max lipsett", "maxwell saidman", "maxwell wiepking",
    "mayar zokaei", "melvin booker", "merle scott", "michael harrison", "michael lelchitski",
    "michael siegel", "michael silverman", "michael tellem", "michael whitaker", "mick sandhu",
    "mike george", "mike higgins", "mike hodges", "mike kneisley",
    "mike lindeman", "mike naiditch", "mike simonetta", "mindaugas veromejus",
    "misko raznatovic", "mitch frankel", "mitch nathan", "mitchell butler", "muhammad abdur-rahim",
    "nate daniels", "nathan conley", "nathan pezeshki", "neal rosenshein", "nick blatchford",
    "nick lotsos", "nicolas dos santos", "niko filipovich", "nima namakian", "noah croom",
    "obrad fimic", "odell mccants", "odell witherspoon iii", "olivier mazet", "omar cooper",
    "omar wilkes", "paco lopez", "paolo zamorano", "paul washington", "pedja materic",
    "pedro power", "perry rogers", "phillip parun", "qais haider", "quique villalobos",
    "rade filipovich", "rafael calvo", "ramon sessions", "raymond brothers", "reggie brown",
    "rich beda", "rich kleiman", "rich paul", "richard clarke", "richard felder",
    "richard gray", "richard howell", "richard kaplan", "rishi daulat", "rob pelinka",
    "robert fayne", "rodney blackstock", "roger montgomery", "ronald shade", "ronnie zeidel",
    "roosevelt barnes", "ross aroyo", "ryan davis", "sam goldfeder", "sam permut",
    "sam porter", "sam rose", "sammy wloszczowski", "sarunas broga", "scott alexander",
    "scott nichols", "sead galijasevic", "sean davis", "sean kennedy", "seth cohen",
    "shayaun saee", "shetellia riley irving", "stephen george boykin", "stephen pina",
    "steve haney", "steve heumann", "steve kauffman", "steve mccaskill", "steve mountain",
    "stu lash", "tabetha plummer", "tadas bulotas", "tallen todorovich", "terrance doyle",
    "terrence felder", "thaddeus foucher", "toby bailey", "todd eley", "todd ramasar",
    "todd seidel", "tony dutt", "tony ronzone", "torrell harris", "tracey carney",
    "travis king", "trinity best", "troy payne", "troy thompson", "ty sullivan",
    "tyler glass", "ugo udezue", "wallace prather", "wassim boutanos", "wilmer jackson",
    "yann balikouzou", "zach kurtin", "zach schreiber", "zack charles"
}

def extract_agents(tags: List[str], text: str = "") -> List[str]:
    """Extract agent names from tags and text."""
    agents = []
    
    # Check tags
    for tag in (tags or []):
        tag_lower = tag.lower()
        if tag_lower in AGENT_NAMES:
            agents.append(tag)
    
    # Also check text for agent mentions
    text_lower = (text or "").lower()
    for agent in AGENT_NAMES:
        if agent in text_lower:
            # Capitalize properly
            agents.append(agent.title())
    
    return list(set(agents))


# =============================================
# MAIN PROCESSING
# =============================================

def process_archive(archive_data: List[Dict], days_filter: int = None) -> Dict:
    """
    Process the full archive and generate reporter statistics.
    
    Args:
        archive_data: List of rumor objects
        days_filter: Optional - only include rumors from last N days
    """
    
    # Filter by date if specified
    if days_filter:
        cutoff = (datetime.now() - timedelta(days=days_filter)).strftime('%Y-%m-%d')
        archive_data = [r for r in archive_data if r.get('archive_date', '9999') >= cutoff]
        print(f"Filtered to {len(archive_data)} rumors from last {days_filter} days")
    
    reporter_stats = defaultdict(lambda: {
        "total": 0,
        "by_topic": defaultdict(int),
        "by_player": defaultdict(int),
        "by_team": defaultdict(int),
        "by_agent": defaultdict(int),
        "by_date": defaultdict(int),
        "breaking": 0,
        "detection_methods": defaultdict(int),
        "rumors_by_team": defaultdict(list),
        "rumors_by_player": defaultdict(list),
        "rumors_by_agent": defaultdict(list)
    })
    
    outlet_stats = defaultdict(lambda: {
        "total": 0,
        "by_topic": defaultdict(int),
        "by_date": defaultdict(int)
    })
    
    processed_count = 0
    skipped_count = 0
    method_counts = defaultdict(int)
    unknown_handles = defaultdict(int)
    
    for rumor in archive_data:
        result, method, is_outlet = extract_reporter(rumor)
        
        if not result:
            skipped_count += 1
            continue
        
        processed_count += 1
        method_counts[method] += 1
        
        text = rumor.get("text", "") or ""
        tags = rumor.get("tags", [])
        date = rumor.get("archive_date", "") or rumor.get("date", "")
        topic = detect_topic(text, tags)
        
        if is_outlet:
            # Track outlet separately
            outlet_key = result["name"].lower().replace(" ", "_")
            outlet_stats[outlet_key]["name"] = result["name"]
            outlet_stats[outlet_key]["total"] += 1
            outlet_stats[outlet_key]["by_topic"][topic] += 1
            if date:
                outlet_stats[outlet_key]["by_date"][date] += 1
        else:
            # Track reporter
            reporter_key = result["name"].lower().replace(" ", "_").replace("@", "")
            
            # Track unknown handles
            if method == "unknown_handle":
                handle = result.get("_handle", result["name"])
                unknown_handles[handle] += 1
            
            stats = reporter_stats[reporter_key]
            stats["name"] = result["name"]
            stats["outlet"] = result["outlet"]
            stats["tier"] = result.get("tier", 4)
            stats["total"] += 1
            stats["detection_methods"][method] += 1
            stats["by_topic"][topic] += 1
            
            if date:
                stats["by_date"][date] += 1
            
            for team in extract_teams(tags):
                stats["by_team"][team] += 1
            for player in extract_players(tags):
                stats["by_player"][player] += 1
            for agent in extract_agents(tags, text):
                stats["by_agent"][agent] += 1
            
            # Create rumor object
            rumor_obj = {
                "date": date,
                "text": text[:300] + "..." if len(text) > 300 else text,
                "topic": topic,
                "source_url": rumor.get("source_url", "")
            }
            
            # Store up to 10 rumors per team
            for team in extract_teams(tags):
                if len(stats["rumors_by_team"][team]) < 10:
                    stats["rumors_by_team"][team].append(rumor_obj)
            
            # Store up to 10 rumors per player
            for player in extract_players(tags):
                if len(stats["rumors_by_player"][player]) < 10:
                    stats["rumors_by_player"][player].append(rumor_obj)
            
            # Store up to 10 rumors per agent
            for agent in extract_agents(tags, text):
                if len(stats["rumors_by_agent"][agent]) < 10:
                    stats["rumors_by_agent"][agent].append(rumor_obj)
    
    # Convert reporters to list
    reporters = []
    for key, stats in reporter_stats.items():
        # Convert rumors dicts - only include teams/players/agents that have rumors
        rumors_by_team = {k: v for k, v in stats["rumors_by_team"].items() if v}
        rumors_by_player = {k: v for k, v in stats["rumors_by_player"].items() if v}
        rumors_by_agent = {k: v for k, v in stats["rumors_by_agent"].items() if v}
        
        reporters.append({
            "id": key,
            "name": stats["name"],
            "outlet": stats["outlet"],
            "tier": stats["tier"],
            "avatar": "".join([n[0] for n in stats["name"].replace("@", "").split()[:2]]).upper()[:2] or "??",
            "total": stats["total"],
            "breaking": stats["breaking"],
            "by_topic": dict(stats["by_topic"]),
            "by_player": dict(sorted(stats["by_player"].items(), key=lambda x: -x[1])[:100]),
            "by_team": dict(sorted(stats["by_team"].items(), key=lambda x: -x[1])),
            "by_agent": dict(sorted(stats["by_agent"].items(), key=lambda x: -x[1])[:50]),
            "by_date": dict(stats["by_date"]),
            "detection_methods": dict(stats["detection_methods"]),
            "rumors_by_team": rumors_by_team,
            "rumors_by_player": rumors_by_player,
            "rumors_by_agent": rumors_by_agent
        })
    
    # Convert outlets to list
    outlets = []
    for key, stats in outlet_stats.items():
        outlets.append({
            "id": key,
            "name": stats["name"],
            "total": stats["total"],
            "by_topic": dict(stats["by_topic"]),
            "by_date": dict(stats["by_date"])
        })
    
    # Sort by total
    reporters.sort(key=lambda x: -x["total"])
    outlets.sort(key=lambda x: -x["total"])
    
    print(f"\n=== Processing Summary ===")
    print(f"Total rumors: {len(archive_data)}")
    print(f"Processed: {processed_count}")
    print(f"Skipped (no reporter): {skipped_count}")
    print(f"Reporters found: {len(reporters)}")
    print(f"Outlets found: {len(outlets)}")
    print(f"\nDetection methods:")
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        print(f"  {method}: {count}")
    
    if unknown_handles:
        print(f"\n=== Top 20 Unknown Twitter Handles ===")
        print("(Add these to REPORTERS_DB for better attribution)")
        for handle, count in sorted(unknown_handles.items(), key=lambda x: -x[1])[:20]:
            print(f"  @{handle}: {count}")
    
    return {
        "generated_at": datetime.now().isoformat(),
        "total_rumors": len(archive_data),
        "processed_rumors": processed_count,
        "total_reporters": len(reporters),
        "total_outlets": len(outlets),
        "detection_methods": dict(method_counts),
        "reporters": reporters,
        "outlets": outlets,
        "unknown_handles": dict(sorted(unknown_handles.items(), key=lambda x: -x[1])[:50])
    }


def generate_js_data(data: Dict, output_path: str = "reporter_data.js"):
    """Generate JavaScript file for the HTML tool."""
    
    js_content = f"""// Reporter Rankings Data
// Generated: {data['generated_at']}
// Total Rumors: {data['total_rumors']}
// Processed: {data['processed_rumors']}
// Total Reporters: {data['total_reporters']}
// Total Outlets: {data['total_outlets']}

const REPORTER_DATA = {json.dumps(data, indent=2)};

// Export for use in HTML
if (typeof window !== 'undefined') {{
    window.REPORTER_DATA = REPORTER_DATA;
}}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\nGenerated {output_path}")
    print(f"  - {data['total_reporters']} reporters")
    print(f"  - {data['total_outlets']} outlets")
    print(f"  - {data['processed_rumors']} rumors attributed")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process HoopsHype Rumors Archive for Reporter Rankings')
    parser.add_argument('input', help='Path to archive JSON file')
    parser.add_argument('-o', '--output', default='reporter_data.js', help='Output JS file path')
    parser.add_argument('--json', action='store_true', help='Also output raw JSON')
    parser.add_argument('--days', type=int, default=None, help='Only include rumors from last N days')
    
    args = parser.parse_args()
    
    # Load archive
    print(f"Loading archive from {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        archive = json.load(f)
    
    print(f"Loaded {len(archive)} rumors")
    
    # Process
    print("Processing...")
    data = process_archive(archive, days_filter=args.days)
    
    # Output
    generate_js_data(data, args.output)
    
    if args.json:
        json_path = args.output.replace('.js', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Also saved JSON to {json_path}")
    
    # Print top reporters
    print("\n=== Top 20 Reporters by Volume ===")
    for i, r in enumerate(data['reporters'][:20], 1):
        methods = r.get('detection_methods', {})
        method_str = ", ".join([f"{k}:{v}" for k, v in methods.items()])
        print(f"  {i:2}. {r['name']:25} ({r['outlet']:20}) - {r['total']:4} rumors [{method_str}]")
    
    print("\n=== Top 10 Outlets by Volume ===")
    for i, o in enumerate(data['outlets'][:10], 1):
        print(f"  {i:2}. {o['name']:30} - {o['total']:4} rumors")


if __name__ == "__main__":
    main()
