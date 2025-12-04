from pydantic import BaseModel, HttpUrl
from typing import Optional, List


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
