import os
import requests
from PIL import Image
from sentence_transformers import SentenceTransformer

# Qdrant secrets must come from environment variables
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set as environment variables")

# ២. Load CLIP Model (ទាញយកតែម្តងគត់ ប្រហែល 600MB)
print("⏳ កំពុងទាញយក Model... (សូមរង់ចាំបន្តិច)")
model = SentenceTransformer('clip-ViT-B-32')

def upload_product(p_id, p_name, p_price, image_filename):
    if not os.path.exists(image_filename):
        print(f"❌ រកមិនឃើញ File: {image_filename}")
        return

    print(f"🧠 កំពុងបំប្លែង '{p_name}' ជា Vector...")
    
    # ៣. បំប្លែងរូបភាពជា Vector
    img = Image.open(image_filename)
    vector_data = model.encode(img).tolist()

    # ៤. រក្សាទុកក្នុង Qdrant Cloud
    headers = {"api-key": QDRANT_API_KEY, "Content-Type": "application/json"}
    payload = {
        "points": [{
            "id": p_id,
            "vector": vector_data,
            "payload": {
                "product_name": p_name, 
                "price": p_price, 
                "image_file": image_filename
            }
        }]
    }
    
    res = requests.put(f"{QDRANT_URL}/collections/products/points", headers=headers, json=payload)
    
    if res.status_code == 200:
        print(f"✅ ជោគជ័យ! '{p_name}' ត្រូវបានបញ្ចូលទៅ Cloud។")
    else:
        print(f"❌ Error: {res.text}")

if __name__ == "__main__":
    # ប្រាកដថាអ្នកមានរូបភាព nike.webp ក្នុង Folder
    upload_product(1, "Nike Strength Dri-FIT Tee", "25.00$", "nike.webp")