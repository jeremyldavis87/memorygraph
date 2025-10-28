"""
Metadata Agent

Handles extraction of non-textual information including QR codes,
color analysis, EXIF metadata, and color-to-category mapping.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
import os

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

from .base_agent import BaseAgent, PartialResult


class QRCode:
    """Container for QR code information"""
    
    def __init__(self, data: str, qr_type: str, position: Dict[str, int], confidence: float = 1.0):
        self.data = data
        self.type = qr_type
        self.position = position
        self.confidence = confidence


class MetadataAgent(BaseAgent):
    """
    Agent responsible for extracting non-textual metadata from images.
    
    Capabilities:
    - QR code scanning with rotation support
    - Color analysis and extraction
    - Color-to-category mapping for QR code association
    - EXIF metadata extraction
    - Image properties analysis
    """
    
    def __init__(self):
        super().__init__("MetadataAgent")
        
        if not PYZBAR_AVAILABLE:
            self.logger.warning("pyzbar not available, QR code scanning will be disabled")
        
        # Color-to-category mappings (can be configured)
        self.color_category_mappings = {
            'yellow': 'general',
            'pink': 'urgent',
            'blue': 'work',
            'green': 'personal',
            'orange': 'ideas',
            'white': 'notes',
            'gray': 'archive'
        }
    
    async def process(self, image_path: str, color_info: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], PartialResult]:
        """
        Main processing method for metadata extraction.
        
        Args:
            image_path: Path to the input image
            color_info: Optional color information from ImageProcessingAgent
            
        Returns:
            Dictionary with metadata or PartialResult if processing fails
        """
        return await self.execute_with_retry(self._extract_metadata, image_path, color_info)
    
    async def _extract_metadata(self, image_path: str, color_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Internal method to extract metadata"""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Scan QR codes
        qr_codes = self._scan_qr_codes(image)
        
        # Analyze colors (if not provided)
        if color_info is None:
            color_analysis = self._analyze_colors(image)
        else:
            color_analysis = color_info
        
        # Extract EXIF metadata
        exif_data = self._extract_exif_metadata(image_path)
        
        # Associate colors with QR codes
        color_qr_associations = self._associate_color_with_qr(qr_codes, color_analysis)
        
        # Log metrics
        self.log_metric("qr_codes_found", len(qr_codes))
        self.log_metric("has_exif_data", 1 if exif_data else 0)
        
        return {
            "qr_codes": [
                {
                    "data": qr.data,
                    "type": qr.type,
                    "position": qr.position,
                    "confidence": qr.confidence
                }
                for qr in qr_codes
            ],
            "color_analysis": color_analysis,
            "exif_metadata": exif_data,
            "color_qr_associations": color_qr_associations,
            "image_properties": {
                "width": image.shape[1],
                "height": image.shape[0],
                "channels": image.shape[2] if len(image.shape) == 3 else 1,
                "file_size": os.path.getsize(image_path) if os.path.exists(image_path) else 0
            }
        }
    
    def _scan_qr_codes(self, image: np.ndarray) -> List[QRCode]:
        """Scan image for QR codes with rotation support"""
        if not PYZBAR_AVAILABLE:
            return []
        
        qr_codes = []
        
        # Try multiple orientations if initial scan fails
        for rotation in [0, 90, 180, 270]:
            rotated = self._rotate_image(image, rotation)
            
            try:
                # Convert OpenCV image to PIL Image for pyzbar
                image_rgb = cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image_rgb)
                
                # Decode QR codes
                decoded_objects = pyzbar.decode(pil_image)
                
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    qr_type = obj.type
                    
                    # Get position (adjust for rotation)
                    rect = obj.rect
                    position = self._adjust_position_for_rotation(
                        rect.left, rect.top, rect.width, rect.height,
                        rotation, image.shape[1], image.shape[0]
                    )
                    
                    qr_codes.append(QRCode(
                        data=qr_data,
                        qr_type=qr_type,
                        position=position,
                        confidence=1.0
                    ))
                
                # If we found QR codes, no need to try other rotations
                if qr_codes:
                    break
                    
            except Exception as e:
                self.logger.warning(f"QR code scanning failed for rotation {rotation}: {e}")
                continue
        
        # Remove duplicates based on data content
        unique_qr_codes = self._deduplicate_qr_codes(qr_codes)
        
        return unique_qr_codes
    
    def _rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by specified angle"""
        if angle == 0:
            return image
        
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        return rotated
    
    def _adjust_position_for_rotation(self, x: int, y: int, width: int, height: int,
                                   rotation: int, img_width: int, img_height: int) -> Dict[str, int]:
        """Adjust QR code position for rotation"""
        if rotation == 0:
            return {"x": x, "y": y, "width": width, "height": height}
        elif rotation == 90:
            return {"x": img_height - y - height, "y": x, "width": height, "height": width}
        elif rotation == 180:
            return {"x": img_width - x - width, "y": img_height - y - height, "width": width, "height": height}
        elif rotation == 270:
            return {"x": y, "y": img_width - x - width, "width": height, "height": width}
        else:
            return {"x": x, "y": y, "width": width, "height": height}
    
    def _deduplicate_qr_codes(self, qr_codes: List[QRCode]) -> List[QRCode]:
        """Remove duplicate QR codes based on data content"""
        seen_data = set()
        unique_codes = []
        
        for qr in qr_codes:
            if qr.data not in seen_data:
                seen_data.add(qr.data)
                unique_codes.append(qr)
        
        return unique_codes
    
    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze colors in the image"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get dominant color
        dominant_color = self._get_dominant_color(image_rgb)
        
        # Get background color
        background_color = self._get_background_color(image_rgb)
        
        # Estimate note type
        note_type = self._estimate_note_type(background_color)
        
        return {
            "dominant_color": {
                "rgb": dominant_color["rgb"],
                "hex": dominant_color["hex"],
                "name": dominant_color["name"]
            },
            "background_color": {
                "rgb": background_color["rgb"],
                "hex": background_color["hex"],
                "name": background_color["name"]
            },
            "estimated_note_type": note_type
        }
    
    def _get_dominant_color(self, image_rgb: np.ndarray) -> Dict[str, Any]:
        """Get dominant color using simple histogram approach"""
        # Reshape image to list of pixels
        pixels = image_rgb.reshape(-1, 3)
        
        # Sample pixels for efficiency
        if len(pixels) > 10000:
            indices = np.random.choice(len(pixels), 10000, replace=False)
            pixels = pixels[indices]
        
        # Get average color
        avg_color = np.mean(pixels, axis=0).astype(int)
        
        return {
            "rgb": avg_color.tolist(),
            "hex": self._rgb_to_hex(avg_color),
            "name": self._rgb_to_name(avg_color)
        }
    
    def _get_background_color(self, image_rgb: np.ndarray) -> Dict[str, Any]:
        """Estimate background color by sampling edges"""
        h, w = image_rgb.shape[:2]
        
        # Sample pixels from edges (likely background)
        edge_pixels = []
        edge_pixels.extend(image_rgb[0, :, :].reshape(-1, 3))  # Top
        edge_pixels.extend(image_rgb[-1, :, :].reshape(-1, 3))  # Bottom
        edge_pixels.extend(image_rgb[:, 0, :].reshape(-1, 3))   # Left
        edge_pixels.extend(image_rgb[:, -1, :].reshape(-1, 3))  # Right
        
        edge_pixels = np.array(edge_pixels)
        
        # Get median color (more robust than mean)
        median_color = np.median(edge_pixels, axis=0).astype(int)
        
        return {
            "rgb": median_color.tolist(),
            "hex": self._rgb_to_hex(median_color),
            "name": self._rgb_to_name(median_color)
        }
    
    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        """Convert RGB to hex"""
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    def _rgb_to_name(self, rgb: np.ndarray) -> str:
        """Map RGB to common color name"""
        COLOR_NAMES = {
            'yellow': ([200, 200, 0], [255, 255, 180]),
            'pink': ([255, 150, 150], [255, 220, 220]),
            'blue': ([100, 150, 200], [180, 220, 255]),
            'green': ([150, 200, 150], [200, 255, 200]),
            'orange': ([255, 150, 50], [255, 220, 150]),
            'white': ([240, 240, 240], [255, 255, 255]),
            'gray': ([150, 150, 150], [200, 200, 200]),
        }
        
        for name, (lower, upper) in COLOR_NAMES.items():
            if all(lower[i] <= rgb[i] <= upper[i] for i in range(3)):
                return name
        
        return 'unknown'
    
    def _estimate_note_type(self, background_color: Dict[str, Any]) -> str:
        """Estimate physical note type based on color"""
        color_name = background_color["name"]
        
        if color_name in ['yellow', 'pink', 'blue', 'green', 'orange']:
            return 'sticky_note'
        elif color_name in ['white']:
            return 'paper'
        else:
            return 'unknown'
    
    def _extract_exif_metadata(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Extract EXIF metadata from image"""
        try:
            with Image.open(image_path) as image:
                exif_data = image._getexif()
                
                if exif_data is None:
                    return None
                
                exif_dict = {}
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_dict[tag] = value
                
                # Extract useful metadata
                useful_metadata = {}
                
                if 'DateTime' in exif_dict:
                    useful_metadata['capture_time'] = exif_dict['DateTime']
                
                if 'Make' in exif_dict:
                    useful_metadata['camera_make'] = exif_dict['Make']
                
                if 'Model' in exif_dict:
                    useful_metadata['camera_model'] = exif_dict['Model']
                
                if 'GPSInfo' in exif_dict:
                    useful_metadata['gps_info'] = exif_dict['GPSInfo']
                
                return useful_metadata if useful_metadata else None
                
        except Exception as e:
            self.logger.warning(f"EXIF extraction failed: {e}")
            return None
    
    def _associate_color_with_qr(self, qr_codes: List[QRCode], color_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Associate colors with QR codes for category mapping"""
        associations = []
        
        background_color_name = color_analysis.get("background_color", {}).get("name", "unknown")
        
        for qr in qr_codes:
            # Map color to category
            category = self.color_category_mappings.get(background_color_name, "general")
            
            # Check if QR code contains category information
            qr_data = qr.data.lower()
            if any(keyword in qr_data for keyword in ['work', 'business', 'office']):
                category = "work"
            elif any(keyword in qr_data for keyword in ['urgent', 'priority', 'asap']):
                category = "urgent"
            elif any(keyword in qr_data for keyword in ['personal', 'home', 'family']):
                category = "personal"
            elif any(keyword in qr_data for keyword in ['idea', 'brainstorm', 'creative']):
                category = "ideas"
            
            associations.append({
                "qr_data": qr.data,
                "color_name": background_color_name,
                "suggested_category": category,
                "confidence": 0.8 if background_color_name != "unknown" else 0.5
            })
        
        return associations
