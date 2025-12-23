
import requests
import time

# Simple in-memory cache with consistent behavior
_cache = {}
_CACHE_DURATION = 86400  # 24 hours for aggressive caching

def search_food_by_name(food_name: str):
    """
    Searches for food with aggressive caching for speed and consistency.
    Strategy: Consistent results, cached for 24 hours
    """
    
    cache_key = food_name.lower().strip()
    current_time = time.time()
    
    # CONSISTENCY FIX: Check cache with 24-hour TTL
    if cache_key in _cache:
        cached_data, timestamp = _cache[cache_key]
        age = current_time - timestamp
        
        # Return cached data if less than 24 hours old
        if age < _CACHE_DURATION:
            print(f"✅ Returning cached results for '{food_name}' (age: {int(age/60)} minutes)")
            return cached_data
    
    # SPEED OPTIMIZATION: Try local DB first for instant results
    print(f"🔍 Checking local database for '{food_name}'...")
    local_result = _search_local_database(food_name, cache_key, current_time)
    
    if local_result.get("products"):
        print(f"✅ Found {len(local_result['products'])} results in local database (instant!)")
        # Cache local results
        _cache[cache_key] = (local_result, current_time)
        return local_result
    
    # Not in local DB, try OpenFoodFacts (with optimizations)
    print(f"🔍 Searching OpenFoodFacts for '{food_name}'...")
    result = _search_openfoodfacts(food_name, cache_key, current_time)
    
    if result.get("products"):
        return result
    
    # No results found anywhere
    print(f"❌ No results found for '{food_name}'")
    return {"products": []}

def _search_openfoodfacts(food_name: str, cache_key: str, current_time: float):
    """Search OpenFoodFacts API with improved speed and reliability"""
    
    # SPEED OPTIMIZATION: Use both endpoints in parallel
    endpoints = [
        "https://world.openfoodfacts.org/cgi/search.pl",
        "https://world.openfoodfacts.net/cgi/search.pl",
    ]
    
    # Better headers to avoid being blocked
    headers = {
        'User-Agent': 'NutritionApp/1.0 (Python requests)',
        'Accept': 'application/json',
    }
    
    # SPEED OPTIMIZATION: Smaller page size and only essential fields
    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5,  # Reduced from 10 for faster response
        "fields": "product_name,brands,nutriments,serving_size"  # Only what we need
    }
    
    # SPEED OPTIMIZATION: Try both endpoints in parallel with shorter timeout
    import concurrent.futures
    
    def try_endpoint(url):
        """Try a single endpoint with optimized settings"""
        try:
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(
                url, 
                params=params, 
                timeout=3,  # REDUCED from 8s to 3s for speed
                allow_redirects=True
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                
                if products:
                    return (True, data, url)
            return (False, None, url)
        except:
            return (False, None, url)
    
    # Try both endpoints in parallel (whichever responds first wins!)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(try_endpoint, url) for url in endpoints]
        
        # Wait for first successful response (or all to fail)
        for future in concurrent.futures.as_completed(futures, timeout=4):
            success, data, url = future.result()
            if success:
                print(f"✅ Found {len(data.get('products', []))} products from OpenFoodFacts ({url})!")
                
                # Process and score products
                products = data.get("products", [])
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
                    
                    # Ensure serving_size exists
                    product["serving_size"] = product.get("serving_size", "100g")
                    
                    scored_products.append((score, product))
                
                # Sort by score (highest first) and take top 5
                scored_products.sort(key=lambda x: x[0], reverse=True)
                data["products"] = [product for score, product in scored_products[:5]]
                
                # Cache the result
                _cache[cache_key] = (data, current_time)
                
                return data
    
    # All endpoints failed
    print(f"❌ OpenFoodFacts failed for '{food_name}' - using local database")
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
