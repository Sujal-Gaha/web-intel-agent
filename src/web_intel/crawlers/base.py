from abc import ABC, abstractmethod

from web_intel.models.crawl_result import CrawlResult


class BaseCrawler(ABC):
    """
    Abstract base class for all web crawlers.

    All crawler implementations must inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    async def crawl(self, url: str, **options) -> CrawlResult:
        """
        Crawl a URL and return structured results.

        Args:
            url: Target URL to crawl
            **options: Crawler-specific options (depth, timeout, etc.)

        Returns:
            CrawlResult with content and metadata

        Raises:
            CrawlerError: If crawling fails

        Examples:
            >>> crawler = SomeCrawler(config)
            >>> result = await crawler.crawl("https://example.com", depth=2)
            >>> print(f"Crawled {result.total_pages} pages")
        """
        pass

    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """
        Validate URL before crawling.

        Args:
            url: URL to validate

        Returns:
            True if valid and accessible, False otherwise

        Examples:
            >>> crawler = SomeCrawler(config)
            >>> if await crawler.validate_url("https://example.com"):
            ...     result = await crawler.crawl("https://example.com")
        """
        pass
