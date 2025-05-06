import asyncio
import httpx
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.schemas.wallet import WalletDetail
from app.schemas.transaction import TransactionRead


async def send_callback(wallet: WalletDetail, db: AsyncSession) -> bool:
    print("SEEEEEND", wallet.callback_ur)
    if not wallet.callback_url:
        return True

    result = await db.execute(
        select(Transaction)
        .where(Transaction.wallet_id == wallet.id)
        .order_by(Transaction.created_at)
    )
    transactions = result.scalars().all()

    transaction_data = [
        TransactionRead.model_validate(tx).model_dump()
        for tx in transactions
    ]

    payload = {
        "id": wallet.id,
        "address": wallet.address,
        "currency": wallet.currency,
        "network": wallet.network,
        "status": wallet.status,
        "created_at": wallet.created_at.isoformat(),
        "transactions": transaction_data,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(wallet.callback_url, json=payload)
        return response.status_code == 200


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=180, max_retries=3)
def task_retry_callback(self, wallet_id: int):
    print("MIMIMIMIMI")
    async def run():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Wallet).options(selectinload(Wallet.transactions)).where(Wallet.id == wallet_id)
            )
            wallet = result.scalar_one_or_none()
            if wallet:
                wallet_data = WalletDetail.model_validate(wallet)
                success = await send_callback(wallet_data, db)
                if not success:
                    raise Exception("Callback failed — will retry")

    asyncio.run(run())
