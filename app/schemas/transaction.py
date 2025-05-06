from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal






class TransactionRead(BaseModel):
    tx_hash: str
    amount: Decimal
    confirmations: int
    status: TransactionStatus
    created_at: datetime

    class Config:
        orm_mode = True


class IncomingTransaction(BaseModel):
    wallet_address: str
    tx_hash: str
    amount: float
