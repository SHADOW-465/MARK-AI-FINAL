"""
EduGrade AI K-5 Grading Platform - FastAPI Main Application
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import logging
from datetime import datetime
import os

from .agents.preprocessing_agent import PreprocessingAgent
from .agents.segmentation_agent import SegmentationAgent
from .agents.grading_agent import GradingAgent
from .agents.factcheck_agent import FactCheckAgent
from .services.firebase_service import FirebaseService
from .api.exams import router as exams_router
from .api.submissions import router as submissions_router
from .api.approvals import router as approvals_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EduGrade AI K-5 Grading Platform",
    description="AI-powered grading system for K-5 education",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
firebase_service = FirebaseService()
preprocessing_agent = PreprocessingAgent()
segmentation_agent = SegmentationAgent()
grading_agent = GradingAgent()
factcheck_agent = FactCheckAgent()

# Include routers
app.include_router(exams_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(approvals_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "EduGrade AI K-5 Grading Platform", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "firebase": await firebase_service.health_check(),
            "preprocessing": preprocessing_agent.is_healthy(),
            "segmentation": segmentation_agent.is_healthy(),
            "grading": grading_agent.is_healthy(),
            "factcheck": factcheck_agent.is_healthy()
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
