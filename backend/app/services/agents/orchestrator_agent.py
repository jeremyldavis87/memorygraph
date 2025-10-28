"""
Orchestrator Agent

Central coordinator that manages all specialized agents and generates
comprehensive JSON output matching the PRD schema. Handles both single
and multi-note processing with graceful error handling.
"""

import asyncio
import os
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    import braintrust
    BRAINTRUST_AVAILABLE = True
except ImportError:
    BRAINTRUST_AVAILABLE = False

from .base_agent import BaseAgent, PartialResult
from .image_processing_agent import ImageProcessingAgent
from .separation_agent import SeparationAgent, NoteRegion
from .extraction_agent import ExtractionAgent, HybridResult
from .structure_agent import StructureRecognitionAgent, DocumentStructure
from .metadata_agent import MetadataAgent
from .postprocess_agent import PostProcessAgent, CorrectionResult
from app.schemas.agent_schemas import ProcessingOutput, Note, ImageMetadata, Summary


class OrchestratorAgent(BaseAgent):
    """
    Central orchestrator that coordinates all specialized agents.
    
    Responsibilities:
    - Task planning and coordination
    - Agent selection and sequencing
    - Result aggregation and validation
    - Quality assessment and routing
    - Comprehensive JSON output generation
    - Error handling and graceful degradation
    """
    
    def __init__(self):
        super().__init__("OrchestratorAgent")
        
        # Initialize all sub-agents
        self.image_agent = ImageProcessingAgent()
        self.separation_agent = SeparationAgent()
        self.extraction_agent = ExtractionAgent()
        self.structure_agent = StructureRecognitionAgent()
        self.metadata_agent = MetadataAgent()
        self.postprocess_agent = PostProcessAgent()
    
    async def process(self, image_path: str, config: Dict[str, Any]) -> Union[ProcessingOutput, PartialResult]:
        """
        Main processing method for complete image analysis.
        
        Args:
            image_path: Path to the input image
            config: Configuration including user preferences
            
        Returns:
            ProcessingOutput with comprehensive results or PartialResult if processing fails
        """
        start_time = time.time()
        
        # Start Braintrust logging if enabled
        if self.braintrust_enabled and BRAINTRUST_AVAILABLE:
            try:
                import braintrust
                with braintrust.start_span(name="orchestrator_process", 
                                         inputs={"image_path": image_path, "config": config}) as span:
                    try:
                        result = await self._process_with_tracing(span, image_path, config, start_time)
                        span.update(output=result, exported=True)
                        return result
                    except Exception as e:
                        span.update(error=str(e), exported=True)
                        raise
            except Exception as e:
                self.logger.warning(f"Braintrust initialization failed, processing without tracing: {e}")
        
        # Process without Braintrust
        return await self._process_without_tracing(image_path, config, start_time)
    
    async def _process_with_tracing(self, span, image_path: str, config: Dict[str, Any], start_time: float) -> Union[ProcessingOutput, PartialResult]:
        """Process with Braintrust tracing enabled"""
        try:
            # Phase 1: Image preprocessing
            self.logger.info("Starting image preprocessing")
            image_result = await self.image_agent.process(image_path)
            
            if isinstance(image_result, PartialResult):
                braintrust.log(stage="image_preprocessing", status="failed", error=image_result.error)
                return self._create_error_result(image_path, "Image preprocessing failed", image_result.error)
            
            processed_path = image_result["processed_path"]
            color_info = image_result["color_info"]
            quality_metrics = image_result["quality_metrics"]
            
            braintrust.log(stage="image_preprocessing", status="success", quality=quality_metrics["overall_quality"])
            
            # Phase 2: Note separation
            self.logger.info("Starting note separation")
            separation_result = await self.separation_agent.process(image_path)
            
            if isinstance(separation_result, PartialResult):
                braintrust.log(stage="note_separation", status="failed", error=separation_result.error)
                return self._create_error_result(image_path, "Note separation failed", separation_result.error)
            
            note_regions = separation_result
            braintrust.log(stage="note_separation", status="success", regions_detected=len(note_regions))
            
            # Phase 3: Process each note region
            self.logger.info(f"Processing {len(note_regions)} note regions")
            processed_notes = []
            
            for i, region in enumerate(note_regions):
                try:
                    note_result = await self._process_single_note(
                        image_path, region, color_info, quality_metrics, config, i + 1
                    )
                    processed_notes.append(note_result)
                except Exception as e:
                    self.logger.error(f"Failed to process note region {i + 1}: {e}")
                    # Create error note
                    error_note = self._create_error_note(f"note_{i+1:03d}", str(e))
                    processed_notes.append(error_note)
            
            # Phase 4: Generate comprehensive output
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            braintrust.log(stage="comprehensive_output_generation", notes_count=len(processed_notes), processing_time_ms=processing_time_ms)
            
            comprehensive_output = self._generate_comprehensive_output(
                image_path, processed_notes, processing_time_ms, image_result
            )
            
            # Log final metrics
            self.log_metric("total_notes_processed", len(processed_notes))
            self.log_metric("processing_time_ms", processing_time_ms)
            self.log_metric("success_rate", len([n for n in processed_notes if n.get("success", True)]) / len(processed_notes))
            
            braintrust.log(
                total_notes_processed=len(processed_notes),
                average_confidence=sum(note.get("quality_metrics", {}).get("overall_confidence", 0) for note in processed_notes if note.get("success")) / len([n for n in processed_notes if n.get("success")]) if any(note.get("success") for note in processed_notes) else 0
            )
            
            return comprehensive_output
            
        except Exception as e:
            self.logger.error(f"Orchestrator processing failed: {e}")
            self.logger.exception("Full traceback:")
            
            # Even if ProcessingOutput validation fails, return the processed notes as raw data
            if isinstance(e, (ValueError, TypeError)) and "validation error" in str(e).lower():
                self.logger.warning("ProcessingOutput validation failed, returning raw notes data")
                return self.create_partial_result(
                    data={"notes": processed_notes, "raw_data": True},
                    error=f"Schema validation failed: {str(e)}",
                    warnings=["ProcessingOutput schema validation failed, using raw data format"]
                )
            
            return self._create_error_result(image_path, "Orchestrator processing failed", str(e))
    
    async def _process_without_tracing(self, image_path: str, config: Dict[str, Any], start_time: float) -> Union[ProcessingOutput, PartialResult]:
        """Process without Braintrust tracing (original implementation)"""
        try:
            # Phase 1: Image preprocessing
            self.logger.info("Starting image preprocessing")
            image_result = await self.image_agent.process(image_path)
            
            if isinstance(image_result, PartialResult):
                return self._create_error_result(image_path, "Image preprocessing failed", image_result.error)
            
            processed_path = image_result["processed_path"]
            color_info = image_result["color_info"]
            quality_metrics = image_result["quality_metrics"]
            
            # Phase 2: Note separation
            self.logger.info("Starting note separation")
            separation_result = await self.separation_agent.process(image_path)
            
            if isinstance(separation_result, PartialResult):
                return self._create_error_result(image_path, "Note separation failed", separation_result.error)
            
            note_regions = separation_result
            
            # Phase 3: Process each note region
            self.logger.info(f"Processing {len(note_regions)} note regions")
            processed_notes = []
            
            for i, region in enumerate(note_regions):
                try:
                    note_result = await self._process_single_note(
                        image_path, region, color_info, quality_metrics, config, i + 1
                    )
                    processed_notes.append(note_result)
                except Exception as e:
                    self.logger.error(f"Failed to process note region {i + 1}: {e}")
                    # Create error note
                    error_note = self._create_error_note(f"note_{i+1:03d}", str(e))
                    processed_notes.append(error_note)
            
            # Phase 4: Generate comprehensive output
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            comprehensive_output = self._generate_comprehensive_output(
                image_path, processed_notes, processing_time_ms, image_result
            )
            
            # Log final metrics
            self.log_metric("total_notes_processed", len(processed_notes))
            self.log_metric("processing_time_ms", processing_time_ms)
            self.log_metric("success_rate", len([n for n in processed_notes if n.get("success", True)]) / len(processed_notes))
            
            return comprehensive_output
            
        except Exception as e:
            self.logger.error(f"Orchestrator processing failed: {e}")
            self.logger.exception("Full traceback:")
            
            # Even if ProcessingOutput validation fails, return the processed notes as raw data
            if isinstance(e, (ValueError, TypeError)) and "validation error" in str(e).lower():
                self.logger.warning("ProcessingOutput validation failed, returning raw notes data")
                return self.create_partial_result(
                    data={"notes": processed_notes, "raw_data": True},
                    error=f"Schema validation failed: {str(e)}",
                    warnings=["ProcessingOutput schema validation failed, using raw data format"]
                )
            
            return self._create_error_result(image_path, "Orchestrator processing failed", str(e))
    
    async def _process_single_note(self, image_path: str, region: NoteRegion, 
                                 color_info: Dict[str, Any], quality_metrics: Dict[str, Any],
                                 config: Dict[str, Any], note_id: int) -> Dict[str, Any]:
        """Process a single note region through all agents"""
        note_start_time = time.time()
        
        # Phase 1: Text extraction
        extraction_result = await self.extraction_agent.process(image_path, region.bbox)
        
        if isinstance(extraction_result, PartialResult):
            return self._create_error_note(f"note_{note_id:03d}", extraction_result.error)
        
        # Phase 2: Structure recognition
        structure_result = await self.structure_agent.process(extraction_result.text)
        
        if isinstance(structure_result, PartialResult):
            return self._create_error_note(f"note_{note_id:03d}", structure_result.error)
        
        # Phase 3: Post-processing
        postprocess_result = await self.postprocess_agent.process(extraction_result.text)
        
        if isinstance(postprocess_result, PartialResult):
            return self._create_error_note(f"note_{note_id:03d}", postprocess_result.error)
        
        # Phase 4: Metadata extraction
        metadata_result = await self.metadata_agent.process(image_path, color_info)
        
        if isinstance(metadata_result, PartialResult):
            return self._create_error_note(f"note_{note_id:03d}", metadata_result.error)
        
        # Compile note result
        note_processing_time = int((time.time() - note_start_time) * 1000)
        
        return {
            "note_id": f"note_{note_id:03d}",
            "success": True,
            "spatial_position": {
                "bounding_box": {
                    "x": region.bbox[0],
                    "y": region.bbox[1],
                    "width": region.bbox[2],
                    "height": region.bbox[3]
                },
                "relative_position": self._determine_relative_position(region.bbox),
                "rotation_angle": 0.0  # Could be enhanced with actual rotation detection
            },
            "visual_metadata": color_info,
            "qr_codes": metadata_result["qr_codes"],
            "text_content": {
                "raw_text": extraction_result.text,
                "formatted_text": postprocess_result.text,
                "extraction_method": extraction_result.extraction_method,
                "confidence_score": extraction_result.confidence
            },
            "structure": {
                "title": {
                    "text": structure_result.title.text if structure_result.title else None,
                    "format": structure_result.title.format if structure_result.title else None,
                    "position": structure_result.title.position if structure_result.title else None
                } if structure_result.title else None,
                "sections": [
                    {
                        "type": section["type"],
                        "content": section.get("content"),
                        "items": section.get("items"),
                        "line_start": section.get("line_start"),
                        "line_end": section.get("line_end")
                    }
                    for section in structure_result.sections
                ],
                "has_title": structure_result.has_title,
                "has_lists": structure_result.has_lists,
                "has_todos": structure_result.has_todos,
                "has_tags": structure_result.has_tags
            },
            "tags": {
                "simple_tags": [tag.name for tag in structure_result.simple_tags],
                "key_value_tags": {tag.name: tag.value for tag in structure_result.key_value_tags}
            },
            "entities": {
                "dates": [],
                "numbers": [],
                "monetary_values": [],
                "people": [],
                "organizations": []
            },
            "quality_metrics": {
                "image_quality": quality_metrics["overall_quality"],
                "text_clarity": extraction_result.confidence,
                "ocr_confidence": extraction_result.confidence * 0.3,  # Estimate OCR portion
                "llm_confidence": extraction_result.confidence * 0.7,  # Estimate LLM portion
                "overall_confidence": extraction_result.confidence
            },
            "processing_details": {
                "preprocessing_applied": ["denoise", "contrast_enhancement", "deskew"],
                "ocr_engine": "tesseract",
                "llm_model": "gpt-4o-mini",
                "llm_tokens_used": 0,  # Could be tracked from AI service
                "post_processing_corrections": len(postprocess_result.corrections)
            },
            "processing_time_ms": note_processing_time
        }
    
    def _determine_relative_position(self, bbox: tuple) -> str:
        """Determine relative position of note in image"""
        # This is a simplified implementation
        # In practice, you'd analyze the bbox relative to image dimensions
        x, y, w, h = bbox
        
        # Simple heuristic based on position
        if y < 200:
            return "top"
        elif y > 400:
            return "bottom"
        else:
            return "middle"
    
    def _create_error_note(self, note_id: str, error_message: str) -> Dict[str, Any]:
        """Create an error note when processing fails"""
        return {
            "note_id": note_id,
            "success": False,
            "error": error_message,
            "text_content": {
                "raw_text": "",
                "formatted_text": "",
                "extraction_method": "error",
                "confidence_score": 0.0
            },
            "structure": {
                "title": None,
                "sections": [],
                "has_title": False,
                "has_lists": False,
                "has_todos": False,
                "has_tags": False
            },
            "tags": {
                "simple_tags": [],
                "key_value_tags": {}
            },
            "entities": {
                "dates": [],
                "numbers": [],
                "monetary_values": [],
                "people": [],
                "organizations": []
            },
            "quality_metrics": {
                "image_quality": 0.0,
                "text_clarity": 0.0,
                "ocr_confidence": 0.0,
                "llm_confidence": 0.0,
                "overall_confidence": 0.0
            },
            "processing_details": {
                "preprocessing_applied": [],
                "ocr_engine": "none",
                "llm_model": "none",
                "llm_tokens_used": 0,
                "post_processing_corrections": 0
            }
        }
    
    def _generate_comprehensive_output(self, image_path: str, processed_notes: List[Dict[str, Any]], 
                                     processing_time_ms: int, image_result: Dict[str, Any]) -> ProcessingOutput:
        """Generate comprehensive output matching PRD schema"""
        
        # Calculate summary statistics
        successful_notes = [note for note in processed_notes if note.get("success", True)]
        total_todos = sum(len(note.get("structure", {}).get("sections", [])) for note in successful_notes)
        total_tags = sum(len(note.get("tags", {}).get("simple_tags", [])) + 
                        len(note.get("tags", {}).get("key_value_tags", {})) for note in successful_notes)
        total_qr_codes = sum(len(note.get("qr_codes", [])) for note in successful_notes)
        
        avg_confidence = 0.0
        if successful_notes:
            avg_confidence = sum(note.get("quality_metrics", {}).get("overall_confidence", 0) 
                               for note in successful_notes) / len(successful_notes)
        
        # Get image metadata
        image_filename = os.path.basename(image_path)
        file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
        
        # Create comprehensive output
        return ProcessingOutput(
            version="2.0",
            processed_at=datetime.utcnow(),
            processing_time_ms=processing_time_ms,
            image_metadata=ImageMetadata(
                filename=image_filename,
                original_dimensions=image_result["original_dimensions"],
                file_size_bytes=file_size,
                format="JPEG",  # Could be detected from file extension
                color_space="RGB"
            ),
            notes=processed_notes,
            summary=Summary(
                total_notes=len(processed_notes),
                total_todos=total_todos,
                total_tags=total_tags,
                total_qr_codes=total_qr_codes,
                average_confidence=avg_confidence,
                processing_status="success" if successful_notes else "failed"
            ),
            errors=[],
            warnings=[]
        )
    
    def _create_error_result(self, image_path: str, error_type: str, error_message: str) -> PartialResult:
        """Create error result when processing fails completely"""
        return self.create_partial_result(
            data={
                "image_path": image_path,
                "error_type": error_type,
                "processing_status": "failed"
            },
            error=error_message,
            warnings=[f"Processing failed: {error_type}"]
        )
