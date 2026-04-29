"""
graph/nodes/grade_documents.py — Node 5: Document Relevance Grading

For each retrieved chunk, asks the LLM whether it's actually relevant
to the user's question. Filters out irrelevant chunks before generation.

Decision logic:
  - If 1+ chunks are relevant → go to generate node
  - If 0 chunks are relevant  → go to web_search node (fallback)
"""

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from llm_factory import get_llm
from langchain_core.documents import Document
from graph.state import AgentState


class GradeDecision(BaseModel):
    """Binary decision: is this chunk relevant?"""
    binary_score: str = Field(
        description="'yes' or 'no' for chunk relevance"
    )


def grade_documents_node(state: AgentState) -> AgentState:
    """
    Node 5: Grade Documents
    
    Evaluates each retrieved chunk for relevance to the user's question.
    Keeps only those that the LLM deems relevant.
    
    Also performs geo-context checking to avoid documents from mismatched
    geographic regions (e.g., rejecting Bangalore hospitals when asking
    about Karachi hospitals).
    
    Args:
        state: Current agent state (must have documents filled)
        
    Returns:
        Updated state with filtered_documents filled
    """
    
    # If no documents, return empty
    if not state.documents:
        state.filtered_documents = []
        return state
    
    # Extract geographic context from conversation (if available)
    expected_geo = _extract_expected_geography(state.relevant_context)
    
    # Build grading prompt
    prompt_template = PromptTemplate(
        input_variables=["question", "chunk"],
        template="""You are a document relevance grader for dementia care.

Question: {question}

Document chunk: {chunk}

Is this document chunk relevant and useful for answering the question?
Consider:
- Does it address the topic?
- Is the information accurate and helpful?
- Is it specific enough to be useful?
- Is it geographically relevant (if a specific location was mentioned)?

Reply with ONLY 'yes' or 'no'."""
    )
    
    # Get LLM
    llm = get_llm()
    
    # Grade each document
    filtered_docs = []
    
    for doc in state.documents:
        # First: Check geographic mismatch (hard filter)
        if expected_geo:
            doc_geo = _extract_document_geography(doc.page_content)
            if doc_geo and doc_geo != expected_geo:
                # Document is from a different geographic region - skip it
                print(f"  ⚠️  Skipping: Geographic mismatch (doc: {doc_geo}, expected: {expected_geo})")
                continue
        
        # Second: LLM relevance check
        response = llm.invoke(
            prompt_template.format(
                question=state.corrected_question,
                chunk=doc.page_content[:500]  # Use first 500 chars to save tokens
            )
        )
        
        # Parse response
        grade = response.content.strip().lower()
        
        # Keep if relevant
        if grade.startswith('yes'):
            filtered_docs.append(doc)
    
    state.filtered_documents = filtered_docs
    
    return state


def _extract_expected_geography(context: str) -> str:
    """
    Extract expected geographic location from conversation context.
    
    Args:
        context: Conversation history context
        
    Returns:
        Geographic indicator ('karachi', 'bangalore', 'singapore', etc.) or empty string
    """
    if not context:
        return ""
    
    context_lower = context.lower()
    
    # Check for specific locations
    locations = {
        'karachi': ['karachi', 'pakistan'],
        'bangalore': ['bangalore', 'bengaluru', 'india'],
        'singapore': ['singapore'],
        'dubai': ['dubai', 'uae'],
    }
    
    for location, keywords in locations.items():
        if any(kw in context_lower for kw in keywords):
            return location
    
    return ""


def _extract_document_geography(content: str) -> str:
    """
    Extract geographic location mentioned in document.
    
    Args:
        content: Document content
        
    Returns:
        Geographic indicator or empty string
    """
    if not content:
        return ""
    
    content_lower = content.lower()
    
    # Check for specific locations
    locations = {
        'karachi': ['karachi', 'pakistan', 'aga khan university hospital'],
        'bangalore': ['bangalore', 'bengaluru', 'nimhans', 'manipal hospitals bangalore'],
        'singapore': ['singapore', 'singhealth', 'national university hospital singapore'],
        'dubai': ['dubai', 'uae', 'emirates'],
    }
    
    for location, keywords in locations.items():
        if any(kw in content_lower for kw in keywords):
            return location
    
    return ""


if __name__ == "__main__":
    # Quick test (requires document retrieval first)
    from graph.state import AgentState
    
    # Example documents for testing
    test_docs = [
        Document(
            page_content="Alzheimer's is a progressive neurodegenerative disease that affects memory and thinking skills.",
            metadata={'source': 'test.pdf', 'page': 1}
        ),
        Document(
            page_content="Paris is the capital of France with a population of about 2 million.",
            metadata={'source': 'test.pdf', 'page': 2}
        ),
        Document(
            page_content="Early signs of dementia include difficulty remembering recent events.",
            metadata={'source': 'test.pdf', 'page': 3}
        ),
    ]
    
    print("Testing Grade Documents Node:")
    print("=" * 60)
    
    state = AgentState(
        question="What are signs of Alzheimer's disease?",
        corrected_question="What are signs of Alzheimer's disease?",
        documents=test_docs
    )
    
    result = grade_documents_node(state)
    
    print(f"Question: {state.corrected_question}")
    print(f"Total documents: {len(result.documents)}")
    print(f"Relevant documents: {len(result.filtered_documents)}\n")
    
    for i, doc in enumerate(result.filtered_documents, 1):
        print(f"Document {i} (RELEVANT):")
        print(f"  {doc.page_content[:80]}...")
        print()
