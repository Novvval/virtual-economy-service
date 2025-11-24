from dataclasses import dataclass

from src.application.repositories.inventory import InventoryRepository
from src.application.repositories.product import ProductRepository
from src.application.repositories.user import UserRepository
from src.interfaces.cache import Cache
from src.interfaces.db_adapter import DbAdapter
from src.interfaces.uow import UnitOfWork


@dataclass
class WriteContext:
    db: DbAdapter
    uow: UnitOfWork
    cache: Cache
    inventory_repo: InventoryRepository
    user_repo: UserRepository
    maximum_allowed: int


@dataclass
class ReadContext:
    db: DbAdapter
    cache: Cache
    product_repo: ProductRepository
    inventory_repo: InventoryRepository
