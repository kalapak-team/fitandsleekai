import io

import httpx
from fastapi import HTTPException, UploadFile
from PIL import Image


async def load_image_from_upload(file: UploadFile) -> Image.Image:
    data = await file.read()
    try:
        return Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image upload: {exc}")


async def load_image_from_url(url: str) -> Image.Image:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20.0)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download image from URL")
    try:
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Downloaded file is not a valid image")
