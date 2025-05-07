from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.whitelist import initiate_withdrawal, get_whitelist_entry, list_whitelist_entries

router = APIRouter(prefix="/whitelist", tags=["whitelist"])


@router.post("/withdraw/{wallet_id}")
async def withdraw_via_whitelist(wallet_id: int, db: AsyncSession = Depends(get_db)):
    return await initiate_withdrawal(wallet_id, db)


@router.get("/{currency}/{network}")
async def get_entry(currency: str, network: str, db: AsyncSession = Depends(get_db)):
    return await get_whitelist_entry(currency, network, db)


@router.get("/")
async def list_entries(db: AsyncSession = Depends(get_db)):
    return await list_whitelist_entries(db)
