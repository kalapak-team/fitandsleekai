import os

import requests

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set as environment variables")

def create_collection():
    headers = {"api-key": QDRANT_API_KEY, "Content-Type": "application/json"}
    
    # លុប Collection ចាស់ចោលសិន (ដើម្បីកុំឱ្យជាន់គ្នា)
    requests.delete(f"{QDRANT_URL}/collections/products", headers=headers)
    
    # បង្កើតថ្មីជាមួយទម្រង់ Vector សម្រាប់ CLIP Model (512 dimensions)
    payload = {
        "vectors": {
            "size": 512, 
            "distance": "Cosine"
        }
    }
    
    res = requests.put(f"{QDRANT_URL}/collections/products", headers=headers, json=payload)
    if res.status_code == 200:
        print("✅ បង្កើត Collection 'products' ជោគជ័យ!")
    else:
        print(f"❌ បង្កើតមិនបាន៖ {res.text}")

if __name__ == "__main__":
    create_collection()