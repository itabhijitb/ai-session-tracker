"""Unified FTS5 search engine — indexes sessions from all adapters into one SQLite DB."""

from __future__ import annotations

import platform
import sqlite3
from pathlib import Path

from ai_session_tracker.adapters import ALL_ADAPTERS, BaseAdapter
from ai_session_tracker.models import Session, SessionPreview


def _default_db_path() -> Path:
    """Platform-aware default index location."""
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "ai-session-tracker" / "index.db"
    return Path.home() / ".config" / "ai-session-tracker" / "index.db"


DEFAULT_DB = _default_db_path()


class SearchEngine:
    """Central index that aggregates sessions from every available agent adapter."""

    def __init__(self, db_path: Path = DEFAULT_DB):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._adapters: list[BaseAdapter] = [cls() for cls in ALL_ADAPTERS]
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.db_path))
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def _init_db(self):
        db = self._conn()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                rowid        INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                agent        TEXT NOT NULL,
                directory    TEXT NOT NULL DEFAULT '',
                title        TEXT DEFAULT '',
                first_prompt TEXT DEFAULT '',
                start_time   TEXT DEFAULT '',
                end_time     TEXT DEFAULT '',
                status       TEXT DEFAULT 'imported',
                UNIQUE(agent, session_id)
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
                session_id,
                agent,
                directory,
                title,
                first_prompt,
                content='sessions',
                content_rowid='rowid'
            );

            CREATE TRIGGER IF NOT EXISTS sessions_ai AFTER INSERT ON sessions BEGIN
                INSERT INTO sessions_fts(rowid, session_id, agent, directory, title, first_prompt)
                VALUES (new.rowid, new.session_id, new.agent, new.directory, new.title, new.first_prompt);
            END;

            CREATE TRIGGER IF NOT EXISTS sessions_ad AFTER DELETE ON sessions BEGIN
                INSERT INTO sessions_fts(sessions_fts, rowid, session_id, agent, directory, title, first_prompt)
                VALUES ('delete', old.rowid, old.session_id, old.agent, old.directory, old.title, old.first_prompt);
            END;

            CREATE TRIGGER IF NOT EXISTS sessions_au AFTER UPDATE ON sessions BEGIN
                INSERT INTO sessions_fts(sessions_fts, rowid, session_id, agent, directory, title, first_prompt)
                VALUES ('delete', old.rowid, old.session_id, old.agent, old.directory, old.title, old.first_prompt);
                INSERT INTO sessions_fts(rowid, session_id, agent, directory, title, first_prompt)
                VALUES (new.rowid, new.session_id, new.agent, new.directory, new.title, new.first_prompt);
            END;
        """)
        db.commit()
        db.close()

    def reindex(self) -> dict[str, int]:
        """Pull sessions from all adapters and upsert into the unified index."""
        counts: dict[str, int] = {}
        db = self._conn()
        for adapter in self._adapters:
            if not adapter.is_available():
                counts[adapter.name] = 0
                continue
            sessions = adapter.list_sessions()
            for s in sessions:
                db.execute(
                    """INSERT INTO sessions (session_id, agent, directory, title, first_prompt, start_time, end_time, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(agent, session_id) DO UPDATE SET
                           directory=excluded.directory,
                           title=excluded.title,
                           first_prompt=CASE WHEN excluded.first_prompt != '' THEN excluded.first_prompt ELSE sessions.first_prompt END,
                           start_time=CASE WHEN excluded.start_time != '' THEN excluded.start_time ELSE sessions.start_time END,
                           end_time=excluded.end_time,
                           status=excluded.status
                    """,
                    (s.session_id, s.agent, s.directory, s.title, s.first_prompt, s.start_time, s.end_time, s.status),
                )
            counts[adapter.name] = len(sessions)
        db.commit()
        db.close()
        return counts

    def search(self, query: str, agent: str | None = None, limit: int = 30) -> list[Session]:
        """Fast FTS5 search across indexed titles, prompts, and directories."""
        safe_query = " ".join(f'"{token}"' for token in query.split())
        db = self._conn()
        if agent:
            rows = db.execute(
                """
                SELECT s.* FROM sessions_fts f
                JOIN sessions s ON s.rowid = f.rowid
                WHERE sessions_fts MATCH ? AND s.agent = ?
                ORDER BY s.start_time DESC LIMIT ?
                """,
                (safe_query, agent, limit),
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT s.* FROM sessions_fts f
                JOIN sessions s ON s.rowid = f.rowid
                WHERE sessions_fts MATCH ?
                ORDER BY s.start_time DESC LIMIT ?
                """,
                (safe_query, limit),
            ).fetchall()
        db.close()
        return [self._row_to_session(r) for r in rows]

    def deep_search(self, query: str, agent: str | None = None, limit: int = 30) -> list[Session]:
        """Search full conversation content via each adapter's native deep search."""
        if len(query.strip()) < 3:
            return []
        results: list[Session] = []
        for adapter in self._adapters:
            if agent and adapter.name != agent:
                continue
            if not adapter.is_available():
                continue
            results.extend(adapter.deep_search(query))
        seen: set[tuple[str, str]] = set()
        deduped: list[Session] = []
        for s in results:
            key = (s.agent, s.session_id)
            if key not in seen:
                seen.add(key)
                deduped.append(s)
        deduped.sort(key=lambda s: s.start_time, reverse=True)
        return deduped[:limit]

    def list_sessions(self, agent: str | None = None, directory: str | None = None, limit: int = 30) -> list[Session]:
        """List sessions from the index, optionally filtered."""
        db = self._conn()
        conditions = []
        params: list = []
        if agent:
            conditions.append("agent = ?")
            params.append(agent)
        if directory:
            conditions.append("directory LIKE ?")
            params.append(f"%{directory}%")
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)
        rows = db.execute(f"SELECT * FROM sessions {where} ORDER BY start_time DESC LIMIT ?", params).fetchall()
        db.close()
        return [self._row_to_session(r) for r in rows]

    def preview(self, session_id: str, agent: str | None = None) -> SessionPreview | None:
        """Get a conversation preview for a session. Tries each adapter until one succeeds."""
        for adapter in self._adapters:
            if agent and adapter.name != agent:
                continue
            if not adapter.is_available():
                continue
            result = adapter.preview(session_id)
            if result:
                return result
        return None

    def status(self) -> list[dict]:
        """Return per-adapter availability and session counts."""
        return [a.status() for a in self._adapters]

    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> Session:
        return Session(
            session_id=row["session_id"],
            agent=row["agent"],
            directory=row["directory"] or "",
            title=row["title"] or "",
            first_prompt=row["first_prompt"] or "",
            start_time=row["start_time"] or "",
            end_time=row["end_time"] or "",
            status=row["status"] or "",
        )
