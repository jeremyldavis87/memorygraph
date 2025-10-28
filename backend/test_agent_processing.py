"""
Test script to process an image through the agent pipeline with detailed logging.
This will help diagnose why Vision LLM is producing poor results.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Load environment variables first
from dotenv import load_dotenv
load_dotenv('.env.development')

# Setup logging to both console and file
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"agent_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def test_agent_processing():
    """Test the agent processing with detailed logging"""
    
    logger.info("=" * 80)
    logger.info("AGENT PROCESSING DIAGNOSTIC TEST")
    logger.info("=" * 80)
    
    # Check if image path is provided
    if len(sys.argv) < 2:
        logger.error("Please provide an image path as argument")
        logger.info("Usage: python test_agent_processing.py <image_path>")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return
    
    logger.info(f"Processing image: {image_path}")
    logger.info(f"Image exists: {os.path.exists(image_path)}")
    logger.info(f"Image size: {os.path.getsize(image_path)} bytes")
    
    try:
        from app.services.agent_service import NoteProcessingAgent
        from app.services.ai_service import AIService
        from app.core.config import settings
        
        logger.info("\n" + "=" * 80)
        logger.info("INITIALIZING SERVICES")
        logger.info("=" * 80)
        
        # Check OpenAI API key
        logger.info(f"OpenAI API Key from env: {os.getenv('OPENAI_API_KEY')[:20] if os.getenv('OPENAI_API_KEY') else 'NOT SET'}...")
        logger.info(f"OpenAI API Key configured: {bool(settings.OPENAI_API_KEY)}")
        logger.info(f"Braintrust API Key configured: {bool(settings.BRAINTRUST_API_KEY)}")
        
        # Initialize the agent
        logger.info("\nInitializing NoteProcessingAgent...")
        agent = NoteProcessingAgent("gpt-4o-mini")
        logger.info("Agent initialized successfully")
        
        # Configuration
        config = {
            "ocr_mode": "auto",  # Use hybrid mode
            "vision_model_preference": "gpt-4o-mini",
            "ocr_confidence_threshold": 0.5,
            "source_type": "rocketbook"
        }
        
        logger.info(f"Configuration: {config}")
        
        logger.info("\n" + "=" * 80)
        logger.info("STARTING AGENT PROCESSING")
        logger.info("=" * 80)
        
        # Process the image
        result = await agent.process_multi_note_image(image_path, config)
        
        logger.info("\n" + "=" * 80)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 80)
        
        # Log results
        logger.info(f"Result type: {type(result)}")
        
        if hasattr(result, 'notes'):
            logger.info(f"Number of notes found: {len(result.notes) if isinstance(result.notes, list) else 1}")
            
            notes = result.notes if isinstance(result.notes, list) else [result.notes]
            
            for i, note in enumerate(notes):
                logger.info(f"\n--- Note {i+1} ---")
                
                if hasattr(note, 'text_content'):
                    text_content = note.text_content
                    logger.info(f"Raw text: {text_content.get('raw_text', '')[:200]}...")
                    logger.info(f"Formatted text: {text_content.get('formatted_text', '')[:200]}...")
                    logger.info(f"Extraction method: {text_content.get('extraction_method', 'unknown')}")
                    logger.info(f"Confidence score: {text_content.get('confidence_score', 0)}")
                
                if hasattr(note, 'structure'):
                    structure = note.structure
                    if structure and hasattr(structure, 'title') and structure.title:
                        logger.info(f"Title: {structure.title.get('text', 'No title')}")
                
                if hasattr(note, 'quality_metrics'):
                    metrics = note.quality_metrics
                    logger.info(f"Quality metrics: {metrics}")
                
                if hasattr(note, 'processing_details'):
                    details = note.processing_details
                    logger.info(f"Processing details: {details}")
        
        elif hasattr(result, 'data'):
            logger.info("Partial result received")
            logger.info(f"Data: {result.data}")
            if hasattr(result, 'error'):
                logger.error(f"Error: {result.error}")
        
        logger.info("\n" + "=" * 80)
        logger.info("DIAGNOSTIC COMPLETE")
        logger.info(f"Full logs saved to: {log_file}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error("Error during processing:", exc_info=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_processing())

