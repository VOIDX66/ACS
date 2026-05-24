from src.infrastructure.sync.payment_queue import PaymentQueue
from src.infrastructure.persistence.balance_repository import InMemoryBalanceRepository
from src.infrastructure.worker_pool.payment_worker import PaymentWorker


class WorkerPoolManager:
    def __init__(self, num_workers: int = 3):
        self._queue = PaymentQueue()
        self._repo = InMemoryBalanceRepository()
        self._workers: list[PaymentWorker] = []
        self._num_workers = num_workers

    def start(self) -> None:
        labels = ["A", "B", "C", "D", "E", "F"]
        for i in range(self._num_workers):
            worker = PaymentWorker(
                worker_label=labels[i % len(labels)],
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
