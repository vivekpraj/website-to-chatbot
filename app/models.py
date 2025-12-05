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
