import asyncio
from pathlib import Path
from typing import Optional

import typer
from typer import Typer

from web_intel.agents.base import BaseAgent
from web_intel.agents.factory import AgentFactory
from web_intel.cli.ui.console import console
from web_intel.core.config import Config
from web_intel.core.orchestrator import AgentOrchestrator
from web_intel.models.query import QueryResult
from web_intel.storage.base import BaseStorage
from web_intel.storage.factory import StorageFactory
from web_intel.utils.exceptions import AgentError, StorageError

app: Typer = typer.Typer(help="🤖 AI query commands")


@app.command("ask")
def query_ask(
    question: str = typer.Argument(..., help="Question to ask about the content"),
    source: Path = typer.Option(
        ...,
        "--source",
        "-s",
        help="Source file containing crawled content",
        exists=True,
    ),
    session: Optional[str] = typer.Option(
        None,
        "--session",
        help="Session ID for conversation continuity",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Override default model (e.g., llama2, mistral)",
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        help="Stream response token by token",
    ),
) -> None:
    """
    Ask a question about crawled content.

    Examples:
        wi query ask "What is this site about?" -s data/example.md
        wi query ask "Tell me about pricing" -s data/example.md --session my-research
    """
    asyncio.run(_query_ask_async(question, source, session, model, stream))


async def _query_ask_async(
    question: str,
    source: Path,
    session: Optional[str],
    model: Optional[str],
    stream: bool,
) -> None:
    """Async implementation of query_ask."""
    try:
        config: Config = Config()
        if model:
            config.update_model(model)

        # Show header
        console.rule("[bold blue]Question")
        console.print(f"[cyan]{question}[/cyan]\n")

        # Initialize components
        agent: BaseAgent = AgentFactory.create("ollama", config)
        storage: BaseStorage = StorageFactory.create(config.storage_type, config)
        orchestrator: AgentOrchestrator = AgentOrchestrator(agent, storage)

        # Process query
        if stream:
            console.print("[bold green]Answer:[/bold green]")
            async for chunk in orchestrator.stream_query(
                prompt=question,
                source_path=source,
                session_id=session,
            ):
                console.print(chunk, end="")
            console.print("\n")
        else:
            with console.status("[bold blue]Thinking..."):
                result: QueryResult = await orchestrator.query_with_source(
                    prompt=question,
                    source_path=source,
                    session_id=session,
                )

            console.print()
            console.print("[bold green]Answer:[/bold green]")
            console.print(result.response)
            console.print()
            console.print(
                f"[dim]Model: {result.model_used} | "
                f"Tokens: {result.tokens_used or 'N/A'}[/dim]"
            )

        # Show session info
        if session:
            console.print(f"\n[dim]💾 Session:[/dim] {session}")
            console.print(
                f"[cyan]Continue conversation:[/cyan] "
                f'wi query ask "follow-up question" -s {source} --session {session}'
            )

    except StorageError as e:
        console.print(f"[red]Storage error:[/red] {e}")
        raise typer.Exit(1)
    except AgentError as e:
        console.print(f"[red]Agent error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        console.print_exception()
        raise typer.Exit(1)


@app.command("interactive")
def query_interactive(
    source: Path = typer.Option(
        ...,
        "--source",
        "-s",
        help="Source file containing crawled content",
        exists=True,
    ),
    session: Optional[str] = typer.Option(
        None,
        "--session",
        help="Session ID for this conversation",
    ),
) -> None:
    """
    Start an interactive query session.

    Example:
        wi query interactive -s data/example.md --session research
    """
    asyncio.run(_query_interactive_async(source, session))


async def _query_interactive_async(source: Path, session: Optional[str]) -> None:
    """Async implementation of interactive mode."""
    # Generate session ID if not provided
    if not session:
        from datetime import datetime

        session = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    console.rule("[bold blue]Interactive Mode")
    console.print(f"[dim]Source:[/dim] {source}")
    console.print(f"[dim]Session:[/dim] {session}")
    console.print("[dim]Commands:[/dim] 'exit' or 'quit' to stop\n")

    # Initialize components
    config: Config = Config()
    agent: BaseAgent = AgentFactory.create("ollama", config)
    storage: BaseStorage = StorageFactory.create(config.storage_type, config)
    orchestrator: AgentOrchestrator = AgentOrchestrator(agent, storage)

    # Interactive loop
    while True:
        try:
            # Get user input
            question: str = console.input("[bold cyan]You:[/bold cyan] ")

            if question.lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not question.strip():
                continue

            # Process query
            with console.status("[bold blue]Thinking..."):
                result: QueryResult = await orchestrator.query_with_source(
                    prompt=question,
                    source_path=source,
                    session_id=session,
                )

            console.print(f"[bold green]Assistant:[/bold green] {result.response}\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}\n")
