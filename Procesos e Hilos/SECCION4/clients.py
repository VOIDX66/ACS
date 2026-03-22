"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Patrón Template Method — Clientes (Productores).
Patrón Factory — Creación de clientes.
"""

import random
import time
import uuid
from abc import ABC
from typing import List

from models import Job, Priority
from observers import EventObserver
from queue import PriorityJobQueue


class Client(ABC):
    """
    Clase base abstracta. Define el esqueleto del comportamiento del cliente
    (Template Method: run → _send_jobs → _generate_job).
    """

    def __init__(
        self,
        name     : str,
        priority : Priority,
        queue    : PriorityJobQueue,
        observers: List[EventObserver],
    ):
        self.name      = name
        self.priority  = priority
        self._queue    = queue
        self._observers= observers
        self.jobs_sent = 0

    # Template Method — no sobreescribir
    def run(self) -> None:
        num_jobs = random.randint(5, 10)
        for _ in range(num_jobs):
            time.sleep(random.uniform(0.05, 0.3))   # simula ritmo del cliente
            job = self._generate_job()
            self._queue.put(job)
            self.jobs_sent += 1
            for obs in self._observers:
                obs.on_job_submitted(job)

    # Hook — puede ser sobreescrito por subclases
    def _generate_job(self) -> Job:
        video_name = f"VIDEO-{uuid.uuid4().hex[:6].upper()}"
        return Job(
            job_id     = str(uuid.uuid4()),
            video_name = video_name,
            client_name= self.name,
            priority   = self.priority,
        )


class PremiumClient(Client):
    def __init__(self, name: str, queue: PriorityJobQueue, observers: list):
        super().__init__(name, Priority.PREMIUM, queue, observers)


class FreeClient(Client):
    def __init__(self, name: str, queue: PriorityJobQueue, observers: list):
        super().__init__(name, Priority.FREE, queue, observers)


class ClientFactory:
    """Fábrica simple: desacopla la creación del tipo concreto de cliente."""

    @staticmethod
    def create(
        client_type: str,
        name       : str,
        queue      : PriorityJobQueue,
        observers  : list,
    ) -> Client:
        if client_type == "premium":
            return PremiumClient(name, queue, observers)
        if client_type == "free":
            return FreeClient(name, queue, observers)
        raise ValueError(f"Tipo de cliente desconocido: '{client_type}'")