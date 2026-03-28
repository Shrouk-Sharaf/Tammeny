import uuid
from io import BytesIO
from datetime import datetime

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from inference import analyze_xray_image
from postproc import format_imaging_results

app = FastAPI(
    title="Tammeny Imaging Service",
    description="AI-powered chest X-ray analysis (DenseNet-121 / NIH)",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MAX_SIZE_MB   = 10


@app.get("/")
async def root():
    return {"service": "Tammeny Imaging Service", "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/models")
async def models():
    return {
        "models": [
            {
                "id": "chest-xray-nih",
                "name": "Chest X-Ray Analyzer",
                "architecture": "DenseNet-121",
                "training_data": "NIH ChestX-ray14",
                "conditions": 14,
                "input_formats": list(ALLOWED_TYPES),
                "max_size_mb": MAX_SIZE_MB,
            }
        ]
    }


@app.post("/analyze/xray")
async def analyze_xray(
    file: UploadFile = File(...),
    confidence_threshold: float = Query(default=0.5, ge=0.1, le=0.99),
    include_visualization: bool = Query(default=False),
):
    # Validate type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            400,
            f"Unsupported file type '{file.content_type}'. Allowed: {', '.join(ALLOWED_TYPES)}",
        )

    file_bytes = await file.read()

    # Validate size
    if len(file_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large. Maximum is {MAX_SIZE_MB} MB.")

    analysis_id = str(uuid.uuid4())[:8]
    print(f"[{analysis_id}] Analysing '{file.filename}' | {len(file_bytes)/1024:.1f} KB | threshold={confidence_threshold}")

    try:
        raw = await analyze_xray_image(BytesIO(file_bytes), confidence_threshold)
        result = format_imaging_results(raw, analysis_id, include_visualization)
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)
