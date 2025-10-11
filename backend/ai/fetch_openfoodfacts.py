"""
OpenFoodFacts data fetcher with caching and SQLite storage.

This module provides functionality to fetch nutrition data from OpenFoodFacts API,
normalize the data into a canonical format, and cache results both in JSONL format
and SQLite database for offline usage.
"""

import json
import sqlite3
import time
import requests
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import argparse
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenFoodFactsFetcher:
    """Fetches and caches nutrition data from OpenFoodFacts API."""
    
    def __init__(self, cache_dir: str = "data", db_path: str = "data/nutrition_facts.db"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.jsonl_path = self.cache_dir / "nutrition_facts.jsonl"
        self.db_path = db_path
        self.base_url = "https://world.openfoodfacts.org/cgi/search.pl"
        self.rate_limit_delay = 1.0  # Be polite with rate limiting
        
        # Initialize SQLite database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for caching food data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                barcode TEXT,
                url TEXT,
                calories_100g REAL,
                protein_100g REAL,
                carbs_100g REAL,
                fat_100g REAL,
                fact_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON foods(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_barcode ON foods(barcode)")
        
        conn.commit()
        conn.close()
    
    def _normalize_nutriments(self, product: Dict) -> Dict:
        """
        Normalize OpenFoodFacts product data into canonical format.
        
        Args:
            product: Raw product data from OpenFoodFacts API
            
        Returns:
            Normalized nutrition data dictionary
        """
        nutriments = product.get("nutriments", {})
        
        # Extract and normalize nutrition values per 100g
        calories_100g = self._safe_float(nutriments.get("energy-kcal_100g") or 
                                       nutriments.get("energy_100g", 0) / 4.184)
        protein_100g = self._safe_float(nutriments.get("proteins_100g", 0))
        carbs_100g = self._safe_float(nutriments.get("carbohydrates_100g", 0))
        fat_100g = self._safe_float(nutriments.get("fat_100g", 0))
        
        # Create fact text for embedding
        fact_text = f"{product.get('product_name', 'Unknown')} — {calories_100g:.0f} kcal/100g, {protein_100g:.1f} g protein/100g"
        
        return {
            "name": product.get("product_name", "Unknown"),
            "barcode": product.get("code", ""),
            "url": f"https://world.openfoodfacts.org/product/{product.get('code', '')}",
            "calories_100g": calories_100g,
            "protein_100g": protein_100g,
            "carbs_100g": carbs_100g,
            "fat_100g": fat_100g,
            "fact_text": fact_text,
            "raw_data": product  # Keep original for debugging
        }
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float, returning 0.0 for invalid values."""
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def search_food(self, query: str, page_size: int = 20) -> List[Dict]:
        """
        Search for food items using OpenFoodFacts API.
        
        Args:
            query: Search query (food name)
            page_size: Number of results per page
            
        Returns:
            List of normalized food data dictionaries
        """
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": page_size,
            "page": 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            products = data.get("products", [])
            normalized_products = []
            
            for product in products:
                # Only include products with valid nutrition data
                if self._has_valid_nutrition(product):
                    normalized = self._normalize_nutriments(product)
                    normalized_products.append(normalized)
            
            logger.info(f"Found {len(normalized_products)} valid products for query: {query}")
            return normalized_products
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data for query '{query}': {e}")
            return []
    
    def _has_valid_nutrition(self, product: Dict) -> bool:
        """Check if product has valid nutrition data."""
        nutriments = product.get("nutriments", {})
        return (
            nutriments.get("energy-kcal_100g") or 
            nutriments.get("energy_100g") or
            nutriments.get("proteins_100g") or
            nutriments.get("carbohydrates_100g") or
            nutriments.get("fat_100g")
        ) is not None
    
    def cache_to_jsonl(self, foods: List[Dict]):
        """Cache food data to JSONL file."""
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            for food in foods:
                f.write(json.dumps(food, ensure_ascii=False) + "\n")
    
    def cache_to_sqlite(self, foods: List[Dict]):
        """Cache food data to SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for food in foods:
            # Check if food already exists
            cursor.execute(
                "SELECT id FROM foods WHERE name = ? AND barcode = ?",
                (food["name"], food["barcode"])
            )
            
            if cursor.fetchone():
                # Update existing record
                cursor.execute("""
                    UPDATE foods SET 
                        calories_100g = ?, protein_100g = ?, carbs_100g = ?, 
                        fat_100g = ?, fact_text = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ? AND barcode = ?
                """, (
                    food["calories_100g"], food["protein_100g"], food["carbs_100g"],
                    food["fat_100g"], food["fact_text"], food["name"], food["barcode"]
                ))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO foods (name, barcode, url, calories_100g, protein_100g, 
                                     carbs_100g, fat_100g, fact_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    food["name"], food["barcode"], food["url"], food["calories_100g"],
                    food["protein_100g"], food["carbs_100g"], food["fat_100g"], food["fact_text"]
                ))
        
        conn.commit()
        conn.close()
    
    def get_food_data(self, food_name: str) -> Optional[Dict]:
        """
        Get food data from cache or fetch from API.
        
        Args:
            food_name: Name of the food to search for
            
        Returns:
            Normalized food data or None if not found
        """
        # First check SQLite cache
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM foods WHERE name LIKE ? ORDER BY updated_at DESC LIMIT 1",
            (f"%{food_name}%",)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Return cached data
            return {
                "name": result[1],
                "barcode": result[2],
                "url": result[3],
                "calories_100g": result[4],
                "protein_100g": result[5],
                "carbs_100g": result[6],
                "fat_100g": result[7],
                "fact_text": result[8]
            }
        
        # If not in cache, fetch from API
        foods = self.search_food(food_name, page_size=1)
        if foods:
            food = foods[0]
            # Cache the result
            self.cache_to_sqlite([food])
            self.cache_to_jsonl([food])
            return food
        
        return None
    
    def seed_database(self, food_names: List[str]):
        """
        Seed the database with common food items.
        
        Args:
            food_names: List of food names to seed
        """
        logger.info(f"Seeding database with {len(food_names)} food items...")
        
        for i, food_name in enumerate(food_names):
            logger.info(f"Processing {i+1}/{len(food_names)}: {food_name}")
            
            # Check if already cached
            if self.get_food_data(food_name):
                logger.info(f"  Already cached: {food_name}")
                continue
            
            # Fetch and cache
            foods = self.search_food(food_name)
            if foods:
                self.cache_to_sqlite(foods)
                self.cache_to_jsonl(foods)
                logger.info(f"  Cached {len(foods)} items for: {food_name}")
            else:
                logger.warning(f"  No data found for: {food_name}")
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        logger.info("Database seeding completed!")


def main():
    """CLI interface for the OpenFoodFacts fetcher."""
    parser = argparse.ArgumentParser(description="Fetch and cache OpenFoodFacts data")
    parser.add_argument("--seed", type=str, help="Comma-separated list of food names to seed")
    parser.add_argument("--query", type=str, help="Single food query")
    parser.add_argument("--cache-dir", type=str, default="data", help="Cache directory")
    
    args = parser.parse_args()
    
    fetcher = OpenFoodFactsFetcher(cache_dir=args.cache_dir)
    
    if args.seed:
        food_names = [name.strip() for name in args.seed.split(",")]
        fetcher.seed_database(food_names)
    elif args.query:
        result = fetcher.get_food_data(args.query)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"No data found for: {args.query}")
    else:
        print("Please provide --seed or --query argument")


if __name__ == "__main__":
    main()

