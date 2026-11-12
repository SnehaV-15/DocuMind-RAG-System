
"""DocuMind: document retrieval and Gemini answer generation."""

import os
import time

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K
)

load_dotenv()

_embedding_model = None
_collection = None
_gemini_client = None


def get_gemini_client():
    """Initialize and return the Gemini client."""

    global _gemini_client

    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Check your .env file."
            )

        _gemini_client = genai.Client(api_key=api_key)

    return _gemini_client


def generate_with_retry(prompt, max_retries=3):
    """Generate a Gemini response with retries for temporary server errors."""

    client = get_gemini_client()
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model_name,
                contents=prompt
            )

        except Exception as exc:
            error = str(exc).lower()

            temporary_error = (
                "503" in error
                or "unavailable" in error
                or "high demand" in error
            )

            if not temporary_error or attempt == max_retries - 1:
                raise

            wait_time = 2 ** (attempt + 1)

            print(
                f"Gemini temporarily unavailable. "
                f"Retry {attempt + 1}/{max_retries - 1} "
                f"in {wait_time} seconds..."
            )

            time.sleep(wait_time)


def get_resources():
    """Initialize the embedding model and ChromaDB collection."""

    global _embedding_model, _collection

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        _embedding_model.max_seq_length = 512

    if _collection is None:
        db = chromadb.PersistentClient(path=str(CHROMA_DIR))

        try:
            _collection = db.get_collection(COLLECTION_NAME)
        except Exception as exc:
            raise RuntimeError(
                "ChromaDB collection not found. Upload a PDF or run ingestion."
            ) from exc

    return _embedding_model, _collection


def refresh_collection():
    """Refresh the collection after uploading and indexing a PDF."""

    global _collection

    db = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        _collection = db.get_collection(COLLECTION_NAME)
    except Exception:
        _collection = db.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    return _collection


def retrieve(question, top_k=TOP_K):
    """Retrieve relevant document chunks from ChromaDB."""

    model, collection = get_resources()

    count = collection.count()

    if count == 0:
        return []

    query_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    )[0].tolist()

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []

    for doc, meta, distance in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0]
    ):
        retrieved.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "chunk": meta.get("chunk", "?"),
            "distance": round(float(distance), 4)
        })

    return retrieved


def answer_with_rag(question):
    """Generate an answer using retrieved document context."""

    chunks = retrieve(question)

    if not chunks:
        return {
            "answer": (
                "No document information is available. "
                "Please upload a PDF first."
            ),
            "sources": []
        }

    context = "\n\n".join(
        f"[Source: {item['source']}, chunk {item['chunk']}]\n"
        f"{item['text']}"
        for item in chunks
    )

    prompt = f"""
You are DocuMind, a document question-answering assistant.

Answer the user's question using ONLY the supplied document context.

If the answer is not present in the context, say:
"I couldn't find that information in the provided documents."

Do not invent facts or use outside knowledge.
Mention the source filename when possible.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

GROUNDED ANSWER:
"""

    response = generate_with_retry(prompt)

    return {
        "answer": response.text or "The model returned an empty response.",
        "sources": chunks
    }


def answer_without_rag(question):
    """Generate a baseline answer without retrieving document context."""

    prompt = f"""
Answer the following question using your general knowledge only.

You have NOT been given any of the user's uploaded documents.
Do not claim to have read or searched any documents.

QUESTION:
{question}

ANSWER:
"""

    response = generate_with_retry(prompt)

    return response.text or "The model returned an empty response."
