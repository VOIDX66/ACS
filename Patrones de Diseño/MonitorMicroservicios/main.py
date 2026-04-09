"""
=============================================================
 SISTEMA DE MONITOREO DE MICROSERVICIOS
 Patrones: Singleton, Observer, Adapter, Facade
=============================================================
"""

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from infrastructure.config import MonitoringConfig
from presentation.facade import MonitoringFacade
from infrastructure.observers import EmailAlert, SlackAlert, PagerDutyAlert
from infrastructure.adapters import LegacyMonitoringAPI, LegacyAPIAdapter, CloudWatchAPI, CloudWatchAdapter, InternalMetricsProvider

console = Console()


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