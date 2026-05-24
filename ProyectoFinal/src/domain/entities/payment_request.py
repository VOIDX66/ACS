from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MethodType(str, Enum):
    CARD = "tarjeta"
    WIRE = "transferencia"
    WALLET = "billetera"


@dataclass
class PaymentRequest:
    merchant_id: int
    amount: float
    currency: str
    method_type: MethodType
    request_id: str = field(default_factory=lambda: uuid4().hex[:8])
    priority: int = 0
    status: PaymentStatus = PaymentStatus.PENDING
    commission: float = 0.0
    final_amount: float = 0.0

    @property
    def display_amount(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    @property
    def display_commission(self) -> str:
        return f"{self.commission:.2f} {self.currency}"

    @property
    def display_final(self) -> str:
        return f"{self.final_amount:.2f} USD"
