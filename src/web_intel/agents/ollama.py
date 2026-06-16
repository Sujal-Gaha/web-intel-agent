import json
from typing import Any, AsyncIterator

import aiohttp

from web_intel.agents.base import BaseAgent
from web_intel.core.config import Config
from web_intel.models.query import QueryContext, QueryResult
from web_intel.utils.exceptions import AgentError


class OllamaAgent(BaseAgent):
    """Ollama-based AI agent implementation."""

    def __init__(self, config: Config) -> None:
        """
        Initialize Ollama agent.

        Args:
            config: Application configuration
        """
        self.config: Config = config
        self.host: str = config.ollama_host
        self.model: str = config.ollama_model
        self.max_context: int = config.max_context_length

        # API endpoints
        self.generate_url: str = f"{self.host}/api/generate"
        self.chat_url: str = f"{self.host}/api/chat"

    async def validate_connection(self) -> bool:
        """
        Validate connection to Ollama server.

        Returns:
            bool: True if connected successfully
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.host}/api/tags") as resp:
                    return resp.status == 200
        except Exception:
            return False

    def prepare_context(self, content: str, max_tokens: int) -> str:
        """
        Prepare content to fit within token limits.
        Simple implementation - truncate if too long.

        Args:
            content: Raw content
            max_tokens: Token limit

        Returns:
            Prepared content
        """
        # Rough approximation: 1 token ≈ 4 characters
        max_chars: int = max_tokens * 4

        if len(content) <= max_chars:
            return content

        # Truncate and add notice
        truncated: str = content[:max_chars]
        return f"{truncated}\n\n[Note: Content truncated to fit context window]"

    async def query(
        self, prompt: str, context: QueryContext, temperature: float = 0.7, **kwargs
    ) -> QueryResult:
        """
        Query Ollama with a prompt.

        Args:
            prompt: User question
            context: Query context with content
            temperature: Sampling temperature
            **kwargs: Additional Ollama options

        Returns:
            QueryResult with response

        Raises:
            AgentError: If query fails
        """
        try:
            full_prompt: str = self._build_prompt(prompt, context)

            payload: dict[str, Any] = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": temperature, **kwargs},
                "think": False,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.generate_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        error_text: str = await resp.text()
                        raise AgentError(
                            f"Ollama API error ({resp.status}): {error_text}"
                        )

                    data = await resp.json()

            response_text = data.get("response", "")

            if not response_text:
                raise AgentError("Empty response from Ollama")

            return QueryResult(
                response=response_text,
                model_used=self.model,
                tokens_used=data.get("eval_count"),
                finish_reason=data.get("done_reason"),
                metadata={
                    "total_duration": data.get("total_duration"),
                    "load_duration": data.get("load_duration"),
                    "prompt_eval_count": data.get("prompt_eval_count"),
                },
            )

        except aiohttp.ClientError as e:
            raise AgentError(f"Network error: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise AgentError(f"Invalid JSON response: {str(e)}") from e
        except AgentError:
            raise
        except Exception as e:
            raise AgentError(f"Query failed: {str(e)}") from e

    async def stream_query(
        self, prompt: str, context: QueryContext, temperature: float = 0.7, **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream query responses token by token.

        Args:
            prompt: User question
            context: Query context
            temperature: Sampling temperature
            **kwargs: Additional options

        Yields:
            str: Response tokens
        """
        try:
            full_prompt: str = self._build_prompt(prompt, context)

            payload: dict[str, Any] = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": True,
                "options": {"temperature": temperature, **kwargs},
                "think": False,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.generate_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300),
                ) as resp:
                    if resp.status != 200:
                        error_text: str = await resp.text()
                        raise AgentError(
                            f"Ollama API error ({resp.status}): {error_text}"
                        )

                    # Stream response line by line
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]

                                # Check if done
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue

        except aiohttp.ClientError as e:
            raise AgentError(f"Streaming error: {str(e)}") from e
        except Exception as e:
            raise AgentError(f"Stream failed: {str(e)}") from e

    def _build_prompt(self, prompt: str, context: QueryContext) -> str:
        """
        Build the full prompt with context.

        Args:
            prompt: User question
            context: Query context

        Returns:
            Full prompt string
        """
        # Prepare content
        prepared_content: str = self.prepare_context(
            context.content, context.max_tokens
        )

        # Build system instruction
        system = (
            "You are a helpful AI assistant analyzing web content. "
            "Answer questions based on the provided content accurately and concisely."
        )

        # Add conversation history if present
        history = ""
        if context.conversation_history:
            history = "\n\nPrevious conversation:\n"
            for msg in context.conversation_history[-5:]:  # Last 5 messages
                role: str = msg.get("role", "user")
                content: str = msg.get("content", "")
                history += f"{role.capitalize()}: {content}\n"

        # Combine everything
        full_prompt: str = f"""{system}

Content to analyze:
{prepared_content}
{history}

User question: {prompt}

Answer:"""

        return full_prompt
