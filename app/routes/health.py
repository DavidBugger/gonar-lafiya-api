from fastapi import APIRouter
from app.model_loader import MODEL, METADATA
from datetime import datetime

router = APIRouter()


@router.get("/health")
def health_check():
    """API health check endpoint."""
    return {
        "status":      "ok",
        "model_loaded": MODEL is not None,
        "model_type":  METADATA.get("model_type", "Unknown"),
        "cv_accuracy": METADATA.get("cv_accuracy", "N/A"),
        "diseases":    METADATA.get("diseases", []),
        "timestamp":   datetime.utcnow().isoformat(),
        "message":     "Livestock Disease Prediction API is running smoothly"
    }
