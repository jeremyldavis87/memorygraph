from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Entity identification
    name = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False)  # person, organization, project, concept, location, etc.
    aliases = Column(JSON)  # Alternative names
    
    # Entity properties
    description = Column(Text)
    properties = Column(JSON)  # Type-specific properties
    
    # Metadata
    first_mentioned = Column(DateTime(timezone=True))
    last_mentioned = Column(DateTime(timezone=True))
    mention_count = Column(Integer, default=0)
    confidence = Column(Integer, default=100)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    note_entities = relationship("NoteEntity", back_populates="entity")
    relationships = relationship("EntityRelationship", foreign_keys="EntityRelationship.source_entity_id")

class EntityRelationship(Base):
    __tablename__ = "entity_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship definition
    source_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    target_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    relationship_type = Column(String, nullable=False)  # mentions, relates_to, depends_on, etc.
    
    # Relationship properties
    strength = Column(Integer, default=1)  # 1-10
    confidence = Column(Integer, default=100)  # 0-100
    properties = Column(JSON)  # Additional relationship data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    source_entity = relationship("Entity", foreign_keys=[source_entity_id])
    target_entity = relationship("Entity", foreign_keys=[target_entity_id])