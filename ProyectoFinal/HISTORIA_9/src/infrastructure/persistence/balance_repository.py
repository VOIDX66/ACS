import threading
from collections import defaultdict

from src.domain.interfaces.payment_repository import BalanceRepository


class InMemoryBalanceRepository(BalanceRepository):
    def __init__(self):
        self._balances: dict[int, float] = defaultdict(float)
        self._lock = threading.Lock()

    def get_balance(self, merchant_id: int) -> float:
        with self._lock:
            return self._balances[merchant_id]

    def add_funds(self, merchant_id: int, amount: float) -> None:
        with self._lock:
            self._balances[merchant_id] += amount
