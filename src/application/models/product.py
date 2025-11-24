import enum
from dataclasses import dataclass
from datetime import datetime

from src.interfaces.domain_model import DomainModel


@dataclass(kw_only=True)
class Product(DomainModel):
    class Type(enum.Enum):
        CONSUMABLE = "consumable"
        PERMANENT = "permanent"

    name: str
    description: str
    price: int
    type: Type
    is_active: bool
    created_at: datetime | None = None
