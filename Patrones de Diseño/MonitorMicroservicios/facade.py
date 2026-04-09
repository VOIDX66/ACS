"""
=============================================================
 PATRON FACADE — INTERFAZ SIMPLIFICADA DEL SUBSISTEMA
=============================================================
"""

from typing import List, Dict
import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from config import MonitoringConfig
from monitor import MicroserviceMonitor
from observers import AlertObserver
from adapters import MetricsProvider

console = Console()


class MonitoringFacade:
    """
    Punto de entrada unico para el sistema de monitoreo.
    Coordina: registro de servicios, ejecucion de ciclos,
    visualizacion de resultados y gestion de alertas.
    """

    def __init__(self):
        self._monitors: Dict[str, MicroserviceMonitor] = {}
        self._config = MonitoringConfig()  # Singleton

    def register_service(
        self,
        name: str,
        provider: MetricsProvider,
        alert_channels: List[AlertObserver],
    ) -> None:
        """Registra un microservicio con su proveedor de metricas y canales de alerta."""
        monitor = MicroserviceMonitor(name, provider)
        for channel in alert_channels:
            monitor.subscribe(channel)
        self._monitors[name] = monitor
        console.print(
            f"  [green][+][/green] Servicio registrado: [bold]{name}[/bold] "
            f"| Canales: {[c.channel_name for c in alert_channels]}"
        )

    def run_cycle(self) -> None:
        """Ejecuta un ciclo completo de monitoreo sobre todos los servicios registrados."""
        console.print()
        console.rule("[bold white] CICLO DE MONITOREO [/bold white]", style="bright_blue")
        console.print(f"  [dim]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")

        # Tabla de resultados
        table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=True,
            header_style="bold cyan",
            title="[bold]Estado de Microservicios[/bold]",
            title_style="dim",
        )
        table.add_column("Servicio",    style="white",   min_width=20)
        table.add_column("CPU %",       justify="right", min_width=8)
        table.add_column("Memoria %",   justify="right", min_width=10)
        table.add_column("Latencia ms", justify="right", min_width=12)
        table.add_column("Error Rate%", justify="right", min_width=12)
        table.add_column("Estado",      justify="center", min_width=10)

        cfg = self._config
        alerts_fired = False

        for name, monitor in self._monitors.items():
            snap = monitor.check()

            def fmt(val, threshold):
                color = "red bold" if val > threshold else "green"
                return f"[{color}]{val:.1f}[/{color}]"

            status_ok = (
                snap.cpu_usage    <= cfg.CPU_THRESHOLD and
                snap.memory_usage <= cfg.MEMORY_THRESHOLD and
                snap.latency_ms   <= cfg.LATENCY_THRESHOLD and
                snap.error_rate   <= cfg.ERROR_RATE_THRESHOLD
            )

            if not status_ok:
                alerts_fired = True

            table.add_row(
                name,
                fmt(snap.cpu_usage,    cfg.CPU_THRESHOLD),
                fmt(snap.memory_usage, cfg.MEMORY_THRESHOLD),
                fmt(snap.latency_ms,   cfg.LATENCY_THRESHOLD),
                fmt(snap.error_rate,   cfg.ERROR_RATE_THRESHOLD),
                "[bold green]OK[/bold green]" if status_ok else "[bold red]ALERTA[/bold red]",
            )

        console.print(table)

        if alerts_fired:
            console.print(Panel(
                "[bold yellow]Alertas disparadas — notificando canales suscritos:[/bold yellow]",
                border_style="yellow", padding=(0, 1)
            ))
            # Las alertas ya fueron notificadas dentro de monitor.check()
            # Solo re-ejecutamos para mostrar las notificaciones agrupadas
            for name, monitor in self._monitors.items():
                snap = monitor.check()

        console.print()

    def show_config(self) -> None:
        """Muestra la configuracion actual del Singleton."""
        cfg = self._config.get_all()
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan",
                      title="[bold]Configuracion Global (Singleton)[/bold]", title_style="dim")
        table.add_column("Metrica",  style="white",  min_width=18)
        table.add_column("Umbral",   justify="right", style="yellow", min_width=12)
        labels = {"cpu": "CPU (%)", "memory": "Memoria (%)",
                  "latency": "Latencia (ms)", "error_rate": "Error Rate (%)"}
        for key, val in cfg.items():
            table.add_row(labels[key], str(val))
        console.print(table)

    def update_threshold(self, metric: str, value: float) -> None:
        """Delega al Singleton — un solo punto de cambio para todos los servicios."""
        self._config.update_threshold(metric, value)