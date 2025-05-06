from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

from app.models.transaction import TransactionStatus


class TransactionRead(BaseModel):
    tx_hash: str
    amount: Decimal
    confirmations: int
    status: TransactionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncomingTransaction(BaseModel):
    wallet_address: str
    tx_hash: str
    amount: float
