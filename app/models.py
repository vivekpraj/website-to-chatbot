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
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)

    # One user -> Many bots
    bots = relationship("Bot", back_populates="owner")


# -----------------------------
# BOT MODEL
# -----------------------------
class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    bot_id = Column(String, unique=True, index=True)     # UUID for chat URL
    website_url = Column(String, nullable=False)

    status = Column(String, default="processing")         # processing / ready / failed

    vector_index_path = Column(String, nullable=True)  # path to chroma folder


    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="bots")
