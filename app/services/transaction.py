from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionStatus
from app.models.wallet import Wallet, WalletStatus
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
    """mock confirmations"""
    wallets_result = await db.execute(
        select(Wallet).where(Wallet.status == WalletStatus.PENDING)
    )
    wallets = wallets_result.scalars().all()

    for wallet in wallets:
        tx_result = await db.execute(
            select(Transaction)
            .where(Transaction.wallet_id == wallet.id)
            .order_by(Transaction.created_at)
        )
        transactions = tx_result.scalars().all()

        if not transactions:
            continue

        first_tx = transactions[0]

        first_tx.confirmations = min(first_tx.confirmations + 1, required)

        if first_tx.confirmations >= required:
            first_tx.status = TransactionStatus.PROCESSED
            wallet.status = WalletStatus.PROCESSED

            if wallet.callback_url:
                task_retry_callback.delay(wallet.id)

        for tx in transactions[1:]:
            tx.confirmations = min(tx.confirmations + 1, required)
            if tx.status != TransactionStatus.PROCESSED:
                tx.status = TransactionStatus.NEW

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
