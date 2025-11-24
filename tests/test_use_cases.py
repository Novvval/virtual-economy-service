from uuid import uuid4
import json

import pytest

from src.application.errors import ValidationError, NotFound
from src.application.models.inventory import Inventory
from src.application.models.product import Product
from src.application.models.user import User
from src.application.use_cases.add_funds import AddFunds
from src.application.use_cases.add_purchase import AddPurchase
from src.application.use_cases.consume_product import ConsumeProduct
from src.application.use_cases.show_inventory import ShowInventory
from .mocks import MockContext


@pytest.fixture
def mock_ctx():
    return MockContext()


@pytest.fixture
def sample_user():
    return User(id=1, username="test", email="test@test.com", balance=1000)


@pytest.fixture
def sample_product():
    return Product(
        id=1, name="Test Product", description="Test", price=100,
        type=Product.Type.CONSUMABLE, is_active=True
    )


class TestAddPurchase:
    @pytest.mark.asyncio
    async def test_purchase_new_product(self, mock_ctx, sample_user, sample_product):
        mock_ctx.user_repo.add_user(sample_user)
        mock_ctx.inventory_repo.add_product(sample_product)
        
        use_case = AddPurchase(mock_ctx)
        result = await use_case(sample_product.id, sample_user.id, str(uuid4()), 1)
        
        assert result["product_id"] == sample_product.id
        assert result["price"] == sample_product.price
        assert result["balance"] == 900

    @pytest.mark.asyncio
    async def test_purchase_existing_consumable(self, mock_ctx, sample_user, sample_product):
        mock_ctx.user_repo.add_user(sample_user)
        mock_ctx.inventory_repo.add_product(sample_product)
        
        existing_inv = Inventory(user=sample_user, product=sample_product, quantity=1)
        mock_ctx.inventory_repo.add_inventory(existing_inv)
        
        use_case = AddPurchase(mock_ctx)
        result = await use_case(sample_product.id, sample_user.id, str(uuid4()), 1)
        
        assert result["product_id"] == sample_product.id
        assert result["price"] == sample_product.price
        assert result["balance"] == 900
        assert existing_inv.quantity == 2

    @pytest.mark.asyncio
    async def test_purchase_insufficient_balance(self, mock_ctx, sample_user, sample_product):
        sample_user.balance = 50
        mock_ctx.user_repo.add_user(sample_user)
        mock_ctx.inventory_repo.add_product(sample_product)
        
        use_case = AddPurchase(mock_ctx)
        
        with pytest.raises(ValidationError, match="Insufficient balance"):
            await use_case(sample_product.id, sample_user.id, str(uuid4()), 1)


class TestAddFunds:
    @pytest.mark.asyncio
    async def test_add_funds_success(self, mock_ctx, sample_user):
        mock_ctx.user_repo.add_user(sample_user)
        
        use_case = AddFunds(mock_ctx)
        result = await use_case(sample_user.id, 500, str(uuid4()))
        
        assert result["user_id"] == sample_user.id
        assert result["previous_balance"] == 1000
        assert result["current_balance"] == 1500

    @pytest.mark.asyncio
    async def test_add_funds_idempotency(self, mock_ctx, sample_user):
        mock_ctx.user_repo.add_user(sample_user)
        await mock_ctx.cache.set("add_funds:1:test-key", "1500")
        
        use_case = AddFunds(mock_ctx)
        result = await use_case(sample_user.id, 500, str(uuid4()))
        
        assert result["user_id"] == sample_user.id
        assert result["previous_balance"] == 1000
        assert result["current_balance"] == 1500

    @pytest.mark.asyncio
    async def test_add_funds_exceeds_maximum(self, mock_ctx, sample_user):
        mock_ctx.user_repo.add_user(sample_user)
        
        use_case = AddFunds(mock_ctx)
        
        with pytest.raises(ValidationError, match="Amount exceeds maximum allowed"):
            await use_case(sample_user.id, 20000, "test-key")


class TestConsumeProduct:
    @pytest.mark.asyncio
    async def test_consume_product_success(self, mock_ctx, sample_user, sample_product):
        inventory = Inventory(user=sample_user, product=sample_product, quantity=3)
        mock_ctx.inventory_repo.add_inventory(inventory)
        
        use_case = ConsumeProduct(mock_ctx)
        result = await use_case(sample_product.id, sample_user.id, str(uuid4()))
        
        assert result["product_id"] == sample_product.id
        assert result["previous_quantity"] == 3
        assert result["current_quantity"] == 2

    @pytest.mark.asyncio
    async def test_consume_product_not_found(self, mock_ctx, sample_user, sample_product):
        use_case = ConsumeProduct(mock_ctx)
        
        with pytest.raises(NotFound, match="Inventory with product id 1 doesn't exist"):
            await use_case(sample_product.id, sample_user.id, str(uuid4()), 1)

    @pytest.mark.asyncio
    async def test_consume_product_out_of_stock(self, mock_ctx, sample_user, sample_product):
        inventory = Inventory(user=sample_user, product=sample_product, quantity=0)
        mock_ctx.inventory_repo.add_inventory(inventory)
        
        use_case = ConsumeProduct(mock_ctx)
        
        with pytest.raises(ValidationError, match="Insufficient quantity"):
            await use_case(sample_product.id, sample_user.id, str(uuid4()), 1)


class TestShowInventory:
    @pytest.mark.asyncio
    async def test_show_inventory_from_cache(self, mock_ctx, sample_user):
        cached_data = json.dumps([{"product_id": 1, "quantity": 2}])
        await mock_ctx.cache.set(f"inventory:{sample_user.id}", cached_data)
        
        use_case = ShowInventory(mock_ctx)
        await use_case(sample_user.id)
        
        cache_hit = await mock_ctx.cache.get(f"inventory:{sample_user.id}")
        assert cache_hit is not None

    @pytest.mark.asyncio
    async def test_show_inventory_from_db(self, mock_ctx, sample_user, sample_product):
        inventory = Inventory(user=sample_user, product=sample_product, quantity=1)
        mock_ctx.inventory_repo.add_inventory(inventory)
        
        use_case = ShowInventory(mock_ctx)
        result = await use_case(sample_user.id)
        
        assert len(result) == 1
        cache_value = await mock_ctx.cache.get(f"inventory:{sample_user.id}")
        assert cache_value is not None