# NeuroCare AI v2 — Implementation Plan

**Project**: Agentic RAG Chatbot for Dementia Care  
**Version**: 2.0  
**Duration**: 5 Days  
**Status**: In Progress

---

## 📋 Project Overview

NeuroCare AI is a domain-restricted Agentic RAG chatbot built with:
- **LangGraph**: Multi-node intelligent pipeline
- **Mistral AI**: Free LLM (or OpenAI alternative)
- **FAISS**: Vector search on local documents
- **FastAPI**: REST API for React frontend

### Core Features
✅ Spell check & auto-correction  
✅ Emotional tone detection  
✅ Topic guard (dementia-only)  
✅ FAISS document retrieval  
✅ Hallucination prevention  
✅ Emotionally aware responses  
✅ Source attribution  

---

## 🗂️ Project Structure

```
neurocare-chatbot/
├── data/                          ← Your PDFs/TXTs
├── vectorstore/                   ← Auto-created FAISS index
├── processed/                     ← Auto-created chunks.jsonl
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── graph.py
│   └── nodes/
│       ├── __init__.py
│       ├── spell_check.py
│       ├── tone_detect.py
│       ├── topic_guard.py
│       ├── retrieve.py
│       ├── grade_documents.py
│       ├── generate.py
│       ├── web_search.py
│       ├── grade_answer.py
│       └── emotional.py
├── ingestion.py
├── chatbot.py
├── server.py
├── llm_factory.py
├── config.py
├── main.py
├── requirements.txt
├── .env
└── PLAN.md
```

---

## 📅 Implementation Phases

### Phase 1: Setup & LLM Factory (Day 1) — 🟨 NOT STARTED
**Objective**: Set up environment and verify LLM is working

**Tasks**:
- [ ] Create `requirements.txt` with all dependencies
- [ ] Create `.env` file with Mistral API key
- [ ] Create `config.py` with all settings
- [ ] Create `llm_factory.py` to load Mistral/OpenAI
- [ ] Create `data/` folder
- [ ] Test: `python -c "from llm_factory import get_llm; print(get_llm().invoke('test'))"`

**Deliverables**: 
- requirements.txt
- .env (with Mistral key)
- config.py
- llm_factory.py

**Status**: ⏳ READY TO START

---

### Phase 2: Document Ingestion (Day 1-2) — 🟨 NOT STARTED
**Objective**: Process documents into FAISS vector index

**Tasks**:
- [ ] Create `ingestion.py` with document loading
- [ ] Create `main.py` with CLI (--ingest flag)
- [ ] Add sample PDFs to `data/` folder
- [ ] Run ingestion: `python main.py --ingest`
- [ ] Verify `vectorstore/index.faiss` is created

**Deliverables**:
- ingestion.py
- main.py (phase 1)
- data/ folder (with documents)
- Auto-created: vectorstore/, processed/

**Status**: ⏳ READY TO START

---

### Phase 3: LangGraph State & Nodes 1-4 (Day 2-3) — 🟨 NOT STARTED
**Objective**: Build spell check, tone detection, topic guard, retrieval nodes

**Nodes to create**:
1. **Spell Check Node** — Auto-fix all typos
2. **Tone Detection Node** — Detect: anxious/sad/frustrated/confused/calm
3. **Topic Guard Node** — Block off-topic questions
4. **Retrieve Node** — FAISS semantic search

**Tasks**:
- [ ] Create `graph/__init__.py`
- [ ] Create `graph/state.py` with AgentState class
- [ ] Create `graph/nodes/__init__.py`
- [ ] Create `graph/nodes/spell_check.py`
- [ ] Create `graph/nodes/tone_detect.py`
- [ ] Create `graph/nodes/topic_guard.py`
- [ ] Create `graph/nodes/retrieve.py`
- [ ] Test each node individually

**Deliverables**:
- graph/state.py
- All 4 node files
- Passing unit tests

**Status**: ⏳ READY TO START

---

