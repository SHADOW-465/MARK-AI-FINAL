# EduGrade AI K-5 Grading Platform

An AI-powered grading system designed specifically for K-5 education, featuring automated answer sheet processing, intelligent grading, and comprehensive teacher-parent communication.

## 🚀 Features

### Core Functionality
- **Automated Answer Sheet Processing**: Upload PDF, JPG, or PNG answer sheets
- **AI-Powered Grading**: Uses Gemini AI for intelligent answer evaluation
- **Fact-Checking Integration**: Perplexity API integration for additional insights
- **Teacher Approval Workflow**: Teachers review and approve grades before parent access
- **Parent Dashboard**: Secure access to approved student reports

### Technical Features
- **OpenCV Image Preprocessing**: Deskewing, noise reduction, contrast enhancement
- **YOLOv8 Tiny Segmentation**: Automatic answer box detection
- **Firebase Integration**: Secure data storage and user management
- **Streamlit Dashboard**: Modern, intuitive web interface
- **Docker Support**: Easy deployment and scaling

## 📋 Prerequisites

- Python 3.11+
- Firebase project with Firestore and Storage enabled
- Gemini AI API key
- Perplexity API key (optional)
- Docker (optional)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Mark-AI
   ```

2. **Set up environment variables**
   ```bash
   cp config.env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Option 2: Manual Installation

1. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

3. **Set up Firebase**
   - Create a Firebase project
   - Download service account credentials
   - Place credentials file in `config/firebase-credentials.json`

4. **Configure environment variables**
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   export PERPLEXITY_API_KEY="your_perplexity_api_key"
   ```

## 🚀 Running the Application

### Backend (FastAPI)
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Streamlit)
```bash
cd frontend
streamlit run streamlit_dashboard.py --server.port 8501
```

## 📖 Usage Guide

### For Teachers

1. **Create an Exam**
   - Navigate to "Create Exam" tab
   - Fill in exam details and answer key
   - Save the exam ID for student submissions

2. **Upload Student Submissions**
   - Go to "Upload Submissions" tab
   - Enter exam ID, student information
   - Upload scanned answer sheets (PDF/JPG/PNG)
   - Start AI processing

3. **Review and Approve**
   - Check "Review & Approve" tab for pending submissions
   - Review AI-generated grades and feedback
   - Override grades if necessary
   - Approve submissions for parent access

### For Parents

1. **Access Student Reports**
   - Enter your child's Student ID
   - View approved reports and grades
   - Download or print report cards
   - Access detailed feedback and insights

### For Administrators

1. **System Management**
   - Monitor system health and usage
   - Manage users and permissions
   - View analytics and reports

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini AI API key | Required |
| `PERPLEXITY_API_KEY` | Perplexity API key | Optional |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase credentials | `config/firebase-credentials.json` |
| `API_BASE_URL` | Backend API URL | `http://localhost:8000/api/v1` |

### Firebase Setup

1. Create a new Firebase project
2. Enable Firestore Database
3. Enable Cloud Storage
4. Generate service account credentials
5. Download and place credentials file

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific test categories:
```bash
# Unit tests only
pytest tests/test_edugrade.py::TestPreprocessingAgent -v

# Integration tests
pytest tests/test_edugrade.py::TestIntegration -v
```

## 📁 Project Structure

```
edugrade-k5/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── agents/                 # AI processing agents
│   │   │   ├── preprocessing_agent.py
│   │   │   ├── segmentation_agent.py
│   │   │   ├── grading_agent.py
│   │   │   └── factcheck_agent.py
│   │   ├── api/                    # API endpoints
│   │   │   ├── exams.py
│   │   │   ├── submissions.py
│   │   │   └── approvals.py
│   │   └── services/               # External services
│   │       └── firebase_service.py
│   └── requirements.txt
├── frontend/
│   ├── streamlit_dashboard.py     # Main UI
│   └── requirements.txt
├── data/
│   ├── models/                    # AI models
│   ├── uploads/                   # Uploaded files
│   ├── processed/                 # Processed images
│   └── regions/                   # Segmented regions
├── tests/
│   └── test_edugrade.py           # Test suite
├── config/
│   └── firebase-credentials.json  # Firebase credentials
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

## 🔄 API Endpoints

### Exams
- `POST /api/v1/exams/` - Create exam
- `GET /api/v1/exams/{exam_id}` - Get exam
- `PUT /api/v1/exams/{exam_id}/answer-key` - Update answer key

### Submissions
- `POST /api/v1/submissions/` - Upload submission
- `GET /api/v1/submissions/{submission_id}` - Get submission
- `POST /api/v1/process/{submission_id}` - Process submission

### Approvals
- `POST /api/v1/approve/{submission_id}` - Approve submission
- `GET /api/v1/approve/pending/{teacher_id}` - Get pending approvals
- `GET /api/v1/reports/{student_id}` - Get student reports

## 🛡️ Security Considerations

- All file uploads are validated for type and size
- Teacher approval required before parent access
- Firebase security rules enforce data access
- API keys stored as environment variables
- Input validation on all endpoints

## 🚀 Deployment

### Production Deployment

1. **Set up production environment variables**
2. **Configure Firebase security rules**
3. **Set up reverse proxy (nginx)**
4. **Enable HTTPS**
5. **Set up monitoring and logging**

### Scaling Considerations

- Use Redis for caching
- Implement horizontal scaling with load balancer
- Use CDN for static assets
- Consider serverless deployment for AI processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test cases for usage examples

## 🔮 Future Enhancements

- [ ] Blockchain integration for grade verification
- [ ] Advanced analytics and reporting
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Integration with LMS systems
- [ ] Advanced AI models for handwriting recognition
- [ ] Real-time collaboration features
