"""
LangGraph workflow for the EduGrade AI application.

This file defines the LangGraph workflow that orchestrates the different
agents in the grading pipeline.
"""

from langgraph.graph import StateGraph, END
from .state import GradingState
from ..agents.preprocessing_agent import PreprocessingAgent
from ..agents.segmentation_agent import SegmentationAgent
from ..agents.grading_agent import GradingAgent
from ..agents.factcheck_agent import FactCheckAgent

def create_workflow():
    """
    Creates the LangGraph workflow for the grading pipeline.

    Returns:
        The compiled LangGraph workflow.
    """
    # Initialize agents
    preprocessing_agent = PreprocessingAgent()
    segmentation_agent = SegmentationAgent()
    grading_agent = GradingAgent()
    factcheck_agent = FactCheckAgent()


    # Build graph
    workflow = StateGraph(GradingState)

    workflow.add_node("preprocess", preprocessing_agent.process)
    workflow.add_node("segment", segmentation_agent.process)
    workflow.add_node("grade", grading_agent.process)
    workflow.add_node("fact_check", factcheck_agent.process)

    # Set up edges
    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "segment")
    workflow.add_edge("segment", "grade")
    workflow.add_edge("grade", "fact_check")
    workflow.add_edge("fact_check", END)


    return workflow.compile()
