from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine

from src.application.repositories.inventory import InventoryRepository
from src.application.repositories.product import ProductRepository
from src.application.repositories.user import UserRepository
from src.interfaces.context import WriteContext, ReadContext
from .cache import init_redis_pool, RedisCache
from .db.db_adapter import sqlalchemy_session_factory, SqlAlchemyDbAdapter
from .db.queries import get_queries
from .db.uow import SqlAlchemyUnitOfWork


@contextmanager
def init_thread_pool(max_workers: int):
    thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    yield thread_pool
    thread_pool.shutdown(wait=True)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_pool = providers.Resource(
        init_redis_pool,
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_password,
    )
    engine = providers.Resource(
        create_async_engine, config.database_url, pool_size=10, max_overflow=20, pool_pre_ping=True
    )
    session_factory = providers.Resource(sqlalchemy_session_factory, engine=engine)

    thread_pool = providers.Resource(
        init_thread_pool,
        max_workers=1,
    )

    cache = providers.Singleton(RedisCache, redis=redis_pool)

    queries = providers.Singleton(get_queries)

    db = providers.Factory(SqlAlchemyDbAdapter, session=session_factory, queries=queries)
    uow = providers.Factory(
        SqlAlchemyUnitOfWork, session=session_factory, cache=cache, active_test=config.active_test
    )

    inventory_repository = providers.Factory(InventoryRepository, db=db)
    product_repository = providers.Factory(ProductRepository, db=db)
    user_repository = providers.Factory(UserRepository, db=db)

    write_context = providers.Factory(
        WriteContext,
        db=db,
        uow=uow,
        cache=cache,
        inventory_repo=inventory_repository,
        user_repo=user_repository,
        maximum_allowed=config.max_balance_update_amount,
    )

    read_context = providers.Factory(
        ReadContext, db=db, cache=cache, product_repo=product_repository, inventory_repo=inventory_repository
    )
