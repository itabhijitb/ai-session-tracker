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
