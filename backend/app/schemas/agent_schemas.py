"""
Agent Response Schemas

Pydantic models for agent responses matching the PRD JSON schema.
Includes both comprehensive and simplified versions for different use cases.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from app.core.config import settings


class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x: int
    y: int
    width: int
    height: int


class SpatialPosition(BaseModel):
    """Spatial position information"""
    bounding_box: BoundingBox
    relative_position: str
    rotation_angle: float


class RGBColor(BaseModel):
    """RGB color information"""
    rgb: List[int]
    hex: str
    name: str


class VisualMetadata(BaseModel):
    """Visual metadata for notes"""
    dominant_color: RGBColor
    background_color: RGBColor
    estimated_note_type: str
    physical_size_estimate: Optional[str] = None


class QRCode(BaseModel):
    """QR code information"""
    data: str
    type: str
    position: Dict[str, int]
    confidence: float


class TextContent(BaseModel):
    """Text content information"""
    raw_text: str
    formatted_text: str
    extraction_method: str
    confidence_score: float


class Title(BaseModel):
    """Title information"""
    text: str
    format: str
    position: Optional[int] = None


class TodoItem(BaseModel):
    """Todo item information"""
    text: str
    completed: bool
    line: int


class Section(BaseModel):
    """Document section information"""
    type: str
    content: Optional[str] = None
    items: Optional[List] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None


class Structure(BaseModel):
    """Document structure information"""
    title: Optional[Title] = None
    sections: List[Section] = []
    has_title: bool = False
    has_lists: bool = False
    has_todos: bool = False
    has_tags: bool = False


class Tags(BaseModel):
    """Tags information"""
    simple_tags: List[str] = []
    key_value_tags: Dict[str, str] = {}


class Entities(BaseModel):
    """Extracted entities"""
    dates: List[str] = []
    numbers: List[str] = []
    monetary_values: List[str] = []
    people: List[str] = []
    organizations: List[str] = []


class QualityMetrics(BaseModel):
    """Quality metrics"""
    image_quality: float
    text_clarity: float
    ocr_confidence: float
    llm_confidence: float
    overall_confidence: float


class ProcessingDetails(BaseModel):
    """Processing details"""
    preprocessing_applied: List[str] = []
    ocr_engine: str = "llm"
    llm_model: str = Field(default_factory=lambda: settings.AGENT_VISION_MODEL)
    llm_tokens_used: int = 0
    post_processing_corrections: int = 0


class Note(BaseModel):
    """Individual note with comprehensive metadata"""
    note_id: str
    spatial_position: Optional[SpatialPosition] = None
    visual_metadata: Optional[VisualMetadata] = None
    qr_codes: List[QRCode] = []
    text_content: Optional[TextContent] = None
    structure: Optional[Structure] = None
    tags: Optional[Tags] = None
    entities: Optional[Entities] = None
    quality_metrics: Optional[QualityMetrics] = None
    processing_details: Optional[ProcessingDetails] = None


class ImageMetadata(BaseModel):
    """Image metadata"""
    filename: str
    original_dimensions: Dict[str, int]
    file_size_bytes: int
    format: str
    color_space: str


class Summary(BaseModel):
    """Processing summary"""
    total_notes: int
    total_todos: int
    total_tags: int
    total_qr_codes: int
    average_confidence: float
    processing_status: str


class ProcessingOutput(BaseModel):
    """Comprehensive processing output matching PRD schema"""
    version: str = "2.0"
    processed_at: datetime
    processing_time_ms: int
    image_metadata: ImageMetadata
    notes: List[Note]
    summary: Summary
    errors: List[str] = []
    warnings: List[str] = []


# Simplified schemas for database storage
class SimplifiedNote(BaseModel):
    """Simplified note for database storage"""
    title: str
    content: str
    original_text: str
    summary: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    action_items: Optional[List[Dict[str, Any]]] = None
    note_metadata_json: Optional[Dict[str, Any]] = None
    qr_code: Optional[str] = None
    category_id: Optional[int] = None
    processing_status: str = "completed"
    ocr_confidence: Optional[int] = None


class AgentResponse(BaseModel):
    """Standard agent response wrapper"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: List[str] = []
    processing_time_ms: Optional[int] = None
    agent_name: str


# Agent-specific result containers
class ImageProcessingResult(BaseModel):
    """Image processing agent result"""
    original_path: str
    processed_path: str
    original_dimensions: Dict[str, int]
    quality_metrics: Dict[str, float]
    color_info: Dict[str, Any]
    processing_applied: List[str]


class SeparationResult(BaseModel):
    """Separation agent result"""
    note_regions: List[Dict[str, Any]]
    detection_method: str
    confidence: float
    total_regions: int


class ExtractionResult(BaseModel):
    """Extraction agent result"""
    text: str
    confidence: float
    ocr_version: str
    llm_version: str
    differences: List[str]
    extraction_method: str


class StructureResult(BaseModel):
    """Structure recognition agent result"""
    title: Optional[Dict[str, Any]] = None
    sections: List[Dict[str, Any]] = []
    bulleted_lists: List[List[Dict[str, Any]]] = []
    numbered_lists: List[List[Dict[str, Any]]] = []
    todos: List[Dict[str, Any]] = []
    simple_tags: List[Dict[str, Any]] = []
    key_value_tags: List[Dict[str, Any]] = []
    has_title: bool = False
    has_lists: bool = False
    has_todos: bool = False
    has_tags: bool = False


class MetadataResult(BaseModel):
    """Metadata agent result"""
    qr_codes: List[Dict[str, Any]] = []
    color_analysis: Dict[str, Any]
    exif_metadata: Optional[Dict[str, Any]] = None
    color_qr_associations: List[Dict[str, Any]] = []
    image_properties: Dict[str, Any]


class PostProcessResult(BaseModel):
    """Post-processing agent result"""
    corrected_text: str
    corrections: List[Dict[str, Any]] = []
    original_text: str
    confidence: float
    formatted_text: str
