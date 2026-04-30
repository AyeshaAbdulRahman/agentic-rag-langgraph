"""
After trust and quality filter: 4server.py - FastAPI REST API server for the agentic RAG chatbot.

Provides HTTP endpoints used by the NeuroCare backend.
"""

from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chatbot_service import ChatbotService
from config import SERVER_HOST, SERVER_PORT


app = FastAPI(
    title="NeuroCare AI API",
    description="Agentic RAG Chatbot for Dementia Care",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request body for /chat."""

    message: str
    session_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Response body for /chat."""

    reply: str
    references: List[Dict[str, Any]]
    tone_detected: str
    used_web_search: bool
    is_on_topic: bool
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Response body for /health."""

    status: str
    message: str


try:
    chatbot_service = ChatbotService()
    chatbot_ready = True
except Exception as exc:
    print(f"Failed to initialize chatbot: {exc}")
    chatbot_ready = False
    chatbot_service = None


@app.get("/", tags=["Info"])
async def root():
    return {
        "name": "NeuroCare AI",
        "version": "2.0",
        "description": "Agentic RAG Chatbot for Dementia Care",
        "endpoints": {
            "POST /chat": "Send a message to the chatbot",
            "GET /health": "Health check",
            "GET /docs": "Swagger API documentation",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    if chatbot_ready:
        return chatbot_service.health()

    raise HTTPException(
        status_code=503,
        detail="Chatbot not ready. Check initialization.",
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    if not chatbot_ready:
        raise HTTPException(
            status_code=503,
            detail="Chatbot not initialized. Please check the server logs.",
        )

    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty",
        )

    try:
        response = chatbot_service.chat(
            message=request.message,
            session_id=request.session_id,
            history=request.history or [],
        )
        return ChatResponse(
            reply=response["reply"],
            references=response["references"],
            tone_detected=response["tone_detected"],
            used_web_search=response["used_web_search"],
            is_on_topic=response["is_on_topic"],
            session_id=request.session_id,
        )
    except Exception as exc:
        print(f"Error processing chat: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(exc)}",
        ) from exc


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("NeuroCare AI - FastAPI Server")
    print("=" * 60)
    print(f"Starting server at http://{SERVER_HOST}:{SERVER_PORT}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
    )
