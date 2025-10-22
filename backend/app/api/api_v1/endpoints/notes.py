from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate, NoteListResponse
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.ocr_service import OCRService
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/", response_model=NoteResponse)
def create_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_note = Note(
        user_id=current_user.id,
        title=note.title,
        content=note.content,
        original_text=note.original_text,
        source_type=note.source_type,
        category_id=note.category_id,
        file_path=note.file_path,
        image_path=note.image_path,
        ocr_mode=note.ocr_mode,
        processing_status="pending"
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/", response_model=NoteListResponse)
def get_notes(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Note).filter(Note.user_id == current_user.id)
    
    if category_id:
        query = query.filter(Note.category_id == category_id)
    
    if search:
        query = query.filter(
            Note.title.contains(search) | 
            Note.content.contains(search) |
            Note.original_text.contains(search)
        )
    
    total = query.count()
    notes = query.offset(skip).limit(limit).all()
    
    return NoteListResponse(
        notes=notes,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    for field, value in note_update.dict(exclude_unset=True).items():
        setattr(note, field, value)
    
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Delete associated files
    if note.file_path and os.path.exists(note.file_path):
        os.remove(note.file_path)
    if note.image_path and os.path.exists(note.image_path):
        os.remove(note.image_path)
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}

@router.post("/upload", response_model=NoteResponse)
def upload_note(
    file: UploadFile = File(...),
    category_id: Optional[int] = Form(None),
    ocr_mode: str = Form("traditional"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads", unique_filename)
    
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    # Process with OCR
    ocr_service = OCRService()
    ocr_result = ocr_service.process_image(file_path, mode=ocr_mode)
    
    # Create note
    note = Note(
        user_id=current_user.id,
        title=ocr_result.get("title", "Untitled"),
        content=ocr_result.get("content", ""),
        original_text=ocr_result.get("original_text", ""),
        source_type="rocketbook",
        category_id=category_id,
        file_path=file_path,
        image_path=file_path,
        ocr_mode=ocr_mode,
        ocr_confidence=ocr_result.get("confidence", 0),
        processing_status="completed"
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    # Process with AI if enabled
    if current_user.ai_processing_enabled:
        ai_service = AIService()
        ai_result = ai_service.process_note(note)
        
        # Update note with AI results
        note.summary = ai_result.get("summary")
        note.entities = ai_result.get("entities")
        note.action_items = ai_result.get("action_items")
        note.tags = ai_result.get("tags")
        note.note_metadata_json = ai_result.get("note_metadata_json")
        
        db.commit()
        db.refresh(note)
    
    return note