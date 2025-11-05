"""
Firebase Service for Data Management
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage
import logging
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self, credentials_path: Optional[str] = None):
        self.db = None
        self.bucket = None
        self.is_healthy_flag = True
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialize_firebase(credentials_path)
    
    def _initialize_firebase(self, credentials_path: Optional[str] = None):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try to find credentials file
                if not credentials_path:
                    # Look for credentials in common locations
                    possible_paths = [
                        "config/firebase-credentials.json",
                        "config/firebase-credentials.json",
                        "firebase-credentials.json",
                        "serviceAccountKey.json"
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            credentials_path = path
                            break
                
                if credentials_path and os.path.exists(credentials_path):
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred)
                    logger.info(f"Firebase initialized with credentials from {credentials_path}")
                else:
                    # Try to use default credentials (for production)
                    firebase_admin.initialize_app()
                    logger.info("Firebase initialized with default credentials")
            
            self.db = firestore.client()
            
            # Initialize storage bucket if available
            try:
                self.bucket = storage.bucket()
                logger.info("Firebase Storage initialized")
            except Exception as e:
                logger.warning(f"Firebase Storage not available: {str(e)}")
            
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}")
            self.is_healthy_flag = False
    
    async def health_check(self) -> bool:
        """Check Firebase connection health"""
        try:
            # Try a simple read operation
            await self._run_in_executor(self._test_connection)
            return True
        except Exception as e:
            logger.error(f"Firebase health check failed: {str(e)}")
            return False
    
    def _test_connection(self):
        """Test Firebase connection"""
        if self.db:
            # Try to read from a test collection
            test_doc = self.db.collection('health_check').document('test').get()
            return True
        return False
    
    async def _run_in_executor(self, func, *args, **kwargs):
        """Run synchronous Firebase operations in executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    # Exam Management
    async def create_exam(self, exam_data: Dict[str, Any]) -> str:
        """Create a new exam"""
        try:
            exam_data['created_at'] = datetime.utcnow()
            exam_data['status'] = 'active'
            
            doc_ref = await self._run_in_executor(
                self.db.collection('exams').add, exam_data
            )
            
            exam_id = doc_ref[1].id
            logger.info(f"Created exam: {exam_id}")
            return exam_id
            
        except Exception as e:
            logger.error(f"Error creating exam: {str(e)}")
            raise
    
    async def get_exam(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """Get exam by ID"""
        try:
            doc = await self._run_in_executor(
                self.db.collection('exams').document(exam_id).get
            )
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = exam_id
                return data
            return None
            
        except Exception as e:
            logger.error(f"Error getting exam {exam_id}: {str(e)}")
            return None
    
    async def get_answer_key(self, exam_id: str) -> Dict[str, Any]:
        """Get answer key for an exam"""
        try:
            exam = await self.get_exam(exam_id)
            if exam and 'answer_key' in exam:
                return exam['answer_key']
            return {}
            
        except Exception as e:
            logger.error(f"Error getting answer key for {exam_id}: {str(e)}")
            return {}
    
    # Submission Management
    async def create_submission(self, submission_data: Dict[str, Any]) -> str:
        """Create a new submission"""
        try:
            submission_data['created_at'] = datetime.utcnow()
            submission_data['status'] = 'uploaded'
            submission_data['processing_stage'] = 'preprocessing'
            
            doc_ref = await self._run_in_executor(
                self.db.collection('submissions').add, submission_data
            )
            
            submission_id = doc_ref[1].id
            logger.info(f"Created submission: {submission_id}")
            return submission_id
            
        except Exception as e:
            logger.error(f"Error creating submission: {str(e)}")
            raise
    
    async def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission by ID"""
        try:
            doc = await self._run_in_executor(
                self.db.collection('submissions').document(submission_id).get
            )
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = submission_id
                return data
            return None
            
        except Exception as e:
            logger.error(f"Error getting submission {submission_id}: {str(e)}")
            return None
    
    async def update_submission_status(self, submission_id: str, status: str, stage: str = None):
        """Update submission status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if stage:
                update_data['processing_stage'] = stage
            
            await self._run_in_executor(
                self.db.collection('submissions').document(submission_id).update,
                update_data
            )
            
            logger.info(f"Updated submission {submission_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating submission status: {str(e)}")
            raise
    
    async def store_grading_results(self, submission_id: str, results: List[Dict[str, Any]]):
        """Store grading results for a submission"""
        try:
            # Calculate total score
            total_score = sum(r.get('score', 0) for r in results if r.get('status') == 'success')
            max_score = sum(r.get('max_score', 0) for r in results if r.get('status') == 'success')
            
            grading_data = {
                'results': results,
                'total_score': total_score,
                'max_score': max_score,
                'percentage': (total_score / max_score * 100) if max_score > 0 else 0,
                'graded_at': datetime.utcnow(),
                'status': 'graded'
            }
            
            await self._run_in_executor(
                self.db.collection('submissions').document(submission_id).update,
                grading_data
            )
            
            logger.info(f"Stored grading results for submission {submission_id}")
            
        except Exception as e:
            logger.error(f"Error storing grading results: {str(e)}")
            raise
    
    # Approval Management
    async def approve_submission(self, submission_id: str, teacher_id: str, 
                               overrides: Optional[Dict[str, Any]] = None) -> bool:
        """Approve a submission for parent viewing"""
        try:
            approval_data = {
                'approved': True,
                'approved_by': teacher_id,
                'approved_at': datetime.utcnow(),
                'status': 'approved'
            }
            
            if overrides:
                approval_data['teacher_overrides'] = overrides
            
            await self._run_in_executor(
                self.db.collection('submissions').document(submission_id).update,
                approval_data
            )
            
            logger.info(f"Submission {submission_id} approved by teacher {teacher_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving submission: {str(e)}")
            return False
    
    async def get_pending_approvals(self, teacher_id: str) -> List[Dict[str, Any]]:
        """Get submissions pending teacher approval"""
        try:
            query = await self._run_in_executor(
                self.db.collection('submissions')
                .where('status', '==', 'pending_review')
                .where('teacher_id', '==', teacher_id)
                .get
            )
            
            submissions = []
            for doc in query:
                data = doc.to_dict()
                data['id'] = doc.id
                submissions.append(data)
            
            return submissions
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {str(e)}")
            return []
    
    # Parent Reports
    async def get_student_reports(self, student_id: str) -> List[Dict[str, Any]]:
        """Get approved reports for a student"""
        try:
            query = await self._run_in_executor(
                self.db.collection('submissions')
                .where('student_id', '==', student_id)
                .where('status', '==', 'approved')
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .get
            )
            
            reports = []
            for doc in query:
                data = doc.to_dict()
                data['id'] = doc.id
                reports.append(data)
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting student reports: {str(e)}")
            return []
    
    # File Storage
    async def upload_file(self, file_path: str, destination_path: str) -> str:
        """Upload file to Firebase Storage"""
        try:
            if not self.bucket:
                logger.warning("Firebase Storage not available")
                return file_path
            
            blob = self.bucket.blob(destination_path)
            
            await self._run_in_executor(blob.upload_from_filename, file_path)
            
            # Make blob publicly accessible
            blob.make_public()
            
            url = blob.public_url
            logger.info(f"Uploaded file to: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return file_path
    
    # User Management
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        try:
            user_data['created_at'] = datetime.utcnow()
            user_data['role'] = user_data.get('role', 'teacher')
            
            doc_ref = await self._run_in_executor(
                self.db.collection('users').add, user_data
            )
            
            user_id = doc_ref[1].id
            logger.info(f"Created user: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            doc = await self._run_in_executor(
                self.db.collection('users').document(user_id).get
            )
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = user_id
                return data
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user (simplified - in production use Firebase Auth)"""
        try:
            query = await self._run_in_executor(
                self.db.collection('users')
                .where('email', '==', email)
                .where('password', '==', password)  # In production, use proper auth
                .get
            )
            
            if query:
                doc = query[0]
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
