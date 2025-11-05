"""
LangGraph workflow for the EduGrade AI application.

This file defines the LangGraph workflow that orchestrates the different
agents in the grading pipeline.
"""

from langgraph.graph import StateGraph, END
from .state import GradingState
from ..agents.preprocessing_agent import PreprocessingAgent
from ..agents.segmentation_agent import SegmentationAgent
from ..agents.ocr_agent import OCRAgent
from ..agents.grading_agent import GradingAgent
from ..agents.feedback_agent import FeedbackAgent
from ..agents.storage_agent import StorageAgent
from ..config import get_settings

settings = get_settings()

def create_workflow():
    """
    Creates the LangGraph workflow for the grading pipeline.

    Returns:
        The compiled LangGraph workflow.
    """
    # Initialize agents
    preprocessing_agent = PreprocessingAgent()
    segmentation_agent = SegmentationAgent(model_path=settings.MODELS_DIR + "/" + settings.YOLO_MODEL)
    ocr_agent = OCRAgent(deepseek_api_key=settings.PERPLEXITY_API_KEY) # Placeholder for deepseek key
    grading_agent = GradingAgent(api_key=settings.OPENAI_API_KEY)
    feedback_agent = FeedbackAgent(api_key=settings.OPENAI_API_KEY)
    # Storage agent needs a db session, which will be passed during invocation

    # Define nodes
    def preprocess_node(state: GradingState) -> GradingState:
        """
        The node for the preprocessing agent.
        """
        result = preprocessing_agent.process(state['image_path'])
        state['preprocessed_image'] = result['preprocessed_image']
        state['status'] = 'preprocessed'
        return state

    def segment_node(state: GradingState) -> GradingState:
        """
        The node for the segmentation agent.
        """
        result = segmentation_agent.process(state['preprocessed_image'])
        state['answer_boxes'] = result['answer_boxes']
        state['cropped_answers'] = result['cropped_answers']
        state['status'] = 'segmented'
        return state

    def ocr_node(state: GradingState) -> GradingState:
        """
        The node for the OCR agent.
        """
        result = ocr_agent.process(state['cropped_answers'])
        state['ocr_results'] = result['ocr_results']
        state['status'] = 'ocr_completed'
        return state

    def grade_node(state: GradingState) -> GradingState:
        """
        The node for the grading agent.
        """
        # Prepare data for grading agent
        answers_to_grade = []
        for i, ocr_result in enumerate(state['ocr_results']):
            answer_key_item = state['answer_key'][i]
            answers_to_grade.append({
                "student_answer": ocr_result['text'],
                "model_answer": answer_key_item['model_answer'],
                "rubric": answer_key_item['rubric_text'],
                "max_marks": answer_key_item['max_marks'],
                "subject": "Unknown" # This should be passed in the state
            })

        result = grading_agent.process(answers_to_grade)
        state['grades'] = result['grades']
        state['status'] = 'graded'
        return state

    def feedback_node(state: GradingState) -> GradingState:
        """
        The node for the feedback agent.
        """
        # This needs more info like student name, overall score etc.
        # This is a simplified version.
        state['status'] = 'feedback_generated'
        return state

    def storage_node(state: GradingState) -> GradingState:
        """
        The node for the storage agent.
        """
        # The storage agent will be called from the service layer,
        # as it needs a db session.
        state['status'] = 'completed'
        return state

    def error_handler_node(state: GradingState) -> GradingState:
        """
        The node for the error handler.
        """
        state['status'] = 'failed'
        return state

    # Build graph
    workflow = StateGraph(GradingState)
    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("segment", segment_node)
    workflow.add_node("ocr", ocr_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("feedback", feedback_node)
    workflow.add_node("storage", storage_node)
    workflow.add_node("error_handler", error_handler_node)

    # Set up edges
    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "segment")
    workflow.add_edge("segment", "ocr")
    workflow.add_edge("ocr", "grade")
    workflow.add_edge("grade", "feedback")
    workflow.add_edge("feedback", "storage")
    workflow.add_edge("storage", END)

    # Add error handling (simplified)
    # A more robust implementation would have conditional edges based on agent output status
    # For now, we'll assume a linear flow.

    return workflow.compile()
