"""
stats_parser.py
----------------
Aggregates admin statistics from multiple sources:
- GameTracker playtime (from version2.py / OCR pipeline)
- CS 1.6 server logs (from log_reader.py)

Outputs unified JSON + CSV in data/weekly/ and copies latest
into frontend/data/ for the web interface.
"""

import os
import json
import csv
from datetime import datetime, timezone

DATA_DIR = os.path.join("data", "weekly")
FRONTEND_DATA_DIR = os.path.join("frontend", "data")

def load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(data: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_csv(data: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "minutes", "slap", "kick", "ban", "rename", "admin_chat"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for name, stats in sorted(data.items()):
            row = {"name": name}
            row.update(stats)
            w.writerow(row)

def aggregate(playtime_json: str, admin_actions_json: str):
    playtime = load_json(playtime_json)
    actions = load_json(admin_actions_json)

    results = {}
    # Load playtime into results
    for row in playtime:
        results[row["name"]] = {
            "minutes": row.get("minutes", 0),
            "slap": 0,
            "kick": 0,
            "ban": 0,
            "rename": 0,
            "admin_chat": 0,
        }

    # Merge in actions
    for name, stats in actions.items():
        if name not in results:
            results[name] = {"minutes": 0, **stats}
        else:
            results[name].update(stats)

    return results

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    playtime_json = os.path.join("weekly_results.json")        # from version2.py
    actions_json = os.path.join(DATA_DIR, f"admin_actions_{now}.json")  # from log_reader.py

    if not os.path.exists(playtime_json) or not os.path.exists(actions_json):
        print("Missing input data. Run version2.py and log_reader.py first.")
        return

    results = aggregate(playtime_json, actions_json)

    # Save combined outputs
    out_json = os.path.join(DATA_DIR, f"combined_stats_{now}.json")
    out_csv = os.path.join(DATA_DIR, f"combined_stats_{now}.csv")
    save_json(results, out_json)
    save_csv(results, out_csv)

    # Copy latest to frontend
    save_json(results, os.path.join(FRONTEND_DATA_DIR, "combined_stats.json"))

    print(f"✅ Combined stats saved → {out_json}, {out_csv}")
    print(f"✅ Frontend updated → frontend/data/combined_stats.json")

if __name__ == "__main__":
    main()
