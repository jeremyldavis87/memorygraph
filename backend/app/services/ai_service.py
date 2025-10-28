from openai import OpenAI
from typing import Dict, Any, List, Optional
import json
import re
import base64
import os
from app.core.config import settings

# Try to import Braintrust for automatic tracing
try:
    import braintrust
    BRAINTRUST_AVAILABLE = True
except ImportError:
    BRAINTRUST_AVAILABLE = False

class AIService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            # Create OpenAI client
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Wrap with Braintrust for automatic tracing if available
            if BRAINTRUST_AVAILABLE and settings.BRAINTRUST_API_KEY:
                try:
                    braintrust.init(
                        project_name="memorygraph-agent",
                        api_key=settings.BRAINTRUST_API_KEY
                    )
                    # Wrap the client for automatic tracing
                    self.client = braintrust.wrap_openai(client)
                except Exception as e:
                    print(f"Failed to wrap OpenAI client with Braintrust: {e}")
                    self.client = client
            else:
                self.client = client
    
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
        
        if not self.client:
            return ""
        
        try:
            response = self.client.chat.completions.create(
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
        
        if not self.client:
            return []
        
        try:
            response = self.client.chat.completions.create(
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
        
        if not self.client:
            return []
        
        try:
            response = self.client.chat.completions.create(
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
        
        if not self.client:
            return []
        
        try:
            response = self.client.chat.completions.create(
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
    
    def process_with_vision_llm(self, image_path: str, prompt: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Process image with vision LLM to extract text and structure.
        """
        if not settings.OPENAI_API_KEY:
            return {"error": "OpenAI API key not configured"}
        
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare the message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            if not self.client:
                return {"error": "OpenAI client not initialized"}
            
            # Call OpenAI Vision API (automatically traced by Braintrust wrapper)
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            return {
                "success": True,
                "text": response.choices[0].message.content.strip(),
                "model_used": model
            }
            
        except Exception as e:
            print(f"Vision LLM processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_note_regions_with_vision(self, image_path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Use vision LLM to detect and describe note regions in a multi-note image.
        """
        prompt = """
        Analyze this image and identify all individual notes. For each note you can see:
        1. Count the total number of notes
        2. Describe the layout (e.g., "3x3 grid", "2x4 layout", etc.)
        3. For each note, provide:
           - Position number (1-9 for 3x3 grid, or sequential numbering)
           - Brief description of the content
           - Whether it has a QR code
           - Whether it has a title (look for ##Title## format or underlined text)
           - Type of content (bullet points, numbered list, checkbox list, plain text, etc.)

        Return your analysis as JSON in this format:
        {
            "total_notes": 9,
            "layout": "3x3 grid",
            "notes": [
                {
                    "position": 1,
                    "description": "Brief description of content",
                    "has_qr_code": true,
                    "has_title": false,
                    "content_type": "bullet_points"
                }
            ]
        }
        """
        
        result = self.process_with_vision_llm(image_path, prompt, model)
        
        if result.get("success"):
            try:
                # Try to parse the JSON response
                analysis = json.loads(result["text"])
                return {
                    "success": True,
                    "analysis": analysis,
                    "model_used": model
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                return {
                    "success": True,
                    "raw_text": result["text"],
                    "model_used": model
                }
        else:
            return result
    
    def extract_text_from_note_region(self, image_path: str, region_description: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Extract text from a specific note region using vision LLM.
        """
        prompt = f"""
        Extract all text from this note region. Pay special attention to:
        1. Preserve the exact formatting (bullet points, numbered lists, checkboxes)
        2. Look for titles marked with ##Title## format or underlined text
        3. Identify action items with checkboxes (☐, ☑, [ ], [x])
        4. Preserve special characters and symbols
        5. Maintain line breaks and spacing

        Note description: {region_description}

        Return the extracted text exactly as written, preserving all formatting.
        """
        
        result = self.process_with_vision_llm(image_path, prompt, model)
        
        if result.get("success"):
            return {
                "success": True,
                "extracted_text": result["text"],
                "model_used": model
            }
        else:
            return result