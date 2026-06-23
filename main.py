from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import git
import os
from chunker import read_python_files, chunk_code
from vector_store import embed_and_store, query_similar_chunks
from llm import generate_answer

app = FastAPI(
    title="Codebase QA Bot",
    description="Ask natural language questions about any GitHub repository",
    version="1.0.0"
)


class RepoRequest(BaseModel):
    repo_url: str


class QueryRequest(BaseModel):
    repo_name: str
    question: str
    top_k: int = 5


class AskRequest(BaseModel):
    repo_name: str
    question: str
    top_k: int = 5


@app.get("/")
def home():
    return {"message": "Codebase QA Bot is running!", "version": "1.0.0"}


@app.post("/ingest")
def ingest_repo(request: RepoRequest):
    try:
        if not request.repo_url.startswith("https://github.com"):
            raise HTTPException(status_code=400, detail="Only GitHub URLs are supported")

        repo_name = request.repo_url.split("/")[-1].replace(".git", "")
        clone_path = f"./repos/{repo_name}"

        if not os.path.exists(clone_path):
            print(f"Cloning {request.repo_url}...")
            git.Repo.clone_from(request.repo_url, clone_path)
        else:
            print(f"Repo already exists, skipping clone.")

        files_data = read_python_files(clone_path)

        if not files_data:
            raise HTTPException(status_code=404, detail="No Python files found in this repository")

        chunks = chunk_code(files_data)
        stored = embed_and_store(chunks, repo_name)

        return {
            "repo": repo_name,
            "files_found": len(files_data),
            "chunks_stored": stored,
            "status": "ingestion complete"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/query")
def query_repo(request: QueryRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        results = query_similar_chunks(
            query=request.question,
            repo_name=request.repo_name,
            top_k=request.top_k
        )

        if not results:
            raise HTTPException(status_code=404, detail="No chunks found — has this repo been ingested?")

        return {
            "question": request.question,
            "repo": request.repo_name,
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/ask")
def ask_question(request: AskRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        chunks = query_similar_chunks(
            query=request.question,
            repo_name=request.repo_name,
            top_k=request.top_k
        )

        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant chunks found — has this repo been ingested?")

        answer = generate_answer(request.question, chunks)

        return {
            "question": request.question,
            "repo": request.repo_name,
            "answer": answer,
            "sources": list(set([c["file_path"] for c in chunks]))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")