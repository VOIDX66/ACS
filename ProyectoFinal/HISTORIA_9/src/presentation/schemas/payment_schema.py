from enum import Enum

from pydantic import BaseModel


class MethodTypeEnum(str, Enum):
    CARD = "tarjeta"
    WIRE = "transferencia"
    WALLET = "billetera"


class PaymentCreate(BaseModel):
    merchant_id: int
    amount: float
    currency: str = "USD"
    method_type: MethodTypeEnum = MethodTypeEnum.CARD


class PaymentResponse(BaseModel):
    request_id: str
    merchant_id: int
    amount: float
    currency: str
    status: str
    commission: float
    final_amount: float
