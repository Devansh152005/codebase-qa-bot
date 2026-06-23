import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

# Load embedding model once (runs locally, no API key needed)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB with a local persistent folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def get_or_create_collection(repo_name: str):
    """
    Each repo gets its own collection in ChromaDB.
    Like a separate table per repo.
    """
    collection = chroma_client.get_or_create_collection(
        name=repo_name.replace("-", "_").replace(".", "_")
    )
    return collection


def embed_and_store(chunks: list[dict], repo_name: str) -> int:
    """
    Takes chunks, embeds them, and stores in ChromaDB.
    Returns number of chunks stored.
    """
    collection = get_or_create_collection(repo_name)

    # Prepare data for ChromaDB
    ids = []
    embeddings = []
    documents = []
    metadatas = []

    print(f"Embedding {len(chunks)} chunks... this may take a minute.")

    for chunk in chunks:
        # Generate embedding for this chunk
        embedding = embedding_model.encode(chunk["content"]).tolist()

        ids.append(chunk["chunk_id"])
        embeddings.append(embedding)
        documents.append(chunk["content"])
        metadatas.append({
            "file_path": chunk["file_path"],
            "chunk_index": chunk["chunk_index"]
        })

    # Store everything in ChromaDB in one batch
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB under collection '{repo_name}'")
    return len(chunks)


def query_similar_chunks(query: str, repo_name: str, top_k: int = 5) -> list[dict]:
    """
    Takes a natural language query, embeds it,
    and returns the top_k most similar chunks from the repo.
    """
    collection = get_or_create_collection(repo_name)

    # Embed the query using the same model
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # Format results nicely
    similar_chunks = []
    for i in range(len(results["ids"][0])):
        similar_chunks.append({
            "chunk_id": results["ids"][0][i],
            "content": results["documents"][0][i],
            "file_path": results["metadatas"][0][i]["file_path"],
            "distance": results["distances"][0][i]
        })

    return similar_chunks