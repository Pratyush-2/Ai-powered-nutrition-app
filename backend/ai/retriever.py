"""
Retrieval API for nutrition facts using FAISS index.

This module provides the main retrieval functionality for finding
similar nutrition facts based on user queries using semantic search.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
from .embeddings import NutritionEmbeddings

logger = logging.getLogger(__name__)

class NutritionRetriever:
    """Handles retrieval of nutrition facts using semantic search."""
    
    def __init__(self, index_path: str = "backend/indexes/nutrition.index", 
                 model_name: str = "all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.model_name = model_name
        self.embeddings = None
        self._load_embeddings()
    
    def _load_embeddings(self):
        """Load the embeddings model and FAISS index."""
        if not Path(self.index_path).exists():
            logger.warning(f"Index file not found at {self.index_path}. Retriever will be unavailable.")
            self.embeddings = None
            return

        try:
            self.embeddings = NutritionEmbeddings(
                model_name=self.model_name,
                index_path=self.index_path
            )
            logger.info("Nutrition retriever initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            self.embeddings = None
    
    def retrieve_facts(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve similar nutrition facts for a given query.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of dictionaries containing:
            - score: Similarity score (0-1)
            - fact_text: The nutrition fact text
            - meta: Metadata including name, barcode, nutrition values
        """
        if not self.embeddings:
            logger.error("Embeddings not loaded")
            return []
        
        try:
            results = self.embeddings.search(query, k=k)
            
            # Format results for API response
            formatted_results = []
            for result in results:
                formatted_result = {
                    "score": result["score"],
                    "fact_text": result["fact_text"],
                    "meta": {
                        "name": result["name"],
                        "barcode": result["barcode"],
                        "url": result["url"],
                        "calories_100g": result["calories_100g"],
                        "protein_100g": result["protein_100g"],
                        "carbs_100g": result["carbs_100g"],
                        "fat_100g": result["fat_100g"]
                    }
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Retrieved {len(formatted_results)} facts for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving facts for query '{query}': {e}")
            return []
    
    def get_fact_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a specific nutrition fact by name.
        
        Args:
            name: Name of the food item
            
        Returns:
            Dictionary with nutrition fact data or None if not found
        """
        if not self.embeddings:
            return None
        
        try:
            # Search for exact name match
            results = self.retrieve_facts(name, k=1)
            if results and results[0]["meta"]["name"].lower() == name.lower():
                return results[0]
            
            # If no exact match, return the best match
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Error getting fact by name '{name}': {e}")
            return None
    
    def get_similar_foods(self, food_name: str, k: int = 5) -> List[Dict]:
        """
        Get foods similar to the given food name.
        
        Args:
            food_name: Name of the food to find similar items for
            k: Number of similar items to return
            
        Returns:
            List of similar food items with scores
        """
        return self.retrieve_facts(food_name, k=k)
    
    def is_available(self) -> bool:
        """Check if the retriever is available and ready to use."""
        return self.embeddings is not None


# Global retriever instance
_retriever_instance = None

def get_retriever() -> NutritionRetriever:
    """Get the global retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = NutritionRetriever()
    return _retriever_instance

def retrieve_facts(query: str, k: int = 5) -> List[Dict]:
    """
    Convenience function to retrieve nutrition facts.
    
    Args:
        query: Search query
        k: Number of results
        
    Returns:
        List of retrieved facts
    """
    retriever = get_retriever()
    return retriever.retrieve_facts(query, k)

