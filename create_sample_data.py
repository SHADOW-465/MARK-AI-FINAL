"""
Sample data and test files for EduGrade AI Platform
"""

import json
import os
from pathlib import Path

def create_sample_data():
    """Create sample data for testing"""
    
    # Create sample answer key
    sample_answer_key = {
        "question_1": {
            "question": "What is 2 + 2?",
            "answer": "4",
            "max_score": 1,
            "type": "multiple_choice"
        },
        "question_2": {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "max_score": 1,
            "type": "short_answer"
        },
        "question_3": {
            "question": "Name three primary colors.",
            "answer": "red, blue, yellow",
            "max_score": 2,
            "type": "short_answer"
        },
        "question_4": {
            "question": "What is 10 - 3?",
            "answer": "7",
            "max_score": 1,
            "type": "multiple_choice"
        },
        "question_5": {
            "question": "Which planet is closest to the Sun?",
            "answer": "Mercury",
            "max_score": 1,
            "type": "multiple_choice"
        }
    }
    
    # Create sample exam data
    sample_exam = {
        "title": "Math and Science Quiz - Grade 3",
        "subject": "Mathematics",
        "grade_level": "3",
        "teacher_id": "teacher_001",
        "answer_key": sample_answer_key,
        "instructions": "Answer all questions. Show your work for math problems.",
        "created_at": "2024-01-15T10:00:00Z",
        "status": "active"
    }
    
    # Create sample submission data
    sample_submission = {
        "exam_id": "exam_001",
        "student_id": "student_001", 
        "student_name": "Alice Johnson",
        "teacher_id": "teacher_001",
        "file_paths": ["data/uploads/sample_answer_sheet.pdf"],
        "status": "pending_review",
        "processing_stage": "grading",
        "created_at": "2024-01-15T14:30:00Z"
    }
    
    # Create sample grading results
    sample_results = [
        {
            "question_number": 1,
            "student_answer": "4",
            "correct_answer": "4",
            "score": 1,
            "max_score": 1,
            "feedback": "Excellent! You got it right!",
            "partial_credit": 1.0,
            "confidence": 0.95,
            "status": "success"
        },
        {
            "question_number": 2,
            "student_answer": "Paris",
            "correct_answer": "Paris",
            "score": 1,
            "max_score": 1,
            "feedback": "Perfect! Paris is indeed the capital of France.",
            "partial_credit": 1.0,
            "confidence": 0.9,
            "status": "success"
        },
        {
            "question_number": 3,
            "student_answer": "red, blue, green",
            "correct_answer": "red, blue, yellow",
            "score": 1,
            "max_score": 2,
            "partial_credit": 0.5,
            "feedback": "Good try! You got red and blue correct, but yellow is also a primary color.",
            "confidence": 0.8,
            "status": "success"
        },
        {
            "question_number": 4,
            "student_answer": "7",
            "correct_answer": "7",
            "score": 1,
            "max_score": 1,
            "feedback": "Great job! 10 - 3 = 7.",
            "partial_credit": 1.0,
            "confidence": 0.95,
            "status": "success"
        },
        {
            "question_number": 5,
            "student_answer": "Venus",
            "correct_answer": "Mercury",
            "score": 0,
            "max_score": 1,
            "feedback": "Not quite right. Mercury is the planet closest to the Sun.",
            "partial_credit": 0.0,
            "confidence": 0.9,
            "status": "success"
        }
    ]
    
    # Save sample data
    sample_dir = Path("data/sample")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    with open(sample_dir / "answer_key.json", "w") as f:
        json.dump(sample_answer_key, f, indent=2)
    
    with open(sample_dir / "exam.json", "w") as f:
        json.dump(sample_exam, f, indent=2)
    
    with open(sample_dir / "submission.json", "w") as f:
        json.dump(sample_submission, f, indent=2)
    
    with open(sample_dir / "grading_results.json", "w") as f:
        json.dump(sample_results, f, indent=2)
    
    print("✅ Sample data created in data/sample/")

def create_test_images():
    """Create test images for development"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a sample answer sheet image
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw header
        draw.text((50, 50), "Math and Science Quiz - Grade 3", fill='black', font=font)
        draw.text((50, 80), "Student Name: Alice Johnson", fill='black', font=font)
        draw.text((50, 110), "Date: January 15, 2024", fill='black', font=font)
        
        # Draw questions
        questions = [
            "1. What is 2 + 2?",
            "2. What is the capital of France?",
            "3. Name three primary colors.",
            "4. What is 10 - 3?",
            "5. Which planet is closest to the Sun?"
        ]
        
        y_pos = 150
        for question in questions:
            draw.text((50, y_pos), question, fill='black', font=font)
            # Draw answer box
            draw.rectangle([300, y_pos, 500, y_pos + 30], outline='black', width=2)
            y_pos += 60
        
        # Save test image
        test_dir = Path("data/sample_sheets")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        img.save(test_dir / "sample_answer_sheet.png")
        print("✅ Test image created: data/sample_sheets/sample_answer_sheet.png")
        
    except ImportError:
        print("⚠️  PIL not available. Skipping test image creation.")

def create_firebase_rules():
    """Create Firebase security rules"""
    
    firestore_rules = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Teachers can read/write exams they created
    match /exams/{examId} {
      allow read, write: if request.auth != null && 
        resource.data.teacher_id == request.auth.uid;
    }
    
    // Teachers can read/write submissions for their exams
    match /submissions/{submissionId} {
      allow read, write: if request.auth != null && 
        resource.data.teacher_id == request.auth.uid;
    }
    
    // Parents can read approved submissions for their children
    match /submissions/{submissionId} {
      allow read: if request.auth != null && 
        resource.data.status == 'approved' &&
        resource.data.student_id in request.auth.token.parent_of;
    }
    
    // Admins have full access
    match /{document=**} {
      allow read, write: if request.auth != null && 
        request.auth.token.admin == true;
    }
  }
}
"""
    
    storage_rules = """
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Users can upload files to their own folder
    match /users/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Teachers can upload files for their exams
    match /exams/{examId}/{allPaths=**} {
      allow read, write: if request.auth != null && 
        request.auth.token.teacher == true;
    }
    
    // Students can upload answer sheets
    match /submissions/{submissionId}/{allPaths=**} {
      allow read, write: if request.auth != null && 
        request.auth.token.student == true;
    }
  }
}
"""
    
    # Save rules files
    rules_dir = Path("config/firebase")
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    with open(rules_dir / "firestore.rules", "w") as f:
        f.write(firestore_rules)
    
    with open(rules_dir / "storage.rules", "w") as f:
        f.write(storage_rules)
    
    print("✅ Firebase security rules created in config/firebase/")

def main():
    """Create all sample data"""
    print("🎓 Creating sample data for EduGrade AI Platform...")
    
    create_sample_data()
    create_test_images()
    create_firebase_rules()
    
    print("\n✅ Sample data creation complete!")
    print("\n📁 Created files:")
    print("   - data/sample/answer_key.json")
    print("   - data/sample/exam.json")
    print("   - data/sample/submission.json")
    print("   - data/sample/grading_results.json")
    print("   - data/sample_sheets/sample_answer_sheet.png")
    print("   - config/firebase/firestore.rules")
    print("   - config/firebase/storage.rules")

if __name__ == "__main__":
    main()
