from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum
from typing import List
from transaction import TransactionRead


class WalletCreate(BaseModel):
    currency: str
    network: str
    callback_url: Optional[HttpUrl] = None


class WalletStatus(str, Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAIL = "FAIL"


class WalletRead(BaseModel):
    id: int
    address: str
    currency: str
    network: str
    status: WalletStatus
    created_at: datetime

    class Config:
        orm_mode = True


class WalletDetail(WalletRead):
    transactions: List[TransactionRead]
