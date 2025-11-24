from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.interfaces.db_adapter import DbAdapter, Query
from ..utils.helpers import cast_dict_types


class SqlAlchemyDbAdapter(DbAdapter):
    def __init__(self, queries: dict, session: AsyncSession, *args, **kwargs):
        super().__init__(queries, *args, **kwargs)
        self.session = session

    async def find_one(self, query: Query, *args, **kwargs):
        result = await self.session.execute(query.value, *args, **kwargs)
        return result.unique().scalars().one_or_none()

    async def find_many(self, query: Query, *args, **kwargs):
        result = await self.session.execute(query.value, *args, **kwargs)
        return result.unique().scalars().all()

    async def execute(self, query: Query, *args, **kwargs):
        result = await self.session.execute(query.value, *args, **kwargs)
        rows = result.fetchall()
        return cast_dict_types([row._asdict() for row in rows])


async def sqlalchemy_session_factory(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
