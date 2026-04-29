"""
graph/nodes/retrieve.py — Node 4: Document Retrieval via FAISS

Loads the FAISS vector index from disk and searches for the top-K
most semantically similar chunks to the user's corrected question.

Uses free local SentenceTransformer embeddings (same model as ingestion).
"""

import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from config import VECTORSTORE_DIR, EMBEDDING_MODEL, TOP_K_RETRIEVAL
from graph.state import AgentState

# ⚡ OPTIMIZATION: Cache embeddings and FAISS index in memory
# Load once on first use, then reuse for all subsequent queries
_cached_embeddings = None
_cached_vectorstore = None


def retrieve_node(state: AgentState) -> AgentState:
    """
    Node 4: Retrieve
    
    Loads FAISS index and searches for top-K semantically similar chunks
    to the corrected user question.
    
    ⚡ OPTIMIZED: 
    - Caches embeddings and FAISS index in memory after first load
    - Injects conversation context into search query for better relevance
    - Avoids geographic mismatches by including location context
    
    Args:
        state: Current agent state (must have corrected_question filled)
        
    Returns:
        Updated state with documents filled (list of top-K chunks)
    """
    global _cached_embeddings, _cached_vectorstore
    
    # Check if vectorstore exists
    vectorstore_path = Path(VECTORSTORE_DIR)
    if not vectorstore_path.exists():
        print(f"⚠️  Vectorstore not found at {VECTORSTORE_DIR}")
        print(f"   Run 'python main.py --ingest' first to build the index")
        state.documents = []
        return state
    
    try:
        # ⚡ Load embeddings from cache or initialize if first time
        if _cached_embeddings is None:
            print("📦 Caching embeddings model in memory...")
            _cached_embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
            print("✓ Embeddings cached")
        
        # ⚡ Load FAISS index from cache or disk if first time
        if _cached_vectorstore is None:
            print("📦 Caching FAISS index in memory...")
            _cached_vectorstore = FAISS.load_local(
                VECTORSTORE_DIR,
                _cached_embeddings,
                allow_dangerous_deserialization=True
            )
            print("✓ FAISS index cached")
        
        # ⚡ NEW: Build enhanced search query with conversation context
        search_query = state.corrected_question
        
        # Extract context hints from relevant_context (if available)
        if state.relevant_context:
            # Try to extract key entities (location, hospital names, etc.) from context
            context_lower = state.relevant_context.lower()
            
            # Geographic hints
            geo_hints = []
            if 'karachi' in context_lower or 'pakistan' in context_lower:
                geo_hints.append('Karachi Pakistan')
            elif 'singapore' in context_lower:
                geo_hints.append('Singapore')
            elif 'bangalore' in context_lower or 'india' in context_lower:
                geo_hints.append('Bangalore India')
            
            # Hospital/organization hints
            org_hints = []
            if 'aga khan' in context_lower:
                org_hints.append('Aga Khan')
            if 'nimhans' in context_lower:
                org_hints.append('NIMHANS')
            if 'manipal' in context_lower:
                org_hints.append('Manipal')
            
            # Enhance query with context
            if geo_hints or org_hints:
                context_boost = ""
                if org_hints:
                    context_boost += f" {' '.join(org_hints)}"
                if geo_hints:
                    context_boost += f" {' '.join(geo_hints)}"
                
                search_query = f"{state.corrected_question}{context_boost}"
                print(f"🔍 Enhanced query with context: {search_query[:100]}...")
        
        # Search for top-K similar chunks using cached index
        documents = _cached_vectorstore.similarity_search(
            search_query,
            k=TOP_K_RETRIEVAL
        )
        
        state.documents = documents
        
    except Exception as e:
        print(f"✗ Error loading vectorstore: {e}")
        state.documents = []
    
    return state


if __name__ == "__main__":
    # Quick test
    from graph.state import AgentState
    
    # This requires an ingested vectorstore to exist
    if not Path(VECTORSTORE_DIR).exists():
        print("⚠️  Vectorstore not found. Run ingestion first:")
        print("   python main.py --ingest")
    else:
        print("Testing Retrieve Node:")
        print("=" * 60)
        
        test_query = "What are the symptoms of Alzheimer's disease?"
        state = AgentState(
            question=test_query,
            corrected_question=test_query
        )
        
        result = retrieve_node(state)
        
        print(f"Query: {test_query}")
        print(f"Retrieved {len(result.documents)} chunks:\n")
        
        for i, doc in enumerate(result.documents, 1):
            print(f"Chunk {i}:")
            print(f"  Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"  Page: {doc.metadata.get('page', 'N/A')}")
            print(f"  Content: {doc.page_content[:100]}...")
            print()
