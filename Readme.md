# 🐄 GonarLafiya — Livestock Disease Prediction API

> **"Gonar Lafiya"** means *"Farm of Health"* in Hausa.  
> An AI-powered REST API that helps Hausa-speaking farmers in Northern Nigeria detect livestock diseases early by analysing animal symptoms.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [ML Model](#ml-model)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Environment & Configuration](#environment--configuration)
- [Deployment (Render)](#deployment-render)
- [Database Schema](#database-schema)
- [Supported Diseases](#supported-diseases)
- [Symptom List](#symptom-list)
- [Contributing](#contributing)

---

## Overview

GonarLafiya is the backend service for a mobile-first livestock health application built for Hausa-speaking farmers in Northern Nigeria. Farmers can describe the symptoms their cattle, sheep, or goats are showing and receive an instant AI-powered disease prediction — complete with advice in both **English and Hausa**.

The API is built with **FastAPI** and powered by a **Random Forest** machine learning model trained to classify three major livestock diseases: FMD, CBPP, and PPR — or return a *healthy* verdict.

---

## Features

- 🤖 **AI Disease Prediction** — Symptom-based disease classification using a Random Forest model (99.81% cross-validated accuracy)
- 🌍 **Bilingual Responses** — All predictions and advice returned in both English and Hausa (`ha`)
- 👨‍🌾 **Farmer Management** — Register farmers and persist their prediction history
- 📋 **Symptom Checklist API** — Dynamic symptom list endpoint used to render UI in the Flutter mobile app
- 🏥 **Severity & Vet Referral** — Each prediction includes a severity level (`None / High / Critical`) and a `seek_vet` flag
- 📊 **Probability Breakdown** — Full probability scores returned for all disease classes
- ❤️ **Health Check** — Endpoint for monitoring model load status and API health

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) 0.131+ |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| ML / Data | scikit-learn, XGBoost, pandas, numpy |
| Deep Learning | TensorFlow / Keras |
| Geospatial | GeoPandas, Rasterio, Folium |
| Data Validation | Pydantic v2 |
| Database | SQLite (via Python `sqlite3`) |
| Deployment | [Render](https://render.com/) |
| Mobile Client | Flutter (external) |

---

## Project Structure

```
backend/
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── render.yaml              # Render deployment config
├── livestock_app.db         # SQLite database (auto-created)
│
├── app/
│   ├── __init__.py
│   ├── schemas.py           # Pydantic request/response models
│   ├── model_loader.py      # Loads ML model + label encoders
│   ├── disease_info.py      # Disease metadata (EN + Hausa advice)
│   └── routes/
│       ├── __init__.py
│       ├── health.py        # GET /api/v1/health
│       ├── predict.py       # POST /api/v1/predict, GET /api/v1/symptoms, GET /api/v1/diseases
│       └── farmer.py        # Farmer registration & history endpoints
│
└── models/
    ├── model.pkl            # Trained Random Forest model
    ├── le_disease.pkl       # Label encoder for disease classes
    ├── le_livestock.pkl     # Label encoder for livestock types
    └── model_metadata.json  # Model accuracy, features, and disease list
```

---

## ML Model

| Property | Value |
|---|---|
| Model Type | Random Forest Classifier |
| Training Accuracy | 100% |
| Cross-Validated Accuracy | **99.81%** (± 0.0015) |
| Feature Count | 21 (1 livestock type + 20 symptoms) |
| Target Classes | CBPP, FMD, Healthy, PPR |
| Supported Livestock | Cattle, Goat, Sheep |

The model is loaded at startup from `models/model.pkl` together with two `LabelEncoder` files for livestock types and disease classes.

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### 🔍 Root

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Returns API status and links to docs |

---

### ❤️ Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Model load status, accuracy, disease list, timestamp |

**Sample Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "Random Forest",
  "cv_accuracy": 0.9981,
  "diseases": ["CBPP", "FMD", "Healthy", "PPR"],
  "timestamp": "2026-02-23T16:00:00.000000",
  "message": "Livestock Disease Prediction API is running smoothly"
}
```

---

### 🤖 Prediction

#### `POST /api/v1/predict`

Predict the disease based on symptoms.

**Request Body:**
```json
{
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
```

> All symptom fields are **binary integers**: `1` = present, `0` = absent. They default to `0` if omitted.

**Response:**
```json
{
  "success": true,
  "predicted_disease": "Foot-and-Mouth Disease (FMD)",
  "predicted_disease_hausa": "Cutar Ƙafa da Baki (FMD)",
  "confidence": "High",
  "probability": 0.97,
  "all_probabilities": {
    "CBPP": 0.01,
    "FMD": 0.97,
    "Healthy": 0.01,
    "PPR": 0.01
  },
  "advice_en": "1. Immediately isolate the affected animal...",
  "advice_ha": "1. Nan da nan ka ware dabbar...",
  "severity": "High",
  "seek_vet": true
}
```

**Confidence Levels:**

| Probability | Confidence |
|---|---|
| ≥ 0.80 | High |
| 0.55 – 0.79 | Medium |
| < 0.55 | Low |

---

#### `GET /api/v1/symptoms`

Returns all 20 supported symptoms in English and Hausa. Used by the Flutter app to dynamically render the symptom checklist.

**Sample Response:**
```json
{
  "success": true,
  "total": 20,
  "symptoms": [
    { "key": "fever", "en": "Fever", "ha": "Zazzaɓi" },
    { "key": "coughing", "en": "Coughing", "ha": "Tari" }
  ]
}
```

---

#### `GET /api/v1/diseases`

Returns all disease classes the model can predict, with English name, Hausa name, and severity rating.

---

### 👨‍🌾 Farmer

#### `POST /api/v1/farmer/register`

Register a new farmer. Phone number must be unique.

**Request Body:**
```json
{
  "name": "Musa Abdullahi",
  "phone": "08012345678",
  "village": "Gwaram",
  "state": "Kano",
  "livestock_types": ["cattle", "goat"]
}
```

**Response:**
```json
{
  "success": true,
  "farmer_id": "A3F9BC12",
  "message": "Farmer 'Musa Abdullahi' registered successfully. Your ID is A3F9BC12.",
  "message_ha": "An yi rajista ga 'Musa Abdullahi' cikin nasara. ID ɗinka shine A3F9BC12."
}
```

---

#### `POST /api/v1/farmer/save-prediction`

Save a prediction result to a farmer's history.

**Query Parameters:** `farmer_id`, `livestock_type`, `predicted_disease`, `confidence`, `probability`, `seek_vet`  
**Body:** `symptoms` (dict)

---

#### `GET /api/v1/farmer/{farmer_id}/history`

Fetch the last 20 predictions for a given farmer.

---

#### `GET /api/v1/farmer/{farmer_id}/profile`

Fetch a farmer's registered profile details.

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip`

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the development server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: [http://localhost:8000](http://localhost:8000)

### 5. Explore the interactive docs

| URL | Description |
|---|---|
| [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI |
| [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc UI |

---

## Environment & Configuration

No environment variables are required to run the project locally. The SQLite database (`livestock_app.db`) is automatically created on first startup.

For production deployments, update the CORS `allow_origins` in `main.py` to restrict access to your mobile app's domain:

```python
# main.py
allow_origins=["https://your-app-domain.com"],
```

---

## Deployment (Render)

This project is configured for one-click deployment to [Render](https://render.com/) using the included `render.yaml` file.

```yaml
services:
  - type: web
    name: gonar-lafiya-api
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Steps:**
1. Push the repository to GitHub.
2. Create a new **Web Service** on Render and connect the repository.
3. Render will auto-detect `render.yaml` and configure the service.
4. The service will be live at: `https://gonar-lafiya-api.onrender.com`

---

## Database Schema

The SQLite database uses two tables, auto-created at startup:

### `farmers`

| Column | Type | Description |
|---|---|---|
| `id` | TEXT (PK) | 8-character uppercase UUID |
| `name` | TEXT | Farmer's full name |
| `phone` | TEXT (UNIQUE) | Phone number |
| `village` | TEXT | Farmer's village |
| `state` | TEXT | Farmer's state |
| `livestock_types` | TEXT | JSON array of livestock types |
| `created_at` | TEXT | ISO 8601 timestamp |

### `predictions`

| Column | Type | Description |
|---|---|---|
| `id` | TEXT (PK) | 12-character UUID |
| `farmer_id` | TEXT (FK) | References `farmers.id` |
| `livestock_type` | TEXT | Cattle / Goat / Sheep |
| `symptoms` | TEXT | JSON object of symptom flags |
| `predicted_disease` | TEXT | Predicted disease key |
| `confidence` | TEXT | High / Medium / Low |
| `probability` | REAL | Confidence score (0–1) |
| `seek_vet` | INTEGER | 1 = Yes, 0 = No |
| `timestamp` | TEXT | ISO 8601 timestamp |

---

## Supported Diseases

| Key | English Name | Hausa Name | Severity |
|---|---|---|---|
| `FMD` | Foot-and-Mouth Disease | Cutar Ƙafa da Baki | High |
| `CBPP` | Contagious Bovine Pleuropneumonia | Cutar Huhu ta Shanu | Critical |
| `PPR` | Peste des Petits Ruminants | Cutar Ƙananan Dabbobi (Sangaya) | High |
| `Healthy` | No Disease Detected | Babu Cuta (Lafiya) | None |

---

## Symptom List

The model accepts **20 binary symptom features** (0 = absent, 1 = present):

| Key | English | Hausa |
|---|---|---|
| `fever` | Fever | Zazzaɓi |
| `blisters_mouth` | Blisters in Mouth | Kumburin Baki |
| `blisters_feet` | Blisters on Feet | Kumburin Ƙafa |
| `lameness` | Lameness / Difficulty Walking | Gurguwa / Wahalar Tafiya |
| `drooling` | Excessive Drooling | Yawan Yawo na Miyau |
| `loss_of_appetite` | Loss of Appetite | Rashin Son Abinci |
| `nasal_discharge` | Nasal Discharge | Ruwan Hanci |
| `coughing` | Coughing | Tari |
| `difficulty_breathing` | Difficulty Breathing | Wahalar Numfashi |
| `chest_pain_signs` | Signs of Chest Pain | Alamomin Ciwo a Ƙirji |
| `weight_loss` | Weight Loss | Raguwar Nauyī |
| `diarrhea` | Diarrhea | Gudawa |
| `eye_discharge` | Eye Discharge | Ruwan Ido |
| `mouth_sores` | Mouth Sores | Rauni a Baki |
| `sneezing` | Sneezing | Atishawa |
| `skin_lesions` | Skin Lesions / Sores | Rauni a Fata |
| `swollen_lymph_nodes` | Swollen Lymph Nodes | Kumburi a Gland |
| `sudden_death` | Sudden Deaths in Herd | Mutuwar Dabbobi Ba zato ba tsammani |
| `weakness` | General Weakness | Gajiya / Raunin Jiki |
| `milk_reduction` | Reduction in Milk Production | Raguwar Madara |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

*Built with ❤️ to improve livestock health outcomes for farmers in Northern Nigeria.*