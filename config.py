from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
EXTRACTED_DIR = BASE_DIR / "extracted_docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "documind_documents"

# Chunk sizes are measured using the embedding model's tokenizer.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 5
