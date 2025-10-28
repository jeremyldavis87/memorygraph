"""
Image Processing Agent

Handles image preprocessing, quality assessment, and color analysis
using OpenCV and scikit-learn for optimal text extraction.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from PIL import Image
import os

try:
    from sklearn.cluster import KMeans
    from collections import Counter
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .base_agent import BaseAgent, PartialResult


class QualityMetrics:
    """Container for image quality assessment metrics"""
    
    def __init__(self, blur_score: float, contrast_score: float, 
                 brightness_score: float, resolution_score: float):
        self.blur_score = blur_score
        self.contrast_score = contrast_score
        self.brightness_score = brightness_score
        self.resolution_score = resolution_score
        self.overall_quality = self._calculate_overall_quality()
    
    def _calculate_overall_quality(self) -> float:
        """Calculate overall quality score from individual metrics"""
        weights = {
            'blur': 0.3,
            'contrast': 0.3,
            'brightness': 0.2,
            'resolution': 0.2
        }
        
        return (
            self.blur_score * weights['blur'] +
            self.contrast_score * weights['contrast'] +
            self.brightness_score * weights['brightness'] +
            self.resolution_score * weights['resolution']
        )


class RGBColor:
    """Container for RGB color information"""
    
    def __init__(self, rgb: List[int], hex_color: str, name: str):
        self.rgb = rgb
        self.hex = hex_color
        self.name = name


class ImageProcessingAgent(BaseAgent):
    """
    Agent responsible for image preprocessing and quality assessment.
    
    Capabilities:
    - Noise reduction and denoising
    - Contrast enhancement
    - Deskewing and rotation correction
    - Image quality assessment
    - Color analysis and extraction
    """
    
    def __init__(self):
        super().__init__("ImageProcessingAgent")
        
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn not available, color analysis will be limited")
    
    async def process(self, image_path: str) -> Union[Dict[str, Any], PartialResult]:
        """
        Main processing method for image preprocessing.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Dictionary containing processed image path and quality metrics
        """
        return await self.execute_with_retry(self._process_image, image_path)
    
    async def _process_image(self, image_path: str) -> Dict[str, Any]:
        """Internal method to process the image"""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Assess original quality
        original_quality = self.assess_quality(image)
        
        # Preprocess image
        processed_image = self.preprocess(image)
        
        # Save processed image
        processed_path = self._save_processed_image(processed_image, image_path)
        
        # Extract color information
        color_info = self.extract_colors(image)
        
        # Log metrics
        self.log_metric("image_quality", original_quality.overall_quality)
        self.log_metric("contrast_score", original_quality.contrast_score)
        self.log_metric("blur_score", original_quality.blur_score)
        
        return {
            "original_path": image_path,
            "processed_path": processed_path,
            "original_dimensions": {
                "width": image.shape[1],
                "height": image.shape[0]
            },
            "quality_metrics": {
                "blur_score": original_quality.blur_score,
                "contrast_score": original_quality.contrast_score,
                "brightness_score": original_quality.brightness_score,
                "resolution_score": original_quality.resolution_score,
                "overall_quality": original_quality.overall_quality
            },
            "color_info": color_info,
            "processing_applied": [
                "denoise",
                "contrast_enhancement", 
                "deskew"
            ]
        }
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Apply comprehensive preprocessing to improve OCR quality.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale for processing
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply denoising
        denoised = self._denoise_image(gray)
        
        # Enhance contrast
        enhanced = self._enhance_contrast(denoised)
        
        # Deskew image
        deskewed, rotation_angle = self._deskew_image(enhanced)
        
        # Apply adaptive thresholding for OCR
        binary = self._binarize_for_ocr(deskewed)
        
        return binary
    
    def assess_quality(self, image: np.ndarray) -> QualityMetrics:
        """
        Assess image quality for OCR readiness.
        
        Args:
            image: Input image
            
        Returns:
            QualityMetrics object with quality scores
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Blur detection using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = min(1.0, laplacian_var / 100.0)  # Normalize
        
        # Contrast measurement
        contrast = gray.std()
        contrast_score = min(1.0, contrast / 127.5)  # Normalize to 0-1
        
        # Brightness check
        brightness = gray.mean()
        brightness_score = min(1.0, abs(brightness - 127.5) / 127.5)  # Optimal around 127.5
        
        # Resolution adequacy
        height, width = gray.shape
        resolution_score = min(1.0, (height * width) / (1000 * 1000))  # Normalize to 1MP
        
        return QualityMetrics(
            blur_score=blur_score,
            contrast_score=contrast_score,
            brightness_score=brightness_score,
            resolution_score=resolution_score
        )
    
    def extract_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract color information from the image.
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with color analysis results
        """
        if not SKLEARN_AVAILABLE:
            return self._extract_colors_simple(image)
        
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
                "rgb": dominant_color.rgb,
                "hex": dominant_color.hex,
                "name": dominant_color.name
            },
            "background_color": {
                "rgb": background_color.rgb,
                "hex": background_color.hex,
                "name": background_color.name
            },
            "estimated_note_type": note_type,
            "physical_size_estimate": self._estimate_size(image.shape)
        }
    
    def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Apply non-local means denoising"""
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Apply CLAHE for adaptive contrast enhancement"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)
    
    def _deskew_image(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Detect and correct image skew/rotation"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image, 0.0
        
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only rotate if angle is significant
        if abs(angle) < 1.0:
            return image, angle
        
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
                               flags=cv2.INTER_CUBIC,
                               borderMode=cv2.BORDER_REPLICATE)
        
        return rotated, angle
    
    def _binarize_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Convert to optimal binary image for OCR"""
        # Adaptive thresholding works best for varied lighting
        binary = cv2.adaptiveThreshold(
            image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        return binary
    
    def _get_dominant_color(self, image_rgb: np.ndarray, k: int = 5) -> RGBColor:
        """Find dominant color using k-means clustering"""
        if not SKLEARN_AVAILABLE:
            # Fallback to simple histogram-based approach
            return self._get_dominant_color_simple(image_rgb)
        
        # Reshape image to list of pixels
        pixels = image_rgb.reshape(-1, 3)
        
        # Sample pixels for efficiency
        if len(pixels) > 10000:
            indices = np.random.choice(len(pixels), 10000, replace=False)
            pixels = pixels[indices]
        
        # Cluster colors
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Find most common cluster
        labels = kmeans.labels_
        counts = Counter(labels)
        dominant_cluster = counts.most_common(1)[0][0]
        
        # Get RGB values
        dominant_rgb = kmeans.cluster_centers_[dominant_cluster].astype(int)
        
        return RGBColor(
            rgb=dominant_rgb.tolist(),
            hex_color=self._rgb_to_hex(dominant_rgb),
            name=self._rgb_to_name(dominant_rgb)
        )
    
    def _get_background_color(self, image_rgb: np.ndarray) -> RGBColor:
        """Estimate background/note color by sampling edges"""
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
        
        return RGBColor(
            rgb=median_color.tolist(),
            hex_color=self._rgb_to_hex(median_color),
            name=self._rgb_to_name(median_color)
        )
    
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
    
    def _estimate_note_type(self, background_color: RGBColor) -> str:
        """Estimate physical note type based on color"""
        color_name = background_color.name
        
        if color_name in ['yellow', 'pink', 'blue', 'green', 'orange']:
            return 'sticky_note'
        elif color_name in ['white']:
            return 'paper'
        else:
            return 'unknown'
    
    def _estimate_size(self, image_shape: Tuple[int, int, int]) -> str:
        """Estimate physical size based on image dimensions"""
        height, width = image_shape[:2]
        
        # Rough estimation based on typical sticky note proportions
        if width > height:
            aspect_ratio = width / height
        else:
            aspect_ratio = height / width
        
        if 0.8 <= aspect_ratio <= 1.2:
            return "3x3_inches"
        elif 0.6 <= aspect_ratio <= 0.8:
            return "3x5_inches"
        else:
            return "unknown"
    
    def _extract_colors_simple(self, image: np.ndarray) -> Dict[str, Any]:
        """Simple color extraction without scikit-learn"""
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get average color
        avg_color = np.mean(image_rgb.reshape(-1, 3), axis=0).astype(int)
        
        return {
            "dominant_color": {
                "rgb": avg_color.tolist(),
                "hex": self._rgb_to_hex(avg_color),
                "name": self._rgb_to_name(avg_color)
            },
            "background_color": {
                "rgb": avg_color.tolist(),
                "hex": self._rgb_to_hex(avg_color),
                "name": self._rgb_to_name(avg_color)
            },
            "estimated_note_type": self._estimate_note_type(
                RGBColor(avg_color.tolist(), self._rgb_to_hex(avg_color), self._rgb_to_name(avg_color))
            ),
            "physical_size_estimate": self._estimate_size(image.shape)
        }
    
    def _get_dominant_color_simple(self, image_rgb: np.ndarray) -> RGBColor:
        """Simple dominant color extraction without clustering"""
        # Get average color
        avg_color = np.mean(image_rgb.reshape(-1, 3), axis=0).astype(int)
        
        return RGBColor(
            rgb=avg_color.tolist(),
            hex_color=self._rgb_to_hex(avg_color),
            name=self._rgb_to_name(avg_color)
        )
    
    def _save_processed_image(self, processed_image: np.ndarray, original_path: str) -> str:
        """Save processed image to disk"""
        # Generate processed image path
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        processed_dir = os.path.join(os.path.dirname(original_path), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        
        processed_path = os.path.join(processed_dir, f"{base_name}_processed.jpg")
        
        # Save image
        cv2.imwrite(processed_path, processed_image)
        
        return processed_path
