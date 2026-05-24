from abc import ABC, abstractmethod

from src.domain.entities.payment_request import PaymentRequest


class BalanceRepository(ABC):
    @abstractmethod
    def get_balance(self, merchant_id: int) -> float: ...

    @abstractmethod
    def add_funds(self, merchant_id: int, amount: float) -> None: ...


class PaymentRepository(ABC):
    @abstractmethod
    def save(self, request: PaymentRequest) -> None: ...

    @abstractmethod
    def find_by_id(self, request_id: str) -> PaymentRequest | None: ...
