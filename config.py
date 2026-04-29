"""
config.py — Central Settings for NeuroCare AI
All configuration in one place. Never hardcode values in other files.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Directories ──────────────────────────────────────────────────────
DATA_DIR = os.getenv('DATA_DIR', 'data')
VECTORSTORE_DIR = os.getenv('VECTORSTORE_DIR', 'vectorstore')
PROCESSED_DIR = os.getenv('PROCESSED_DIR', 'processed')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ── Document Processing Settings ─────────────────────────────────────
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))      # Increased from 800 for laptop speed
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 100)) # Reduced from 150 for faster processing
TOP_K_RETRIEVAL = int(os.getenv('TOP_K_RETRIEVAL', 4))  # Reduced from 5 for faster queries

# ── Embedding Model ──────────────────────────────────────────────────
# Free local SentenceTransformer — no API key needed
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

# ── LLM Configuration ────────────────────────────────────────────────
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'mistral')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Model names
MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-small-latest')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# ── LLM Parameters ───────────────────────────────────────────────────
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0))  # Deterministic
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', 2000))

# ── Server Settings ─────────────────────────────────────────────────
SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
SERVER_PORT = int(os.getenv('SERVER_PORT', 5001))

# ── Feature Flags ────────────────────────────────────────────────────
ENABLE_SPELL_CHECK = os.getenv('ENABLE_SPELL_CHECK', 'true').lower() == 'true'
ENABLE_TONE_DETECTION = os.getenv('ENABLE_TONE_DETECTION', 'true').lower() == 'true'
ENABLE_WEB_SEARCH = os.getenv('ENABLE_WEB_SEARCH', 'true').lower() == 'true'

# ── Retry Settings ───────────────────────────────────────────────────
MAX_GENERATE_RETRIES = int(os.getenv('MAX_GENERATE_RETRIES', 2))

# ── Validation ───────────────────────────────────────────────────────
if LLM_PROVIDER not in ['mistral', 'openai']:
    raise ValueError(f"LLM_PROVIDER must be 'mistral' or 'openai', got: {LLM_PROVIDER}")

if LLM_PROVIDER == 'mistral' and not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is required when LLM_PROVIDER='mistral'")

if LLM_PROVIDER == 'openai' and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER='openai'")
