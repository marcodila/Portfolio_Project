"""
LangChain RAG chain for the portfolio chatbot (LCEL implementation).

Uses LangChain Expression Language instead of the deprecated RetrievalQA,
which is compatible with LangChain 0.2+ including 1.x.
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from .embeddings import load_index

_PROMPT = ChatPromptTemplate.from_template(
    """You are an AI assistant embedded in Marco Di Laudo's professional portfolio website.
Your job is to help visitors learn about Marco's background, projects, and skills, and to guide them around the site.
Answer questions in a friendly, professional tone. Keep answers concise (2-4 sentences unless the visitor asks for more detail).
If you don't know something, say so honestly — never fabricate information about Marco.
Only answer based on the context provided below.

Context:
{context}

Question: {question}

Answer:"""
)

_chain = None


def _format_docs(docs) -> str:
    return '\n\n'.join(doc.page_content for doc in docs)


def _build_chain():
    llm = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash',
        temperature=0.3,
        google_api_key=os.environ.get('GEMINI_KEY', ''),
    )
    retriever = load_index().as_retriever(
        search_type='similarity',
        search_kwargs={'k': 4},
    )
    # LCEL chain: retrieve → format → prompt → LLM → parse
    chain = (
        {'context': retriever | _format_docs, 'question': RunnablePassthrough()}
        | _PROMPT
        | llm
        | StrOutputParser()
    )
    return chain


def ask(question: str) -> str:
    """Run the RAG chain and return a text answer."""
    global _chain
    if _chain is None:
        _chain = _build_chain()
    return _chain.invoke(question)
