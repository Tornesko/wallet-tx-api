from sqlalchemy.orm import selectinload

from app.models.wallet import Wallet, WalletStatus
from app.schemas.wallet import WalletCreate
from app.models.transaction import Transaction
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import Optional


async def create_wallet(data: WalletCreate, db: AsyncSession) -> Wallet:
    generated_address = uuid.uuid4().hex

    wallet = Wallet(
        address=generated_address,
        currency=data.currency,
        network=data.network,
        status=WalletStatus.NEW,
        callback_url=str(data.callback_url) if data.callback_url else None,
    )

    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)

    return wallet


async def get_wallet_with_transactions(wallet_id: int, db: AsyncSession):
    result = await db.execute(
        select(Wallet)
        .options(selectinload(Wallet.transactions))
        .where(Wallet.id == wallet_id)
    )
    return result.scalar_one_or_none()
