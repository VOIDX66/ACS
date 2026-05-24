from src.core.config import settings
from src.infrastructure.sync.payment_queue import PaymentQueue
from src.infrastructure.persistence.balance_repository import InMemoryBalanceRepository
from src.infrastructure.worker_pool.payment_worker import PaymentWorker

_LABELS = ["A", "B", "C", "D", "E", "F"]


class WorkerPoolFactory:
    @staticmethod
    def create_pool(num_workers: int | None = None, use_priority: bool = False):
        workers = num_workers or settings.PAYMENT_WORKERS
        queue = PaymentQueue()

        if use_priority:
            queue.enable_priority()

        repo = InMemoryBalanceRepository()
        pool = WorkerPoolManager._from_factory(workers, queue, repo)
        return pool


class WorkerPoolManager:
    def __init__(self, num_workers: int = 3):
        self._queue = PaymentQueue()
        self._repo = InMemoryBalanceRepository()
        self._workers: list[PaymentWorker] = []
        self._num_workers = num_workers

    @classmethod
    def _from_factory(cls, num_workers, queue, repo):
        instance = cls.__new__(cls)
        instance._queue = queue
        instance._repo = repo
        instance._workers = []
        instance._num_workers = num_workers
        return instance

    def start(self) -> None:
        for i in range(self._num_workers):
            worker = PaymentWorker(
                worker_label=_LABELS[i % len(_LABELS)],
                queue=self._queue,
                repo=self._repo,
            )
            worker.start()
            self._workers.append(worker)

    def join(self) -> None:
        self._queue.join()
        for w in self._workers:
            w.join(timeout=5)

    @property
    def queue(self) -> PaymentQueue:
        return self._queue

    @property
    def repo(self) -> InMemoryBalanceRepository:
        return self._repo

    @property
    def workers(self) -> list[PaymentWorker]:
        return self._workers
