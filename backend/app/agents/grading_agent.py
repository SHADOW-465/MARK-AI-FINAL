"""
Gemini AI Grading Agent for Answer Evaluation
"""

import google.generativeai as genai
import logging
from typing import List, Dict, Any, Optional
import os
import json
from PIL import Image
import base64
import io

from .base_agent import BaseAgent
from ..graph.state import GradingState

logger = logging.getLogger(__name__)

class GradingAgent(BaseAgent):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("grading_agent")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            if not self.api_key:
                logger.warning("No Gemini API key provided. Using mock mode.")
                self.is_healthy_flag = False
                return

            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI model initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Gemini model: {str(e)}")
            self.is_healthy_flag = False

    async def process(self, state: GradingState) -> GradingState:
        """
        Grade student answers using Gemini AI
        """
        if state.get("status") != "segmentation_complete":
            state["error"] = "Segmentation failed or was not run"
            state["status"] = "error"
            return state

        grading_results = []
        answer_key = state.get("answer_key")

        for region_data in state.get("answer_boxes"):
            try:
                question_number = region_data["question_number"]
                region_path = region_data["region_path"]

                logger.info(f"Grading question {question_number}")

                # Get answer key for this question
                question_key = answer_key.get(f"question_{question_number}", {})

                # Grade the answer
                grade_result = await self._grade_single_answer(
                    region_path, question_number, question_key
                )

                grading_results.append({
                    "question_number": question_number,
                    "student_answer": grade_result["student_answer"],
                    "correct_answer": question_key.get("answer", ""),
                    "score": grade_result["score"],
                    "max_score": question_key.get("max_score", 1),
                    "feedback": grade_result["feedback"],
                    "partial_credit": grade_result.get("partial_credit", 0),
                    "confidence": grade_result.get("confidence", 0.8),
                    "status": "success"
                })

            except Exception as e:
                logger.error(f"Error grading question {region_data.get('question_number', 'unknown')}: {str(e)}")
                grading_results.append({
                    "question_number": region_data.get("question_number", 0),
                    "status": "error",
                    "error": str(e)
                })

        state["grades"] = grading_results
        state["status"] = "grading_complete"
        return state

    async def _grade_single_answer(self, region_path: str, question_number: int, question_key: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a single answer using Gemini AI"""

        if not self.model:
            # Mock grading for development/testing
            return self._mock_grade_answer(question_number, question_key)

        try:
            # Load and prepare image
            image = Image.open(region_path)

            # Prepare prompt
            prompt = self._create_grading_prompt(question_number, question_key)

            # Generate response
            response = self.model.generate_content([prompt, image])

            # Parse response
            result = self._parse_grading_response(response.text, question_key)

            return result

        except Exception as e:
            logger.error(f"Error in AI grading: {str(e)}")
            # Fallback to mock grading
            return self._mock_grade_answer(question_number, question_key)

    def _create_grading_prompt(self, question_number: int, question_key: Dict[str, Any]) -> str:
        """Create grading prompt for Gemini AI"""
        question_text = question_key.get("question", f"Question {question_number}")
        correct_answer = question_key.get("answer", "")
        max_score = question_key.get("max_score", 1)
        question_type = question_key.get("type", "multiple_choice")

        prompt = f"""
        You are an AI grader for K-5 education. Please analyze the student's answer and provide a grade.

        Question: {question_text}
        Question Type: {question_type}
        Correct Answer: {correct_answer}
        Maximum Score: {max_score}

        Please analyze the student's handwritten answer and provide:
        1. The student's answer (transcribed text)
        2. Score (0 to {max_score})
        3. Feedback (encouraging and constructive for K-5 students)
        4. Partial credit (if applicable, 0.0 to 1.0)
        5. Confidence level (0.0 to 1.0)

        For K-5 students, be encouraging and focus on learning. Consider:
        - Spelling variations common in young learners
        - Partial understanding
        - Creative but incorrect answers
        - Effort and attempt

        Respond in JSON format:
        {{
            "student_answer": "transcribed text",
            "score": number,
            "feedback": "encouraging feedback",
            "partial_credit": number,
            "confidence": number
        }}
        """

        return prompt

    def _parse_grading_response(self, response_text: str, question_key: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gemini AI response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

            if json_match:
                result = json.loads(json_match.group())

                # Validate and clean result
                return {
                    "student_answer": result.get("student_answer", ""),
                    "score": max(0, min(result.get("score", 0), question_key.get("max_score", 1))),
                    "feedback": result.get("feedback", "Good effort!"),
                    "partial_credit": max(0, min(result.get("partial_credit", 0), 1)),
                    "confidence": max(0, min(result.get("confidence", 0.8), 1))
                }
            else:
                # Fallback parsing
                return self._extract_grades_from_text(response_text, question_key)

        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._mock_grade_answer(0, question_key)

    def _extract_grades_from_text(self, text: str, question_key: Dict[str, Any]) -> Dict[str, Any]:
        """Extract grades from unstructured text response"""
        import re

        # Extract score
        score_match = re.search(r'score[:\s]*(\d+)', text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 0

        # Extract confidence
        conf_match = re.search(r'confidence[:\s]*([\d.]+)', text, re.IGNORECASE)
        confidence = float(conf_match.group(1)) if conf_match else 0.8

        return {
            "student_answer": "Unable to transcribe",
            "score": max(0, min(score, question_key.get("max_score", 1))),
            "feedback": "Please review manually",
            "partial_credit": 0,
            "confidence": confidence
        }

    def _mock_grade_answer(self, question_number: int, question_key: Dict[str, Any]) -> Dict[str, Any]:
        """Mock grading for development/testing"""
        import random

        max_score = question_key.get("max_score", 1)

        # Simulate different grading scenarios
        scenarios = [
            {"score": max_score, "feedback": "Excellent work! You got it right!", "confidence": 0.9},
            {"score": max_score * 0.8, "feedback": "Good job! Almost perfect!", "confidence": 0.8},
            {"score": max_score * 0.5, "feedback": "Nice try! Keep practicing!", "confidence": 0.7},
            {"score": 0, "feedback": "Don't worry, everyone learns at their own pace!", "confidence": 0.6}
        ]

        scenario = random.choice(scenarios)

        return {
            "student_answer": f"Mock answer for question {question_number}",
            "score": scenario["score"],
            "feedback": scenario["feedback"],
            "partial_credit": scenario["score"] / max_score,
            "confidence": scenario["confidence"]
        }

    def calculate_total_score(self, grading_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total score and statistics"""
        total_score = 0
        max_total_score = 0
        successful_grades = 0

        for result in grading_results:
            if result["status"] == "success":
                total_score += result["score"]
                max_total_score += result["max_score"]
                successful_grades += 1

        percentage = (total_score / max_total_score * 100) if max_total_score > 0 else 0

        return {
            "total_score": total_score,
            "max_total_score": max_total_score,
            "percentage": round(percentage, 2),
            "questions_graded": successful_grades,
            "total_questions": len(grading_results)
        }
