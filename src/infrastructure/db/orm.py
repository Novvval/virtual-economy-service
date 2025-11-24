from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Index, text, \
    UniqueConstraint
from sqlalchemy.orm import registry, relationship

from src.application.models.user import User
from src.application.models.product import Product
from src.application.models.inventory import Inventory
from src.application.models.transaction import Transaction

mapper_registry = registry()
metadata = mapper_registry.metadata

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), nullable=False),
    Column("email", String(100), nullable=False),
    Column("balance", Integer, nullable=False, default=0),
    Column("created_at", DateTime, nullable=True),
)

product_table = Table(
    "product",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("description", String(500), nullable=False),
    Column("price", Integer, nullable=False),
    Column("type", Enum(Product.Type), nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False),
)

inventory_table = Table(
    "inventory",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("product_id", Integer, ForeignKey("product.id"), nullable=False),
    Column("quantity", Integer, nullable=True, default=1),
    Column("purchased_at", DateTime, nullable=False),
    UniqueConstraint("user_id", "product_id", name="unique_user_product")
)

transaction_table = Table(
    "transaction",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("product_id", Integer, ForeignKey("product.id"), nullable=False),
    Column("amount", Integer, nullable=False),
    Column("status", Enum(Transaction.Status), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Index(
        "transaction_status_created_at_idx",
        "status", "created_at",
        postgresql_where=text("status = 'COMPLETED'"),
    )
)

_mappers_initialized = False


def init_mappers():
    global _mappers_initialized
    if _mappers_initialized:
        return

    mapper_registry.map_imperatively(User, user_table)
    mapper_registry.map_imperatively(Product, product_table)
    mapper_registry.map_imperatively(
        Inventory, inventory_table, properties={"user": relationship(User), "product": relationship(Product)}
    )
    mapper_registry.map_imperatively(Transaction, transaction_table)
    _mappers_initialized = True


async def create_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)
