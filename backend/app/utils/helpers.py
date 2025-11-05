"""
Utility functions and helpers for EduGrade AI Platform
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

def load_config(config_path: str = "config.env") -> Dict[str, Any]:
    """Load configuration from environment file"""
    config = {}
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    # Override with environment variables
    for key in config:
        config[key] = os.getenv(key, config[key])
    
    return config

def ensure_directories():
    """Ensure all required directories exist"""
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

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file type"""
    file_extension = Path(filename).suffix.lower()
    return file_extension in [f".{ext}" for ext in allowed_types]

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def create_sample_answer_key() -> Dict[str, Any]:
    """Create a sample answer key for testing"""
    return {
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
            "question": "Name three colors.",
            "answer": "red, blue, green",
            "max_score": 2,
            "type": "short_answer"
        }
    }

def format_percentage(score: float, max_score: float) -> float:
    """Format percentage with proper rounding"""
    if max_score == 0:
        return 0.0
    return round((score / max_score) * 100, 2)

def generate_submission_id() -> str:
    """Generate unique submission ID"""
    import uuid
    return str(uuid.uuid4())

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    return filename

def get_image_dimensions(image_path: str) -> tuple:
    """Get image dimensions"""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            return img.size
    except Exception:
        return (0, 0)

def convert_pdf_to_images(pdf_path: str, output_dir: str) -> list:
    """Convert PDF pages to images"""
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path)
        image_paths = []
        
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"page_{i+1}.png")
            image.save(image_path, "PNG")
            image_paths.append(image_path)
        
        return image_paths
    except ImportError:
        logging.warning("pdf2image not installed. PDF processing unavailable.")
        return []
    except Exception as e:
        logging.error(f"Error converting PDF: {str(e)}")
        return []

def create_thumbnail(image_path: str, size: tuple = (200, 200)) -> str:
    """Create thumbnail of image"""
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_path = image_path.replace('.', '_thumb.')
            img.save(thumb_path)
            
            return thumb_path
    except Exception as e:
        logging.error(f"Error creating thumbnail: {str(e)}")
        return image_path

def validate_api_response(response: Dict[str, Any], required_fields: list) -> bool:
    """Validate API response has required fields"""
    return all(field in response for field in required_fields)

def format_error_message(error: Exception) -> str:
    """Format error message for user display"""
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Common error mappings
    error_mappings = {
        "FileNotFoundError": "File not found. Please check the file path.",
        "PermissionError": "Permission denied. Please check file permissions.",
        "ValueError": "Invalid input. Please check your data.",
        "ConnectionError": "Connection failed. Please check your network.",
        "TimeoutError": "Request timed out. Please try again."
    }
    
    return error_mappings.get(error_type, f"{error_type}: {error_msg}")

def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "machine": platform.machine()
    }

def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are available"""
    dependencies = {
        "opencv": False,
        "ultralytics": False,
        "firebase": False,
        "streamlit": False,
        "plotly": False,
        "pandas": False,
        "pillow": False,
        "requests": False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies
