from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.auth.models import User
from app.products.dao import ProductDAO
from app.products.schemas import SProduct, SProductRB, SProductFilters
from app.schemas import SMessageResponse

router = APIRouter(prefix='/products', tags=['Products'])

@router.get("/")
async def all_products(filters: SProductFilters = Depends(),
                       _: User = Depends(get_current_user)) -> list[SProduct]:
    products = await ProductDAO.find_all_by_filters(filters)
    return [
        SProduct.model_validate(prod, from_attributes=True)
        for prod in products
    ]

@router.post("/")
async def create_product(product: SProductRB,
                         _: User = Depends(get_current_admin_user)) -> SProduct:
    product_dict = product.model_dump()
    new_product = await ProductDAO.add(**product_dict)
    return SProduct.model_validate(new_product, from_attributes=True)

@router.delete("/{product_id}")
async def delete_product(product_id: int,
                         _: User = Depends(get_current_admin_user)) -> SMessageResponse:
    count = await ProductDAO.delete(id=product_id)
    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {product_id=} not found"
        )
    return SMessageResponse(
        message=f'Product with {product_id=} has been deleted',
    )

@router.put("/{product_id}")
async def update_product(product_id: int,
                         product: SProductRB,
                         _: User = Depends(get_current_admin_user)) -> SProduct:
    count = await ProductDAO.update(
        filter_by={'id': product_id},
        **product.model_dump(),
    )
    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Product with {product_id=} not found",
        )
    new_product = await ProductDAO.find_one_or_none_by_id(product_id)
    return SProduct.model_validate(new_product, from_attributes=True)




