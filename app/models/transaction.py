from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.schemas.transaction import TransactionStatus, WalletStatus


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
