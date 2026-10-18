"""Adapter for Devin CLI — reads sessions.db from Devin's local data directory.

Paths by platform:
  macOS/Linux: ~/.local/share/devin/cli/sessions.db
  Windows:     %APPDATA%/devin/cli/sessions.db
"""

from __future__ import annotations

import json
import platform
import sqlite3
from pathlib import Path

from ai_session_tracker.adapters.base import BaseAdapter
from ai_session_tracker.models import Message, Session, SessionPreview


def _devin_db_path() -> Path:
    if platform.system() == "Windows":
        appdata = Path.home() / "AppData" / "Roaming" / "devin" / "cli" / "sessions.db"
        if appdata.exists():
            return appdata
        return Path.home() / ".local" / "share" / "devin" / "cli" / "sessions.db"
    return Path.home() / ".local" / "share" / "devin" / "cli" / "sessions.db"


DB_PATH = _devin_db_path()


class DevinAdapter(BaseAdapter):
    name = "devin"

    def is_available(self) -> bool:
        return DB_PATH.exists()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(DB_PATH))
        db.row_factory = sqlite3.Row
        return db

    def list_sessions(self) -> list[Session]:
        if not self.is_available():
            return []
        db = self._connect()
        rows = db.execute(
            """
            SELECT id, working_directory, title,
                   datetime(created_at, 'unixepoch', 'localtime') AS started,
                   datetime(last_activity_at, 'unixepoch', 'localtime') AS ended
            FROM sessions
            WHERE hidden = 0
            ORDER BY last_activity_at DESC
            """
        ).fetchall()
        db.close()
        return [
            Session(
                session_id=r["id"],
                agent="devin",
                directory=r["working_directory"] or "",
                title=r["title"] or "",
                start_time=r["started"] or "",
                end_time=r["ended"] or "",
                status="imported",
            )
            for r in rows
        ]

    def deep_search(self, query: str) -> list[Session]:
        if not self.is_available():
            return []
        db = self._connect()
        like = f"%{query}%"
        rows = db.execute(
            """
            SELECT s.id, s.working_directory, s.title,
                   datetime(s.created_at, 'unixepoch', 'localtime') AS started,
                   datetime(s.last_activity_at, 'unixepoch', 'localtime') AS ended
            FROM sessions s
            WHERE s.hidden = 0
              AND s.id IN (
                  SELECT DISTINCT m.session_id
                  FROM message_nodes m
                  WHERE m.chat_message LIKE ?
              )
            ORDER BY s.last_activity_at DESC
            LIMIT 30
            """,
            (like,),
        ).fetchall()
        db.close()
        return [
            Session(
                session_id=r["id"],
                agent="devin",
                directory=r["working_directory"] or "",
                title=r["title"] or "",
                start_time=r["started"] or "",
                end_time=r["ended"] or "",
                status="native",
            )
            for r in rows
        ]

    def preview(self, session_id: str) -> SessionPreview | None:
        if not self.is_available():
            return None
        db = self._connect()
        sess = db.execute(
            """SELECT id, working_directory, title,
                      datetime(created_at, 'unixepoch', 'localtime') AS started
               FROM sessions WHERE id = ? AND hidden = 0""",
            (session_id,),
        ).fetchone()
        if not sess:
            db.close()
            return None
        rows = db.execute(
            """SELECT chat_message,
                      datetime(created_at, 'unixepoch', 'localtime') AS ts
               FROM message_nodes
               WHERE session_id = ?
               ORDER BY created_at ASC""",
            (session_id,),
        ).fetchall()
        db.close()

        messages: list[Message] = []
        seen_content: set[str] = set()
        for r in rows:
            try:
                msg = json.loads(r["chat_message"])
            except (json.JSONDecodeError, TypeError):
                continue
            role = msg.get("role", "")
            if role not in ("user", "assistant"):
                continue
            content = msg.get("content", "")
            if not content or not isinstance(content, str):
                continue
            key = f"{role}:{content[:100]}"
            if key in seen_content:
                continue
            seen_content.add(key)
            messages.append(Message(role=role, content=content, timestamp=r["ts"] or ""))

        return SessionPreview(
            session_id=session_id,
            agent="devin",
            title=sess["title"] or "",
            directory=sess["working_directory"] or "",
            start_time=sess["started"] or "",
            messages=messages,
            total_messages=len(messages),
        )
