from fastapi import APIRouter, HTTPException
from app.schemas import (
    FarmerRegisterRequest, FarmerRegisterResponse, 
    FarmerLoginRequest, FarmerLoginResponse, FarmerProfile,
    FarmersListResponse
)
from typing import List
import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path

router = APIRouter()

DB_PATH = Path(__file__).resolve().parent.parent.parent / "livestock_app.db"


# ── Database setup ───────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id            TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            phone         TEXT UNIQUE NOT NULL,
            village       TEXT NOT NULL,
            state         TEXT NOT NULL,
            livestock_types TEXT NOT NULL,
            created_at    TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                TEXT PRIMARY KEY,
            farmer_id         TEXT,
            livestock_type    TEXT NOT NULL,
            symptoms          TEXT NOT NULL,
            predicted_disease TEXT NOT NULL,
            confidence        TEXT NOT NULL,
            probability       REAL NOT NULL,
            seek_vet          INTEGER NOT NULL,
            timestamp         TEXT NOT NULL,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    """)

    conn.commit()
    conn.close()


# Initialize DB on import
init_db()


# ── Farmer Registration ──────────────────────────────────────────
@router.post("/farmer/register", response_model=FarmerRegisterResponse)
def register_farmer(request: FarmerRegisterRequest):
    """Register a new farmer in the system."""
    conn = get_db()
    try:
        farmer_id  = str(uuid.uuid4())[:8].upper()
        created_at = datetime.utcnow().isoformat()
        livestock  = json.dumps([lt.value for lt in request.livestock_types])

        conn.execute("""
            INSERT INTO farmers (id, name, phone, village, state, livestock_types, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (farmer_id, request.name, request.phone,
              request.village, request.state, livestock, created_at))
        conn.commit()

        return FarmerRegisterResponse(
            success=True,
            farmer_id=farmer_id,
            message=f"Farmer '{request.name}' registered successfully. Your ID is {farmer_id}.",
            message_ha=f"An yi rajista ga '{request.name}' cikin nasara. ID ɗinka shine {farmer_id}."
        )

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="A farmer with this phone number is already registered."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# ── Save Prediction to History ───────────────────────────────────
@router.post("/farmer/save-prediction")
def save_prediction(
    farmer_id: str,
    livestock_type: str,
    symptoms: dict,
    predicted_disease: str,
    confidence: str,
    probability: float,
    seek_vet: bool
):
    """Save a prediction result to the farmer's history."""
    conn = get_db()
    try:
        pred_id   = str(uuid.uuid4())[:12]
        timestamp = datetime.utcnow().isoformat()

        conn.execute("""
            INSERT INTO predictions
            (id, farmer_id, livestock_type, symptoms, predicted_disease, confidence, probability, seek_vet, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred_id, farmer_id, livestock_type,
            json.dumps(symptoms), predicted_disease,
            confidence, probability, int(seek_vet), timestamp
        ))
        conn.commit()
        return {"success": True, "prediction_id": pred_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# ── Get Farmer History ───────────────────────────────────────────
@router.get("/farmer/{farmer_id}/history")
def get_farmer_history(farmer_id: str):
    """Get prediction history for a specific farmer."""
    conn = get_db()
    try:
        # Verify farmer exists
        farmer = conn.execute(
            "SELECT * FROM farmers WHERE id = ?", (farmer_id,)
        ).fetchone()

        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found.")

        predictions = conn.execute(
            """SELECT id, livestock_type, predicted_disease, confidence, probability, seek_vet, timestamp
               FROM predictions WHERE farmer_id = ? ORDER BY timestamp DESC LIMIT 20""",
            (farmer_id,)
        ).fetchall()

        history = [
            {
                "id":               row["id"],
                "livestock_type":   row["livestock_type"],
                "predicted_disease": row["predicted_disease"],
                "confidence":       row["confidence"],
                "probability":      row["probability"],
                "seek_vet":         bool(row["seek_vet"]),
                "timestamp":        row["timestamp"]
            }
            for row in predictions
        ]

        return {
            "success":    True,
            "farmer_id":  farmer_id,
            "farmer_name": farmer["name"],
            "total":      len(history),
            "history":    history
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# ── Get Farmer Profile ───────────────────────────────────────────
@router.get("/farmer/{farmer_id}/profile")
def get_farmer_profile(farmer_id: str):
    """Get farmer profile details."""
    conn = get_db()
    try:
        farmer = conn.execute(
            "SELECT * FROM farmers WHERE id = ?", (farmer_id,)
        ).fetchone()

        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found.")

        return {
            "success":        True,
            "id":             farmer["id"],
            "name":           farmer["name"],
            "phone":          farmer["phone"],
            "village":        farmer["village"],
            "state":          farmer["state"],
            "livestock_types": json.loads(farmer["livestock_types"]),
            "created_at":     farmer["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
# ── Farmer Login ────────────────────────────────────────────────
@router.post("/farmer/login", response_model=FarmerLoginResponse)
def login_farmer(request: FarmerLoginRequest):
    """Retrieve farmer profile by phone number (Login)."""
    conn = get_db()
    try:
        farmer = conn.execute(
            "SELECT * FROM farmers WHERE phone = ?", (request.phone,)
        ).fetchone()

        if not farmer:
            return FarmerLoginResponse(
                success=False,
                message="No farmer found with this phone number.",
                message_ha="Ba a sami manomin da ke da wannan lambar waya ba.",
                profile=None
            )

        profile = FarmerProfile(
            id=farmer["id"],
            name=farmer["name"],
            phone=farmer["phone"],
            village=farmer["village"],
            state=farmer["state"],
            livestock_types=json.loads(farmer["livestock_types"]),
            created_at=farmer["created_at"]
        )

        return FarmerLoginResponse(
            success=True,
            message="Login successful.",
            message_ha="An shiga cikin nasara.",
            profile=profile
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# ── List All Farmers ───────────────────────────────────────────
@router.get("/farmers", response_model=FarmersListResponse)
def list_farmers():
    """Retrieve all registered farmers."""
    conn = get_db()
    try:
        farmers_data = conn.execute(
            "SELECT * FROM farmers ORDER BY created_at DESC"
        ).fetchall()

        farmers = [
            FarmerProfile(
                id=row["id"],
                name=row["name"],
                phone=row["phone"],
                village=row["village"],
                state=row["state"],
                livestock_types=json.loads(row["livestock_types"]),
                created_at=row["created_at"]
            )
            for row in farmers_data
        ]

        return FarmersListResponse(
            success=True,
            total=len(farmers),
            farmers=farmers
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
