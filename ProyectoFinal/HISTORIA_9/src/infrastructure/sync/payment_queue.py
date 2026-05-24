import threading
from queue import Queue, Empty, Full

from src.core.config import settings
from src.core.console import console
from src.domain.entities.payment_request import PaymentRequest


class PaymentQueue:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._q = Queue(maxsize=settings.QUEUE_MAX_SIZE)
        return cls._instance

    def enqueue(self, request: PaymentRequest) -> bool:
        try:
            self._q.put(request, block=True, timeout=5)
            return True
        except Full:
            console.log("[error]Cola llena, no se pudo encolar[/]")
            return False

    def dequeue(self, timeout: float = 2.0) -> PaymentRequest | None:
        try:
            return self._q.get(block=True, timeout=timeout)
        except Empty:
            return None

    def task_done(self) -> None:
        self._q.task_done()

    def join(self) -> None:
        self._q.join()

    @property
    def qsize(self) -> int:
        return self._q.qsize()
