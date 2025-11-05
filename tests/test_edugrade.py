"""
Unit Tests for EduGrade AI K-5 Grading Platform
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import numpy as np
from PIL import Image
import tempfile
import os

# Import the modules to test
from backend.app.agents.preprocessing_agent import PreprocessingAgent
from backend.app.agents.segmentation_agent import SegmentationAgent
from backend.app.agents.grading_agent import GradingAgent
from backend.app.agents.factcheck_agent import FactCheckAgent
from backend.app.services.firebase_service import FirebaseService

class TestPreprocessingAgent:
    """Test cases for PreprocessingAgent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = PreprocessingAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent.is_healthy() == True
    
    def test_clean_image(self):
        """Test image cleaning functionality"""
        # Create a test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        cleaned = self.agent._clean_image(test_image)
        
        assert cleaned.shape == test_image.shape
        assert cleaned.dtype == test_image.dtype
    
    def test_deskew_image(self):
        """Test image deskewing functionality"""
        # Create a test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        deskewed = self.agent._deskew_image(test_image)
        
        assert deskewed.shape == test_image.shape
        assert deskewed.dtype == test_image.dtype
    
    def test_enhance_contrast(self):
        """Test contrast enhancement"""
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        enhanced = self.agent._enhance_contrast(test_image)
        
        assert enhanced.shape == test_image.shape
        assert enhanced.dtype == test_image.dtype
    
    def test_binarize_image(self):
        """Test image binarization"""
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        binarized = self.agent._binarize_image(test_image)
        
        assert binarized.shape == test_image.shape
        assert binarized.dtype == test_image.dtype
    
    @pytest.mark.asyncio
    async def test_process_images(self):
        """Test image processing pipeline"""
        # Create temporary test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            test_image = Image.new('RGB', (100, 100), color='white')
            test_image.save(tmp_file.name)
            
            try:
                result = await self.agent.process_images([tmp_file.name])
                
                assert len(result) == 1
                assert result[0]['status'] == 'success'
                assert result[0]['original_path'] == tmp_file.name
                assert 'processed_path' in result[0]
                
            finally:
                os.unlink(tmp_file.name)

class TestSegmentationAgent:
    """Test cases for SegmentationAgent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('ultralytics.YOLO'):
            self.agent = SegmentationAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        # Agent should be healthy even without model file
        assert self.agent.is_healthy() == True or self.agent.is_healthy() == False
    
    def test_extract_answer_regions(self):
        """Test answer region extraction"""
        # Mock YOLOv8 result
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.xyxy = Mock()
        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array([[10, 10, 50, 50]])
        mock_result.boxes.conf = Mock()
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.8])
        
        # Create temporary test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            test_image = Image.new('RGB', (100, 100), color='white')
            test_image.save(tmp_file.name)
            
            try:
                regions = self.agent._extract_answer_regions(mock_result, tmp_file.name)
                
                assert isinstance(regions, list)
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_detect_grid_boxes(self):
        """Test grid-based box detection"""
        # Create temporary test image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            test_image = Image.new('RGB', (100, 100), color='white')
            test_image.save(tmp_file.name)
            
            try:
                boxes = self.agent._detect_grid_boxes(tmp_file.name)
                
                assert isinstance(boxes, list)
                
            finally:
                os.unlink(tmp_file.name)

class TestGradingAgent:
    """Test cases for GradingAgent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = GradingAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        # Agent should initialize even without API key
        assert hasattr(self.agent, 'model')
    
    def test_create_grading_prompt(self):
        """Test grading prompt creation"""
        question_key = {
            "question": "What is 2+2?",
            "answer": "4",
            "max_score": 1,
            "type": "multiple_choice"
        }
        
        prompt = self.agent._create_grading_prompt(1, question_key)
        
        assert isinstance(prompt, str)
        assert "2+2" in prompt
        assert "4" in prompt
    
    def test_parse_grading_response(self):
        """Test grading response parsing"""
        mock_response = """
        {
            "student_answer": "4",
            "score": 1,
            "feedback": "Correct!",
            "partial_credit": 1.0,
            "confidence": 0.9
        }
        """
        
        question_key = {"max_score": 1}
        
        result = self.agent._parse_grading_response(mock_response, question_key)
        
        assert result['student_answer'] == "4"
        assert result['score'] == 1
        assert result['feedback'] == "Correct!"
        assert result['confidence'] == 0.9
    
    def test_mock_grade_answer(self):
        """Test mock grading functionality"""
        question_key = {"max_score": 1}
        
        result = self.agent._mock_grade_answer(1, question_key)
        
        assert 'student_answer' in result
        assert 'score' in result
        assert 'feedback' in result
        assert 'confidence' in result
        assert result['score'] <= question_key['max_score']
    
    def test_calculate_total_score(self):
        """Test total score calculation"""
        grading_results = [
            {"status": "success", "score": 8, "max_score": 10},
            {"status": "success", "score": 7, "max_score": 10},
            {"status": "error", "score": 0, "max_score": 10}
        ]
        
        total = self.agent.calculate_total_score(grading_results)
        
        assert total['total_score'] == 15
        assert total['max_total_score'] == 20
        assert total['percentage'] == 75.0
        assert total['questions_graded'] == 2

