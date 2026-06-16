from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional

RoleLiteral = Literal["system", "user", "assistant"]


@dataclass
class Message:
    """A single message in a conversation."""

    role: RoleLiteral
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Conversation session."""

    session_id: str
    messages: list[Message] = field(default_factory=list)
    context_source: Optional[str] = None  # Path to source content
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: RoleLiteral, content: str, **metadata) -> None:
        """Add a message to the session."""
        message: Message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self.updated_at: datetime = datetime.now()

    def get_recent_messages(self, n: int = 5) -> list[dict[str, str]]:
        """
        Get recent messages formatted for context.

        Args:
            n: Number of recent messages

        Returns:
            List of dicts with 'role' and 'content'
        """
        recent: list[Message] = (
            self.messages[-n:] if len(self.messages) > n else self.messages
        )
        return [{"role": msg.role, "content": msg.content} for msg in recent]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata,
                }
                for msg in self.messages
            ],
            "context_source": self.context_source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        """Create Session from dictionary."""
        messages: list[Message] = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                metadata=msg.get("metadata", {}),
            )
            for msg in data.get("messages", [])
        ]

        return cls(
            session_id=data["session_id"],
            messages=messages,
            context_source=data.get("context_source"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )
