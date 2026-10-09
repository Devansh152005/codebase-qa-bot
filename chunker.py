import os
import os

CODE_EXTENSIONS = {
    # code
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".c", ".cpp",
    ".h", ".hpp", ".cs", ".rb", ".php", ".kt", ".swift", ".sh", ".sql",
    # config / docs / markup
    ".md", ".txt", ".yml", ".yaml", ".json", ".toml", ".html", ".css",
}
SPECIAL_FILENAMES = {"Dockerfile", "Makefile"}          # no extension
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__",
             "dist", "build", "target", ".next", ".idea"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "poetry.lock", "pnpm-lock.yaml"}
MAX_FILE_SIZE = 200_000   # bytes

def read_python_files(repo_path: str) -> list[dict]:
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if name in SKIP_FILES or name.endswith(".min.js"):
                continue
            if ext not in CODE_EXTENSIONS and name not in SPECIAL_FILENAMES:
                continue
            full_path = os.path.join(root, name)
            if os.path.getsize(full_path) > MAX_FILE_SIZE:
                continue
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                continue          # binary or unreadable file
            if not content.strip():
                continue
            files.append({
                "file_path": os.path.relpath(full_path, repo_path),
                "content": content,
                "extension": ext or name,
            })
    return files

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