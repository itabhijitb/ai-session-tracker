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
