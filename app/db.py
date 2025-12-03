from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -----------------------------------------
# DATABASE URL (SQLite)
# -----------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# For SQLite, we need connect_args
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Dependency to get DB session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
