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
            
            # Extract chunk metadata
            chunk_id = doc.metadata.get('chunk_id', 'N/A')
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            
            # Build source reference in format: "Chunk <ID> | Page <N> | <filename>"
            source_ref = f"Chunk {chunk_id} | Page {page} | {source}"
            
            sources.append({
                'text': doc.page_content[:500],  # Include more context (500 chars instead of 200)
                'source': source_ref,
                'chunk_id': chunk_id,
                'page': page,
                'filename': source,
                'full_text': doc.page_content  # Store full text for detailed references
            })
    
    # Priority 2: Use web search results if no documents
    elif state.web_search_results:
        context_text += f"\n{state.web_search_results}"
        sources.append({
            'text': 'Web search results',
            'source': 'Web Search',
            'chunk_id': 'N/A',
            'page': 'N/A',
            'filename': 'Web Search',
            'full_text': state.web_search_results
        })
    
    # Build generation prompt with detailed answer instructions
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a compassionate dementia care expert assistant.

You are having a multi-turn conversation. Pay attention to the conversation history
to provide contextually relevant answers. Reference previous exchanges when helpful.

==== DETAILED ANSWER GUIDELINES ====

Your goal is to provide COMPREHENSIVE, WELL-STRUCTURED, and DETAILED answers.

ANSWER STRUCTURE:
1. Start with a clear, direct answer to the main question
2. Provide detailed explanation backed by context
3. Include practical details, examples, and specifics from the provided information
4. Organize information into logical paragraphs (not bullet points unless asked)

DEPTH GUIDELINES:
- For SIMPLE questions: Provide at least 1-2 detailed paragraphs (4-5 sentences each)
- For MODERATE complexity: Provide 2-3 comprehensive paragraphs explaining different aspects
- For COMPLEX questions: Provide 3-5+ paragraphs with structured guidance, specific examples, and practical tips
- For caregiving/practical questions: Always give step-by-step guidance with real details from context
- ALWAYS extract and USE the full context - don't abbreviate or summarize superficially

QUALITY REQUIREMENTS:
- Be confident and authoritative while staying grounded in provided context
- Explain WHY things matter and HOW to apply information when relevant
- Break down complex topics into understandable parts
- Use clear transitions between ideas
- Reference specific details from the context you're given
- If context is incomplete, provide what's available and explicitly note gaps

IMPORTANT: Answer using ONLY the provided context.
If context is insufficient, be honest and note what information is missing.
Never invent, infer, or add unsupported medical facts.

Context (includes conversation history and/or documents):
{context}

User's Question: {question}

=== GENERATE DETAILED ANSWER NOW ==="""
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
            "I apologize, but I don't have enough information in my documents to answer this question comprehensively. "
            "The context needed to provide you a detailed answer is not available. "
            "Would you like me to search the web for more detailed information on this topic?"
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
