from datetime import datetime
from typing import List
from enum import Enum

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductInput(BaseModel):
    name: str
    price: float
    quantity: float


class PaymentType(str, Enum):
    cashless = "cashless"
    cash = "cash"


class PaymentInput(BaseModel):
    type: PaymentType
    amount: float


class ReceiptCreate(BaseModel):
    products: List[ProductInput]
    payment: PaymentInput


class ProductOutput(ProductInput):
    total: float


class PaymentOutput(PaymentInput):
    pass


class ReceiptOutput(BaseModel):
    id: int
    products: List[ProductOutput]
    payment: PaymentOutput
    total: float
    rest: float
    created_at: datetime
