"""Unit tests for data models."""

from typing import Any, Dict, List

import pytest

from web_intel.models.crawl_result import CrawlResult, PageResult
from web_intel.models.query import QueryContext, QueryResult
from web_intel.models.session import Session


class TestPageResult:
    """Tests for PageResult model."""

    def test_create_page_result(self) -> None:
        """Test creating a PageResult."""
        page: PageResult = PageResult(
            url="https://example.com",
            content="Test content",
            title="Test Page",
            status_code=200,
        )

        assert page.url == "https://example.com"
        assert page.content == "Test content"
        assert page.title == "Test Page"
        assert page.status_code == 200

    def test_page_result_with_metadata(self) -> None:
        """Test PageResult with metadata."""
        page: PageResult = PageResult(
            url="https://example.com", content="Content", metadata={"custom": "value"}
        )

        assert page.metadata["custom"] == "value"

    def test_page_result_repr(self) -> None:
        """Test PageResult string representation."""
        page: PageResult = PageResult(url="https://example.com", content="Test")

        repr_str: str = repr(page)
        assert "https://example.com" in repr_str
        assert "content_length=4" in repr_str


class TestCrawlResult:
    """Tests for CrawlResult model."""

    def test_create_crawl_result(self, sample_page_result) -> None:
        """Test creating a CrawlResult."""
        result: CrawlResult = CrawlResult(
            source_url="https://example.com",
            pages=[sample_page_result],
            success=True,
            total_pages=1,
            crawl_depth=1,
        )

        assert result.source_url == "https://example.com"
        assert len(result.pages) == 1
        assert result.success is True
        assert result.total_pages == 1

    def test_combined_content(self, sample_page_result) -> None:
        """Test combined_content property."""
        result: CrawlResult = CrawlResult(
            source_url="https://example.com",
            pages=[sample_page_result],
            success=True,
            total_pages=1,
        )

        combined: str = result.combined_content
        assert "https://example.com" in combined
        assert "This is test content" in combined

    def test_all_urls(self) -> None:
        """Test all_urls property."""
        pages: list[PageResult] = [
            PageResult(url="https://example.com/page1", content="Content 1"),
            PageResult(url="https://example.com/page2", content="Content 2"),
        ]

        result: CrawlResult = CrawlResult(
            source_url="https://example.com", pages=pages, success=True, total_pages=2
        )

        urls: list[str] = result.all_urls
        assert len(urls) == 2
        assert "https://example.com/page1" in urls
        assert "https://example.com/page2" in urls

    def test_success_rate(self) -> None:
        """Test success_rate calculation."""
        result: CrawlResult = CrawlResult(
            source_url="https://example.com",
            pages=[],
            success=True,
            total_pages=10,
            failed_pages=2,
        )

        assert result.success_rate == 0.8  # 8/10 = 0.8


class TestSession:
    """Tests for Session model."""

    def test_create_session(self) -> None:
        """Test creating a Session."""
        session: Session = Session(session_id="test-123")

        assert session.session_id == "test-123"
        assert len(session.messages) == 0

    def test_add_message(self) -> None:
        """Test adding messages to session."""
        session: Session = Session(session_id="test-123")

        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")

        assert len(session.messages) == 2
        assert session.messages[0].role == "user"
        assert session.messages[0].content == "Hello"
        assert session.messages[1].role == "assistant"

    def test_get_recent_messages(self) -> None:
        """Test getting recent messages."""
        session: Session = Session(session_id="test-123")

        # Add many messages
        for i in range(10):
            session.add_message("user", f"Message {i}")

        # Get last 3
        recent: List[Dict[str, str]] = session.get_recent_messages(n=3)

        assert len(recent) == 3
        assert recent[-1]["content"] == "Message 9"

    def test_session_serialization(self) -> None:
        """Test session to_dict and from_dict."""
        session: Session = Session(session_id="test-123")
        session.add_message("user", "Test")

        # Serialize
        data: Dict[str, Any] = session.to_dict()

        assert data["session_id"] == "test-123"
        assert len(data["messages"]) == 1

        # Deserialize
        restored: Session = Session.from_dict(data)

        assert restored.session_id == "test-123"
        assert len(restored.messages) == 1
        assert restored.messages[0].content == "Test"


class TestQueryContext:
    """Tests for QueryContext model."""

    def test_create_query_context(self) -> None:
        """Test creating a QueryContext."""
        context: QueryContext = QueryContext(content="Test content", max_tokens=1000)

        assert context.content == "Test content"
        assert context.max_tokens == 1000
        assert len(context.conversation_history) == 0

    def test_query_context_validation(self) -> None:
        """Test QueryContext validation."""
        with pytest.raises(ValueError):
            QueryContext(content="", max_tokens=1000)

        with pytest.raises(ValueError):
            QueryContext(content="Test", max_tokens=0)


class TestQueryResult:
    """Tests for QueryResult model."""

    def test_create_query_result(self) -> None:
        """Test creating a QueryResult."""
        result: QueryResult = QueryResult(
            response="Test response", model_used="llama2", tokens_used=50
        )

        assert result.response == "Test response"
        assert result.model_used == "llama2"
        assert result.tokens_used == 50

    def test_query_result_serialization(self) -> None:
        """Test QueryResult to_dict and from_dict."""
        result: QueryResult = QueryResult(
            response="Test", model_used="llama2", tokens_used=50, finish_reason="stop"
        )

        # Serialize
        data: Dict[str, Any] = result.to_dict()

        assert data["response"] == "Test"
        assert data["model_used"] == "llama2"

        # Deserialize
        restored: QueryResult = QueryResult.from_dict(data)

        assert restored.response == "Test"
        assert restored.model_used == "llama2"
