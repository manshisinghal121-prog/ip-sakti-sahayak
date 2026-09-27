"""
IP-SAKTI Sahayak — FastAPI Backend API Engine
with Visual Cards, Sanskrit Shlokas & Risk Assessment
"""

import os
import sys
import uvicorn

from typing import List, Optional, Dict, Any

from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Depends
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from deep_translator import GoogleTranslator
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# DATABASE
# ============================================================

from db import (
    init_db,
    save_query,
    SessionLocal
)


# ============================================================
# AUTHENTICATION
# ============================================================

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


# ============================================================
# SECURITY
# ============================================================

security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Validate the JWT token and return the current user.
    """

    payload = decode_access_token(
        credentials.credentials
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    username = payload.get("sub")

    db = SessionLocal()

    try:

        user = get_user(
            db,
            username
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        return user

    finally:

        db.close()


# ============================================================
# PROJECT PATHS
# ============================================================

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(
    SCRIPT_DIR
)

FRONTEND_DIR = os.path.join(
    PROJECT_ROOT,
    "frontend"
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


# ============================================================
# PROJECT MODULES
# ============================================================

from scripts.rag_assistant import (
    generate_rag_response
)

from ml.predict import (
    predict_question
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="IP-SAKTI Sahayak API Engine",
    description=(
        "Multilingual RAG Engine for "
        "Ayurveda IP & Regulatory Guidance"
    ),
    version="1.1.0"
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_db()


# ============================================================
# FRONTEND STATIC FILES
# ============================================================

app.mount(
    "/frontend",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="frontend"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# LANGUAGE MAP
# ============================================================

LANGUAGE_MAP = {

    # --------------------------------------------------------
    # English
    # --------------------------------------------------------

    "en": "en",
    "english": "en",
    "English": "en",

    # --------------------------------------------------------
    # Hindi
    # --------------------------------------------------------

    "hi": "hi",
    "hindi": "hi",
    "Hindi": "hi",
    "हिंदी": "hi",
    "Hindi (हिंदी)": "hi",

    # --------------------------------------------------------
    # Sanskrit
    # --------------------------------------------------------

    "sa": "sa",
    "sanskrit": "sa",
    "Sanskrit": "sa",
    "संस्कृत": "sa",
    "संस्कृतम्": "sa",
    "Sanskrit (संस्कृतम्)": "sa",

    # --------------------------------------------------------
    # Bengali
    # --------------------------------------------------------

    "bn": "bn",
    "bengali": "bn",
    "Bengali": "bn",
    "বাংলা": "bn",

    # --------------------------------------------------------
    # Gujarati
    # --------------------------------------------------------

    "gu": "gu",
    "gujarati": "gu",
    "Gujarati": "gu",
    "ગુજરાતી": "gu",

    # --------------------------------------------------------
    # Marathi
    # --------------------------------------------------------

    "mr": "mr",
    "marathi": "mr",
    "Marathi": "mr",
    "मराठी": "mr",

    # --------------------------------------------------------
    # Tamil
    # --------------------------------------------------------

    "ta": "ta",
    "tamil": "ta",
    "Tamil": "ta",
    "தமிழ்": "ta",

    # --------------------------------------------------------
    # Telugu
    # --------------------------------------------------------

    "te": "te",
    "telugu": "te",
    "Telugu": "te",
    "తెలుగు": "te",

    # --------------------------------------------------------
    # Kannada
    # --------------------------------------------------------

    "kn": "kn",
    "kannada": "kn",
    "Kannada": "kn",
    "ಕನ್ನಡ": "kn",

    # --------------------------------------------------------
    # Malayalam
    # --------------------------------------------------------

    "ml": "ml",
    "malayalam": "ml",
    "Malayalam": "ml",
    "മലയാളം": "ml",

    # --------------------------------------------------------
    # Punjabi
    # --------------------------------------------------------

    "pa": "pa",
    "punjabi": "pa",
    "Punjabi": "pa",
    "ਪੰਜਾਬੀ": "pa",

    # --------------------------------------------------------
    # Urdu
    # --------------------------------------------------------

    "ur": "ur",
    "urdu": "ur",
    "Urdu": "ur",
    "اردو": "ur",

    # --------------------------------------------------------
    # Odia
    # --------------------------------------------------------

    "or": "or",
    "odia": "or",
    "Odia": "or",
    "ଓଡ଼ିଆ": "or",

    # --------------------------------------------------------
    # Assamese
    # --------------------------------------------------------

    "as": "as",
    "assamese": "as",
    "Assamese": "as",
    "অসমীয়া": "as",
}


# ============================================================
# NORMALIZE LANGUAGE
# ============================================================

def normalize_language(
    language: Optional[str]
) -> str:

    if not language:

        return "en"

    value = str(
        language
    ).strip()

    # Direct match
    if value in LANGUAGE_MAP:

        return LANGUAGE_MAP[value]

    # Lowercase match
    lowered = value.lower()

    for key, code in LANGUAGE_MAP.items():

        if str(key).lower() == lowered:

            return code

    # Already a language code
    valid_codes = set(
        LANGUAGE_MAP.values()
    )

    if lowered in valid_codes:

        return lowered

    # Default
    return "en"


# ============================================================
# FINAL ANSWER TRANSLATOR
# ============================================================

def translate_final_answer(
    text: str,
    language: Optional[str]
) -> str:

    """
    Translate the COMPLETE final answer.

    This is deliberately placed in main.py so that
    even if rag_assistant.py produces an English answer,
    the final API response is translated before reaching
    the frontend.
    """

    if not text:

        return text

    target_language = normalize_language(
        language
    )

    print(
        f"[LANGUAGE] Received: {language}",
        flush=True
    )

    print(
        f"[LANGUAGE] Target code: {target_language}",
        flush=True
    )

    # English does not need translation
    if target_language == "en":

        return text

    try:

        translator = GoogleTranslator(
            source="auto",
            target=target_language
        )

        translated_text = translator.translate(
            text
        )

        if translated_text:

            print(
                f"[LANGUAGE] Translation successful: "
                f"{target_language}",
                flush=True
            )

            return translated_text

        print(
            "[LANGUAGE] Translator returned empty text.",
            flush=True
        )

        return text

    except Exception as error:

        print(
            "[LANGUAGE ERROR]",
            error,
            flush=True
        )

        # Never crash the whole API because of
        # translation.
        return text


# ============================================================
# REQUEST MODEL
# ============================================================

class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question",
    )

    language: str = Field(
        default="en",
        description="Response language code",
    )

    persona: str = Field(
        default="innovator",
        description="User persona",
    )

    mode: str = Field(
        default="assistant",
        description="Response mode: assistant, patentability, or compliance",
    )

# ============================================================
# AUTH REGISTER
# ============================================================

@app.post(
    "/api/v1/auth/register",
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    request: UserCreate
):

    db = SessionLocal()

    try:

        # Check username
        existing_username = get_user(
            db,
            request.username
        )

        if existing_username:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists."
            )

        # Check email
        existing_email = db.query(
            User
        ).filter(
            User.email == request.email
        ).first()

        if existing_email:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered."
            )

        # Create user
        user = create_user(
            db,
            request.username.strip(),
            request.email.strip().lower(),
            request.password,
            role="user"
        )

        return {

            "message":
                "User registered successfully.",

            "user": {

                "id": user.id,

                "username":
                    user.username,

                "email":
                    user.email,

                "role":
                    user.role,
            }
        }

    finally:

        db.close()


# ============================================================
# AUTH LOGIN
# ============================================================

@app.get("/login")
async def login_page():
    return FileResponse(FRONTEND_DIR / "login.html")

@app.post(
    "/api/v1/auth/login",
    response_model=Token
)
async def login_user(
    request: UserLogin
):

    db = SessionLocal()

    try:

        user = get_user(
            db,
            request.username
        )

        if (
            not user
            or not verify_password(
                request.password,
                user.hashed_password
            )
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        access_token = create_access_token(
            user.username,
            user.role
        )

        return {

            "access_token":
                access_token,

            "token_type":
                "bearer"
        }

    finally:

        db.close()


# ============================================================
# CITATION MODEL
# ============================================================

class Citation(BaseModel):

    ref: str

    document: str

    section: str

    jurisdiction: str

    authority: str

    snippet: str

    page: Optional[int] = None


# ============================================================
# QUERY RESPONSE
# ============================================================

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

    herb_visual: Optional[
        Dict[str, Any]
    ] = None

    risk_assessment: Optional[
        Dict[str, Any]
    ] = None

    compliance_roadmap: Optional[
        List[Dict[str, Any]]
    ] = None


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
def read_root():

    return FileResponse(
        os.path.join(
            FRONTEND_DIR,
            "index.html"
        )
    )


# ============================================================
# PATENTABILITY PAGE
# ============================================================

@app.get("/patentability")
def patentability_page():

    return FileResponse(
        os.path.join(
            FRONTEND_DIR,
            "patentability.html"
        )
    )


# ============================================================
# COMPLIANCE PAGE
# ============================================================

@app.get("/compliance")
def compliance_page():

    return FileResponse(
        os.path.join(
            FRONTEND_DIR,
            "compliance.html"
        )
    )


# ============================================================
# HERB PAGE
# ============================================================

@app.get("/herbs")
def herbs_page():

    return FileResponse(
        os.path.join(
            FRONTEND_DIR,
            "herbs.html"
        )
    )


# ============================================================
# AI ASSISTANT PAGE
# ============================================================

@app.get("/assistant")
def assistant_page():

    return FileResponse(
        os.path.join(
            FRONTEND_DIR,
            "ai_assistant.html"
        )
    )


# ============================================================
# MAIN QUERY API
# ============================================================

@app.post(
    "/api/v1/query",
    response_model=QueryResponse
)
async def process_query(
    request: QueryRequest,
    current_user: User = Depends(
        get_current_user
    )
):

    # ========================================================
    # 1. NORMALIZE LANGUAGE
    # ========================================================

    selected_language = normalize_language(
        request.language
    )

    print(
        "========================================",
        flush=True
    )

    print(
        "[QUERY] User:",
        current_user.username,
        flush=True
    )

    print(
        "[QUERY] Question:",
        request.query,
        flush=True
    )

    print(
        "[QUERY] Original language:",
        request.language,
        flush=True
    )

    print(
        "[QUERY] Normalized language:",
        selected_language,
        flush=True
    )

    print(
        "========================================",
        flush=True
    )


    # ========================================================
    # 2. ML CLASSIFICATION
    # ========================================================

    ml_result = predict_question(
        request.query
    )


    # ========================================================
    # 3. RAG RESPONSE
    # ========================================================

    result = generate_rag_response(

        user_query=request.query,

        persona=request.persona,

        language=selected_language,

        ml_category=ml_result["category"]
    )


    # ========================================================
    # 4. GET ANSWER
    # ========================================================

    answer_text = result.get(
        "answer",
        ""
    )


    # ========================================================
    # 5. FINAL TRANSLATION
    #
    # IMPORTANT:
    # We translate HERE after the complete RAG response
    # has already been created.
    # ========================================================

    answer_text = translate_final_answer(

        answer_text,

        selected_language
    )


    # ========================================================
    # 6. SAVE QUERY TO DATABASE
    # ========================================================

    try:

        save_query(

            query=request.query,

            persona=(
                request.persona
                or "innovator"
            ),

            language=selected_language,

            ml_category=ml_result.get(
                "category"
            ),

            ml_confidence=ml_result.get(
                "confidence"
            ),

            ml_confidence_level=ml_result.get(
                "confidence_level"
            ),

            answer=answer_text
        )

    except Exception as db_error:

        print(
            f"[WARN] Database save failed: "
            f"{db_error}",
            flush=True
        )


    # ========================================================
    # 7. RETURN RESPONSE TO FRONTEND
    # ========================================================

    return QueryResponse(

        query=result[
            "user_query"
        ],

        persona=result[
            "persona"
        ],

        language=selected_language,

        question_focus=result.get(
            "question_focus"
        ),

        ml_category=ml_result[
            "category"
        ],

        ml_confidence=ml_result[
            "confidence"
        ],

        ml_confidence_level=ml_result[
            "confidence_level"
        ],

        # THIS IS THE TRANSLATED ANSWER
        answer=answer_text,

        citations=result[
            "citations"
        ],

        herb_visual=result.get(
            "herb_visual"
        ),

        risk_assessment=result.get(
            "risk_assessment"
        ),

        compliance_roadmap=result.get(
            "compliance_roadmap"
        )
    )


# ============================================================
# APP STATIC MOUNTS
# ============================================================

app.mount(
    "/app",
    StaticFiles(
        directory=PROJECT_ROOT,
        html=True
    ),
    name="app"
)


app.mount(
    "/assets",
    StaticFiles(
        directory=os.path.join(
            PROJECT_ROOT,
            "assets"
        ),
        check_dir=False
    ),
    name="assets"
)


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "[INFO] Starting IP-SAKTI Sahayak "
        "API Server on port 8000 ...",
        flush=True
    )

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )