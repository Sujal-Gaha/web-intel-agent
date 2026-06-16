from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class QueryContext:
    """
    Context for a query.

    Contains the content to analyze and metadata about the query.
    """

    content: str
    """The main content to analyze (crawled website, document, etc.)"""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the query"""

    max_tokens: int = 20_000
    """Maximum tokens to use for context"""

    conversation_history: list[dict[str, str]] = field(default_factory=list)
    """Previous messages in the conversation (for multi-turn dialogs)"""

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not self.content:
            raise ValueError("Content cannot be empty")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")


@dataclass
class QueryResult:
    """
    Result from an agent query.

    Contains the response and metadata about the generation.
    """

    response: str
    """The agent's response text"""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the response"""

    model_used: str = "unknown"
    """Name/identifier of the model that generated the response"""

    tokens_used: Optional[int] = None
    """Number of tokens used in generation (if available)"""

    finish_reason: Optional[str] = None
    """Reason why generation finished (e.g., 'stop', 'length', 'error')"""

    timestamp: datetime = field(default_factory=datetime.now)
    """When this response was generated"""

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not self.response:
            raise ValueError("Response cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dict representation of the result
        """
        return {
            "response": self.response,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "finish_reason": self.finish_reason,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueryResult":
        """
        Create QueryResult from dictionary.

        Args:
            data: Dictionary with result data

        Returns:
            QueryResult instance
        """
        return cls(
            response=data["response"],
            model_used=data.get("model_used", "unknown"),
            tokens_used=data.get("tokens_used"),
            finish_reason=data.get("finish_reason"),
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if "timestamp" in data
                else datetime.now()
            ),
            metadata=data.get("metadata", {}),
        )
