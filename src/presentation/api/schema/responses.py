from datetime import datetime

from pydantic import BaseModel, Field


class InventoryItem(BaseModel):
    name: str = Field(description="Name of the inventory item")
    type: str = Field(description="Product type (consumable | permanent)")
    price: int = Field(description="Product price")
    quantity: int = Field(description="Quantity of the product")
    purchased_at: datetime = Field(description="Date and time when the product was purchased")


class InventoryResponse(BaseModel):
    products: list[InventoryItem] = Field(description="Products list")


class PopularProduct(BaseModel):
    product_id: int = Field(description="ID of the product")
    name: str = Field(description="Name of the product")
    price: int = Field(description="Product's price")
    type: str = Field(description="Product type (consumable | permanent)")
    purchase_count: int = Field(description="Number of times the product was purchased")


class PopularProductsResponse(BaseModel):
    products: list[PopularProduct] = Field(description="Products list")


class FundsAddedResponse(BaseModel):
    message: str = Field(description="Success message")
    user_id: int = Field(description="ID of the User")
    previous_balance: int = Field(description="User's previous balance")
    current_balance: int = Field(description="User's current balance")


class ProductConsumedResponse(BaseModel):
    message: str = Field(description="Success message")
    product_id: int = Field(description="ID of the used product")
    product_name: str = Field(description="Name of the product")
    previous_quantity: int = Field(description="Previous quantity of the product")
    current_quantity: int = Field(description="Current quantity of the product after consumption")


class ProductPurchasedResponse(BaseModel):
    message: str = Field(description="Success message")
    product_id: int = Field(description="ID of the purchased product")
    price: int = Field(description="Price paid for the product")
    balance: int = Field(description="User's remaining balance after purchase")


COMMON_RESPONSES = {
    400: {
        "description": "Bad request",
        "content": {
            "application/json": {
                "example": {"error": "Bad request", "details (optional)": [{"description": "error description"}]}
            }
        },
    },
    401: {"description": "Unauthorized", "content": {"application/json": {"example": {"error": "Unauthorized"}}}},
    403: {"description": "Forbidden", "content": {"application/json": {"example": {"error": "Access denied"}}}},
    404: {
        "description": "Not found",
        "content": {
            "application/json": {
                "example": {"error": "Not found", "details (optional)": [{"description": "error description"}]}
            }
        },
    },
    429: {
        "description": "Too many requests",
        "content": {"application/json": {"example": {"error": "Rate limit exceeded"}}},
    },
}
