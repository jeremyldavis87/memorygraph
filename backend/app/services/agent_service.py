from typing import Dict, Any, List, Optional, Union
import os
import uuid
from datetime import datetime

from app.services.agents.orchestrator_agent import OrchestratorAgent
from app.services.agents.base_agent import PartialResult
from app.schemas.agent_schemas import ProcessingOutput
from app.core.config import settings


class NoteProcessingAgent:
    def __init__(self, model_name: str = None):
        """
        Initialize the note processing agent with the new multi-agent architecture.
        """
        # Use settings.AGENT_VISION_MODEL if not provided
        self.model_name = model_name or settings.AGENT_VISION_MODEL
        self.orchestrator = OrchestratorAgent()
    
    async def process_multi_note_image(self, image_path: str, config: Dict[str, Any] = None) -> Union[ProcessingOutput, PartialResult]:
        """
        Process a multi-note image using the orchestrator agent.
        
        Args:
            image_path: Path to the image file
            config: Optional configuration dictionary
            
        Returns:
            ProcessingOutput with comprehensive results or PartialResult if processing fails
        """
        if config is None:
            config = {}
        
        # Add default configuration
        config.setdefault("multi_note_detection_enabled", True)
        config.setdefault("vision_model", self.model_name)
        config.setdefault("parallel_processing", True)
        
        # Process using orchestrator
        result = await self.orchestrator.process(image_path, config)
        
        return result