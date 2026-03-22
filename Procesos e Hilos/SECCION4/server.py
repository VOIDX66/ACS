"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Servidor — Orquestador (VideoTranscodingServer).
"""

import threading
import time
from typing import List

from clients import Client, ClientFactory
from observers import EventObserver, ConsoleLogger
from queue import PriorityJobQueue
from strategies import AntiStarvationStrategy
from workers import Worker


class VideoTranscodingServer:
    """
    Orquesta la creación de la cola, workers y clientes.
    Implementa el patrón Producer-Consumer a nivel de sistema.
    """

    def __init__(
        self,
        num_workers           : int = 3,
        max_consecutive_premium: int = 3,
    ):
        self._observers: List[EventObserver] = [ConsoleLogger()]

        strategy     = AntiStarvationStrategy(max_consecutive_premium)
        self._queue  = PriorityJobQueue(strategy)

        self._workers: List[Worker] = [
            Worker(f"Worker-{i+1}", self._queue, self._observers)
            for i in range(num_workers)
        ]
        self._clients: List[Client] = []

    def add_client(self, client_type: str, name: str) -> None:
        client = ClientFactory.create(client_type, name, self._queue, self._observers)
        self._clients.append(client)

    def start(self) -> None:
        for obs in self._observers:
            obs.on_system_started(len(self._workers), len(self._clients))

        # Iniciar workers (hilos demonio)
        worker_threads = []
        for w in self._workers:
            t = threading.Thread(target=w.run, name=w.name, daemon=True)
            worker_threads.append(t)
            t.start()

        # Iniciar clientes (hilos productores)
        client_threads = []
        for c in self._clients:
            t = threading.Thread(target=c.run, name=c.name)
            client_threads.append(t)
            t.start()

        # Esperar a que todos los clientes terminen de enviar trabajos
        for t in client_threads:
            t.join()

        # Drenar la cola: esperar hasta que esté vacía
        while self._queue.size > 0:
            time.sleep(0.05)

        # Dar tiempo a que el último trabajo en vuelo termine
        time.sleep(max(w._queue._cond.__class__.__name__ and 0.5 for w in self._workers))
        time.sleep(0.8)

        # Señal de apagado a los workers
        self._queue.shutdown()
        for t in worker_threads:
            t.join(timeout=5)

        # Recopilar estadísticas y notificar
        queue_stats = self._queue.stats
        stats = {
            "workers"        : {w.name: w.jobs_processed for w in self._workers},
            "total_sent"     : sum(c.jobs_sent for c in self._clients),
            "total_processed": sum(w.jobs_processed for w in self._workers),
            "forced"         : queue_stats["forced"],
        }
        for obs in self._observers:
            obs.on_system_finished(stats)