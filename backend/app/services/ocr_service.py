import cv2
import pytesseract
from PIL import Image
import numpy as np
from typing import Dict, Any
import re

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
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
        
        # Get confidence scores
        data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Extract title
        title = self._extract_title(text)
        
        # Extract tags
        tags = self._extract_tags(text)
        
        # Extract action items
        action_items = self._extract_action_items(text)
        
        return {
            "original_text": text.strip(),
            "content": text.strip(),
            "title": title,
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
    
    def _extract_title(self, text: str) -> str:
        """
        Extract title from text using various patterns
        """
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