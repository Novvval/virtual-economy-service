import json

from src.interfaces.usecase import UseCase
from ..errors import NotFound
from ..models.inventory import Inventory
from ..models.transaction import Transaction


class AddPurchase(UseCase):
    async def __call__(self, product_id: int, user_id: int, idempotency_hash: str, quantity: int = 1) -> dict:
        async with self.ctx.uow as uow:
            cached = await self.ctx.cache.get(idempotency_hash)
            if cached:
                return json.loads(cached)
            product = await self.ctx.inventory_repo.find_product(product_id)
            if product is None:
                raise NotFound(f"Product with id {product_id} doesn't exist")

            user = await self.ctx.user_repo.find_user(user_id)
            inventory = await self.ctx.inventory_repo.find_inventory(product_id, user_id)
            if inventory:
                inventory.update_quantity(quantity)
            else:
                inventory = Inventory(user=user, product=product, quantity=quantity)

            user.remove_funds(product.price)
            # In a real scenario, we would return a pending transaction here, and then handle the payments in separate
            # usecase
            transaction = Transaction(
                user_id=user.id, product_id=product_id, amount=quantity, status=Transaction.Status.COMPLETED
            )
            await uow.persist([user, inventory, transaction])

            async with self.ctx.uow as nested_uow:
                full_inventory = await self.ctx.inventory_repo.list(user_id)
                nested_uow.cache_set(
                    f"inventory:{user_id}",
                    json.dumps([inv.asdict() for inv in full_inventory], default=str),
                    options={"ttl": 60 * 5},
                )
                message = {
                    "message": "Product purchased",
                    "product_id": product_id,
                    "price": product.price,
                    "balance": user.balance,
                }
                nested_uow.cache_set(idempotency_hash, json.dumps(message), options={"ttl": 60 * 5})

                return message
