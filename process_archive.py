"""
Reporter Rankings Data Processor v2
Extracts reporter statistics from the HoopsHype Rumors Archive.

Detection methods:
1. "Reporter Name:" pattern at start of text
2. Twitter/X handle extraction from source_url
3. Mid-text mentions ("According to Reporter Name", "per Reporter Name")
4. Fallback to outlet name
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
        "handles": ["shaborz", "shaborz_", "shamscharania"],
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
        "handles": ["jakelfischer", "jfischer"],
        "variations": ["fischer"]
    },
    "chris haynes": {
        "name": "Chris Haynes",
        "outlet": "Bleacher Report",
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
        "handles": ["kaborz"],
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
        "handles": ["baborz"],
        "variations": ["holmes"]
    },
    "michael scotto": {
        "name": "Michael Scotto",
        "outlet": "HoopsHype",
        "tier": 2,
        "handles": ["mikeascotto"],
        "variations": ["scotto"]
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
        "handles": ["sam_amick"],
        "variations": ["amick"]
    },
    "shams charania athletic": {
        "name": "Shams Charania",
        "outlet": "ESPN",
        "tier": 1,
        "handles": [],
        "variations": []
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
        "name": "Marcus Thompson",
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
    "jake storm": {
        "name": "Jake Storm",
        "outlet": "Bleacher Report",
        "tier": 2,
        "handles": ["jakestorm99"],
        "variations": []
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
    "nick wright": {
        "name": "Nick Wright",
        "outlet": "Fox Sports",
        "tier": 2,
        "handles": ["gaborzy"],
        "variations": ["wright"]
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
    "steve bulpett": {
        "name": "Steve Bulpett",
        "outlet": "Heavy.com",
        "tier": 2,
        "handles": ["stevebhoop"],
        "variations": ["bulpett"]
    },
    "sean highkin": {
        "name": "Sean Highkin",
        "outlet": "Rose Garden Report",
        "tier": 2,
        "handles": ["seanhighkin"],
        "variations": ["highkin"]
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
        "handles": ["jaborz"],
        "variations": ["edwards"]
    },
    "kellan olson": {
        "name": "Kellan Olson",
        "outlet": "Arizona Sports",
        "tier": 2,
        "handles": ["kellanolson"],
        "variations": ["olson"]
    },
    "duane rankin": {
        "name": "Duane Rankin",
        "outlet": "Arizona Republic",
        "tier": 2,
        "handles": ["duaborz"],
        "variations": ["rankin"]
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
    "john gambadoro": {
        "name": "John Gambadoro",
        "outlet": "Arizona Sports",
        "tier": 3,
        "handles": ["gamaborz"],
        "variations": ["gambadoro"]
    },
    "marc berman": {
        "name": "Marc Berman",
        "outlet": "NY Post",
        "tier": 3,
        "handles": ["nyaborz"],
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
        "handles": ["iaborz"],
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
    "dave early": {
        "name": "Dave Early",
        "outlet": "NBC Sports Bay Area",
        "tier": 3,
        "handles": ["daveearlynba"],
        "variations": ["early"]
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
        "handles": ["jdaborz"],
        "variations": ["dumas"]
    },
    "chris biderman": {
        "name": "Chris Biderman",
        "outlet": "Sacramento Bee",
        "tier": 3,
        "handles": ["chrisaborz"],
        "variations": ["biderman"]
    },
    "james ham": {
        "name": "James Ham",
        "outlet": "ESPN 1320",
        "tier": 3,
        "handles": ["jaborz_"],
        "variations": ["ham"]
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
        "handles": ["barryaborz"],
        "variations": ["jackson"]
    },
    "anthony chiang": {
        "name": "Anthony Chiang",
        "outlet": "Miami Herald",
        "tier": 3,
        "handles": ["anthonychiang"],
        "variations": ["chiang"]
    },
    "greg sylvander": {
        "name": "Greg Sylvander",
        "outlet": "Bally Sports Florida",
        "tier": 3,
        "handles": ["gregaborz"],
        "variations": ["sylvander"]
    },
    "greg logan": {
        "name": "Greg Logan",
        "outlet": "Newsday",
        "tier": 3,
        "handles": ["greglogannyaaa"],
        "variations": ["logan"]
    },
    "brian lewis": {
        "name": "Brian Lewis",
        "outlet": "NY Post",
        "tier": 3,
        "handles": ["nyaborzy"],
        "variations": ["lewis"]
    },
    "alex schiffer": {
        "name": "Alex Schiffer",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["alexschiffer"],
        "variations": ["schiffer"]
    },
    "kristian winfield": {
        "name": "Kristian Winfield",
        "outlet": "NY Daily News",
        "tier": 3,
        "handles": ["kaborz"],
        "variations": ["winfield"]
    },
    "k.c. johnson": {
        "name": "K.C. Johnson",
        "outlet": "NBC Sports Chicago",
        "tier": 3,
        "handles": ["kcjhoop"],
        "variations": ["johnson"]
    },
    "rob schaefer": {
        "name": "Rob Schaefer",
        "outlet": "NBC Sports Chicago",
        "tier": 3,
        "handles": ["robaborz"],
        "variations": ["schaefer"]
    },
    "joe cowley": {
        "name": "Joe Cowley",
        "outlet": "Chicago Sun-Times",
        "tier": 3,
        "handles": ["joecowleyhoops"],
        "variations": ["cowley"]
    },
    "darnell mayberry": {
        "name": "Darnell Mayberry",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["daborz"],
        "variations": ["mayberry"]
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
        "handles": ["jaborz_"],
        "variations": ["lewenberg"]
    },
    "rod beard": {
        "name": "Rod Beard",
        "outlet": "Detroit News",
        "tier": 3,
        "handles": ["daborz"],
        "variations": ["beard"]
    },
    "omari sankofa ii": {
        "name": "Omari Sankofa II",
        "outlet": "Detroit Free Press",
        "tier": 3,
        "handles": ["osankofa"],
        "variations": ["sankofa"]
    },
    "chris fedor": {
        "name": "Chris Fedor",
        "outlet": "Cleveland.com",
        "tier": 3,
        "handles": ["chrisaborz"],
        "variations": ["fedor"]
    },
    "kelsey russo": {
        "name": "Kelsey Russo",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["kelseyrusso"],
        "variations": ["russo"]
    },
    "evan dammarell": {
        "name": "Evan Dammarell",
        "outlet": "Right Down Euclid",
        "tier": 3,
        "handles": ["evandaborz"],
        "variations": ["dammarell"]
    },
    "cayleigh griffin": {
        "name": "Cayleigh Griffin",
        "outlet": "Bally Sports Indiana",
        "tier": 3,
        "handles": ["cayleighgriffin"],
        "variations": ["griffin"]
    },
    "scott agness": {
        "name": "Scott Agness",
        "outlet": "Fieldhouse Files",
        "tier": 3,
        "handles": ["scottaborz"],
        "variations": ["agness"]
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
        "handles": ["jimaborz"],
        "variations": ["owczarski"]
    },
    "dane moore": {
        "name": "Dane Moore",
        "outlet": "SKOR North",
        "tier": 3,
        "handles": ["daborz"],
        "variations": ["moore"]
    },
    "chris hine": {
        "name": "Chris Hine",
        "outlet": "Minneapolis Star Tribune",
        "tier": 3,
        "handles": ["chrisaborz"],
        "variations": ["hine"]
    },
    "drew hill": {
        "name": "Drew Hill",
        "outlet": "Daily Memphian",
        "tier": 3,
        "handles": ["drewaborz"],
        "variations": ["hill"]
    },
    "damichael cole": {
        "name": "Damichael Cole",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["damaborz"],
        "variations": ["cole"]
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
    "alykhan bijani": {
        "name": "Alykhan Bijani",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["alaborz"],
        "variations": ["bijani"]
    },
    "christian clark": {
        "name": "Christian Clark",
        "outlet": "NOLA.com",
        "tier": 3,
        "handles": ["christaborz"],
        "variations": ["clark"]
    },
    "oleh kosel": {
        "name": "Oleh Kosel",
        "outlet": "Pelican Debrief",
        "tier": 3,
        "handles": ["olehaborz"],
        "variations": ["kosel"]
    },
    "paul garcia": {
        "name": "Paul Garcia",
        "outlet": "Project Spurs",
        "tier": 3,
        "handles": ["paulaborz"],
        "variations": ["garcia"]
    },
    "tom orsborn": {
        "name": "Tom Orsborn",
        "outlet": "San Antonio Express-News",
        "tier": 3,
        "handles": ["tom_orsborn"],
        "variations": ["orsborn"]
    },
    "jeff garcia": {
        "name": "Jeff Garcia",
        "outlet": "KENS5",
        "tier": 3,
        "handles": ["jeffgarcia"],
        "variations": []
    },
    "maddie lee": {
        "name": "Maddie Lee",
        "outlet": "The Oklahoman",
        "tier": 3,
        "handles": ["maborz"],
        "variations": ["lee"]
    },
    "joe mussatto": {
        "name": "Joe Mussatto",
        "outlet": "The Oklahoman",
        "tier": 3,
        "handles": ["jaborz"],
        "variations": ["mussatto"]
    },
    "jamie hudson": {
        "name": "Jamie Hudson",
        "outlet": "Bally Sports Southwest",
        "tier": 3,
        "handles": ["jamieaborz"],
        "variations": ["hudson"]
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
        "handles": ["btownaborz"],
        "variations": ["townsend"]
    },
    "khobi price": {
        "name": "Khobi Price",
        "outlet": "Orlando Sentinel",
        "tier": 3,
        "handles": ["khobiprice"],
        "variations": ["price"]
    },
    "cody taylor": {
        "name": "Cody Taylor",
        "outlet": "Locked On Magic",
        "tier": 3,
        "handles": ["codyaborz"],
        "variations": ["taylor"]
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
    "lauren l. williams": {
        "name": "Lauren L. Williams",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["laurenaborz"],
        "variations": ["williams"]
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
        "handles": ["caborz"],
        "variations": ["hughes"]
    },
    "quinton mayo": {
        "name": "Quinton Mayo",
        "outlet": "NBC Sports Washington",
        "tier": 3,
        "handles": ["qaborz"],
        "variations": ["mayo"]
    },
    "ava wallace": {
        "name": "Ava Wallace",
        "outlet": "Washington Post",
        "tier": 3,
        "handles": ["avawallace"],
        "variations": ["wallace"]
    },
    "josh robbins": {
        "name": "Josh Robbins",
        "outlet": "The Athletic",
        "tier": 3,
        "handles": ["joshuabrobbing"],
        "variations": ["robbins"]
    },
    "ben anderson": {
        "name": "Ben Anderson",
        "outlet": "KSL",
        "tier": 3,
        "handles": ["benaborz"],
        "variations": ["anderson"]
    },
    "andy larsen": {
        "name": "Andy Larsen",
        "outlet": "Salt Lake Tribune",
        "tier": 3,
        "handles": ["andyaborz"],
        "variations": ["larsen"]
    },
    "casey holdahl": {
        "name": "Casey Holdahl",
        "outlet": "Blazers.com",
        "tier": 3,
        "handles": ["choldahl"],
        "variations": ["holdahl"]
    },
    "aaron fentress": {
        "name": "Aaron Fentress",
        "outlet": "The Oregonian",
        "tier": 3,
        "handles": ["aaborz"],
        "variations": ["fentress"]
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
        "handles": ["bennettnba"],
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
        "handles": ["adamaborz"],
        "variations": ["mares"]
    },
    
    # ===================
    # Additional well-known reporters
    # ===================
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
        "handles": ["malaborz"],
        "variations": ["andrews"]
    },
    "kendrick perkins": {
        "name": "Kendrick Perkins",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["kendrickperkins"],
        "variations": ["perkins"]
    },
    "richard jefferson": {
        "name": "Richard Jefferson",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["richardjefferson"],
        "variations": ["jefferson"]
    },
    "jj redick": {
        "name": "JJ Redick",
        "outlet": "ESPN",
        "tier": 2,
        "handles": ["jaborz"],
        "variations": ["redick"]
    },
    "seth partnow": {
        "name": "Seth Partnow",
        "outlet": "The Athletic",
        "tier": 2,
        "handles": ["sethpartnow"],
        "variations": ["partnow"]
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
    "jeremy woo": {
        "name": "Jeremy Woo",
        "outlet": "Sports Illustrated",
        "tier": 2,
        "handles": ["jeremywoo"],
        "variations": ["woo"]
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
        "handles": ["baborz"],
        "variations": ["siegel"]
    },
    "chris sheridan": {
        "name": "Chris Sheridan",
        "outlet": "SheridanHoops",
        "tier": 3,
        "handles": ["sheaborz"],
        "variations": ["sheridan"]
    },
    "marc j. spears": {
        "name": "Marc Spears",
        "outlet": "Andscape",
        "tier": 2,
        "handles": ["marcjspears"],
        "variations": ["spears"]
    },
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
        "load management", "soreness", "inflammation"
    ],
    "contract": [
        "contract", "extension", "sign", "signing", "free agent", "free agency",
        "max", "deal", "years", "million", "salary", "option", "decline", "accept",
        "negotiate", "offer", "restricted", "unrestricted", "rfa", "ufa", "supermax",
        "player option", "team option", "buyout"
    ],
    "frontoffice": [
        "coach", "coaching", "fired", "hire", "gm", "general manager", "president",
        "front office", "executive", "owner", "ownership", "management", "staff",
        "assistant", "interim", "promote", "search", "candidate"
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
        if handle not in ['status', 'i', 'search', 'hashtag', 'home', 'explore']:
            return handle
    return None


def extract_reporter_from_text_start(text: str) -> Optional[Dict]:
    """Extract reporter from 'Name Name:' pattern at start of text."""
    if not text:
        return None
    
    # Pattern: "First Last:" or "First Middle Last:" at the very start
    match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+(?:\s+[A-Z]+)?)\s*:', text)
    if match:
        name = match.group(1).strip().lower()
        # Check if this matches a known reporter
        if name in NAME_TO_REPORTER:
            return NAME_TO_REPORTER[name]
        # Try without middle initial
        name_parts = name.split()
        if len(name_parts) >= 2:
            simple_name = f"{name_parts[0]} {name_parts[-1]}"
            if simple_name in NAME_TO_REPORTER:
                return NAME_TO_REPORTER[simple_name]
    
    return None


def extract_reporter_from_text_body(text: str) -> Optional[Dict]:
    """Extract reporter mentioned in text body."""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Patterns to look for
    patterns = [
        r'according to ([a-z]+ [a-z]+)',
        r'per ([a-z]+ [a-z]+)',
        r'([a-z]+ [a-z]+) reports',
        r'([a-z]+ [a-z]+) reported',
        r'([a-z]+ [a-z]+) says',
        r'([a-z]+ [a-z]+) said',
        r'source[s]? told ([a-z]+ [a-z]+)',
        r'([a-z]+ [a-z]+) of espn',
        r'([a-z]+ [a-z]+) of the athletic',
        r'([a-z]+ [a-z]+) of yahoo',
        r'([a-z]+ [a-z]+) of bleacher report',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            potential_name = match.group(1).strip()
            if potential_name in NAME_TO_REPORTER:
                return NAME_TO_REPORTER[potential_name]
    
    return None


def extract_reporter(rumor: Dict) -> Tuple[Optional[Dict], str]:
    """
    Extract reporter from a rumor using multiple methods.
    Returns (reporter_dict, detection_method)
    """
    text = rumor.get("text", "") or ""
    source_url = rumor.get("source_url", "") or ""
    outlet = rumor.get("outlet", "") or ""
    
    # Method 1: Check for "Name Name:" at start of text
    reporter = extract_reporter_from_text_start(text)
    if reporter:
        return reporter, "text_start"
    
    # Method 2: Extract handle from X/Twitter URL
    handle = extract_handle_from_url(source_url)
    if handle and handle in HANDLE_TO_REPORTER:
        return HANDLE_TO_REPORTER[handle], "twitter_handle"
    
    # Method 3: Check for reporter mentioned in text body
    reporter = extract_reporter_from_text_body(text)
    if reporter:
        return reporter, "text_body"
    
    # Method 4: If we found a handle but don't have it mapped, create entry
    if handle:
        # Create a new entry for unknown handle
        return {
            "name": f"@{handle}",
            "outlet": "X/Twitter",
            "tier": 3,
            "handles": [handle],
            "variations": []
        }, "unknown_handle"
    
    # Method 5: Fall back to outlet
    if outlet and outlet.lower() not in ['x.com', 'twitter.com', '']:
        return {
            "name": outlet,
            "outlet": outlet,
            "tier": 4,
            "handles": [],
            "variations": []
        }, "outlet_fallback"
    
    return None, "none"


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
        "draft", "coaching", "front office", "rumors", "nba", "statistics"
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


# =============================================
# MAIN PROCESSING
# =============================================

def process_archive(archive_data: List[Dict]) -> Dict:
    """Process the full archive and generate reporter statistics."""
    
    reporter_stats = defaultdict(lambda: {
        "total": 0,
        "by_topic": defaultdict(int),
        "by_player": defaultdict(int),
        "by_team": defaultdict(int),
        "by_date": defaultdict(int),
        "breaking": 0,
        "detection_methods": defaultdict(int),
        "rumors": []
    })
    
    processed_count = 0
    skipped_count = 0
    method_counts = defaultdict(int)
    
    for rumor in archive_data:
        reporter, method = extract_reporter(rumor)
        
        if not reporter:
            skipped_count += 1
            continue
        
        processed_count += 1
        method_counts[method] += 1
        
        reporter_key = reporter["name"].lower().replace(" ", "_").replace("@", "")
        text = rumor.get("text", "") or ""
        tags = rumor.get("tags", [])
        date = rumor.get("date", "") or rumor.get("archive_date", "")
        
        # Update stats
        stats = reporter_stats[reporter_key]
        stats["name"] = reporter["name"]
        stats["outlet"] = reporter["outlet"]
        stats["tier"] = reporter.get("tier", 4)
        stats["total"] += 1
        stats["detection_methods"][method] += 1
        
        # Topic
        topic = detect_topic(text, tags)
        stats["by_topic"][topic] += 1
        
        # Date
        if date:
            stats["by_date"][date] += 1
        
        # Teams and players
        for team in extract_teams(tags):
            stats["by_team"][team] += 1
        for player in extract_players(tags):
            stats["by_player"][player] += 1
        
        # Keep sample rumors
        if len(stats["rumors"]) < 20:
            stats["rumors"].append({
                "date": date,
                "text": text[:300] + "..." if len(text) > 300 else text,
                "topic": topic,
                "teams": extract_teams(tags),
                "players": extract_players(tags)[:5],
                "source_url": rumor.get("source_url", "")
            })
    
    # Convert to final format
    reporters = []
    for key, stats in reporter_stats.items():
        reporters.append({
            "id": key,
            "name": stats["name"],
            "outlet": stats["outlet"],
            "tier": stats["tier"],
            "avatar": "".join([n[0] for n in stats["name"].replace("@", "").split()[:2]]).upper()[:2] or "??",
            "total": stats["total"],
            "breaking": stats["breaking"],
            "by_topic": dict(stats["by_topic"]),
            "by_player": dict(sorted(stats["by_player"].items(), key=lambda x: -x[1])[:20]),
            "by_team": dict(sorted(stats["by_team"].items(), key=lambda x: -x[1])),
            "by_date": dict(stats["by_date"]),
            "detection_methods": dict(stats["detection_methods"]),
            "recent_rumors": stats["rumors"][:10]
        })
    
    # Sort by total
    reporters.sort(key=lambda x: -x["total"])
    
    print(f"\n=== Processing Summary ===")
    print(f"Total rumors: {len(archive_data)}")
    print(f"Processed: {processed_count}")
    print(f"Skipped (no reporter): {skipped_count}")
    print(f"\nDetection methods:")
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        print(f"  {method}: {count}")
    
    return {
        "generated_at": datetime.now().isoformat(),
        "total_rumors": len(archive_data),
        "processed_rumors": processed_count,
        "total_reporters": len(reporters),
        "detection_methods": dict(method_counts),
        "reporters": reporters
    }


def generate_js_data(data: Dict, output_path: str = "reporter_data.js"):
    """Generate JavaScript file for the HTML tool."""
    
    js_content = f"""// Reporter Rankings Data
// Generated: {data['generated_at']}
// Total Rumors: {data['total_rumors']}
// Processed: {data['processed_rumors']}
// Total Reporters: {data['total_reporters']}

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
    print(f"  - {data['processed_rumors']} rumors attributed")


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
    
    # Print top reporters
    print("\n=== Top 20 Reporters by Volume ===")
    for i, r in enumerate(data['reporters'][:20], 1):
        methods = r.get('detection_methods', {})
        method_str = ", ".join([f"{k}:{v}" for k, v in methods.items()])
        print(f"  {i:2}. {r['name']:25} ({r['outlet']:20}) - {r['total']:4} rumors [{method_str}]")


if __name__ == "__main__":
    main()
