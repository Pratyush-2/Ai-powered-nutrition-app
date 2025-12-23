import requests
import json

print("Testing OpenFoodFacts API connection...")
print("=" * 60)

url = "https://world.openfoodfacts.org/cgi/search.pl"
params = {
    "search_terms": "rice",
    "search_simple": 1,
    "action": "process",
    "json": 1,
    "page_size": 5
}

try:
    print(f"\nRequesting: {url}")
    print(f"Params: {params}")
    print("\nSending request...")
    
    response = requests.get(url, params=params, timeout=10)
    
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"✅ Response Time: {response.elapsed.total_seconds():.2f} seconds")
    
    data = response.json()
    products = data.get("products", [])
    
    print(f"\n✅ Products Found: {len(products)}")
    
    if products:
        print("\n" + "=" * 60)
        print("FIRST PRODUCT:")
        print("=" * 60)
        product = products[0]
        print(f"Name: {product.get('product_name', 'N/A')}")
        print(f"Brand: {product.get('brands', 'N/A')}")
        
        nutriments = product.get('nutriments', {})
        print(f"\nNutrition (per 100g):")
        print(f"  Calories: {nutriments.get('energy-kcal_100g', 'N/A')}")
        print(f"  Protein: {nutriments.get('proteins_100g', 'N/A')}g")
        print(f"  Carbs: {nutriments.get('carbohydrates_100g', 'N/A')}g")
        print(f"  Fat: {nutriments.get('fat_100g', 'N/A')}g")
        
        print("\n✅ OpenFoodFacts API is WORKING!")
    else:
        print("\n⚠️  No products found for 'rice'")
        
except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT - OpenFoodFacts API is not responding")
    print("   This could be due to:")
    print("   - Slow internet connection")
    print("   - OpenFoodFacts server issues")
    print("   - Firewall blocking the request")
    
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ CONNECTION ERROR: {e}")
    print("   This could be due to:")
    print("   - No internet connection")
    print("   - DNS issues")
    print("   - Firewall/proxy blocking")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"   Type: {type(e).__name__}")

print("\n" + "=" * 60)
