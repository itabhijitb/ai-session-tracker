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
