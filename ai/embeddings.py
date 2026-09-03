"""
GenVendorAI Embeddings Module
Generates dense vector embeddings for vendor profiles using Sentence-Transformers (all-MiniLM-L6-v2).
Provides fallback local hashing embeddings if transformer weights cannot be downloaded.
"""

import os
import numpy as np
from typing import Dict, Any, List, Optional

_MODEL_INSTANCE = None
_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def get_embedding_model():
    """Loads SentenceTransformer model with singleton caching."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Suppress excessive huggingface logs
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            _MODEL_INSTANCE = SentenceTransformer(_MODEL_NAME)
        except Exception as e:
            print(f"[Embeddings] Warning: Failed to load SentenceTransformer ({e}). Using robust fallback vectorizer.")
            _MODEL_INSTANCE = "FALLBACK"
    return _MODEL_INSTANCE


def get_vendor_embedding_text(vendor_data: Dict[str, Any]) -> str:
    """
    Constructs a rich text representation of a vendor for semantic indexing.
    Combines Name, Category, Address, and operational context.
    """
    name = vendor_data.get("Vendor Name") or vendor_data.get("vendor_name", "")
    category = vendor_data.get("Business Category") or vendor_data.get("business_category", "")
    address = vendor_data.get("Address") or vendor_data.get("address", "")
    gstin = vendor_data.get("GSTIN") or vendor_data.get("gstin", "")
    
    parts = []
    if name and name != "Not available":
        parts.append(f"Vendor Name: {name}")
    if category and category != "Not available":
        parts.append(f"Business Category & Services: {category}")
    if address and address != "Not available":
        parts.append(f"Location & Address: {address}")
    if gstin and gstin != "Not available":
        parts.append(f"GSTIN Tax Identification: {gstin}")

    return " | ".join(parts) if parts else "Unknown Vendor Master Profile"


def _fallback_embedding(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """Deterministic, fast bag-of-words / char n-gram hashing vectorizer for offline resilience."""
    vec = np.zeros(dim, dtype=np.float32)
    clean_text = text.lower().strip()
    words = clean_text.split()
    for w in words:
        # Hash each word into index
        idx = hash(w) % dim
        vec[idx] += 1.0
    for i in range(len(clean_text) - 2):
        trigram = clean_text[i:i+3]
        idx = hash(trigram) % dim
        vec[idx] += 0.5
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def generate_embedding(text: str) -> np.ndarray:
    """
    Generates a normalized 1D numpy embedding vector for input text.
    """
    if not text or not text.strip():
        return np.zeros(EMBEDDING_DIM, dtype=np.float32)

    model = get_embedding_model()
    if model != "FALLBACK" and model is not None:
        try:
            emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return emb.astype(np.float32)
        except Exception as e:
            print(f"[Embeddings] Encode error: {e}. Falling back.")
            return _fallback_embedding(text)
    else:
        return _fallback_embedding(text)


def generate_batch_embeddings(texts: List[str]) -> np.ndarray:
    """Generates normalized embeddings for a list of texts."""
    model = get_embedding_model()
    if model != "FALLBACK" and model is not None:
        try:
            embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embs.astype(np.float32)
        except Exception:
            return np.vstack([_fallback_embedding(t) for t in texts])
    else:
        return np.vstack([_fallback_embedding(t) for t in texts])
