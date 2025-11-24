import json

from src.interfaces.usecase import UseCase
from ..errors import NotFound


class ConsumeProduct(UseCase):
    async def __call__(self, product_id: int, user_id: int, idempotency_hash: str, quantity: int = 1) -> dict:
        async with self.ctx.uow as uow:
            cached = await self.ctx.cache.get(idempotency_hash)
            if cached:
                return json.loads(cached)
            inventory = await self.ctx.inventory_repo.find_inventory(product_id, user_id)
            if not inventory:
                raise NotFound(f"Inventory with product id {product_id} doesn't exist")
            prev_quantity = inventory.quantity
            inventory.decrease_quantity(quantity)
            current_quantity = inventory.quantity
            if inventory.quantity >= 0:
                await uow.persist([inventory])
            else:
                await uow.delete([inventory])
            message = {
                "message": "Product consumed",
                "product_id": product_id,
                "product_name": inventory.product.name,
                "previous_quantity": prev_quantity,
                "current_quantity": current_quantity,
            }
            full_inventory = await self.ctx.inventory_repo.list(user_id)
            uow.cache_set(
                f"inventory:{user_id}",
                json.dumps([inv.asdict() for inv in full_inventory], default=str),
                options={"ttl": 60 * 5},
            )
            uow.cache_set(idempotency_hash, json.dumps(message), options={"ttl": 60 * 5})
            return message
