from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.domain.entities.payment_request import PaymentRequest, MethodType, PaymentStatus
from src.infrastructure.persistence.models import PaymentModel


class SQLPaymentRepository:
    def __init__(self, db: Session):
        self._db = db

    def save(self, request: PaymentRequest) -> PaymentModel:
        existing = (
            self._db.query(PaymentModel)
            .filter(PaymentModel.request_id == request.request_id)
            .first()
        )
        if existing:
            existing.status = request.status.value
            existing.commission = request.commission
            existing.final_amount = request.final_amount
            self._db.flush()
            return existing

        model = PaymentModel(
            request_id=request.request_id,
            merchant_id=request.merchant_id,
            amount=request.amount,
            currency=request.currency,
            method_type=request.method_type.value,
            priority=request.priority,
            status=request.status.value,
            commission=request.commission,
            final_amount=request.final_amount,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.flush()
        return model

    def find_by_id(self, request_id: str) -> PaymentRequest | None:
        model = (
            self._db.query(PaymentModel)
            .filter(PaymentModel.request_id == request_id)
            .first()
        )
        if not model:
            return None

        return PaymentRequest(
            request_id=model.request_id,
            merchant_id=model.merchant_id,
            amount=model.amount,
            currency=model.currency,
            method_type=MethodType(model.method_type),
            priority=model.priority,
            status=PaymentStatus(model.status),
            commission=model.commission,
            final_amount=model.final_amount,
        )
