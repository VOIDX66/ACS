import itertools
import threading
from queue import Queue, PriorityQueue, Empty, Full

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
                    cls._instance._use_priority = False
                    cls._instance._counter = itertools.count()
        return cls._instance

    def enable_priority(self) -> None:
        if not self._use_priority and self._q.empty():
            self._q = PriorityQueue(maxsize=settings.QUEUE_MAX_SIZE)
            self._use_priority = True

    def enqueue(self, request: PaymentRequest) -> bool:
        try:
            if self._use_priority:
                item = (-request.priority, next(self._counter), request)
            else:
                item = request
            self._q.put(item, block=True, timeout=5)
            return True
        except Full:
            console.log("[error]Cola llena, no se pudo encolar[/]")
            return False

    def dequeue(self, timeout: float = 2.0) -> PaymentRequest | None:
        try:
            item = self._q.get(block=True, timeout=timeout)
            if self._use_priority:
                _, _, request = item
                return request
            return item
        except Empty:
            return None

    def task_done(self) -> None:
        self._q.task_done()

    def join(self) -> None:
        self._q.join()

    @property
    def qsize(self) -> int:
        return self._q.qsize()
