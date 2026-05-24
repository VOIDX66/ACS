from sqlalchemy.orm import Session

from src.domain.entities.payment_request import PaymentRequest
from src.domain.interfaces.payment_repository import PaymentRepository


class SQLPaymentRepository(PaymentRepository):
    def __init__(self, db: Session):
        self._db = db

    def save(self, request: PaymentRequest) -> None:
        ...

    def find_by_id(self, request_id: str) -> PaymentRequest | None:
        ...
