from app.services.transaction import check_confirmations, fail_stale_wallets
from celery import shared_task
from app.db.session import AsyncSessionLocal

import asyncio
import nest_asyncio

nest_asyncio.apply()


@shared_task
def task_check_confirmations():
    """mock confirmations"""
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


