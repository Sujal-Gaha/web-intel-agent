from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class PageResult:
    """
    Result from a single crawled page.

    Contains the page content and metadata.
    """

    url: str
    """The URL of the crawled page"""

    content: str
    """The extracted content (markdown, HTML, or text)"""

    title: Optional[str] = None
    """Page title if available"""

    status_code: Optional[int] = None
    """HTTP status code (200, 404, etc.)"""

    crawled_at: datetime = field(default_factory=datetime.now)
    """When this page was crawled"""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the page"""

    def __repr__(self) -> str:
        return f"PageResult(url='{self.url}', content_length={len(self.content)})"


@dataclass
class CrawlResult:
    """
    Complete crawl operation result.

    Contains all pages crawled and metadata about the operation.
    """

    source_url: str
    """The starting URL that was crawled"""

    pages: list[PageResult]
    """List of all successfully crawled pages"""

    success: bool
    """Whether the crawl completed successfully"""

    total_pages: int
    """Total number of pages crawled"""

    failed_pages: int = 0
    """Number of pages that failed to crawl"""

    crawl_depth: int = 1
    """Maximum depth crawled"""

    started_at: datetime = field(default_factory=datetime.now)
    """When the crawl started"""

    completed_at: Optional[datetime] = None
    """When the crawl completed"""

    error_message: Optional[str] = None
    """Error message if crawl failed"""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the crawl"""

    @property
    def combined_content(self) -> str:
        """
        Get all page content combined into a single string.

        Returns:
            Combined content from all pages
        """
        return "\n\n".join(
            [f"--- From: {page.url} ---\n{page.content}" for page in self.pages]
        )

    @property
    def all_urls(self) -> list[str]:
        """
        Get list of all crawled URLs.

        Returns:
            List of URLs
        """
        return [page.url for page in self.pages]

    @property
    def success_rate(self) -> float:
        """
        Calculate success rate as percentage.

        Returns:
            Success rate from 0.0 to 1.0
        """
        if self.total_pages == 0:
            return 0.0
        return (self.total_pages - self.failed_pages) / self.total_pages

    @property
    def duration_seconds(self) -> Optional[float]:
        """
        Calculate crawl duration in seconds.

        Returns:
            Duration in seconds, or None if not completed
        """
        if not self.completed_at:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    def __repr__(self) -> str:
        return (
            f"CrawlResult(source_url='{self.source_url}', "
            f"total_pages={self.total_pages}, "
            f"success_rate={self.success_rate:.1%})"
        )
