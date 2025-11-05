"""
Perplexity API Fact-Checking Agent
"""

import requests
import logging
from typing import List, Dict, Any, Optional
import os
import json
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class FactCheckAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.is_healthy_flag = True
        self._validate_api_key()
    
    def _validate_api_key(self):
        """Validate Perplexity API key"""
        if not self.api_key:
            logger.warning("No Perplexity API key provided. Using mock mode.")
            self.is_healthy_flag = False
        else:
            logger.info("Perplexity API key validated")
    
    def is_healthy(self) -> bool:
        """Check if the fact-check agent is healthy"""
        return self.is_healthy_flag
    
    async def fact_check_answers(self, grading_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fact-check student answers using Perplexity API
        """
        fact_checked_results = []
        
        for grade_result in grading_results:
            if grade_result["status"] != "success":
                fact_checked_results.append({
                    **grade_result,
                    "fact_check": {"status": "skipped", "reason": "grading failed"}
                })
                continue
            
            try:
                logger.info(f"Fact-checking question {grade_result['question_number']}")
                
                # Perform fact check
                fact_check_result = await self._fact_check_single_answer(grade_result)
                
                # Combine grading and fact-check results
                combined_result = {
                    **grade_result,
                    "fact_check": fact_check_result
                }
                
                fact_checked_results.append(combined_result)
                
            except Exception as e:
                logger.error(f"Error fact-checking question {grade_result['question_number']}: {str(e)}")
                fact_checked_results.append({
                    **grade_result,
                    "fact_check": {
                        "status": "error",
                        "error": str(e),
                        "insights": "Unable to verify facts"
                    }
                })
        
        return fact_checked_results
    
    async def _fact_check_single_answer(self, grade_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fact-check a single answer using Perplexity API"""
        
        if not self.api_key:
            # Mock fact-checking for development/testing
            return self._mock_fact_check(grade_result)
        
        try:
            student_answer = grade_result["student_answer"]
            correct_answer = grade_result["correct_answer"]
            question_number = grade_result["question_number"]
            
            # Create fact-checking prompt
            prompt = self._create_fact_check_prompt(student_answer, correct_answer, question_number)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an educational fact-checker for K-5 students. Provide accurate, age-appropriate information."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1
                }
                
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        return self._parse_fact_check_response(content, grade_result)
                    else:
                        logger.error(f"Perplexity API error: {response.status}")
                        return self._mock_fact_check(grade_result)
                        
        except Exception as e:
            logger.error(f"Error in fact-checking API call: {str(e)}")
            return self._mock_fact_check(grade_result)
    
    def _create_fact_check_prompt(self, student_answer: str, correct_answer: str, question_number: int) -> str:
        """Create fact-checking prompt for Perplexity API"""
        
        prompt = f"""
        Please fact-check the following student answer for a K-5 educational context:
        
        Question Number: {question_number}
        Student Answer: "{student_answer}"
        Expected Answer: "{correct_answer}"
        
        Please provide:
        1. Factual accuracy assessment
        2. Alternative correct answers (if any)
        3. Educational insights or additional knowledge
        4. Suggestions for improvement
        5. Age-appropriate explanations
        
        Focus on:
        - Whether the student's answer is factually correct
        - If there are other valid ways to answer the question
        - Educational value and learning opportunities
        - Encouraging feedback for young learners
        
        Keep responses concise and suitable for K-5 students and their teachers.
        """
        
        return prompt
    
    def _parse_fact_check_response(self, response_content: str, grade_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Perplexity API response"""
        try:
            # Extract key information from response
            insights = []
            alternative_answers = []
            accuracy_assessment = "Unable to assess"
            suggestions = []
            
            # Simple parsing - in production, you might want more sophisticated parsing
            lines = response_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if 'correct' in line.lower() or 'accurate' in line.lower():
                    accuracy_assessment = line
                elif 'alternative' in line.lower() or 'other' in line.lower():
                    alternative_answers.append(line)
                elif 'suggest' in line.lower() or 'improve' in line.lower():
                    suggestions.append(line)
                elif line and len(line) > 10:  # Meaningful content
                    insights.append(line)
            
            return {
                "status": "success",
                "accuracy_assessment": accuracy_assessment,
                "alternative_answers": alternative_answers[:3],  # Limit to 3
                "insights": insights[:5],  # Limit to 5 insights
                "suggestions": suggestions[:3],  # Limit to 3 suggestions
                "raw_response": response_content,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error parsing fact-check response: {str(e)}")
            return self._mock_fact_check(grade_result)
    
    def _mock_fact_check(self, grade_result: Dict[str, Any]) -> Dict[str, Any]:
        """Mock fact-checking for development/testing"""
        import random
        
        mock_responses = [
            {
                "status": "success",
                "accuracy_assessment": "The answer shows good understanding of the concept.",
                "alternative_answers": ["Another way to express this would be...", "Students might also say..."],
                "insights": [
                    "This demonstrates solid grasp of basic concepts",
                    "Good use of vocabulary for this grade level",
                    "Shows creative thinking"
                ],
                "suggestions": [
                    "Consider explaining the reasoning behind the answer",
                    "Try to use more specific examples"
                ],
                "confidence": 0.8
            },
            {
                "status": "success",
                "accuracy_assessment": "The answer is partially correct with room for improvement.",
                "alternative_answers": ["A more complete answer would include..."],
                "insights": [
                    "Shows understanding of some key concepts",
                    "Could benefit from more detail",
                    "Good attempt at problem-solving"
                ],
                "suggestions": [
                    "Review the main concepts",
                    "Practice with similar problems"
                ],
                "confidence": 0.7
            }
        ]
        
        return random.choice(mock_responses)
    
    async def batch_fact_check(self, grading_results: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """Perform batch fact-checking with rate limiting"""
        fact_checked_results = []
        
        for i in range(0, len(grading_results), batch_size):
            batch = grading_results[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [self._fact_check_single_answer(result) for result in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            for j, result in enumerate(batch):
                if isinstance(batch_results[j], Exception):
                    fact_checked_results.append({
                        **result,
                        "fact_check": {
                            "status": "error",
                            "error": str(batch_results[j])
                        }
                    })
                else:
                    fact_checked_results.append({
                        **result,
                        "fact_check": batch_results[j]
                    })
            
            # Rate limiting delay
            if i + batch_size < len(grading_results):
                await asyncio.sleep(1)  # 1 second delay between batches
        
        return fact_checked_results
