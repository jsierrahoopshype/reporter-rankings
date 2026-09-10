#!/usr/bin/env python3
"""
reporter_rankings_build.py — incremental builder for the NBA Reporter Rankings tool.

Replaces the old "download raw JSON files from the hoopshype-rumors repo" step,
which has been dead since those files stopped being committed.

How it works
------------
  * Pulls the archive from the hoopshype-rumors-api Cloudflare Worker,
    authenticated with the HH_API_KEY environment variable.
  * Parts 1..N-1 never change. Their aggregates are computed once and stored in
    agg/part_N.json (counts only, tiny). Only the newest part is re-downloaded
    on every run, so a normal run pulls ~70MB instead of ~435MB.
  * Raw rumor JSON goes to a scratch dir and is deleted. It is never committed,
    never cached, never published.
  * The published reporter_data.js holds counts only: no rumor text, no source
    URLs, no quotes. Nothing from the archive itself leaves the runner.
  * All reporter detection and name/outlet curation is imported from
    process_archive.py, which is not modified.

Usage
-----
  python reporter_rankings_build.py                  # normal incremental build
  python reporter_rankings_build.py --rebuild-all    # ignore agg/, redo every part
  python reporter_rankings_build.py --force          # skip the sanity guard
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from collections import defaultdict
from datetime import datetime

import requests

# Reuse every bit of the existing detection/curation logic. process_archive.py
# stays untouched — this script only imports from it.
from process_archive import (
    extract_reporter,
    detect_topic,
    extract_teams,
    extract_players,
    extract_agents,
)

API_BASE = "https://hoopshype-rumors-api.thejorgesierra.workers.dev"
ALLOWED_REFERER = "https://jsierrahoopshype.github.io/hoopshype-rumors/hoopshype_rumors_tool.html"
ALLOWED_ORIGIN = "https://jsierrahoopshype.github.io"

AGG_DIR = "agg"
OUTPUT_JS = "reporter_data.js"

# Abort rather than publish if the new build loses more than this share of the
# previous build's volume. This is the guard that was missing: the old workflow
# happily committed an empty file 4x a day for months.
MIN_RATIO = 0.90


def api_headers():
    key = os.environ.get("HH_API_KEY", "").strip()
    if not key:
        sys.exit(
            "ERROR: HH_API_KEY is not set.\n"
            "In GitHub Actions, add it under Settings > Secrets and variables > Actions."
        )
    return {
        "X-API-Key": key,
        # Belt and braces: the Worker accepts either the key or an allowlisted
        # origin/referer, and the allowlist rules have changed once already.
        "Referer": ALLOWED_REFERER,
        "Origin": ALLOWED_ORIGIN,
        "User-Agent": "reporter-rankings-build/1.0",
    }


def fetch_json(url, dest_path=None):
    """GET a JSON endpoint. Streams to disk first when dest_path is given, so a
    70MB part never sits in memory twice."""
    r = requests.get(url, headers=api_headers(), stream=bool(dest_path), timeout=300)
    if r.status_code != 200:
        sys.exit(f"ERROR: {url} returned HTTP {r.status_code}")
    if not dest_path:
        return r.json()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    with open(dest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def part_count():
    """Read /api/rumors/index and work out how many parts exist. The index shape
    has changed before, so accept the obvious variants."""
    data = fetch_json(f"{API_BASE}/api/rumors/index")

    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for key in ("parts", "files", "chunks"):
            val = data.get(key)
            if isinstance(val, list):
                return len(val)
            if isinstance(val, int):
                return val
        for key in ("total_parts", "part_count", "num_parts", "count"):
            if isinstance(data.get(key), int):
                return data[key]
    sys.exit(f"ERROR: could not read a part count from /api/rumors/index: {list(data)[:10]}")


def rumors_from_payload(payload):
    """A part endpoint may return a bare list or an object wrapping one."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("rumors", "data", "items", "results"):
            if isinstance(payload.get(key), list):
                return payload[key]
    sys.exit("ERROR: part payload did not contain a list of rumors")


