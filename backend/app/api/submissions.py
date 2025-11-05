"""
API Endpoints for Submission Management
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import List, Dict, Any, Optional
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

from ..services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class SubmissionCreate(BaseModel):
    exam_id: str
    student_id: str
    student_name: str
    teacher_id: str

class SubmissionResponse(BaseModel):
    id: str
    exam_id: str
    student_id: str
    student_name: str
    teacher_id: str
    file_paths: List[str]
    status: str
    processing_stage: str
    created_at: datetime

class SubmissionStatus(BaseModel):
    status: str
    processing_stage: Optional[str] = None
    error_message: Optional[str] = None

# Dependency injection
def get_firebase_service() -> FirebaseService:
    return FirebaseService()

# Create uploads directory
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/submissions/", response_model=SubmissionResponse)
async def create_submission(
    exam_id: str = Form(...),
    student_id: str = Form(...),
    student_name: str = Form(...),
    teacher_id: str = Form(...),
    files: List[UploadFile] = File(...),
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Upload answer sheets and create submission"""
    try:
        # Validate files
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded"
            )
        
        # Check file types
        allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        for file in files:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type: {file.content_type}. Allowed: {allowed_types}"
                )
        
        # Generate unique submission ID
        submission_id = str(uuid.uuid4())
        
        # Save uploaded files
        file_paths = []
        for file in files:
            # Generate unique filename
            file_extension = Path(file.filename).suffix
            filename = f"{submission_id}_{file.filename}"
            file_path = UPLOAD_DIR / filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            file_paths.append(str(file_path))
            logger.info(f"Saved file: {file_path}")
        
        # Create submission record
        submission_data = {
            "exam_id": exam_id,
            "student_id": student_id,
            "student_name": student_name,
            "teacher_id": teacher_id,
            "file_paths": file_paths,
            "status": "uploaded",
            "processing_stage": "preprocessing"
        }
        
        submission_id = await firebase.create_submission(submission_data)
        
        # Return submission info
        submission = await firebase.get_submission(submission_id)
        return SubmissionResponse(**submission)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create submission: {str(e)}"
        )

@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get submission by ID"""
    try:
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        return SubmissionResponse(**submission)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission {submission_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submission: {str(e)}"
        )

@router.get("/submissions/teacher/{teacher_id}", response_model=List[SubmissionResponse])
async def get_teacher_submissions(
    teacher_id: str,
    status_filter: Optional[str] = None,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get all submissions for a teacher"""
    try:
        # This would need to be implemented in FirebaseService
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting teacher submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teacher submissions: {str(e)}"
        )

@router.get("/submissions/student/{student_id}", response_model=List[SubmissionResponse])
async def get_student_submissions(
    student_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get all submissions for a student"""
    try:
        # This would need to be implemented in FirebaseService
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting student submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student submissions: {str(e)}"
        )

@router.put("/submissions/{submission_id}/status")
async def update_submission_status(
    submission_id: str,
    status_update: SubmissionStatus,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Update submission status"""
    try:
        # Check if submission exists
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Update status
        await firebase.update_submission_status(
            submission_id, 
            status_update.status, 
            status_update.processing_stage
        )
        
        return {"message": "Submission status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating submission status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update submission status: {str(e)}"
        )

@router.get("/submissions/{submission_id}/results")
async def get_submission_results(
    submission_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get grading results for a submission"""
    try:
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Check if results exist
        if 'results' not in submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grading results not found"
            )
        
        return {
            "submission_id": submission_id,
            "results": submission['results'],
            "total_score": submission.get('total_score', 0),
            "max_score": submission.get('max_score', 0),
            "percentage": submission.get('percentage', 0),
            "graded_at": submission.get('graded_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submission results: {str(e)}"
        )

@router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Delete a submission"""
    try:
        # Check if submission exists
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Delete associated files
        for file_path in submission.get('file_paths', []):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete file {file_path}: {str(e)}")
        
        # Delete submission record
        await firebase.db.collection('submissions').document(submission_id).delete()
        
        return {"message": "Submission deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete submission: {str(e)}"
        )
