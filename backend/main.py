"""
IP-SAKTI Sahayak — FastAPI Backend API Engine with Visual Cards, Sanskrit Shlokas & Risk Assessment
"""

import os
import sys
from unittest import result

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
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
app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    persona: Optional[str] = "innovator"

class Citation(BaseModel):
    ref: str
    document: str
    section: str
    jurisdiction: str
    authority: str
    snippet: str
    page: Optional[int] = None
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


@app.get("/assistant")
def assistant_page():
    return FileResponse(
        os.path.join(FRONTEND_DIR, "ai_assistant.html")
    )

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):

    # ML classification
    ml_result = predict_question(request.query)

    # Existing RAG system with ML-based routing
    result = generate_rag_response(
        user_query=request.query,
        persona=request.persona,
        language=request.language,
        ml_category=ml_result["category"]
    )

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

if __name__ == "__main__":
    print("[INFO] Starting IP-SAKTI Sahayak API Server on port 8000 ...", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000)
