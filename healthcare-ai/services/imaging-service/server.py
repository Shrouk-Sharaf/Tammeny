# services/imaging-service/server.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from inference import analyze_xray_image
from postproc import format_imaging_results
import uuid
from datetime import datetime
from io import BytesIO

app = FastAPI(
    title="Medical Imaging Service",
    description="AI-powered medical image analysis for X-Rays",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Medical Imaging Service", 
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/models")
async def get_available_models():
    """Return available imaging models"""
    return {
        "models": [
            {
                "id": "chest-xray-nih",
                "name": "Chest X-Ray Analyzer",
                "type": "classification",
                "description": "Detects 14 thoracic conditions from chest X-rays using NIH-trained DenseNet",
                "input_types": ["image/jpeg", "image/png"],
                "max_size_mb": 10
            }
        ]
    }

@app.post("/analyze/xray")
async def analyze_xray(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.5,  # ✅ Make sure this is 0.5, not 0.1
    include_visualization: bool = False
):
    """Analyze chest X-ray image for thoracic conditions"""
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(
                400, 
                f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # ✅ FIX: Read the file content properly for Streamlit uploads
        file_content = await file.read()
        
        # Create a file-like object from the content
        image_file = BytesIO(file_content)
        
        # Validate file size (10MB max)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(400, "File too large. Maximum size is 10MB")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())[:8]
        
        print(f"🔍 Analyzing X-Ray {analysis_id}...")
        print(f"📁 File info: {file.filename}, Size: {len(file_content)} bytes")
        print(f"🎯 Confidence threshold: {confidence_threshold}")  # ✅ Debug print
        
        # Perform analysis - pass the BytesIO object AND the confidence threshold
        raw_results = await analyze_xray_image(
            image_file,  # Now passing BytesIO instead of UploadFile
            confidence_threshold=confidence_threshold  # ✅ Pass the threshold
        )
        
        # Format results
        formatted_results = format_imaging_results(
            raw_results, 
            analysis_id,
            include_visualization=include_visualization
        )
        
        return JSONResponse(content=formatted_results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "imaging",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)