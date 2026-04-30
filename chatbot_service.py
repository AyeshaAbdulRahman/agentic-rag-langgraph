"""
chatbot_service.py - Session-aware service wrapper for FastAPI.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from chatbot import ChatHandler


class ChatbotService:
    """Bridge API requests to ChatHandler while preserving backend sessions."""

    def __init__(self):
        self.handler = ChatHandler()
        self.memory = self.handler.memory

    def chat(
        self,
        *,
        message: str,
        session_id: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        if session_id:
            self._ensure_session_state(session_id, history or [])
        return self.handler.chat(message, session_id=session_id)

    def health(self) -> Dict[str, str]:
        return {
            "status": "healthy",
            "message": "NeuroCare AI is running",
        }

    def _ensure_session_state(self, session_id: str, history: List[Dict[str, str]]) -> None:
        if session_id not in self.memory.sessions:
            self.memory.sessions[session_id] = {
                "history": [],
                "importance_scores": {},
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "turn_count": 0,
            }

        session = self.memory.sessions[session_id]
        if session["history"] or not history:
            session["last_accessed"] = datetime.now()
            return

        pending_user: Optional[str] = None
        for item in history:
            role = (item.get("role") or "").strip().lower()
            content = (item.get("content") or "").strip()
            if not content:
                continue

            if role == "user":
                pending_user = content
            elif role in {"assistant", "bot"} and pending_user:
                self.memory.add_exchange(session_id, pending_user, content)
                pending_user = None

        session["last_accessed"] = datetime.now()
