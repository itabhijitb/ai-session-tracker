"""Basic tests for the search engine."""

import tempfile
from pathlib import Path

from ai_session_tracker.index.engine import SearchEngine
from ai_session_tracker.models import Session


def test_engine_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        _ = SearchEngine(db_path=db_path)
        assert db_path.exists()


def test_engine_reindex_runs():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = SearchEngine(db_path=db_path)
        counts = engine.reindex()
        assert isinstance(counts, dict)


def test_engine_search_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = SearchEngine(db_path=db_path)
        results = engine.search("nonexistent_xyzzy_query")
        assert results == []


def test_session_model():
    s = Session(
        session_id="test-123",
        agent="devin",
        directory="/tmp/test",
        title="My Test Session",
    )
    assert s.display_title == "My Test Session"
    assert s.short_id == "test-123"
    assert s.agent == "devin"


def test_session_model_untitled():
    s = Session(session_id="x", agent="devin", directory="/tmp", first_prompt="hello world")
    assert s.display_title == "hello world"


def test_session_model_no_title():
    s = Session(session_id="x", agent="devin", directory="/tmp")
    assert s.display_title == "(untitled)"


def test_engine_records_last_indexed():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SearchEngine(db_path=Path(tmpdir) / "test.db")
        assert engine.last_indexed() is None
        engine.reindex()
        assert engine.last_indexed() is not None


def test_resolve_session_id_prefix():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SearchEngine(db_path=Path(tmpdir) / "test.db")
        db = engine._conn()
        db.executemany(
            "INSERT INTO sessions (session_id, agent) VALUES (?, ?)",
            [("abc-111", "claude-code"), ("abc-222", "devin"), ("xyz-999", "devin")],
        )
        db.commit()
        db.close()
        assert engine.resolve_session_id("xyz") == ("xyz-999", "devin")
        assert engine.resolve_session_id("abc") is None  # ambiguous
        assert engine.resolve_session_id("abc", agent="devin") == ("abc-222", "devin")
        assert engine.resolve_session_id("nope") is None
