import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")
if not api_key:
    print("Error: FIRECRAWL_API_KEY not found in environment variables.")
    exit(1)

url = "https://api.firecrawl.dev/v1/scrape"
target_url = "https://feastables.com/collections/snacking-chocolate"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "url": target_url,
    "formats": ["extract"],
    "extract": {
        "schema": {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "image_url": {"type": "string"},
                            "price": {"type": "string"}
                        },
                        "required": ["name", "image_url"]
                    }
                }
            },
            "required": ["products"]
        }
    }
}

print(f"Scraping {target_url} for product images...")

try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    if data.get("success"):
        products = data["data"]["extract"].get("products", [])
        print(json.dumps(products, indent=2))
        
        # Save to file for easy access
        with open("fecha_products.json", "w") as f:
            json.dump(products, f, indent=2)
            
    else:
        print(f"Error: {data.get('error')}")

except Exception as e:
    print(f"Exception occurred: {str(e)}")
