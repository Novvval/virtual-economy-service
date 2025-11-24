import json
from datetime import timedelta, date
from src.interfaces.usecase import UseCase


class ShowPopularProducts(UseCase):
    async def __call__(self, limit: int = 5, start_date=None) -> list[dict]:
        start_date = start_date or date.today() - timedelta(days=7)
        cached = await self.ctx.cache.get(f"popular_products:{str(start_date)}:{limit}")
        if cached:
            return json.loads(cached)
        result = await self.ctx.product_repo.find_popular_products(start_date, limit)
        await self.ctx.cache.set(
            f"popular_products:{str(start_date)}:{limit}", json.dumps(result, default=str), {"ttl": 3600}
        )
        return result
