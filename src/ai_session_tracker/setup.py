"""Post-installation setup script — updates AGENTS.md across detected agents."""

from __future__ import annotations

import re
from pathlib import Path

from ai_session_tracker.adapters import ALL_ADAPTERS

SECTION_HEADER = "## ais (ai-session-tracker)"

# agent name -> (AGENTS.md path, default file header, agent-specific closing line)
AGENT_TARGETS = {
    "devin": (
        Path.home() / ".config" / "devin" / "AGENTS.md",
        "# Devin AGENTS\n",
        "**Resume**: Use `devin -r <session-id>` to resume sessions found by `ais`.",
    ),
    "claude-code": (
        Path.home() / ".claude" / "AGENTS.md",
        "# Claude Code AGENTS\n",
        "**Resume**: Use `/resume` inside Claude Code to resume sessions found by `ais`.",
    ),
}


def _ais_section(resume_line: str) -> str:
    return f"""{SECTION_HEADER}

Unified session search across AI coding agents (Devin, Claude Code, Cursor, Windsurf).

**Installation**: `pip install ai-session-tracker`

**Commands**:
- `ais search "keyword"` — Search across all AI agent sessions
- `ais search --deep "keyword"` — Deep search (full conversation content)
- `ais search --agent claude-code "key"` — Search only one agent's sessions
- `ais list` — List recent sessions
- `ais list --agent devin` — List only Devin sessions
- `ais status` — Show detected agents
- `ais index` — Rebuild the search index
- `ais preview <session-id>` — Preview a session without resuming

{resume_line}
"""


def update_agents_md(path: Path, default_header: str, resume_line: str) -> bool:
    """Insert or refresh the ais section in an AGENTS.md file. Returns True if the file changed."""
    section = _ais_section(resume_line)
    content = path.read_text(encoding="utf-8", errors="replace") if path.exists() else default_header

    # Existing section runs from its header to the next top-level "## " heading or EOF
    pattern = re.compile(rf"^{re.escape(SECTION_HEADER)}\n.*?(?=^## |\Z)", re.DOTALL | re.MULTILINE)
    if pattern.search(content):
        new_content = pattern.sub(lambda _: section + "\n", content, count=1).rstrip("\n") + "\n"
    else:
        new_content = content.rstrip("\n") + "\n\n" + section

    if new_content == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_content, encoding="utf-8")
    return True


def setup_agents():
    """Run post-installation setup across all detected agents."""
    print("[setup] Updating AGENTS.md across detected agents...")

    for adapter_cls in ALL_ADAPTERS:
        adapter = adapter_cls()
        target = AGENT_TARGETS.get(adapter.name)
        if target and adapter.is_available():
            path, header, resume_line = target
            if update_agents_md(path, header, resume_line):
                print(f"[updated] {path}")
            else:
                print(f"[ok] {path} already up to date")

    print("[setup] AGENTS.md updates complete")


if __name__ == "__main__":
    setup_agents()
