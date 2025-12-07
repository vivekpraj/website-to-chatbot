import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app import models, schemas
from app.routers.auth import get_current_user
from app.services.vector_store import reset_chroma_for_bot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------------------------------
# Helper: ensure caller is SUPER ADMIN
# ---------------------------------------------------
def ensure_super_admin(current_user: models.User):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Admin access only")


# ---------------------------------------------------
# 1) LIST ALL USERS  (ADMIN ONLY)
# ---------------------------------------------------
@router.get("/users", response_model=List[schemas.AdminUserSummary])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Admin: see all users + how many bots each has.
    """
    ensure_super_admin(current_user)

    users = db.query(models.User).all()
    out: list[schemas.AdminUserSummary] = []

    for u in users:
        bot_count = (
            db.query(models.Bot)
            .filter(models.Bot.user_id == u.id)
            .count()
        )

        out.append(
            schemas.AdminUserSummary(
                id=u.id,
                email=u.email,
                name=u.name,
                role=u.role,
                bot_count=bot_count,
            )
        )

    return out


# ---------------------------------------------------
# 2) LIST ALL BOTS (ADMIN ONLY)
#    Optional filter: ?owner_id=123
# ---------------------------------------------------
@router.get("/bots", response_model=List[schemas.AdminBotSummary])
def list_bots(
    owner_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Admin: see all bots in the system.
    Optional: filter by owner_id.
    """
    ensure_super_admin(current_user)

    query = db.query(models.Bot)

    if owner_id is not None:
        query = query.filter(models.Bot.user_id == owner_id)

    bots = query.all()
    out: list[schemas.AdminBotSummary] = []

    for b in bots:
        out.append(
            schemas.AdminBotSummary(
                bot_id=b.bot_id,
                owner_id=b.user_id,
                owner_email=b.owner.email if b.owner else None,
                website_url=b.website_url,
                status=b.status,
                message_count=b.message_count or 0,
                created_at=b.created_at,
                last_used_at=b.last_used_at,
            )
        )

    return out


# ---------------------------------------------------
# 3) GLOBAL SAAS METRICS (ADMIN ONLY)
# ---------------------------------------------------
@router.get("/stats", response_model=schemas.SaaSStats)
def get_saas_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Admin: high-level stats for the whole platform.
    """
    ensure_super_admin(current_user)

    total_users = db.query(models.User).count()
    total_bots = db.query(models.Bot).count()

    total_messages = (
        db.query(func.coalesce(func.sum(models.Bot.message_count), 0))
        .scalar()
        or 0
    )

    return schemas.SaaSStats(
        total_users=total_users,
        total_bots=total_bots,
        total_messages=total_messages,
    )


# ---------------------------------------------------
# 4) DELETE BOT (ADMIN ONLY)
# ---------------------------------------------------
@router.delete("/bots/{bot_id}")
def admin_delete_bot(
    bot_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Admin: delete any bot + its Chroma index.
    """
    ensure_super_admin(current_user)

    bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # delete vector store folder
    reset_chroma_for_bot(bot_id)

    db.delete(bot)
    db.commit()

    return {"detail": f"Bot {bot_id} deleted"}


# ---------------------------------------------------
# 5) DELETE USER (ADMIN ONLY)
# ---------------------------------------------------
@router.delete("/users/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Admin: delete a user (and their bots via cascade).
    """
    ensure_super_admin(current_user)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Optionally: delete each bot's Chroma
    for bot in user.bots:
        reset_chroma_for_bot(bot.bot_id)

    db.delete(user)
    db.commit()

    return {"detail": f"User {user_id} deleted (and their bots)"}
