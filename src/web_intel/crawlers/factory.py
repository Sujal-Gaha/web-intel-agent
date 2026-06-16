from typing import Callable, Optional

from web_intel.core.config import Config
from web_intel.crawlers.base import BaseCrawler
from web_intel.crawlers.crawl4ai import Crawl4AICrawler

CrawlerConstructor = Callable[
    [Config, Optional[Callable[[str, int, int], None]]], BaseCrawler
]


class CrawlerFactory:
    """Factory for creating crawler instances."""

    _crawlers: dict[str, CrawlerConstructor] = {
        "crawl4ai": Crawl4AICrawler,
    }

    @classmethod
    def create(
        cls,
        crawler_type: str,
        config: Config,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> BaseCrawler:
        """Create a crawler instance."""
        crawler_class: CrawlerConstructor | None = cls._crawlers.get(crawler_type)

        if not crawler_class:
            available: str = ", ".join(cls._crawlers.keys())
            raise ValueError(
                f"Unknown crawler type: '{crawler_type}'. "
                f"Available crawlers: {available}"
            )

        return crawler_class(config, progress_callback)

    @classmethod
    def register(cls, name: str, crawler_class: CrawlerConstructor) -> None:
        """Register a new crawler implementation."""
        cls._crawlers[name] = crawler_class

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister a crawler implementation."""
        if name in cls._crawlers:
            del cls._crawlers[name]
            return True
        return False

    @classmethod
    def list_available(cls) -> list[str]:
        """List all available crawler types."""
        return list(cls._crawlers.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a crawler type is registered."""
        return name in cls._crawlers
