from src.interfaces.repository import Repository
from ..models.user import User


class UserRepository(Repository):
    async def find_user(self, user_id: int) -> User:
        query = self.db.queries["find_user_by_id"]
        return await self.db.find_one(query, {"user_id": user_id})
