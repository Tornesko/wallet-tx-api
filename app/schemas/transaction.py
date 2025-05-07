import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, HttpUrl


# === ENUMS ===
class StatusEnum(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAIL = "FAIL"


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Transactions
class IncomingTransaction(BaseModel):
    wallet_address: str
    tx_hash: str
    amount: Decimal


class TransactionRead(ORMBaseModel):
    tx_hash: str
    amount: Decimal
    confirmations: int
    status: StatusEnum
    created_at: datetime


# Wallets
class WalletCreate(BaseModel):
    currency: str
    network: str
    callback_url: Optional[HttpUrl] = None


class WalletRead(ORMBaseModel):
    id: int
    address: str
    currency: str
    network: str
    status: StatusEnum
    created_at: datetime
    callback_url: Optional[HttpUrl] = None


class WalletDetail(WalletRead):
    transactions: List[TransactionRead]
