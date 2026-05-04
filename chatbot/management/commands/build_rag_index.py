"""
Management command: python manage.py build_rag_index

Loads all Markdown files from chatbot/knowledge_base/, embeds them
using OpenAI text-embedding-3-small, and saves the FAISS index to
chatbot/rag/faiss_index/. Safe to run repeatedly — rebuilds from scratch.
"""
from django.core.management.base import BaseCommand
from chatbot.rag.embeddings import build_index, INDEX_DIR
from chatbot.rag.loader import KNOWLEDGE_BASE_DIR


class Command(BaseCommand):
    help = 'Build (or rebuild) the FAISS vector index from the knowledge base Markdown files.'

    def handle(self, *args, **options):
        self.stdout.write('Building RAG index...')
        md_files = list(KNOWLEDGE_BASE_DIR.glob('*.md'))
        if not md_files:
            self.stderr.write(self.style.ERROR(
                f'No .md files found in {KNOWLEDGE_BASE_DIR}. Aborting.'
            ))
            return

        self.stdout.write(f'  Found {len(md_files)} knowledge base file(s):')
        for f in md_files:
            self.stdout.write(f'    · {f.name}')

        store = build_index()
        self.stdout.write(self.style.SUCCESS(
            f'  Index saved to {INDEX_DIR} ({store.index.ntotal} vectors)'
        ))
