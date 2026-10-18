# ai-session-tracker — Cold Start Blueprint

> Give this entire document to Devin (or any AI coding agent) to recreate the project from scratch.
> Contains every source file, ecosystem integration, and session context needed for a clean rebuild.

---

## SESSION CONTEXT

### What this project is

A cross-platform Python CLI tool (`ais`) that provides unified full-text search across
AI coding agent sessions. Instead of searching each agent's history separately, `ais`
indexes them all into one SQLite FTS5 database and lets you search, list, preview, and
filter sessions from a single command.

### Supported agents

| Agent | Local storage it reads | Resume method |
|-------|----------------------|---------------|
| Devin CLI | `~/.local/share/devin/cli/sessions.db` (SQLite) | `devin -r <session-id>` |
| Claude Code | `~/.claude/projects/<dir>/<id>.jsonl` (JSONL) | `/resume` inside Claude Code |
| Cursor | `~/Library/Application Support/Cursor/` (state.vscdb SQLite) | Open Cursor session history |
| Windsurf | `~/.codeium/windsurf/` (JSON/JSONL) | Open Windsurf session history |

### Key design decisions

1. **Adapter pattern** — one adapter per agent, each reads native local storage. Adding a new agent = one new file + register in `ALL_ADAPTERS`.
2. **SQLite FTS5 for search** — zero external dependencies, built into Python's `sqlite3`. Works on all platforms.
3. **Auto-index on first run** — no manual `ais index` step needed for first-time users.
4. **Deep search fallback** — if FTS5 title search returns nothing, automatically searches full conversation content.
5. **3-char minimum on deep search** — prevents false positives from overly short queries.
6. **Platform-aware paths** — each adapter resolves macOS, Linux, and Windows paths correctly.
7. **No Status column** — removed because all sessions show "imported" (backfilled, not live-tracked). Adds no value.
8. **`>>>` latest marker** — every result set marks the most recent session and shows agent-specific resume commands.

### Ecosystem integration

The `devin-sessions` shell wrapper (`~/.config/devin/scripts/devin-sessions`) was converted to a thin wrapper that delegates to `ais`. This means existing muscle memory (`devin-sessions search "query"`) still works but now searches all agents. The session hook (`session_hook.sh`) still uses `session_db.py` for write operations (start/prompt/end) since `ais` is read-only.

---

## PROMPT

```
Create a Python CLI tool called `ai-session-tracker` (command: `ais`) that provides
unified search across AI coding agent sessions — Devin, Claude Code, Cursor, and Windsurf.

Requirements:
1. Installable via `pip install -e .` with entry point `ais`
2. Uses hatchling as build backend
3. Dependencies: click>=8.1, rich>=13.0 (no others)
4. Python 3.10+
5. Works on Mac, Windows, and Linux

Architecture:
- Adapter pattern: one adapter per agent, each reads that agent's native local storage
- Unified SQLite FTS5 index for fast full-text search
- CLI built with click, tables rendered with rich

Agent storage locations:
- Devin: ~/.local/share/devin/cli/sessions.db (SQLite with sessions + message_nodes tables)
  Windows: %APPDATA%/devin/cli/sessions.db
- Claude Code: ~/.claude/projects/<encoded-dir>/<session-id>.jsonl (JSONL, one line per message)
  History index: ~/.claude/history.jsonl
- Cursor: ~/Library/Application Support/Cursor/ (Mac), %APPDATA%/Cursor (Win), ~/.config/Cursor (Linux)
  Uses state.vscdb (SQLite) with ItemTable for chat/composer data
- Windsurf: ~/.codeium/windsurf/ (all platforms)
  Windows also: %APPDATA%/Codeium/Windsurf/
  JSON/JSONL files under code_tracker/history/

CLI commands:
- `ais search <query>` — FTS5 search, auto-fallback to deep search if no results
- `ais search --deep <query>` — search full conversation content
- `ais search --since "last week" <query>` — time filtering with natural language dates
- `ais list` — list recent sessions, supports --agent, --dir, --since, --before
- `ais preview <session-id>` — show conversation flow without resuming
- `ais status` — show which agents are detected, session counts, storage paths
- `ais index` — rebuild the unified search index

UX requirements:
- >>> marker on the most recent session in every result table
- Agent-specific resume commands in footer (devin -r <id>, claude /resume, etc.)
- Auto-index on first run (no manual `ais index` needed)
- Helpful "No Results" panel with suggestions
- Examples in every --help command
- Natural date parsing: "today", "yesterday", "last week", "3 days ago", ISO dates
- Minimum 3-char query guard on deep search to avoid false positives

Create all files listed below with their exact contents. Then run:
  pip install -e .
  python -m pytest tests/ -v
  ais status
  ais --help
```

