"""
GenVendorAI Search Routes
Endpoints for natural-language semantic vector retrieval across the vendor knowledge base.
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from ai.semantic_search import semantic_search_vendors

router = APIRouter(prefix="/api/search", tags=["Semantic Search"])


class SemanticSearchRequest(BaseModel):
    query: str
    min_similarity: float = 0.20
    category: Optional[str] = "All"
    top_k: int = 10


@router.post("/semantic")
def search_vendors_endpoint(req: SemanticSearchRequest):
    """Performs natural-language semantic vector search using SBERT + FAISS."""
    if not req.query.strip():
        return {"query": req.query, "total": 0, "results": []}

    results = semantic_search_vendors(
        query=req.query,
        top_k=req.top_k,
        min_similarity=req.min_similarity,
        category_filter=req.category if req.category != "All" else None
    )

    return {
        "query": req.query,
        "total": len(results),
        "results": results
    }