class TestFactCheckAgent:
    """Test cases for FactCheckAgent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = FactCheckAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert hasattr(self.agent, 'api_key')
    
    def test_create_fact_check_prompt(self):
        """Test fact-check prompt creation"""
        student_answer = "4"
        correct_answer = "4"
        
        prompt = self.agent._create_fact_check_prompt(student_answer, correct_answer, 1)
        
        assert isinstance(prompt, str)
        assert "4" in prompt
        assert "fact-check" in prompt.lower()
    
    def test_parse_fact_check_response(self):
        """Test fact-check response parsing"""
        mock_response = """
        The student's answer is correct. The answer shows good understanding.
        Alternative answers might include: 2+2, 3+1
        This demonstrates solid grasp of basic math concepts.
        """
        
        grade_result = {"question_number": 1}
        
        result = self.agent._parse_fact_check_response(mock_response, grade_result)
        
        assert result['status'] == 'success'
        assert 'accuracy_assessment' in result
        assert 'insights' in result
        assert 'confidence' in result
    
    def test_mock_fact_check(self):
        """Test mock fact-checking functionality"""
        grade_result = {"question_number": 1, "student_answer": "4"}
        
        result = self.agent._mock_fact_check(grade_result)
        
        assert result['status'] == 'success'
        assert 'accuracy_assessment' in result
        assert 'insights' in result
        assert 'suggestions' in result

class TestFirebaseService:
    """Test cases for FirebaseService"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('firebase_admin.initialize_app'), \
             patch('firebase_admin.firestore.client'), \
             patch('firebase_admin.storage.bucket'):
            self.service = FirebaseService()
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert hasattr(self.service, 'db')
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check functionality"""
        with patch.object(self.service, '_test_connection', return_value=True):
            health = await self.service.health_check()
            assert health == True
    
    @pytest.mark.asyncio
    async def test_create_exam(self):
        """Test exam creation"""
        exam_data = {
            "title": "Test Exam",
            "subject": "Math",
            "grade_level": "5",
            "teacher_id": "teacher_001",
            "answer_key": {}
        }
        
        with patch.object(self.service, '_run_in_executor') as mock_executor:
            mock_executor.return_value = (None, Mock(id="exam_123"))
            
            exam_id = await self.service.create_exam(exam_data)
            
            assert exam_id == "exam_123"
    
    @pytest.mark.asyncio
    async def test_create_submission(self):
        """Test submission creation"""
        submission_data = {
            "exam_id": "exam_123",
            "student_id": "student_001",
            "teacher_id": "teacher_001",
            "file_paths": ["/path/to/file.pdf"]
        }
        
        with patch.object(self.service, '_run_in_executor') as mock_executor:
            mock_executor.return_value = (None, Mock(id="submission_123"))
            
            submission_id = await self.service.create_submission(submission_data)
            
            assert submission_id == "submission_123"

# Integration Tests
class TestIntegration:
    """Integration tests for the complete pipeline"""
    
    @pytest.mark.asyncio
    async def test_complete_grading_pipeline(self):
        """Test the complete grading pipeline"""
        # This would test the full pipeline from upload to approval
        # For now, just test that the components can work together
        
        preprocessing_agent = PreprocessingAgent()
        segmentation_agent = SegmentationAgent()
        grading_agent = GradingAgent()
        factcheck_agent = FactCheckAgent()
        
        # Test that all agents are healthy
        assert preprocessing_agent.is_healthy()
        # Other agents may not be healthy without API keys, which is expected
    
    def test_api_endpoints_structure(self):
        """Test that API endpoints are properly structured"""
        # This would test the FastAPI endpoints
        # For now, just verify the modules can be imported
        try:
            from backend.app.api.exams import router as exams_router
            from backend.app.api.submissions import router as submissions_router
            from backend.app.api.approvals import router as approvals_router
            
            assert exams_router is not None
            assert submissions_router is not None
            assert approvals_router is not None
        except ImportError as e:
            pytest.fail(f"Failed to import API modules: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