---

## DIRECTORY STRUCTURE

```
ai-session-tracker/
    .gitignore
    LICENSE
    Makefile
    README.md
    install.sh
    install.ps1
    pyproject.toml
    src/ai_session_tracker/
        __init__.py
        cli.py
        models.py
        adapters/
            __init__.py
            base.py
            devin.py
            claude_code.py
            cursor.py
            windsurf.py
        index/
            __init__.py
            engine.py
    tests/
        __init__.py
        test_engine.py
```

---

## FILE CONTENTS

### .gitignore

```
__pycache__/
*.egg-info/
dist/
build/
.pytest_cache/
*.pyc
.config/ai-session-tracker/
```

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ai-session-tracker"
version = "0.1.0"
description = "Unified session search across AI coding agents (Devin, Claude Code, Cursor, Windsurf)"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [{ name = "Abhijit Bhattacharya" }]
keywords = ["ai", "coding-agent", "session", "search", "devin", "claude", "cursor", "windsurf"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "click>=8.1,<9",
    "rich>=13.0,<14",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov", "ruff"]

[project.scripts]
ais = "ai_session_tracker.cli:main"

[project.urls]
Homepage = "https://github.com/abhijit-bhattacharya/ai-session-tracker"
Repository = "https://github.com/abhijit-bhattacharya/ai-session-tracker"

[tool.hatch.build.targets.wheel]
packages = ["src/ai_session_tracker"]

[tool.ruff]
line-length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### LICENSE

```
MIT License

Copyright (c) 2026 Abhijit Bhattacharya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Makefile

```makefile
.PHONY: install dev test lint build publish clean

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

build: clean
	pip install build
	python -m build

publish-test: build
	pip install twine
	twine upload --repository testpypi dist/*

publish: build
	pip install twine
	twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### install.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== ai-session-tracker installer ==="
echo ""

PYTHON=${PYTHON:-python3}
PY_VER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10+ required (found $PY_VER)"
    exit 1
fi
echo "[ok] Python $PY_VER"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    echo "[..] Installing from local source..."
    $PYTHON -m pip install "$SCRIPT_DIR" --quiet
else
    echo "[..] Installing from PyPI..."
    $PYTHON -m pip install ai-session-tracker --quiet
fi
echo "[ok] Package installed"

if command -v ais &>/dev/null; then
    echo "[ok] 'ais' command available"
else
    AIS_PATH=$($PYTHON -c "import sysconfig; print(sysconfig.get_path('scripts'))")/ais
    if [ -f "$AIS_PATH" ]; then
        echo "[!!] 'ais' installed at $AIS_PATH but not in PATH"
        echo "     Add this to your shell profile:"
        echo "     export PATH=\"$($PYTHON -c 'import sysconfig; print(sysconfig.get_path("scripts"))'):\$PATH\""
    else
        echo "[!!] 'ais' command not found in PATH. You may need to restart your shell."
    fi
fi

echo ""
echo "[..] Building initial index..."
ais index 2>/dev/null || $PYTHON -m ai_session_tracker.cli index
echo ""
echo "[ok] Setup complete!"
echo ""
echo "Usage:"
echo "  ais search 'keyword'        Search across all AI agent sessions"
echo "  ais search -d 'keyword'     Deep search (full conversation content)"
echo "  ais search -a devin 'key'   Search only Devin sessions"
echo "  ais list                    List recent sessions"
echo "  ais list -a claude-code     List only Claude Code sessions"
echo "  ais status                  Show detected agents"
echo "  ais index                   Rebuild the search index"
```

### install.ps1

```powershell
# ai-session-tracker installer for Windows
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "=== ai-session-tracker installer ===" -ForegroundColor Cyan
Write-Host ""

try {
    $pyVer = python --version 2>&1
    Write-Host "[ok] $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path "$scriptDir\pyproject.toml") {
    Write-Host "[..] Installing from local source..."
    python -m pip install $scriptDir --quiet
} else {
    Write-Host "[..] Installing from PyPI..."
    python -m pip install ai-session-tracker --quiet
}
Write-Host "[ok] Package installed" -ForegroundColor Green

$aisPath = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
if (Get-Command ais -ErrorAction SilentlyContinue) {
    Write-Host "[ok] 'ais' command available" -ForegroundColor Green
} else {
    Write-Host "[!!] 'ais' installed at $aisPath but not in PATH" -ForegroundColor Yellow
    Write-Host "     Add to PATH: $aisPath"
}

Write-Host ""
Write-Host "[..] Building initial index..."
try {
    ais index
} catch {
    python -m ai_session_tracker.cli index
}

Write-Host ""
Write-Host "[ok] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:"
Write-Host "  ais search 'keyword'        Search across all AI agent sessions"
Write-Host "  ais search -d 'keyword'     Deep search (full conversation content)"
Write-Host "  ais list                    List recent sessions"
Write-Host "  ais status                  Show detected agents"
Write-Host "  ais index                   Rebuild the search index"
```

### src/ai_session_tracker/__init__.py

```python
"""ai-session-tracker: Unified session search across AI coding agents."""

__version__ = "0.1.0"
```

### src/ai_session_tracker/models.py

```python
"""Unified data models shared across all adapters."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # user | assistant | system
    content: str
    timestamp: str = ""

    @property
    def short_content(self) -> str:
        """First 200 chars, stripped of XML tags and whitespace."""
        text = self.content.strip()
        for tag in ("<local-command-caveat>", "<command-name>", "<command-message>",
                     "<command-args>", "<local-command-stdout>"):
            if text.startswith(tag):
                return ""
        if len(text) > 200:
            return text[:200] + "..."
        return text


@dataclass
class SessionPreview:
    """Conversation preview for a session."""

    session_id: str
    agent: str
    title: str
    directory: str
    start_time: str
    messages: list[Message] = field(default_factory=list)
    total_messages: int = 0

    @property
    def user_messages(self) -> list[Message]:
        return [m for m in self.messages if m.role == "user" and m.short_content]

    @property
    def assistant_messages(self) -> list[Message]:
        return [m for m in self.messages if m.role == "assistant" and m.short_content]


@dataclass
class Session:
    """Normalized session record — agent-agnostic."""

    session_id: str
    agent: str  # devin | claude-code | cursor | windsurf
    directory: str
    title: str = ""
    first_prompt: str = ""
    start_time: str = ""
    end_time: str = ""
    status: str = "unknown"
    message_count: int = 0
    extra: dict = field(default_factory=dict)

    @property
    def display_title(self) -> str:
        return self.title or self.first_prompt or "(untitled)"

    @property
    def short_id(self) -> str:
        return self.session_id[:20]

    @property
    def short_dir(self) -> str:
        d = self.directory
        home = str(__import__("pathlib").Path.home())
        if d.startswith(home):
            d = "~" + d[len(home):]
        return d[-45:] if len(d) > 45 else d
```

### src/ai_session_tracker/adapters/__init__.py

```python
"""Agent adapters — each knows how to read one agent's local session storage."""

from ai_session_tracker.adapters.base import BaseAdapter
from ai_session_tracker.adapters.devin import DevinAdapter
from ai_session_tracker.adapters.claude_code import ClaudeCodeAdapter
from ai_session_tracker.adapters.windsurf import WindsurfAdapter
from ai_session_tracker.adapters.cursor import CursorAdapter

ALL_ADAPTERS: list[type[BaseAdapter]] = [
    DevinAdapter,
    ClaudeCodeAdapter,
    WindsurfAdapter,
    CursorAdapter,
]

__all__ = [
    "BaseAdapter",
    "DevinAdapter",
    "ClaudeCodeAdapter",
    "WindsurfAdapter",
    "CursorAdapter",
    "ALL_ADAPTERS",
]
```

### src/ai_session_tracker/adapters/base.py

```python
"""Base adapter interface that every agent adapter must implement."""

from __future__ import annotations

import abc

from ai_session_tracker.models import Session, SessionPreview


class BaseAdapter(abc.ABC):
    """Read sessions from one AI coding agent's local storage."""

    name: str = "unknown"

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Return True if this agent's data exists on the current machine."""

    @abc.abstractmethod
    def list_sessions(self) -> list[Session]:
        """Return all discoverable sessions (metadata only, lightweight)."""

    @abc.abstractmethod
    def deep_search(self, query: str) -> list[Session]:
        """Search full conversation content for the query string."""

    def preview(self, session_id: str) -> SessionPreview | None:
        """Return a conversation preview for a specific session. Override in subclasses."""
        return None

    def status(self) -> dict:
        """Return a summary of this adapter's state."""
        available = self.is_available()
        count = len(self.list_sessions()) if available else 0
        return {"agent": self.name, "available": available, "sessions": count}
```

### src/ai_session_tracker/adapters/devin.py

```python
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
```

### src/ai_session_tracker/adapters/claude_code.py

```python
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
```

### src/ai_session_tracker/adapters/cursor.py

```python
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
                if folder.startswith("file://"):
                    folder = folder[7:]
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
                                        first_msg = (m.get("text", m.get("content", "")) if isinstance(m, dict) else str(m))[:150]
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
```

### src/ai_session_tracker/adapters/windsurf.py

```python
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
        return any(
            (base / ch).exists() for base in CODEIUM_DIRS for ch in CHANNELS
        )

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
```

### src/ai_session_tracker/index/__init__.py

```python
"""Unified FTS5 search index."""
```

### src/ai_session_tracker/index/engine.py

```python
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
```

### src/ai_session_tracker/cli.py

```python
"""CLI entry point — installed as `ais` command."""

from __future__ import annotations

from datetime import datetime, timedelta
import re

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ai_session_tracker.index.engine import SearchEngine
from ai_session_tracker.models import Session, SessionPreview

console = Console()

RESUME_COMMANDS = {
    "devin": "devin -r {id}",
    "claude-code": "claude --resume (use /resume in Claude Code)",
    "cursor": "Open Cursor and use session history",
    "windsurf": "Open Windsurf and use session history",
}


def _resume_hint(session: Session) -> str:
    template = RESUME_COMMANDS.get(session.agent, f"Resume using {session.agent}")
    return template.format(id=session.session_id)


def _render_table(sessions: list[Session], title: str = "Sessions"):
    if not sessions:
        console.print(Panel(
            "[yellow]No matching sessions found.[/yellow]\n\n"
            "Suggestions:\n"
            "  - Try broader keywords:  [bold]ais search pipeline[/bold]\n"
            "  - Search inside conversations:  [bold]ais search --deep \"exact phrase\"[/bold]\n"
            "  - Rebuild the index:  [bold]ais index[/bold]\n"
            "  - Check detected agents:  [bold]ais status[/bold]",
            title="No Results",
            border_style="yellow",
        ))
        return

    from pathlib import Path
    home = str(Path.home())

    t = Table(title=title, show_lines=False, pad_edge=False)
    t.add_column("#", style="bold yellow", no_wrap=True)
    t.add_column("Agent", style="cyan", no_wrap=True)
    t.add_column("Session ID", style="bold", no_wrap=True)
    t.add_column("Directory")
    t.add_column("Title / First Prompt")
    t.add_column("Started", no_wrap=True)

    for i, s in enumerate(sessions):
        marker = ">>>" if i == 0 else str(i + 1)

        display = s.title or s.first_prompt or "(untitled)"
        if len(display) > 35:
            display = display[:35] + ".."

        d = s.directory
        if d.startswith(home):
            d = "~" + d[len(home):]
        if len(d) > 40:
            d = ".." + d[-38:]

        row_style = "bold" if i == 0 else ""
        t.add_row(
            marker,
            s.agent,
            s.session_id[:20],
            d,
            display,
            s.start_time[:19] if s.start_time else "",
            style=row_style,
        )
    console.print(t)

    latest = sessions[0]
    console.print()
    console.print(f"  [bold yellow]>>>[/bold yellow] = most recent session")
    console.print(f"  [bold]To resume latest:[/bold] [green]{_resume_hint(latest)}[/green]")
    console.print(f"  [dim]To resume any other: replace the session ID in the command above[/dim]")


def _parse_date(value: str) -> str | None:
    v = value.strip().lower()
    now = datetime.now()

    if v == "today":
        return now.strftime("%Y-%m-%d")
    if v == "yesterday":
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    if v == "last week":
        return (now - timedelta(weeks=1)).strftime("%Y-%m-%d")
    if v == "last month":
        return (now - timedelta(days=30)).strftime("%Y-%m-%d")

    m = re.match(r"(\d+)\s+(day|week|month)s?\s+ago", v)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit == "day":
            return (now - timedelta(days=n)).strftime("%Y-%m-%d")
        elif unit == "week":
            return (now - timedelta(weeks=n)).strftime("%Y-%m-%d")
        elif unit == "month":
            return (now - timedelta(days=n * 30)).strftime("%Y-%m-%d")

    if re.match(r"\d{4}-\d{2}-\d{2}", v):
        return v[:10]

    return None


def _filter_by_time(sessions: list[Session], since: str | None, before: str | None) -> list[Session]:
    filtered = sessions
    if since:
        since_date = _parse_date(since)
        if since_date:
            filtered = [s for s in filtered if s.start_time[:10] >= since_date]
    if before:
        before_date = _parse_date(before)
        if before_date:
            filtered = [s for s in filtered if s.start_time[:10] <= before_date]
    return filtered


def _auto_index_if_empty(engine: SearchEngine) -> bool:
    sessions = engine.list_sessions(limit=1)
    if sessions:
        return False
    console.print("[dim]First run detected — building index from all agents...[/dim]")
    counts = engine.reindex()
    total = sum(counts.values())
    if total > 0:
        console.print(f"[green]Indexed {total} sessions.[/green]\n")
    else:
        console.print(
            "[yellow]No sessions found. Make sure you have at least one AI agent "
            "(Devin, Claude Code, Cursor, or Windsurf) installed and have used it.[/yellow]\n"
        )
    return True


@click.group()
@click.version_option(package_name="ai-session-tracker")
def main():
    """ais — Find any past AI coding session in seconds.

    Works across Devin, Claude Code, Cursor, and Windsurf.
    Searches session titles, first prompts, and (with --deep) full conversations.

    Quick start:

      ais search "pipeline debug"      Find sessions by keyword

      ais preview <session-id>         See what happened in a session

      ais list --since "last week"     Recent sessions with time filter

      ais status                       See which agents are detected

    """


@main.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--agent", "-a", default=None,
              help="Only search one agent: devin, claude-code, cursor, or windsurf")
@click.option("--deep", "-d", is_flag=True,
              help="Search inside full conversations, not just titles (slower but thorough)")
@click.option("--since", "-s", default=None,
              help='Only show sessions after this date: "2026-10-01", "last week", "3 days ago"')
@click.option("--before", "-b", default=None,
              help='Only show sessions before this date: "2026-10-01", "yesterday"')
@click.option("--limit", "-n", default=30, help="Maximum number of results to show")
def search(query: tuple[str, ...], agent: str | None, deep: bool,
           since: str | None, before: str | None, limit: int):
    """Search your AI coding sessions by keyword.

    Searches session titles and first prompts. If nothing is found, automatically
    searches inside full conversation content as a fallback.

    \b
    Examples:
      ais search pipeline debug
      ais search --deep "config.yaml"
      ais search --agent devin "IPS shuffle"
      ais search --since "last week" pipeline
      ais search --since 2026-10-01 --before 2026-10-15 debug
    """
    q = " ".join(query)
    engine = SearchEngine()
    _auto_index_if_empty(engine)

    if deep:
        results = engine.deep_search(q, agent=agent, limit=limit)
        title = f"Results for '{q}' (full conversation search)"
    else:
        results = engine.search(q, agent=agent, limit=limit)
        if not results:
            results = engine.deep_search(q, agent=agent, limit=limit)
            if results:
                console.print(
                    "[dim]No match in titles — searched inside full conversations instead.[/dim]\n"
                )
        title = f"Results for '{q}'"

    if since or before:
        results = _filter_by_time(results, since, before)
        if since:
            title += f" (since {_parse_date(since)})"
        if before:
            title += f" (before {_parse_date(before)})"

    _render_table(results, title=title)


@main.command(name="list")
@click.option("--agent", "-a", default=None,
              help="Only list one agent: devin, claude-code, cursor, or windsurf")
@click.option("--dir", "-d", "directory", default=None,
              help="Only show sessions from this folder (partial match works)")
@click.option("--since", "-s", default=None,
              help='Only show sessions after this date: "2026-10-01", "last week", "3 days ago"')
@click.option("--before", "-b", default=None,
              help='Only show sessions before this date: "2026-10-01", "yesterday"')
@click.option("--limit", "-n", default=30, help="Maximum number of results to show")
def list_sessions(agent: str | None, directory: str | None,
                  since: str | None, before: str | None, limit: int):
    """List your recent AI coding sessions.

    Shows the most recent sessions across all agents, newest first.

    \b
    Examples:
      ais list
      ais list --agent devin
      ais list --dir ~/Projects/my-repo
      ais list --since "last week"
      ais list --since "3 days ago" --agent devin
    """
    engine = SearchEngine()
    _auto_index_if_empty(engine)
    results = engine.list_sessions(agent=agent, directory=directory, limit=limit)
    title = "Recent Sessions"
    if since or before:
        results = _filter_by_time(results, since, before)
        if since:
            title += f" (since {_parse_date(since)})"
        if before:
            title += f" (before {_parse_date(before)})"
    _render_table(results, title=title)


@main.command()
@click.argument("session_id", required=True)
@click.option("--agent", "-a", default=None,
              help="Specify the agent if session ID exists in multiple agents")
@click.option("--messages", "-m", default=20,
              help="Number of conversation turns to show (default: 20)")
def preview(session_id: str, agent: str | None, messages: int):
    """Preview what happened in a session without resuming it.

    Shows the conversation flow: what you asked and what the agent answered.

    \b
    Examples:
      ais preview pewter-snowshoe
      ais preview --agent devin harmonious-sync
      ais preview --messages 50 pewter-snowshoe
    """
    engine = SearchEngine()
    result = engine.preview(session_id, agent=agent)

    if not result:
        console.print(Panel(
            f"[yellow]Session '{session_id}' not found.[/yellow]\n\n"
            "Suggestions:\n"
            f"  - Check the ID: [bold]ais search \"{session_id[:10]}\"[/bold]\n"
            "  - Specify the agent: [bold]ais preview --agent devin <id>[/bold]\n"
            "  - Rebuild the index: [bold]ais index[/bold]",
            title="Session Not Found",
            border_style="yellow",
        ))
        return

    from pathlib import Path
    home = str(Path.home())
    d = result.directory
    if d.startswith(home):
        d = "~" + d[len(home):]

    console.print(Panel(
        f"[bold]Session:[/bold] {result.session_id}\n"
        f"[bold]Agent:[/bold] {result.agent}\n"
        f"[bold]Directory:[/bold] {d}\n"
        f"[bold]Title:[/bold] {result.title or '(untitled)'}\n"
        f"[bold]Started:[/bold] {result.start_time}\n"
        f"[bold]Messages:[/bold] {result.total_messages} total "
        f"({len(result.user_messages)} from you, {len(result.assistant_messages)} from agent)",
        title="Session Info",
        border_style="blue",
    ))

    console.print()
    shown = 0
    for msg in result.messages:
        text = msg.short_content
        if not text:
            continue
        if shown >= messages:
            remaining = result.total_messages - shown
            if remaining > 0:
                console.print(f"\n[dim]... {remaining} more messages. "
                              f"Use --messages {result.total_messages} to see all.[/dim]")
            break

        if msg.role == "user":
            console.print(f"\n  [bold cyan]You:[/bold cyan] {text}")
        else:
            console.print(f"\n  [bold green]Agent:[/bold green] {text}")
        shown += 1

    console.print()
    hint = _resume_hint(Session(
        session_id=result.session_id, agent=result.agent, directory=result.directory))
    console.print(f"  [bold]To resume:[/bold] [green]{hint}[/green]")


@main.command()
def status():
    """Check which AI agents are installed and how many sessions each has.

    \b
    Example:
      ais status
    """
    engine = SearchEngine()

    t = Table(title="Detected AI Agents", show_lines=False)
    t.add_column("Agent", style="bold", width=15)
    t.add_column("Installed?", width=12)
    t.add_column("Sessions", justify="right", width=10)
    t.add_column("Where it stores data", width=50)

    agent_paths = {
        "devin": "~/.local/share/devin/cli/sessions.db",
        "claude-code": "~/.claude/projects/**/*.jsonl",
        "cursor": "~/Library/Application Support/Cursor/ (Mac) or %APPDATA%\\Cursor (Win)",
        "windsurf": "~/.codeium/windsurf/",
    }

    for s in engine.status():
        available = "[green]yes[/green]" if s["available"] else "[red]no[/red]"
        path = agent_paths.get(s["agent"], "unknown")
        t.add_row(s["agent"], available, str(s["sessions"]), f"[dim]{path}[/dim]")

    console.print(t)
    console.print()
    console.print("[dim]Agents marked 'no' are either not installed or have no session history yet.[/dim]")


