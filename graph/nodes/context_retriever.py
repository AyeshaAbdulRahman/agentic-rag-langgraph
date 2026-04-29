"""
graph/nodes/context_retriever.py — Node 2.5: Context Retrieval from History

Retrieves relevant context from conversation history to provide continuity
in multi-turn conversations. This node runs after tone detection and before
topic guard to enhance question understanding with historical context.

Flow: Spell Check → Tone Detect → [NEW] Context Retrieval → Topic Guard → ...
"""

from graph.state import AgentState
from conversation_memory import get_memory_manager


def context_retriever_node(state: AgentState) -> AgentState:
    """
    Node 2.5: Context Retriever
    
    Retrieves relevant context from previous exchanges in the conversation.
    This allows the system to understand follow-up questions and maintain
    conversation continuity.
    
    For example:
    - Q1: "What is dementia?"
    - Q2: "What are the symptoms?" → Uses Q1 context
    - Q3: "How is it treated?" → Uses Q1+Q2 context
    
    Args:
        state: Current agent state (should have session_id and conversation_history)
        
    Returns:
        Updated state with relevant_context filled
    """
    
    # Initialize if no session
    if not state.session_id:
        state.relevant_context = ""
        return state
    
    try:
        # Get memory manager
        memory = get_memory_manager()
        
        # Retrieve context from history
        context = memory.get_context(
            session_id=state.session_id,
            current_question=state.corrected_question,
            max_context_length=1500
        )
        
        state.relevant_context = context
        
        if context:
            print(f"✓ Retrieved conversation context ({len(context)} chars)")
        
    except Exception as e:
        print(f"⚠️  Context retrieval error: {e}")
        state.relevant_context = ""
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    from conversation_memory import ConversationMemory
    
    print("Testing Context Retriever Node:")
    print("=" * 60)
    
    # Create memory and session
    memory = ConversationMemory()
    session_id = memory.create_session()
    
    # Add some history
    memory.add_exchange(
        session_id,
        "What is dementia?",
        "Dementia is a general term for a decline in mental ability..."
    )
    
    memory.add_exchange(
        session_id,
        "What are the symptoms?",
        "Common symptoms include memory loss, confusion, difficulty..."
    )
    
    # Test context retrieval
    state = AgentState(
        question="How is it treated?",
        corrected_question="How is dementia treated?",
        session_id=session_id
    )
    
    result = context_retriever_node(state)
    
    print(f"\nInput Question: {result.corrected_question}")
    print(f"\nRetrieved Context:\n{result.relevant_context}")
