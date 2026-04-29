"""
graph/nodes/topic_guard.py — Node 3: Topic Guard / Conversation Blocker

Checks if the query is about dementia, Alzheimer's, memory care, or caregiving.
If NOT — ends conversation with a kind, empathetic refusal.
If YES — allows the graph to continue.

This is the gatekeeper node.
"""

from langchain_core.prompts import PromptTemplate
from llm_factory import get_llm
from graph.state import AgentState


def topic_guard_node(state: AgentState) -> AgentState:
    """
    Node 3: Topic Guard
    
    Checks if the query is dementia/memory-care related.
    If NO  → sets refusal_message and is_on_topic=False → graph ends
    If YES → sets is_on_topic=True → graph continues
    
    Args:
        state: Current agent state (must have corrected_question filled)
        
    Returns:
        Updated state with is_on_topic and possibly refusal_message filled
    """
    
    # Build prompt for topic checking
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="""Is this question about dementia, Alzheimer's, memory care, caregiving, or related topics?

Question: "{question}"

Consider related topics:
- Dementia and Alzheimer's disease
- Memory loss and cognitive decline
- Caregiving and care strategies
- Behavioral changes in dementia
- Support for patients and families
- End-of-life care
- Medications and treatments for memory disorders

Reply with ONLY 'YES' or 'NO'. No explanation."""
    )
    
    # Get LLM and run chain
    llm = get_llm()
    chain = prompt_template | llm
    
    # Check if on topic
    response = chain.invoke({"question": state.corrected_question})
    is_on_topic = response.content.strip().upper().startswith('YES')
    
    state.is_on_topic = is_on_topic
    
    # If off-topic, set refusal message
    if not is_on_topic:
        state.refusal_message = (
            "I'm here specifically to support with dementia-related questions. "
            "I'm not able to help with that topic, but I'm ready to assist you with "
            "anything about memory care, caregiving, or Alzheimer's whenever you need. 💙"
        )
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    
    test_questions = [
        ("What is dementia?", True),
        ("How do I care for someone with Alzheimer's?", True),
        ("What is Python programming?", False),
        ("How do I cook pasta?", False),
        ("My mom has memory loss, what should I do?", True),
    ]
    
    print("Testing Topic Guard Node:")
    print("=" * 60)
    
    for question, expected in test_questions:
        state = AgentState(
            question=question,
            corrected_question=question
        )
        result = topic_guard_node(state)
        status = "✓" if result.is_on_topic == expected else "✗"
        print(f"{status} Question: {question}")
        print(f"  On Topic: {result.is_on_topic} (expected: {expected})")
        if not result.is_on_topic:
            print(f"  Refusal: {result.refusal_message[:50]}...")
        print()
