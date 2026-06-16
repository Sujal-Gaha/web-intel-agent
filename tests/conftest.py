import asyncio
from datetime import datetime

import pytest

from web_intel.core.config import Config
from web_intel.models.crawl_result import CrawlResult, PageResult
from web_intel.models.query import QueryContext, QueryResult
from web_intel.models.session import Session


# Configure async testing
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Configuration fixtures
@pytest.fixture
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        ollama_host="http://localhost:11434",
        ollama_model="deepseek-r1:14b",
        storage_path="./test_data",
        crawler_timeout=10,
        max_context_length=1000,
    )


@pytest.fixture
def temp_storage_path(tmp_path):
    """Create a temporary storage directory."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    return storage_dir


# Model fixtures
@pytest.fixture
def sample_page_result() -> PageResult:
    """Create a sample PageResult."""
    return PageResult(
        url="https://example.com",
        content="# Example Page\n\nThis is test content.",
        title="Example Page",
        status_code=200,
        metadata={"has_markdown": True, "content_length": 42},
    )


@pytest.fixture
def sample_crawl_result(sample_page_result) -> CrawlResult:
    """Create a sample CrawlResult."""
    return CrawlResult(
        source_url="https://example.com",
        pages=[sample_page_result],
        success=True,
        total_pages=1,
        failed_pages=0,
        crawl_depth=1,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        metadata={"crawler": "test", "duration_seconds": 1.0},
    )


@pytest.fixture
def sample_query_context() -> QueryContext:
    """Create a sample QueryContext."""
    return QueryContext(
        content="This is test content for querying.",
        max_tokens=1000,
        conversation_history=[],
        metadata={"source": "test"},
    )


@pytest.fixture
def sample_query_result() -> QueryResult:
    """Create a sample QueryResult."""
    return QueryResult(
        response="This is a test response.",
        model_used="test-model",
        tokens_used=50,
        finish_reason="stop",
        metadata={"test": True},
    )


@pytest.fixture
def sample_session() -> Session:
    """Create a sample Session."""
    session: Session = Session(session_id="test-session-123")
    session.add_message("user", "What is this?")
    session.add_message("assistant", "This is a test.")
    return session


# Mock fixtures
@pytest.fixture
def mock_llm_response():
    """Mock LLM response data."""
    return {
        "response": "This is a mock response from the LLM.",
        "tokens_used": 25,
        "finish_reason": "stop",
        "metadata": {
            "total_duration": 1000000,
            "load_duration": 100000,
        },
    }
