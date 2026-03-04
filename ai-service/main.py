import os
from typing import List

from dotenv import load_dotenv
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.model_loader import get_model
from app.qdrant_logic import get_qdrant_client, search_vectors
from utils.image_helper import load_image_from_upload, load_image_from_url
from app.sync_service import run_sync

load_dotenv()

app = FastAPI(title="FitAndSleek AI Service", version="1.0.0")

allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "products")
QDRANT_SEARCH_LIMIT = int(os.getenv("QDRANT_SEARCH_LIMIT", "5"))

model = get_model()
qdrant_client = get_qdrant_client()


@app.get("/")
async def health():
    return {"status": "ok"}


@app.get("/verify-cloud")
async def verify_cloud():
    try:
        info = qdrant_client.get_collection(collection_name=QDRANT_COLLECTION)
        return {"qdrant": "connected", "points_count": getattr(info, "points_count", None)}
    except Exception as exc:
        return {"qdrant": "error", "message": str(exc)}


@app.post("/scan-to-search")
async def scan_to_search(file: UploadFile = File(...)):
    try:
        img = await load_image_from_upload(file)
        vector = model.encode(img).tolist()
        results = search_vectors(qdrant_client, QDRANT_COLLECTION, vector, QDRANT_SEARCH_LIMIT)
        return {"results": results}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/scan-to-search-url")
async def scan_to_search_url(data: dict = Body(...)):
    image_url = data.get("url")
    if not image_url or not isinstance(image_url, str):
        raise HTTPException(status_code=400, detail="`url` is required")

    try:
        img = await load_image_from_url(image_url)
        vector = model.encode(img).tolist()
        results = search_vectors(qdrant_client, QDRANT_COLLECTION, vector, QDRANT_SEARCH_LIMIT)
        return {"results": results}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))