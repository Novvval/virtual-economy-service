from src.interfaces.repository import Repository
from ..models.inventory import Inventory
from ..models.product import Product


class InventoryRepository(Repository):
    async def find_inventory(self, product_id: int, user_id: int) -> Inventory:
        query = self.db.queries["find_inventory"]
        return await self.db.find_one(query, {"product_id": product_id, "user_id": user_id})

    async def find_product(self, product_id: int) -> Product:
        query = self.db.queries["find_product_by_id"]
        return await self.db.find_one(query, {"product_id": product_id})

    async def list(self, user_id: int) -> list[Inventory]:
        query = self.db.queries["find_inventories_by_user"]
        return await self.db.find_many(query, {"user_id": user_id})
