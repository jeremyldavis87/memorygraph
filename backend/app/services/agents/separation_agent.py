"""
Separation Agent

Handles multi-note detection and separation using parallel execution of
QR code detection, OpenCV contour detection, and Vision LLM analysis.
Selects the method with highest confidence for optimal results.
"""

import cv2
import numpy as np
import asyncio
from typing import Dict, Any, List, Tuple, Optional, Union
from PIL import Image
import json
import base64

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

from .base_agent import BaseAgent, PartialResult
from app.services.ai_service import AIService
from app.core.config import settings


class NoteRegion:
    """Container for detected note region information"""
    
    def __init__(self, bbox: Tuple[int, int, int, int], position: int, 
                 qr_code: Optional[str] = None, detection_method: str = "unknown",
                 confidence: float = 0.0):
        self.bbox = bbox  # (x, y, width, height)
        self.position = position
        self.qr_code = qr_code
        self.detection_method = detection_method
        self.confidence = confidence


class SeparationAgent(BaseAgent):
    """
    Agent responsible for detecting and separating multiple notes in an image.
    
    Uses parallel execution of three detection methods:
    1. QR code detection with pyzbar
    2. OpenCV contour detection
    3. Vision LLM analysis (gpt-5-mini)
    
    Selects the method with highest confidence for optimal results.
    """
    
    def __init__(self):
        super().__init__("SeparationAgent")
        self.ai_service = AIService()
        
        if not PYZBAR_AVAILABLE:
            self.logger.warning("pyzbar not available, QR code detection will be disabled")
    
    async def process(self, image_path: str, config: Dict[str, Any] = None) -> Union[List[NoteRegion], PartialResult]:
        """
        Main processing method for note separation.
        
        Args:
            image_path: Path to the input image
            config: Optional configuration dict with source_type, etc.
            
        Returns:
            List of NoteRegion objects or PartialResult if processing fails
        """
        return await self.execute_with_retry(self._detect_note_regions, image_path, config)
    
    async def _detect_note_regions(self, image_path: str, config: Dict[str, Any] = None) -> List[NoteRegion]:
        """Internal method to detect note regions using parallel methods"""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Check if this is a Rocketbook image
        source_type = config.get("source_type", "") if config else ""
        is_rocketbook = source_type.lower() == "rocketbook"
        
        # Run all detection methods in parallel
        tasks = []
        
        if PYZBAR_AVAILABLE:
            tasks.append(self._detect_qr_regions(image))
        else:
            tasks.append(asyncio.create_task(self._create_empty_result("qr_disabled")))
        
        tasks.append(self._detect_contours(image))
        tasks.append(self._detect_with_vision(image_path))
        
        # Wait for all methods to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and empty results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Detection method {i} failed: {result}")
                continue
            if result and len(result) > 0:
                valid_results.append(result)
        
        if not valid_results:
            # All methods failed
            if is_rocketbook:
                # For Rocketbook images, assume 3x3 grid
                self.logger.info("All detection methods failed, assuming 3x3 grid for Rocketbook image")
                return self._create_3x3_grid(image)
            else:
                return [self._create_single_region(image)]
        
        # Select method with highest confidence
        best_result = self._select_best_method(valid_results)
        
        # For Rocketbook images, if we detected fewer than 9 regions but have some QR codes,
        # create a 3x3 grid instead
        if is_rocketbook and len(best_result) < 9:
            # Check if any QR codes were detected
            qr_results = [r for r in results if isinstance(r, list) and len(r) > 0 and any(reg.qr_code for reg in r)]
            if qr_results or len(best_result) >= 4:
                # Likely a multi-note Rocketbook image - create 3x3 grid
                self.logger.info(f"Detected {len(best_result)} regions for Rocketbook image, creating 3x3 grid")
                return self._create_3x3_grid(image)
        
        # Log metrics
        self.log_metric("detection_method", len(best_result))
        self.log_metric("total_regions", len(best_result))
        
        return best_result
    
    async def _detect_qr_regions(self, image: np.ndarray) -> List[NoteRegion]:
        """Detect note regions using QR codes"""
        try:
            # Convert OpenCV image to PIL Image for pyzbar
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Decode QR codes
            decoded_objects = pyzbar.decode(pil_image)
            
            if not decoded_objects:
                return []
            
            regions = []
            img_height, img_width = image.shape[:2]
            
            # Calculate grid cell size (assuming 3x3 grid)
            cell_width = img_width // 3
            cell_height = img_height // 3
            
            for obj in decoded_objects:
                # Get QR code data
                qr_data = obj.data.decode('utf-8')
                
                # Get bounding box
                rect = obj.rect
                qr_bbox = (rect.left, rect.top, rect.width, rect.height)
                
                # Estimate position in grid
                position = self._estimate_grid_position(qr_bbox, img_width, img_height)
                
                # Calculate note region based on grid position
                row = (position - 1) // 3
                col = (position - 1) % 3
                
                x = col * cell_width
                y = row * cell_height
                w = cell_width
                h = cell_height
                
                region = NoteRegion(
                    bbox=(x, y, w, h),
                    position=position,
                    qr_code=qr_data,
                    detection_method="qr_code",
                    confidence=1.0  # QR codes are very reliable
                )
                regions.append(region)
            
            return regions
            
        except Exception as e:
            self.logger.error(f"QR code detection failed: {e}")
            return []
    
    async def _detect_contours(self, image: np.ndarray) -> List[NoteRegion]:
        """Detect note regions using OpenCV contour detection"""
        try:
            # Preprocess for contour detection
            preprocessed = self._preprocess_for_contours(image)
            
            # Find contours
            contours, _ = cv2.findContours(
                preprocessed,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours
            valid_contours = self._filter_contours(contours, image.shape)
            
            # Convert to note regions
            regions = []
            for i, contour in enumerate(valid_contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate confidence based on contour quality
                confidence = self._calculate_contour_confidence(contour, image.shape)
                
                region = NoteRegion(
                    bbox=(x, y, w, h),
                    position=i + 1,
                    detection_method="contour",
                    confidence=confidence
                )
                regions.append(region)
            
            return regions
            
        except Exception as e:
            self.logger.error(f"Contour detection failed: {e}")
            return []
    
    async def _detect_with_vision(self, image_path: str) -> List[NoteRegion]:
        """Detect note regions using Vision LLM"""
        try:
            # Use AI service for vision analysis
            vision_result = self.ai_service.detect_note_regions_with_vision(
                image_path, settings.AGENT_VISION_MODEL
            )
            
            if not vision_result.get("success"):
                return []
            
            analysis = vision_result.get("analysis", {})
            if not analysis:
                return []
            
            # Load image for region calculation
            image = cv2.imread(image_path)
            img_height, img_width = image.shape[:2]
            
            regions = []
            total_notes = analysis.get("total_notes", 1)
            layout = analysis.get("layout", "single")
            
            if "3x3" in layout.lower() and total_notes <= 9:
                # Create 3x3 grid regions
                cell_width = img_width // 3
                cell_height = img_height // 3
                
                for i in range(min(total_notes, 9)):
                    row = i // 3
                    col = i % 3
                    
                    x = col * cell_width
                    y = row * cell_height
                    w = cell_width
                    h = cell_height
                    
                    region = NoteRegion(
                        bbox=(x, y, w, h),
                        position=i + 1,
                        detection_method="vision_llm",
                        confidence=0.8  # Vision LLM confidence
                    )
                    regions.append(region)
            else:
                # For other layouts, create regions based on analysis
                notes_info = analysis.get("notes", [])
                for note_info in notes_info:
                    position = note_info.get("position", len(regions) + 1)
                    
                    # Estimate region based on position
                    if total_notes <= 4:
                        # 2x2 layout
                        row = (position - 1) // 2
                        col = (position - 1) % 2
                        cell_width = img_width // 2
                        cell_height = img_height // 2
                    else:
                        # Default to single region
                        cell_width = img_width
                        cell_height = img_height
                        row = 0
                        col = 0
                    
                    x = col * cell_width
                    y = row * cell_height
                    w = cell_width
                    h = cell_height
                    
                    region = NoteRegion(
                        bbox=(x, y, w, h),
                        position=position,
                        detection_method="vision_llm",
                        confidence=0.8
                    )
                    regions.append(region)
            
            return regions
            
        except Exception as e:
            self.logger.error(f"Vision LLM detection failed: {e}")
            return []
    
    def _preprocess_for_contours(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for contour detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11, 2
        )
        
        # Morphological operations to connect note regions
        kernel = np.ones((3, 3), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        return morph
    
    def _filter_contours(self, contours: List, image_shape: Tuple[int, int, int]) -> List:
        """Filter contours to identify valid notes"""
        height, width = image_shape[:2]
        image_area = height * width
        
        valid_contours = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            
            # Size filters
            min_area = image_area * 0.01  # At least 1% of image
            max_area = image_area * 0.95  # At most 95% of image
            
            if not (min_area < area < max_area):
                continue
            
            # Aspect ratio filter (notes are generally rectangular)
            aspect_ratio = w / h
            if not (0.3 < aspect_ratio < 3.0):
                continue
            
            # Minimum dimensions
            if w < 50 or h < 50:
                continue
            
            # Shape approximation (notes should be roughly rectangular)
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # Should have 4-8 corners (rectangular-ish)
            if not (4 <= len(approx) <= 8):
                continue
            
            valid_contours.append(contour)
        
        return valid_contours
    
    def _calculate_contour_confidence(self, contour, image_shape: Tuple[int, int, int]) -> float:
        """Calculate confidence score for a contour"""
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Base confidence from area
        height, width = image_shape[:2]
        image_area = height * width
        area_ratio = area / image_area
        
        # Optimal area ratio for sticky notes (1-10% of image)
        if 0.01 <= area_ratio <= 0.1:
            area_score = 1.0
        elif 0.005 <= area_ratio <= 0.2:
            area_score = 0.7
        else:
            area_score = 0.3
        
        # Aspect ratio score
        aspect_ratio = w / h
        if 0.5 <= aspect_ratio <= 2.0:
            aspect_score = 1.0
        elif 0.3 <= aspect_ratio <= 3.0:
            aspect_score = 0.7
        else:
            aspect_score = 0.3
        
        # Shape regularity score
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if 4 <= len(approx) <= 6:
            shape_score = 1.0
        elif 3 <= len(approx) <= 8:
            shape_score = 0.7
        else:
            shape_score = 0.3
        
        # Weighted average
        confidence = (area_score * 0.4 + aspect_score * 0.3 + shape_score * 0.3)
        return min(1.0, confidence)
    
    def _estimate_grid_position(self, bbox: Tuple[int, int, int, int], 
                              img_width: int, img_height: int) -> int:
        """Estimate the position of a QR code in a grid layout"""
        x, y, w, h = bbox
        
        # Calculate center point
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Determine grid position
        col = min(2, max(0, int(center_x / (img_width / 3))))
        row = min(2, max(0, int(center_y / (img_height / 3))))
        
        # Convert to 1-based position
        position = row * 3 + col + 1
        return position
    
    def _select_best_method(self, results: List[List[NoteRegion]]) -> List[NoteRegion]:
        """Select the detection method with highest confidence"""
        if not results:
            return []
        
        # Calculate average confidence for each method
        method_scores = []
        for result in results:
            if not result:
                continue
            
            avg_confidence = sum(region.confidence for region in result) / len(result)
            method_scores.append((result, avg_confidence))
        
        if not method_scores:
            return []
        
        # Select method with highest average confidence
        best_result, best_score = max(method_scores, key=lambda x: x[1])
        
        self.log_metric("best_detection_confidence", best_score)
        self.log_metric("detection_method_used", best_result[0].detection_method if best_result else "none")
        
        return best_result
    
    def _create_3x3_grid(self, image: np.ndarray) -> List[NoteRegion]:
        """Create a 3x3 grid of note regions for Rocketbook images"""
        height, width = image.shape[:2]
        cell_width = width // 3
        cell_height = height // 3
        
        regions = []
        for i in range(9):
            row = i // 3
            col = i % 3
            
            x = col * cell_width
            y = row * cell_height
            w = cell_width
            h = cell_height
            
            region = NoteRegion(
                bbox=(x, y, w, h),
                position=i + 1,
                detection_method="3x3_grid_fallback",
                confidence=0.7  # Moderate confidence for fallback
            )
            regions.append(region)
        
        return regions
    
    def _create_single_region(self, image: np.ndarray) -> NoteRegion:
        """Create a single region covering the entire image"""
        height, width = image.shape[:2]
        return NoteRegion(
            bbox=(0, 0, width, height),
            position=1,
            detection_method="single_note",
            confidence=0.5
        )
    
    async def _create_empty_result(self, reason: str) -> List[NoteRegion]:
        """Create empty result for disabled methods"""
        self.logger.info(f"Detection method disabled: {reason}")
        return []
