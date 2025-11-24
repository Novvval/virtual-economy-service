from src.interfaces.repository import Repository


class ProductRepository(Repository):
    async def find_popular_products(self, start_date, limit=5):
        query = self.db.queries["find_popular_products_by_purchases"]
        result = await self.db.execute(query, {"start_date": start_date, "limit": limit})
        return result
