"""Tests for timestamp normalization across agent formats."""

from datetime import datetime, timezone

from ai_session_tracker.models import Session, normalize_timestamp


def test_normalize_local_sqlite_format_unchanged():
    assert normalize_timestamp("2026-10-18 15:29:07") == "2026-10-18 15:29:07"


def test_normalize_utc_iso_converts_to_local():
    expected = datetime(2026, 10, 18, 10, 21, 57, tzinfo=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    assert normalize_timestamp("2026-10-18T10:21:57.907Z") == expected


def test_normalize_epoch_millis_and_seconds():
    secs = 1760000000
    expected = datetime.fromtimestamp(secs).strftime("%Y-%m-%d %H:%M:%S")
    assert normalize_timestamp(secs) == expected
    assert normalize_timestamp(secs * 1000) == expected
    assert normalize_timestamp(str(secs * 1000)) == expected


def test_normalize_empty_and_garbage():
    assert normalize_timestamp("") == ""
    assert normalize_timestamp(None) == ""
    assert normalize_timestamp("not a date") == "not a date"


def test_mixed_agent_timestamps_sort_chronologically():
    later_local = Session("a", "devin", "/", start_time="2026-10-18 23:59:00")
    earlier_utc = Session("b", "claude-code", "/", start_time="2026-10-17T00:00:00Z")
    ordered = sorted([earlier_utc, later_local], key=lambda s: s.start_time, reverse=True)
    assert ordered[0].session_id == "a"
