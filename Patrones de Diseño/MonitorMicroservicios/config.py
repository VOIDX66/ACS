"""
=============================================================
 CONFIGURACION CENTRALIZADA - PATRON SINGLETON
=============================================================
"""

from __future__ import annotations
import threading
from typing import Dict

from rich.console import Console

console = Console()


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