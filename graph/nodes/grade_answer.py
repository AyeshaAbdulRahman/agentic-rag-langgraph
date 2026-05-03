"""
graph/nodes/grade_answer.py — Node 7: Answer Grading & Hallucination Check

Anti-hallucination verification. Checks that the generated answer is
actually supported by the context that was provided.

If grounded: proceed to emotional node
If not grounded and retries remaining: go back to generate node
If not grounded but max retries exceeded: replace with a safe fallback
"""

from langchain_core.prompts import PromptTemplate
from llm_factory import get_llm
from config import MAX_GENERATE_RETRIES
from graph.state import AgentState


def grade_answer_node(state: AgentState) -> AgentState:
    """
    Node 7: Grade Answer
    
    Verifies that the generated answer is grounded in the provided context.
    Prevents hallucination by checking logical consistency.
    
    Args:
        state: Current agent state (must have generation filled)
        
    Returns:
        Updated state with answer_grounded and possibly incremented retry_count
    """
    
    # Prepare context string
    context_text = ""
    
    if state.filtered_documents:
        for i, doc in enumerate(state.filtered_documents):
            context_text += f"\n[Document {i+1}]\n{doc.page_content[:300]}...\n"
    elif state.web_search_results:
        context_text = state.web_search_results[:500]
    else:
        state.generation = (
            "I do not have enough grounded information in the available context to answer this reliably. "
            "I can only answer based on the provided material, so I would rather be transparent than guess."
        )
        state.answer_grounded = True
        return state
    
    # Build grading prompt
    prompt_template = PromptTemplate(
        input_variables=["context", "answer"],
        template="""You are a fact-checker for medical information.

Context provided:
{context}

Generated answer:
{answer}

Is this answer fully supported by the context above?
Consider:
- Are all claims in the answer backed by the context?
- Are there any claims the answer makes that contradict the context?
- Is the answer logically consistent with the context?

Reply with ONLY 'yes' or 'no'."""
    )
    
    # Get LLM
    llm = get_llm()
    
    # Run grading
    response = llm.invoke(
        prompt_template.format(
            context=context_text,
            answer=state.generation
        )
    )
    
    # Parse response
    grade = response.content.strip().lower()
    is_grounded = grade.startswith('yes')
    
    state.answer_grounded = is_grounded
    
    # If not grounded, retry while allowed.
    if not is_grounded and state.retry_count < MAX_GENERATE_RETRIES:
        state.retry_count += 1
    else:
        # If retries are exhausted, replace the answer with a safe fallback.
        if not is_grounded:
            state.generation = (
                "I cannot verify a fully grounded answer from the available context. "
                "To avoid giving you misleading information, I should stop here instead of guessing. "
                "If you want, I can answer only the clearly supported part of the question."
            )
        state.answer_grounded = True
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    from langchain_core.documents import Document
    
    # Test documents
    test_docs = [
        Document(
            page_content="Dementia is a general term for loss of memory and ability to think clearly.",
            metadata={'source': 'test.pdf', 'page': 1}
        )
    ]
    
    test_cases = [
        ("Dementia involves loss of memory and thinking ability, according to medical experts.", True),
        ("Dementia is caused by eating too much sugar.", False),
        ("Loss of memory is a symptom related to dementia.", True),
    ]
    
    print("Testing Grade Answer Node:")
    print("=" * 60)
    
    for answer, expected_grounded in test_cases:
        state = AgentState(
            question="What is dementia?",
            corrected_question="What is dementia?",
            filtered_documents=test_docs,
            generation=answer
        )
        
        result = grade_answer_node(state)
        status = "✓" if result.answer_grounded == expected_grounded else "?"
        print(f"{status} Answer: {answer[:60]}...")
        print(f"   Grounded: {result.answer_grounded} (expected: {expected_grounded})")
        print()
