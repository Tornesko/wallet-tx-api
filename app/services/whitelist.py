from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.models.transaction import Wallet, Transaction
from app.models.whitelist import Whitelist
from app.schemas.transaction import WalletStatus


async def initiate_withdrawal(wallet_id: int, db: AsyncSession) -> dict:
    wallet = await db.get(Wallet, wallet_id)
    if not wallet or wallet.status != WalletStatus.PROCESSED:
        raise HTTPException(status_code=400, detail="Wallet not eligible for withdrawal")

    result = await db.execute(
        select(Whitelist).where(
            Whitelist.currency == wallet.currency,
            Whitelist.network == wallet.network
        )
    )
    whitelist = result.scalar_one_or_none()
    if not whitelist:
        raise HTTPException(status_code=400, detail="No whitelisted address found")

    result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.wallet_id == wallet.id)
    )
    total = result.scalar() or 0

    print(f"Withdrawing {total} {wallet.currency} from {wallet.address} to {whitelist.address}")

    return {
        "detail": "Withdrawal initiated",
        "to": whitelist.address,
        "amount": total
    }


async def get_whitelist_entry(currency: str, network: str, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Whitelist).where(
            Whitelist.currency == currency,
            Whitelist.network == network
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Whitelist entry not found")

    return {
        "currency": entry.currency,
        "network": entry.network,
        "address": entry.address
    }


async def list_whitelist_entries(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(Whitelist))
    entries = result.scalars().all()

    return [
        {
            "currency": entry.currency,
            "network": entry.network,
            "address": entry.address
        }
        for entry in entries
    ]
