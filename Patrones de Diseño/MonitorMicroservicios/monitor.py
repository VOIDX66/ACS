"""
=============================================================
 MONITOR DE MICROSERVICIO
=============================================================
"""

from observers import AlertSubject
from config import MonitoringConfig
from adapters import MetricsProvider, MetricsSnapshot


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