def aggregate(rumors):
    """Turn a list of rumor records into counts. Returns a plain, mergeable dict.
    Nothing here retains rumor text, quotes or URLs."""
    reporters = defaultdict(lambda: {
        "name": "",
        "outlet": "",
        "tier": 4,
        "total": 0,
        "by_topic": defaultdict(int),
        "by_player": defaultdict(int),
        "by_team": defaultdict(int),
        "by_agent": defaultdict(int),
        "by_date": defaultdict(int),
        "detection_methods": defaultdict(int),
    })
    outlets = defaultdict(lambda: {
        "name": "",
        "total": 0,
        "by_topic": defaultdict(int),
        "by_date": defaultdict(int),
    })
    methods = defaultdict(int)
    unknown_handles = defaultdict(int)
    processed = 0
    skipped = 0

    for rumor in rumors:
        result, method, is_outlet = extract_reporter(rumor)
        if not result:
            skipped += 1
            continue

        processed += 1
        methods[method] += 1

        text = rumor.get("text", "") or ""
        tags = rumor.get("tags", []) or []
        date = rumor.get("archive_date", "") or rumor.get("date", "")
        topic = detect_topic(text, tags)

        if is_outlet:
            key = result["name"].lower().replace(" ", "_")
            o = outlets[key]
            o["name"] = result["name"]
            o["total"] += 1
            o["by_topic"][topic] += 1
            if date:
                o["by_date"][date] += 1
            continue

        key = result["name"].lower().replace(" ", "_").replace("@", "")
        if method == "unknown_handle":
            unknown_handles[result.get("_handle", result["name"])] += 1

        s = reporters[key]
        s["name"] = result["name"]
        s["outlet"] = result["outlet"]
        s["tier"] = result.get("tier", 4)
        s["total"] += 1
        s["detection_methods"][method] += 1
        s["by_topic"][topic] += 1
        if date:
            s["by_date"][date] += 1
        for team in extract_teams(tags):
            s["by_team"][team] += 1
        for player in extract_players(tags):
            s["by_player"][player] += 1
        for agent in extract_agents(tags, text):
            s["by_agent"][agent] += 1

    return {
        "rumors": len(rumors),
        "processed": processed,
        "skipped": skipped,
        "methods": dict(methods),
        "unknown_handles": dict(unknown_handles),
        "reporters": {k: _plain(v) for k, v in reporters.items()},
        "outlets": {k: _plain(v) for k, v in outlets.items()},
    }


def _plain(d):
    return {k: (dict(v) if isinstance(v, defaultdict) else v) for k, v in d.items()}


def _add_counts(target, source):
    for k, v in source.items():
        target[k] = target.get(k, 0) + v


def merge(part_aggs):
    """Merge per-part aggregates into the final payload, in the exact schema the
    frontend already expects (minus recent_rumors, which the UI no longer uses)."""
    reporters = {}
    outlets = {}
    methods = {}
    unknown = {}
    total_rumors = 0
    total_processed = 0

    for agg in part_aggs:
        total_rumors += agg["rumors"]
        total_processed += agg["processed"]
        _add_counts(methods, agg["methods"])
        _add_counts(unknown, agg["unknown_handles"])

        for key, s in agg["reporters"].items():
            tgt = reporters.setdefault(key, {
                "name": s["name"], "outlet": s["outlet"], "tier": s["tier"], "total": 0,
                "by_topic": {}, "by_player": {}, "by_team": {}, "by_agent": {},
                "by_date": {}, "detection_methods": {},
            })
            # Later parts are more recent, so let them win on outlet/tier.
            tgt["name"] = s["name"] or tgt["name"]
            tgt["outlet"] = s["outlet"] or tgt["outlet"]
            tgt["tier"] = s["tier"]
            tgt["total"] += s["total"]
            for field in ("by_topic", "by_player", "by_team", "by_agent", "by_date", "detection_methods"):
                _add_counts(tgt[field], s[field])

        for key, s in agg["outlets"].items():
            tgt = outlets.setdefault(key, {"name": s["name"], "total": 0, "by_topic": {}, "by_date": {}})
            tgt["name"] = s["name"] or tgt["name"]
            tgt["total"] += s["total"]
            _add_counts(tgt["by_topic"], s["by_topic"])
            _add_counts(tgt["by_date"], s["by_date"])

    reporter_list = []
    for key, s in reporters.items():
        initials = "".join(n[0] for n in s["name"].replace("@", "").split()[:2]).upper()[:2] or "??"
        reporter_list.append({
            "id": key,
            "name": s["name"],
            "outlet": s["outlet"],
            "tier": s["tier"],
            "avatar": initials,
            "total": s["total"],
            "breaking": 0,
            "by_topic": s["by_topic"],
            "by_player": dict(sorted(s["by_player"].items(), key=lambda x: -x[1])[:100]),
            "by_team": dict(sorted(s["by_team"].items(), key=lambda x: -x[1])),
            "by_agent": dict(sorted(s["by_agent"].items(), key=lambda x: -x[1])[:50]),
            "by_date": s["by_date"],
            "detection_methods": s["detection_methods"],
        })

    outlet_list = [{"id": k, **v} for k, v in outlets.items()]
    reporter_list.sort(key=lambda x: -x["total"])
    outlet_list.sort(key=lambda x: -x["total"])

    return {
        "generated_at": datetime.now().isoformat(),
        "total_rumors": total_rumors,
        "processed_rumors": total_processed,
        "total_reporters": len(reporter_list),
        "total_outlets": len(outlet_list),
        "detection_methods": methods,
        "reporters": reporter_list,
        "outlets": outlet_list,
        "unknown_handles": dict(sorted(unknown.items(), key=lambda x: -x[1])[:50]),
    }


