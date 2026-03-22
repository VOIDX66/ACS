"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Patrones de diseño aplicados:
  - Producer-Consumer  : clientes (productores) + workers (consumidores) + cola compartida
  - Strategy           : AntiStarvationStrategy — encapsula la lógica de selección de trabajos
  - Observer           : ConsoleLogger — desacoplado del servidor, registra eventos
  - Factory            : ClientFactory — crea instancias de PremiumClient / FreeClient
  - Template Method    : Client.run() define el esqueleto; _generate_job() es el hook

Primitivas de sincronización:
  - threading.Condition (wraps un Lock) : acceso exclusivo a la cola + wait/notify para workers
  - threading.Event                     : señal de "no llegan más trabajos" (shutdown)
  - counter simple protegido por el mismo Lock : cuenta premiums consecutivos para anti-inanición
"""

import threading
import time
import random
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List

import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════════
# ENUMS Y DATA CLASSES
# ═══════════════════════════════════════════════════════

class Priority(Enum):
    PREMIUM = 1
    FREE    = 2

    def label(self) -> str:
        return "Premium" if self == Priority.PREMIUM else "Gratuito"


@dataclass
class Job:
    job_id     : str
    video_name : str
    client_name: str
    priority   : Priority
    arrival_time: float = field(default_factory=time.time)
    forced_free : bool  = False          # marcado por la estrategia anti-inanición

    def __str__(self) -> str:
        return f"[{self.video_name}] de {self.client_name} ({self.priority.label()})"


# ═══════════════════════════════════════════════════════
# PATRÓN OBSERVER — Logging desacoplado
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# PATRÓN STRATEGY — Selección del próximo trabajo
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# COLA CON PRIORIDAD — Thread-safe
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# PATRÓN TEMPLATE METHOD — Clientes (Productores)
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# PATRÓN FACTORY — Creación de clientes
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# WORKER (Consumidor)
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# SERVIDOR — Orquestador (VideoTranscodingServer)
# ═══════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    random.seed(42)   # reproducibilidad para pruebas; quitar en producción

    server = VideoTranscodingServer(
        num_workers            = 3,
        max_consecutive_premium= 3,   # fuerza un Gratuito cada 3 Premiums consecutivos
    )

    # Agregar clientes Premium (3)
    for i in range(1, 4):
        server.add_client("premium", f"Cliente-Premium-{i}")

    # Agregar clientes Gratuitos (5)
    for i in range(1, 6):
        server.add_client("free", f"Cliente-Gratis-{i}")

    server.start()