from __future__ import annotations

import os
from typing import List, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

# Configuration via environment variables to keep secrets out of code
PG_URL = os.getenv("PG_URL")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = "products"
MODEL_NAME = "clip-ViT-B-32"
VECTOR_SIZE = 512


def ensure_env():
    missing = [name for name, val in {
        "PG_URL": PG_URL,
        "QDRANT_URL": QDRANT_URL,
        "QDRANT_API_KEY": QDRANT_API_KEY,
    }.items() if not val]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def fetch_products() -> List[Tuple]:
    # Render requires sslmode=require in the URL
    conn = psycopg2.connect(PG_URL, cursor_factory=RealDictCursor)
    try:
        with conn.cursor() as cur:
            # Grab all columns to stay resilient to naming differences
            cur.execute("SELECT * FROM products")
            return cur.fetchall()
    finally:
        conn.close()


def ensure_collection(client: QdrantClient) -> None:
    if client.collection_exists(collection_name=COLLECTION):
        print(f"🗑️ Dropping existing collection '{COLLECTION}'...")
        client.delete_collection(collection_name=COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def sync_production_to_cloud():
    ensure_env()
    print("🚀 Pulling products from Render PostgreSQL...")

    products = fetch_products()
    print(f"📦 Found {len(products)} products.")

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    model = SentenceTransformer(MODEL_NAME)

    ensure_collection(client)

    print("🧠 Encoding product names with CLIP...")
    points: List[PointStruct] = []
    for row in products:
        p_id = row.get("id")
        p_name = row.get("product_name") or row.get("name") or ""
        p_price = float(row.get("price") or row.get("product_price") or 0)
        p_image = row.get("main_image") or row.get("image_url")

        vector = model.encode(p_name).tolist()
        points.append(
            PointStruct(
                id=p_id,
                vector=vector,
                payload={
                    "product_name": p_name,
                    "price": p_price,
                    "main_image": p_image,
                },
            )
        )

    if not points:
        print("No products to sync.")
        return

    print("☁️ Upserting to Qdrant Cloud...")
    client.upsert(collection_name=COLLECTION, points=points)
    print(f"✅ Done. Synced {len(points)} products to Qdrant Cloud.")


if __name__ == "__main__":
    sync_production_to_cloud()
