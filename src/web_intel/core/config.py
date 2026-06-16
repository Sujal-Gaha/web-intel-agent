from pathlib import Path
from typing import Any, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Application configuration with environment variable support.

    All settings can be overridden via environment variables with
    the prefix WEB_INTEL_ (e.g., WEB_INTEL_OLLAMA_HOST).
    """

    # ========== Ollama Settings ==========
    ollama_host: str = Field(
        default="http://localhost:11434", description="Ollama API host URL"
    )

    ollama_model: str = Field(
        default="deepseek-r1:14b",
        description="Ollama model to use (llama2, mistral, etc.)",
    )

    # ========== Crawler Settings ==========
    crawler_type: str = Field(
        default="crawl4ai",
        description="Type of crawler to use (crawl4ai, playwright, etc.)",
    )

    crawler_timeout: int = Field(
        default=30, description="Timeout for crawling operations in seconds", ge=1
    )

    crawler_max_depth: int = Field(
        default=5, description="Default maximum crawling depth", ge=1, le=10
    )

    # ========== Storage Settings ==========
    storage_type: str = Field(
        default="file", description="Type of storage backend (file, sqlite, postgres)"
    )

    storage_path: str = Field(
        default="./data", description="Base path for file storage"
    )

    # ========== Agent Settings ==========
    max_context_length: int = Field(
        default=4000, description="Maximum context length in tokens", ge=100
    )

    agent_temperature: float = Field(
        default=0.7, description="Temperature for LLM sampling", ge=0.0, le=2.0
    )

    # ========== CLI Settings ==========
    cli_verbose: bool = Field(default=False, description="Enable verbose output in CLI")

    cli_color: bool = Field(default=True, description="Enable colored output in CLI")

    # ========== Advanced Settings ==========
    enable_caching: bool = Field(
        default=True, description="Enable caching of crawl results"
    )

    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WEB_INTEL_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("storage_path")
    @classmethod
    def create_storage_path(cls, v: str) -> str:
        """Create storage directory if it doesn't exist."""
        path: Path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper: str = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    def get_storage_path(self, subdir: Optional[str] = None) -> Path:
        """
        Get storage path, optionally with subdirectory.

        Args:
            subdir: Optional subdirectory name

        Returns:
            Path object
        """
        base: Path = Path(self.storage_path)
        if subdir:
            path: Path = base / subdir
            path.mkdir(parents=True, exist_ok=True)
            return path
        return base

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()

    def update_model(self, model: str) -> None:
        self.ollama_model = model

    def __repr__(self) -> str:
        return (
            f"Config(\n"
            f"  ollama_host='{self.ollama_host}',\n"
            f"  ollama_model='{self.ollama_model}',\n"
            f"  crawler_type='{self.crawler_type}',\n"
            f"  storage_type='{self.storage_type}',\n"
            f"  storage_path='{self.storage_path}'\n"
            f")"
        )
