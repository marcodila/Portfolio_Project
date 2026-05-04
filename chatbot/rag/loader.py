"""
Loads Markdown knowledge base files and splits them into chunks
suitable for embedding and retrieval.
"""
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent / 'knowledge_base'

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=['\n\n', '\n', '. ', ' ', ''],
)


def load_documents():
    """Return a list of LangChain Document objects from all .md files."""
    docs = []
    for md_file in sorted(KNOWLEDGE_BASE_DIR.glob('*.md')):
        loader = TextLoader(str(md_file), encoding='utf-8')
        raw = loader.load()
        chunks = _SPLITTER.split_documents(raw)
        docs.extend(chunks)
    return docs
