from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.models.entity import Entity, EntityRelationship
from app.schemas.entity import EntityResponse, EntityRelationshipResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[EntityResponse])
def get_entities(
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Entity).filter(Entity.user_id == current_user.id)
    
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    
    if search:
        query = query.filter(Entity.name.contains(search))
    
    entities = query.order_by(Entity.mention_count.desc()).all()
    return entities

@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(
    entity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entity = db.query(Entity).filter(
        Entity.id == entity_id,
        Entity.user_id == current_user.id
    ).first()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return entity

@router.get("/{entity_id}/relationships", response_model=List[EntityRelationshipResponse])
def get_entity_relationships(
    entity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    relationships = db.query(EntityRelationship).filter(
        EntityRelationship.user_id == current_user.id,
        (EntityRelationship.source_entity_id == entity_id) | 
        (EntityRelationship.target_entity_id == entity_id)
    ).all()
    
    return relationships

@router.delete("/{entity_id}")
def delete_entity(
    entity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entity = db.query(Entity).filter(
        Entity.id == entity_id,
        Entity.user_id == current_user.id
    ).first()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Delete relationships
    db.query(EntityRelationship).filter(
        (EntityRelationship.source_entity_id == entity_id) |
        (EntityRelationship.target_entity_id == entity_id)
    ).delete()
    
    db.delete(entity)
    db.commit()
    return {"message": "Entity deleted successfully"}