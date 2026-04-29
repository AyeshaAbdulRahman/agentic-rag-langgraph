"""
chatbot.py — ChatHandler Class with Conversation Memory

Main interface for running the LangGraph chatbot with multi-turn conversation support.
Used by both:
  1. server.py (FastAPI REST API)
  2. main.py (Terminal mode)

NEW: Maintains conversation history per session for context awareness.

Initializes the graph, handles execution, maintains memory, and formats responses.
"""

from typing import Dict, Any, List, Optional
from graph.graph import compiled_graph
from graph.state import AgentState
from conversation_memory import get_memory_manager
import uuid


class ChatHandler:
    """
    Main chatbot handler that executes the LangGraph with conversation memory.
    
    Supports:
    - Multi-turn conversations with context awareness
    - Session-based memory management
    - Conversation history tracking
    
    Usage (Terminal):
        chatbot = ChatHandler()
        session_id = chatbot.create_session()
        response = chatbot.chat("Tell me about dementia", session_id=session_id)
        print(response['reply'])
        
    Usage (API):
        chatbot = ChatHandler()
        response = chatbot.chat("Tell me about dementia", session_id="user_123")
    """
    
    def __init__(self):
        """Initialize the ChatHandler with the compiled graph and memory manager.
        
        ⚡ OPTIMIZATION: Pre-loads the embedding model at startup to avoid
        delayed first response (~2-5 seconds).
        """
        self.graph = compiled_graph
        self.memory = get_memory_manager()
        
        # ⚡ Pre-load embeddings at startup (not on first query)
        self._preload_embeddings()
    
    def _preload_embeddings(self) -> None:
        """Pre-load embeddings model to cache in memory at startup."""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from config import EMBEDDING_MODEL
            
            print("⚡ Pre-loading embedding model...")
            embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
            print("✓ Embedding model pre-loaded and cached")
        except Exception as e:
            print(f"⚠️  Could not pre-load embeddings: {e}")
            print("   (Will load on first query instead)")
    
    def create_session(self) -> str:
        """
        Create a new conversation session.
        
        Returns:
            session_id: Unique identifier for the session
        """
        session_id = self.memory.create_session()
        print(f"📌 New session created: {session_id}")
        return session_id
    
    def chat(self, user_message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the chatbot graph and return formatted response with conversation memory.
        
        Args:
            user_message: User's input question/message
            session_id: Optional session identifier for multi-turn conversations
                       If None, creates stateless response
            
        Returns:
            Dictionary with keys:
              - reply: Final emotionally-aware answer
              - references: List of source references
              - tone_detected: Detected emotional tone
              - used_web_search: Whether web search was used
              - is_on_topic: Whether question was dementia-related
              - session_id: Session ID for tracking
              - turn_number: Turn count in this session
        """
        
        try:
            # Initialize state with user input
            initial_state = AgentState(
                question=user_message,
                session_id=session_id
            )
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Format response
            response = self._format_response(final_state)
            
            # Store in memory if session exists
            if session_id:
                self.memory.add_exchange(
                    session_id,
                    user_message,
                    response['reply']
                )
                response['session_id'] = session_id
                summary = self.memory.get_session_summary(session_id)
                response['turn_number'] = summary.get('turn_count', 0)
            
            return response
        
        except Exception as e:
            # Error handling
            print(f"✗ Error in chatbot: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'reply': f"I encountered an error processing your request: {str(e)}",
                'references': [],
                'tone_detected': 'calm',
                'used_web_search': False,
                'is_on_topic': True,
                'error': str(e),
                'session_id': session_id
            }
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session to clear
            
        Returns:
            True if successful
        """
        return self.memory.clear_session(session_id)
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session info
        """
        return self.memory.get_session_summary(session_id)
    
    def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        self.memory.cleanup_expired_sessions()
    
    def _format_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the final state into a user-friendly response.
        
        Args:
            state: Final state after graph execution (returned as dict by invoke)
            
        Returns:
            Formatted response dictionary
        """
        
        # Check if question was off-topic
        if not state.get('is_on_topic', False):
            reply = state.get('refusal_message') or (
                "I'm here specifically to help with dementia-related questions. "
                "Please ask me about memory care, caregiving, or Alzheimer's."
            )
        else:
            # Use the final emotional answer
            reply = state.get('final_answer') or state.get('generation') or (
                "I apologize, but I wasn't able to generate a proper response. "
                "Please try asking your question differently."
            )
        
        # Format references
        references = []
        sources = state.get('sources', [])
        if sources:
            for source in sources:
                references.append({
                    'text': source.get('text', '')[:100],
                    'source': source.get('source', 'Unknown'),
                    'page': source.get('page', 'N/A')
                })
        
        # Build response
        response = {
            'reply': reply,
            'references': references,
            'tone_detected': state.get('user_tone', 'calm'),
            'used_web_search': state.get('used_web_search', False),
            'is_on_topic': state.get('is_on_topic', False),
            'retry_count': state.get('retry_count', 0),
            'corrected_question': state.get('corrected_question', ''),
            'has_context': bool(state.get('relevant_context', ''))
        }
        
        return response


if __name__ == "__main__":
    # Quick test of ChatHandler
    print("Testing ChatHandler:")
    print("=" * 60)
    
    try:
        chatbot = ChatHandler()
        print("✓ ChatHandler initialized\n")
        
        # Test on-topic question
        print("Test 1: On-topic question")
        response = chatbot.chat("What is Alzheimer's disease?")
        print(f"Reply: {response['reply'][:100]}...")
        print(f"Tone: {response['tone_detected']}")
        print(f"On Topic: {response['is_on_topic']}\n")
        
        # Test off-topic question
        print("Test 2: Off-topic question")
        response = chatbot.chat("How do I cook pasta?")
        print(f"Reply: {response['reply'][:100]}...")
        print(f"On Topic: {response['is_on_topic']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
