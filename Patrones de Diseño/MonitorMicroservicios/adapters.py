"""
=============================================================
 PATRON ADAPTER — INTEGRACION CON APIs EXTERNAS HETEROGENEAS
=============================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import random
import datetime


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