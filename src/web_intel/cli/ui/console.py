from rich.console import Console
from rich.theme import Theme

# Custom theme
custom_theme: Theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
    }
)

# Global console instance
console: Console = Console(theme=custom_theme)
