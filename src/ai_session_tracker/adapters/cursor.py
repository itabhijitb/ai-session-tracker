"""Adapter for Cursor — reads from ~/Library/Application Support/Cursor/ (macOS)
or ~/.config/Cursor/ (Linux) or %APPDATA%/Cursor/ (Windows).

Cursor stores Composer / chat history in its globalStorage SQLite DB (state.vscdb)
and in workspace-specific storage directories.
"""

from __future__ import annotations

import json
import platform
import sqlite3
from pathlib import Path

from ai_session_tracker.adapters.base import BaseAdapter
from ai_session_tracker.models import Session


def _cursor_data_dir() -> Path:
    """Return the Cursor application data directory for the current OS."""
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Cursor"
    elif system == "Linux":
        return Path.home() / ".config" / "Cursor"
    elif system == "Windows":
        appdata = Path.home() / "AppData" / "Roaming" / "Cursor"
        if appdata.exists():
            return appdata
        return Path.home() / ".cursor"
    return Path.home() / ".cursor"


def _find_state_dbs(data_dir: Path) -> list[Path]:
    """Find all state.vscdb files (SQLite) in Cursor's storage."""
    dbs = []
    for name in ["state.vscdb", "state.sqlite"]:
        p = data_dir / "User" / "globalStorage" / name
        if p.exists():
            dbs.append(p)
    ws_dir = data_dir / "User" / "workspaceStorage"
    if ws_dir.is_dir():
        for ws in ws_dir.iterdir():
            for name in ["state.vscdb", "state.sqlite"]:
                p = ws / name
                if p.exists():
                    dbs.append(p)
    return dbs


class CursorAdapter(BaseAdapter):
    name = "cursor"

    def __init__(self):
        self._data_dir = _cursor_data_dir()

    def is_available(self) -> bool:
        return self._data_dir.exists()

    def _read_workspace_json(self, ws_dir: Path) -> dict:
        """Read workspace.json from a workspace storage directory."""
        wj = ws_dir / "workspace.json"
        if wj.exists():
            try:
                return json.loads(wj.read_text(encoding="utf-8", errors="replace"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def list_sessions(self) -> list[Session]:
        if not self.is_available():
            return []
        sessions = []
        ws_root = self._data_dir / "User" / "workspaceStorage"
        if ws_root.is_dir():
            for ws_dir in ws_root.iterdir():
                if not ws_dir.is_dir():
                    continue
                ws_info = self._read_workspace_json(ws_dir)
                folder = ws_info.get("folder", ws_info.get("workspace", ""))
                folder = folder.removeprefix("file://")
                sessions.append(
                    Session(
                        session_id=ws_dir.name,
                        agent="cursor",
                        directory=folder,
                        status="imported",
                    )
                )

        for db_path in _find_state_dbs(self._data_dir):
            try:
                db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                db.row_factory = sqlite3.Row
                rows = db.execute(
                    "SELECT key, value FROM ItemTable WHERE key LIKE '%composer%' OR key LIKE '%chat%' LIMIT 100"
                ).fetchall()
                for r in rows:
                    try:
                        val = json.loads(r["value"]) if r["value"] else {}
                        if isinstance(val, dict) and "conversations" in val:
                            for conv in val["conversations"]:
                                sid = conv.get("id", conv.get("composerId", ""))
                                if sid:
                                    first_msg = ""
                                    msgs = conv.get("messages", conv.get("text", []))
                                    if isinstance(msgs, list) and msgs:
                                        m = msgs[0]
                                        first_msg = (
                                            m.get("text", m.get("content", "")) if isinstance(m, dict) else str(m)
                                        )[:150]
                                    sessions.append(
                                        Session(
                                            session_id=str(sid),
                                            agent="cursor",
                                            directory="",
                                            first_prompt=first_msg,
                                            status="imported",
                                        )
                                    )
                    except (json.JSONDecodeError, TypeError):
                        continue
                db.close()
            except (sqlite3.OperationalError, OSError):
                continue

        sessions.sort(key=lambda s: s.start_time, reverse=True)
        return sessions

    def deep_search(self, query: str) -> list[Session]:
        if not self.is_available():
            return []
        query_lower = query.lower()
        matches = []
        for db_path in _find_state_dbs(self._data_dir):
            try:
                db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                rows = db.execute("SELECT key, value FROM ItemTable WHERE value LIKE ?", (f"%{query}%",)).fetchall()
                for r in rows:
                    key = r[0] or ""
                    if query_lower in (r[1] or "").lower():
                        matches.append(
                            Session(
                                session_id=key[:60],
                                agent="cursor",
                                directory=str(db_path.parent),
                                status="native",
                            )
                        )
                db.close()
            except (sqlite3.OperationalError, OSError):
                continue
        return matches[:30]
