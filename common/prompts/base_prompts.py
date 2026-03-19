"""
base_prompts.py — General-purpose prompt templates for common agentic patterns.
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# ─── Simple Q&A ──────────────────────────────────────────────────────────────
QA_PROMPT = PromptTemplate.from_template(
    "Answer the following question concisely and accurately.\n\nQuestion: {question}\n\nAnswer:"
)

# ─── RAG (Retrieval-Augmented Generation) ────────────────────────────────────
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant. Answer the user's question using ONLY the "
     "provided context. If the context does not contain enough information, say "
     "'I don't have enough information to answer that.'\n\nContext:\n{context}"),
    ("human", "{question}"),
])

# ─── ReAct Agent ─────────────────────────────────────────────────────────────
REACT_SYSTEM_PROMPT = (
    "You are an intelligent assistant with access to tools. "
    "Think step by step, use tools when needed, and provide a clear final answer."
)
