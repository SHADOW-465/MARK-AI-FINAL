"""
State definition for the LangGraph workflow.

This file defines the shared state that is passed between the different
agents in the grading pipeline.
"""

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
import numpy as np

class GradingState(TypedDict):
    """
    The shared state for the grading workflow.

    Attributes:
        submission_id: The ID of the submission being graded.
        exam_id: The ID of the exam for the submission.
        image_path: The path to the answer sheet image.
        answer_key: The answer key for the exam.
        preprocessed_image: The preprocessed answer sheet image.
        answer_boxes: The detected answer boxes.
        cropped_answers: The cropped answer images.
        ocr_results: The OCR results for the answer images.
        grades: The grades for the submission.
        feedback: The personalized feedback for the student.
        status: The current status of the grading process.
        error: Any error message that occurred during the grading process.
    """
    submission_id: int
    exam_id: int
    image_path: str
    answer_key: List[Dict[str, Any]]
    preprocessed_image: Optional[np.ndarray]
    answer_boxes: Optional[List[Dict[str, Any]]]
    cropped_answers: Optional[List[np.ndarray]]
    ocr_results: Optional[List[Dict[str, Any]]]
    grades: Optional[List[Dict[str, Any]]]
    feedback: Optional[str]
    status: str
    error: Optional[str]