@main.command()
def index():
    """Rebuild the search index from all installed agents.

    Run this after installing a new agent, or if search results seem incomplete.
    This reads each agent's session data and builds a unified search index.

    \b
    Example:
      ais index
    """
    engine = SearchEngine()
    with console.status("[bold]Reading sessions from all agents..."):
        counts = engine.reindex()

    t = Table(title="Index Complete", show_lines=False)
    t.add_column("Agent", style="bold", width=15)
    t.add_column("Sessions Found", justify="right", width=18)

    total = 0
    for agent_name, count in counts.items():
        t.add_row(agent_name, str(count))
        total += count
    t.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")

    console.print(t)
    console.print(f"\n[dim]Index saved to: {engine.db_path}[/dim]")

    if total == 0:
        console.print(
            "\n[yellow]No sessions found. Make sure you have used at least one "
            "supported agent (Devin, Claude Code, Cursor, or Windsurf).[/yellow]"
        )
    else:
        console.print(f"\n[green]Ready! Try:[/green] ais search \"your keyword\"")


if __name__ == "__main__":
    main()
```

### tests/__init__.py

```python
```

### tests/test_engine.py

```python
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
```

---

## VERIFICATION AFTER CREATION

Run these commands to verify the project was created correctly:

```bash
cd ai-session-tracker
pip install -e ".[dev]"
python -m pytest tests/ -v          # Expect 6/6 passed
ais --help                           # Should show quick start guide
ais search --help                    # Should show examples
ais preview --help                   # Should show examples
ais status                           # Should detect installed agents
ais index                            # Should build the search index
ais search "test"                    # Should return results (if any agent has sessions)
```

---

## ECOSYSTEM FILES (outside the project directory)

These files live in the user's Devin config and integrate `ais` into the Devin workflow.
They are optional — `ais` works standalone without them.

### ~/.config/devin/scripts/devin-sessions

> Thin wrapper that routes legacy `devin-sessions` commands to `ais`.
> Place at `~/.config/devin/scripts/devin-sessions` and `chmod +x`.

```bash
#!/usr/bin/env bash
# devin-sessions — now a thin wrapper around `ais` (ai-session-tracker).
#
# `ais` provides unified search across Devin, Claude Code, Cursor, and Windsurf.
# This wrapper translates old devin-sessions commands to ais equivalents.

