import random
import time
import threading
from queue import Empty

from src.core.console import console
from src.domain.entities.payment_request import PaymentRequest, PaymentStatus
from src.domain.interfaces.payment_repository import BalanceRepository
from src.infrastructure.sync.payment_queue import PaymentQueue
from src.infrastructure.sync.payment_config import payment_config


class PaymentWorker(threading.Thread):
    def __init__(self, worker_label: str, queue: PaymentQueue, repo: BalanceRepository):
        super().__init__(name=f"Worker-{worker_label}", daemon=True)
        self._queue = queue
        self._repo = repo
        self._label = worker_label
        self.processed = 0

    def run(self):
        console.log(f"[worker]{self.name}[/] iniciado, esperando pagos...")
        while True:
            request = self._queue.dequeue(timeout=3.0)
            if request is None:
                break

            request.status = PaymentStatus.PROCESSING

            rate = payment_config.get_rate(request.currency)
            request.commission = round(request.amount * 0.05, 2)
            net_amount = request.amount - request.commission
            request.final_amount = round(net_amount * rate, 2)

            console.log(
                f"[worker]{self.name}[/] procesando pago [amount]{request.request_id}[/] "
                f"merchant [merchant]{request.merchant_id}[/] "
                f"método [info]{request.method_type.value}[/] ... "
                f"Comisión [currency]{request.display_commission}[/]"
            )

            time.sleep(random.uniform(0.2, 0.8))

            request.status = PaymentStatus.COMPLETED
            self._repo.add_funds(request.merchant_id, request.final_amount)

            console.log(
                f"[worker]{self.name}[/] [status.completed]completado[/] "
                f"pago [amount]{request.request_id}[/]. "
                f"Nuevo saldo merchant [merchant]{request.merchant_id}[/]: "
                f"[amount]{self._repo.get_balance(request.merchant_id):.2f}[/] USD"
            )

            self.processed += 1
            self._queue.task_done()
