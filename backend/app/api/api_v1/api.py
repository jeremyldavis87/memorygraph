from fastapi import APIRouter
from app.api.api_v1.endpoints import notes, categories, entities, auth, search, qr_codes

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(qr_codes.router, prefix="/qr-codes", tags=["qr-codes"])