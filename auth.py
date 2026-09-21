from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import re

from dotenv import load_dotenv
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session

from db import Base


# ============================================================
# SECURITY CONFIGURATION
# ============================================================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not configured. Add SECRET_KEY to the project .env file."
    )

if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY must be at least 32 characters long."
    )


# ============================================================
# USER DATABASE MODEL
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="user",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# REQUEST MODELS
# ============================================================

class UserCreate(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=255
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )


class UserLogin(BaseModel):

    username: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128
    )


class Token(BaseModel):
    access_token: str
    token_type: str


# ============================================================
# BASIC EMAIL VALIDATION
# ============================================================

def validate_email(email: str) -> bool:

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(pattern, email)
    )


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password: str) -> str:

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ============================================================
# JWT TOKEN
# ============================================================

def create_access_token(
    username: str,
    role: str
) -> str:

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(
    token: str
) -> Optional[dict]:

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            return None

        return payload

    except JWTError:

        return None


# ============================================================
# DATABASE USER FUNCTIONS
# ============================================================

def get_user(
    db: Session,
    username: str
):

    return (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = "user"
):

    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        hashed_password=hash_password(password),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user