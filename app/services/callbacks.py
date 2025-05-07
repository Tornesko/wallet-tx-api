import asyncio
import json
from datetime import datetime
from decimal import Decimal

import httpx
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.transaction import Transaction, Wallet
from app.schemas.transaction import TransactionRead, WalletDetail


def default_serializer(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()


async def send_callback(wallet: WalletDetail, db: AsyncSession) -> bool:
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
    json_payload = json.dumps(payload, default=default_serializer)

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(str(wallet.callback_url), json=json_payload)
        return response.status_code == 200


async def retry_callback(wallet_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Wallet).options(selectinload(Wallet.transactions)).where(Wallet.id == wallet_id)
        )
        wallet = result.scalar_one_or_none()
        if wallet:
            wallet_data = WalletDetail.model_validate(wallet)
            success = await send_callback(wallet_data, db)
            if not success:
                print("Callback failed")


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=180, max_retries=3)
def task_retry_callback(self, wallet_id: int):
    asyncio.run(retry_callback(wallet_id))
