import threading

from src.infrastructure.sync.read_write_lock import ReadWriteLock


class PaymentConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._rates = {
                        "USD": 1.0,
                        "EUR": 1.08,
                        "GBP": 1.27,
                        "JPY": 0.0067,
                    }
                    cls._instance._rwlock = ReadWriteLock()
        return cls._instance

    def get_rate(self, currency: str) -> float:
        self._rwlock.acquire_read()
        try:
            return self._rates.get(currency, 1.0)
        finally:
            self._rwlock.release_read()

    def update_rates(self, new_rates: dict[str, float]) -> None:
        self._rwlock.acquire_write()
        try:
            self._rates.update(new_rates)
        finally:
            self._rwlock.release_write()

    @property
    def rates(self) -> dict:
        self._rwlock.acquire_read()
        try:
            return dict(self._rates)
        finally:
            self._rwlock.release_read()


payment_config = PaymentConfig()
