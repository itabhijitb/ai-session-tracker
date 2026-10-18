"""Basic tests for the search engine."""

import tempfile
from pathlib import Path

from ai_session_tracker.index.engine import SearchEngine
from ai_session_tracker.models import Session


def test_engine_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = SearchEngine(db_path=db_path)
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
