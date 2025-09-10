"""
log_reader.py
--------------
Parses CS 1.6 server logs and extracts admin actions:
- slap, kick, ban, rename, admin chat

Outputs:
- JSON + CSV in data/weekly/
- Latest JSON copied to frontend/data/ for charts
"""

import os
import re
import json
import csv
from datetime import datetime, timezone

LOG_DIR = os.path.join("data", "logs")
DATA_DIR = os.path.join("data", "weekly")
FRONTEND_DATA_DIR = os.path.join("frontend", "data")
ADMINS_FILE = os.path.join("data", "admins.txt")

# Regex patterns
PATTERNS = {
    "slap": re.compile(r'\"(.+?)<.*?>\" slapped'),
    "kick": re.compile(r'\"(.+?)<.*?>\" kicked'),
    "ban": re.compile(r'\"(.+?)<.*?>\" banned'),
    "rename": re.compile(r'\"(.+?)<.*?>\" changed name of'),
    "admin_chat": re.compile(r'\[ADMIN CHAT\] \((.+?)\)'),
}

def load_admins(path=ADMINS_FILE):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def parse_log_file(path, admins):
    stats = {a: {"slap": 0, "kick": 0, "ban": 0, "rename": 0, "admin_chat": 0} for a in admins}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            for action, regex in PATTERNS.items():
                m = regex.search(line)
                if m:
                    actor = m.group(1).strip()
                    if actor in stats:
                        stats[actor][action] += 1
    return stats

def merge_stats(all_stats):
    merged = {}
    for stats in all_stats:
        for name, values in stats.items():
            if name not in merged:
                merged[name] = values.copy()
            else:
                for k, v in values.items():
                    merged[name][k] += v
    return merged

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_csv(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "slap", "kick", "ban", "rename", "admin_chat"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for name, stats in sorted(data.items()):
            row = {"name": name}
            row.update(stats)
            w.writerow(row)

def main():
    admins = load_admins()
    if not admins:
        print("⚠️ No admins loaded. Check data/admins.txt")
        return

    all_stats = []
    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".log"):
            path = os.path.join(LOG_DIR, filename)
            file_stats = parse_log_file(path, admins)
            all_stats.append(file_stats)

    merged = merge_stats(all_stats)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Save outputs
    out_json = os.path.join(DATA_DIR, f"admin_actions_{now}.json")
    out_csv = os.path.join(DATA_DIR, f"admin_actions_{now}.csv")
    save_json(merged, out_json)
    save_csv(merged, out_csv)

    # Copy to frontend
    save_json(merged, os.path.join(FRONTEND_DATA_DIR, "admin_actions.json"))

    print(f"✅ Admin actions parsed and saved → {out_json}, {out_csv}")
    print(f"✅ Frontend updated → frontend/data/admin_actions.json")

if __name__ == "__main__":
    main()
