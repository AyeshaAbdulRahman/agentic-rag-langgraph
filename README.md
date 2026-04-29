# 🧠 NeuroCare AI v2 — Complete Implementation Guide

## ✨ What You Have

A fully implemented, production-ready **Agentic RAG Chatbot for Dementia Care** built with:
- **LangGraph**: Multi-node intelligent agent pipeline
- **Mistral AI**: Free LLM (or OpenAI alternative)
- **FAISS**: Local vector search on your documents
- **FastAPI**: REST API for React/web frontend
- **Spell Check**: Auto-correction of user queries
- **Emotional Intelligence**: Tone-aware responses

---

## 📦 What's Included

### Core Files (5 Phases)

**Phase 1 - Setup**
- `requirements.txt` — All dependencies
- `.env` — Configuration (API keys)
- `config.py` — Centralized settings
- `llm_factory.py` — LLM provider switching

**Phase 2 - Document Processing**
- `ingestion.py` — Transform PDFs/TXTs → FAISS index
- `data/` — Your dementia documents (add PDFs/TXTs here)

**Phase 3 - LangGraph State & Nodes 1-4**
- `graph/state.py` — Shared state between nodes
- `graph/nodes/spell_check.py` — Auto-fix typos
- `graph/nodes/tone_detect.py` — Detect emotion (anxious/sad/frustrated/confused/calm)
- `graph/nodes/topic_guard.py` — Block off-topic questions
- `graph/nodes/retrieve.py` — FAISS semantic search

**Phase 4 - Nodes 5-8 & Graph**
- `graph/nodes/grade_documents.py` — Relevance grading
- `graph/nodes/generate.py` — Answer generation
- `graph/nodes/web_search.py` — DuckDuckGo fallback
- `graph/nodes/grade_answer.py` — Hallucination prevention
- `graph/nodes/emotional.py` — Emotional tone wrapping
- `graph/graph.py` — Graph assembly & orchestration

**Phase 5 - Chatbot & Server**
- `chatbot.py` — ChatHandler class (graph executor)
- `server.py` — FastAPI REST API
- `main.py` — CLI entry point (--ingest, --chat, --server)

### Documentation
- `PLAN.md` — Detailed implementation plan with progress tracking
- `docx_content.txt` — Original requirements document
- `README.md` — This file

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Free Mistral API Key
```
URL: https://console.mistral.ai
Sign up (no credit card needed)
Create API key → Copy it
```

### Step 2: Configure Environment
Edit `.env` file:
```
MISTRAL_API_KEY=your_key_here
LLM_PROVIDER=mistral
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=neurocare-rag
```

### Step 3: Install Dependencies
```bash
# If using venv:
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Mac/Linux

# Install packages:
pip install -r requirements.txt
```

### Step 4: Add Your Dementia Documents
```bash
# Place PDFs and TXTs in data/ folder
cp your_dementia_guide.pdf data/
cp your_caregiving_handbook.txt data/
```

### Step 5: Build FAISS Index
```bash
python main.py --ingest
```
Expected output: Creates `vectorstore/` and `processed/` folders

### Step 6: Test in Terminal
```bash
python main.py --chat
```

Type dementia questions and test responses!

### Step 7: Start Server
```bash
python main.py --server
```
Server starts at: **http://127.0.0.1:5001**

---

## 📖 Usage Modes

### Mode 1: Ingest Documents
```bash
python main.py --ingest
```
- Reads all PDFs/TXTs from `data/`
- Creates chunks
- Builds FAISS vector index
- Saves metadata
- **Run this whenever you add new documents**

### Mode 2: Terminal Chat (Testing)
```bash
python main.py --chat
```
- Interactive chatbot in terminal
- Type questions
- Get responses with tone and sources
- Type `exit` to quit

### Mode 3: FastAPI Server
```bash
python main.py --server
```
- Starts REST API at localhost:5001
- Endpoints:
  - `POST /chat` — Send message, get response
  - `GET /health` — Check if running
  - `GET /docs` — Swagger documentation

---

## 🔌 API Integration

### REST API Example (cURL)
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is dementia?"}'
```

### Response
```json
{
  "reply": "Dementia is a general term for loss of memory and thinking ability...",
  "references": [
    {
      "text": "Dementia symptoms include...",
      "source": "dementia_guide.pdf",
      "page": 5
    }
  ],
  "tone_detected": "calm",
  "used_web_search": false,
  "is_on_topic": true
}
```

### React/Frontend Integration
```javascript
const response = await fetch('http://localhost:5001/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userInput })
});

const data = await response.json();
console.log(data.reply);
```

---

## 🔍 System Flow

```
User Input
    ↓
[1] Spell Check Node         → Auto-fix typos
    ↓
[2] Tone Detection Node      → Detect emotion
    ↓
[3] Topic Guard Node         → Block off-topic?
    ↓ (if on-topic)
[4] Retrieve Node            → FAISS search
    ↓
[5] Grade Documents Node     → Filter relevant
    ↓
