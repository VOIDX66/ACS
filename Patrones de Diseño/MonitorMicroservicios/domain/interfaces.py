"""
=============================================================
 INTERFACES (PORTS) - CLEAN ARCHITECTURE
=============================================================
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import MetricsSnapshot


class AlertObserver(ABC):
    """Interfaz que deben implementar todos los canales de alerta."""
    @abstractmethod
    def alert(self, service: str, metric: str, value: float, threshold: float) -> None: ...

    @property
    @abstractmethod
    def channel_name(self) -> str: ...


class MetricsProvider(ABC):
    """Target: interfaz que el sistema interno espera."""
    @abstractmethod
    def get_metrics(self) -> 'MetricsSnapshot': ...
