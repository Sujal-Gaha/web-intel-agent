from abc import ABC, abstractmethod

from web_intel.models.crawl_result import CrawlResult


class BaseCrawler(ABC):
    """Abstract base for all crawlers"""

    @abstractmethod
    async def crawl(self, url: str, **options) -> CrawlResult:
        """Crawl a URL and return structured results"""
        pass

    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """Validate URL before crawling"""
        pass
