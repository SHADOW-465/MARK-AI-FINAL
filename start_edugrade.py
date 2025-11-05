#!/usr/bin/env python3
"""
EduGrade AI K-5 Grading Platform - Startup Script
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def load_environment():
    """Load environment variables from config file"""
    config_file = "config.env"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded environment from {config_file}")
    else:
        print(f"⚠️  Config file {config_file} not found")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "streamlit",
        "opencv-python",
        "ultralytics",
        "firebase-admin",
        "requests",
        "plotly",
        "pandas"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data/uploads",
        "data/processed",
        "data/regions", 
        "data/visualizations",
        "data/models",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        "GEMINI_API_KEY",
        "PERPLEXITY_API_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("The application will run in mock mode for these services")
    else:
        print("✅ All environment variables are set")

def start_backend():
    """Start the FastAPI backend"""
    print("\n🚀 Starting EduGrade AI Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Change to backend directory and start uvicorn
        os.chdir(backend_dir)
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
        print("✅ Backend started on http://localhost:8000")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start backend: {str(e)}")
        return False

def start_frontend():
    """Start the Streamlit frontend"""
    print("\n🚀 Starting EduGrade AI Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Change to frontend directory and start streamlit
        os.chdir(frontend_dir)
        subprocess.Popen([
            sys.executable, "-m", "streamlit", 
            "run", "streamlit_dashboard.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        
        print("✅ Frontend started on http://localhost:8501")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {str(e)}")
        return False

def main():
    """Main startup function"""
    print("🎓 EduGrade AI K-5 Grading Platform")
    print("=" * 50)
    
    # Load environment variables first
    print("\n🔧 Loading environment configuration...")
    load_environment()
    
    # Check system requirements
    print("\n📋 Checking system requirements...")
    check_python_version()
    
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Setup directories
    print("\n📁 Setting up directories...")
    setup_directories()
    
    # Check environment
    print("\n🔧 Checking environment...")
    check_environment_variables()
    
    # Start services
    print("\n🚀 Starting services...")
    
    # Start backend
    backend_success = start_backend()
    
    # Wait a moment for backend to start
    if backend_success:
        time.sleep(3)
    
    # Start frontend
    frontend_success = start_frontend()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎓 EduGrade AI Platform Status")
    print("=" * 50)
    
    if backend_success:
        print("✅ Backend: http://localhost:8000")
        print("   - API Documentation: http://localhost:8000/docs")
        print("   - Health Check: http://localhost:8000/health")
    else:
        print("❌ Backend: Failed to start")
    
    if frontend_success:
        print("✅ Frontend: http://localhost:8501")
        print("   - Teacher Dashboard: http://localhost:8501")
        print("   - Parent Dashboard: http://localhost:8501")
    else:
        print("❌ Frontend: Failed to start")
    
    if backend_success and frontend_success:
        print("\n🎉 EduGrade AI Platform is running!")
        print("\n📖 Quick Start:")
        print("1. Open http://localhost:8501 in your browser")
        print("2. Select 'Teacher' from the sidebar")
        print("3. Create an exam and upload answer sheets")
        print("4. Review and approve submissions")
        print("\n📚 For more information, see README.md")
    else:
        print("\n❌ Some services failed to start. Check the logs above.")
    
    print("\nPress Ctrl+C to stop all services")

if __name__ == "__main__":
    try:
        main()
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down EduGrade AI Platform...")
        sys.exit(0)
