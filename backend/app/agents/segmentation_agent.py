"""
YOLOv8 Tiny Segmentation Agent for Answer Box Detection
"""

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel
import logging
from typing import List, Dict, Any, Tuple
import os
from pathlib import Path

from .base_agent import BaseAgent
from ..graph.state import GradingState

logger = logging.getLogger(__name__)

# Fix for PyTorch 2.6 weights loading security
# This allows loading YOLOv8 models which use custom classes
torch.serialization.add_safe_globals([DetectionModel])

class SegmentationAgent(BaseAgent):
    def __init__(self, model_path: str = "data/models/yolov8-tiny.pt"):
        super().__init__("segmentation_agent")
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load YOLOv8 Tiny model"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                logger.info(f"YOLOv8 model loaded from {self.model_path}")
            else:
                # Download and use pre-trained model if custom model not available
                self.model = YOLO('yolov8n.pt')  # nano version for speed
                logger.info("Using pre-trained YOLOv8n model")
        except Exception as e:
            logger.error(f"Error loading YOLOv8 model: {str(e)}")
            self.is_healthy_flag = False

    async def process(self, state: GradingState) -> GradingState:
        """
        Segment answer boxes from processed images using YOLOv8
        """
        if state.get("status") != "preprocessing_complete":
            state["error"] = "Image preprocessing failed or was not run"
            state["status"] = "error"
            return state

        try:
            image_path = state.get("image_path")
            logger.info(f"Segmenting answers in: {image_path}")

            # Run YOLOv8 inference
            results = self.model(image_path)

            # Extract answer boxes
            answer_regions = self._extract_answer_regions(results[0], image_path)

            # Fallback to grid detection if YOLOv8 finds no boxes
            if not answer_regions:
                logger.info("No answer boxes detected by YOLOv8, trying grid detection")
                answer_regions = self._detect_grid_boxes(image_path)

            state["answer_boxes"] = answer_regions
            state["status"] = "segmentation_complete"
            return state

        except Exception as e:
            logger.error(f"Error segmenting {state.get('original_path')}: {str(e)}")
            state["error"] = str(e)
            state["status"] = "error"
            return state


    def _extract_answer_regions(self, result, image_path: str) -> List[Dict[str, Any]]:
        """Extract answer regions from YOLOv8 results"""
        answer_regions = []

        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xyxy.cpu().numpy()  # Get bounding boxes
            confidences = result.boxes.conf.cpu().numpy()  # Get confidence scores

            for i, (box, conf) in enumerate(zip(boxes, confidences)):
                if conf > 0.5:  # Confidence threshold
                    x1, y1, x2, y2 = box

                    # Load image to extract region
                    image = cv2.imread(image_path)
                    if image is not None:
                        # Extract region
                        region = image[int(y1):int(y2), int(x1):int(x2)]

                        # Save region
                        region_path = self._save_answer_region(region, image_path, i)

                        answer_regions.append({
                            "question_number": i + 1,
                            "coordinates": {
                                "x1": int(x1), "y1": int(y1),
                                "x2": int(x2), "y2": int(y2)
                            },
                            "confidence": float(conf),
                            "region_path": region_path,
                            "region_size": region.shape
                        })

        return answer_regions

    def _detect_grid_boxes(self, image_path: str) -> List[Dict[str, Any]]:
        """Fallback grid detection for standardized answer sheets"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

            # Detect horizontal lines
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=2)

            # Detect vertical lines
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=2)

            # Combine lines
            grid = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0)

            # Find contours (answer boxes)
            contours, _ = cv2.findContours(grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            answer_regions = []
            for i, contour in enumerate(contours):
                # Filter by area (typical answer box size)
                area = cv2.contourArea(contour)
                if 1000 < area < 50000:  # Adjust thresholds based on typical answer box sizes
                    x, y, w, h = cv2.boundingRect(contour)

                    # Extract region
                    region = image[y:y+h, x:x+w]
                    region_path = self._save_answer_region(region, image_path, i)

                    answer_regions.append({
                        "question_number": i + 1,
                        "coordinates": {
                            "x1": x, "y1": y,
                            "x2": x + w, "y2": y + h
                        },
                        "confidence": 0.8,  # Grid detection confidence
                        "region_path": region_path,
                        "region_size": region.shape,
                        "detection_method": "grid"
                    })

            # Sort by y-coordinate (top to bottom)
            answer_regions.sort(key=lambda x: x["coordinates"]["y1"])

            return answer_regions

        except Exception as e:
            logger.error(f"Error in grid detection: {str(e)}")
            return []

    def _save_answer_region(self, region: np.ndarray, original_path: str, region_index: int) -> str:
        """Save extracted answer region"""
        # Create regions directory
        regions_dir = Path("data/regions")
        regions_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        original_name = Path(original_path).stem
        region_path = regions_dir / f"{original_name}_region_{region_index}.png"

        # Save region
        cv2.imwrite(str(region_path), region)

        return str(region_path)

    def visualize_detections(self, image_path: str, answer_regions: List[Dict[str, Any]]) -> str:
        """Create visualization of detected answer regions"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None

            # Draw bounding boxes
            for region in answer_regions:
                coords = region["coordinates"]
                cv2.rectangle(image,
                            (coords["x1"], coords["y1"]),
                            (coords["x2"], coords["y2"]),
                            (0, 255, 0), 2)

                # Add question number
                cv2.putText(image, f"Q{region['question_number']}",
                          (coords["x1"], coords["y1"] - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Save visualization
            vis_dir = Path("data/visualizations")
            vis_dir.mkdir(parents=True, exist_ok=True)

            original_name = Path(image_path).stem
            vis_path = vis_dir / f"{original_name}_detections.png"
            cv2.imwrite(str(vis_path), image)

            return str(vis_path)

        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            return None
