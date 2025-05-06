from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.wallet import Wallet
from app.schemas.transaction import IncomingTransaction
from app.services.transaction import on_new_chain_tx

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_transaction(
        payload: IncomingTransaction,
        db: AsyncSession = Depends(get_db),
):
    wallet = await db.execute(
        select(Wallet).where(Wallet.address == payload.wallet_address)
    )
    wallet_obj = wallet.scalar_one_or_none()

    if not wallet_obj:
        raise HTTPException(status_code=404, detail="Wallet not found")

    tx = await on_new_chain_tx(wallet_obj, payload.tx_hash, payload.amount, db)
    if tx is None:
        return {"detail": "Transaction already exists or ignored"}

    return {"detail": "Transaction registered", "tx_hash": tx.tx_hash}
