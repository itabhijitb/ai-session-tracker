"""Unified data models shared across all adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


def normalize_timestamp(value) -> str:
    """Normalize epoch (s/ms) or ISO timestamps to local time 'YYYY-MM-DD HH:MM:SS'.

    Agents store times differently (Claude Code: UTC ISO with 'Z', Devin: local
    'YYYY-MM-DD HH:MM:SS', some: epoch millis). A single format keeps sorting and
    date filtering correct across agents. Unparseable values are returned as-is.
    """
    if value is None or value == "":
        return ""
    try:
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().isdigit()):
            ts = float(value)
            dt = datetime.fromtimestamp(ts / 1000 if ts > 1e11 else ts)
        else:
            dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                dt = dt.astimezone().replace(tzinfo=None)
    except (ValueError, OverflowError, OSError):
        return str(value)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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
        for tag in (
            "<local-command-caveat>",
            "<command-name>",
            "<command-message>",
            "<command-args>",
            "<local-command-stdout>",
        ):
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

    def __post_init__(self):
        self.start_time = normalize_timestamp(self.start_time)

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

    def __post_init__(self):
        self.start_time = normalize_timestamp(self.start_time)
        self.end_time = normalize_timestamp(self.end_time)

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
            d = "~" + d[len(home) :]
        return d[-45:] if len(d) > 45 else d
