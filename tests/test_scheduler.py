import pytest
from scheduler import get_utc_run_time
import pytz
from datetime import datetime

def test_utc_run_time_is_valid_format():
    """get_utc_run_time should return a time string in HH:MM format."""
    result = get_utc_run_time()
    assert len(result) == 5
    assert result[2] == ':'

def test_utc_run_time_differs_from_local():
    """UTC run time should differ from Athens local time (UTC is behind Athens)."""
    result = get_utc_run_time()
    assert result != "22:45"  # UTC should never equal Athens local time