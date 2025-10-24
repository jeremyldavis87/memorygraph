from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.category import Category, QRCode
from app.schemas.category import CategoryResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/map")
def map_qr_code_to_category(
    qr_code: str,
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Map a QR code to a category for the current user
    """
    # Verify category belongs to user
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if QR code mapping already exists
    existing_mapping = db.query(QRCode).filter(
        QRCode.code == qr_code,
        QRCode.user_id == current_user.id
    ).first()
    
    if existing_mapping:
        # Update existing mapping
        existing_mapping.category_id = category_id
        existing_mapping.updated_at = datetime.utcnow()
    else:
        # Create new mapping
        new_mapping = QRCode(
            code=qr_code,
            category_id=category_id,
            user_id=current_user.id
        )
        db.add(new_mapping)
    
    db.commit()
    
    return {
        "message": "QR code mapped successfully",
        "qr_code": qr_code,
        "category_id": category_id,
        "category_name": category.name
    }

@router.get("/", response_model=List[dict])
def get_qr_code_mappings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all QR code mappings for the current user
    """
    mappings = db.query(QRCode, Category).join(
        Category, QRCode.category_id == Category.id
    ).filter(QRCode.user_id == current_user.id).all()
    
    return [
        {
            "qr_code": mapping.QRCode.code,
            "category_id": mapping.QRCode.category_id,
            "category_name": mapping.Category.name,
            "created_at": mapping.QRCode.created_at,
            "updated_at": mapping.QRCode.updated_at
        }
        for mapping in mappings
    ]

@router.get("/unmapped")
def get_unmapped_qr_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get QR codes that have been detected but not yet mapped
    This would typically query recent notes with QR codes that don't have mappings
    """
    # For now, return empty list - this would be implemented based on note history
    # In a real implementation, you'd query notes with QR codes that don't have mappings
    return []

@router.delete("/{qr_code}")
def remove_qr_code_mapping(
    qr_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a QR code mapping
    """
    mapping = db.query(QRCode).filter(
        QRCode.code == qr_code,
        QRCode.user_id == current_user.id
    ).first()
    
    if not mapping:
        raise HTTPException(status_code=404, detail="QR code mapping not found")
    
    db.delete(mapping)
    db.commit()
    
    return {"message": "QR code mapping removed successfully"}

@router.get("/detect/{qr_code}")
def detect_qr_code_category(
    qr_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a QR code has an existing mapping and return the category
    """
    mapping = db.query(QRCode, Category).join(
        Category, QRCode.category_id == Category.id
    ).filter(
        QRCode.code == qr_code,
        QRCode.user_id == current_user.id
    ).first()
    
    if mapping:
        return {
            "qr_code": qr_code,
            "category_id": mapping.QRCode.category_id,
            "category_name": mapping.Category.name,
            "mapped": True
        }
    else:
        return {
            "qr_code": qr_code,
            "mapped": False
        }
