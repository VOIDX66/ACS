"""
=============================================================
 PATRON OBSERVER — ALERTAS MULTICANAL
=============================================================
"""

from rich.console import Console

from domain.interfaces import AlertObserver

console = Console()


class EmailAlert(AlertObserver):
    def __init__(self, recipient: str):
        self._recipient = recipient

    @property
    def channel_name(self) -> str:
        return "Email"

    def alert(self, service: str, metric: str, value: float, threshold: float) -> None:
        console.print(
            f"    [cyan][[EMAIL]][/cyan] -> {self._recipient} | "
            f"[bold]{service}[/bold]: {metric} en [red]{value:.1f}[/red] "
            f"(umbral: {threshold})"
        )


class SlackAlert(AlertObserver):
    def __init__(self, channel: str):
        self._channel = channel

    @property
    def channel_name(self) -> str:
        return "Slack"

    def alert(self, service: str, metric: str, value: float, threshold: float) -> None:
        console.print(
            f"    [magenta][[SLACK]][/magenta] -> #{self._channel} | "
            f"[bold]{service}[/bold]: {metric} en [red]{value:.1f}[/red] "
            f"(umbral: {threshold})"
        )


class PagerDutyAlert(AlertObserver):
    """Nuevo canal — agregado sin modificar nada existente (Open/Closed)."""
    def __init__(self, escalation_policy: str):
        self._policy = escalation_policy

    @property
    def channel_name(self) -> str:
        return "PagerDuty"

    def alert(self, service: str, metric: str, value: float, threshold: float) -> None:
        console.print(
            f"    [red][[PAGERDUTY]][/red] -> policy:{self._policy} | "
            f"INCIDENTE: [bold]{service}[/bold] {metric}={value:.1f} > {threshold} "
            f"[blink][red]CRITICO[/red][/blink]"
        )