DB_SCRIPT="$HOME/.config/devin/scripts/session_db.py"

if ! command -v ais &>/dev/null; then
    echo "Error: 'ais' command not found."
    echo "Install it:  pip install -e ~/Projects/ai-session-tracker"
    echo "Falling back to legacy session_db.py..."
    python3 "$DB_SCRIPT" "$@"
    exit $?
fi

if [ $# -eq 0 ]; then
    echo "devin-sessions — now powered by ais (ai-session-tracker)"
    echo ""
    echo "Commands:"
    echo "  search <keyword>         Search across all AI agents (Devin, Claude Code, ...)"
    echo "  deep-search <keyword>    Search full conversation content"
    echo "  list [--all]             List recent sessions"
    echo "  preview <session-id>     See what happened in a session"
    echo "  status                   Show detected agents and session counts"
    echo "  backfill / index         Rebuild the search index"
    echo "  active                   Show sessions that haven't ended (legacy)"
    echo ""
    echo "Tip: You can also use 'ais' directly for more options."
    exit 0
fi

CMD="$1"
shift

case "$CMD" in
    search)
        ais search "$@"
        ;;
    deep-search)
        ais search --deep "$@"
        ;;
    list)
        ais list "$@"
        ;;
    preview)
        ais preview "$@"
        ;;
    status)
        ais status
        ;;
    backfill|index)
        ais index
        ;;
    active)
        # Legacy — still uses session_db.py since ais doesn't track active state
        python3 "$DB_SCRIPT" active
        ;;
    # Hook operations — still handled by session_db.py
    start|prompt|title|end|init)
        python3 "$DB_SCRIPT" "$CMD" "$@"
        ;;
    *)
        echo "Unknown command: $CMD"
        echo "Run 'devin-sessions' with no arguments to see available commands."
        exit 1
        ;;
