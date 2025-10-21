from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    qr_code: Optional[str] = None
    default_tags: Optional[List[Dict[str, Any]]] = None
    processing_rules: Optional[Dict[str, Any]] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    qr_code: Optional[str] = None
    default_tags: Optional[List[Dict[str, Any]]] = None
    processing_rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True