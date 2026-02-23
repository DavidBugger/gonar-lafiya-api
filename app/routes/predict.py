from fastapi import APIRouter, HTTPException
from app.schemas import PredictionRequest, PredictionResponse
from app.model_loader import MODEL, LE_DISEASE, LE_LIVESTOCK, METADATA
from app.disease_info import DISEASE_INFO, get_confidence_label
import pandas as pd
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict_disease(request: PredictionRequest):
    """
    Predict livestock disease based on symptoms.
    Accepts livestock type and binary symptom inputs.
    Returns predicted disease in English and Hausa with advice.
    """

    if MODEL is None:
        raise HTTPException(
            status_code=503,
            detail="ML model is not loaded. Please check server configuration."
        )

    try:
        # ── 1. Encode livestock type ─────────────────────────────
        livestock_enc = LE_LIVESTOCK.transform([request.livestock_type.value])[0]

        # ── 2. Build feature vector in correct order ─────────────
        feature_cols = METADATA.get("symptoms", [])

        symptom_values = {
            "fever":                request.fever,
            "blisters_mouth":       request.blisters_mouth,
            "blisters_feet":        request.blisters_feet,
            "lameness":             request.lameness,
            "drooling":             request.drooling,
            "loss_of_appetite":     request.loss_of_appetite,
            "nasal_discharge":      request.nasal_discharge,
            "coughing":             request.coughing,
            "difficulty_breathing": request.difficulty_breathing,
            "chest_pain_signs":     request.chest_pain_signs,
            "weight_loss":          request.weight_loss,
            "diarrhea":             request.diarrhea,
            "eye_discharge":        request.eye_discharge,
            "mouth_sores":          request.mouth_sores,
            "sneezing":             request.sneezing,
            "skin_lesions":         request.skin_lesions,
            "swollen_lymph_nodes":  request.swollen_lymph_nodes,
            "sudden_death":         request.sudden_death,
            "weakness":             request.weakness,
            "milk_reduction":       request.milk_reduction,
        }

        # Build row: livestock_type first, then symptoms in metadata order
        row = [livestock_enc] + [symptom_values.get(s, 0) for s in feature_cols]
        all_feature_cols = ["livestock_type"] + feature_cols
        input_df = pd.DataFrame([row], columns=all_feature_cols)

        # ── 3. Predict ───────────────────────────────────────────
        pred_encoded   = MODEL.predict(input_df)[0]
        pred_proba_arr = MODEL.predict_proba(input_df)[0]
        disease_name   = LE_DISEASE.inverse_transform([pred_encoded])[0]

        # Build probability dictionary
        disease_classes = LE_DISEASE.classes_
        all_probs = {
            cls: round(float(prob), 4)
            for cls, prob in zip(disease_classes, pred_proba_arr)
        }

        top_probability = all_probs[disease_name]
        confidence      = get_confidence_label(top_probability)

        # ── 4. Get disease info & advice ─────────────────────────
        info = DISEASE_INFO.get(disease_name, DISEASE_INFO["Healthy"])

        return PredictionResponse(
            success=True,
            predicted_disease=info["name_en"],
            predicted_disease_hausa=info["name_ha"],
            confidence=confidence,
            probability=top_probability,
            all_probabilities=all_probs,
            advice_en=info["advice_en"],
            advice_ha=info["advice_ha"],
            severity=info["severity"],
            seek_vet=info["seek_vet"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.get("/symptoms", tags=["Prediction"])
def get_symptoms():
    """
    Returns the full list of symptoms in English and Hausa.
    Used by the Flutter app to build the symptom checklist UI.
    """
    symptoms_bilingual = [
        {"key": "fever",                "en": "Fever",                      "ha": "Zazzaɓi"},
        {"key": "blisters_mouth",       "en": "Blisters in Mouth",          "ha": "Kumburin Baki"},
        {"key": "blisters_feet",        "en": "Blisters on Feet",           "ha": "Kumburin Ƙafa"},
        {"key": "lameness",             "en": "Lameness / Difficulty Walking","ha": "Gurguwa / Wahalar Tafiya"},
        {"key": "drooling",             "en": "Excessive Drooling",         "ha": "Yawan Yawo na Miyau"},
        {"key": "loss_of_appetite",     "en": "Loss of Appetite",           "ha": "Rashin Son Abinci"},
        {"key": "nasal_discharge",      "en": "Nasal Discharge",            "ha": "Ruwan Hanci"},
        {"key": "coughing",             "en": "Coughing",                   "ha": "Tari"},
        {"key": "difficulty_breathing", "en": "Difficulty Breathing",       "ha": "Wahalar Numfashi"},
        {"key": "chest_pain_signs",     "en": "Signs of Chest Pain",        "ha": "Alamomin Ciwo a Ƙirji"},
        {"key": "weight_loss",          "en": "Weight Loss",                "ha": "Raguwar Nauyī"},
        {"key": "diarrhea",             "en": "Diarrhea",                   "ha": "Gudawa"},
        {"key": "eye_discharge",        "en": "Eye Discharge",              "ha": "Ruwan Ido"},
        {"key": "mouth_sores",          "en": "Mouth Sores",                "ha": "Rauni a Baki"},
        {"key": "sneezing",             "en": "Sneezing",                   "ha": "Atishawa"},
        {"key": "skin_lesions",         "en": "Skin Lesions / Sores",       "ha": "Rauni a Fata"},
        {"key": "swollen_lymph_nodes",  "en": "Swollen Lymph Nodes",        "ha": "Kumburi a Gland"},
        {"key": "sudden_death",         "en": "Sudden Deaths in Herd",      "ha": "Mutuwar Dabbobi Ba zato ba tsammani"},
        {"key": "weakness",             "en": "General Weakness",           "ha": "Gajiya / Raunin Jiki"},
        {"key": "milk_reduction",       "en": "Reduction in Milk Production","ha": "Raguwar Madara"},
    ]
    return {"success": True, "symptoms": symptoms_bilingual, "total": len(symptoms_bilingual)}


@router.get("/diseases", tags=["Prediction"])
def get_diseases():
    """Returns list of diseases the model can predict."""
    diseases = [
        {
            "key":      d,
            "name_en":  info["name_en"],
            "name_ha":  info["name_ha"],
            "severity": info["severity"]
        }
        for d, info in DISEASE_INFO.items()
    ]
    return {"success": True, "diseases": diseases}
