# Codebase QA Bot

A RAG-powered backend that lets you ask natural language questions about any GitHub repository.

## How it works

```
GitHub Repo → Clone → Chunk → Embed → ChromaDB → Retrieve → LLM → Answer
```

1. `/ingest` clones a GitHub repo, chunks all `.py` files, embeds them using `all-MiniLM-L6-v2`, and stores in ChromaDB
2. `/ask` embeds your question, retrieves the top-k similar chunks, and generates an answer using Llama 3 via Groq

## Tech Stack

- **FastAPI** — REST API framework
- **ChromaDB** — local vector database
- **SentenceTransformers** — local embedding model (all-MiniLM-L6-v2)
- **Groq + Llama 3** — LLM for answer generation
- **GitPython** — programmatic repo cloning

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/codebase-qa-bot
cd codebase-qa-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_key_here
```

Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/ingest` | Clone and index a GitHub repo |
| POST | `/query` | Get raw similar chunks for a question |
| POST | `/ask` | Get a full LLM-generated answer |

## Example Usage

**Ingest a repo:**
```json
POST /ingest
{
  "repo_url": "https://github.com/tiangolo/fastapi"
}
```

**Ask a question:**
```json
POST /ask
{
  "repo_name": "fastapi",
  "question": "How does FastAPI handle request routing?",
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "How does FastAPI handle request routing?",
  "repo": "fastapi",
  "answer": "FastAPI handles routing through the APIRouter class in routing.py...",
  "sources": ["./repos/fastapi/fastapi/routing.py"]
}
```

## Design Decisions

- **Chunking by lines with overlap** — 30 lines per chunk, 5 line overlap ensures no function is split without context
- **Local embeddings** — no API cost or latency for embedding, runs fully offline
- **Separate `/query` and `/ask`** — allows debugging retrieval quality independently from generation quality
- **One ChromaDB collection per repo** — keeps search scoped, prevents cross-repo noise