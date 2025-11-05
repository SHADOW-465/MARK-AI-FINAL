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
- Docker

## 🛠️ Installation

### With Docker (Recommended)

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd Mark-AI
    ```

2.  **Set up environment variables**
    Create a `.env` file in the root directory and add the following variables:
    ```
    GEMINI_API_KEY="your_gemini_api_key"
    PERPLEXITY_API_KEY="your_perplexity_api_key"
    ```
    See the **Environment Variables** section for a complete list of all possible variables.

3.  **Run with Docker Compose**
    ```bash
    docker-compose up -d
    ```
    The application will be available at `http://localhost:8501`.

### Manual Installation

1.  **Install backend dependencies**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Install frontend dependencies**
    ```bash
    cd frontend
    pip install -r requirements.txt
    ```

3.  **Set up Firebase**
    - Create a Firebase project
    - Download your service account credentials
    - Place the credentials file at `config/firebase-credentials.json`

4.  **Configure environment variables**
    Create a `config.env` file in the root directory and add all the required variables. See the **Environment Variables** section for a complete list.

## 🚀 Running the Application

### With the Startup Script
The easiest way to run the application manually is with the provided startup script:
```bash
python start_edugrade.py
```
This script will:
- Load environment variables from `config.env`
- Check system requirements
- Set up necessary directories
- Start the backend and frontend servers

### Manually
#### Backend (FastAPI)
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
#### Frontend (Streamlit)
```bash
cd frontend
streamlit run streamlit_dashboard.py --server.port 8501
```

## 🔧 Environment Variables

The following environment variables are used to configure the application. You can set them in a `.env` file for Docker or a `config.env` file for manual execution.

| Variable | Description | Default | Required |
|---|---|---|---|
| `API_BASE_URL` | The base URL for the backend API. | `http://localhost:8000/api/v1` | No |
| `BACKEND_HOST` | The host for the backend server. | `0.0.0.0` | No |
| `BACKEND_PORT` | The port for the backend server. | `8000` | No |
| `FRONTEND_HOST` | The host for the frontend server. | `localhost` | No |
| `FRONTEND_PORT` | The port for the frontend server. | `8501` | No |
| `FIREBASE_CREDENTIALS_PATH`| Path to the Firebase credentials file. | `config/firebase-credentials.json` | Yes |
| `FIREBASE_PROJECT_ID` | Your Firebase project ID. | | Yes |
| `FIREBASE_STORAGE_BUCKET` | Your Firebase storage bucket URL. | | Yes |
| `GEMINI_API_KEY` | Your Google Gemini AI API key. | | Yes |
| `PERPLEXITY_API_KEY` | Your Perplexity AI API key. | | Yes |
| `YOLO_MODEL_PATH` | The path to the YOLOv8 model file. | `data/models/yolov8-tiny.pt` | No |
| `YOLO_CONFIDENCE_THRESHOLD` | The confidence threshold for the YOLOv8 model. | `0.5` | No |
| `MAX_FILE_SIZE_MB` | The maximum file size for uploads in MB. | `10` | No |
| `ALLOWED_FILE_TYPES` | The allowed file types for uploads. | `pdf,jpg,jpeg,png` | No |
| `UPLOAD_DIRECTORY` | The directory to store uploaded files. | `data/uploads` | No |
| `PROCESSED_DIRECTORY` | The directory to store processed images. | `data/processed` | No |
| `REGIONS_DIRECTORY` | The directory to store segmented answer regions. | `data/regions` | No |
| `MAX_CONCURRENT_PROCESSING`| The maximum number of concurrent processing jobs. | `5` | No |
| `PROCESSING_TIMEOUT_SECONDS`| The timeout for processing a submission in seconds. | `300` | No |
| `LOG_LEVEL` | The logging level. | `INFO` | No |
| `LOG_FILE` | The path to the log file. | `logs/edugrade.log` | No |
| `SECRET_KEY` | A secret key for signing tokens. | | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| The expiration time for access tokens in minutes. | `30` | No |
| `DEBUG` | Whether to run in debug mode. | `True` | No |
| `RELOAD` | Whether to automatically reload the server on code changes. | `True` | No |

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
