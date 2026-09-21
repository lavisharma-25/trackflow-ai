import pytest

from src.tools.tracker_tools._shared import get_tracker_path
from src.tools.tracker_tools.delete_tracker import delete_tracker
from src.tools.tracker_tools.remove_records import remove_records


def test_legacy_tracker_path_rejects_traversal():
    with pytest.raises(ValueError, match="Unsafe"):
        get_tracker_path("../outside")


def test_legacy_destructive_tools_require_confirmation():
    assert delete_tracker("expenses")["error"] == "Deletion requires confirmed=true"
    assert remove_records("expenses")["error"] == "Record removal requires confirmed=true"
