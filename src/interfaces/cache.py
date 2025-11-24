from abc import ABC, abstractmethod


class Cache(ABC):
    @abstractmethod
    async def get(self, key: str, options: dict = None) -> str | None: ...

    @abstractmethod
    async def set(self, key: str, value: str, options: dict = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str, options: dict = None) -> None: ...

    @abstractmethod
    async def iter(self, pattern: str, options: dict = None): ...
