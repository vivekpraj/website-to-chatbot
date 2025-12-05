import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fastapi.security import APIKeyHeader

from app.db import get_db
from app import models, schemas

router = APIRouter()
logger = logging.getLogger(__name__)

# ====================================
# JWT CONFIG
# ====================================
SECRET_KEY = "super-secret-dev-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ====================================
# THIS SHOWS THE "AUTHORIZE" BUTTON
# ====================================
auth_header = APIKeyHeader(name="Authorization", auto_error=False)


# ====================================
# PASSWORD HELPERS
# ====================================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


# ====================================
# CREATE ACCESS TOKEN
# ====================================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ====================================
# READ TOKEN FROM Authorization HEADER
# ====================================
def get_current_user(
    token: str = Depends(auth_header),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ====================================
# REGISTER
# ====================================
@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    new_user = models.User(
        email=payload.email,
        name=payload.name,
        hashed_password=get_password_hash(payload.password),
        role="client",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ====================================
# LOGIN (RETURNS ACCESS TOKEN)
# ====================================
@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return {"access_token": token, "token_type": "bearer"}

# ====================================
# SUPER ADMIN: CHANGE USER ROLE
# ====================================
@router.post("/set-role")
def set_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Ensure only the SUPER ADMIN can do this
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Admin access only")

    # Validate user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the role
    user.role = new_role
    db.commit()
    db.refresh(user)

    return {
        "message": "Role updated successfully",
        "user_id": user.id,
        "new_role": user.role
    }
