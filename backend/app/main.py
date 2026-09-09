from fastapi import FastAPI
from api.inference import router as inference_router
from api.history import router as history_router

app = FastAPI(
    title="VEDA API",
    description="Vehicle Evaluation & Diagnostics Agent API",
    version="1.0.0"
)

app.include_router(inference_router, prefix="/api/v1/inference", tags=["inference"])
app.include_router(history_router, prefix="/api/v1", tags=["history"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
