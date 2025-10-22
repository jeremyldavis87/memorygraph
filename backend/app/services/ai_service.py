import openai
from typing import Dict, Any, List
import json
import re
from app.core.config import settings

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    def process_note(self, note) -> Dict[str, Any]:
        """
        Process note with AI to extract entities, generate summary, etc.
        """
        if not settings.OPENAI_API_KEY:
            return self._fallback_processing(note)
        
        try:
            # Generate summary
            summary = self._generate_summary(note.content or note.original_text)
            
            # Extract entities
            entities = self._extract_entities(note.content or note.original_text)
            
            # Extract action items
            action_items = self._extract_action_items_ai(note.content or note.original_text)
            
            # Generate tags
            tags = self._generate_tags(note.content or note.original_text, note.title)
            
            return {
                "summary": summary,
                "entities": entities,
                "action_items": action_items,
                "tags": tags,
            "note_metadata_json": {
                "ai_processed": True,
                "processing_timestamp": note.created_at.isoformat()
            }
            }
        except Exception as e:
            print(f"AI processing failed: {e}")
            return self._fallback_processing(note)
    
    def _generate_summary(self, text: str) -> str:
        """
        Generate a summary of the note content
        """
        if not text or len(text.strip()) < 50:
            return ""
        
        prompt = f"""
        Please provide a concise 2-3 sentence summary of the following text:
        
        {text}
        
        Summary:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Summary generation failed: {e}")
            return ""
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        """
        if not text:
            return []
        
        prompt = f"""
        Extract named entities from the following text. Return as JSON array with objects containing:
        - name: entity name
        - type: one of (person, organization, project, concept, location, date, technology)
        - confidence: 0-100
        
        Text: {text}
        
        JSON:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            # Try to parse JSON
            entities = json.loads(result)
            return entities if isinstance(entities, list) else []
        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return []
    
    def _extract_action_items_ai(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract action items using AI
        """
        if not text:
            return []
        
        prompt = f"""
        Extract action items from the following text. Return as JSON array with objects containing:
        - text: action item description
        - completed: boolean
        - priority: one of (low, normal, high, urgent)
        - due_date: if mentioned, in YYYY-MM-DD format
        
        Text: {text}
        
        JSON:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            action_items = json.loads(result)
            return action_items if isinstance(action_items, list) else []
        except Exception as e:
            print(f"Action item extraction failed: {e}")
            return []
    
    def _generate_tags(self, text: str, title: str) -> List[Dict[str, Any]]:
        """
        Generate relevant tags for the note
        """
        if not text:
            return []
        
        prompt = f"""
        Generate 3-5 relevant tags for this note. Consider both the title and content.
        Return as JSON array of strings.
        
        Title: {title}
        Content: {text}
        
        JSON:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            tags = json.loads(result)
            return [{"name": tag, "type": "ai_generated"} for tag in tags if isinstance(tags, list)]
        except Exception as e:
            print(f"Tag generation failed: {e}")
            return []
    
    def _fallback_processing(self, note) -> Dict[str, Any]:
        """
        Fallback processing when AI is not available
        """
        return {
            "summary": "",
            "entities": [],
            "action_items": [],
            "tags": [],
            "note_metadata_json": {
                "ai_processed": False,
                "processing_timestamp": note.created_at.isoformat()
            }
        }