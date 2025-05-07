from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user

from app.api.routes import transactions, callbacks, whitelist, auth, dev

router = APIRouter()

router.include_router(transactions.router, dependencies=[Depends(get_current_user)], tags=["transactions"])
router.include_router(callbacks.router, dependencies=[Depends(get_current_user)], tags=["callbacks"])
router.include_router(whitelist.router, dependencies=[Depends(get_current_user)], tags=["whitelist"])

router.include_router(auth.router, tags=["auth"])
router.include_router(dev.router, tags=["test"])