### Phase 4: Nodes 5-8 & Graph Assembly (Day 3-4) — 🟨 NOT STARTED
**Objective**: Build grading, generation, web search, emotional nodes + assemble LangGraph

**Nodes to create**:
5. **Grade Documents Node** — Relevance filtering
6. **Generate Node** — Answer generation
7. **Web Search Node** — DuckDuckGo fallback
8. **Emotional Node** — Tone-aware response wrapping
9. **Graph Assembly** — Connect all nodes

**Tasks**:
- [ ] Create `graph/nodes/grade_documents.py`
- [ ] Create `graph/nodes/generate.py`
- [ ] Create `graph/nodes/web_search.py`
- [ ] Create `graph/nodes/grade_answer.py`
- [ ] Create `graph/nodes/emotional.py`
- [ ] Create `graph/graph.py` — assemble graph with conditional edges
- [ ] Test full graph with sample queries

**Deliverables**:
- All 5 node files
- graph.py with complete LangGraph
- Passing integration tests

**Status**: ⏳ READY TO START

---

### Phase 5: Server, CLI & Frontend Integration (Day 4-5) — 🟨 NOT STARTED
**Objective**: Create REST API and complete CLI

**Tasks**:
- [ ] Create `chatbot.py` with ChatHandler class
- [ ] Create `server.py` with FastAPI endpoints
- [ ] Complete `main.py` with all CLI modes
- [ ] Test with Postman: POST /chat
- [ ] Run full system: `python main.py --server`

**Deliverables**:
- chatbot.py
- server.py
- Complete main.py
- API working at localhost:5001

**Status**: ⏳ READY TO START

---

## 🔧 Setup Prerequisites

### 1. Get Mistral API Key (FREE)
```
URL: https://console.mistral.ai
Sign up (no credit card needed)
Create API key (starts with: sk-)
```

### 2. Python Version
- Python 3.13+ recommended
- Virtual environment: `python -m venv venv`

### 3. Installation Command (Phase 1)
```bash
pip install langgraph langchain langchain-community langchain-mistralai langchain-openai faiss-cpu sentence-transformers duckduckgo-search pypdf python-dotenv pyspellchecker fastapi uvicorn pydantic tqdm torch httpx
```

---

## ✅ Testing Strategy

### Phase 1 Test
```bash
python -c "from llm_factory import get_llm; llm = get_llm(); print(llm.invoke('Hello'))"
```
**Expected**: LLM responds with text (proves API key works)

### Phase 2 Test
```bash
python main.py --ingest
ls vectorstore/
```
**Expected**: `index.faiss` and `index.pkl` files exist

### Phase 3 Test
```bash
python -c "
from graph.nodes.spell_check import spell_check_node
from graph.state import AgentState
state = AgentState(question='wht is demnetia')
result = spell_check_node(state)
print(result.corrected_question)
"
```
**Expected**: `corrected_question` is 'what is dementia'

### Phase 4 Test
```bash
python main.py --chat
```
**Expected**: Chat works in terminal, asks for user input

### Phase 5 Test
```bash
python main.py --server
# In another terminal:
curl -X POST http://localhost:5001/chat -H "Content-Type: application/json" -d '{"message": "What is dementia?"}'
```
**Expected**: JSON response with reply, tone, sources

---

## 📊 Current Progress

| Phase | Status | Completion | Start Date | End Date |
|-------|--------|------------|-----------|----------|
| Phase 1: Setup | 🟨 Ready | 0% | - | - |
| Phase 2: Ingestion | 🟨 Ready | 0% | - | - |
| Phase 3: Nodes 1-4 | 🟨 Ready | 0% | - | - |
| Phase 4: Nodes 5-8 | 🟨 Ready | 0% | - | - |
| Phase 5: Server | 🟨 Ready | 0% | - | - |

---

## 🚀 Next Steps

**Start with Phase 1**: Create all environment and configuration files.  
**Estimated time**: 30 minutes  
**Success metric**: LLM responds to test input