esac
```

### ~/.config/devin/skills/session-search/SKILL.md

> Devin skill that teaches the agent to use `ais` for session searches.

```markdown
---
name: session-search
description: Search past AI coding sessions by keyword, directory, or topic. Works across Devin, Claude Code, Cursor, and Windsurf.
argument-hint: "<search query>"
allowed-tools:
  - exec
  - read
triggers:
  - user
  - model
---

# Session Search

Search or list AI coding sessions using the `ais` command (ai-session-tracker).
Covers Devin, Claude Code, Cursor, and Windsurf sessions.

## Prerequisites

`ais` must be installed: `pip install -e ~/Projects/ai-session-tracker`

## Steps

### 1. Search by keyword
ais search "<USER_QUERY>"

### 2. Deep search (full conversation content)
ais search --deep "<USER_QUERY>"

### 3. Search a specific agent
ais search --agent devin "<USER_QUERY>"
ais search --agent claude-code "<USER_QUERY>"

### 4. Search by time
ais search --since "last week" "<USER_QUERY>"
ais list --since 2026-10-01

### 5. List recent sessions
ais list
ais list --agent devin

### 6. Preview a session
ais preview <session-id>

### 7. Present results
The output includes:
- >>> marker on the most recent session
- Agent name (devin, claude-code, cursor, windsurf)
- Session ID, Directory, Title, Start time
- Agent-specific resume command

Resume commands by agent:
- Devin: devin -r <session-id>
- Claude Code: use /resume inside Claude Code
- Cursor: open Cursor and use session history
- Windsurf: open Windsurf and use session history
```

---

## SETUP ON A NEW MACHINE

```bash
# 1. Clone or copy the project
git clone <repo-url> ~/Projects/ai-session-tracker
# Or: copy this entire COLD_START.md and have an AI agent recreate all files

# 2. Install
cd ~/Projects/ai-session-tracker
pip install -e ".[dev]"

# 3. Verify
python -m pytest tests/ -v          # 6/6 should pass
ais --help                           # Shows quick start guide
ais status                           # Detects installed agents
ais index                            # Builds the search index

# 4. (Optional) Set up devin-sessions wrapper
mkdir -p ~/.config/devin/scripts
cp <devin-sessions-content-above> ~/.config/devin/scripts/devin-sessions
chmod +x ~/.config/devin/scripts/devin-sessions

# 5. (Optional) Set up Devin skill
mkdir -p ~/.config/devin/skills/session-search
cp <skill-content-above> ~/.config/devin/skills/session-search/SKILL.md
```
