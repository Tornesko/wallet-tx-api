from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class TransactionStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAIL = "FAIL"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)
    tx_hash = Column(String, nullable=False)
    amount = Column(Numeric(precision=20, scale=8), nullable=False)
    confirmed = Column(Boolean, default=False)
    confirmations = Column(Integer, default=0)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.NEW, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    wallet = relationship("Wallet", back_populates="transactions")