[CONDITIONAL]
    ├─ No relevant docs → [6b] Web Search Node (DuckDuckGo)
    │
    └─ Has relevant docs → [6a] Generate Node
         ↓
         Paths meet here
         ↓
[7] Grade Answer Node        → Check hallucinations
    ↓
[8] Emotional Response Node  → Add warmth based on tone
    ↓
FINAL RESPONSE (with sources)
```

---

## 🛠️ Configuration

### Edit `config.py` to customize:

```python
# Document processing
CHUNK_SIZE = 800              # Bigger = fewer chunks
CHUNK_OVERLAP = 150           # Overlap between chunks
TOP_K_RETRIEVAL = 5           # Number of chunks to retrieve

# Embedding model
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # Free, 384-dim embeddings

# LLM settings
LLM_TEMPERATURE = 0           # 0 = deterministic, 1 = random
LLM_MAX_TOKENS = 2000         # Max response length

# Server
SERVER_HOST = '127.0.0.1'     # Change to '0.0.0.0' for external access
SERVER_PORT = 5001
```

---

## 📊 Project Statistics

| Component | Count | Status |
|-----------|-------|--------|
| Nodes | 8 | ✓ Complete |
| Graph edges | 11 | ✓ Complete |
| Configuration files | 3 | ✓ Complete |
| Entry points | 3 modes | ✓ Complete |
| API endpoints | 3 | ✓ Complete |
| External APIs | 2 | ✓ Configured |

**Total Lines of Code**: ~2000+ production-ready lines

---

## ⚡ Performance Tuning

### Faster Responses
```python
# In config.py
CHUNK_SIZE = 1000              # Larger chunks (fewer to process)
TOP_K_RETRIEVAL = 3            # Fewer chunks to retrieve
```

### Better Accuracy
```python
# In config.py
CHUNK_SIZE = 500               # Smaller chunks (more precise)
TOP_K_RETRIEVAL = 7            # More chunks to consider
CHUNK_OVERLAP = 250            # More overlap (more context)
```

### Reduce Token Usage (Lower Costs)
```python
# In config.py
LLM_MAX_TOKENS = 1000          # Shorter responses
```

---

## 🐛 Troubleshooting

### "MISTRAL_API_KEY not found"
- Edit `.env` file
- Add your API key: `MISTRAL_API_KEY=sk-xxxxx`
- Restart the server

### "Vectorstore not found"
- Run: `python main.py --ingest`
- Ensure `data/` folder has PDF/TXT files

### "ModuleNotFoundError: No module named 'langgraph'"
- Reinstall dependencies: `pip install -r requirements.txt`

### "Port 5001 already in use"
- Use different port: `python main.py --server --port 8000`

### "LLM not responding"
- Check internet connection
- Verify API key is valid
- Check Mistral console for rate limits

### "Off-topic questions get no response"
- This is intentional! Topic guard blocks non-dementia questions
- Try: "Tell me about Alzheimer's disease"

---

## 🎯 Next Steps

### Customize for Your Use Case
1. **Add more documents** to `data/` folder
2. **Test with real users** in chat mode
3. **Tune parameters** in `config.py`
4. **Deploy server** to production

### Frontend Integration
- [React example](./examples/react-integration.md) (coming soon)
- REST API is ready at `/chat` endpoint
- All responses include sources and tone

### Monitoring
- Check server logs
- Monitor token usage in Mistral console
- Track response times

---

## 📚 File Reference

### Configuration
- `config.py` — All settings in one place
- `.env` — Environment variables (keep secret!)
- `requirements.txt` — Python dependencies

### Ingestion
- `ingestion.py` — Document processing pipeline
- `data/` — Your dementia documents

### Graph Nodes
- `graph/state.py` — Shared state object
- `graph/nodes/spell_check.py` — Typo fixing
- `graph/nodes/tone_detect.py` — Emotion detection
- `graph/nodes/topic_guard.py` — Topic filtering
- `graph/nodes/retrieve.py` — Vector search
- `graph/nodes/grade_documents.py` — Relevance grading
- `graph/nodes/generate.py` — Answer generation
- `graph/nodes/web_search.py` — Web fallback
- `graph/nodes/grade_answer.py` — Hallucination check
- `graph/nodes/emotional.py` — Tone wrapping
- `graph/graph.py` — Graph assembly

### Application
- `chatbot.py` — Chat handler class
- `server.py` — FastAPI server
- `main.py` — CLI entry point

---

## 💙 Support

This chatbot is built with ❤️ for dementia patients and caregivers.

**For issues or questions**:
1. Check this README
2. Review `PLAN.md` for architecture details
3. Check individual node files for documentation
4. Test with `python main.py --chat` first

---

## 📄 License

Free to use and modify for dementia care applications.

---

## 🎉 You're All Set!

Your NeuroCare AI chatbot is ready to help dementia patients and caregivers.

**Quick Start Summary**:
```bash
1. pip install -r requirements.txt
2. python main.py --ingest          # Build index
3. python main.py --chat             # Test
4. python main.py --server           # Deploy
```

Questions? Stuck? Check your document content in `data/` folder and run ingestion again.

**Good luck! 🧠💙**
