import pickle
import json
import os
from pathlib import Path

# ── Resolve model directory ──────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# ── Load model and encoders ──────────────────────────────────────
def load_model():
    model_path      = MODEL_DIR / "model.pkl"
    le_disease_path = MODEL_DIR / "le_disease.pkl"
    le_livestock_path = MODEL_DIR / "le_livestock.pkl"
    metadata_path   = MODEL_DIR / "model_metadata.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Please copy model.pkl, le_disease.pkl, le_livestock.pkl "
            "and model_metadata.json into the /models folder."
        )

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    with open(le_disease_path, "rb") as f:
        le_disease = pickle.load(f)

    with open(le_livestock_path, "rb") as f:
        le_livestock = pickle.load(f)

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    return model, le_disease, le_livestock, metadata


# ── Singleton – loaded once when app starts ──────────────────────
try:
    MODEL, LE_DISEASE, LE_LIVESTOCK, METADATA = load_model()
    print("✅ Model loaded successfully")
    print(f"   Model type  : {METADATA.get('model_type')}")
    print(f"   CV Accuracy : {METADATA.get('cv_accuracy', 'N/A')}")
    print(f"   Diseases    : {METADATA.get('diseases')}")
except FileNotFoundError as e:
    print(f"⚠️  WARNING: {e}")
    MODEL, LE_DISEASE, LE_LIVESTOCK, METADATA = None, None, None, {}
