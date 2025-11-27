from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    anonymous_handle: str

class User(UserBase):
    id: int
    anonymous_handle: str
    verified: bool
    real_name: Optional[str] = None
    xp: int = 0
    level: int = 1
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
