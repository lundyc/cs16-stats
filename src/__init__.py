"""
src package
-----------
Contains all backend scripts for the project:
- log_reader: parses CS 1.6 logs for admin actions
- stats_parser: merges log + GameTracker OCR data
- version2: main playtime/leaderboard collector
- grab_gt_stats / gametime_ocr: legacy OCR tools
- utils: helper functions
"""
__all__ = [
    "log_reader",
    "stats_parser",
    "version2",
    "grab_gt_stats",
    "gametime_ocr",
]
