"""Adapter for Windsurf / Codeium.

Paths by platform:
  macOS/Linux: ~/.codeium/windsurf/
  Windows:     %USERPROFILE%/.codeium/windsurf/ or %APPDATA%/Codeium/Windsurf/
"""

from __future__ import annotations

import json
import platform
from pathlib import Path

from ai_session_tracker.adapters.base import BaseAdapter
from ai_session_tracker.models import Session

CODEIUM_DIRS: list[Path] = [Path.home() / ".codeium"]
if platform.system() == "Windows":
    CODEIUM_DIRS.append(Path.home() / "AppData" / "Roaming" / "Codeium")
CHANNELS = ["windsurf", "windsurf-next", "windsurf-insiders"]


def _find_history_dirs() -> list[Path]:
    """Find all Windsurf history directories across channels."""
    dirs = []
    for base in CODEIUM_DIRS:
        for channel in CHANNELS:
            hist = base / channel / "code_tracker" / "history"
            if hist.is_dir():
                dirs.append(hist)
            global_storage = base / channel / "globalStorage"
            if global_storage.is_dir():
                dirs.append(global_storage)
    return dirs


class WindsurfAdapter(BaseAdapter):
    name = "windsurf"

    def is_available(self) -> bool:
        return any((base / ch).exists() for base in CODEIUM_DIRS for ch in CHANNELS)

    def list_sessions(self) -> list[Session]:
        if not self.is_available():
            return []
        sessions = []
        for hist_dir in _find_history_dirs():
            for f in hist_dir.rglob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
                    if isinstance(data, dict):
                        sid = data.get("id", data.get("session_id", f.stem))
                        sessions.append(
                            Session(
                                session_id=str(sid),
                                agent="windsurf",
                                directory=data.get("workspace", data.get("directory", "")),
                                title=data.get("title", ""),
                                first_prompt=data.get("prompt", data.get("query", ""))[:150],
                                start_time=data.get("timestamp", data.get("created_at", "")),
                                status="imported",
                            )
                        )
                except (json.JSONDecodeError, OSError):
                    continue
            for f in hist_dir.rglob("*.jsonl"):
                try:
                    first_line = f.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
                    if first_line.strip():
                        data = json.loads(first_line)
                        sessions.append(
                            Session(
                                session_id=data.get("id", f.stem),
                                agent="windsurf",
                                directory=data.get("workspace", ""),
                                title=data.get("title", ""),
                                start_time=data.get("timestamp", ""),
                                status="imported",
                            )
                        )
                except (json.JSONDecodeError, OSError):
                    continue
        sessions.sort(key=lambda s: s.start_time, reverse=True)
        return sessions

    def deep_search(self, query: str) -> list[Session]:
        if not self.is_available():
            return []
        query_lower = query.lower()
        matches = []
        for hist_dir in _find_history_dirs():
            for f in hist_dir.rglob("*"):
                if f.suffix not in (".json", ".jsonl", ".txt", ".log"):
                    continue
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    if query_lower in content.lower():
                        matches.append(
                            Session(
                                session_id=f.stem,
                                agent="windsurf",
                                directory=str(f.parent),
                                start_time="",
                                status="native",
                            )
                        )
                except OSError:
                    continue
        return matches[:30]
