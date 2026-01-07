import requests
import json

# Test searches
searches = ["rice", "eggs", "chocolate", "chapati", "amul", "apple"]

for query in searches:
    print(f"\n{'='*50}")
    print(f"SEARCHING: {query}")
    print('='*50)
    
    try:
        response = requests.post(
            'http://localhost:8000/search-food/',
            json={'query': query},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            
            if products:
                print(f"Found {len(products)} results:")
                for i, product in enumerate(products[:5], 1):
                    name = product.get('product_name', 'Unknown')
                    print(f"  {i}. {name}")
            else:
                print("No results found")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")

print(f"\n{'='*50}")
print("Test complete!")
