from abc import ABC, abstractmethod
from pathlib import Path

from web_intel.models.crawl_result import CrawlResult
from web_intel.models.session import Session


class BaseStorage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def save_crawl_result(
        self, result: CrawlResult, format: str = "markdown"
    ) -> str:
        """
        Save crawl result and return ID.

        Args:
            result: CrawlResult to save
            format: Output format (markdown, json, html)

        Returns:
            str: Unique identifier for saved result
        """
        pass

    @abstractmethod
    async def load_crawl_result(self, result_id: str) -> CrawlResult:
        """
        Load crawl result by ID.

        Args:
            result_id: Unique identifier

        Returns:
            CrawlResult instance
        """
        pass

    @abstractmethod
    async def load_content_from_path(self, path: Path) -> str:
        """
        Load content from a file path.

        Args:
            path: Path to content file

        Returns:
            str: File content
        """
        pass

    @abstractmethod
    async def save_session(self, session: Session) -> None:
        """
        Save conversation session.

        Args:
            session: Session to save
        """
        pass

    @abstractmethod
    async def load_session(self, session_id: str) -> Session:
        """
        Load conversation session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session instance
        """
        pass

    @abstractmethod
    async def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if exists
        """
        pass