def write_js(data, output_path=OUTPUT_JS):
    """Write reporter_data.js. Same file the frontend already loads, but the JSON
    is written compact instead of indented: identical data, ~40% fewer bytes."""
    body = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    js = (
        "// Reporter Rankings Data\n"
        f"// Generated: {data['generated_at']}\n"
        f"// Total Rumors: {data['total_rumors']}\n"
        f"// Processed: {data['processed_rumors']}\n"
        f"// Total Reporters: {data['total_reporters']}\n"
        f"// Total Outlets: {data['total_outlets']}\n\n"
        f"const REPORTER_DATA = {body};\n\n"
        "// Export for use in HTML\n"
        "if (typeof window !== 'undefined') {\n"
        "    window.REPORTER_DATA = REPORTER_DATA;\n"
        "}\n"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js)


def previous_processed():
    """Read '// Processed: N' out of the existing reporter_data.js."""
    try:
        with open(OUTPUT_JS, "r", encoding="utf-8") as f:
            for _ in range(10):
                line = f.readline()
                if line.startswith("// Processed:"):
                    return int(line.split(":", 1)[1].strip())
    except (OSError, ValueError):
        pass
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild-all", action="store_true", help="ignore agg/ and reprocess every part")
    ap.add_argument("--force", action="store_true", help="publish even if the volume guard trips")
    args = ap.parse_args()

    os.makedirs(AGG_DIR, exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="rumors-")

    try:
        n = part_count()
        print(f"Archive reports {n} parts")

        part_aggs = []
        for i in range(1, n + 1):
            agg_path = os.path.join(AGG_DIR, f"part_{i}.json")
            is_newest = (i == n)

            # Parts below the newest one are frozen: aggregate once, reuse forever.
            if not args.rebuild_all and not is_newest and os.path.exists(agg_path):
                with open(agg_path, "r", encoding="utf-8") as f:
                    agg = json.load(f)
                print(f"  part {i}: cached ({agg['processed']:,} attributed)")
                part_aggs.append(agg)
                continue

            raw_path = os.path.join(scratch, f"part_{i}.json")
            print(f"  part {i}: downloading...", flush=True)
            payload = fetch_json(f"{API_BASE}/api/rumors/part/{i}", dest_path=raw_path)
            rumors = rumors_from_payload(payload)
            agg = aggregate(rumors)
            print(f"  part {i}: {len(rumors):,} rumors, {agg['processed']:,} attributed")

            # Never commit an aggregate for the newest part: it grows on every
            # run, and rewriting a multi-MB file 2x a day would bloat the repo.
            if not is_newest:
                with open(agg_path, "w", encoding="utf-8") as f:
                    json.dump(agg, f, separators=(",", ":"))

            part_aggs.append(agg)
            del payload, rumors
            os.remove(raw_path)

        data = merge(part_aggs)

        print("\n=== Build summary ===")
        print(f"Total rumors:    {data['total_rumors']:,}")
        print(f"Attributed:      {data['processed_rumors']:,}")
        print(f"Reporters:       {data['total_reporters']:,}")
        print(f"Outlets:         {data['total_outlets']:,}")

        prev = previous_processed()
        if data["processed_rumors"] == 0:
            sys.exit("ABORT: build produced zero attributed rumors. Not publishing.")
        if prev and data["processed_rumors"] < prev * MIN_RATIO and not args.force:
            sys.exit(
                f"ABORT: attributed rumors dropped from {prev:,} to "
                f"{data['processed_rumors']:,}. Not publishing. "
                "Re-run with --force if this drop is expected."
            )

        write_js(data, OUTPUT_JS)
        print(f"\nWrote {OUTPUT_JS} ({os.path.getsize(OUTPUT_JS) / 1e6:.1f} MB)")

        print("\n=== Top 20 reporters ===")
        for i, r in enumerate(data["reporters"][:20], 1):
            print(f"  {i:2}. {r['name'][:28]:28} ({r['outlet'][:22]:22}) {r['total']:6,}")

    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
