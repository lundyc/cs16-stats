"""
Unit tests for log_reader.py
Run with: pytest tests/test_log_reader.py
"""

import os
import tempfile
import pytest
from src import log_reader


SAMPLE_LOG = """
L 09/10/2025 - 09:01:12: "chani<1><STEAM_0:1:12345><CT>" slapped "PlayerOne<2><STEAM_0:1:54321><TERRORIST>" with 0 damage
L 09/10/2025 - 09:02:12: "BaRoN<3><STEAM_0:1:11111><CT>" kicked "PlayerTwo<4><STEAM_0:1:22222><TERRORIST>"
L 09/10/2025 - 09:03:12: "US-B<5><STEAM_0:1:33333><CT>" banned "PlayerThree<6><STEAM_0:1:44444><TERRORIST>" (minutes "60") (reason "abuse")
L 09/10/2025 - 09:04:12: "R()CK~KI||3R<7><STEAM_0:1:55555><CT>" changed name of "PlayerFour<8><STEAM_0:1:66666><TERRORIST>" to "Renamed"
L 09/10/2025 - 09:05:12: [ADMIN CHAT] (chani) : "stack A"
"""


@pytest.fixture
def sample_log_file():
    """Creates a temporary log file with sample content."""
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".log") as tmp:
        tmp.write(SAMPLE_LOG)
        tmp_path = tmp.name
    yield tmp_path
    os.remove(tmp_path)


def test_parse_log_file(sample_log_file):
    admins = ["chani", "BaRoN", "US-B", "R()CK~KI||3R"]

    stats = log_reader.parse_log_file(sample_log_file, admins)

    assert stats["chani"]["slap"] == 1
    assert stats["BaRoN"]["kick"] == 1
    assert stats["US-B"]["ban"] == 1
    assert stats["R()CK~KI||3R"]["rename"] == 1
    assert stats["chani"]["admin_chat"] == 1


def test_merge_stats():
    admins = ["chani"]
    stats1 = {"chani": {"slap": 1, "kick": 0, "ban": 0, "rename": 0, "admin_chat": 1}}
    stats2 = {"chani": {"slap": 2, "kick": 1, "ban": 0, "rename": 0, "admin_chat": 0}}

    merged = log_reader.merge_stats([stats1, stats2])

    assert merged["chani"]["slap"] == 3
    assert merged["chani"]["kick"] == 1
    assert merged["chani"]["admin_chat"] == 1
