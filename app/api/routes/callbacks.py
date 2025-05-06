from fastapi import APIRouter
from app.services.callbacks import retry_callback

router = APIRouter(prefix="/callbacks", tags=["callbacks"])


@router.post("/retry-direct/{wallet_id}")
async def retry_callback_direct(wallet_id: int):
    await retry_callback(wallet_id)
    return {"detail": f"Callback manually triggered for wallet {wallet_id}"}
