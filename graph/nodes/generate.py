"""
graph/nodes/generate.py — Node 6a: Answer Generation

Generates the actual answer using either:
  1. Document chunks (if available from retrieval)
  2. Web search results (if document retrieval failed)

Uses a carefully designed prompt to ensure accuracy and dementia-specific focus.
"""

from langchain_core.prompts import PromptTemplate
from llm_factory import get_llm
from graph.state import AgentState


def generate_node(state: AgentState) -> AgentState:
    """
    Node 6a: Generate (with Conversation Context)
    
    Generates an answer based on available context:
    - Conversation history (if available - for context continuity)
    - If filtered_documents exist: use document chunks
    - Else if web_search_results exist: use web results
    - Else: create a helpful response acknowledging lack of information
    
    Args:
        state: Current agent state (must have filtered_documents or web_search_results)
        
    Returns:
        Updated state with generation and sources filled
    """
    
    # Prepare context and sources
    context_text = ""
    sources = []
    
    # Priority 0: Include conversation history context
    if state.relevant_context:
        context_text += f"\n{state.relevant_context}\n"
    
    # Priority 1: Use document chunks if available
    if state.filtered_documents:
        for i, doc in enumerate(state.filtered_documents):
            context_text += f"\n[Document {i+1}]\n{doc.page_content}\n"
            sources.append({
                'text': doc.page_content[:200],
                'source': doc.metadata.get('source', 'Unknown'),
                'page': doc.metadata.get('page', 'N/A')
            })
    
    # Priority 2: Use web search results if no documents
    elif state.web_search_results:
        context_text += f"\n{state.web_search_results}"
        sources.append({
            'text': 'Web search results',
            'source': 'Web Search',
            'page': 'N/A'
        })
    
    # Build generation prompt
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a compassionate dementia care expert assistant.

You are having a multi-turn conversation. Pay attention to the conversation history
to provide contextually relevant answers. Reference previous exchanges when helpful.

Answer the question using ONLY the provided context.
If the context does not contain enough information, say so honestly.
Do not make up any information.
If web search results are present, use only facts from the highest-trust
sources in the context and ignore anything promotional, sensational, or uncertain.

Context (includes conversation history and/or documents):
{context}

Current Question: {question}

Provide a clear, accurate, helpful answer that builds on the conversation:"""
    )
    
    # Get LLM
    llm = get_llm()
    chain = prompt_template | llm
    
    # Generate answer
    if context_text:
        response = chain.invoke(
            {"context": context_text, "question": state.corrected_question}
        )
        generation = response.content
    else:
        generation = (
            "I apologize, but I don't have enough information in my documents to answer this question. "
            "Would you like me to search the web for more information?"
        )
    
    state.generation = generation.strip()
    state.sources = sources
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    from langchain_core.documents import Document
    
    # Test with mock documents
    test_docs = [
        Document(
            page_content="Dementia is a general term for loss of memory and ability to think clearly. "
                        "Alzheimer's disease is the most common cause of dementia.",
            metadata={'source': 'dementia_guide.pdf', 'page': 1}
        )
    ]
    
    print("Testing Generate Node:")
    print("=" * 60)
    
    state = AgentState(
        question="What is dementia?",
        corrected_question="What is dementia?",
        filtered_documents=test_docs
    )
    
    result = generate_node(state)
    
    print(f"Question: {result.corrected_question}\n")
    print(f"Generated Answer:")
    print(f"{result.generation}\n")
    print(f"Sources: {len(result.sources)} source(s)")
    for src in result.sources:
        print(f"  - {src['source']} (Page {src['page']})")
