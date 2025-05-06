import random


# MOCKED
async def get_confirmations(tx_hash: str) -> int:
    return random.randint(7, 13)
