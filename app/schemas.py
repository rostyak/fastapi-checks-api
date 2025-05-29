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
