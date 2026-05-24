import threading
import time

from src.core.console import console
from src.domain.entities.payment_request import PaymentRequest
from src.infrastructure.worker_pool.pool_manager import WorkerPoolManager
from src.infrastructure.metrics.collector import metrics
from rich.table import Table


class PaymentService:
    def __init__(self):
        self._pool = WorkerPoolManager()

    def process_batch(self, requests: list[PaymentRequest]) -> Table:
        self._pool.start()
        start = time.time()

        producer_threads = []
        for i, request in enumerate(requests, 1):
            t = threading.Thread(
                target=self._enqueue_request,
                args=(i, request),
                daemon=True,
            )
            t.start()
            producer_threads.append(t)

        for t in producer_threads:
            t.join()

        self._pool.join()
        metrics.increment("batch_completed")
        metrics.record_timing("batch_duration", time.time() - start)

        return self._build_summary_table(requests)

    def _enqueue_request(self, producer_id: int, request: PaymentRequest) -> None:
        self._pool.queue.enqueue(request)
        metrics.increment("payments_enqueued")
        console.log(
            f"[producer]Productor {producer_id}[/] encolando pago de "
            f"merchant [merchant]{request.merchant_id}[/] "
            f"por [amount]{request.display_amount}[/]"
        )

    def _build_summary_table(self, requests: list[PaymentRequest]) -> Table:
        table = Table(title="[header]Resumen de Pagos Procesados[/]", header_style="header")
        table.add_column("ID", style="dim")
        table.add_column("Merchant", style="merchant")
        table.add_column("Monto", style="amount")
        table.add_column("Comisión", style="currency")
        table.add_column("Final (USD)", style="amount")
        table.add_column("Estado", style="status.completed")

        for r in requests:
            status_style = {
                "pending": "status.pending",
                "processing": "status.processing",
                "completed": "status.completed",
                "failed": "status.failed",
            }.get(r.status.value, "white")

            table.add_row(
                r.request_id,
                str(r.merchant_id),
                r.display_amount,
                r.display_commission,
                r.display_final,
                f"[{status_style}]{r.status.value.upper()}[/]",
            )

        for w in self._pool.workers:
            table.caption = f"Workers: {[f'{w.name} ({w.processed} pagos)' for w in self._pool.workers]}"

        return table
