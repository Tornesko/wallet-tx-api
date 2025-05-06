import enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, HttpUrl
from datetime import datetime
from decimal import Decimal


class TransactionStatus(str, enum.Enum):
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

    model_config = ConfigDict(from_attributes=True)


class IncomingTransaction(BaseModel):
    wallet_address: str
    tx_hash: str
    amount: float


class WalletStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAIL = "FAIL"


class WalletCreate(BaseModel):
    currency: str
    network: str
    callback_url: Optional[HttpUrl] = None


class WalletRead(BaseModel):
    id: int
    address: str
    currency: str
    network: str
    status: WalletStatus
    created_at: datetime
    callback_url: Optional[HttpUrl] = None

    model_config = ConfigDict(from_attributes=True)


class WalletDetail(WalletRead):
    transactions: List[TransactionRead]
