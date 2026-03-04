from __future__ import annotations

import os
from typing import List

from psycopg2.extras import RealDictCursor
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.database import get_db_connection
from app.model_loader import get_model
from app.qdrant_logic import get_qdrant_client

VECTOR_SIZE = 512
DEFAULT_COLLECTION = "products"


def _fetch_products() -> List[dict]:
    """Fetch all rows from products table with flexible column handling."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM products")
            return cur.fetchall()
    finally:
        conn.close()


def _ensure_collection(client: QdrantClient, collection: str, drop_existing: bool) -> None:
    if drop_existing and client.collection_exists(collection_name=collection):
        client.delete_collection(collection_name=collection)

    if not client.collection_exists(collection_name=collection):
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def run_sync() -> int:
    """Sync products from Postgres to Qdrant Cloud. Returns number of points upserted."""
    collection = os.getenv("QDRANT_COLLECTION", DEFAULT_COLLECTION)
    drop = os.getenv("SYNC_DROP_COLLECTION", "true").lower() in {"1", "true", "yes"}

    products = _fetch_products()
    if not products:
        print("No products to sync.")
        return 0

    model = get_model()
    client = get_qdrant_client()

    _ensure_collection(client, collection, drop)

    points: List[PointStruct] = []
    for idx, row in enumerate(products):
        name = row.get("product_name") or row.get("name") or ""
        price = float(row.get("price") or row.get("product_price") or 0)
        image = row.get("image_url") or row.get("main_image") or row.get("image")
        pid = row.get("id") if row.get("id") is not None else idx

        vector = model.encode(name).tolist()
        points.append(
            PointStruct(
                id=pid,
                vector=vector,
                payload={
                    "product_name": name,
                    "price": price,
                    "image_url": image,
                },
            )
        )

    client.upsert(collection_name=collection, points=points)
    print(f"✅ Synced {len(points)} products to Qdrant collection '{collection}'.")
    return len(points)


if __name__ == "__main__":
    run_sync()
