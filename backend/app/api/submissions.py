"""
API Endpoints for Submission Management
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status, BackgroundTasks
from typing import List, Optional
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

from ..services.firebase_service import FirebaseService
from ..services.grading_service import grading_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class SubmissionResponse(BaseModel):
    id: str
    exam_id: str
    student_id: str
    student_name: str
    teacher_id: str
    image_url: str
    status: str
    created_at: datetime

class SubmissionStatus(BaseModel):
    status: str
    error_message: Optional[str] = None

# Dependency injection
def get_firebase_service() -> FirebaseService:
    return FirebaseService()

# Create uploads directory
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/submissions/", response_model=SubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_submission(
    background_tasks: BackgroundTasks,
    exam_id: str = Form(...),
    student_id: str = Form(...),
    student_name: str = Form(...),
    teacher_id: str = Form(...),
    files: List[UploadFile] = File(...),
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Upload answer sheets and create submission. Grading will run in the background."""
    try:
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

        file = files[0]
        allowed_types = ["image/jpeg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file type: {file.content_type}")

        submission_id = str(uuid.uuid4())

        file_extension = Path(file.filename).suffix
        filename = f"{submission_id}{file_extension}"
        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"Saved file: {file_path}")

        submission_data = {
            "exam_id": exam_id,
            "student_id": student_id,
            "student_name": student_name,
            "teacher_id": teacher_id,
            "image_url": str(file_path),
            "status": "processing",
            "created_at": datetime.utcnow()
        }

        await firebase.create_submission(submission_id, submission_data)

        background_tasks.add_task(grading_service.grade_submission, submission_id)

        return SubmissionResponse(id=submission_id, **submission_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating submission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create submission: {str(e)}")

@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get submission by ID"""
    try:
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

        return SubmissionResponse(id=submission_id, **submission)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission {submission_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get submission: {str(e)}")

@router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Delete a submission"""
    try:
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

        if 'image_url' in submission and submission['image_url']:
            file_path = submission['image_url']
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")

        await firebase.delete_submission(submission_id)

        return {"message": "Submission deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting submission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete submission: {str(e)}")
