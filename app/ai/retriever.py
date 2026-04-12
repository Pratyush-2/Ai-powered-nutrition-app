
import json
import numpy as np
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "app/indexes/nutrition.index")
EMB_MODEL = os.getenv("EMB_MODEL", "all-MiniLM-L6-v2")
METADATA_PATH = "app/indexes/metadata.jsonl"

# Lazy-loaded resources (loaded on first call, not at import time)
# This saves ~500MB RAM at startup, critical for free-tier hosting
_index = None
_model = None
_metadata = None

def _load_resources():
    """Lazily load FAISS index, SentenceTransformer model, and metadata."""
    global _index, _model, _metadata
    
    if _index is not None:
        return  # Already loaded
    
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        
        logger.info("Loading FAISS index and SentenceTransformer model (first call)...")
        
        _index = faiss.read_index(FAISS_INDEX_PATH)
        _model = SentenceTransformer(EMB_MODEL)
        
        _metadata = []
        with open(METADATA_PATH, "r") as f:
            for line in f:
                _metadata.append(json.loads(line))
        
        logger.info("FAISS resources loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load FAISS resources: {e}")
        raise

def retrieve_facts(query: str, k: int = 5) -> list[dict]:
    """
    Retrieves the top k most relevant facts for a given query.
    Resources are lazy-loaded on first call.
    """
    import faiss
    
    _load_resources()
    
    # Encode the query into an embedding
    query_embedding = _model.encode([query], convert_to_numpy=True)

    # Normalize the query embedding
    faiss.normalize_L2(query_embedding)

    # Search the FAISS index
    distances, indices = _index.search(query_embedding, k)

    # Prepare the results
    results = []
    for i in range(k):
        if i < len(indices[0]):
            index_val = indices[0][i]
            if index_val < len(_metadata):
                # Retrieve fact_text from jsonl file
                fact_text = ""
                with open("data/nutrition_facts.jsonl", "r") as f:
                    for j, line in enumerate(f):
                        if j == index_val:
                            data = json.loads(line)
                            fact_text = data.get("fact_text", "")
                            break

                results.append({
                    "score": float(distances[0][i]),
                    "fact": fact_text,
                    "meta": _metadata[index_val]
                })

    return results
