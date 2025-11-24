import json

from src.application.errors import NotFound
from src.interfaces.usecase import UseCase


class AddFunds(UseCase):
    async def __call__(self, user_id: int, amount: int, idempotency_hash: str):
        async with self.ctx.uow as uow:
            cached = await self.ctx.cache.get(idempotency_hash)
            if cached:
                return json.loads(cached)

            user = await self.ctx.user_repo.find_user(user_id)
            if user is None:
                raise NotFound(f"User with id {user_id} doesn't exist")
            prev_balance = user.balance
            user.add_funds(amount, self.ctx.maximum_allowed)
            cur_balance = user.balance

            await uow.persist([user])
            message = {
                "message": "Funds added",
                "user_id": user.id,
                "previous_balance": prev_balance,
                "current_balance": cur_balance,
            }
            uow.cache_set(idempotency_hash, json.dumps(message), {"ttl": 60 * 5})
            return message
