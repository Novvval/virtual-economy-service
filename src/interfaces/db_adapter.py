from abc import ABC, abstractmethod


class Query:
    def __init__(self, query):
        self.value = query


class DbAdapter(ABC):
    def __init__(self, queries, *args, **kwargs):
        self.queries = queries

    @abstractmethod
    async def find_one(self, query: Query, *args, **kwargs): ...

    @abstractmethod
    async def find_many(self, query: Query, *args, **kwargs): ...

    @abstractmethod
    async def execute(self, query: Query, *args, **kwargs): ...
