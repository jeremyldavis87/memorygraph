from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
import os
import uuid
from datetime import datetime
import braintrust

from app.services.ocr_service import OCRService
from app.services.ai_service import AIService
from app.core.config import settings


class NoteProcessingAgent:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the note processing agent with pydantic-ai and Braintrust observability.
        """
        self.model_name = model_name
        self.ocr_service = OCRService()
        self.ai_service = AIService()
        
        # Initialize Braintrust if API key is available
        self.braintrust_enabled = bool(settings.BRAINTRUST_API_KEY)
        if self.braintrust_enabled:
            braintrust.init(
                api_key=settings.BRAINTRUST_API_KEY,
                project="memorygraph-agent"
            )
        
        # Initialize the agent
        self.agent = Agent(
            model=OpenAIModel(model_name),
            result_type=Dict[str, Any],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the note processing agent.
        """
        return """
        You are an intelligent note processing agent that can detect and process multiple notes in a single image.
        
        Your capabilities:
        1. Detect note boundaries using QR codes, OpenCV contours, or vision analysis
        2. Process each note individually with OCR or vision LLM
        3. Make intelligent decisions about when to use OCR vs vision processing
        4. Extract structured information from handwritten notes
        
        Decision logic:
        - Always try OCR first (cost-effective)
        - Use vision LLM only when OCR confidence is below threshold
        - Prioritize QR code detection for note counting
        - Fall back to contour detection if QR codes are unreliable
        - Use vision LLM as last resort for note detection
        
        You should return structured data about each detected note including:
        - Position in the image
        - Extracted text content
        - Title (if found)
        - Action items (if any)
        - QR code data (if present)
        - Processing method used
        - Confidence score
        """
    
    def process_multi_note_image(self, image_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main entry point for processing multi-note images.
        
        Args:
            image_path: Path to the image file
            config: Configuration including user preferences
        
        Returns:
            List of processed note dictionaries
        """
        # Start Braintrust logging if enabled
        if self.braintrust_enabled:
            return self._process_with_braintrust(image_path, config)
        else:
            return self._process_without_braintrust(image_path, config)
    
    @braintrust.traced(name="process_multi_note_image")
    def _process_with_braintrust(self, image_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process with Braintrust observability."""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Get configuration
            confidence_threshold = config.get("ocr_confidence_threshold", 90)
            vision_model = config.get("vision_model_preference", "gpt-4o-mini")
            
            # Step 1: Detect note count and regions
            note_regions = self._detect_note_regions(image, image_path, vision_model)
            
            # Note: braintrust.log() calls removed due to issues with traced context
            # print(f"Note regions detected: {len(note_regions)}")
            
            if not note_regions:
                # Fallback to single note processing
                result = [self._process_single_note(image_path, config, detection_method="single_note")]
                return result
            
            # Step 2: Process each note region
            processed_notes = []
            for i, region in enumerate(note_regions):
                note_result = self._process_single_note_region(
                    image, region, image_path, config, i + 1
                )
                processed_notes.append(note_result)
                
                # Log individual note processing
                # braintrust.log() calls removed
                pass
            
            # braintrust.log() output removed
            return processed_notes
            
        except Exception as e:
            # Don't use braintrust.log() here as it's outside the traced context
            print(f"Error processing multi-note image: {e}")
            # Fallback to single note processing
            return [self._process_single_note(image_path, config, detection_method="error_fallback")]
    
    def _process_without_braintrust(self, image_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process without Braintrust observability."""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Get configuration
            confidence_threshold = config.get("ocr_confidence_threshold", 90)
            vision_model = config.get("vision_model_preference", "gpt-4o-mini")
            
            # Step 1: Detect note count and regions
            note_regions = self._detect_note_regions(image, image_path, vision_model)
            
            if not note_regions:
                # Fallback to single note processing
                return [self._process_single_note(image_path, config, detection_method="single_note")]
            
            # Step 2: Process each note region
            processed_notes = []
            for i, region in enumerate(note_regions):
                note_result = self._process_single_note_region(
                    image, region, image_path, config, i + 1
                )
                processed_notes.append(note_result)
            
            return processed_notes
            
        except Exception as e:
            print(f"Error processing multi-note image: {e}")
            # Fallback to single note processing
            return [self._process_single_note(image_path, config, detection_method="error_fallback")]
    
    def _detect_note_regions(self, image: np.ndarray, image_path: str, vision_model: str) -> List[Dict[str, Any]]:
        """
        Detect note regions using the hierarchical approach:
        1. QR code detection
        2. OpenCV contour detection
        3. Vision LLM fallback
        """
        # Step 1: Try QR code detection
        qr_codes = self.ocr_service.detect_qr_codes_in_regions(image)
        
        if len(qr_codes) > 1:
            # Use QR codes to determine note regions
            return self._create_regions_from_qr_codes(qr_codes, image)
        
        # Step 2: Try OpenCV contour detection
        contours = self.ocr_service.detect_note_boundaries_opencv(image)
        
        if len(contours) > 1:
            # Use contours to determine note regions
            return self._create_regions_from_contours(contours, image)
        
        # Step 3: Fall back to vision LLM
        vision_result = self.ai_service.detect_note_regions_with_vision(image_path, vision_model)
        
        if vision_result.get("success"):
            return self._create_regions_from_vision_analysis(vision_result, image)
        
        # If all methods fail, return empty list
        return []
    
    def _create_regions_from_qr_codes(self, qr_codes: List[Dict[str, Any]], image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Create note regions based on QR code positions.
        """
        regions = []
        img_height, img_width = image.shape[:2]
        
        # Calculate grid cell size
        cell_width = img_width // 3
        cell_height = img_height // 3
        
        for qr_code in qr_codes:
            position = qr_code["position"]
            
            # Calculate region boundaries based on grid position
            row = (position - 1) // 3
            col = (position - 1) % 3
            
            x = col * cell_width
            y = row * cell_height
            w = cell_width
            h = cell_height
            
            regions.append({
                "bbox": (x, y, w, h),
                "position": position,
                "qr_code": qr_code["data"],
                "detection_method": "qr_code"
            })
        
        return regions
    
    def _create_regions_from_contours(self, contours: List[Tuple[int, int, int, int]], image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Create note regions based on detected contours.
        """
        regions = []
        
        for i, contour in enumerate(contours):
            x, y, w, h = contour
            
            regions.append({
                "bbox": contour,
                "position": i + 1,
                "qr_code": None,
                "detection_method": "contour"
            })
        
        return regions
    
    def _create_regions_from_vision_analysis(self, vision_result: Dict[str, Any], image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Create note regions based on vision LLM analysis.
        """
        regions = []
        
        if "analysis" in vision_result:
            analysis = vision_result["analysis"]
            total_notes = analysis.get("total_notes", 1)
            layout = analysis.get("layout", "single")
            
            img_height, img_width = image.shape[:2]
            
            if "3x3" in layout.lower():
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
                    
                    regions.append({
                        "bbox": (x, y, w, h),
                        "position": i + 1,
                        "qr_code": None,
                        "detection_method": "vision_llm"
                    })
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
                    
                    regions.append({
                        "bbox": (x, y, w, h),
                        "position": position,
                        "qr_code": None,
                        "detection_method": "vision_llm"
                    })
        
        return regions
    
    def _process_single_note_region(self, image: np.ndarray, region: Dict[str, Any], 
                                   image_path: str, config: Dict[str, Any], position: int) -> Dict[str, Any]:
        """
        Process a single note region.
        """
        try:
            # Extract the region from the image
            bbox = region["bbox"]
            region_image = self.ocr_service.extract_region(image, bbox)
            
            # Save region image temporarily
            region_path = f"/tmp/region_{uuid.uuid4()}.jpg"
            cv2.imwrite(region_path, region_image)
            
            # Process the region
            result = self._process_single_note(region_path, config, region["detection_method"])
            
            # Add region-specific metadata
            result["note_position"] = position
            result["qr_code"] = region.get("qr_code")
            result["detection_method"] = region["detection_method"]
            result["bbox"] = bbox
            
            # Clean up temporary file
            if os.path.exists(region_path):
                os.remove(region_path)
            
            return result
            
        except Exception as e:
            print(f"Error processing note region: {e}")
            return self._create_error_note_result(position, str(e))
    
    def _process_single_note(self, image_path: str, config: Dict[str, Any], 
                            detection_method: str = "single") -> Dict[str, Any]:
        """
        Process a single note with OCR and optional vision LLM fallback.
        """
        # Add Braintrust logging if enabled
        if self.braintrust_enabled:
            # Try to use braintrust with experiment.start_span
            try:
                from braintrust import experiment
                with experiment.start_span(
                    name="process_single_note",
                    inputs={
                        "image_path": image_path,
                        "detection_method": detection_method,
                        "config": config
                    }
                ) as span:
                    return self._process_single_note_with_braintrust(image_path, config, detection_method, span)
            except Exception as e:
                print(f"Braintrust span error: {e}")
                # Fall back to non-braintrust processing
                return self._process_single_note_without_braintrust(image_path, config, detection_method)
        else:
            return self._process_single_note_without_braintrust(image_path, config, detection_method)
    
    def _process_single_note_with_braintrust(self, image_path: str, config: Dict[str, Any], 
                                            detection_method: str, span) -> Dict[str, Any]:
        """Process single note with Braintrust observability."""
        try:
            # Get configuration
            confidence_threshold = config.get("ocr_confidence_threshold", 90)
            vision_model = config.get("vision_model_preference", "gpt-4o-mini")
            
            # Step 1: Try OCR first
            ocr_result = self.ocr_service.process_image(image_path)
            
            # Calculate quality score
            quality_score = self.ocr_service.calculate_ocr_quality_score(ocr_result)
            
            span.log(
                ocr_confidence=quality_score,
                confidence_threshold=confidence_threshold,
                ocr_text_length=len(ocr_result.get("content", "")),
                qr_code_detected=bool(ocr_result.get("qr_code"))
            )
            
            # Step 2: Check if OCR quality is sufficient
            if quality_score >= confidence_threshold:
                # OCR is good enough
                span.log(processing_method="ocr", fallback_reason="none")
                result = {
                    "success": True,
                    "content": ocr_result["content"],
                    "original_text": ocr_result["original_text"],
                    "title": ocr_result["title"],
                    "sections": ocr_result["sections"],
                    "action_items": ocr_result["action_items"],
                    "tags": ocr_result["tags"],
                    "confidence": quality_score,
                    "processing_method": "ocr",
                    "qr_code": ocr_result["qr_code"],
                    "detection_method": detection_method
                }
                span.log(output=result)
                return result
            else:
                # OCR quality is insufficient, use vision LLM
                span.log(processing_method="vision_llm", fallback_reason="low_ocr_confidence")
                
                vision_result = self.ai_service.extract_text_from_note_region(
                    image_path, 
                    "Extract all text from this note, preserving formatting",
                    vision_model
                )
                
                span.log(
                    vision_llm_success=vision_result.get("success", False),
                    vision_model_used=vision_model
                )
                
                if vision_result.get("success"):
                    extracted_text = vision_result["extracted_text"]
                    
                    # Process the extracted text with existing OCR methods for structure
                    title = self.ocr_service._extract_title(extracted_text)
                    sections = self.ocr_service._extract_sections(extracted_text)
                    action_items = self.ocr_service._extract_action_items(extracted_text)
                    tags = self.ocr_service._extract_tags(extracted_text)
                    
                    result = {
                        "success": True,
                        "content": extracted_text,
                        "original_text": extracted_text,
                        "title": title,
                        "sections": sections,
                        "action_items": action_items,
                        "tags": tags,
                        "confidence": 95,  # High confidence for vision LLM
                        "processing_method": "vision_llm",
                        "qr_code": ocr_result["qr_code"],  # Still try to get QR code from original
                        "detection_method": detection_method
                    }
                    span.log(output=result)
                    return result
                else:
                    # Vision LLM failed, return OCR result anyway
                    span.log(processing_method="ocr_fallback", fallback_reason="vision_llm_failed")
                    result = {
                        "success": True,
                        "content": ocr_result["content"],
                        "original_text": ocr_result["original_text"],
                        "title": ocr_result["title"],
                        "sections": ocr_result["sections"],
                        "action_items": ocr_result["action_items"],
                        "tags": ocr_result["tags"],
                        "confidence": quality_score,
                        "processing_method": "ocr_fallback",
                        "qr_code": ocr_result["qr_code"],
                        "detection_method": detection_method
                    }
                    span.log(output=result)
                    return result
                    
        except Exception as e:
            span.log(error=str(e))
            print(f"Error processing single note: {e}")
            return self._create_error_note_result(1, str(e))
    
    def _process_single_note_without_braintrust(self, image_path: str, config: Dict[str, Any], 
                                              detection_method: str) -> Dict[str, Any]:
        """Process single note without Braintrust observability."""
        try:
            # Get configuration
            confidence_threshold = config.get("ocr_confidence_threshold", 90)
            vision_model = config.get("vision_model_preference", "gpt-4o-mini")
            
            # Step 1: Try OCR first
            ocr_result = self.ocr_service.process_image(image_path)
            
            # Calculate quality score
            quality_score = self.ocr_service.calculate_ocr_quality_score(ocr_result)
            
            # Step 2: Check if OCR quality is sufficient
            if quality_score >= confidence_threshold:
                # OCR is good enough
                return {
                    "success": True,
                    "content": ocr_result["content"],
                    "original_text": ocr_result["original_text"],
                    "title": ocr_result["title"],
                    "sections": ocr_result["sections"],
                    "action_items": ocr_result["action_items"],
                    "tags": ocr_result["tags"],
                    "confidence": quality_score,
                    "processing_method": "ocr",
                    "qr_code": ocr_result["qr_code"],
                    "detection_method": detection_method
                }
            else:
                # OCR quality is insufficient, use vision LLM
                vision_result = self.ai_service.extract_text_from_note_region(
                    image_path, 
                    "Extract all text from this note, preserving formatting",
                    vision_model
                )
                
                if vision_result.get("success"):
                    extracted_text = vision_result["extracted_text"]
                    
                    # Process the extracted text with existing OCR methods for structure
                    title = self.ocr_service._extract_title(extracted_text)
                    sections = self.ocr_service._extract_sections(extracted_text)
                    action_items = self.ocr_service._extract_action_items(extracted_text)
                    tags = self.ocr_service._extract_tags(extracted_text)
                    
                    return {
                        "success": True,
                        "content": extracted_text,
                        "original_text": extracted_text,
                        "title": title,
                        "sections": sections,
                        "action_items": action_items,
                        "tags": tags,
                        "confidence": 95,  # High confidence for vision LLM
                        "processing_method": "vision_llm",
                        "qr_code": ocr_result["qr_code"],  # Still try to get QR code from original
                        "detection_method": detection_method
                    }
                else:
                    # Vision LLM failed, return OCR result anyway
                    return {
                        "success": True,
                        "content": ocr_result["content"],
                        "original_text": ocr_result["original_text"],
                        "title": ocr_result["title"],
                        "sections": ocr_result["sections"],
                        "action_items": ocr_result["action_items"],
                        "tags": ocr_result["tags"],
                        "confidence": quality_score,
                        "processing_method": "ocr_fallback",
                        "qr_code": ocr_result["qr_code"],
                        "detection_method": detection_method
                    }
                    
        except Exception as e:
            print(f"Error processing single note: {e}")
            return self._create_error_note_result(1, str(e))
    
    def _create_error_note_result(self, position: int, error_message: str) -> Dict[str, Any]:
        """
        Create an error note result.
        """
        return {
            "success": False,
            "content": "",
            "original_text": "",
            "title": f"Error Processing Note {position}",
            "sections": [],
            "action_items": [],
            "tags": [],
            "confidence": 0,
            "processing_method": "error",
            "qr_code": None,
            "detection_method": "error",
            "note_position": position,
            "error": error_message
        }
