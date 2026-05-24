from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.presentation.api.deps import get_current_user
from src.presentation.schemas.payment_schema import PaymentCreate, PaymentResponse
from src.domain.entities.payment_request import PaymentRequest, MethodType
from src.infrastructure.persistence.models import UserModel
from src.application.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/batch", response_model=list[PaymentResponse])
def submit_batch(
    body: list[PaymentCreate],
    user: UserModel = Depends(get_current_user),
):
    requests = [
        PaymentRequest(
            merchant_id=p.merchant_id,
            amount=p.amount,
            currency=p.currency,
            method_type=MethodType(p.method_type.value),
            priority=p.priority,
        )
        for p in body
    ]

    service = PaymentService()
    service.process_batch(requests)

    return [
        PaymentResponse(
            request_id=r.request_id,
            merchant_id=r.merchant_id,
            amount=r.amount,
            currency=r.currency,
            status=r.status.value,
            commission=r.commission,
            final_amount=r.final_amount,
        )
        for r in requests
    ]
