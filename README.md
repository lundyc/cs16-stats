# CS 1.6 Admin Stats & Gametime Tracker

## 📌 Overview

This project tracks **admin activity** and **playtime stats** for a Counter-Strike 1.6 server.

It combines two data sources:

- **GameTracker graphs** → OCR of playtime charts (minutes played).
- **HLDS/AMX Mod X logs** → parsed admin actions (slaps, kicks, bans, renames, admin chat).

Outputs are stored in **CSV/JSON** and displayed in a simple **Bootstrap/Chart.js frontend**.

---

## ⚙️ Installation

```bash
# clone repo
git clone <your-repo-url>
cd project-root

# install dependencies
pip install -r requirements.txt
```
