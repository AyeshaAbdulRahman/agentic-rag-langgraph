"""
graph/graph.py — LangGraph Assembly & Orchestration (with Conversation Memory)

Assembles all 9 nodes into a complete directed graph with conditional edges.

Flow:
START → spell_check → tone_detect → context_retriever → topic_guard → [CONDITIONAL]
  → retrieve → grade_documents → [CONDITIONAL]
    → web_search OR generate → grade_answer → [CONDITIONAL]
      → emotional → END

NEW: context_retriever enables multi-turn conversation awareness
"""

from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes.spell_check import spell_check_node
from graph.nodes.tone_detect import tone_detect_node
from graph.nodes.context_retriever import context_retriever_node
from graph.nodes.topic_guard import topic_guard_node
from graph.nodes.retrieve import retrieve_node
from graph.nodes.grade_documents import grade_documents_node
from graph.nodes.generate import generate_node
from graph.nodes.web_search import web_search_node
from graph.nodes.grade_answer import grade_answer_node
from graph.nodes.emotional import emotional_node


def build_graph():
    """
    Build and compile the complete LangGraph with conversation memory.
    
    Returns:
        Compiled LangGraph ready for execution
    """
    
    # Create state graph
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("spell_check", spell_check_node)
    workflow.add_node("tone_detect", tone_detect_node)
    workflow.add_node("context_retriever", context_retriever_node)
    workflow.add_node("topic_guard", topic_guard_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("grade_answer", grade_answer_node)
    workflow.add_node("emotional", emotional_node)
    
    # Set entry point
    workflow.set_entry_point("spell_check")
    
    # Add edges (linear sequence for most)
    workflow.add_edge("spell_check", "tone_detect")
    workflow.add_edge("tone_detect", "context_retriever")  # Sequential (safer)
    workflow.add_edge("context_retriever", "topic_guard")
    
    # Topic guard: conditional branch
    workflow.add_conditional_edges(
        "topic_guard",
        lambda x: "END" if not x.is_on_topic else "retrieve",
        {
            "END": END,
            "retrieve": "retrieve"
        }
    )
    
    workflow.add_edge("retrieve", "grade_documents")
    
    # Grade documents: conditional branch
    workflow.add_conditional_edges(
        "grade_documents",
        lambda x: "web_search" if not x.filtered_documents else "generate",
        {
            "web_search": "web_search",
            "generate": "generate"
        }
    )
    
    # Web search joins generate
    workflow.add_edge("web_search", "generate")
    
    workflow.add_edge("generate", "grade_answer")
    
    # Grade answer: conditional branch (retry or proceed)
    def should_retry(x):
        if not x.answer_grounded and x.retry_count < 2:
            return "generate"  # Retry
        else:
            return "emotional"  # Proceed
    
    workflow.add_conditional_edges(
        "grade_answer",
        should_retry,
        {
            "generate": "generate",
            "emotional": "emotional"
        }
    )
    
    workflow.add_edge("emotional", END)
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    return compiled_graph


# Create the global compiled graph
compiled_graph = build_graph()


if __name__ == "__main__":
    # Visualize graph structure
    print("LangGraph Structure:")
    print("=" * 60)
    print("""
    START
      ↓
    [1] spell_check
      ↓
    [2] tone_detect
      ↓
    [3] topic_guard ──[CONDITIONAL]──→ END (if off-topic)
      ↓ (if on-topic)
    [4] retrieve
      ↓
    [5] grade_documents ──[CONDITIONAL]──→ web_search (if no relevant docs)
      ↓ (if has relevant docs)      ↓
    [6a] generate ←──────────────────┘
      ↓
    [7] grade_answer ──[CONDITIONAL]──→ generate (retry if not grounded)
      ↓ (if grounded or max retries)
    [8] emotional
      ↓
      END
    """)
    print("=" * 60)
    print("\nGraph compiled successfully!")
    print(f"Entry point: spell_check")
    print(f"Exit point: END")
