from fastapi import APIRouter
from app.services.callbacks import task_retry_callback

router = APIRouter(prefix="/callbacks", tags=["callbacks"])


@router.post("/retry/{wallet_id}")
async def retry_callback(wallet_id: int):
    task_retry_callback.delay(wallet_id)
    return {"detail": f"Retry callback task scheduled for wallet_id {wallet_id}"}
