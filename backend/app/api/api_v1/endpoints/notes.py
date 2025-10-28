from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime
import asyncio
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate, NoteListResponse
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.ocr_service import OCRService
from app.services.ai_service import AIService
from app.services.agent_service import NoteProcessingAgent
from app.services.graph_client import graph_client, Triple

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_note_for_graph(note_id: int, content: str, title: str, user_id: int):
    """
    Background task to process note for knowledge graph.
    """
    try:
        # Extract triples from note content
        extraction_result = await graph_client.extract_triples(
            content=content,
            title=title,
            source_type="rocketbook",
            user_id=user_id
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
            await graph_client.bulk_insert_triples(
                triples=triples,
                note_id=note_id,
                user_id=user_id
            )
            
    except Exception as e:
        print(f"Graph processing failed for note {note_id}: {str(e)}")

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
    
    # Queue graph processing as background task
    if note.content:
        background_tasks.add_task(
            process_note_for_graph,
            note_id=db_note.id,
            content=note.content,
            title=note.title,
            user_id=current_user.id
        )
    
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
async def upload_note(
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
    
    # Check if file is an image
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    is_image = file_extension.lower() in image_extensions
    
    # Process with OCR or agent for images
    if is_image:
        # Check if multi-note detection is enabled for user
        if current_user.multi_note_detection_enabled:
            # Use new agent architecture for multi-note processing
            agent = NoteProcessingAgent(current_user.vision_model_preference)
            config = {
                "ocr_confidence_threshold": current_user.ocr_confidence_threshold,
                "vision_model_preference": current_user.vision_model_preference,
                "source_type": "rocketbook"  # Indicate this is a Rocketbook for special processing
            }
            
            # Process with orchestrator agent
            processing_result = await agent.process_multi_note_image(file_path, config)
            
            # Log processing result for debugging
            logger.info(f"Processing result type: {type(processing_result)}")
            logger.info(f"Processing result attributes: {dir(processing_result)}")
            if hasattr(processing_result, '__dict__'):
                logger.info(f"Processing result dict keys: {processing_result.__dict__.keys()}")
            
            # Handle comprehensive JSON response
            # Check if we have a ProcessingOutput object or PartialResult
            if hasattr(processing_result, 'notes'):
                # Success case - ProcessingOutput object
                notes_data = processing_result.notes if isinstance(processing_result.notes, list) else [processing_result.notes]
                comprehensive_output = processing_result.model_dump() if hasattr(processing_result, 'model_dump') else {}
            elif hasattr(processing_result, 'data') and processing_result.data:
                # PartialResult with raw data
                logger.warning("Handling PartialResult with raw notes data")
                notes_data = processing_result.data.get("notes", [])
                comprehensive_output = processing_result.data
            else:
                notes_data = []
            
            # Create multiple notes from comprehensive results
            if notes_data:
                created_notes = []
                parent_note_id = None
                
                for note_data in notes_data:
                    # Convert Pydantic model to dict if needed
                    if hasattr(note_data, 'model_dump'):
                        note_dict = note_data.model_dump()
                    elif isinstance(note_data, dict):
                        note_dict = note_data
                    else:
                        logger.warning(f"Skipping note_data with unknown type: {type(note_data)}")
                        continue
                    
                    if not note_dict.get("success", True) if "success" in note_dict else True:
                        logger.info(f"Skipping note with success=False")
                        continue
                    
                    # Extract data from comprehensive structure
                    text_content = note_dict.get("text_content", {})
                    structure = note_dict.get("structure", {})
                    tags = note_dict.get("tags", {})
                    qr_codes = note_dict.get("qr_codes", [])
                    
                    # Check for QR code mapping
                    final_category_id = category_id
                    qr_code = None
                    if qr_codes:
                        qr_code = qr_codes[0].get("data") if qr_codes else None
                    
                    if qr_code:
                        from app.models.category import QRCode
                        qr_mapping = db.query(QRCode).filter(
                            QRCode.code == qr_code,
                            QRCode.user_id == current_user.id
                        ).first()
                        
                        if qr_mapping:
                            final_category_id = qr_mapping.category_id
                    
                    # Prepare content for hybrid storage
                    full_content = text_content.get("formatted_text", "")
                    full_original_text = text_content.get("raw_text", "")
                    content_preview = full_content[:1000] if full_content else ""
                    original_text_preview = full_original_text[:1000] if full_original_text else ""
                    
                    # Extract title from structure
                    title_data = structure.get("title")
                    title = title_data.get("text") if title_data else f"Note {len(created_notes) + 1}"
                    
                    # Create note
                    note = Note(
                        user_id=current_user.id,
                        title=title,
                        content=content_preview,
                        original_text=original_text_preview,
                        content_preview=content_preview,
                        has_full_content_in_graph=True,
                        source_type="rocketbook",
                        category_id=final_category_id,
                        file_path=file_path,
                        image_path=file_path,
                        ocr_mode=ocr_mode,
                        ocr_confidence=int(text_content.get("confidence_score", 0) * 100),
                        processing_status="completed",
                        parent_note_id=parent_note_id,
                        note_position=note_dict.get("note_id", len(created_notes) + 1),
                        detection_method="orchestrator_agent",
                        note_metadata_json={
                            "comprehensive_output": comprehensive_output,
                            "note_data": note_dict,
                            "qr_code": qr_code,
                            "qr_code_mapped": qr_code is not None and final_category_id != category_id,
                            "full_content": full_content,
                            "full_original_text": full_original_text,
                            "processing_method": text_content.get("extraction_method", "unknown"),
                            "agent_processed": True,
                            "structure": structure,
                            "tags": tags,
                            "quality_metrics": note_dict.get("quality_metrics", {})
                        }
                    )
                    
                    db.add(note)
                    db.commit()
                    db.refresh(note)
                    
                    # Set parent_note_id for subsequent notes
                    if parent_note_id is None:
                        parent_note_id = note.id
                    
                    # Process with AI if enabled
                    if current_user.ai_processing_enabled:
                        ai_service = AIService()
                        ai_result = ai_service.process_note(note)
                        
                        # Update note with AI results
                        note.summary = ai_result.get("summary")
                        note.entities = ai_result.get("entities")
                        note.action_items = ai_result.get("action_items")
                        note.tags = ai_result.get("tags")
                        note.note_metadata_json.update(ai_result.get("note_metadata_json", {}))
                        
                        db.commit()
                        db.refresh(note)
                    
                    created_notes.append(note)
                
                # Return the first note (parent) with information about total count
                if created_notes:
                    parent_note = created_notes[0]
                    parent_note.note_metadata_json["total_notes_created"] = len(created_notes)
                    parent_note.note_metadata_json["child_note_ids"] = [note.id for note in created_notes[1:]]
                    db.commit()
                    db.refresh(parent_note)
                    return parent_note
                else:
                    # Fallback to single note processing if agent failed
                    ocr_service = OCRService()
                    ocr_result = ocr_service.process_image(file_path, mode=ocr_mode)
                    
                    # Process single note with traditional OCR
                    return _create_single_note_from_ocr(
                        ocr_result, file_path, category_id, current_user, db, ocr_mode
                    )
            else:
                # Error case - fallback to traditional OCR
                ocr_service = OCRService()
                ocr_result = ocr_service.process_image(file_path, mode=ocr_mode)
                
                # Process single note with traditional OCR
                return _create_single_note_from_ocr(
                    ocr_result, file_path, category_id, current_user, db, ocr_mode
                )
        else:
            # Use traditional OCR processing
            ocr_service = OCRService()
            ocr_result = ocr_service.process_image(file_path, mode=ocr_mode)
            
            # Process single note with traditional OCR
            return _create_single_note_from_ocr(
                ocr_result, file_path, category_id, current_user, db, ocr_mode
            )
    else:
        # For non-image files, read as text
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                text_content = f.read()
        
        # Create a simple OCR result for text files
        ocr_result = {
            "original_text": text_content.strip(),
            "content": text_content.strip(),
            "title": os.path.splitext(file.filename)[0] if file.filename else "Untitled",
            "sections": [],
            "qr_code": None,
            "confidence": 100,  # Assume perfect for text files
            "tags": [],
            "action_items": []
        }
        
        # Process single note with text content
        return _create_single_note_from_ocr(
            ocr_result, file_path, category_id, current_user, db, ocr_mode
        )

def _create_single_note_from_ocr(ocr_result, file_path, category_id, current_user, db, ocr_mode):
    """
    Helper function to create a single note from OCR results.
    """
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
    
    # Prepare content for hybrid storage
    full_content = ocr_result.get("content", "")
    full_original_text = ocr_result.get("original_text", "")
    content_preview = full_content[:1000] if full_content else ""
    original_text_preview = full_original_text[:1000] if full_original_text else ""
    
    # Create note
    note = Note(
        user_id=current_user.id,
        title=ocr_result.get("title", "Untitled"),
        content=content_preview,  # Store preview in PostgreSQL
        original_text=original_text_preview,  # Store preview in PostgreSQL
        content_preview=content_preview,
        has_full_content_in_graph=True,  # Full content will be stored in Neo4j
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
            "qr_code_mapped": qr_code is not None and final_category_id != category_id,
            "full_content": full_content,  # Store full content in metadata for now
            "full_original_text": full_original_text
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
        note.note_metadata_json.update(ai_result.get("note_metadata_json", {}))
        
        db.commit()
        db.refresh(note)
    
    return note

@router.post("/{note_id}/extract-graph")
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