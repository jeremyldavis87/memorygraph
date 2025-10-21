from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.models.note import Note
from app.models.entity import Entity
from app.schemas.note import NoteResponse
from app.schemas.entity import EntityResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/notes", response_model=List[NoteResponse])
def search_notes(
    q: str = Query(..., description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    entity_id: Optional[int] = Query(None, description="Filter by entity"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search notes using natural language query
    """
    query = db.query(Note).filter(Note.user_id == current_user.id)
    
    # Basic text search
    search_terms = q.lower().split()
    search_conditions = []
    
    for term in search_terms:
        search_conditions.append(
            or_(
                Note.title.ilike(f"%{term}%"),
                Note.content.ilike(f"%{term}%"),
                Note.original_text.ilike(f"%{term}%"),
                Note.summary.ilike(f"%{term}%")
            )
        )
    
    if search_conditions:
        query = query.filter(and_(*search_conditions))
    
    # Apply filters
    if category_id:
        query = query.filter(Note.category_id == category_id)
    
    if entity_id:
        # Search for notes that mention this entity
        query = query.join(Note.note_entities).filter(
            Note.note_entities.any(entity_id=entity_id)
        )
    
    notes = query.order_by(Note.created_at.desc()).limit(50).all()
    return notes

@router.get("/entities", response_model=List[EntityResponse])
def search_entities(
    q: str = Query(..., description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search entities using natural language query
    """
    query = db.query(Entity).filter(Entity.user_id == current_user.id)
    
    # Basic text search
    search_terms = q.lower().split()
    search_conditions = []
    
    for term in search_terms:
        search_conditions.append(
            or_(
                Entity.name.ilike(f"%{term}%"),
                Entity.description.ilike(f"%{term}%")
            )
        )
    
    if search_conditions:
        query = query.filter(and_(*search_conditions))
    
    # Apply filters
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    
    entities = query.order_by(Entity.mention_count.desc()).limit(50).all()
    return entities

@router.get("/suggestions")
def get_search_suggestions(
    q: str = Query(..., description="Partial search query"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    """
    suggestions = []
    
    # Get note title suggestions
    note_titles = db.query(Note.title).filter(
        Note.user_id == current_user.id,
        Note.title.ilike(f"%{q}%")
    ).limit(5).all()
    
    suggestions.extend([{"text": title[0], "type": "note_title"} for title in note_titles])
    
    # Get entity suggestions
    entities = db.query(Entity.name, Entity.entity_type).filter(
        Entity.user_id == current_user.id,
        Entity.name.ilike(f"%{q}%")
    ).limit(5).all()
    
    suggestions.extend([{"text": name, "type": f"entity_{entity_type}"} for name, entity_type in entities])
    
    return {"suggestions": suggestions}