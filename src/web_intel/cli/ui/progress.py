from contextlib import contextmanager
from typing import Any, Generator

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)


@contextmanager
def show_progress() -> Generator[Progress, Any, None]:
    """Context manager for showing progress."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
    ) as progress:
        yield progress
