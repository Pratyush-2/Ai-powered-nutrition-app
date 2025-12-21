
import requests
import time
from functools import lru_cache

# Simple in-memory cache
_cache = {}
_CACHE_DURATION = 300  # 5 minutes

@lru_cache(maxsize=100)
def search_food_by_name(food_name: str):
    """
    Searches for food with intelligent sorting and caching.
    Prioritizes: exact matches > starts with > contains > others
    """
    
    # Check cache first
    cache_key = food_name.lower().strip()
    current_time = time.time()
    
    if cache_key in _cache:
        cached_data, timestamp = _cache[cache_key]
        if current_time - timestamp < _CACHE_DURATION:
            return cached_data
    
    # Try external API first, then fallback to local data
    result = _search_openfoodfacts(food_name, cache_key, current_time)
    
    # If no results from API, try local database
    if not result.get("products"):
        print(f"No external results for '{food_name}', using local database")
        result = _search_local_database(food_name, cache_key, current_time)
    
    return result

def _search_openfoodfacts(food_name: str, cache_key: str, current_time: float):
    """Search OpenFoodFacts API with improved error handling"""
    
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process", 
        "json": 1,
        "page_size": 20,  # Limit results for speed
        "sort_by": "popularity"  # Better sorting than last_modified
    }
    
    try:
        # Try with longer timeout and different parameters
        response = requests.get(url, params=params, timeout=15)  # Increased timeout
        response.raise_for_status()
        
        data = response.json()
        products = data.get("products", [])
        
        # If no products found, try a simpler search
        if not products:
            print(f"No products found for '{food_name}', trying simpler search...")
            simple_params = {
                "search_terms": food_name,
                "json": 1,
                "page_size": 10,
            }
            response2 = requests.get(url, params=simple_params, timeout=10)
            if response2.status_code == 200:
                data2 = response2.json()
                products = data2.get("products", [])
                print(f"Simple search found {len(products)} products")
        
        # Intelligent scoring and sorting
        scored_products = []
        search_lower = food_name.lower().strip()
        
        for product in products:
            product_name = product.get("product_name", "").lower().strip()
            if not product_name:
                continue
                
            # Calculate relevance score
            score = 0
            
            # Exact match = highest score
            if product_name == search_lower:
                score = 100
            # Starts with search term
            elif product_name.startswith(search_lower):
                score = 80
            # Contains search term as whole word
            elif f" {search_lower} " in f" {product_name} ":
                score = 60
            # Contains search term anywhere
            elif search_lower in product_name:
                score = 40
            # Partial word matches
            else:
                words = search_lower.split()
                matches = sum(1 for word in words if word in product_name)
                if matches > 0:
                    score = 20 + (matches * 5)
                else:
                    score = 10
            
            # Boost score for common food items
            if any(term in product_name for term in ['rice', 'chicken', 'beef', 'fish', 'eggs', 'milk', 'bread', 'pasta']):
                score += 5
                
            # Penalize branded or processed foods (less for search results)
            if any(term in product_name for term in ['ben\'s', 'brand', 'processed', 'instant', 'ready']):
                score -= 2  # Reduced penalty for search
            
            # Ensure serving_size exists
            product["serving_size"] = product.get("serving_size", "100g")
            
            scored_products.append((score, product))
        
        # Sort by score (highest first) and take top 10
        scored_products.sort(key=lambda x: x[0], reverse=True)
        data["products"] = [product for score, product in scored_products[:10]]
        
        # Cache the result
        _cache[cache_key] = (data, current_time)
        
        return data
        
    except requests.exceptions.Timeout:
        print(f"OpenFoodFacts API timeout for '{food_name}'")
        # Return cached data if available, even if expired
        if cache_key in _cache:
            return _cache[cache_key][0]
        return {"products": []}
    except requests.exceptions.RequestException as e:
        print(f"OpenFoodFacts API error for '{food_name}': {e}")
        # Return cached data if available, even if expired
        if cache_key in _cache:
            return _cache[cache_key][0]
        return {"products": []}
    except Exception as e:
        print(f"Food search error for '{food_name}': {e}")
        return {"products": []}

def _search_local_database(food_name: str, cache_key: str, current_time: float):
    """Search local nutrition database as fallback"""
    search_lower = food_name.lower().strip()
    
    # Import local database
    try:
        from app.ai_pipeline.enhanced_image_recognition import food_recognizer
        local_db = getattr(food_recognizer, 'nutrition_db', {})
    except:
        local_db = {}
    
    # Find matches in local database
    matches = []
    for db_key, nutrition in local_db.items():
        db_key_lower = db_key.lower()
        score = 0
        
        # Exact match
        if db_key_lower == search_lower:
            score = 100
        # Contains search term
        elif search_lower in db_key_lower:
            score = 80
        # Fuzzy match
        else:
            search_words = set(search_lower.split())
            db_words = set(db_key_lower.split())
            common_words = search_words.intersection(db_words)
            if common_words:
                score = 60 + (len(common_words) * 10)
        
        if score > 50:  # Only include reasonable matches
            # Convert nutrition data to OpenFoodFacts-like format
            product = {
                "product_name": db_key.title(),
                "nutriments": {
                    "energy-kcal_100g": nutrition.get("calories", 0),
                    "proteins_100g": nutrition.get("protein", 0),
                    "fat_100g": nutrition.get("fat", 0),
                    "sugars_100g": nutrition.get("sugar", 0),
                    "carbohydrates_100g": nutrition.get("carbs", 0),
                    "fiber_100g": nutrition.get("fiber", 0),
                },
                "serving_size": nutrition.get("serving_size", "100g"),
                "_local_fallback": True  # Mark as local data
            }
            matches.append((score, product))
    
    # Sort by score and return top matches
    matches.sort(key=lambda x: x[0], reverse=True)
    products = [product for score, product in matches[:10]]
    
    result = {"products": products}
    
    # Cache the result
    _cache[cache_key] = (result, current_time)
    
    return result
