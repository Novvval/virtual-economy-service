from sqlalchemy import select, bindparam, func, desc
from sqlalchemy.orm import joinedload
from .orm import init_mappers
from ...application.models.user import User

_queries = None


def get_queries():
    global _queries
    if _queries is None:
        init_mappers()

        from src.application.models.inventory import Inventory
        from src.application.models.product import Product
        from src.application.models.transaction import Transaction
        from src.interfaces.db_adapter import Query

        _queries = {
            "find_inventory": Query(
                select(Inventory)
                .join(Product)
                .where(
                    Inventory.user_id == bindparam("user_id"),
                    Inventory.product_id == bindparam("product_id"),
                    Product.is_active == True,  # noqa: E712
                )
                .options(joinedload(Inventory.product), joinedload(Inventory.user))
            ),
            "find_inventories_by_user": Query(
                select(Inventory)
                .where(Inventory.user_id == bindparam("user_id"))
                .options(joinedload(Inventory.product), joinedload(Inventory.user))
                .order_by(Inventory.quantity.desc())
            ),
            "find_user_by_id": Query(select(User).where(User.id == bindparam("user_id"))),
            "find_product_by_id": Query(select(Product).where(Product.id == bindparam("product_id"))),
            "find_popular_products_by_purchases": Query(
                select(
                    Product.id.label("product_id"),
                    Product.name,
                    Product.price,
                    Product.type,
                    func.sum(Transaction.amount).label("purchase_count"),
                )
                .join(Transaction, Product.id == Transaction.product_id)
                .where(
                    Transaction.status == Transaction.Status.COMPLETED,
                    Transaction.created_at >= bindparam("start_date"),
                )
                .group_by(Product.id, Product.name, Product.price, Product.type)
                .order_by(desc("purchase_count"))
                .limit(bindparam("limit"))
            ),
        }
    return _queries


queries = get_queries()
