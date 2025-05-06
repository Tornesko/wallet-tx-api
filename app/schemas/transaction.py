from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TransactionStatus(str, Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAIL = "FAIL"


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

