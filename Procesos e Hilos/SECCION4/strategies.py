"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Patrón Strategy — Selección del próximo trabajo.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from models import Job


class JobSelectionStrategy(ABC):
    """Interfaz Strategy: decide qué trabajo extraer de las colas."""

    @abstractmethod
    def select(
        self,
        premium_queue: list,
        free_queue   : list,
        consecutive_premium: int,
    ) -> Optional[Job]:
        ...


class AntiStarvationStrategy(JobSelectionStrategy):
    """
    Implementación concreta del Strategy.

    Regla:
      - Normalmente elige trabajos Premium sobre Gratuitos.
      - Cuando se han procesado MAX_CONSECUTIVE_PREMIUM trabajos premium
        seguidos y hay trabajos Gratuitos en espera, FUERZA uno Gratuito.
        Esto garantiza que ningún trabajo Gratuito espere más de
        MAX_CONSECUTIVE_PREMIUM * max_processing_time segundos.
    """

    def __init__(self, max_consecutive_premium: int = 3):
        self.max_consecutive = max_consecutive_premium

    def select(
        self,
        premium_queue: list,
        free_queue   : list,
        consecutive_premium: int,
    ) -> Optional[Job]:

        # Condición de anti-inanición: forzar trabajo gratuito
        if consecutive_premium >= self.max_consecutive and free_queue:
            job = free_queue.pop(0)
            job.forced_free = True
            return job

        # Flujo normal: Premium tiene prioridad
        if premium_queue:
            return premium_queue.pop(0)

        if free_queue:
            return free_queue.pop(0)

        return None