from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.transaction import Wallet
from app.schemas.transaction import IncomingTransaction, WalletCreate, WalletRead, WalletDetail
from app.services.transaction import process_wallet_transaction, get_wallet_with_transactions, create_wallet

router = APIRouter()


@router.post("/transactions", response_model=WalletRead, status_code=201)
async def create_transaction_view(wallet: WalletCreate, db: AsyncSession = Depends(get_db)):
    return await create_wallet(wallet, db)


@router.get("/transactions/{wallet_id}", response_model=WalletDetail)
async def read_transaction(wallet_id: int, db: AsyncSession = Depends(get_db), ):
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

    transaction = await process_wallet_transaction(wallet_obj, payload.tx_hash, payload.amount, db)
    if transaction is None:
        return {"detail": "Transaction already exists or ignored"}

    return {"detail": "Transaction registered", "tx_hash": transaction.tx_hash}
