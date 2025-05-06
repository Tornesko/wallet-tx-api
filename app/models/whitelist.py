from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base


class Whitelist(Base):
    __tablename__ = "whitelist"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False, unique=True)
    currency = Column(String, nullable=False)
    network = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("address", "currency", "network", name="uniq_address_currency_network"),
    )
