from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode = True

class ContentCreate(BaseModel):
    text: str

class ContentResponse(BaseModel):
    id: int
    text: str
    summary: Optional[str]
    sentiment: Optional[str]
    class Config:
        orm_mode = True

class ContentResponse(BaseModel):
    id: int
    text: str
    class Config:
        orm_mode = True