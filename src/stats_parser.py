"""
stats_parser.py
---------------
Merges:
- GameTracker playtime (weekly_results.json from version2.py)
- CS 1.6 server logs (admin_actions.json from log_reader.py)

Outputs:
- Dated combined JSON + CSV in data/weekly/
- Latest combined JSON in docs/data/ for the frontend
"""

import os
import json
import csv
from datetime import datetime, timezone

DATA_DIR = os.path.join("data", "weekly")
FRONTEND_DATA_DIR = os.path.join("docs", "data")

def load_json(path: str):
    if not os.path.exists(path):
        return None
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

def aggregate(playtime, actions):
    results = {}

    # Add playtime
    for row in playtime:
        results[row["name"]] = {
            "minutes": row.get("minutes", 0),
            "slap": 0,
            "kick": 0,
            "ban": 0,
            "rename": 0,
            "admin_chat": 0,
        }

    # Merge actions
    for name, stats in actions.items():
        if name not in results:
            results[name] = {
                "minutes": 0,
                "slap": 0,
                "kick": 0,
                "ban": 0,
                "rename": 0,
                "admin_chat": 0,
            }
        for k, v in stats.items():
            results[name][k] = results[name].get(k, 0) + v

    return results

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Inputs: latest JSONs
    playtime_json = os.path.join(FRONTEND_DATA_DIR, "weekly_results.json")
    actions_json = os.path.join(FRONTEND_DATA_DIR, "admin_actions.json")

    playtime = load_json(playtime_json)
    actions = load_json(actions_json)

    if not playtime or not actions:
        print("⚠️ Missing input data. Run version2.py and log_reader.py first.")
        return

    results = aggregate(playtime, actions)

    # Save dated archive in data/weekly/
    out_json = os.path.join(DATA_DIR, f"combined_stats_{now}.json")
    out_csv = os.path.join(DATA_DIR, f"combined_stats_{now}.csv")
    save_json(results, out_json)
    save_csv(results, out_csv)

    # Save latest for frontend
    save_json(results, os.path.join(FRONTEND_DATA_DIR, "combined_stats.json"))

    print(f"✅ Combined stats saved → {out_json}, {out_csv}")
    print(f"✅ Frontend updated → docs/data/combined_stats.json")

if __name__ == "__main__":
    main()
