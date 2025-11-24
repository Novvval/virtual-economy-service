from datetime import date

from dependency_injector.wiring import inject
from fastapi import APIRouter, Query, Request

from src.application.use_cases.show_popular_products import ShowPopularProducts
from ..depends import ReadContextDep, limiter
from ..schema.responses import PopularProductsResponse, PopularProduct

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/popular-products",
    summary="Show most frequently bought products",
    description="Show most frequently bought products. Optionally filter by start date",
    response_description="List of popular products, ordered by purchase count",
)
@limiter.limit("100/second")
@inject
async def get_popular_products(
    request: Request,
    ctx: ReadContextDep,
    limit: int = Query(default=5, description="Maximum number of products to return", ge=1, le=100),
    start_date: date = Query(default=None, description="Filter products purchased after this date"),
) -> PopularProductsResponse:
    usecase = ShowPopularProducts(ctx)
    result = await usecase(limit, start_date)
    return PopularProductsResponse(
        products=[
            PopularProduct(
                product_id=item["product_id"],
                name=item["name"],
                price=item["price"],
                type=item["type"],
                purchase_count=item["purchase_count"],
            )
            for item in result
        ]
    )
