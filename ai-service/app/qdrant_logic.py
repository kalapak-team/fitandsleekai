import os
from typing import List

from fastapi import HTTPException
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse


def get_qdrant_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    if not url or not api_key:
        raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set")
    return QdrantClient(url=url, api_key=api_key)


def search_vectors(client: QdrantClient, collection: str, vector: List[float], limit: int):
    try:
        results = client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
            with_payload=True,
        )
        return [r.dict() for r in results]
    except UnexpectedResponse as exc:
        raise HTTPException(status_code=502, detail=f"Qdrant error: {exc}")
