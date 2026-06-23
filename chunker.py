import os

def read_python_files(repo_path: str) -> list[dict]:
    """
    Walks through a cloned repo and reads all .py files.
    Returns a list of dicts with file path and raw content.
    """
    files_data = []

    for root, dirs, files in os.walk(repo_path):
        # Skip hidden folders like .git
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    files_data.append({
                        "file_path": file_path,
                        "content": content
                    })
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    return files_data
def chunk_code(files_data: list[dict], chunk_size: int = 30, overlap: int = 5) -> list[dict]:
    """
    Splits each file's content into overlapping chunks of lines.
    
    chunk_size = number of lines per chunk
    overlap = how many lines are repeated between chunks (for context continuity)
    """
    all_chunks = []

    for file in files_data:
        lines = file["content"].splitlines()
        total_lines = len(lines)

        start = 0
        chunk_index = 0

        while start < total_lines:
            end = min(start + chunk_size, total_lines)
            chunk_lines = lines[start:end]
            chunk_text = "\n".join(chunk_lines)

            # Skip empty chunks
            if chunk_text.strip():
                all_chunks.append({
                    "chunk_id": f"{file['file_path']}::chunk_{chunk_index}",
                    "file_path": file["file_path"],
                    "chunk_index": chunk_index,
                    "content": chunk_text
                })
                chunk_index += 1

            start += chunk_size - overlap  # overlap creates continuity

    return all_chunks