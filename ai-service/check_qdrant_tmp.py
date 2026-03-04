from qdrant_client import QdrantClient
import json

client = QdrantClient(host="127.0.0.1", port=6333)
count = client.count(collection_name="products").count
pts, _ = client.scroll(collection_name="products", limit=5)

print("count", count)
print(json.dumps([
    {
        "id": p.id,
        "product_name": p.payload.get("product_name"),
        "image_url": p.payload.get("image_url"),
        "price": p.payload.get("price"),
    }
    for p in pts
], ensure_ascii=False, indent=2))