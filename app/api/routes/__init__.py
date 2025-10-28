"""Exports API routers for easy inclusion in the application."""
from fastapi import APIRouter

from app.api.routes import auth, categories, orders, products, stocks, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(stocks.router)
api_router.include_router(orders.router)

__all__ = ["api_router"]
