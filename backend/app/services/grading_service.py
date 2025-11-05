"""
Grading service for the EduGrade AI application.

This service orchestrates the entire grading workflow, from retrieving the
submission data to executing the LangGraph workflow and updating the database
with the final results.
"""

from .firebase_service import FirebaseService
from ..graph.workflow import create_workflow
from ..graph.state import GradingState
import logging

logger = logging.getLogger(__name__)

class GradingService:
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.workflow = create_workflow()

    async def grade_submission(self, submission_id: str):
        """
        Grades a submission.

        Args:
            submission_id: The ID of the submission to grade.
        """
        logger.info(f"Starting grading for submission {submission_id}")

        # Retrieve submission and exam data from Firebase
        submission = self.firebase_service.get_submission(submission_id)
        if not submission:
            logger.error(f"Submission {submission_id} not found.")
            return

        exam = self.firebase_service.get_exam(submission["exam_id"])
        if not exam:
            logger.error(f"Exam {submission['exam_id']} not found for submission {submission_id}.")
            return

        # Initialize workflow with state
        initial_state = GradingState(
            submission_id=submission_id,
            exam_id=submission["exam_id"],
            image_path=submission["image_url"],
            answer_key=exam["answer_key"],
            status="pending",
            preprocessed_image=None,
            answer_boxes=None,
            cropped_answers=None,
            ocr_results=None,
            grades=None,
            feedback=None,
            error=None
        )

        # Execute LangGraph workflow
        final_state = await self.workflow.ainvoke(initial_state)

        # Update Firebase with results
        self.firebase_service.update_submission(submission_id, {"status": final_state['status'], "grades": final_state['grades']})
        logger.info(f"Finished grading for submission {submission_id}")

grading_service = GradingService()
