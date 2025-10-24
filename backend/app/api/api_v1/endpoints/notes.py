from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime
import asyncio

from app.core.database import get_db
from app.models.user import User
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate, NoteListResponse
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.ocr_service import OCRService
from app.services.ai_service import AIService
# Temporarily disabled for CI/CD compatibility
# from app.services.graph_client import graph_client, Triple

router = APIRouter()

# Temporarily disabled for CI/CD compatibility
# async def process_note_for_graph(note_id: int, content: str, title: str, user_id: int):
#     """
#     Background task to process note for knowledge graph.
#     """
#     try:
#         # Extract triples from note content
#         extraction_result = await graph_client.extract_triples(
#             content=content,
#             title=title,
#             source_type="rocketbook",
#             user_id=user_id
#         )
#         
#         # Convert to Triple objects
#         triples = [
#             Triple(
#                 subject=triple["subject"],
#                 predicate=triple["predicate"],
#                 object=triple["object"],
#                 confidence=triple["confidence"],
#                 entity_type=triple["entity_type"],
#                 relationship_type=triple["relationship_type"],
#                 properties=triple.get("properties", {})
#             )
#             for triple in extraction_result.triples
#         ]
#         
#         # Insert triples into graph
#         if triples:
#             await graph_client.bulk_insert_triples(
#                 triples=triples,
#                 note_id=note_id,
#                 user_id=user_id
#             )
#             
#     except Exception as e:
#         print(f"Graph processing failed for note {note_id}: {str(e)}")

@router.post("/", response_model=NoteResponse)
def create_note(
    note: NoteCreate,
    background_tasks: BackgroundTasks,
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
    
    # Temporarily disabled for CI/CD compatibility
    # # Queue graph processing as background task
    # if note.content:
    #     background_tasks.add_task(
    #         process_note_for_graph,
    #         note_id=db_note.id,
    #         content=note.content,
    #         title=note.title,
    #         user_id=current_user.id
    #     )
    
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
    
    # Check for QR code mapping
    final_category_id = category_id
    qr_code = ocr_result.get("qr_code")
    
    if qr_code:
        # Check if QR code has a mapping
        from app.models.category import QRCode
        qr_mapping = db.query(QRCode).filter(
            QRCode.code == qr_code,
            QRCode.user_id == current_user.id
        ).first()
        
        if qr_mapping:
            final_category_id = qr_mapping.category_id
    
    # Create note
    note = Note(
        user_id=current_user.id,
        title=ocr_result.get("title", "Untitled"),
        content=ocr_result.get("content", ""),
        original_text=ocr_result.get("original_text", ""),
        source_type="rocketbook",
        category_id=final_category_id,
        file_path=file_path,
        image_path=file_path,
        ocr_mode=ocr_mode,
        ocr_confidence=ocr_result.get("confidence", 0),
        processing_status="completed",
        note_metadata_json={
            "sections": ocr_result.get("sections", []),
            "qr_code": qr_code,
            "qr_code_mapped": qr_code is not None and final_category_id != category_id
        }
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

# Temporarily disabled for CI/CD compatibility
# @router.post("/{note_id}/extract-graph")
async def extract_graph_from_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger graph extraction for a specific note.
    """
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if not note.content:
        raise HTTPException(status_code=400, detail="Note has no content to process")
    
    try:
        # Extract triples from note content
        extraction_result = await graph_client.extract_triples(
            content=note.content,
            title=note.title,
            source_type=note.source_type,
            user_id=current_user.id
        )
        
        # Convert to Triple objects
        triples = [
            Triple(
                subject=triple["subject"],
                predicate=triple["predicate"],
                object=triple["object"],
                confidence=triple["confidence"],
                entity_type=triple["entity_type"],
                relationship_type=triple["relationship_type"],
                properties=triple.get("properties", {})
            )
            for triple in extraction_result.triples
        ]
        
        # Insert triples into graph
        if triples:
            insert_result = await graph_client.bulk_insert_triples(
                triples=triples,
                note_id=note_id,
                user_id=current_user.id
            )
            
            return {
                "message": "Graph extraction completed",
                "triples_extracted": len(triples),
                "triples_inserted": insert_result.inserted_count,
                "processing_time": extraction_result.processing_time,
                "model_used": extraction_result.model_used
            }
        else:
            return {
                "message": "No triples extracted from note",
                "triples_extracted": 0,
                "triples_inserted": 0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph extraction failed: {str(e)}")

# @router.get("/{note_id}/graph-context")
async def get_note_graph_context(
    note_id: int,
    max_depth: int = 2,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get graph context for a specific note.
    """
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    try:
        context_result = await graph_client.get_graph_context(
            note_id=note_id,
            max_depth=max_depth,
            limit=limit,
            user_id=current_user.id
        )
        
        return {
            "note_id": note_id,
            "note_title": note.title,
            "context": context_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph context retrieval failed: {str(e)}")

# @router.get("/graph/stats")
async def get_graph_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get knowledge graph statistics for the current user.
    """
    try:
        stats = await graph_client.get_graph_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph stats retrieval failed: {str(e)}")

# @router.get("/graph/health")
async def get_graph_health():
    """
    Check the health of all graph services.
    """
    try:
        health_status = await graph_client.health_check()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")