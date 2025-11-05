"""
API Endpoints for Exam Management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from pydantic import BaseModel

from ..services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class ExamCreate(BaseModel):
    title: str
    subject: str
    grade_level: str
    teacher_id: str
    answer_key: Dict[str, Any]
    instructions: Optional[str] = None

class ExamResponse(BaseModel):
    id: str
    title: str
    subject: str
    grade_level: str
    teacher_id: str
    answer_key: Dict[str, Any]
    instructions: Optional[str]
    created_at: datetime
    status: str

class AnswerKeyItem(BaseModel):
    question_number: int
    question: str
    answer: str
    max_score: int
    question_type: str = "multiple_choice"

# Dependency injection
def get_firebase_service() -> FirebaseService:
    return FirebaseService()

@router.post("/exams/", response_model=ExamResponse)
async def create_exam(
    exam: ExamCreate,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Create a new exam with answer key"""
    try:
        exam_data = exam.dict()
        exam_id = await firebase.create_exam(exam_data)
        
        # Return the created exam
        created_exam = await firebase.get_exam(exam_id)
        return ExamResponse(**created_exam)
        
    except Exception as e:
        logger.error(f"Error creating exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create exam: {str(e)}"
        )

@router.get("/exams/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get exam by ID"""
    try:
        exam = await firebase.get_exam(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        return ExamResponse(**exam)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exam {exam_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get exam: {str(e)}"
        )

@router.get("/exams/teacher/{teacher_id}", response_model=List[ExamResponse])
async def get_teacher_exams(
    teacher_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get all exams for a teacher"""
    try:
        # This would need to be implemented in FirebaseService
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting teacher exams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teacher exams: {str(e)}"
        )

@router.put("/exams/{exam_id}/answer-key")
async def update_answer_key(
    exam_id: str,
    answer_key: Dict[str, Any],
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Update answer key for an exam"""
    try:
        # Check if exam exists
        exam = await firebase.get_exam(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        # Update answer key
        await firebase.db.collection('exams').document(exam_id).update({
            'answer_key': answer_key,
            'updated_at': datetime.utcnow()
        })
        
        return {"message": "Answer key updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating answer key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update answer key: {str(e)}"
        )

@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Delete an exam"""
    try:
        # Check if exam exists
        exam = await firebase.get_exam(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        # Delete exam
        await firebase.db.collection('exams').document(exam_id).delete()
        
        return {"message": "Exam deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting exam: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete exam: {str(e)}"
        )

@router.get("/exams/{exam_id}/answer-key")
async def get_answer_key(
    exam_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get answer key for an exam"""
    try:
        answer_key = await firebase.get_answer_key(exam_id)
        if not answer_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer key not found"
            )
        
        return {"answer_key": answer_key}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting answer key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get answer key: {str(e)}"
        )
