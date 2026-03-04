from __future__ import annotations

import os

import psycopg2
from psycopg2.extras import RealDictCursor
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "fitandsleek_angkor",
    "user": "postgres",
    "password": "postgres123",
}

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = "products"
MODEL_NAME = "clip-ViT-B-32"
VECTOR_SIZE = 512  # clip-ViT-B-32 output dimension


def check_db_connection() -> bool:
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        print("✅ PostgreSQL connection OK")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


def ensure_collection(client: QdrantClient) -> None:
    if client.collection_exists(collection_name=COLLECTION):
        client.delete_collection(collection_name=COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def fetch_products():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, price, image_url FROM products")
            return cur.fetchall()
    finally:
        conn.close()


def main():
    if not check_db_connection():
        return

    model = SentenceTransformer(MODEL_NAME)

    # Prefer cloud URL/API key when provided, otherwise fall back to local host/port
    if QDRANT_URL and QDRANT_API_KEY:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        print(f"➡️  Using Qdrant Cloud at {QDRANT_URL}")
    else:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        print(f"➡️  Using local Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
    ensure_collection(client)

    rows = fetch_products()
    points = []
    for idx, row in enumerate(rows):
        name = row.get("name") or ""
        vector = model.encode(name).tolist()
        points.append(
            PointStruct(
                id=row.get("id") if row.get("id") is not None else idx,
                vector=vector,
                payload={
                    "product_name": name,
                    "price": float(row.get("price") or 0),
                    "image_url": row.get("image_url"),
                },
            )
        )

    if not points:
        print("No products found to sync.")
        return

    client.upsert(collection_name=COLLECTION, points=points)
    print(f"✅ Synced {len(points)} products to Qdrant.")


if __name__ == "__main__":
    main()
