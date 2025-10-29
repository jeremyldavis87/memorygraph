"""
Tracing script for note upload process
Tests the full flow with detailed logging
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv('.env.development')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.services.agent_service import NoteProcessingAgent
from app.core.config import settings

async def test_note_upload():
    """Test the full note upload and processing flow"""
    
    # Test image path
    image_path = "backend/tests/test-files/26372.jpg"
    
    if not os.path.exists(image_path):
        logger.error(f"Test image not found: {image_path}")
        return
    
    logger.info("=" * 80)
    logger.info("STARTING NOTE UPLOAD TRACE")
    logger.info("=" * 80)
    
    logger.info(f"Test image: {image_path}")
    logger.info(f"Image exists: {os.path.exists(image_path)}")
    logger.info(f"Image size: {os.path.getsize(image_path)} bytes")
    
    # Check configuration
    logger.info("\n" + "=" * 80)
    logger.info("CONFIGURATION CHECK")
    logger.info("=" * 80)
    logger.info(f"AGENT_VISION_MODEL: {settings.AGENT_VISION_MODEL}")
    logger.info(f"OCR_MODE: {settings.OCR_MODE}")
    logger.info(f"OPENAI_API_KEY configured: {bool(settings.OPENAI_API_KEY)}")
    if settings.OPENAI_API_KEY:
        logger.info(f"OPENAI_API_KEY (first 20 chars): {settings.OPENAI_API_KEY[:20]}...")
    
    # Initialize agent
    logger.info("\n" + "=" * 80)
    logger.info("INITIALIZING AGENT")
    logger.info("=" * 80)
    agent = NoteProcessingAgent()
    logger.info(f"Agent model_name: {agent.model_name}")
    
    # Configuration
    config = {
        "ocr_mode": "llm",  # Force LLM only
        "vision_model_preference": settings.AGENT_VISION_MODEL,
        "multi_note_detection_enabled": True,
        "parallel_processing": True,
        "source_type": "rocketbook"
    }
    
    logger.info("\n" + "=" * 80)
    logger.info("CONFIGURATION")
    logger.info("=" * 80)
    for key, value in config.items():
        logger.info(f"{key}: {value}")
    
    # Process image
    logger.info("\n" + "=" * 80)
    logger.info("PROCESSING IMAGE")
    logger.info("=" * 80)
    
    try:
        result = await agent.process_multi_note_image(image_path, config)
        
        logger.info("\n" + "=" * 80)
        logger.info("PROCESSING RESULT")
        logger.info("=" * 80)
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result attributes: {dir(result)}")
        
        if hasattr(result, 'notes'):
            notes = result.notes if isinstance(result.notes, list) else [result.notes]
            logger.info(f"\nNumber of notes detected: {len(notes)}")
            
            for i, note in enumerate(notes, 1):
                logger.info(f"\n--- Note {i} ---")
                if hasattr(note, 'note_id'):
                    logger.info(f"Note ID: {note.note_id}")
                if hasattr(note, 'text_content'):
                    logger.info(f"Title: {getattr(note.text_content, 'title', 'N/A')}")
                    logger.info(f"Text length: {len(getattr(note.text_content, 'content', ''))}")
                    logger.info(f"Text preview (first 500 chars):")
                    logger.info(getattr(note.text_content, 'content', '')[:500])
                elif hasattr(note, 'content'):
                    logger.info(f"Content length: {len(note.content)}")
                    logger.info(f"Content preview (first 500 chars):")
                    logger.info(note.content[:500])
        else:
            logger.error("No notes found in result!")
            logger.error(f"Result: {result}")
            
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_note_upload())

