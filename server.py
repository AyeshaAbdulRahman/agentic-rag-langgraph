"""
server.py — FastAPI REST API Server

Provides HTTP endpoints for the chatbot.
Used by React frontend (or any HTTP client).

Endpoints:
  POST /chat              - Send message, get response
  GET /health            - Health check
  GET /                  - API info

CORS: Enabled for all origins (allows React to connect)

Usage:
  uvicorn server:app --host 127.0.0.1 --port 5001
  or: python main.py --server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from chatbot import ChatHandler
from config import SERVER_HOST, SERVER_PORT


# ── FastAPI App Setup ────────────────────────────────────────────────

app = FastAPI(
    title="NeuroCare AI API",
    description="Agentic RAG Chatbot for Dementia Care",
    version="2.0"
)

# ── CORS Setup (allow React frontend from any port) ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response Models ──────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    message: str
    session_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Response body for /chat endpoint."""
    reply: str
    references: List[Dict[str, Any]]
    tone_detected: str
    used_web_search: bool
    is_on_topic: bool
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Response body for /health endpoint."""
    status: str
    message: str


# ── Global ChatHandler ───────────────────────────────────────────────

try:
    chatbot = ChatHandler()
    chatbot_ready = True
except Exception as e:
    print(f"✗ Failed to initialize chatbot: {e}")
    chatbot_ready = False
    chatbot = None


# ── Endpoints ────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    """API information endpoint."""
    return {
        "name": "NeuroCare AI",
        "version": "2.0",
        "description": "Agentic RAG Chatbot for Dementia Care",
        "endpoints": {
            "POST /chat": "Send a message to the chatbot",
            "GET /health": "Health check",
            "GET /docs": "Swagger API documentation"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    if chatbot_ready:
        return {
            "status": "healthy",
            "message": "NeuroCare AI is running"
        }
    else:
        raise HTTPException(
            status_code=503,
            detail="Chatbot not ready. Check initialization."
        )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint - send a message to the chatbot.
    
    Args:
        request: ChatRequest with message, session_id, and chat history
        
    Returns:
        ChatResponse with reply and metadata
    """
    
    if not chatbot_ready:
        raise HTTPException(
            status_code=503,
            detail="Chatbot not initialized. Please check the server logs."
        )
    
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    try:
        # Run chatbot
        response = chatbot.chat(request.message)
        
        # Build response object
        return ChatResponse(
            reply=response['reply'],
            references=response['references'],
            tone_detected=response['tone_detected'],
            used_web_search=response['used_web_search'],
            is_on_topic=response['is_on_topic'],
            session_id=request.session_id
        )
    
    except Exception as e:
        print(f"✗ Error processing chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )


# ── Error Handlers ───────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


# ── Server Entry Point ───────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 NeuroCare AI — FastAPI Server")
    print("=" * 60)
    print(f"Starting server at http://{SERVER_HOST}:{SERVER_PORT}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )
