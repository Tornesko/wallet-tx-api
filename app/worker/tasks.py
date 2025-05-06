from celery import shared_task
from app.db.session import AsyncSessionLocal
from app.services.transaction import check_confirmations, fail_stale_wallets
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.callbacks.sender import send_callback

import asyncio
import nest_asyncio
nest_asyncio.apply()


@shared_task
def task_check_confirmations():
    print("task_check_confirmations started")

    async def run():
        async with AsyncSessionLocal() as db:
            await check_confirmations(db)

    asyncio.run(run())


@shared_task
def task_fail_stale():
    async def run():
        async with AsyncSessionLocal() as db:
            await fail_stale_wallets(db)

    asyncio.run(run())


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def task_retry_callback(self, wallet_id: int, tx_id: int):
    async def run():
        async with AsyncSessionLocal() as db:
            wallet = await db.get(Wallet, wallet_id)
            tx = await db.get(Transaction, tx_id)
            if wallet and tx:
                await send_callback(wallet, tx)

    asyncio.run(run())
