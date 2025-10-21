from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    source_type: str = "rocketbook"
    category_id: Optional[int] = None

class NoteCreate(NoteBase):
    original_text: Optional[str] = None
    ocr_mode: str = "traditional"
    file_path: Optional[str] = None
    image_path: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    action_items: Optional[List[Dict[str, Any]]] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    original_text: Optional[str]
    summary: Optional[str]
    file_path: Optional[str]
    image_path: Optional[str]
    ocr_mode: str
    ocr_confidence: Optional[int]
    processing_status: str
    entities: Optional[List[Dict[str, Any]]]
    action_items: Optional[List[Dict[str, Any]]]
    tags: Optional[List[Dict[str, Any]]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    captured_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class NoteListResponse(BaseModel):
    notes: List[NoteResponse]
    total: int
    page: int
    size: int