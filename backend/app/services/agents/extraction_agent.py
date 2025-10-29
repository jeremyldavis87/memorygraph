"""
Extraction Agent

Handles text extraction using parallel processing of OCR and Vision LLM.
Merges results with Vision LLM as ground truth for optimal accuracy.
"""

import asyncio
import cv2
import numpy as np
from typing import Dict, Any, Optional, Union, Tuple, List
from difflib import SequenceMatcher
import re

from .base_agent import BaseAgent, PartialResult
from app.services.ai_service import AIService
from app.core.config import settings


class ExtractionResult:
    """Container for text extraction results"""
    
    def __init__(self, text: str, confidence: float, method: str, 
                 raw_data: Optional[Dict[str, Any]] = None):
        self.text = text
        self.confidence = confidence
        self.method = method
        self.raw_data = raw_data or {}


class HybridResult:
    """Container for hybrid extraction results"""
    
    def __init__(self, text: str, confidence: float, ocr_version: str, 
                 llm_version: str, differences: List[str], extraction_method: str):
        self.text = text
        self.confidence = confidence
        self.ocr_version = ocr_version
        self.llm_version = llm_version
        self.differences = differences
        self.extraction_method = extraction_method


class ExtractionAgent(BaseAgent):
    """
    Agent responsible for text extraction using parallel OCR and Vision LLM processing.
    
    Capabilities:
    - Parallel OCR and Vision LLM execution
    - Result merging with Vision LLM as ground truth
    - Confidence scoring and quality assessment
    - Error handling and fallback strategies
    """
    
    def __init__(self):
        super().__init__("ExtractionAgent")
        self.ai_service = AIService()
        
    
    async def process(self, image_path: str, region_bbox: Optional[Tuple[int, int, int, int]] = None, config: Optional[Dict[str, Any]] = None) -> Union[HybridResult, PartialResult]:
        """
        Main processing method for text extraction.
        
        Args:
            image_path: Path to the input image
            region_bbox: Optional bounding box (x, y, width, height) for region extraction
            config: Optional configuration dict with ocr_mode setting
            
        Returns:
            HybridResult with merged text or PartialResult if processing fails
        """
        return await self.execute_with_retry(self._extract_parallel, image_path, region_bbox, config)
    
    async def _extract_parallel(self, image_path: str, region_bbox: Optional[Tuple[int, int, int, int]] = None, config: Optional[Dict[str, Any]] = None) -> HybridResult:
        """Internal method to run OCR and Vision LLM based on ocr_mode"""
        # Get ocr_mode from config
        ocr_mode = config.get("ocr_mode", "auto") if config else "auto"
        
        # Prepare image for extraction
        if region_bbox:
            # Extract region from image
            image = cv2.imread(image_path)
            x, y, w, h = region_bbox
            region_image = image[y:y+h, x:x+w]
            
            # Save region image temporarily
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                cv2.imwrite(tmp_file.name, region_image)
                region_path = tmp_file.name
        else:
            region_path = image_path
        
        try:
            # Only use Vision LLM (traditional OCR removed)
            if ocr_mode == "llm":
                # Only use Vision LLM
                self.logger.info("Using LLM mode (Vision LLM only)")
                llm_result = await self._extract_with_vision(region_path)
                
                # In LLM-only mode, fail hard if Vision LLM fails
                if llm_result.confidence == 0.0 or not llm_result.text or len(llm_result.text.strip()) == 0:
                    error_msg = llm_result.raw_data.get("error", "Vision LLM extraction failed")
                    self.logger.error(f"LLM-only mode failed: {error_msg}")
                    return self.create_partial_result(
                        error=f"Vision LLM extraction failed in LLM-only mode: {error_msg}",
                        data={"image_path": region_path, "ocr_mode": ocr_mode}
                    )
                
                return HybridResult(
                    text=llm_result.text,
                    confidence=llm_result.confidence,
                    ocr_version="",
                    llm_version=llm_result.text,
                    differences=["OCR skipped in LLM mode"],
                    extraction_method="vision_only"
                )
            else:
                # Default: hybrid mode (auto) - run both in parallel
                self.logger.info("Using hybrid mode (OCR + Vision LLM)")
                ocr_task = asyncio.create_task(self._extract_with_ocr(region_path))
                llm_task = asyncio.create_task(self._extract_with_vision(region_path))
                
                # Wait for both to complete
                ocr_result, llm_result = await asyncio.gather(ocr_task, llm_task)
                
                # Merge results
                merged_result = self._merge_results(ocr_result, llm_result)
                
                # Log metrics
                self.log_metric("ocr_confidence", ocr_result.confidence)
                self.log_metric("llm_confidence", llm_result.confidence)
                self.log_metric("final_confidence", merged_result.confidence)
                self.log_metric("text_length", len(merged_result.text))
                
                return merged_result
            
        finally:
            # Clean up temporary file if created
            if region_bbox and region_path != image_path:
                try:
                    import os
                    os.unlink(region_path)
                except:
                    pass
    
    
    async def _extract_with_vision(self, image_path: str) -> ExtractionResult:
        """Extract text using Vision LLM"""
        try:
            self.logger.info(f"Starting Vision LLM extraction for: {image_path}")
            
            # Use AI service for vision extraction
            vision_result = self.ai_service.extract_text_from_note_region(
                image_path,
                "Extract all text from this note, preserving formatting and structure. "
                "Pay special attention to titles marked with ##Title## format, "
                "bullet points, numbered lists, and checkboxes.",
                settings.AGENT_VISION_MODEL
            )
            
            self.logger.info(f"Vision LLM result: success={vision_result.get('success')}")
            
            if not vision_result.get("success"):
                error_msg = vision_result.get("error", "Unknown error")
                self.logger.error(f"Vision LLM extraction failed: {error_msg}")
                return ExtractionResult(
                    text="",
                    confidence=0.0,
                    method="vision_llm_failed",
                    raw_data={"error": error_msg}
                )
            
            extracted_text = vision_result["extracted_text"]
            self.logger.info(f"Vision LLM extracted {len(extracted_text)} characters")
            self.logger.debug(f"Extracted text preview: {extracted_text[:500]}")
            
            # Calculate confidence based on text characteristics
            confidence = self._calculate_vision_confidence(extracted_text)
            
            self.logger.info(f"Vision LLM confidence: {confidence}")
            
            return ExtractionResult(
                text=extracted_text.strip(),
                confidence=confidence,
                method="vision_llm",
                raw_data={
                    "model_used": vision_result.get("model_used", settings.AGENT_VISION_MODEL),
                    "word_count": len(extracted_text.split()),
                    "character_count": len(extracted_text)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Vision LLM extraction exception: {e}", exc_info=True)
            return ExtractionResult(
                text="",
                confidence=0.0,
                method="vision_llm_failed",
                raw_data={"error": str(e)}
            )
    
    
    def _calculate_vision_confidence(self, text: str) -> float:
        """Calculate confidence score for Vision LLM results"""
        if not text.strip():
            return 0.0
        
        # Base confidence for Vision LLM
        base_confidence = 0.9
        
        # Adjust based on text characteristics
        word_count = len(text.split())
        char_count = len(text)
        
        # Penalty for very short text
        if word_count < 3:
            base_confidence -= 0.2
        elif word_count < 10:
            base_confidence -= 0.1
        
        # Bonus for structured content
        if '##' in text:  # Has titles
            base_confidence += 0.05
        if any(marker in text for marker in ['•', '-', '*', '1.', '2.', '3.']):  # Has lists
            base_confidence += 0.05
        if any(marker in text for marker in ['[ ]', '[x]', '☐', '☑']):  # Has checkboxes
            base_confidence += 0.05
        
        return min(1.0, max(0.0, base_confidence))
    
    def _merge_results(self, ocr_result: ExtractionResult, llm_result: ExtractionResult) -> HybridResult:
        """Merge OCR and Vision LLM results with LLM as ground truth"""
        # If Vision LLM failed, use OCR result
        if llm_result.confidence == 0.0:
            return HybridResult(
                text=ocr_result.text,
                confidence=ocr_result.confidence,
                ocr_version=ocr_result.text,
                llm_version="",
                differences=["Vision LLM failed"],
                extraction_method="ocr_only"
            )
        
        # If OCR failed, use Vision LLM result
        if ocr_result.confidence == 0.0:
            return HybridResult(
                text=llm_result.text,
                confidence=llm_result.confidence,
                ocr_version="",
                llm_version=llm_result.text,
                differences=["OCR failed"],
                extraction_method="vision_only"
            )
        
        # Both succeeded, merge with LLM as ground truth
        merged_text, differences = self._merge_texts(ocr_result.text, llm_result.text)
        
        # Calculate hybrid confidence
        hybrid_confidence = self._calculate_hybrid_confidence(ocr_result, llm_result)
        
        return HybridResult(
            text=merged_text,
            confidence=hybrid_confidence,
            ocr_version=ocr_result.text,
            llm_version=llm_result.text,
            differences=differences,
            extraction_method="hybrid"
        )
    
    def _merge_texts(self, ocr_text: str, llm_text: str) -> Tuple[str, List[str]]:
        """Merge OCR and LLM texts using sequence matching"""
        # Use sequence matcher to align texts
        matcher = SequenceMatcher(None, ocr_text, llm_text)
        
        merged_text = []
        differences = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Both agree, use either
                merged_text.append(ocr_text[i1:i2])
            elif tag == 'replace':
                # Conflict: prefer LLM
                merged_text.append(llm_text[j1:j2])
                differences.append(f"OCR: '{ocr_text[i1:i2]}' → LLM: '{llm_text[j1:j2]}'")
            elif tag == 'delete':
                # OCR has extra text: check if it's noise
                extra_text = ocr_text[i1:i2]
                if self._looks_like_noise(extra_text):
                    differences.append(f"Removed OCR noise: '{extra_text}'")
                    continue  # Skip it
                else:
                    merged_text.append(extra_text)  # Keep it
            elif tag == 'insert':
                # LLM has extra text: trust it
                merged_text.append(llm_text[j1:j2])
                differences.append(f"Added LLM text: '{llm_text[j1:j2]}'")
        
        return ''.join(merged_text), differences
    
    def _looks_like_noise(self, text: str) -> bool:
        """Determine if text looks like OCR noise"""
        if not text.strip():
            return True
        
        # Check for excessive unusual characters
        unusual_chars = re.findall(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\{\}\"\'\/\\]', text)
        if len(unusual_chars) > len(text) * 0.3:  # More than 30% unusual chars
            return True
        
        # Check for very long words (likely OCR errors)
        words = text.split()
        for word in words:
            if len(word) > 20:
                return True
        
        # Check for single character words
        single_chars = [word for word in words if len(word) == 1]
        if len(single_chars) > len(words) * 0.5:  # More than 50% single chars
            return True
        
        return False
    
    def _calculate_hybrid_confidence(self, ocr_result: ExtractionResult, llm_result: ExtractionResult) -> float:
        """Calculate confidence for hybrid result"""
        # Weight LLM confidence more heavily
        weights = {
            'ocr': 0.3,
            'llm': 0.7
        }
        
        hybrid_confidence = (
            ocr_result.confidence * weights['ocr'] +
            llm_result.confidence * weights['llm']
        )
        
        return min(1.0, hybrid_confidence)
