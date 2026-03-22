"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Cola con prioridad — Thread-safe.
"""

import threading
from typing import Optional, List

from models import Job, Priority
from strategies import JobSelectionStrategy


class PriorityJobQueue:
    """
    Cola de dos niveles (Premium / Gratuito) protegida con
    threading.Condition para wait/notify entre productores y consumidores.
    """

    def __init__(self, strategy: JobSelectionStrategy):
        self._premium_queue : List[Job] = []
        self._free_queue    : List[Job] = []
        self._strategy      = strategy
        self._consecutive_premium = 0
        self._total_submitted     = 0
        self._forced_count        = 0

        # Condition internaliza un Lock; lo usamos para TODA la sección crítica
        self._cond     = threading.Condition()
        self._shutdown = False       # señal: no llegan más trabajos

    # ── Productor ──────────────────────────────────────
    def put(self, job: Job) -> None:
        with self._cond:
            if job.priority == Priority.PREMIUM:
                self._premium_queue.append(job)
            else:
                self._free_queue.append(job)
            self._total_submitted += 1
            self._cond.notify()          # despierta un worker en espera

    # ── Consumidor ─────────────────────────────────────
    def get(self) -> Optional[Job]:
        """Bloquea hasta que haya un trabajo disponible o shutdown sea True."""
        with self._cond:
            # Esperar mientras no hay trabajo Y aún pueden llegar más
            while not self._premium_queue and not self._free_queue:
                if self._shutdown:
                    return None           # señal de parada: el worker debe terminar
                self._cond.wait()

            # Si shutdown y cola vacía → salir
            if self._shutdown and not self._premium_queue and not self._free_queue:
                return None

            job = self._strategy.select(
                self._premium_queue,
                self._free_queue,
                self._consecutive_premium,
            )

            if job is None:
                return None

            # Actualizar contador anti-inanición
            if job.forced_free or job.priority == Priority.FREE:
                self._consecutive_premium = 0
            else:
                self._consecutive_premium += 1

            if job.forced_free:
                self._forced_count += 1

            return job

    # ── Control ────────────────────────────────────────
    def shutdown(self) -> None:
        """Señala a todos los workers que no habrá más trabajos."""
        with self._cond:
            self._shutdown = True
            self._cond.notify_all()

    @property
    def size(self) -> int:
        with self._cond:
            return len(self._premium_queue) + len(self._free_queue)

    @property
    def stats(self) -> dict:
        with self._cond:
            return {
                "total_submitted": self._total_submitted,
                "forced"         : self._forced_count,
            }