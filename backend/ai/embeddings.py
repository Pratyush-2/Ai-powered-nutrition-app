"""
Embeddings generation and FAISS index management.

This module handles the creation of embeddings from nutrition fact text,
building FAISS indices for efficient similarity search, and persisting
the index and metadata for later retrieval.
"""

import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NutritionEmbeddings:
    """Manages embeddings generation and FAISS index operations."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = "backend/indexes/nutrition.index"):
        self.model_name = model_name
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize the embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = None
        self.metadata = []
        
    def load_jsonl_data(self, jsonl_path: str) -> List[Dict]:
        """Load nutrition facts from JSONL file."""
        data = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        logger.info(f"Loaded {len(data)} nutrition facts from {jsonl_path}")
        return data
    
    def generate_embeddings(self, facts: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """
        Generate embeddings for nutrition facts.
        
        Args:
            facts: List of nutrition fact dictionaries
            
        Returns:
            Tuple of (embeddings_array, metadata_list)
        """
        logger.info(f"Generating embeddings for {len(facts)} facts...")
        
        # Extract fact texts
        fact_texts = [fact["fact_text"] for fact in facts]
        
        # Generate embeddings
        embeddings = self.model.encode(fact_texts, convert_to_numpy=True)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Prepare metadata
        metadata = []
        for i, fact in enumerate(facts):
            meta = {
                "index": i,
                "name": fact["name"],
                "barcode": fact["barcode"],
                "url": fact["url"],
                "calories_100g": fact["calories_100g"],
                "protein_100g": fact["protein_100g"],
                "carbs_100g": fact["carbs_100g"],
                "fat_100g": fact["fat_100g"],
                "fact_text": fact["fact_text"]
            }
            metadata.append(meta)
        
        logger.info(f"Generated {embeddings.shape[0]} embeddings with dimension {embeddings.shape[1]}")
        return embeddings, metadata
    
    def build_faiss_index(self, embeddings: np.ndarray, metadata: List[Dict]) -> faiss.Index:
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings: Normalized embeddings array
            metadata: List of metadata dictionaries
            
        Returns:
            FAISS index object
        """
        logger.info("Building FAISS index...")
        
        # Create FAISS index for inner product (cosine similarity with normalized vectors)
        index = faiss.IndexFlatIP(self.dimension)
        
        # Add embeddings to index
        index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.metadata = metadata
        
        logger.info(f"Built FAISS index with {index.ntotal} vectors")
        return index
    
    def save_index(self, index: faiss.Index, metadata: List[Dict], embeddings_path: str = None):
        """
        Save FAISS index and metadata to disk.
        
        Args:
            index: FAISS index object
            metadata: List of metadata dictionaries
            embeddings_path: Optional path to save raw embeddings
        """
        logger.info(f"Saving FAISS index to {self.index_path}")
        
        # Save FAISS index
        faiss.write_index(index, str(self.index_path))
        
        # Save metadata
        metadata_path = self.index_path.parent / "metadata.jsonl"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            for meta in metadata:
                f.write(json.dumps(meta, ensure_ascii=False) + "\n")
        
        # Save raw embeddings if requested
        if embeddings_path:
            embeddings_path = Path(embeddings_path)
            np.save(embeddings_path, index.reconstruct_n(0, index.ntotal))
            logger.info(f"Saved raw embeddings to {embeddings_path}")
        
        # Save index info
        info_path = self.index_path.parent / "index_info.json"
        info = {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "num_vectors": index.ntotal,
            "index_type": "IndexFlatIP",
            "created_at": datetime.now().isoformat()
        }
        
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info("Index and metadata saved successfully!")
    
    def load_index(self) -> Tuple[faiss.Index, List[Dict]]:
        """
        Load FAISS index and metadata from disk.
        
        Returns:
            Tuple of (index, metadata)
        """
        if not self.index_path.exists():
            raise FileNotFoundError(f"Index not found at {self.index_path}")
        
        logger.info(f"Loading FAISS index from {self.index_path}")
        
        # Load FAISS index
        index = faiss.read_index(str(self.index_path))
        
        # Load metadata
        metadata_path = self.index_path.parent / "metadata.jsonl"
        metadata = []
        with open(metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    metadata.append(json.loads(line))
        
        logger.info(f"Loaded index with {index.ntotal} vectors and {len(metadata)} metadata entries")
        return index, metadata
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar nutrition facts.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of search results with scores and metadata
        """
        if self.index is None:
            self.index, self.metadata = self.load_index()
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search index
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Format results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["score"] = float(score)
                result["rank"] = i + 1
                results.append(result)
        
        return results
    
    def build_from_jsonl(self, jsonl_path: str, save_embeddings: bool = True):
        """
        Build complete FAISS index from JSONL file.
        
        Args:
            jsonl_path: Path to JSONL file with nutrition facts
            save_embeddings: Whether to save raw embeddings
        """
        # Load data
        facts = self.load_jsonl_data(jsonl_path)
        
        if not facts:
            logger.warning("No facts found in JSONL file")
            return
        
        # Generate embeddings
        embeddings, metadata = self.generate_embeddings(facts)
        
        # Build index
        index = self.build_faiss_index(embeddings, metadata)
        
        # Save everything
        embeddings_path = str(self.index_path.parent / "embeddings.npy") if save_embeddings else None
        self.save_index(index, metadata, embeddings_path)
        
        # Store in instance for immediate use
        self.index = index
        self.metadata = metadata


def main():
    """CLI interface for building FAISS index."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build FAISS index from nutrition facts")
    parser.add_argument("--jsonl", type=str, required=True, help="Path to JSONL file")
    parser.add_argument("--model", type=str, default="all-MiniLM-L6-v2", help="Embedding model name")
    parser.add_argument("--index-path", type=str, default="backend/indexes/nutrition.index", help="Output index path")
    parser.add_argument("--save-embeddings", action="store_true", help="Save raw embeddings")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Build index
    embeddings = NutritionEmbeddings(model_name=args.model, index_path=args.index_path)
    embeddings.build_from_jsonl(args.jsonl, save_embeddings=args.save_embeddings)
    
    print("FAISS index built successfully!")


if __name__ == "__main__":
    main()

