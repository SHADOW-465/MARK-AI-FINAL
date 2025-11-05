"""
API Endpoints for Grade Approval Management
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
class GradeOverride(BaseModel):
    question_number: int
    new_score: float
    new_feedback: str
    reason: str

class ApprovalRequest(BaseModel):
    teacher_id: str
    overrides: Optional[List[GradeOverride]] = None
    comments: Optional[str] = None

class ApprovalResponse(BaseModel):
    submission_id: str
    approved: bool
    approved_by: str
    approved_at: datetime
    teacher_overrides: Optional[List[GradeOverride]] = None
    comments: Optional[str] = None

class SubmissionReview(BaseModel):
    submission_id: str
    student_name: str
    exam_title: str
    total_score: float
    max_score: float
    percentage: float
    results: List[Dict[str, Any]]
    status: str
    created_at: datetime

# Dependency injection
def get_firebase_service() -> FirebaseService:
    return FirebaseService()

@router.post("/approve/{submission_id}", response_model=ApprovalResponse)
async def approve_submission(
    submission_id: str,
    approval_request: ApprovalRequest,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Approve a submission for parent viewing"""
    try:
        # Check if submission exists
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Check if submission is ready for approval
        if submission.get('status') != 'pending_review':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Submission is not ready for approval. Current status: {submission.get('status')}"
            )
        
        # Check if teacher has permission
        if submission.get('teacher_id') != approval_request.teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teacher does not have permission to approve this submission"
            )
        
        # Apply teacher overrides if any
        overrides_data = None
        if approval_request.overrides:
            overrides_data = [override.dict() for override in approval_request.overrides]
            
            # Update submission results with overrides
            await _apply_teacher_overrides(submission_id, approval_request.overrides, firebase)
        
        # Approve submission
        success = await firebase.approve_submission(
            submission_id,
            approval_request.teacher_id,
            overrides_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve submission"
            )
        
        # Get updated submission
        updated_submission = await firebase.get_submission(submission_id)
        
        return ApprovalResponse(
            submission_id=submission_id,
            approved=True,
            approved_by=approval_request.teacher_id,
            approved_at=updated_submission.get('approved_at', datetime.utcnow()),
            teacher_overrides=approval_request.overrides,
            comments=approval_request.comments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve submission: {str(e)}"
        )

@router.get("/approve/pending/{teacher_id}", response_model=List[SubmissionReview])
async def get_pending_approvals(
    teacher_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get submissions pending teacher approval"""
    try:
        pending_submissions = await firebase.get_pending_approvals(teacher_id)
        
        reviews = []
        for submission in pending_submissions:
            # Get exam details
            exam = await firebase.get_exam(submission.get('exam_id'))
            exam_title = exam.get('title', 'Unknown Exam') if exam else 'Unknown Exam'
            
            review = SubmissionReview(
                submission_id=submission['id'],
                student_name=submission.get('student_name', 'Unknown Student'),
                exam_title=exam_title,
                total_score=submission.get('total_score', 0),
                max_score=submission.get('max_score', 0),
                percentage=submission.get('percentage', 0),
                results=submission.get('results', []),
                status=submission.get('status', 'unknown'),
                created_at=submission.get('created_at', datetime.utcnow())
            )
            reviews.append(review)
        
        return reviews
        
    except Exception as e:
        logger.error(f"Error getting pending approvals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending approvals: {str(e)}"
        )

@router.put("/approve/{submission_id}/override")
async def override_grade(
    submission_id: str,
    override: GradeOverride,
    teacher_id: str = Depends(lambda: "teacher_id"),  # In production, get from auth
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Override a specific grade before approval"""
    try:
        # Check if submission exists
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Check if teacher has permission
        if submission.get('teacher_id') != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teacher does not have permission to override this submission"
            )
        
        # Apply override
        await _apply_teacher_overrides(submission_id, [override], firebase)
        
        return {"message": "Grade override applied successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error overriding grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to override grade: {str(e)}"
        )

@router.get("/reports/{student_id}")
async def get_student_reports(
    student_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get approved reports for a student (parent view)"""
    try:
        reports = await firebase.get_student_reports(student_id)
        
        # Format reports for parent view
        formatted_reports = []
        for report in reports:
            formatted_report = {
                "submission_id": report['id'],
                "exam_title": "Unknown Exam",  # Would need to fetch from exam
                "student_name": report.get('student_name', 'Unknown Student'),
                "total_score": report.get('total_score', 0),
                "max_score": report.get('max_score', 0),
                "percentage": report.get('percentage', 0),
                "results": report.get('results', []),
                "approved_at": report.get('approved_at'),
                "teacher_feedback": report.get('teacher_feedback', '')
            }
            formatted_reports.append(formatted_report)
        
        return {
            "student_id": student_id,
            "reports": formatted_reports,
            "total_reports": len(formatted_reports)
        }
        
    except Exception as e:
        logger.error(f"Error getting student reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student reports: {str(e)}"
        )

@router.get("/reports/{student_id}/{submission_id}")
async def get_single_report(
    student_id: str,
    submission_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """Get a single approved report for a student"""
    try:
        submission = await firebase.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Check if it's approved and belongs to the student
        if submission.get('status') != 'approved':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not approved yet"
            )
        
        if submission.get('student_id') != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Report does not belong to this student"
            )
        
        # Get exam details
        exam = await firebase.get_exam(submission.get('exam_id'))
        
        return {
            "submission_id": submission_id,
            "student_id": student_id,
            "exam_title": exam.get('title', 'Unknown Exam') if exam else 'Unknown Exam',
            "student_name": submission.get('student_name', 'Unknown Student'),
            "total_score": submission.get('total_score', 0),
            "max_score": submission.get('max_score', 0),
            "percentage": submission.get('percentage', 0),
            "results": submission.get('results', []),
            "approved_at": submission.get('approved_at'),
            "teacher_feedback": submission.get('teacher_feedback', ''),
            "fact_check_insights": submission.get('fact_check_insights', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting single report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report: {str(e)}"
        )

async def _apply_teacher_overrides(
    submission_id: str, 
    overrides: List[GradeOverride], 
    firebase: FirebaseService
):
    """Apply teacher overrides to submission results"""
    try:
        submission = await firebase.get_submission(submission_id)
        if not submission or 'results' not in submission:
            return
        
        results = submission['results']
        
        # Apply overrides
        for override in overrides:
            question_num = override.question_number
            for i, result in enumerate(results):
                if result.get('question_number') == question_num:
                    results[i]['score'] = override.new_score
                    results[i]['feedback'] = override.new_feedback
                    results[i]['teacher_override'] = True
                    results[i]['override_reason'] = override.reason
                    break
        
        # Recalculate total score
        total_score = sum(r.get('score', 0) for r in results if r.get('status') == 'success')
        max_score = sum(r.get('max_score', 0) for r in results if r.get('status') == 'success')
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Update submission
        await firebase.db.collection('submissions').document(submission_id).update({
            'results': results,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
            'teacher_overrides_applied': True,
            'overrides_applied_at': datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Error applying teacher overrides: {str(e)}")
        raise
