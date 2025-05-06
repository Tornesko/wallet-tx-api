from app.callbacks.sender import send_callback
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.worker.tasks import task_retry_callback


async def trigger_callback(wallet: Wallet, tx: Transaction):
    success = await send_callback(wallet, tx)
    if not success:
        task_retry_callback.delay(wallet.id, tx.id)
