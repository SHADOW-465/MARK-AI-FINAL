"""
OpenCV Preprocessing Agent for Image Cleaning and Enhancement
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import List, Dict, Any
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class PreprocessingAgent:
    def __init__(self):
        self.is_healthy_flag = True
        
    def is_healthy(self) -> bool:
        """Check if the preprocessing agent is healthy"""
        return self.is_healthy_flag
    
    async def process_images(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process uploaded images through OpenCV preprocessing pipeline
        """
        processed_images = []
        
        for file_path in file_paths:
            try:
                logger.info(f"Processing image: {file_path}")
                
                # Load image
                image = cv2.imread(file_path)
                if image is None:
                    logger.error(f"Could not load image: {file_path}")
                    continue
                
                # Convert to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Apply preprocessing steps
                cleaned_image = self._clean_image(image_rgb)
                deskewed_image = self._deskew_image(cleaned_image)
                enhanced_image = self._enhance_contrast(deskewed_image)
                binarized_image = self._binarize_image(enhanced_image)
                
                # Save processed image
                processed_path = self._save_processed_image(binarized_image, file_path)
                
                processed_images.append({
                    "original_path": file_path,
                    "processed_path": processed_path,
                    "dimensions": binarized_image.shape,
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                processed_images.append({
                    "original_path": file_path,
                    "processed_path": None,
                    "error": str(e),
                    "status": "error"
                })
        
        return processed_images
    
    def _clean_image(self, image: np.ndarray) -> np.ndarray:
        """Remove noise and artifacts from the image"""
        # Convert to grayscale for noise reduction
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Convert back to RGB
        cleaned = cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB)
        
        return cleaned
    
    def _deskew_image(self, image: np.ndarray, max_angle: float = 15.0) -> np.ndarray:
        """Correct skew in the image (±15 degrees)"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Find lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # Calculate average angle
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = theta * 180 / np.pi
                if angle > 90:
                    angle -= 180
                angles.append(angle)
            
            if angles:
                avg_angle = np.mean(angles)
                
                # Only correct if angle is significant
                if abs(avg_angle) > 0.5 and abs(avg_angle) <= max_angle:
                    # Rotate image
                    h, w = image.shape[:2]
                    center = (w // 2, h // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, -avg_angle, 1.0)
                    deskewed = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                            flags=cv2.INTER_CUBIC, 
                                            borderMode=cv2.BORDER_REPLICATE)
                    return deskewed
        
        return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back to RGB
        enhanced_lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    def _binarize_image(self, image: np.ndarray) -> np.ndarray:
        """Convert image to binary (black and white) for better OCR"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to RGB for consistency
        binary_rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        
        return binary_rgb
    
    def _save_processed_image(self, image: np.ndarray, original_path: str) -> str:
        """Save processed image and return the new path"""
        # Create processed directory
        processed_dir = Path("data/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate new filename
        original_name = Path(original_path).stem
        processed_path = processed_dir / f"{original_name}_processed.png"
        
        # Convert numpy array to PIL Image and save
        pil_image = Image.fromarray(image)
        pil_image.save(processed_path)
        
        return str(processed_path)
    
    def get_image_stats(self, image_path: str) -> Dict[str, Any]:
        """Get statistics about the processed image"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not load image"}
            
            height, width = image.shape[:2]
            
            return {
                "dimensions": {"width": width, "height": height},
                "file_size": os.path.getsize(image_path),
                "channels": image.shape[2] if len(image.shape) == 3 else 1,
                "dtype": str(image.dtype)
            }
        except Exception as e:
            return {"error": str(e)}
