"""
GenVendorAI Vector Store Module
Manages the FAISS vector index and vendor metadata mappings for semantic similarity search and deduplication.
"""

import os
import pickle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from ai.embeddings import generate_embedding, get_vendor_embedding_text, EMBEDDING_DIM

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DIR = os.path.join(BASE_DIR, "vector_db")
FAISS_INDEX_PATH = os.path.join(VECTOR_DIR, "vendor_index.faiss")
METADATA_PATH = os.path.join(VECTOR_DIR, "vendor_metadata.pkl")

# In-memory globals
_FAISS_INDEX = None
_METADATA_STORE: List[Dict[str, Any]] = []
_FALLBACK_VECTORS: Optional[np.ndarray] = None


def _load_or_create_index():
    """Loads existing FAISS index and metadata or creates a new empty one."""
    global _FAISS_INDEX, _METADATA_STORE, _FALLBACK_VECTORS
    os.makedirs(VECTOR_DIR, exist_ok=True)

    # 1. Load Metadata
    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "rb") as f:
                _METADATA_STORE = pickle.load(f)
        except Exception as e:
            print(f"[VectorStore] Failed to load metadata: {e}")
            _METADATA_STORE = []
    else:
        _METADATA_STORE = []

    # 2. Load FAISS Index
    try:
        import faiss
        if os.path.exists(FAISS_INDEX_PATH):
            _FAISS_INDEX = faiss.read_index(FAISS_INDEX_PATH)
        else:
            # IndexFlatIP with normalized vectors computes Cosine Similarity directly
            _FAISS_INDEX = faiss.IndexFlatIP(EMBEDDING_DIM)
    except Exception as e:
        print(f"[VectorStore] FAISS not available or load failed ({e}). Using Numpy Vector Matrix fallback.")
        _FAISS_INDEX = None
        if os.path.exists(FAISS_INDEX_PATH + ".npy"):
            try:
                _FALLBACK_VECTORS = np.load(FAISS_INDEX_PATH + ".npy")
            except Exception:
                _FALLBACK_VECTORS = None


def init_vector_store():
    """Initializes the vector store."""
    _load_or_create_index()


def save_vector_store():
    """Persists FAISS index and metadata to disk."""
    global _FAISS_INDEX, _METADATA_STORE, _FALLBACK_VECTORS
    os.makedirs(VECTOR_DIR, exist_ok=True)
    
    # Save metadata
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(_METADATA_STORE, f)

    # Save index
    try:
        import faiss
        if _FAISS_INDEX is not None:
            faiss.write_index(_FAISS_INDEX, FAISS_INDEX_PATH)
    except Exception:
        if _FALLBACK_VECTORS is not None:
            np.save(FAISS_INDEX_PATH + ".npy", _FALLBACK_VECTORS)


def add_vendor_to_index(vendor_data: Dict[str, Any]) -> int:
    """
    Computes embedding for vendor and inserts it into vector index and metadata store.
    Returns current total vector count.
    """
    global _FAISS_INDEX, _METADATA_STORE, _FALLBACK_VECTORS
    if _FAISS_INDEX is None and _FALLBACK_VECTORS is None:
        _load_or_create_index()

    text_to_embed = get_vendor_embedding_text(vendor_data)
    embedding = generate_embedding(text_to_embed).reshape(1, -1)

    # Check if vendor already exists in metadata by GSTIN or Name to prevent duplicate vector slots
    gstin = str(vendor_data.get("GSTIN") or vendor_data.get("gstin") or "").strip().upper()
    existing_idx = None
    if gstin and gstin != "NOT AVAILABLE":
        for idx, m in enumerate(_METADATA_STORE):
            m_gst = str(m.get("GSTIN") or m.get("gstin") or "").strip().upper()
            if m_gst == gstin:
                existing_idx = idx
                break

    if existing_idx is not None:
        # Update existing metadata
        _METADATA_STORE[existing_idx] = vendor_data
        save_vector_store()
        return len(_METADATA_STORE)

    # Add to FAISS Index
    try:
        import faiss
        if _FAISS_INDEX is None:
            _FAISS_INDEX = faiss.IndexFlatIP(EMBEDDING_DIM)
        _FAISS_INDEX.add(embedding)
    except Exception:
        if _FALLBACK_VECTORS is None:
            _FALLBACK_VECTORS = embedding
        else:
            _FALLBACK_VECTORS = np.vstack([_FALLBACK_VECTORS, embedding])

    _METADATA_STORE.append(vendor_data)
    save_vector_store()
    return len(_METADATA_STORE)


