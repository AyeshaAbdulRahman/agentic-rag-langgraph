"""
ingestion.py — Document Ingestion Pipeline

Processes all PDFs and TXT files from data/ folder:
1. Loads documents
2. Splits into overlapping chunks
3. Creates embeddings using free SentenceTransformer
4. Builds FAISS vector index
5. Saves chunk metadata

Run once: python ingestion.py
Or via: python main.py --ingest
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from tqdm import tqdm

from config import (
    DATA_DIR,
    VECTORSTORE_DIR,
    PROCESSED_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL
)


def load_documents_from_dir(data_dir: str) -> List[Document]:
    """
    Load all PDF and TXT files from the data directory.
    
    Args:
        data_dir: Path to directory containing documents
        
    Returns:
        List of Document objects with metadata
    """
    documents = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"✗ Data directory not found: {data_dir}")
        return documents
    
    # Find all PDFs and TXTs
    pdf_files = list(data_path.glob('*.pdf'))
    txt_files = list(data_path.glob('*.txt'))
    all_files = pdf_files + txt_files
    
    if not all_files:
        print(f"⚠ No PDF or TXT files found in {data_dir}")
        return documents
    
    print(f"📄 Found {len(all_files)} documents to process")
    
    for file_path in tqdm(all_files, desc="Loading documents"):
        try:
            if file_path.suffix.lower() == '.pdf':
                documents.extend(_load_pdf(file_path))
            elif file_path.suffix.lower() == '.txt':
                documents.extend(_load_txt(file_path))
        except Exception as e:
            print(f"✗ Error loading {file_path}: {e}")
    
    print(f"✓ Loaded {len(documents)} document pages")
    return documents


def _load_pdf(file_path: Path) -> List[Document]:
    """Extract text from PDF file."""
    documents = []
    pdf_reader = PdfReader(file_path)
    
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        'source': file_path.name,
                        'page': page_num + 1,
                        'type': 'pdf'
                    }
                )
            )
    
    return documents


def _load_txt(file_path: Path) -> List[Document]:
    """Extract text from TXT file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    return [
        Document(
            page_content=text,
            metadata={
                'source': file_path.name,
                'page': 1,
                'type': 'txt'
            }
        )
    ]


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and blank lines.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def chunk_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """
    Split documents into overlapping chunks.
    
    Args:
        documents: List of Document objects
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunked Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    for doc in tqdm(documents, desc="Chunking documents"):
        # Clean the text first
        cleaned_text = clean_text(doc.page_content)
        
        # Split into chunks
        split_texts = text_splitter.split_text(cleaned_text)
        
        for chunk_num, chunk_text in enumerate(split_texts):
            chunks.append(
                Document(
                    page_content=chunk_text,
                    metadata={
                        **doc.metadata,
                        'chunk_id': f"{doc.metadata['source']}_chunk_{chunk_num}",
                        'original_source': doc.metadata['source']
                    }
                )
            )
    
    print(f"✓ Created {len(chunks)} chunks")
    return chunks


def create_vectorstore(
    chunks: List[Document],
    vectorstore_dir: str = VECTORSTORE_DIR
) -> FAISS:
    """
    Create FAISS vector store from chunks.
    
    Uses free local SentenceTransformer embeddings.
    No API key required.
    
    Args:
        chunks: List of Document chunks
        vectorstore_dir: Directory to save FAISS index
        
    Returns:
        FAISS vector store object
    """
    print(f"🔄 Creating embeddings using {EMBEDDING_MODEL}...")
    
    # Use HuggingFaceEmbeddings from langchain-huggingface (updated, no deprecation)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}  # Use CPU to avoid CUDA issues
    )
    
    # Create FAISS index with progress
    print(f"🔄 Building FAISS index from {len(chunks)} chunks...")
    print("⏳ This may take 5-15 minutes depending on your CPU...")
    
    # Process chunks in batches with progress bar
    vectorstore = None
    batch_size = 500
    
    for i in tqdm(range(0, len(chunks), batch_size), desc="Building FAISS", unit="batch"):
        batch = chunks[i:i + batch_size]
        
        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            # Add batch to existing vectorstore
            vectorstore.add_documents(batch)
    
    # Save to disk
    os.makedirs(vectorstore_dir, exist_ok=True)
    vectorstore.save_local(vectorstore_dir)
    print(f"✓ FAISS index saved to {vectorstore_dir}/")
    
    return vectorstore


def save_chunks_jsonl(
    chunks: List[Document],
    output_dir: str = PROCESSED_DIR
) -> None:
    """
    Save chunk metadata to JSONL file for reference.
    
    Args:
        chunks: List of Document chunks
        output_dir: Directory to save chunks.jsonl
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = Path(output_dir) / 'chunks.jsonl'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            chunk_dict = {
                'content': chunk.page_content,
                'metadata': chunk.metadata
            }
            f.write(json.dumps(chunk_dict) + '\n')
    
    print(f"✓ Chunk metadata saved to {output_file}")


def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("🧠 NeuroCare AI — Document Ingestion Pipeline")
    print("=" * 60)
    
    try:
        # Step 1: Load documents
        print("\n📚 Step 1: Loading documents...")
        documents = load_documents_from_dir(DATA_DIR)
        
        if not documents:
            print("✗ No documents loaded. Add PDFs/TXTs to data/ folder.")
            return
        
        # Step 2: Chunk documents
        print("\n✂️  Step 2: Chunking documents...")
        chunks = chunk_documents(documents)
        
        # Step 3: Create vector store
        print("\n🔍 Step 3: Creating FAISS vector store...")
        vectorstore = create_vectorstore(chunks)
        
        # Step 4: Save chunk metadata
        print("\n💾 Step 4: Saving chunk metadata...")
        save_chunks_jsonl(chunks)
        
        print("\n" + "=" * 60)
        print("✓ Ingestion complete!")
        print(f"  Documents processed: {len(documents)}")
        print(f"  Chunks created: {len(chunks)}")
        print(f"  Vector store: {VECTORSTORE_DIR}/")
        print(f"  Metadata: {PROCESSED_DIR}/chunks.jsonl")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
