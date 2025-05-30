import secrets
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    receipts = relationship("Receipt", back_populates="user")


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    payment_type = Column(String, nullable=False)
    payment_amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    rest = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="receipts")
    items = relationship(
        "ReceiptItem", back_populates="receipt", lazy="selectin"
    )

    public_token = Column(
        String, unique=True, default=lambda: secrets.token_urlsafe(16)
    )


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    receipt = relationship("Receipt", back_populates="items")
