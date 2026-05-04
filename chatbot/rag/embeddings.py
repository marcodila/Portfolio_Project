"""
Manages the FAISS vector index: build from scratch or load from disk.

The index is persisted to chatbot/rag/faiss_index/ (gitignored).
Call build_index() once at deploy time via the build_rag_index management command.
At runtime, load_index() returns the cached store; subsequent calls are instant
because the module-level _index variable is reused within the same process.
"""
import os
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from .loader import load_documents

INDEX_DIR = Path(__file__).resolve().parent / 'faiss_index'

_index: FAISS | None = None


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Lazily construct the embeddings client so import-time validation is avoided."""
    return GoogleGenerativeAIEmbeddings(
        model='models/gemini-embedding-001',
        google_api_key=os.environ.get('GEMINI_KEY', ''),
    )


def build_index() -> FAISS:
    """Load knowledge base docs, embed them, persist to INDEX_DIR, return the store."""
    global _index
    docs = load_documents()
    store = FAISS.from_documents(docs, _get_embeddings())
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(INDEX_DIR))
    _index = store
    return store


def load_index() -> FAISS:
    """Return the FAISS index, loading from disk if not already in memory."""
    global _index
    if _index is not None:
        return _index

    embeddings = _get_embeddings()

    if INDEX_DIR.exists():
        _index = FAISS.load_local(
            str(INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        return _index

    return build_index()
