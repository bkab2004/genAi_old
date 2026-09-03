"""
GenVendorAI AI & Risk Intelligence Package
Provides vector embeddings, FAISS similarity search, semantic query matching, and explainable risk assessment.
"""

from ai.embeddings import get_embedding_model, generate_embedding, get_vendor_embedding_text
from ai.vector_store import (
    init_vector_store,
    add_vendor_to_index,
    search_similar_vendors,
    rebuild_vector_index,
    get_vector_store_stats
)
from ai.semantic_search import semantic_search_vendors
from ai.risk_engine import generate_vendor_risk_assessment

__all__ = [
    "get_embedding_model",
    "generate_embedding",
    "get_vendor_embedding_text",
    "init_vector_store",
    "add_vendor_to_index",
    "search_similar_vendors",
    "rebuild_vector_index",
    "get_vector_store_stats",
    "semantic_search_vendors",
    "generate_vendor_risk_assessment"
]
