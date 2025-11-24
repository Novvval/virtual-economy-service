from typing import Dict, List
from src.interfaces.cache import Cache
from src.interfaces.uow import UnitOfWork
from src.interfaces.domain_model import DomainModel
from src.application.models.user import User
from src.application.models.product import Product
from src.application.models.inventory import Inventory


class MockCache(Cache):
    def __init__(self):
        self.data: Dict[str, str] = {}

    async def get(self, key: str, options: dict = None) -> str | None:
        return self.data.get(key)

    async def set(self, key: str, value: str, options: dict = None) -> None:
        self.data[key] = value

    async def delete(self, key: str, options: dict = None) -> None:
        self.data.pop(key, None)

    async def iter(self, pattern: str, options: dict = None):
        for key in self.data:
            if pattern in key:
                yield key


class MockUnitOfWork(UnitOfWork):
    def __init__(self, cache: Cache):
        super().__init__(cache)
        self.committed = False
        self.rolled_back = False
        self.persisted_objects: List[DomainModel] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True

    async def persist(self, objs: list[DomainModel]):
        self.persisted_objects.extend(objs)

    async def delete(self, objs: list[DomainModel]): pass

    async def _create_savepoint(self): pass

    async def _release_savepoint(self): pass

    async def _rollback_to_savepoint(self): pass


class MockUserRepository:
    def __init__(self):
        self.users = {}

    async def find_user(self, user_id: int) -> User:
        return self.users.get(user_id)

    def add_user(self, user: User):
        self.users[user.id] = user


class MockInventoryRepository:
    def __init__(self):
        self.inventories = {}
        self.products = {}

    async def find_inventory(self, product_id: int, user_id: int) -> Inventory:
        return self.inventories.get((user_id, product_id))

    async def find_product(self, product_id: int) -> Product:
        return self.products.get(product_id)

    async def list(self, user_id: int) -> list[Inventory]:
        return [inv for (uid, _), inv in self.inventories.items() if uid == user_id]

    def add_inventory(self, inventory: Inventory):
        self.inventories[(inventory.user.id, inventory.product.id)] = inventory

    def add_product(self, product: Product):
        self.products[product.id] = product


class MockContext:
    def __init__(self):
        self.cache = MockCache()
        self.uow = MockUnitOfWork(self.cache)
        self.user_repo = MockUserRepository()
        self.inventory_repo = MockInventoryRepository()
        self.maximum_allowed = 10000