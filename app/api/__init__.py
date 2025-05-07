from fastapi import APIRouter
from app.api.routes import transactions, callbacks, whitelist

router = APIRouter()
router.include_router(transactions.router, tags=["transactions"])
router.include_router(callbacks.router, tags=["callbacks"])
router.include_router(whitelist.router, tags=["whitelist"])
