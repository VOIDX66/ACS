from rich.console import Console
from rich.theme import Theme

_acs_theme = Theme({
    "producer": "bold cyan",
    "worker": "bold green",
    "reader": "bold blue",
    "writer": "bold yellow",
    "barrier": "bold magenta",
    "amount": "bold white",
    "currency": "italic yellow",
    "status.pending": "dim yellow",
    "status.processing": "bold cyan",
    "status.completed": "bold green",
    "status.failed": "bold red",
    "merchant": "bold white on dark_blue",
    "header": "bold white on dark_green",
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
})

console = Console(theme=_acs_theme)
