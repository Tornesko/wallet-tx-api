from sqlalchemy import Column, String, Integer, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class WalletStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAIL = "FAIL"


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, nullable=False)
    currency = Column(String, nullable=False)
    network = Column(String, nullable=False)
    status = Column(Enum(WalletStatus), default=WalletStatus.NEW, nullable=False)
    callback_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    transactions = relationship(
        "Transaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
        lazy="raise"
    )