def add_vendor(vendor_data: Dict[str, Any]) -> int:
    """Alias for add_vendor_to_index."""
    return add_vendor_to_index(vendor_data)


def search_similar_vendors(
    query: Union[str, np.ndarray, Dict[str, Any]],
    top_k: int = 5,
    threshold: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Searches for semantically similar vendors in the vector store.
    
    Args:
        query: Query string, embedding vector, or vendor dict.
        top_k: Max results to return.
        threshold: Minimum similarity cutoff (0.0 to 1.0).
        
    Returns:
        List of dicts: [
            {
                "vendor": vendor_dict,
                "similarity": float,
                "similarity_pct": str,
                "tier": "High" | "Medium" | "Low"
            }
        ]
    """
    global _FAISS_INDEX, _METADATA_STORE, _FALLBACK_VECTORS
    if _FAISS_INDEX is None and _FALLBACK_VECTORS is None:
        _load_or_create_index()

    if not _METADATA_STORE:
        return []

    # Prepare query vector
    if isinstance(query, dict):
        query_text = get_vendor_embedding_text(query)
        q_vec = generate_embedding(query_text).reshape(1, -1)
    elif isinstance(query, str):
        q_vec = generate_embedding(query).reshape(1, -1)
    elif isinstance(query, np.ndarray):
        q_vec = query.reshape(1, -1)
    else:
        return []

    results = []
    k = min(top_k, len(_METADATA_STORE))

    # FAISS Search
    try:
        import faiss
        if _FAISS_INDEX is not None and _FAISS_INDEX.ntotal > 0:
            distances, indices = _FAISS_INDEX.search(q_vec, k)
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1 and idx < len(_METADATA_STORE):
                    sim = float(dist)
                    # Clip between 0 and 1
                    sim = max(0.0, min(1.0, sim))
                    if sim >= threshold:
                        tier = "High (>=85%)" if sim >= 0.85 else ("Medium (70-85%)" if sim >= 0.70 else "Low (<70%)")
                        results.append({
                            "vendor": _METADATA_STORE[idx],
                            "similarity": sim,
                            "similarity_pct": f"{sim:.1%}",
                            "tier": tier
                        })
            return results
    except Exception as e:
        print(f"[VectorStore] FAISS search error: {e}. Falling back to cosine matrix.")

    # Fallback Numpy Cosine Search
    if _FALLBACK_VECTORS is not None and len(_FALLBACK_VECTORS) > 0:
        sims = np.dot(_FALLBACK_VECTORS, q_vec.T).flatten()
        top_indices = np.argsort(-sims)[:k]
        for idx in top_indices:
            sim = float(sims[idx])
            sim = max(0.0, min(1.0, sim))
            if sim >= threshold and idx < len(_METADATA_STORE):
                tier = "High (>=85%)" if sim >= 0.85 else ("Medium (70-85%)" if sim >= 0.70 else "Low (<70%)")
                results.append({
                    "vendor": _METADATA_STORE[idx],
                    "similarity": sim,
                    "similarity_pct": f"{sim:.1%}",
                    "tier": tier
                })

    return results


def search_vendors(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Convenience wrapper for semantic search."""
    return search_similar_vendors(query_text, top_k=top_k)


def rebuild_vector_index(all_vendors: List[Dict[str, Any]]):
    """Rebuilds the entire index from a list of vendor records."""
    global _FAISS_INDEX, _METADATA_STORE, _FALLBACK_VECTORS
    _METADATA_STORE = []
    
    try:
        import faiss
        _FAISS_INDEX = faiss.IndexFlatIP(EMBEDDING_DIM)
    except Exception:
        _FAISS_INDEX = None
        _FALLBACK_VECTORS = None

    for v in all_vendors:
        add_vendor_to_index(v)


def get_vector_store_stats() -> Dict[str, Any]:
    """Returns vector store health and count."""
    global _METADATA_STORE, _FAISS_INDEX
    return {
        "indexed_vendors": len(_METADATA_STORE),
        "engine": "FAISS FlatIP" if _FAISS_INDEX is not None else "Numpy Fallback",
        "embedding_dim": EMBEDDING_DIM
    }
