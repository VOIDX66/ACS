"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Patrón Observer — Logging desacoplado.
"""

import threading
from abc import ABC, abstractmethod
from typing import List

from models import Job, Priority


class EventObserver(ABC):
    @abstractmethod
    def on_job_submitted(self, job: Job) -> None: ...

    @abstractmethod
    def on_job_started(self, worker_name: str, job: Job) -> None: ...

    @abstractmethod
    def on_job_completed(self, worker_name: str, job: Job, duration: float) -> None: ...

    @abstractmethod
    def on_system_started(self, num_workers: int, num_clients: int) -> None: ...

    @abstractmethod
    def on_system_finished(self, stats: dict) -> None: ...


class ConsoleLogger(EventObserver):
    """Implementación concreta del Observer: escribe en stdout de forma thread-safe."""

    RESET  = "\033[0m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"

    def __init__(self):
        self._lock = threading.Lock()

    def _print(self, msg: str) -> None:
        with self._lock:
            print(msg)

    def on_job_submitted(self, job: Job) -> None:
        color = self.YELLOW if job.priority == Priority.PREMIUM else self.CYAN
        self._print(
            f"{color}  ↑  {job.client_name}: Envió trabajo [{job.video_name}]{self.RESET}"
        )

    def on_job_started(self, worker_name: str, job: Job) -> None:
        color  = self.YELLOW if job.priority == Priority.PREMIUM else self.CYAN
        note   = f" {self.MAGENTA}⚠ (anti-inanición: forzado){self.RESET}" if job.forced_free else ""
        self._print(
            f"{self.BOLD}{self.BLUE}  ► {worker_name}{self.RESET}: "
            f"Procesando [{job.video_name}] de {color}{job.client_name}{self.RESET} "
            f"[{job.priority.label()}]{note}"
        )

    def on_job_completed(self, worker_name: str, job: Job, duration: float) -> None:
        self._print(
            f"{self.GREEN}  ✓ {worker_name}{self.RESET}: "
            f"Completó [{job.video_name}] en {duration:.2f}s"
        )

    def on_system_started(self, num_workers: int, num_clients: int) -> None:
        sep = "═" * 60
        self._print(f"\n{self.BOLD}{sep}")
        self._print(f"  🚀 Sistema de Transcodificación de Vídeo")
        self._print(f"     {num_workers} workers  |  {num_clients} clientes")
        self._print(f"{sep}{self.RESET}\n")

    def on_system_finished(self, stats: dict) -> None:
        sep = "═" * 60
        self._print(f"\n{self.BOLD}{sep}")
        self._print(f"  🏁 --- Sistema finalizado ---")
        self._print(f"{sep}{self.RESET}")
        self._print(f"\n{self.BOLD}📊 Estadísticas finales:{self.RESET}")
        for name, count in stats["workers"].items():
            self._print(f"   {name}: {count} trabajos procesados")
        self._print(f"\n   Total enviados  : {stats['total_sent']}")
        self._print(f"   Total procesados: {stats['total_processed']}")
        self._print(f"   Forzados (anti-inanición): {stats['forced']}")
        self._print("")