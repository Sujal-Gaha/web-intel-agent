from pathlib import Path
from typing import Any, AsyncIterator, Optional

from web_intel.agents.base import BaseAgent
from web_intel.models.query import QueryContext, QueryResult
from web_intel.models.session import Session
from web_intel.storage.base import BaseStorage
from web_intel.utils.exceptions import AgentError, StorageError


class AgentOrchestrator:
    """
    Orchestrates agent interactions with storage and context.
    This is the high-level API that CLI commands use.
    """

    def __init__(
        self,
        agent: BaseAgent,
        storage: BaseStorage,
    ) -> None:
        """
        Initialize orchestrator.

        Args:
            agent: AI agent instance
            storage: Storage backend instance
        """
        self.agent: BaseAgent = agent
        self.storage: BaseStorage = storage

    async def query_with_source(
        self,
        prompt: str,
        source_path: Path,
        session_id: Optional[str] = None,
        max_tokens: int = 20_000,
        **agent_kwargs,
    ) -> QueryResult:
        """
        Query agent using content from a source file.

        Args:
            prompt: User question
            source_path: Path to source content file
            session_id: Optional session ID for conversation
            max_tokens: Maximum context tokens
            **agent_kwargs: Additional agent options

        Returns:
            QueryResult with response

        Raises:
            StorageError: If source cannot be loaded
            AgentError: If query fails
        """
        try:
            # Load source content
            content: str = await self.storage.load_content_from_path(source_path)

            # Load or create session
            conversation_history: list[Any] = []
            session: Optional[Session] = None
            if session_id:
                session = await self.storage.load_session(session_id)
                conversation_history = session.get_recent_messages(n=5)

            # Build context
            context: QueryContext = QueryContext(
                content=content,
                max_tokens=max_tokens,
                conversation_history=conversation_history,
                metadata={
                    "source_path": str(source_path),
                    "session_id": session_id,
                },
            )

            # Query agent
            result: QueryResult = await self.agent.query(
                prompt, context, **agent_kwargs
            )

            # Save to session if provided
            if session_id and session is not None:
                session.add_message("user", prompt)
                session.add_message("assistant", result.response)
                session.context_source = str(source_path)
                await self.storage.save_session(session)

            return result

        except StorageError:
            raise
        except AgentError:
            raise
        except Exception as e:
            raise AgentError(f"Query orchestration failed: {e}") from e

    async def stream_query(
        self,
        prompt: str,
        source_path: Path,
        session_id: Optional[str] = None,
        max_tokens: int = 20_000,
        **agent_kwargs,
    ) -> AsyncIterator[str]:
        """
        Stream query responses token by token.

        This is an async generator function.

        Args:
            prompt: User question
            source_path: Path to source content
            session_id: Optional session ID
            max_tokens: Maximum context tokens
            **agent_kwargs: Additional agent options

        Yields:
            str: Response tokens
        """
        try:
            # Load content
            content: str = await self.storage.load_content_from_path(source_path)

            # Load session if exists
            conversation_history: list[Any] = []
            session: Optional[Session] = None
            if session_id:
                session = await self.storage.load_session(session_id)
                conversation_history = session.get_recent_messages(n=5)

            # Build context
            context: QueryContext = QueryContext(
                content=content,
                max_tokens=max_tokens,
                conversation_history=conversation_history,
                metadata={
                    "source_path": str(source_path),
                    "session_id": session_id,
                },
            )

            # Stream response
            full_response = ""
            async for chunk in self.agent.stream_query(prompt, context, **agent_kwargs):
                full_response += chunk
                yield chunk

            # Save to session after streaming completes
            if session_id and session is not None:
                session.add_message("user", prompt)
                session.add_message("assistant", full_response)
                session.context_source = str(source_path)
                await self.storage.save_session(session)

        except Exception as e:
            raise AgentError(f"Stream orchestration failed: {e}") from e
