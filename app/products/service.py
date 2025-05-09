from app.kafka.schemas import KafkaNewProductAvailable
from app.products.dao import ProductDAO
from app.products.models import Product
from app.products.schemas import SFullProduct, SSupplierShort


def product_to_full_schema(product: Product) -> SFullProduct:
    return SFullProduct(
        id=product.id,
        title=product.title,
        description=product.description,
        available=product.available,
        unit=product.unit,
        suppliers=[
            SSupplierShort(
                title=sup.supplier.title,
                price=sup.price,
            )
            for sup in product.suppliers
        ]
    )

async def update_available_stock(new_available: KafkaNewProductAvailable) -> None:
    count = await ProductDAO.update_available_stock(
        new_available.product_id,
        new_available.available,
    )
    if count == 0:
        raise ValueError('Something went wrong with updating available stock', new_available.model_dump())
