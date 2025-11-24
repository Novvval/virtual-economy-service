import enum
from dataclasses import dataclass
from datetime import datetime

from src.interfaces.domain_model import DomainModel


@dataclass(kw_only=True)
class Transaction(DomainModel):
    class Status(enum.Enum):
        PENDING = 1
        COMPLETED = 2
        FAILED = 3

    user_id: int
    product_id: int
    amount: int
    status: Status
    created_at: datetime = datetime.now()
