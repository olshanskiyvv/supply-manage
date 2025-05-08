from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.auth.models import User, Role
from app.suppliers.dao import SuppliersDAO
from app.suppliers.schemas import (
    SSupplier,
    SSupplierRB,
    SSupplierFilters,
    SSupplierAdmin,
    SFullSupplier,
    SSupplierProductRB
)
from app.schemas import SMessageResponse
from app.suppliers.service import (
    supplier_to_full_schema,
    add_products_to_supplier,
    delete_products_from_supplier,
    update_supplier_data,
    create_new_supplier
)

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
    new_supplier = await create_new_supplier(current_admin.id, supplier)
    return new_supplier


@router.put('/{supplier_id}/')
async def update_supplier(supplier_id: int,
                          supplier: SSupplierRB,
                          current_admin: User = Depends(get_current_admin_user)) -> SSupplierAdmin:
    old_supplier = SuppliersDAO.find_one_or_none_by_id(supplier_id)
    if old_supplier is None:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found"
        )

    new_supplier = await update_supplier_data(current_admin.id, supplier_id, supplier)
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


@router.get('/{supplier_id}/')
async def get_supplier_by_id(supplier_id: int,
                             _: User = Depends(get_current_user)) -> SFullSupplier:
    supplier = await SuppliersDAO.find_full_by_id(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found",
        )
    return supplier_to_full_schema(supplier)


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
    updated_supplier = await add_products_to_supplier(supplier, products)
    return updated_supplier


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

    updated_supplier = await delete_products_from_supplier(supplier_id, products)
    return updated_supplier
