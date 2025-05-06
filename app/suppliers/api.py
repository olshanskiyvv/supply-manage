from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.auth.models import User, Role
from app.suppliers.dao import SuppliersDAO
from app.suppliers.schemas import SSupplier, SSupplierRB, SSupplierFilters, SSupplierAdmin
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
                          current_user: User = Depends(get_current_admin_user)) -> SMessageResponse:
    count = await SuppliersDAO.delete(id=supplier_id)
    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Supplier with {supplier_id=} not found",
        )
    return SMessageResponse(
        message=f"Supplier with {supplier_id=} has been deleted",
    )