import os
import uuid
from typing import Optional
from PIL import Image
import cv2
import numpy as np

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension"""
    file_extension = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"

def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    os.makedirs(directory_path, exist_ok=True)

def is_valid_image(file_path: str) -> bool:
    """Check if file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def resize_image_if_needed(image_path: str, max_width: int = 1920, max_height: int = 1080) -> str:
    """Resize image if it's too large, return path to resized image"""
    try:
        with Image.open(image_path) as img:
            if img.width <= max_width and img.height <= max_height:
                return image_path
            
            # Calculate new dimensions maintaining aspect ratio
            ratio = min(max_width / img.width, max_height / img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save resized image
            resized_path = image_path.replace('.', '_resized.')
            resized_img.save(resized_path, quality=95)
            
            return resized_path
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_path

def preprocess_image_for_ocr(image_path: str) -> str:
    """Preprocess image for better OCR results"""
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return image_path
        
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
        
        # Save processed image
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, cleaned)
        
        return processed_path
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return image_path