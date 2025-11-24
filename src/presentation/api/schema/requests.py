from pydantic import BaseModel, Field


class ConsumeProductRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount of consumable products to subtract from the user's inventory")


class AddFundsRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount to add to user balance (must be positive)")


class PurchaseRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount of products to purchase (must be positive)")
