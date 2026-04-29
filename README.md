# NeuroCare AI

NeuroCare AI is an agentic RAG chatbot for dementia care. It combines document retrieval, response validation, topic filtering, tone-aware replies, and web fallback search to deliver grounded answers for patients, caregivers, and healthcare-related use cases.

## Features

- Dementia-focused question answering
- FAISS-based document retrieval
- LangGraph multi-step agent pipeline
- Spell correction and tone detection
- Off-topic filtering
- Answer grounding and hallucination checks
- FastAPI server for frontend integration

## Tech Stack

- Python
- LangGraph
- FAISS
- FastAPI
- Mistral or OpenAI
- Local embedding model: `all-MiniLM-L6-v2`

## Project Structure

```text
agentic-rag-chatbot/
├── data/                  # Source documents (PDF/TXT)
├── graph/                 # LangGraph state, graph, and nodes
├── processed/             # Generated chunk metadata
├── vectorstore/           # Generated FAISS index
├── chatbot.py             # Chat handler
├── ingestion.py           # Document ingestion pipeline
├── main.py                # CLI entry point
├── server.py              # FastAPI server
├── config.py              # Central configuration
└── requirements.txt       # Python dependencies
```

## Step-by-Step Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd agentic-rag-chatbot
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your provider settings.

Example for Mistral:

```env
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_mistral_api_key
```

Example for OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
```

### 5. Add your documents

Place your dementia-related PDF or TXT files inside the `data/` folder.

### 6. Build the vector index

```bash
python main.py --ingest
```

This command:

- loads documents from `data/`
- splits them into chunks
- creates embeddings
- builds the FAISS index

### 7. Run the chatbot in terminal mode

```bash
python main.py --chat
```

### 8. Run the API server

```bash
python main.py --server
```

Default server URL:

```text
http://127.0.0.1:5001
```

## Usage Modes

### Ingest documents

```bash
python main.py --ingest
```

### Start terminal chat

```bash
python main.py --chat
```

### Start API server

```bash
python main.py --server
```

### Start server on a custom host and port

```bash
python main.py --server --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - API info
- `GET /health` - health check
- `GET /docs` - Swagger UI
- `POST /chat` - chatbot response

Example request:

```bash
curl -X POST http://127.0.0.1:5001/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"What is dementia?\"}"
```

## Recommended Workflow

1. Clone the project.
2. Create a virtual environment.
3. Install dependencies.
4. Add API credentials in `.env`.
5. Put source documents in `data/`.
6. Run `python main.py --ingest`.
7. Test with `python main.py --chat`.
8. Start the backend with `python main.py --server`.

## Notes

- Re-run ingestion whenever you add or update documents.
- The chatbot is designed for dementia-related queries.
- Generated folders such as `vectorstore/` and `processed/` are created after ingestion.

## License

This project is available for educational and research use.
