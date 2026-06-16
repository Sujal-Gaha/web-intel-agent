"""Unit tests for configuration."""

import os
from pathlib import Path

import pytest

from web_intel.core.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config: Config = Config()

        assert config.ollama_host == "http://localhost:11434"
        assert config.ollama_model == "deepseek-r1:14b"
        assert config.storage_type == "file"
        assert config.crawler_timeout > 0

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config: Config = Config(ollama_model="mistral", crawler_timeout=60)

        assert config.ollama_model == "mistral"
        assert config.crawler_timeout == 60

    def test_env_variable_override(self) -> None:
        """Test environment variable override."""
        os.environ["WEB_INTEL_OLLAMA_MODEL"] = "codellama"

        config: Config = Config()

        assert config.ollama_model == "codellama"

        # Cleanup
        del os.environ["WEB_INTEL_OLLAMA_MODEL"]

    def test_storage_path_creation(self, tmp_path) -> None:
        """Test that storage path is created."""
        storage_path = tmp_path / "test_storage"

        config: Config = Config(storage_path=str(storage_path))

        # Path should be created
        assert Path(config.storage_path).exists()

    def test_get_storage_path(self, tmp_path) -> None:
        """Test get_storage_path method."""
        config: Config = Config(storage_path=str(tmp_path))

        subdir: Path = config.get_storage_path("crawls")

        assert subdir.exists()
        assert subdir.name == "crawls"

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        # Invalid timeout
        with pytest.raises(ValueError):
            Config(crawler_timeout=-1)

        # Invalid log level
        with pytest.raises(ValueError):
            Config(log_level="INVALID")
