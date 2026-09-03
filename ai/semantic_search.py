"""
GenVendorAI Semantic Search Module
Executes natural-language search over the vendor knowledge base, combining vector retrieval with database metadata.
"""

from typing import List, Dict, Any, Optional
from ai.vector_store import search_similar_vendors
from database.database import get_all_vendors_df, get_vendor_by_gstin


def semantic_search_vendors(
    query: str,
    top_k: int = 10,
    min_similarity: float = 0.20,
    category_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Performs natural language semantic search across all indexed vendors.
    
    Args:
        query: Natural language query (e.g., 'IT software companies in Pune', 'reliable logistics suppliers').
        top_k: Number of search results to return.
        min_similarity: Minimum similarity score threshold (0.0 to 1.0).
        category_filter: Optional category restriction.
        
    Returns:
        List of enriched vendor match records.
    """
    if not query or not query.strip():
        return []

    # 1. Search vector store
    raw_results = search_similar_vendors(query, top_k=top_k * 2, threshold=min_similarity)

    # 2. Enrich with database records
    enriched = []
    for item in raw_results:
        vendor_meta = item.get("vendor", {})
        sim = item.get("similarity", 0.0)
        tier = item.get("tier", "Low")
        
        # Check category filter if provided
        cat = vendor_meta.get("Business Category") or vendor_meta.get("business_category", "")
        if category_filter and category_filter.lower() != "all":
            if category_filter.lower() not in cat.lower():
                continue

        # Look up live DB record for latest risk & recommendation
        gstin = vendor_meta.get("GSTIN") or vendor_meta.get("gstin", "")
        db_rec = get_vendor_by_gstin(gstin) if gstin else None

        record = {
            "Vendor Name": (db_rec.get("vendor_name") if db_rec else None) or vendor_meta.get("Vendor Name") or vendor_meta.get("vendor_name", "Unknown"),
            "Business Category": (db_rec.get("business_category") if db_rec else None) or cat or "General",
            "Address": (db_rec.get("address") if db_rec else None) or vendor_meta.get("Address") or "N/A",
            "GSTIN": gstin or "N/A",
            "PAN": (db_rec.get("pan") if db_rec else None) or vendor_meta.get("PAN") or "N/A",
            "Contact Person": (db_rec.get("contact_person") if db_rec else None) or vendor_meta.get("Contact Person") or "N/A",
            "Phone": (db_rec.get("phone") if db_rec else None) or vendor_meta.get("Phone") or "N/A",
            "Email": (db_rec.get("email") if db_rec else None) or vendor_meta.get("Email") or "N/A",
            "Bank Name": (db_rec.get("bank_name") if db_rec else None) or vendor_meta.get("Bank Name") or "N/A",
            "Risk Score": db_rec.get("risk_score", 0) if db_rec else vendor_meta.get("risk_score", 0),
            "Risk Level": db_rec.get("risk_level", "UNKNOWN") if db_rec else vendor_meta.get("risk_level", "UNKNOWN"),
            "Recommendation": db_rec.get("recommendation", "REVIEW") if db_rec else vendor_meta.get("recommendation", "REVIEW"),
            "Validation Status": db_rec.get("validation_status", "VALID") if db_rec else "VALID",
            "Similarity Score": sim,
            "Similarity Pct": f"{sim:.1%}",
            "Similarity Tier": tier
        }
        enriched.append(record)
        if len(enriched) >= top_k:
            break

    return enriched
