import threading

from sentence_transformers import SentenceTransformer

_MODEL = None
_LOCK = threading.Lock()
MODEL_NAME = "clip-ViT-B-32"


def get_model() -> SentenceTransformer:
    """Load the CLIP model once per process."""
    global _MODEL
    if _MODEL is None:
        with _LOCK:
            if _MODEL is None:
                _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL
