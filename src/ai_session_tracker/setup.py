"""Post-installation setup script — updates AGENTS.md across detected agents."""

from __future__ import annotations

import json
import platform
from pathlib import Path

from ai_session_tracker.adapters import ALL_ADAPTERS, BaseAdapter


def _update_devin_agents_md():
    """Update ~/.config/devin/AGENTS.md with ais information."""
    devin_agents = Path.home() / ".config" / "devin" / "AGENTS.md"
    devin_agents.parent.mkdir(parents=True, exist_ok=True)

    if devin_agents.exists():
        content = devin_agents.read_text(encoding="utf-8", errors="replace")
    else:
        content = "# Devin AGENTS\n\n"

    ais_section = """
## ais (ai-session-tracker)

Unified session search across AI coding agents (Devin, Claude Code, Cursor, Windsurf).

**Installation**: `pip install -e ~/Projects/ai-session-tracker`

**Commands**:
- `ais search "keyword"` — Search across all AI agent sessions
- `ais search --deep "keyword"` — Deep search (full conversation content)
- `ais search --agent devin "key"` — Search only Devin sessions
- `ais list` — List recent sessions
- `ais list --agent claude-code` — List only Claude Code sessions
- `ais status` — Show detected agents
- `ais index` — Rebuild the search index
- `ais preview <session-id>` — Preview a session without resuming

**Integration**: The `devin-sessions` wrapper script delegates to `ais` for search operations.
"""

    if "ais (ai-session-tracker)" not in content:
        with open(devin_agents, "a", encoding="utf-8") as f:
            f.write(ais_section)
        print(f"[updated] {devin_agents}")


def _update_claude_agents_md():
    """Update ~/.claude/AGENTS.md with ais information."""
    claude_agents = Path.home() / ".claude" / "AGENTS.md"
    claude_agents.parent.mkdir(parents=True, exist_ok=True)

    if claude_agents.exists():
        content = claude_agents.read_text(encoding="utf-8", errors="replace")
    else:
        content = "# Claude Code AGENTS\n\n"

    ais_section = """
## ais (ai-session-tracker)

Unified session search across AI coding agents (Devin, Claude Code, Cursor, Windsurf).

**Installation**: `pip install -e ~/Projects/ai-session-tracker`

**Commands**:
- `ais search "keyword"` — Search across all AI agent sessions
- `ais search --deep "keyword"` — Deep search (full conversation content)
- `ais search --agent claude-code "key"` — Search only Claude Code sessions
- `ais list` — List recent sessions
- `ais list --agent devin` — List only Devin sessions
- `ais status` — Show detected agents
- `ais index` — Rebuild the search index
- `ais preview <session-id>` — Preview a session without resuming

**Resume**: Use `/resume` inside Claude Code to resume sessions found by `ais`.
"""

    if "ais (ai-session-tracker)" not in content:
        with open(claude_agents, "a", encoding="utf-8") as f:
            f.write(ais_section)
        print(f"[updated] {claude_agents}")


def setup_agents():
    """Run post-installation setup across all detected agents."""
    print("[setup] Updating AGENTS.md across detected agents...")

    for adapter_cls in ALL_ADAPTERS:
        adapter = adapter_cls()
        if adapter.is_available():
            if adapter.name == "devin":
                _update_devin_agents_md()
            elif adapter.name == "claude-code":
                _update_claude_agents_md()

    print("[setup] AGENTS.md updates complete")


if __name__ == "__main__":
    setup_agents()
