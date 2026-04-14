"""FastAPI route registration."""

from fastapi import APIRouter

from app.routes.accounts import router as accounts_router
from app.routes.qbr import router as qbr_router

api_router = APIRouter(prefix="/api")
api_router.include_router(accounts_router)
api_router.include_router(qbr_router)

__all__ = ["api_router"]
