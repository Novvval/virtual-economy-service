from dataclasses import dataclass
from datetime import datetime

from src.interfaces.domain_model import DomainModel
from .product import Product
from .user import User
from ..errors import ValidationError


@dataclass(kw_only=True)
class Inventory(DomainModel):
    user: User
    product: Product
    quantity: int = 0
    purchased_at: datetime = datetime.now()

    def update_quantity(self, quantity: int = 1):
        if self.product.type == self.product.Type.PERMANENT and self.quantity == 1:
            raise ValidationError("Permanent product already purchased")
        if self.user.balance < self.product.price:
            raise ValidationError("Insufficient balance")
        self.quantity += quantity

    def decrease_quantity(self, quantity: int = 1):
        if self.quantity - quantity < 0:
            raise ValidationError("Insufficient quantity")
        self.quantity -= quantity
