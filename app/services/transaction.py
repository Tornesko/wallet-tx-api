import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction, Wallet
from app.schemas.transaction import WalletCreate, WalletStatus, TransactionStatus
from app.services.callbacks import task_retry_callback


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


async def process_wallet_transaction(wallet: Wallet, tx_hash: str, amount: float, db: AsyncSession) -> Optional[Transaction]:
    existing_transaction_result = await db.execute(
        select(Transaction).where(Transaction.tx_hash == tx_hash)
    )
    if existing_transaction_result.scalar_one_or_none():
        return None

    transactions_result = await db.execute(
        select(Transaction)
        .where(Transaction.wallet_id == wallet.id)
        .order_by(Transaction.created_at)
    )
    existing_transactions = transactions_result.scalars().all()

    is_first_transaction = len(existing_transactions) == 0

    transaction = Transaction(
        wallet_id=wallet.id,
        tx_hash=tx_hash,
        amount=amount,
        confirmations=0,
        status=TransactionStatus.PENDING if is_first_transaction else TransactionStatus.NEW
    )
    db.add(transaction)

    if is_first_transaction and wallet.status == WalletStatus.NEW:
        wallet.status = WalletStatus.PENDING

    await db.commit()
    await db.refresh(transaction)
    return transaction


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
