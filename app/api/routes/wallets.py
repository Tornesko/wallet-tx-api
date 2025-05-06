from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletRead, WalletDetail
from app.services.transaction import on_new_chain_tx
from app.services.wallet import create_wallet, get_wallet_with_transactions
from app.db.session import AsyncSessionLocal, get_db
from fastapi import HTTPException

router = APIRouter()


@router.post("/wallets", response_model=WalletRead, status_code=201)
async def create_wallet_view(wallet: WalletCreate, db: AsyncSession = Depends(get_db)):
    return await create_wallet(wallet, db)


@router.get("/wallets/{wallet_id}", response_model=WalletDetail)
async def read_wallet(wallet_id: int, db: AsyncSession = Depends(get_db)):
    wallet = await get_wallet_with_transactions(wallet_id, db)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet
