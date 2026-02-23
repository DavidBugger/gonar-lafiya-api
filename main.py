from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import predict, health, farmer

app = FastAPI(
    title="Livestock Disease Prediction API",
    description="API for predicting livestock diseases for Hausa-speaking farmers in Northern Nigeria",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allow requests from Flutter mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(farmer.router, prefix="/api/v1", tags=["Farmer"])


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Livestock Disease Prediction API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }
