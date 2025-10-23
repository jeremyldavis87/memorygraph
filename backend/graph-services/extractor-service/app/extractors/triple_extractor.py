import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import httpx

class Entity(BaseModel):
    name: str
    type: str  # Person, Organization, Project, Task, Note, etc.
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)

class Relationship(BaseModel):
    subject: str
    predicate: str
    object: str
    confidence: float = Field(ge=0.0, le=1.0)
    properties: Dict[str, Any] = Field(default_factory=dict)

class ExtractionResult(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]
    triples: List[Dict[str, Any]]
    processing_time: float
    model_used: str

class TripleExtractor:
    def __init__(self):
        self.llm_provider = os.getenv("GRAPH_EXTRACTION_LLM_PROVIDER", "openai")
        self.model_name = os.getenv("GRAPH_EXTRACTION_MODEL", "gpt-4o-nano")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize LLM
        if self.llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.openai_api_key,
                temperature=0.1
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        # In-memory job storage (in production, use Redis or database)
        self.jobs: Dict[str, Dict[str, Any]] = {}
        
        # Core entity types from schema
        self.core_entity_types = [
            "Person", "Organization", "Project", "Task", "Note", "Meeting",
            "Decision", "Event", "Concept", "Location"
        ]
        
        # Core relationship types from schema
        self.core_relationship_types = [
            "WORKS_FOR", "WORKS_WITH", "MANAGES", "REPORTS_TO", "PART_OF",
            "MEMBER_OF", "ASSIGNED_TO", "PART_OF_PROJECT", "DEPENDS_ON",
            "CONTRIBUTES_TO", "OWNS", "BLOCKS", "ATTENDED", "MENTIONED_IN",
            "DISCUSSED", "SPOKE_WITH", "SENT_TO", "REFERENCES", "RELATES_TO",
            "TEACHES", "APPLIES_TO", "INSPIRED_BY", "LEARNED_FROM",
            "PRECEDED_BY", "FOLLOWED_BY", "OCCURRED_DURING", "DUE_BY",
            "SCHEDULED_FOR", "CAUSED_BY", "LED_TO", "RESULTED_IN",
            "INFLUENCED_BY", "PREVENTED", "SUMMARIZES", "EXPANDS_ON",
            "CONTRADICTS", "SUPPORTS", "REPLACES", "UPDATES", "LOCATED_IN",
            "HAPPENED_AT", "WORKS_FROM", "PARENT_OF", "CHILD_OF",
            "INSTANCE_OF", "CATEGORY_OF", "TAGGED_WITH", "HAS_METADATA",
            "KNOWS", "RELATED_TO", "INTRODUCED_BY"
        ]

    async def extract_triples(self, content: str, title: Optional[str] = None, 
                            source_type: str = "rocketbook", user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract knowledge graph triples from note content.
        """
        start_time = time.time()
        
        # Prepare the extraction prompt
        prompt = self._create_extraction_prompt(content, title, source_type)
        
        try:
            # Get LLM response
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            result_text = response.content
            
            # Parse the structured response
            entities, relationships = self._parse_llm_response(result_text)
            
            # Create triples from entities and relationships
            triples = self._create_triples(entities, relationships)
            
            processing_time = time.time() - start_time
            
            return {
                "triples": triples,
                "entities": [entity.dict() for entity in entities],
                "relationships": [rel.dict() for rel in relationships],
                "processing_time": processing_time,
                "model_used": self.model_name
            }
            
        except Exception as e:
            raise Exception(f"Triple extraction failed: {str(e)}")

    async def extract_triples_async(self, note_id: int, content: str, title: Optional[str] = None,
                                  source_type: str = "rocketbook", user_id: int = None) -> str:
        """
        Queue an async triple extraction job.
        """
        job_id = str(uuid.uuid4())
        
        # Store job info
        self.jobs[job_id] = {
            "status": "queued",
            "note_id": note_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "result": None,
            "error": None
        }
        
        # Start background task
        asyncio.create_task(self._process_async_extraction(job_id, content, title, source_type))
        
        return job_id

    async def _process_async_extraction(self, job_id: str, content: str, 
                                      title: Optional[str], source_type: str):
        """
        Process async extraction in background.
        """
        try:
            self.jobs[job_id]["status"] = "processing"
            
            result = await self.extract_triples(content, title, source_type)
            
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["result"] = result
            
        except Exception as e:
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error"] = str(e)

    async def get_extraction_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of an extraction job.
        """
        if job_id not in self.jobs:
            raise ValueError("Job not found")
        
        job = self.jobs[job_id]
        return {
            "job_id": job_id,
            "status": job["status"],
            "created_at": job["created_at"],
            "error": job.get("error")
        }

    async def get_extraction_result(self, job_id: str) -> Dict[str, Any]:
        """
        Get the result of a completed extraction job.
        """
        if job_id not in self.jobs:
            raise ValueError("Job not found")
        
        job = self.jobs[job_id]
        if job["status"] != "completed":
            raise ValueError("Job not completed yet")
        
        return job["result"]

    def _create_extraction_prompt(self, content: str, title: Optional[str], source_type: str) -> str:
        """
        Create the extraction prompt for the LLM.
        """
        prompt = f"""
Extract knowledge graph entities and relationships from the following {source_type} note:

Title: {title or 'No title'}

Content:
{content}

Please extract:
1. ENTITIES: People, organizations, projects, tasks, concepts, locations, events, etc.
2. RELATIONSHIPS: How these entities relate to each other

Focus on the core entity types: {', '.join(self.core_entity_types)}
Use relationship types from: {', '.join(self.core_relationship_types[:20])}...

Return your response in this JSON format:
{{
  "entities": [
    {{
      "name": "Entity Name",
      "type": "EntityType",
      "properties": {{"key": "value"}},
      "confidence": 0.9
    }}
  ],
  "relationships": [
    {{
      "subject": "Entity1",
      "predicate": "RELATIONSHIP_TYPE",
      "object": "Entity2",
      "confidence": 0.8,
      "properties": {{"key": "value"}}
    }}
  ]
}}
"""
        return prompt

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the LLM.
        """
        return """You are an expert knowledge graph extraction system. Your task is to analyze text content and extract structured entities and relationships that can be stored in a knowledge graph.

Guidelines:
1. Extract only factual, explicit information from the text
2. Use the provided entity and relationship types
3. Assign confidence scores (0.0-1.0) based on how explicit the information is
4. For entities, include relevant properties like dates, roles, descriptions
5. For relationships, use the standard relationship types provided
6. Be conservative - only extract information that is clearly stated
7. Handle ambiguity by creating separate entities with different contexts

Entity extraction priorities:
- High: People, Organizations, Projects, Tasks, Decisions
- Medium: Concepts, Locations, Events, Meetings
- Low: Keywords, Insights (only if clearly stated)

Relationship extraction rules:
- Co-occurrence: Entities mentioned together likely have relationships
- Temporal: Events and notes in sequence are related
- Semantic: Look for explicit relationship indicators
- Action: Tasks assigned to people, projects involving people
"""

    def _parse_llm_response(self, response_text: str) -> tuple[List[Entity], List[Relationship]]:
        """
        Parse the LLM response into structured entities and relationships.
        """
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
            else:
                # Fallback: try to parse the entire response as JSON
                data = json.loads(response_text)
            
            entities = [Entity(**entity) for entity in data.get("entities", [])]
            relationships = [Relationship(**rel) for rel in data.get("relationships", [])]
            
            return entities, relationships
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: create minimal entities from the text
            entities = self._fallback_entity_extraction(response_text)
            relationships = []
            return entities, relationships

    def _fallback_entity_extraction(self, text: str) -> List[Entity]:
        """
        Fallback entity extraction when JSON parsing fails.
        """
        entities = []
        
        # Simple keyword-based extraction
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and len(line) > 10:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    description = parts[1].strip()
                    
                    # Determine entity type based on context
                    entity_type = "Concept"
                    if any(word in name.lower() for word in ['person', 'people', 'individual']):
                        entity_type = "Person"
                    elif any(word in name.lower() for word in ['company', 'organization', 'team']):
                        entity_type = "Organization"
                    elif any(word in name.lower() for word in ['project', 'initiative']):
                        entity_type = "Project"
                    elif any(word in name.lower() for word in ['task', 'action', 'todo']):
                        entity_type = "Task"
                    
                    entities.append(Entity(
                        name=name,
                        type=entity_type,
                        properties={"description": description},
                        confidence=0.5
                    ))
        
        return entities

    def _create_triples(self, entities: List[Entity], relationships: List[Relationship]) -> List[Dict[str, Any]]:
        """
        Create triples from entities and relationships.
        """
        triples = []
        
        # Add entity triples
        for entity in entities:
            triples.append({
                "subject": entity.name,
                "predicate": "INSTANCE_OF",
                "object": entity.type,
                "confidence": entity.confidence,
                "entity_type": entity.type,
                "relationship_type": "INSTANCE_OF",
                "properties": entity.properties
            })
        
        # Add relationship triples
        for rel in relationships:
            triples.append({
                "subject": rel.subject,
                "predicate": rel.predicate,
                "object": rel.object,
                "confidence": rel.confidence,
                "entity_type": "Relationship",
                "relationship_type": rel.predicate,
                "properties": rel.properties
            })
        
        return triples
