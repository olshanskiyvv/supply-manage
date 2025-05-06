from fastapi import FastAPI

from app.auth.api import router as auth_router
from app.products.api import router as products_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(products_router)


