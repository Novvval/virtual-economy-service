from dataclasses import dataclass
from datetime import datetime
from ..errors import ValidationError

from src.interfaces.domain_model import DomainModel


@dataclass(kw_only=True)
class User(DomainModel):
    username: str
    email: str
    balance: int
    created_at: datetime = datetime.now()

    def add_funds(self, amount: int, maximum_allowed: int) -> int:
        if amount > maximum_allowed:
            raise ValidationError("Amount exceeds maximum allowed")
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        self.balance += amount
        return self.balance

    def remove_funds(self, amount: int):
        if amount > self.balance:
            raise ValidationError("Insufficient balance")
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        self.balance -= amount
        return self.balance
