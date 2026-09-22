"""
IP-SAKTI Sahayak — FastAPI Backend API Engine with Visual Cards, Sanskrit Shlokas & Risk Assessment
"""

import os
import sys
from unittest import result
from collections import defaultdict, deque
from time import monotonic
from dotenv import load_dotenv
from fastapi import Header
from sqlalchemy.orm import Session
from db import SessionLocal
from auth import User

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from db import init_db, save_query, SessionLocal
from auth import (
    User,
    UserCreate,
    UserLogin,
    Token,
    get_user,
    create_user,
    verify_password,
    create_access_token,
    decode_access_token,
)

load_dotenv()

# Simple per-IP/user in-memory rate limiter.
# No extra package is required. Limits reset automatically after each window.
_RATE_LIMIT_BUCKETS = defaultdict(deque)

def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"

def enforce_rate_limit(
    request: Request,
    bucket_name: str,
    max_requests: int,
    window_seconds: int,
) -> None:
    key = f"{bucket_name}:{_client_ip(request)}"
    now = monotonic()
    bucket = _RATE_LIMIT_BUCKETS[key]

    while bucket and now - bucket[0] >= window_seconds:
        bucket.popleft()

    if len(bucket) >= max_requests:
        retry_after = max(
            1,
            int(window_seconds - (now - bucket[0]))
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Try again in about {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    bucket.append(now)

security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    db = SessionLocal()
    try:
        user = get_user(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    finally:
        db.close()

import uvicorn

from typing import List, Optional, Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
sys.path.insert(0, PROJECT_ROOT)

from scripts.rag_assistant import generate_rag_response
from ml.predict import predict_question

app = FastAPI(
    title="IP-SAKTI Sahayak API Engine",
    description="Multilingual RAG Engine for Ayurveda IP & Regulatory Guidance",
    version="1.1.0"
)

# Initialize the database when the API starts. Uses PostgreSQL in deployment via DATABASE_URL.
init_db()
app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000"
    ).split(",")
    if origin.strip()
]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        # Only enable HSTS when the application is actually served over HTTPS.
        # This avoids breaking local HTTP development.
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    language: Optional[str] = "en"
    persona: Optional[str] = "innovator"

@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: UserCreate, http_request: Request):
    enforce_rate_limit(
        http_request,
        bucket_name="register",
        max_requests=3,
        window_seconds=300,
    )

    db = SessionLocal()
    try:
        existing_username = get_user(db, request.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists."
            )

        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered."
            )

        user = create_user(
            db,
            request.username.strip(),
            request.email.strip().lower(),
            request.password,
            role="user"
        )

        return {
            "message": "User registered successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        }
    finally:
        db.close()


@app.post("/api/v1/auth/login", response_model=Token)
async def login_user(request: UserLogin, http_request: Request):
    enforce_rate_limit(
        http_request,
        bucket_name="login",
        max_requests=5,
        window_seconds=60,
    )

    db = SessionLocal()
    try:
        user = get_user(db, request.username)

        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(user.username, user.role)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    finally:
        db.close()


class Citation(BaseModel):
    ref: str
    document: str
    section: str
    jurisdiction: str
    authority: str
    snippet: str
    page: Optional[int] = None
    source_type: Optional[str] = None
    relevance_score: Optional[float] = None
class QueryResponse(BaseModel):
    query: str
    persona: str
    language: str
    question_focus: Optional[str] = None

    ml_category: Optional[str] = None
    ml_confidence: Optional[float] = None
    ml_confidence_level: Optional[str] = None

    answer: str
    citations: List[Citation]
    herb_visual: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    compliance_roadmap: Optional[List[Dict[str, Any]]] = None

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
@app.get("/patentability")
def patentability_page():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "patentability.html")
    )


@app.get("/compliance")
def compliance_page():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "compliance.html")
    )


@app.get("/herbs")
def herbs_page():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "herbs.html")
    )

@app.get("/login")
async def login_page():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "login.html")
    )


@app.get("/register")
async def register_page():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "register.html")
    )


@app.get("/assistant")
async def assistant_page():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "ai_assistant.html")
    )

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    http_request: Request = None,
):
    enforce_rate_limit(
        http_request,
        bucket_name=f"query:{current_user.username}",
        max_requests=30,
        window_seconds=60,
    )

    # ML classification
    ml_result = predict_question(request.query)

    # Existing RAG system with ML-based routing
    result = generate_rag_response(
        user_query=request.query,
        persona=request.persona,
        language=request.language,
        ml_category=ml_result["category"]
    )

    # Persist the completed interaction for history, analytics, and future user accounts.
    try:
        save_query(
            query=request.query,
            persona=request.persona or "innovator",
            language=request.language or "en",
            ml_category=ml_result.get("category"),
            ml_confidence=ml_result.get("confidence"),
            ml_confidence_level=ml_result.get("confidence_level"),
            answer=result.get("answer", "")
        )
    except Exception as db_error:
        # Database failure must not break the core ML + RAG response.
        print(f"[WARN] Database save failed: {db_error}", flush=True)

    return QueryResponse(
        query=result["user_query"],
        persona=result["persona"],
        language=result["language"],
        question_focus=result.get("question_focus"),

        ml_category=ml_result["category"],
        ml_confidence=ml_result["confidence"],
        ml_confidence_level=ml_result["confidence_level"],

        answer=result["answer"],
        citations=result["citations"],
        herb_visual=result.get("herb_visual"),
        risk_assessment=result.get("risk_assessment"),
        compliance_roadmap=result.get("compliance_roadmap")
    )
app.mount("/app", StaticFiles(directory=PROJECT_ROOT, html=True), name="app")
app.mount("/assets", StaticFiles(directory=os.path.join(PROJECT_ROOT, "assets"), check_dir=False), name="assets")

# ============================================================
# ADMIN - VIEW REGISTERED USERS
# ============================================================

@app.get("/api/v1/admin/users")
def view_registered_users(x_admin_key: str = Header(default="")):

    admin_key = os.getenv("ADMIN_VIEW_KEY")

    if not admin_key or x_admin_key != admin_key:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    db = SessionLocal()

    try:
        users = (
            db.query(User)
            .order_by(User.created_at.desc())
            .all()
        )

        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at
            }
            for user in users
        ]

    finally:
        db.close()
    if __name__ == "__main__":
    print("[INFO] Starting IP-SAKTI Sahayak API Server on port 8000 ...", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000)