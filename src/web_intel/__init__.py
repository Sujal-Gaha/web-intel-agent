__version__ = "0.1.0"

# Expose main components at package level
from web_intel.agents.factory import AgentFactory
from web_intel.core.config import Config
from web_intel.core.orchestrator import AgentOrchestrator
from web_intel.crawlers.factory import CrawlerFactory
from web_intel.storage.factory import StorageFactory

__all__ = [
    "Config",
    "AgentFactory",
    "CrawlerFactory",
    "StorageFactory",
    "AgentOrchestrator",
]
