from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class BaseLLMClient(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    async def generate(self) -> dict[str, Any]:
        """Non-streaming generation"""

    @abstractmethod
    async def stream_generate(self) -> AsyncIterator[str]:
        """Streaming generation"""

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Check if service is accessible"""

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Get model information"""
