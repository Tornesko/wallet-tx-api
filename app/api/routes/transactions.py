from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.wallet import Wallet
from app.schemas.transaction import IncomingTransaction
from app.schemas.wallet import WalletCreate, WalletRead, WalletDetail
from app.services.transaction import on_new_chain_tx
from app.services.wallet import get_wallet_with_transactions, create_wallet

router = APIRouter()


@router.post("/transactions", response_model=WalletRead, status_code=201)
async def create_transaction_view(wallet: WalletCreate, db: AsyncSession = Depends(get_db)):
    return await create_wallet(wallet, db)


@router.get("/transactions/{transaction_id}", response_model=WalletDetail)
async def read_transaction(wallet_id: int, db: AsyncSession = Depends(get_db)):
    wallet = await get_wallet_with_transactions(wallet_id, db)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.post("/register_transaction", status_code=status.HTTP_201_CREATED)
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
