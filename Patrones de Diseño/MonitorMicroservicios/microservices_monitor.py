"""
=============================================================
 SISTEMA DE MONITOREO DE MICROSERVICIOS
 Patrones: Singleton, Observer, Adapter, Facade
=============================================================
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import random
import datetime
import threading

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich import box

console = Console()


# =============================================================
# PATRON SINGLETON — Configuracion centralizada
# =============================================================
# JUSTIFICACION: Todos los componentes del sistema deben leer
# los MISMOS umbrales de alerta. Si MonitoringConfig no fuera
# Singleton, cada modulo podria instanciar su propia copia con
# valores distintos, rompiendo la consistencia global.
# Thread-safe mediante threading.Lock para entornos concurrentes.

class MonitoringConfig:
    """
    Unica fuente de verdad para todos los parametros del sistema.
    Garantizado por Singleton: solo existe UNA instancia en todo el proceso.
    """
    _instance: MonitoringConfig | None = None
    _lock: threading.Lock = threading.Lock()

    # Umbrales de alerta globales
    CPU_THRESHOLD:    float = 80.0   # %
    MEMORY_THRESHOLD: float = 75.0   # %
    LATENCY_THRESHOLD: float = 500.0 # ms
    ERROR_RATE_THRESHOLD: float = 5.0 # %

    def __new__(cls) -> MonitoringConfig:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def update_threshold(self, metric: str, value: float) -> None:
        """Cambia un umbral en tiempo real — todos los componentes lo ven de inmediato."""
        attr = f"{metric.upper()}_THRESHOLD"
        if hasattr(self, attr):
            setattr(self.__class__, attr, value)
            console.print(f"  [dim][CONFIG] Umbral '{metric}' actualizado a {value}[/dim]")
        else:
            raise ValueError(f"Metrica desconocida: '{metric}'")

    def get_all(self) -> Dict[str, float]:
        return {
            "cpu":        self.CPU_THRESHOLD,
            "memory":     self.MEMORY_THRESHOLD,
            "latency":    self.LATENCY_THRESHOLD,
            "error_rate": self.ERROR_RATE_THRESHOLD,
        }


# =============================================================
# PATRON OBSERVER — Alertas multicanal
# =============================================================
# JUSTIFICACION: El monitor no debe saber COMO se entrega una alerta.
# Observer desacopla completamente la deteccion del umbral superado
# del mecanismo de notificacion. Agregar Teams o PagerDuty =
# crear un AlertObserver nuevo y suscribirlo. Cero cambios al monitor.

class AlertObserver(ABC):
    """Interfaz que deben implementar todos los canales de alerta."""
    @abstractmethod
    def alert(self, service: str, metric: str, value: float, threshold: float) -> None: ...

    @property
    @abstractmethod
    def channel_name(self) -> str: ...


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


class AlertSubject:
    """Sujeto observable. Gestiona suscriptores y dispara alertas."""
    def __init__(self):
        self._observers: List[AlertObserver] = []

    def subscribe(self, observer: AlertObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: AlertObserver) -> None:
        self._observers.remove(observer)

    def _notify_all(self, service: str, metric: str, value: float, threshold: float) -> None:
        for obs in self._observers:
            obs.alert(service, metric, value, threshold)


# =============================================================
# PATRON ADAPTER — Integracion con APIs externas heterogeneas
# =============================================================
# JUSTIFICACION: Las APIs externas de monitoreo devuelven datos
# en formatos completamente distintos. Sin Adapter, el nucleo
# del sistema tendria que conocer cada formato externo, creando
# acoplamiento fuerte y violando SRP. El Adapter normaliza todo
# a una interfaz unica: get_metrics() -> MetricsSnapshot.

class MetricsSnapshot:
    """Formato interno uniforme de metricas."""
    def __init__(
        self,
        cpu_usage: float,
        memory_usage: float,
        latency_ms: float,
        error_rate: float,
    ):
        self.cpu_usage    = cpu_usage
        self.memory_usage = memory_usage
        self.latency_ms   = latency_ms
        self.error_rate   = error_rate
        self.timestamp    = datetime.datetime.now()


class MetricsProvider(ABC):
    """Target: interfaz que el sistema interno espera."""
    @abstractmethod
    def get_metrics(self) -> MetricsSnapshot: ...


# ── API legada con formato heterogeneo ──────────────────────
class LegacyMonitoringAPI:
    """Simulacion de API legada con claves no estandar."""
    def fetch_data(self) -> Dict[str, Any]:
        return {
            "cpu_usage_percent":    round(random.uniform(40, 95), 1),
            "mem_used_pct":         round(random.uniform(50, 90), 1),
            "response_time_ms":     round(random.uniform(100, 800), 1),
            "error_percentage":     round(random.uniform(0, 12), 2),
        }

class LegacyAPIAdapter(MetricsProvider):
    """
    Adapter: traduce el formato de LegacyMonitoringAPI
    al formato interno MetricsSnapshot.
    El sistema nunca habla directamente con la API legada.
    """
    def __init__(self, legacy_api: LegacyMonitoringAPI):
        self._api = legacy_api

    def get_metrics(self) -> MetricsSnapshot:
        raw = self._api.fetch_data()
        return MetricsSnapshot(
            cpu_usage    = raw["cpu_usage_percent"],
            memory_usage = raw["mem_used_pct"],
            latency_ms   = raw["response_time_ms"],
            error_rate   = raw["error_percentage"],
        )


# ── API moderna con otro formato heterogeneo ─────────────────
class CloudWatchAPI:
    """Simulacion de API cloud con estructura anidada."""
    def query_metrics(self) -> Dict[str, Any]:
        return {
            "Metrics": {
                "CPUUtilization":      round(random.uniform(20, 99), 1),
                "MemoryUtilization":   round(random.uniform(30, 95), 1),
                "AverageLatency":      round(random.uniform(50, 1200), 1),
                "HTTPErrorRate":       round(random.uniform(0, 15), 2),
            }
        }

class CloudWatchAdapter(MetricsProvider):
    """Adapter para CloudWatch — misma interfaz, distinta fuente."""
    def __init__(self, cloudwatch: CloudWatchAPI):
        self._api = cloudwatch

    def get_metrics(self) -> MetricsSnapshot:
        raw = self._api.query_metrics()["Metrics"]
        return MetricsSnapshot(
            cpu_usage    = raw["CPUUtilization"],
            memory_usage = raw["MemoryUtilization"],
            latency_ms   = raw["AverageLatency"],
            error_rate   = raw["HTTPErrorRate"],
        )


# ── Generador de metricas internas (sin adaptacion necesaria) ─
class InternalMetricsProvider(MetricsProvider):
    """Servicio que ya expone el formato interno directamente."""
    def __init__(self, service_name: str):
        self._name = service_name

    def get_metrics(self) -> MetricsSnapshot:
        return MetricsSnapshot(
            cpu_usage    = round(random.uniform(10, 92), 1),
            memory_usage = round(random.uniform(20, 88), 1),
            latency_ms   = round(random.uniform(30, 950), 1),
            error_rate   = round(random.uniform(0, 10), 2),
        )


# =============================================================
# MONITOR DE MICROSERVICIO
# =============================================================

class MicroserviceMonitor(AlertSubject):
    """
    Combina Observer (hereda AlertSubject) con la config Singleton.
    Evalua metricas contra los umbrales globales y dispara alertas.
    """
    def __init__(self, service_name: str, provider: MetricsProvider):
        super().__init__()
        self.service_name = service_name
        self._provider    = provider
        self._config      = MonitoringConfig()  # Singleton: siempre la misma instancia

    def check(self) -> MetricsSnapshot:
        snap = self._provider.get_metrics()
        cfg  = self._config

        checks = [
            ("CPU",        snap.cpu_usage,    cfg.CPU_THRESHOLD),
            ("Memoria",    snap.memory_usage, cfg.MEMORY_THRESHOLD),
            ("Latencia",   snap.latency_ms,   cfg.LATENCY_THRESHOLD),
            ("Error Rate", snap.error_rate,   cfg.ERROR_RATE_THRESHOLD),
        ]

        for metric, value, threshold in checks:
            if value > threshold:
                self._notify_all(self.service_name, metric, value, threshold)

        return snap


# =============================================================
# PATRON FACADE — Interfaz simplificada del subsistema
# =============================================================
# JUSTIFICACION: El equipo de operaciones no deberia necesitar
# conocer MonitoringConfig, MicroserviceMonitor, AlertSubject,
# ni los distintos Adapters. La Facade expone UNA interfaz
# simple: register_service() y run_cycle(), ocultando toda
# la complejidad de coordinacion interna.

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


# =============================================================
# DEMO COMPLETA
# =============================================================

def run_demo():
    console.print()
    console.rule(
        "[bold bright_white] SISTEMA DE MONITOREO DE MICROSERVICIOS [/bold bright_white]",
        style="bright_yellow"
    )
    console.print("[dim]  Singleton · Observer · Adapter · Facade[/dim]\n")

    # ── Verificacion Singleton: ambas referencias apuntan al mismo objeto
    cfg1 = MonitoringConfig()
    cfg2 = MonitoringConfig()
    console.print(Panel(
        f"[bold]Verificacion Singleton:[/bold]\n"
        f"  cfg1 is cfg2 = [bold green]{cfg1 is cfg2}[/bold green]\n"
        f"  id(cfg1) = {id(cfg1)} | id(cfg2) = {id(cfg2)}",
        border_style="green", padding=(0, 1),
        title="[bold]Singleton[/bold]"
    ))

    # ── Facade: punto de entrada unico
    monitor_facade = MonitoringFacade()

    console.print()
    console.rule("[bold]Registro de servicios[/bold]", style="dim")

    # Canales de alerta compartidos
    email_alert    = EmailAlert("ops-team@fintech.com")
    slack_alert    = SlackAlert("alertas-produccion")
    pagerduty_alert = PagerDutyAlert("P1-escalation")

    # Servicio 1: usa API legada (necesita Adapter)
    legacy_api     = LegacyMonitoringAPI()
    legacy_adapter = LegacyAPIAdapter(legacy_api)
    monitor_facade.register_service(
        "payment-service",
        legacy_adapter,
        [email_alert, slack_alert, pagerduty_alert],
    )

    # Servicio 2: usa CloudWatch (necesita Adapter diferente)
    cloudwatch     = CloudWatchAPI()
    cw_adapter     = CloudWatchAdapter(cloudwatch)
    monitor_facade.register_service(
        "auth-service",
        cw_adapter,
        [email_alert, slack_alert],
    )

    # Servicio 3: proveedor interno (sin adaptacion)
    internal       = InternalMetricsProvider("fraud-detector")
    monitor_facade.register_service(
        "fraud-detector",
        internal,
        [email_alert, pagerduty_alert],
    )

    # ── Mostrar configuracion inicial del Singleton
    console.print()
    monitor_facade.show_config()

    # ── Primer ciclo de monitoreo
    monitor_facade.run_cycle()

    # ── Cambio de umbral en tiempo real (Singleton propaga a todos)
    console.rule("[bold]Actualizacion de umbral en tiempo real[/bold]", style="dim")
    console.print("  Bajando umbral de CPU a 60% para mayor sensibilidad...\n")
    monitor_facade.update_threshold("cpu", 60.0)
    monitor_facade.show_config()

    # ── Segundo ciclo con nuevo umbral
    monitor_facade.run_cycle()


if __name__ == "__main__":
    run_demo()
