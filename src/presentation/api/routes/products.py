from dependency_injector.wiring import inject
from fastapi import APIRouter, Request

from src.application.use_cases.add_purchase import AddPurchase
from src.application.use_cases.consume_product import ConsumeProduct
from ..depends import limiter, IdempotentRequestDep, WriteContextDep
from ..schema.requests import PurchaseRequest, ConsumeProductRequest
from ..schema.responses import ProductConsumedResponse, ProductPurchasedResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/{product_id}/use",
    summary="Use a consumable product",
    description="Use a consumable product for the authenticated user.",
    response_description="Details of the consumed product and updated quantity",
)
@limiter.limit("10/minute")
@inject
async def use_product(
    request: Request,
    product_id: int,
    body: ConsumeProductRequest,
    ctx: WriteContextDep,
    idempotency_dep: IdempotentRequestDep,
) -> ProductConsumedResponse:
    usecase = ConsumeProduct(ctx)
    result = await usecase(product_id, idempotency_dep["user_id"], idempotency_dep["idempotency_hash"], body.amount)
    return ProductConsumedResponse(**result)


@router.post(
    "/{product_id}/purchase",
    summary="Purchase a product",
    description="Purchase a product for the authenticated user. Requires sufficient balance.",
    response_description="Details of the purchased product and updated balance",
)
@limiter.limit("2/minute")
@inject
async def purchase_product(
    request: Request,
    product_id: int,
    body: PurchaseRequest,
    ctx: WriteContextDep,
    idempotency_dep: IdempotentRequestDep,
) -> ProductPurchasedResponse:
    usecase = AddPurchase(ctx)
    result = await usecase(product_id, idempotency_dep["user_id"], idempotency_dep["idempotency_hash"], body.amount)
    return ProductPurchasedResponse(**result)
