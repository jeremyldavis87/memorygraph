import cv2
import pytesseract
from PIL import Image
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import re
from pyzbar import pyzbar

class OCRService:
    def __init__(self):
        # Configure Tesseract
        self.tesseract_config = r'--oem 3 --psm 6'
    
    def process_image(self, image_path: str, mode: str = "traditional") -> Dict[str, Any]:
        """
        Process image with OCR and extract text, title, and other information
        """
        # Load and preprocess image
        image = cv2.imread(image_path)
        processed_image = self._preprocess_image(image)
        
        # Detect QR code first
        qr_code = self._detect_qr_code(image)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
        
        # Get confidence scores
        data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Extract title with ## pattern support
        title = self._extract_title(text)
        
        # Extract section headers
        sections = self._extract_sections(text)
        
        # Extract tags
        tags = self._extract_tags(text)
        
        # Extract action items
        action_items = self._extract_action_items(text)
        
        return {
            "original_text": text.strip(),
            "content": text.strip(),
            "title": title,
            "sections": sections,
            "qr_code": qr_code,
            "confidence": int(avg_confidence),
            "tags": tags,
            "action_items": action_items
        }
    
    def _preprocess_image(self, image):
        """
        Preprocess image for better OCR results
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _detect_qr_code(self, image) -> Optional[str]:
        """
        Detect and decode QR codes in the image
        """
        try:
            # Convert OpenCV image to PIL Image for pyzbar
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Decode QR codes
            decoded_objects = pyzbar.decode(pil_image)
            
            if decoded_objects:
                # Return the first QR code found
                return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            print(f"QR code detection error: {e}")
        
        return None
    
    def _extract_title(self, text: str) -> str:
        """
        Extract title from text using various patterns, prioritizing ##Title## format
        """
        # Priority 1: Look for ##Title## pattern
        hash_pattern = r'##([^#]+)##'
        matches = re.findall(hash_pattern, text)
        if matches:
            return matches[0].strip()
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for underlined text (common in handwritten notes)
            if line.startswith('_') and line.endswith('_'):
                return line[1:-1].strip()
            
            # Check for all caps (common for titles)
            if line.isupper() and len(line) > 3:
                return line.title()
            
            # Check for text in brackets or parentheses
            if (line.startswith('[') and line.endswith(']')) or \
               (line.startswith('(') and line.endswith(')')):
                return line[1:-1].strip()
            
            # Check for text with asterisks
            if line.startswith('*') and line.endswith('*'):
                return line[1:-1].strip()
            
            # First non-empty line as fallback
            if len(line) > 3:
                return line
        
        return "Untitled"
    
    def _extract_sections(self, text: str) -> list:
        """
        Extract all ##...## patterns as section headers
        """
        hash_pattern = r'##([^#]+)##'
        matches = re.findall(hash_pattern, text)
        return [{"title": match.strip(), "type": "section"} for match in matches]
    
    def _extract_tags(self, text: str) -> list:
        """
        Extract tags from text (@tag format)
        """
        tag_pattern = r'@(\w+(?:-\w+)*)'
        tags = re.findall(tag_pattern, text)
        return [{"name": tag, "type": "simple"} for tag in tags]
    
    def _extract_action_items(self, text: str) -> list:
        """
        Extract action items and checkboxes from text
        """
        action_items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for checkbox patterns
            checkbox_patterns = [
                r'\[\s*\]',  # [ ]
                r'\[\s*x\s*\]',  # [x]
                r'\[\s*✓\s*\]',  # [✓]
                r'-\s*\[\s*\]',  # - [ ]
                r'-\s*\[\s*x\s*\]',  # - [x]
            ]
            
            for pattern in checkbox_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract text after checkbox
                    item_text = re.sub(pattern, '', line).strip()
                    if item_text:
                        action_items.append({
                            "text": item_text,
                            "completed": 'x' in line.lower() or '✓' in line,
                            "priority": "normal"
                        })
                    break
        
        return action_items
    
    def detect_note_boundaries_opencv(self, image) -> List[Tuple[int, int, int, int]]:
        """
        Detect note boundaries using OpenCV contour detection.
        Returns list of bounding boxes (x, y, width, height) for detected notes.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        note_regions = []
        min_area = 10000  # Minimum area for a note (adjust based on image size)
        aspect_ratio_range = (0.5, 2.0)  # Expected aspect ratio range for notes
        
        for contour in contours:
            # Calculate contour area
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check aspect ratio
            aspect_ratio = w / h
            if not (aspect_ratio_range[0] <= aspect_ratio <= aspect_ratio_range[1]):
                continue
            
            # Check if contour is roughly rectangular
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # If it has 4 corners, it's likely a rectangle
            if len(approx) >= 4:
                note_regions.append((x, y, w, h))
        
        # Sort by position (top to bottom, left to right)
        note_regions.sort(key=lambda box: (box[1], box[0]))
        
        return note_regions
    
    def extract_region(self, image, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract a region from the image using the bounding box.
        bbox: (x, y, width, height)
        """
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]
    
    def calculate_ocr_quality_score(self, ocr_result: Dict[str, Any]) -> float:
        """
        Calculate a quality score for OCR results based on confidence and text characteristics.
        Returns a score between 0 and 100.
        """
        confidence = ocr_result.get("confidence", 0)
        text = ocr_result.get("original_text", "")
        
        # Base score from OCR confidence
        base_score = confidence
        
        # Adjust score based on text characteristics
        if not text.strip():
            return 0
        
        # Check for common OCR errors
        error_patterns = [
            r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\{\}\"\'\/\\]',  # Unusual characters
            r'\b\w{1}\b',  # Single character words (often OCR errors)
            r'\b\w{20,}\b',  # Very long words (often OCR errors)
        ]
        
        error_penalty = 0
        for pattern in error_patterns:
            matches = re.findall(pattern, text)
            error_penalty += len(matches) * 2  # Penalty per error
        
        # Check for reasonable text structure
        lines = text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if len(non_empty_lines) < 2:
            error_penalty += 10  # Penalty for very short text
        
        # Calculate final score
        final_score = max(0, base_score - error_penalty)
        return min(100, final_score)
    
    def detect_qr_codes_in_regions(self, image) -> List[Dict[str, Any]]:
        """
        Detect QR codes in the image and return their locations and data.
        Returns list of dictionaries with 'data', 'bbox', and 'position' keys.
        """
        try:
            # Convert OpenCV image to PIL Image for pyzbar
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Decode QR codes
            decoded_objects = pyzbar.decode(pil_image)
            
            qr_codes = []
            for obj in decoded_objects:
                # Get bounding box
                rect = obj.rect
                bbox = (rect.left, rect.top, rect.width, rect.height)
                
                # Estimate position in grid (rough approximation)
                img_height, img_width = image.shape[:2]
                position = self._estimate_grid_position(bbox, img_width, img_height)
                
                qr_codes.append({
                    'data': obj.data.decode('utf-8'),
                    'bbox': bbox,
                    'position': position
                })
            
            return qr_codes
        except Exception as e:
            print(f"QR code detection error: {e}")
            return []
    
    def _estimate_grid_position(self, bbox: Tuple[int, int, int, int], img_width: int, img_height: int) -> int:
        """
        Estimate the position of a QR code in a grid layout.
        Assumes a 3x3 grid layout and returns position (1-9).
        """
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