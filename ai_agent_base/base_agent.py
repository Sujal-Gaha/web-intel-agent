from abc import ABC, abstractmethod
from typing import List

class BaseAIAgent(ABC):
    """Abstract base class for all AI agent versions."""

    def __init__(self, file_path: str, model: str):
        self.file_path = file_path
        self.model = model

    @abstractmethod
    def _read_and_process_file(self) -> None:
        """Read and process the input file."""
        ...

    @abstractmethod
    def _chunk_text(self, max_tokens: int = 2000) -> None:
        """Split the content into manageable chunks."""
        ...

    @abstractmethod
    def _generate_responses(self, user_prompt: str) -> List[str]:
        """Generate responses using the chosen AI backend."""
        ...

    @abstractmethod
    def _save_responses(self, prompt: str, responses: List[str]) -> None:
        """Save responses to output storage."""
        ...

    @abstractmethod
    def process(self) -> None:
        """Main loop for user interaction and response generation."""
        ...
