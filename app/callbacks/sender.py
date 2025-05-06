import httpx
from app.models.wallet import Wallet
from app.models.transaction import Transaction


async def send_callback(wallet: Wallet, tx: Transaction):
    if not wallet.callback_url:
        return False

    payload = {
        "status": wallet.status.value,
        "txHash": tx.tx_hash,
        "amount": float(tx.amount),
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(wallet.callback_url, json=payload, timeout=5)
            resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Callback failed for wallet {wallet.id}: {e}")
        return False
