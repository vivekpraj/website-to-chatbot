from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import logging

from .db import Base, engine
from . import models 
from .routers import bots, chat


# -----------------------------
# LOGGING CONFIGURATION
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI()


# -----------------------------
# DATABASE TABLE CREATION
# -----------------------------
logger.info("Creating database tables if not exist...")
Base.metadata.create_all(bind=engine)
logger.info("Database setup complete.")


# -----------------------------
# STATIC FILES & TEMPLATES
# -----------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# -----------------------------
# ROUTERS
# -----------------------------
app.include_router(bots.router, prefix="/bots", tags=["Bots"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
