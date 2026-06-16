class WebIntelError(Exception):
    """Base exception for all web-intel errors."""

    pass


class CrawlerError(WebIntelError):
    """Crawler-related errors."""

    pass


class AgentError(WebIntelError):
    """Agent-related errors."""

    pass


class StorageError(WebIntelError):
    """Storage-related errors."""

    pass


class ValidationError(WebIntelError):
    """Input validation errors."""

    pass
