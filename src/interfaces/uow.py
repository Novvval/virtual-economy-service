from abc import ABC, abstractmethod
from typing import Callable

from .cache import Cache
from .domain_model import DomainModel


class UnitOfWork(ABC):
    def __init__(self, cache: Cache):
        self.cache = cache
        self._cache_operations: list[Callable] = []
        self._depth = 0

    async def __aenter__(self):
        self._depth += 1
        if self._depth > 1:
            await self._create_savepoint()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.rollback()
            elif self._depth > 1:
                await self._release_savepoint()
        finally:
            self._depth -= 1

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...

    @abstractmethod
    async def persist(self, objs: list[DomainModel]): ...

    @abstractmethod
    async def delete(self, objs: list[DomainModel]): ...

    def cache_set(self, key: str, value: str, options: dict = None):
        self._cache_operations.append(lambda: self.cache.set(key, value, options))

    def cache_delete(self, key: str, options: dict = None):
        self._cache_operations.append(lambda: self.cache.delete(key, options))

    @abstractmethod
    async def _create_savepoint(self): ...

    @abstractmethod
    async def _release_savepoint(self): ...

    @abstractmethod
    async def _rollback_to_savepoint(self): ...
