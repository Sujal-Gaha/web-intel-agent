from abc import ABC, abstractmethod
from typing import AsyncIterator

from web_intel.models.query import QueryContext, QueryResult


class BaseAgent(ABC):
    """Abstract base class for AI agents."""

    @abstractmethod
    async def query(self, prompt: str, context: QueryContext, **kwargs) -> QueryResult:
        """
        Query the agent with a prompt and context.

        Args:
            prompt: User's question/prompt
            context: QueryContext with content and metadata
            **kwargs: Additional provider-specific options

        Returns:
            QueryResult with response and metadata
        """
        pass

    @abstractmethod
    async def stream_query(
        self, prompt: str, context: QueryContext, **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream responses token by token.

        Args:
            prompt: User's question/prompt
            context: QueryContext with content and metadata
            **kwargs: Additional provider-specific options

        Yields:
            str: Token chunks as they arrive
        """
        if False:  # Never executes, but makes it a generator
            yield ""
        raise NotImplementedError("Subclass must implement stream_query")

    @abstractmethod
    def prepare_context(self, content: str, max_tokens: int) -> str:
        """
        Prepare content to fit within token limits.

        Args:
            content: Raw content to prepare
            max_tokens: Maximum token limit

        Returns:
            Prepared context string
        """
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate that the agent can connect to its backend.

        Returns:
            bool: True if connection is valid
        """
        pass
