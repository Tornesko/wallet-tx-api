import random


# MOCKED
async def get_confirmations_from_node(tx_hash: str) -> int:
    return random.randint(7, 13)
