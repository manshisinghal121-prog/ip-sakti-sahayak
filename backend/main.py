"""
IP-SAKTI Sahayak — FastAPI Backend API Engine with Visual Cards, Sanskrit Shlokas & Risk Assessment
"""

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from typing import List, Optional, Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from scripts.rag_assistant import generate_rag_response

app = FastAPI(
    title="IP-SAKTI Sahayak API Engine",
    description="Multilingual RAG Engine for Ayurveda IP & Regulatory Guidance",
    version="1.1.0"
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
    answer: str
    citations: List[Citation]
    herb_visual: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    compliance_roadmap: Optional[List[Dict[str, Any]]] = None

@app.get("/")
def read_root():
    return FileResponse(os.path.join(PROJECT_ROOT, "frontend_wireframe_mockup.html"))

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    result = generate_rag_response(
        user_query=request.query,
        persona=request.persona,
        language=request.language
    )
    
    return QueryResponse(
        query=result["user_query"],
        persona=result["persona"],
        language=result["language"],
        answer=result["answer"],
        citations=result["citations"],
        herb_visual=result.get("herb_visual"),
        risk_assessment=result.get("risk_assessment"),
        compliance_roadmap=result.get("compliance_roadmap")
    )

app.mount("/app", StaticFiles(directory=PROJECT_ROOT, html=True), name="app")

if __name__ == "__main__":
    print("[INFO] Starting IP-SAKTI Sahayak API Server on port 8000 ...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
