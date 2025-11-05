"""
EduGrade AI K-5 Grading Platform - Streamlit Dashboard
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="EduGrade AI K-5 Grading Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

class EduGradeAPI:
    """API client for EduGrade backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return {}
    
    def create_exam(self, exam_data: Dict[str, Any]) -> str:
        """Create a new exam"""
        response = self._make_request("POST", "/exams/", json=exam_data)
        return response.get("id", "")
    
    def get_exam(self, exam_id: str) -> Dict[str, Any]:
        """Get exam by ID"""
        return self._make_request("GET", f"/exams/{exam_id}")
    
    def create_submission(self, files: List[bytes], form_data: Dict[str, str]) -> Dict[str, Any]:
        """Create submission with file upload"""
        try:
            url = f"{self.base_url}/submissions/"
            files_data = [("files", file) for file in files]
            response = requests.post(url, files=files_data, data=form_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Upload Error: {str(e)}")
            return {}
    
    def process_submission(self, submission_id: str) -> Dict[str, Any]:
        """Process submission through AI pipeline"""
        return self._make_request("POST", f"/process/{submission_id}")
    
    def get_submission(self, submission_id: str) -> Dict[str, Any]:
        """Get submission by ID"""
        return self._make_request("GET", f"/submissions/{submission_id}")
    
    def get_pending_approvals(self, teacher_id: str) -> List[Dict[str, Any]]:
        """Get pending approvals for teacher"""
        return self._make_request("GET", f"/approve/pending/{teacher_id}")
    
    def approve_submission(self, submission_id: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Approve submission"""
        return self._make_request("POST", f"/approve/{submission_id}", json=approval_data)
    
    def get_student_reports(self, student_id: str) -> Dict[str, Any]:
        """Get student reports"""
        return self._make_request("GET", f"/reports/{student_id}")

# Initialize API client
api = EduGradeAPI(API_BASE_URL)

def main():
    """Main application"""
    st.markdown('<h1 class="main-header">🎓 EduGrade AI K-5 Grading Platform</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    user_type = st.sidebar.selectbox("Select User Type", ["Teacher", "Parent", "Admin"])
    
    if user_type == "Teacher":
        teacher_dashboard()
    elif user_type == "Parent":
        parent_dashboard()
    else:
        admin_dashboard()

def teacher_dashboard():
    """Teacher dashboard"""
    st.header("👩‍🏫 Teacher Dashboard")
    
    # Teacher login
    teacher_id = st.text_input("Teacher ID", value="teacher_001")
    
    if not teacher_id:
        st.warning("Please enter your Teacher ID")
        return
    
    # Tabs for different teacher functions
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Exam", "📤 Upload Submissions", "✅ Review & Approve", "📊 Analytics"])
    
    with tab1:
        create_exam_tab(teacher_id)
    
    with tab2:
        upload_submissions_tab(teacher_id)
    
    with tab3:
        review_approve_tab(teacher_id)
    
    with tab4:
        analytics_tab(teacher_id)

def create_exam_tab(teacher_id: str):
    """Create exam tab"""
    st.subheader("Create New Exam")
    
    with st.form("create_exam_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            exam_title = st.text_input("Exam Title", placeholder="Math Quiz - Chapter 5")
            subject = st.selectbox("Subject", ["Mathematics", "English", "Science", "Social Studies", "Other"])
            grade_level = st.selectbox("Grade Level", ["K", "1", "2", "3", "4", "5"])
        
        with col2:
            instructions = st.text_area("Instructions", placeholder="Instructions for students...")
        
        # Answer key section
        st.subheader("Answer Key")
        
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=5)
        
        answer_key = {}
        for i in range(1, num_questions + 1):
            with st.expander(f"Question {i}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    question_text = st.text_input(f"Question {i}", key=f"q{i}_text")
                    answer_key[f"question_{i}"] = {
                        "question": question_text,
                        "answer": st.text_input(f"Answer {i}", key=f"q{i}_answer"),
                        "max_score": st.number_input(f"Max Score {i}", min_value=1, max_value=10, value=1, key=f"q{i}_score"),
                        "type": st.selectbox(f"Type {i}", ["multiple_choice", "short_answer", "essay"], key=f"q{i}_type")
                    }
        
        submitted = st.form_submit_button("Create Exam")
        
        if submitted:
            exam_data = {
                "title": exam_title,
                "subject": subject,
                "grade_level": grade_level,
                "teacher_id": teacher_id,
                "answer_key": answer_key,
                "instructions": instructions
            }
            
            exam_id = api.create_exam(exam_data)
            if exam_id:
                st.success(f"Exam created successfully! Exam ID: {exam_id}")
            else:
                st.error("Failed to create exam")

def upload_submissions_tab(teacher_id: str):
    """Upload submissions tab"""
    st.subheader("Upload Student Answer Sheets")
    
    with st.form("upload_submissions_form"):
        exam_id = st.text_input("Exam ID", placeholder="Enter exam ID")
        student_id = st.text_input("Student ID", placeholder="student_001")
        student_name = st.text_input("Student Name", placeholder="John Doe")
        
        uploaded_files = st.file_uploader(
            "Upload Answer Sheets",
            type=['pdf', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Upload scanned answer sheets (PDF, JPG, PNG)"
        )
        
        submitted = st.form_submit_button("Upload & Process")
        
        if submitted and uploaded_files and exam_id and student_id and student_name:
            # Convert uploaded files to bytes
            files_data = []
            for file in uploaded_files:
                files_data.append(file.getvalue())
            
            form_data = {
                "exam_id": exam_id,
                "student_id": student_id,
                "student_name": student_name,
                "teacher_id": teacher_id
            }
            
            submission = api.create_submission(files_data, form_data)
            
            if submission:
                submission_id = submission.get("id")
                st.success(f"Files uploaded successfully! Submission ID: {submission_id}")
                
                # Process submission
                if st.button("Start AI Processing"):
                    with st.spinner("Processing submission through AI pipeline..."):
                        process_result = api.process_submission(submission_id)
                        
                    if process_result:
                        st.success("AI processing completed!")
                        st.json(process_result)
                    else:
                        st.error("AI processing failed")

def review_approve_tab(teacher_id: str):
    """Review and approve tab"""
    st.subheader("Review & Approve Submissions")
    
    # Get pending approvals
    pending_submissions = api.get_pending_approvals(teacher_id)
    
    if not pending_submissions:
        st.info("No submissions pending approval")
        return
    
    for submission in pending_submissions:
        with st.expander(f"📄 {submission['student_name']} - {submission['exam_title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Student:** {submission['student_name']}")
                st.write(f"**Exam:** {submission['exam_title']}")
                st.write(f"**Score:** {submission['total_score']}/{submission['max_score']} ({submission['percentage']:.1f}%)")
                st.write(f"**Submitted:** {submission['created_at']}")
                
                # Display results
                if submission['results']:
                    st.subheader("Grading Results")
                    
                    for result in submission['results']:
                        if result['status'] == 'success':
                            with st.container():
                                col_a, col_b, col_c = st.columns([1, 2, 1])
                                
                                with col_a:
                                    st.metric(
                                        f"Q{result['question_number']}",
                                        f"{result['score']}/{result['max_score']}"
                                    )
                                
                                with col_b:
                                    st.write(f"**Answer:** {result['student_answer']}")
                                    st.write(f"**Feedback:** {result['feedback']}")
                                
                                with col_c:
                                    if st.button(f"Override Q{result['question_number']}", key=f"override_{submission['submission_id']}_{result['question_number']}"):
                                        st.session_state[f"override_{submission['submission_id']}_{result['question_number']}"] = True
            
            with col2:
                st.subheader("Actions")
                
                if st.button(f"✅ Approve", key=f"approve_{submission['submission_id']}"):
                    approval_data = {
                        "teacher_id": teacher_id,
                        "comments": "Approved by teacher"
                    }
                    
                    result = api.approve_submission(submission['submission_id'], approval_data)
                    
                    if result:
                        st.success("Submission approved!")
                        st.rerun()
                    else:
                        st.error("Failed to approve submission")
                
                if st.button(f"❌ Reject", key=f"reject_{submission['submission_id']}"):
                    st.warning("Rejection feature not implemented yet")

def analytics_tab(teacher_id: str):
    """Analytics tab"""
    st.subheader("Teaching Analytics")
    
    # Mock analytics data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Exams", "12", "3")
    
    with col2:
        st.metric("Submissions Graded", "156", "23")
    
    with col3:
        st.metric("Average Score", "78.5%", "5.2%")
    
    with col4:
        st.metric("Pending Reviews", "8", "-2")
    
    # Performance chart
    st.subheader("Class Performance Trends")
    
    # Mock data
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    scores = [70 + (i % 20) for i in range(len(dates))]
    
    df = pd.DataFrame({
        'Date': dates,
        'Average Score': scores
    })
    
    fig = px.line(df, x='Date', y='Average Score', title='Average Class Scores Over Time')
    st.plotly_chart(fig, use_container_width=True)

def parent_dashboard():
    """Parent dashboard"""
    st.header("👨‍👩‍👧‍👦 Parent Dashboard")
    
    # Parent login
    student_id = st.text_input("Student ID", value="student_001")
    
    if not student_id:
        st.warning("Please enter your child's Student ID")
        return
    
    st.subheader(f"Reports for Student: {student_id}")
    
    # Get student reports
    reports_data = api.get_student_reports(student_id)
    
    if not reports_data or not reports_data.get('reports'):
        st.info("No approved reports available yet. Please check back later.")
        return
    
    reports = reports_data['reports']
    
    for report in reports:
        with st.expander(f"📊 {report['exam_title']} - {report['approved_at']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Student:** {report['student_name']}")
                st.write(f"**Exam:** {report['exam_title']}")
                st.write(f"**Score:** {report['total_score']}/{report['max_score']} ({report['percentage']:.1f}%)")
                st.write(f"**Approved:** {report['approved_at']}")
                
                # Display detailed results
                if report['results']:
                    st.subheader("Detailed Results")
                    
                    for result in report['results']:
                        if result['status'] == 'success':
                            with st.container():
                                col_a, col_b = st.columns([1, 3])
                                
                                with col_a:
                                    st.metric(
                                        f"Q{result['question_number']}",
                                        f"{result['score']}/{result['max_score']}"
                                    )
                                
                                with col_b:
                                    st.write(f"**Answer:** {result['student_answer']}")
                                    st.write(f"**Feedback:** {result['feedback']}")
                                    
                                    # Show fact-check insights if available
                                    if 'fact_check' in result and result['fact_check'].get('insights'):
                                        with st.expander("Additional Insights"):
                                            for insight in result['fact_check']['insights']:
                                                st.write(f"💡 {insight}")
            
            with col2:
                st.subheader("Actions")
                
                if st.button(f"📥 Download Report", key=f"download_{report['submission_id']}"):
                    st.success("Report download started!")
                
                if st.button(f"🖨️ Print Report", key=f"print_{report['submission_id']}"):
                    st.success("Report sent to printer!")

def admin_dashboard():
    """Admin dashboard"""
    st.header("⚙️ Admin Dashboard")
    
    # Admin login
    admin_id = st.text_input("Admin ID", value="admin_001")
    
    if not admin_id:
        st.warning("Please enter your Admin ID")
        return
    
    # Admin tabs
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Analytics", "🔧 System Health"])
    
    with tab1:
        st.subheader("User Management")
        
        user_type = st.selectbox("User Type", ["Teachers", "Students", "Parents"])
        
        if user_type == "Teachers":
            st.write("Teacher Management")
            # Mock teacher data
            teachers_df = pd.DataFrame({
                'Teacher ID': ['teacher_001', 'teacher_002', 'teacher_003'],
                'Name': ['Ms. Johnson', 'Mr. Smith', 'Ms. Davis'],
                'Subject': ['Mathematics', 'English', 'Science'],
                'Active Exams': [5, 3, 4],
                'Last Login': ['2024-01-15', '2024-01-14', '2024-01-15']
            })
            st.dataframe(teachers_df)
    
    with tab2:
        st.subheader("System Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Users", "156", "12")
            st.metric("Active Exams", "23", "5")
        
        with col2:
            st.metric("Submissions Processed", "1,234", "89")
            st.metric("System Uptime", "99.9%", "0.1%")
        
        # Usage chart
        st.subheader("System Usage")
        
        # Mock data
        hours = list(range(24))
        usage = [10 + (h % 8) * 5 for h in hours]
        
        fig = go.Figure(data=go.Scatter(x=hours, y=usage, mode='lines+markers'))
        fig.update_layout(title="Hourly System Usage", xaxis_title="Hour", yaxis_title="Active Users")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("System Health")
        
        # Health check
        try:
            health_response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                st.success("✅ System is healthy")
                
                # Display service status
                services = health_data.get('services', {})
                
                for service, status in services.items():
                    if status:
                        st.write(f"✅ {service.title()}: Healthy")
                    else:
                        st.write(f"❌ {service.title()}: Unhealthy")
            else:
                st.error("❌ System health check failed")
        except Exception as e:
            st.error(f"❌ Unable to check system health: {str(e)}")

if __name__ == "__main__":
    main()
