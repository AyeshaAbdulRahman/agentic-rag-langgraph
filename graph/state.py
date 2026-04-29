"""
graph/state.py — LangGraph Agent State

Defines AgentState: the shared memory object that every node reads and writes.
LangGraph passes this state from node to node automatically.

All nodes operate on a single instance of this state, updated incrementally.
"""

from typing import List, Optional, Annotated, Any
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langgraph.graph import add_messages


class AgentState(BaseModel):
    """
    Shared state object for all nodes in the LangGraph.
    
    Each node reads some fields and writes others.
    LangGraph manages the state flow between nodes.
    """
    
    # ── Input ────────────────────────────────────────────────────────
    question: str = Field(
        ...,
        description="Original raw user message (before corrections)"
    )
    
    # ── Node 1: Spell Check ──────────────────────────────────────────
    corrected_question: str = Field(
        default="",
        description="User message after spell correction"
    )
    
    # ── Node 2: Tone Detection ───────────────────────────────────────
    user_tone: str = Field(
        default="calm",
        description="Detected emotional tone: anxious/sad/frustrated/confused/calm"
    )
    
    # ── Node 3: Topic Guard ──────────────────────────────────────────
    is_on_topic: bool = Field(
        default=True,
        description="True if dementia-related, False if off-topic"
    )
    refusal_message: Optional[str] = Field(
        default=None,
        description="Kind refusal message if off-topic"
    )
    
    # ── Node 4: Retrieve ─────────────────────────────────────────────
    documents: List[Document] = Field(
        default_factory=list,
        description="Top-K chunks from FAISS search"
    )
    
    # ── Node 5: Grade Documents ──────────────────────────────────────
    filtered_documents: List[Document] = Field(
        default_factory=list,
        description="Only relevant chunks after grading"
    )
    
    # ── Node 6b: Web Search ──────────────────────────────────────────
    web_search_results: Optional[str] = Field(
        default=None,
        description="DuckDuckGo search results as formatted string"
    )
    used_web_search: bool = Field(
        default=False,
        description="Flag: True if web search was used"
    )
    
    # ── Node 6a: Generate ───────────────────────────────────────────
    generation: str = Field(
        default="",
        description="Raw LLM answer before emotional wrapping"
    )
    
    # ── Node 7: Grade Answer ─────────────────────────────────────────
    answer_grounded: bool = Field(
        default=False,
        description="True if answer is supported by context"
    )
    retry_count: int = Field(
        default=0,
        description="Tracks how many times generation was retried"
    )
    
    # ── Node 8: Emotional Response ───────────────────────────────────
    final_answer: str = Field(
        default="",
        description="Final empathetic answer ready for user"
    )
    
    # ── Sources ──────────────────────────────────────────────────────
    sources: List[dict] = Field(
        default_factory=list,
        description="List of {text, source, page} for each chunk used"
    )
    
    # ── Conversation Memory / Context ────────────────────────────────
    conversation_history: List[dict] = Field(
        default_factory=list,
        description="List of {role: 'user'|'assistant', content: str} for session memory"
    )
    relevant_context: str = Field(
        default="",
        description="Relevant context retrieved from conversation history"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Unique session identifier for multi-turn conversations"
    )
    
    class Config:
        arbitrary_types_allowed = True
