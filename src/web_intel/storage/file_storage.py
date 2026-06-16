import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import ParseResult

import aiofiles

from web_intel.core.config import Config
from web_intel.models.crawl_result import CrawlResult, PageResult
from web_intel.models.session import Session
from web_intel.storage.base import BaseStorage
from web_intel.utils.exceptions import StorageError


class FileStorage(BaseStorage):
    """File-based storage implementation."""

    def __init__(self, config: Config) -> None:
        """
        Initialize file storage.

        Args:
            config: Application configuration
        """
        self.config: Config = config
        self.base_path: Path = Path(config.storage_path)
        self.crawls_path: Path = self.base_path / "crawls"
        self.sessions_path: Path = self.base_path / "sessions"

        # Create directories
        self.crawls_path.mkdir(parents=True, exist_ok=True)
        self.sessions_path.mkdir(parents=True, exist_ok=True)

    async def save_crawl_result(
        self, result: CrawlResult, format: str = "markdown"
    ) -> str:
        """
        Save crawl result to file.

        Args:
            result: CrawlResult to save
            format: Output format (markdown, json)

        Returns:
            str: Result ID (filename without extension)
        """
        try:
            # Generate ID from URL and timestamp
            from urllib.parse import urlparse

            parsed: ParseResult = urlparse(result.source_url)
            domain: str = parsed.netloc.replace(".", "_")
            timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_id: str = f"{domain}_{timestamp}"

            if format == "markdown":
                await self._save_as_markdown(result, result_id)
            elif format == "json":
                await self._save_as_json(result, result_id)
            else:
                raise ValueError(f"Unsupported format: {format}")

            return result_id

        except Exception as e:
            raise StorageError(f"Failed to save crawl result: {e}") from e

    async def _save_as_markdown(self, result: CrawlResult, result_id: str) -> None:
        """Save result as markdown file."""
        filepath: Path = self.crawls_path / f"{result_id}.md"

        content = f"""
            # Crawl Result: {result.source_url}

            **Crawled at:** {result.started_at.isoformat()}
            **Total pages:** {result.total_pages}
            **Success rate:** {result.success_rate:.1%}
            ---

            {result.combined_content}
        """

        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(content)

    async def _save_as_json(self, result: CrawlResult, result_id: str) -> None:
        """Save result as JSON file."""
        filepath: Path = self.crawls_path / f"{result_id}.json"

        data = {
            "source_url": result.source_url,
            "started_at": result.started_at.isoformat(),
            "completed_at": (
                result.completed_at.isoformat() if result.completed_at else None
            ),
            "total_pages": result.total_pages,
            "failed_pages": result.failed_pages,
            "crawl_depth": result.crawl_depth,
            "metadata": result.metadata,
            "pages": [
                {
                    "url": page.url,
                    "title": page.title,
                    "content": page.content,
                    "status_code": page.status_code,
                    "crawled_at": page.crawled_at.isoformat(),
                    "metadata": page.metadata,
                }
                for page in result.pages
            ],
        }

        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=2))

    async def load_crawl_result(self, result_id: str) -> CrawlResult:
        """Load crawl result from JSON file."""
        filepath: Path = self.crawls_path / f"{result_id}.json"

        if not filepath.exists():
            raise StorageError(f"Crawl result not found: {result_id}")

        try:
            async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                content: str = await f.read()
                data = json.loads(content)

            pages: list[PageResult] = [
                PageResult(
                    url=page["url"],
                    content=page["content"],
                    title=page.get("title"),
                    status_code=page.get("status_code"),
                    crawled_at=datetime.fromisoformat(page["crawled_at"]),
                    metadata=page.get("metadata", {}),
                )
                for page in data["pages"]
            ]

            return CrawlResult(
                source_url=data["source_url"],
                pages=pages,
                success=True,
                total_pages=data["total_pages"],
                failed_pages=data.get("failed_pages", 0),
                crawl_depth=data.get("crawl_depth", 1),
                started_at=datetime.fromisoformat(data["started_at"]),
                completed_at=(
                    datetime.fromisoformat(data["completed_at"])
                    if data.get("completed_at")
                    else None
                ),
                metadata=data.get("metadata", {}),
            )

        except Exception as e:
            raise StorageError(f"Failed to load crawl result: {e}") from e

    async def load_content_from_path(self, path: Path) -> str:
        """
        Load content from file.

        Args:
            path: Path to file

        Returns:
            str: File content
        """
        if not path.exists():
            raise StorageError(f"File not found: {path}")

        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                return cast(str, await f.read())
        except Exception as e:
            raise StorageError(f"Failed to read file: {e}") from e

    async def save_session(self, session: Session) -> None:
        """Save conversation session."""
        filepath: Path = self.sessions_path / f"{session.session_id}.json"

        try:
            data: dict[str, Any] = session.to_dict()
            async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            raise StorageError(f"Failed to save session: {e}") from e

    async def load_session(self, session_id: str) -> Session:
        """Load conversation session."""
        filepath: Path = self.sessions_path / f"{session_id}.json"

        if not filepath.exists():
            # Create new session if doesn't exist
            return Session(session_id=session_id)

        try:
            async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                content: str = await f.read()
                data = json.loads(content)

            return Session.from_dict(data)

        except Exception as e:
            raise StorageError(f"Failed to load session: {e}") from e

    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        filepath: Path = self.sessions_path / f"{session_id}.json"
        return filepath.exists()
