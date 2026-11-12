
"""Chunk extracted documents and store embeddings in ChromaDB."""

import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    EXTRACTED_DIR,
    CHROMA_DIR,
    EMBEDDING_MODEL,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


def split_into_token_chunks(
    text,
    tokenizer,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):
    """Split long text into overlapping token chunks."""

    if chunk_size < 1:
        raise ValueError("CHUNK_SIZE must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "CHUNK_OVERLAP must be smaller than CHUNK_SIZE."
        )

    # Tokenize the document without truncating it.
    # Overflow windows prevent oversized model inputs.
    encoded = tokenizer(
        text,
        add_special_tokens=False,
        truncation=True,
        max_length=chunk_size,
        stride=overlap,
        return_overflowing_tokens=True
    )

    chunks = []

    for token_ids in encoded["input_ids"]:

        piece = tokenizer.decode(
            token_ids,
            skip_special_tokens=True
        ).strip()

        if piece:
            chunks.append(piece)

    return chunks


def ingest_documents():
    """Extract chunks, generate embeddings and store them in ChromaDB."""

    files = sorted(EXTRACTED_DIR.glob("*.txt"))

    if not files:
        raise RuntimeError("No extracted documents found.")

    print("Loading embedding model...")

    model = SentenceTransformer(EMBEDDING_MODEL)

    model.max_seq_length = 512

    tokenizer = model.tokenizer

    if CHUNK_SIZE > model.max_seq_length:
        raise ValueError(
            f"Chunk size {CHUNK_SIZE} exceeds "
            f"model limit {model.max_seq_length}."
        )

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    all_chunks = []
    all_ids = []
    all_metadata = []

    # Process every extracted document.
    for file_path in files:

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        chunks = split_into_token_chunks(
            text,
            tokenizer
        )

        print(
            f"{file_path.name}: {len(chunks)} chunks"
        )

        for index, chunk in enumerate(chunks):

            digest = hashlib.md5(
                f"{file_path.name}:{index}:{chunk}".encode("utf-8")
            ).hexdigest()

            all_ids.append(digest)
            all_chunks.append(chunk)

            all_metadata.append({
                "source": file_path.name,
                "chunk": index + 1
            })

    if not all_chunks:
        raise RuntimeError("No text chunks found.")

    print(
        f"Creating embeddings for {len(all_chunks)} chunks..."
    )

    embeddings = model.encode(
        all_chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    # All embeddings are generated before modifying the database.
    # This prevents deletion of old chunks if embedding generation fails.

    current_sources = {
        file_path.name for file_path in files
    }

    print("Updating ChromaDB records...")

    # Remove old records for documents being re-ingested.
    for source in current_sources:

        collection.delete(
            where={"source": source}
        )

    # Insert new chunks in batches.
    batch_size = 100

    for start in range(0, len(all_chunks), batch_size):

        end = min(start + batch_size, len(all_chunks))

        collection.upsert(
            ids=all_ids[start:end],
            documents=all_chunks[start:end],
            metadatas=all_metadata[start:end],
            embeddings=embeddings[start:end].tolist()
        )

    total = collection.count()

    print("\nIngestion completed successfully.")
    print(f"Documents processed: {len(files)}")
    print(f"New chunks generated: {len(all_chunks)}")
    print(f"Total chunks in ChromaDB: {total}")

    return total


def main():
    ingest_documents()


if __name__ == "__main__":
    main()
