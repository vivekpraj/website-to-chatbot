from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime


# -----------------------------
# BOT CREATION REQUEST
# -----------------------------
class BotCreateRequest(BaseModel):
    website_url: HttpUrl


# -----------------------------
# BOT CREATION RESPONSE
# -----------------------------
class BotCreateResponse(BaseModel):
    bot_id: str
    chat_url: str
    status: str


# -----------------------------
# CHAT REQUEST
# -----------------------------
class ChatRequest(BaseModel):
    message: str


# -----------------------------
# CHAT RESPONSE
# -----------------------------
class SourceChunk(BaseModel):
    text: str
    page_url: str | None = None

class ChatResponse(BaseModel):
    answer: str
    source_chunks: list[SourceChunk]


# -----------------------------
# USER SCHEMAS
# -----------------------------
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str   # plain password from client


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True  # for SQLAlchemy integration (Pydantic v2)


# -----------------------------
# TOKEN SCHEMAS
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None