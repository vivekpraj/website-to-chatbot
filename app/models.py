from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


# -----------------------------
# USER MODEL
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    hashed_password = Column(String, nullable=False)

    # Role: superadmin / client
    role = Column(String, default="client")

    # One user -> Many bots
    bots = relationship("Bot", back_populates="owner", cascade="all, delete")


# -----------------------------
# BOT MODEL
# -----------------------------
class Bot(Base):
    __tablename__ = "bots"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    bot_id = Column(String, unique=True, index=True)
    website_url = Column(String, nullable=False)

    status = Column(String, default="processing")
    vector_index_path = Column(String, nullable=True)
    
    message_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="bots")
# -----------------------------
# CHATSESSION MODEL
# -----------------------------
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)  # public UUID
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"))

    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    message_count = Column(Integer, default=0)

    # Relationship (optional)
    bot = relationship("Bot")
# -----------------------------
# CHATLOG MODEL
# -----------------------------

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String, index=True)    # public session UUID
    bot_id = Column(Integer, ForeignKey("bots.id"))

    user_message = Column(String, nullable=False)
    bot_response = Column(String, nullable=False)

    retrieved_sources = Column(String, nullable=True)  # JSON string of sources

    response_time_ms = Column(Integer, nullable=True)  # how long LLM took

    created_at = Column(DateTime, default=datetime.utcnow)

    bot = relationship("Bot")