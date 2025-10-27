from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Content
    title = Column(String, nullable=False)
    content = Column(Text)
    original_text = Column(Text)  # Raw OCR text
    summary = Column(Text)  # AI-generated summary
    content_preview = Column(Text)  # First 1000 characters for quick access
    has_full_content_in_graph = Column(Boolean, default=False)  # Flag indicating full content is in Neo4j
    
    # Metadata
    source_type = Column(String, default="rocketbook")  # rocketbook, audio, video, document, etc.
    file_path = Column(String)  # Path to original file
    image_path = Column(String)  # Path to processed image
    
    # Processing
    ocr_mode = Column(String, default="traditional")
    ocr_confidence = Column(Integer)  # 0-100
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Multi-note detection
    parent_note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)  # For notes extracted from multi-note images
    note_position = Column(Integer, nullable=True)  # Position in multi-note image
    detection_method = Column(String, nullable=True)  # qr_code, contour, vision_llm
    
    # AI Analysis
    entities = Column(JSON)  # Extracted entities
    action_items = Column(JSON)  # Extracted action items
    tags = Column(JSON)  # Extracted tags
    note_metadata_json = Column(JSON)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    captured_at = Column(DateTime(timezone=True))  # When the note was originally captured
    
    # Relationships
    user = relationship("User", back_populates="notes")
    category = relationship("Category", back_populates="notes")
    note_tags = relationship("NoteTag", back_populates="note")
    note_entities = relationship("NoteEntity", back_populates="note")

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    tag_name = Column(String, nullable=False)
    tag_type = Column(String, default="simple")  # simple or key_value
    tag_value = Column(String)  # For key:value pairs
    
    # Relationships
    note = relationship("Note", back_populates="note_tags")

class NoteEntity(Base):
    __tablename__ = "note_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    mention_text = Column(String)  # How the entity was mentioned
    confidence = Column(Integer)  # 0-100
    
    # Relationships
    note = relationship("Note", back_populates="note_entities")
    entity = relationship("Entity", back_populates="note_entities")