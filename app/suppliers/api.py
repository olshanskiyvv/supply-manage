from itertools import product

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.auth.models import User, Role
from app.suppliers.dao import SuppliersDAO, SupplierProductDAO
from app.suppliers.models import Supplier
from app.suppliers.schemas import (
    SSupplier,
    SSupplierRB,
    SSupplierFilters,
    SSupplierAdmin,
    SFullSupplier,
    SProductShort, SSupplierProductRB
)
from app.schemas import SMessageResponse

router = APIRouter(prefix='/suppliers', tags=['Suppliers'])


@router.get('/')
async def all_suppliers(filters: SSupplierFilters = Depends(),
                        current_user: User = Depends(get_current_user)) -> list[SSupplier | SSupplierAdmin]:
    suppliers = await SuppliersDAO.find_all_by_filters(filters)
    if current_user.role == Role.ADMIN:
        return [
            SSupplierAdmin.model_validate(sup, from_attributes=True)
            for sup in suppliers
        ]
    return [
        SSupplier.model_validate(sup, from_attributes=True)
        for sup in suppliers
    ]


@router.post('/')
async def create_supplier(supplier: SSupplierRB,
                          current_admin: User = Depends(get_current_admin_user)) -> SSupplierAdmin:
    supplier_dict = supplier.model_dump()
    supplier_dict['admin_id'] = current_admin.id
    supplier_dict['topic_name_base'] = slugify(supplier.title)
    new_supplier = await SuppliersDAO.add(**supplier_dict)
    return new_supplier


@router.put('/{supplier_id}/')
async def update_supplier(supplier_id: int,
                          supplier: SSupplierRB,
                          current_admin: User = Depends(get_current_admin_user)) -> SSupplierAdmin:
    supplier_dict = supplier.model_dump()
    supplier_dict['admin_id'] = current_admin.id
    count = await SuppliersDAO.update(
        filter_by={'id': supplier_id},
        **supplier_dict
    )
    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found",
        )
    new_supplier = await SuppliersDAO.find_one_or_none_by_id(supplier_id)
    return new_supplier


@router.delete('/{supplier_id}/')
async def delete_supplier(supplier_id: int,
                          _: User = Depends(get_current_admin_user)) -> SMessageResponse:
    count = await SuppliersDAO.delete(id=supplier_id)
    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found",
        )
    return SMessageResponse(
        message=f"Supplier with {supplier_id=} has been deleted",
    )


def _supplier_to_full_schema(supplier: Supplier) -> SFullSupplier:
    return SFullSupplier(
        id=supplier.id,
        title=supplier.title,
        ogrn=supplier.ogrn,
        products=[
            SProductShort(
                product_id=prod.product_id,
                title=prod.product.title,
                product_code=prod.supplier_product_id,
                price=prod.price,
            )
            for prod in supplier.products
        ]
    )


@router.get('/{supplier_id}/')
async def get_supplier_by_id(supplier_id: int,
                             _: User = Depends(get_current_user)) -> SFullSupplier:
    supplier = await SuppliersDAO.find_full_by_id(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found",
        )
    return _supplier_to_full_schema(supplier)


@router.post('/{supplier_id}/products/')
async def add_supplied_products(supplier_id: int,
                                products: list[SSupplierProductRB],
                                _: User = Depends(get_current_admin_user)) -> SFullSupplier:
    supplier = await SuppliersDAO.find_one_or_none_by_id(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found",
        )
    new_products = [
        {
            'product_id': product.product_id,
            'supplier_id': supplier_id,
            'supplier_product_id': product.supplier_product_code,
            'price': product.current_price,
        }
        for product in products
    ]
    await SupplierProductDAO.add_all(*new_products)
    supplier = await SuppliersDAO.find_full_by_id(supplier_id)
    return _supplier_to_full_schema(supplier)


@router.delete('/{supplier_id}/products/')
async def delete_supplied_products(supplier_id: int,
                                   products: list[int],
                                   _: User = Depends(get_current_admin_user)) -> SFullSupplier:
    supplier = await SuppliersDAO.find_one_or_none_by_id(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found",
        )
    if len(products) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"List of products to delete is empty",
        )
    await SupplierProductDAO.delete_by_supplier_id_and_product_ids(supplier_id, products)
    supplier = await SuppliersDAO.find_full_by_id(supplier_id)
    return _supplier_to_full_schema(supplier)
