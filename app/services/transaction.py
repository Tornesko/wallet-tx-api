from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionStatus
from app.models.wallet import Wallet, WalletStatus
from app.services.get_confirmation import get_confirmations
from app.services.callbacks import task_retry_callback


async def on_new_chain_tx(wallet: Wallet, tx_hash: str, amount: float, db: AsyncSession):
    tx = Transaction(
        wallet_id=wallet.id,
        tx_hash=tx_hash,
        amount=amount,
        confirmations=0,
        status=TransactionStatus.PENDING
    )
    db.add(tx)

    wallet.status = WalletStatus.PENDING
    await db.commit()
    await db.refresh(tx)
    await db.refresh(wallet)
    return tx


async def check_confirmations(db: AsyncSession, required: int = 10):
    result = await db.execute(
        select(Transaction).where(Transaction.status == TransactionStatus.PENDING)
    )
    transactions = result.scalars().all()

    for tx in transactions:
        current = await get_confirmations(tx.tx_hash)
        if current >= required:
            tx.status = TransactionStatus.PROCESSED
            wallet = await db.get(Wallet, tx.wallet_id)
            wallet.status = WalletStatus.PROCESSED
            if wallet.callback_url:
                task_retry_callback.delay(wallet.id)
        else:
            tx.confirmations = current

    await db.commit()


async def fail_stale_wallets(db: AsyncSession, timeout_hours: int = 72):
    cutoff = datetime.utcnow() - timedelta(hours=timeout_hours)
    result = await db.execute(
        select(Wallet).where(
            Wallet.status == WalletStatus.NEW,
            Wallet.created_at < cutoff
        )
    )
    for w in result.scalars().all():
        w.status = WalletStatus.FAIL
    await db.commit()
