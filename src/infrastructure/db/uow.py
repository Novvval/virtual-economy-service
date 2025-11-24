from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from src.interfaces.uow import UnitOfWork
from src.interfaces.domain_model import DomainModel
from src.interfaces.cache import Cache


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession, cache: Cache, active_test: bool = False):
        super().__init__(cache)
        self.session = session
        self._cache_operations: list[Callable] = []
        self._nested_transaction = None
        self.active_test = active_test

    async def __aenter__(self):
        if self._depth == 1:
            await self.session.__aenter__()
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        if self._depth == 0:
            if exc_type is None and not self.active_test:
                await self.session.commit()
                for operation in self._cache_operations:
                    await operation()
            else:
                await self.session.rollback()

            self._cache_operations.clear()
            await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        await self.session.commit()
        for operation in self._cache_operations:
            await operation()
        self._cache_operations.clear()

    async def rollback(self):
        await self.session.rollback()
        self._cache_operations.clear()

    async def persist(self, objs: list[DomainModel]):
        self.session.add_all(objs)

    async def delete(self, objs: list[DomainModel]):
        for obj in objs:
            await self.session.delete(obj)

    def cache_set(self, key: str, value: str, options: dict = None):
        self._cache_operations.append(lambda: self.cache.set(key, value, options))

    def cache_delete(self, key: str, options: dict = None):
        self._cache_operations.append(lambda: self.cache.delete(key, options))

    async def _create_savepoint(self):
        self._nested_transaction = await self.session.begin_nested()

    async def _release_savepoint(self):
        if self._nested_transaction:
            await self._nested_transaction.commit()
            self._nested_transaction = None

    async def _rollback_to_savepoint(self):
        if self._nested_transaction:
            await self._nested_transaction.rollback()
            self._nested_transaction = None
