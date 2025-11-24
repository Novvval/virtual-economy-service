from dependency_injector.wiring import inject
from fastapi import APIRouter, Request

from src.application.errors import AccessError
from src.application.use_cases.add_funds import AddFunds
from src.application.use_cases.show_inventory import ShowInventory
from ..depends import AuthenticatedUserDep, limiter, IdempotentRequestDep, WriteContextDep, ReadContextDep
from ..schema.requests import AddFundsRequest
from ..schema.responses import InventoryResponse, FundsAddedResponse, InventoryItem

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/{user_id}/add-funds",
    summary="Add funds",
    description="Add funds to user's balance",
    response_description="User's balance after adding funds",
)
@limiter.limit("5/minute")
@inject
async def add_funds(
    request: Request, user_id: int, body: AddFundsRequest, ctx: WriteContextDep, idempotency_dep: IdempotentRequestDep
) -> FundsAddedResponse:
    if user_id != idempotency_dep["user_id"]:
        raise AccessError
    usecase = AddFunds(ctx)
    result = await usecase(idempotency_dep["user_id"], body.amount, idempotency_dep["idempotency_hash"])
    return FundsAddedResponse(**result)


@router.get(
    "/{user_id}/inventory",
    summary="Show inventory",
    description="Show user's product inventory",
    response_description="List of products in user's inventory",
)
@limiter.limit("100/second")
@inject
async def get_inventory(
    request: Request,
    user_id: int,
    user_dep: AuthenticatedUserDep,
    ctx: ReadContextDep,
) -> InventoryResponse:
    if user_id != user_dep:
        raise AccessError
    usecase = ShowInventory(ctx)
    result = await usecase(user_dep)
    inventory_items = [
        InventoryItem(
            name=item["product"]["name"],
            type=item["product"]["type"],
            price=item["product"]["price"],
            quantity=item["quantity"],
            purchased_at=item["purchased_at"],
        )
        for item in result
    ]

    return InventoryResponse(products=inventory_items)
