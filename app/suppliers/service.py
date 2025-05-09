from slugify import slugify

from app.kafka.schemas import KafkaNewSupplierPrice
from app.suppliers.dao import SupplierProductDAO, SuppliersDAO
from app.suppliers.models import Supplier
from app.suppliers.schemas import SFullSupplier, SProductShort, SSupplierProductRB, SSupplierAdmin, SSupplierRB


def supplier_to_full_schema(supplier: Supplier) -> SFullSupplier:
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

async def create_new_supplier(admin_id: int,
                              supplier: SSupplierRB) -> SSupplierAdmin:
    supplier_dict = supplier.model_dump()
    supplier_dict['admin_id'] = admin_id
    supplier_dict['topic_name_base'] = slugify(supplier.title)
    new_supplier = await SuppliersDAO.add(**supplier_dict)
    return SSupplierAdmin.model_validate(new_supplier, from_attributes=True)


async def update_supplier_data(admin_id: int, supplier_id: int, supplier: SSupplierRB) -> SSupplierAdmin:
    supplier_dict = supplier.model_dump()
    supplier_dict['admin_id'] = admin_id
    await SuppliersDAO.update(
        filter_by={'id': supplier_id},
        **supplier_dict
    )
    new_supplier = await SuppliersDAO.find_one_or_none_by_id(supplier_id)
    return SSupplierAdmin.model_validate(new_supplier, from_attributes=True)


async def add_products_to_supplier(supplier: Supplier,
                                   products: list[SSupplierProductRB]) -> SFullSupplier:
    new_products = [
        {
            'product_id': product.product_id,
            'supplier_id': supplier.id,
            'supplier_product_id': product.supplier_product_code,
            'price': product.current_price,
        }
        for product in products
    ]
    await SupplierProductDAO.add_all(*new_products)
    supplier = await SuppliersDAO.find_full_by_id(supplier.id)
    return supplier_to_full_schema(supplier)


async def delete_products_from_supplier(supplier_id: int,
                                        products: list[int]) -> SFullSupplier:
    await SupplierProductDAO.delete_by_supplier_id_and_product_ids(supplier_id, products)
    supplier = await SuppliersDAO.find_full_by_id(supplier_id)
    return supplier_to_full_schema(supplier)


async def update_supplier_product_price(new_price: KafkaNewSupplierPrice) -> None:
    supplier = await SuppliersDAO.find_one_or_none(ogrn=new_price.ogrn)
    if supplier is None:
        raise ValueError(f'Supplier with ogrn={new_price.ogrn} not found')
    count = await SupplierProductDAO.update_price_by_supplier_id_and_product_code(
        supplier.id,
        new_price.product_code,
        new_price.price,
    )
    if count == 0:
        raise ValueError('Something went wrong while updating product price', new_price.model_dump())


