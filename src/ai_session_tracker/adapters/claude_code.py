"""Adapter for Claude Code — reads from ~/.claude/projects/**/*.jsonl + history.jsonl"""

from __future__ import annotations

import json
from pathlib import Path

from ai_session_tracker.adapters.base import BaseAdapter
from ai_session_tracker.models import Message, Session, SessionPreview

CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"


def _decode_project_dir(dirname: str) -> str:
    """Decode Claude Code's directory encoding: '-' delimited path segments."""
    return dirname.replace("-", "/") if dirname.startswith("-") else dirname


def _read_jsonl_safe(path: Path, max_lines: int = 0) -> list[dict]:
    """Read a JSONL file, skipping malformed lines."""
    results = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if max_lines and i >= max_lines:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return results


class ClaudeCodeAdapter(BaseAdapter):
    name = "claude-code"

    def is_available(self) -> bool:
        return PROJECTS_DIR.exists()

    def _build_history_index(self) -> dict[str, dict]:
        """Build session_id -> {project, timestamp, display} from history.jsonl."""
        index: dict[str, dict] = {}
        if not HISTORY_FILE.exists():
            return index
        for entry in _read_jsonl_safe(HISTORY_FILE):
            sid = entry.get("sessionId", "")
            if sid and sid not in index:
                index[sid] = {
                    "project": entry.get("project", ""),
                    "timestamp": entry.get("timestamp", 0),
                    "display": entry.get("display", ""),
                }
        return index

    def list_sessions(self) -> list[Session]:
        if not self.is_available():
            return []
        history = self._build_history_index()
        sessions = []
        for proj_dir in PROJECTS_DIR.iterdir():
            if not proj_dir.is_dir():
                continue
            directory = _decode_project_dir(proj_dir.name)
            for jsonl_file in proj_dir.glob("*.jsonl"):
                sid = jsonl_file.stem
                title = ""
                first_prompt = ""
                timestamp = ""
                for entry in _read_jsonl_safe(jsonl_file, max_lines=10):
                    if entry.get("type") == "user" and "message" in entry:
                        msg = entry["message"]
                        content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
                        first_prompt = content[:150] if isinstance(content, str) else ""
                        break
                    if not timestamp and "timestamp" in entry:
                        timestamp = entry["timestamp"]

                hist = history.get(sid, {})
                if not directory or directory == proj_dir.name:
                    directory = hist.get("project", directory)
                if not timestamp and hist.get("timestamp"):
                    ts = hist["timestamp"]
                    if isinstance(ts, (int, float)):
                        from datetime import datetime
                        timestamp = datetime.fromtimestamp(ts / 1000).isoformat()

                sessions.append(
                    Session(
                        session_id=sid,
                        agent="claude-code",
                        directory=directory,
                        title=title,
                        first_prompt=first_prompt,
                        start_time=str(timestamp),
                        status="imported",
                    )
                )
        sessions.sort(key=lambda s: s.start_time, reverse=True)
        return sessions

    def deep_search(self, query: str) -> list[Session]:
        if not self.is_available():
            return []
        query_lower = query.lower()
        matches = []
        for proj_dir in PROJECTS_DIR.iterdir():
            if not proj_dir.is_dir():
                continue
            directory = _decode_project_dir(proj_dir.name)
            for jsonl_file in proj_dir.glob("*.jsonl"):
                sid = jsonl_file.stem
                found = False
                first_prompt = ""
                timestamp = ""
                try:
                    with open(jsonl_file, "r", encoding="utf-8", errors="replace") as f:
                        for line in f:
                            if not timestamp:
                                try:
                                    entry = json.loads(line)
                                    if "timestamp" in entry:
                                        timestamp = entry["timestamp"]
                                    if entry.get("type") == "user" and not first_prompt:
                                        msg = entry.get("message", {})
                                        content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
                                        first_prompt = content[:150] if isinstance(content, str) else ""
                                except json.JSONDecodeError:
                                    pass
                            if query_lower in line.lower():
                                found = True
                                break
                except OSError:
                    continue
                if found:
                    matches.append(
                        Session(
                            session_id=sid,
                            agent="claude-code",
                            directory=directory,
                            first_prompt=first_prompt,
                            start_time=str(timestamp),
                            status="native",
                        )
                    )
        matches.sort(key=lambda s: s.start_time, reverse=True)
        return matches[:30]

    def preview(self, session_id: str) -> SessionPreview | None:
        if not self.is_available():
            return None
        jsonl_file = None
        directory = ""
        for proj_dir in PROJECTS_DIR.iterdir():
            if not proj_dir.is_dir():
                continue
            candidate = proj_dir / f"{session_id}.jsonl"
            if candidate.exists():
                jsonl_file = candidate
                directory = _decode_project_dir(proj_dir.name)
                break
        if not jsonl_file:
            return None

        entries = _read_jsonl_safe(jsonl_file)
        messages: list[Message] = []
        title = ""
        start_time = ""
        for entry in entries:
            if not start_time and "timestamp" in entry:
                start_time = str(entry["timestamp"])
            etype = entry.get("type", "")
            if etype not in ("user", "assistant"):
                continue
            msg = entry.get("message", {})
            if isinstance(msg, dict):
                content = msg.get("content", "")
                if isinstance(content, list):
                    text_parts = [p.get("text", "") for p in content
                                  if isinstance(p, dict) and p.get("type") == "text"]
                    content = " ".join(text_parts)
            else:
                content = str(msg)
            if not content or not isinstance(content, str):
                continue
            ts = entry.get("timestamp", "")
            messages.append(Message(role=etype, content=content, timestamp=str(ts)))

        return SessionPreview(
            session_id=session_id,
            agent="claude-code",
            title=title,
            directory=directory,
            start_time=start_time,
            messages=messages,
            total_messages=len(messages),
        )
