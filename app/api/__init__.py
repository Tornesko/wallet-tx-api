from fastapi import APIRouter
from app.api.routes import wallets, transactions, callbacks

router = APIRouter()
router.include_router(wallets.router, tags=["wallets"])
router.include_router(transactions.router, tags=["transactions"])
router.include_router(callbacks.router, tags=["callbacks"])
