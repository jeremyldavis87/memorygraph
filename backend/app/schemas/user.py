from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) > 72:
            raise ValueError('Password cannot be longer than 72 characters')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    default_ocr_mode: str
    auto_capture: bool
    ai_processing_enabled: bool
    vision_model_preference: str
    ocr_confidence_threshold: int
    multi_note_detection_enabled: bool
    
    class Config:
        from_attributes = True

class UserSettingsUpdate(BaseModel):
    vision_model_preference: Optional[str] = None
    ocr_confidence_threshold: Optional[int] = None
    multi_note_detection_enabled: Optional[bool] = None
    default_ocr_mode: Optional[str] = None
    auto_capture: Optional[bool] = None
    ai_processing_enabled: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None