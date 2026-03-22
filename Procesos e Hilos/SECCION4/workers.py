"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Worker (Consumidor).
"""

import random
import time
from typing import List

from models import Job
from observers import EventObserver
from queue import PriorityJobQueue


class Worker:
    """
    Hilo consumidor. Extrae trabajos de la cola y los procesa
    (simulado con time.sleep). Notifica a los observers.
    """

    def __init__(
        self,
        name     : str,
        queue    : PriorityJobQueue,
        observers: List[EventObserver],
    ):
        self.name            = name
        self._queue          = queue
        self._observers      = observers
        self.jobs_processed  = 0

    def run(self) -> None:
        while True:
            job = self._queue.get()
            if job is None:
                break                              # señal de parada

            for obs in self._observers:
                obs.on_job_started(self.name, job)

            duration = random.uniform(0.3, 1.2)   # simula transcodificación
            time.sleep(duration)

            self.jobs_processed += 1
            for obs in self._observers:
                obs.on_job_completed(self.name, job, duration)