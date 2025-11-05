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

@app.post("/api/v1/process/{submission_id}")
async def process_submission(submission_id: str):
    """
    Process a submission through the complete pipeline:
    1. Preprocessing
    2. Segmentation
    3. AI Grading
    4. Fact Checking
    """
    try:
        # Get submission from Firebase
        submission = await firebase_service.get_submission(submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Update status to processing
        await firebase_service.update_submission_status(submission_id, "processing")
        
        # Step 1: Preprocessing
        logger.info(f"Starting preprocessing for submission {submission_id}")
        preprocessed_images = await preprocessing_agent.process_images(submission['file_paths'])
        
        # Step 2: Segmentation
        logger.info(f"Starting segmentation for submission {submission_id}")
        segmented_regions = await segmentation_agent.segment_answers(preprocessed_images)
        
        # Step 3: AI Grading
        logger.info(f"Starting AI grading for submission {submission_id}")
        answer_key = await firebase_service.get_answer_key(submission['exam_id'])
        grades = await grading_agent.grade_answers(segmented_regions, answer_key)
        
        # Step 4: Fact Checking
        logger.info(f"Starting fact checking for submission {submission_id}")
        fact_checked_results = await factcheck_agent.fact_check_answers(grades)
        
        # Store results in Firebase
        await firebase_service.store_grading_results(submission_id, fact_checked_results)
        
        # Update status to pending review
        await firebase_service.update_submission_status(submission_id, "pending_review")
        
        return {
            "message": "Submission processed successfully",
            "submission_id": submission_id,
            "status": "pending_review",
            "results": fact_checked_results
        }
        
    except Exception as e:
        logger.error(f"Error processing submission {submission_id}: {str(e)}")
        await firebase_service.update_submission_status(submission_id, "error")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
