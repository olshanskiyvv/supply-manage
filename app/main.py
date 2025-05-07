from fastapi import FastAPI

from app.auth.api import router as auth_router
from app.products.api import router as products_router
from app.suppliers.api import router as suppliers_router
from app.orders.api import router as orders_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(suppliers_router)
app.include_router(orders_router)


