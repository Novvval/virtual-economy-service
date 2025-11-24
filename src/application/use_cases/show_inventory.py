import json

from src.interfaces.usecase import UseCase


class ShowInventory(UseCase):
    async def __call__(self, user_id: int) -> list[dict]:
        cached = await self.ctx.cache.get(f"inventory:{user_id}")
        if cached:
            return json.loads(cached)
        else:
            inventory = await self.ctx.inventory_repo.list(user_id)
            inventory_serialized = [inv.asdict() for inv in inventory]
            await self.ctx.cache.set(
                f"inventory:{user_id}", json.dumps(inventory_serialized, default=str), {"ttl": 60 * 5}
            )

            return inventory_serialized
