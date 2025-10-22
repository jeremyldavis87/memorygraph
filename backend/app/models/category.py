from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Category definition
    name = Column(String, nullable=False)
    description = Column(Text)
    color = Column(String)  # Hex color code
    icon = Column(String)  # Icon identifier
    
    # QR Code mapping
    qr_code = Column(String, unique=True)  # QR code identifier
    
    # Settings
    default_tags = Column(JSON)  # Default tags for this category
    processing_rules = Column(JSON)  # Custom processing rules
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    notes = relationship("Note", back_populates="category")

class QRCode(Base):
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # QR Code definition
    code = Column(String, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Settings
    auto_capture = Column(Boolean, default=True)
    processing_rules = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    category = relationship("Category")