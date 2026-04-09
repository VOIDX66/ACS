"""
=============================================================
 ENTITIES - CORE DOMAIN OBJECTS
=============================================================
"""
import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .interfaces import AlertObserver


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


class AlertSubject:
    """Sujeto observable. Gestiona suscriptores y dispara alertas."""
    def __init__(self):
        self._observers: List['AlertObserver'] = []

    def subscribe(self, observer: 'AlertObserver') -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: 'AlertObserver') -> None:
        self._observers.remove(observer)

    def _notify_all(self, service: str, metric: str, value: float, threshold: float) -> None:
        for obs in self._observers:
            obs.alert(service, metric, value, threshold)
