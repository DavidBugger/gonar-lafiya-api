from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from enum import Enum


class LivestockType(str, Enum):
    cattle = "cattle"
    sheep  = "sheep"
    goat   = "goat"


# ── Prediction Request ───────────────────────────────────────────
class PredictionRequest(BaseModel):
    livestock_type: LivestockType = Field(..., description="Type of livestock")

    # Symptoms (all binary: 0 = No, 1 = Yes)
    fever:                int = Field(0, ge=0, le=1)
    blisters_mouth:       int = Field(0, ge=0, le=1)
    blisters_feet:        int = Field(0, ge=0, le=1)
    lameness:             int = Field(0, ge=0, le=1)
    drooling:             int = Field(0, ge=0, le=1)
    loss_of_appetite:     int = Field(0, ge=0, le=1)
    nasal_discharge:      int = Field(0, ge=0, le=1)
    coughing:             int = Field(0, ge=0, le=1)
    difficulty_breathing: int = Field(0, ge=0, le=1)
    chest_pain_signs:     int = Field(0, ge=0, le=1)
    weight_loss:          int = Field(0, ge=0, le=1)
    diarrhea:             int = Field(0, ge=0, le=1)
    eye_discharge:        int = Field(0, ge=0, le=1)
    mouth_sores:          int = Field(0, ge=0, le=1)
    sneezing:             int = Field(0, ge=0, le=1)
    skin_lesions:         int = Field(0, ge=0, le=1)
    swollen_lymph_nodes:  int = Field(0, ge=0, le=1)
    sudden_death:         int = Field(0, ge=0, le=1)
    weakness:             int = Field(0, ge=0, le=1)
    milk_reduction:       int = Field(0, ge=0, le=1)

    class Config:
        json_schema_extra = {
            "example": {
                "livestock_type": "cattle",
                "fever": 1,
                "blisters_mouth": 1,
                "blisters_feet": 1,
                "lameness": 1,
                "drooling": 1,
                "loss_of_appetite": 1,
                "nasal_discharge": 0,
                "coughing": 0,
                "difficulty_breathing": 0,
                "chest_pain_signs": 0,
                "weight_loss": 1,
                "diarrhea": 0,
                "eye_discharge": 0,
                "mouth_sores": 1,
                "sneezing": 0,
                "skin_lesions": 0,
                "swollen_lymph_nodes": 0,
                "sudden_death": 0,
                "weakness": 1,
                "milk_reduction": 0
            }
        }


# ── Prediction Response ──────────────────────────────────────────
class DiseaseInfo(BaseModel):
    name_en:      str
    name_ha:      str
    probability:  float
    confidence:   str   # High / Medium / Low


class PredictionResponse(BaseModel):
    success:          bool
    predicted_disease: str
    predicted_disease_hausa: str
    confidence:       str
    probability:      float
    all_probabilities: Dict[str, float]
    advice_en:        str
    advice_ha:        str
    severity:         str
    seek_vet:         bool


# ── Farmer Registration ──────────────────────────────────────────
class FarmerRegisterRequest(BaseModel):
    name:          str = Field(..., min_length=2, max_length=100)
    phone:         str = Field(..., min_length=10, max_length=15)
    village:       str = Field(..., min_length=2, max_length=100)
    state:         str = Field(..., min_length=2, max_length=50)
    livestock_types: List[LivestockType]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Musa Abdullahi",
                "phone": "08012345678",
                "village": "Gwaram",
                "state": "Kano",
                "livestock_types": ["cattle", "goat"]
            }
        }


class FarmerRegisterResponse(BaseModel):
    success:    bool
    farmer_id:  str
    message:    str
    message_ha: str


# ── Login & Profile ──────────────────────────────────────────────
class FarmerLoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)


class FarmerProfile(BaseModel):
    id: str
    name: str
    phone: str
    village: str
    state: str
    livestock_types: List[str]
    created_at: str


class FarmerLoginResponse(BaseModel):
    success: bool
    message: str
    message_ha: str
    profile: Optional[FarmerProfile] = None
