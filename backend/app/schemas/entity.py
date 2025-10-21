from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class EntityBase(BaseModel):
    name: str
    entity_type: str
    description: Optional[str] = None
    aliases: Optional[List[str]] = None
    properties: Optional[Dict[str, Any]] = None

class EntityResponse(EntityBase):
    id: int
    user_id: int
    first_mentioned: Optional[datetime]
    last_mentioned: Optional[datetime]
    mention_count: int
    confidence: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EntityRelationshipResponse(BaseModel):
    id: int
    user_id: int
    source_entity_id: int
    target_entity_id: int
    relationship_type: str
    strength: int
    confidence: int
    properties: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True