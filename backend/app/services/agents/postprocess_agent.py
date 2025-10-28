"""
Post-Process Agent

Handles intelligent text correction and enhancement using contextual
understanding to identify and fix OCR errors, normalize formatting,
and generate clean formatted output.
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass

from .base_agent import BaseAgent, PartialResult
from app.services.ai_service import AIService


@dataclass
class ErrorCandidate:
    """Container for potential OCR error information"""
    word: str
    position: int
    confidence: float
    alternatives: List[str]


@dataclass
class Correction:
    """Container for text correction information"""
    original: str
    corrected: str
    confidence: float
    reason: str
    position: int


@dataclass
class CorrectionResult:
    """Container for correction results"""
    text: str
    corrections: List[Correction]
    original_text: str
    confidence: float


class PostProcessAgent(BaseAgent):
    """
    Agent responsible for intelligent text correction and enhancement.
    
    Capabilities:
    - OCR error identification using confidence scores
    - Alternative generation using OCR confusion matrix
    - Contextual correction with Vision LLM
    - Text normalization and formatting
    - Markdown formatting generation
    """
    
    def __init__(self):
        super().__init__("PostProcessAgent")
        self.ai_service = AIService()
        
        # Common OCR mistakes mapping
        self.ocr_common_mistakes = {
            # Letter/Number confusion
            'l': ['I', '1', '|'],
            'I': ['l', '1', '|'],
            '1': ['l', 'I', '|'],
            'O': ['0', 'o'],
            '0': ['O', 'o'],
            'o': ['O', '0'],
            'S': ['5', '$'],
            '5': ['S'],
            'B': ['8'],
            '8': ['B'],
            'Z': ['2'],
            '2': ['Z'],
            
            # Letter combinations
            'rn': ['m'],
            'm': ['rn'],
            'vv': ['w'],
            'w': ['vv'],
            'cl': ['d'],
            'd': ['cl'],
            'nn': ['m'],
        }
        
        # Common English words for validation
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
            'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
            'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
            'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
            'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
            'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
            'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has',
            'had', 'were', 'said', 'each', 'which', 'their', 'said', 'if',
            'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them',
            'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into',
            'him', 'time', 'has', 'two', 'more', 'go', 'no', 'way', 'could',
            'my', 'than', 'first', 'been', 'call', 'who', 'its', 'now',
            'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made',
            'may', 'part'
        }
    
    async def process(self, text: str, ocr_confidence: Optional[Dict[int, float]] = None) -> Union[CorrectionResult, PartialResult]:
        """
        Main processing method for text correction.
        
        Args:
            text: Input text to correct
            ocr_confidence: Optional word-level confidence scores
            
        Returns:
            CorrectionResult with corrected text or PartialResult if processing fails
        """
        return await self.execute_with_retry(self._correct_text, text, ocr_confidence)
    
    async def _correct_text(self, text: str, ocr_confidence: Optional[Dict[int, float]] = None) -> CorrectionResult:
        """Internal method to correct text"""
        if not text.strip():
            return CorrectionResult(
                text=text,
                corrections=[],
                original_text=text,
                confidence=1.0
            )
        
        # Identify likely errors
        error_candidates = self._identify_likely_errors(text, ocr_confidence)
        
        if not error_candidates:
            # No errors identified, just normalize formatting
            normalized_text = self._normalize_text(text)
            return CorrectionResult(
                text=normalized_text,
                corrections=[],
                original_text=text,
                confidence=1.0
            )
        
        # Correct errors using contextual understanding
        correction_result = await self._correct_with_context(text, error_candidates)
        
        # Normalize the corrected text
        normalized_text = self._normalize_text(correction_result.text)
        
        # Generate formatted version
        formatted_text = self._format_markdown(normalized_text)
        
        return CorrectionResult(
            text=formatted_text,
            corrections=correction_result.corrections,
            original_text=text,
            confidence=correction_result.confidence
        )
    
    def _identify_likely_errors(self, text: str, ocr_confidence: Optional[Dict[int, float]]) -> List[ErrorCandidate]:
        """Identify words that are likely OCR errors"""
        error_candidates = []
        words = text.split()
        
        for i, word in enumerate(words):
            # Clean word for analysis
            clean_word = re.sub(r'[^\w]', '', word.lower())
            
            if not clean_word:
                continue
            
            # Check if word is in common words dictionary
            if clean_word in self.common_words:
                continue
            
            # Get confidence for this word
            word_confidence = ocr_confidence.get(i, 0.5) if ocr_confidence else 0.5
            
            # Low confidence + not in dictionary = likely error
            if word_confidence < 0.8:
                # Generate alternative interpretations
                alternatives = self._generate_alternatives(clean_word)
                
                if alternatives:
                    error_candidates.append(ErrorCandidate(
                        word=word,
                        position=i,
                        confidence=word_confidence,
                        alternatives=alternatives
                    ))
        
        return error_candidates
    
    def _generate_alternatives(self, word: str) -> List[str]:
        """Generate alternative spellings based on OCR confusion matrix"""
        alternatives = set()
        
        # Try replacing each character with common confusions
        for i, char in enumerate(word):
            if char in self.ocr_common_mistakes:
                for replacement in self.ocr_common_mistakes[char]:
                    alt_word = word[:i] + replacement + word[i+1:]
                    if self._is_valid_word(alt_word):
                        alternatives.add(alt_word)
        
        # Try replacing character pairs
        for i in range(len(word) - 1):
            pair = word[i:i+2]
            if pair in self.ocr_common_mistakes:
                for replacement in self.ocr_common_mistakes[pair]:
                    alt_word = word[:i] + replacement + word[i+2:]
                    if self._is_valid_word(alt_word):
                        alternatives.add(alt_word)
        
        return list(alternatives)
    
    def _is_valid_word(self, word: str) -> bool:
        """Check if word is valid (in common words or looks reasonable)"""
        if word in self.common_words:
            return True
        
        # Check if it looks like a reasonable word
        if len(word) < 2 or len(word) > 20:
            return False
        
        # Check for reasonable character patterns
        if re.match(r'^[a-zA-Z]+$', word):
            return True
        
        return False
    
    async def _correct_with_context(self, text: str, error_candidates: List[ErrorCandidate]) -> CorrectionResult:
        """Use LLM to contextually correct identified errors"""
        if not error_candidates:
            return CorrectionResult(
                text=text,
                corrections=[],
                original_text=text,
                confidence=1.0
            )
        
        # Build correction prompt
        prompt = self._build_correction_prompt(text, error_candidates)
        
        try:
            # Use AI service for correction
            correction_result = self.ai_service._generate_summary(prompt)  # Reuse existing method
            
            # Parse corrections from AI response
            corrections = self._parse_correction_response(correction_result)
            
            # Apply corrections to text
            corrected_text = self._apply_corrections(text, corrections)
            
            return CorrectionResult(
                text=corrected_text,
                corrections=corrections,
                original_text=text,
                confidence=0.9  # High confidence for AI corrections
            )
            
        except Exception as e:
            self.logger.warning(f"AI correction failed: {e}")
            # Fall back to simple corrections
            return self._simple_corrections(text, error_candidates)
    
    def _build_correction_prompt(self, text: str, errors: List[ErrorCandidate]) -> str:
        """Build prompt for AI correction"""
        error_context = "\n".join([
            f"- Word '{e.word}' (confidence: {e.confidence:.2f}, alternatives: {e.alternatives})"
            for e in errors
        ])
        
        prompt = f"""
You are correcting potential OCR errors in handwritten text.

Original text:
{text}

Potential errors identified:
{error_context}

For each error, determine:
1. Is it actually an error?
2. If yes, what is the correct word?
3. Why (provide brief reasoning)

Consider the context carefully. Only correct if you are confident.

Provide response as JSON array:
[
  {{"original": "word", "corrected": "word", "confidence": 0.95, "reason": "explanation"}},
  ...
]
"""
        
        return prompt
    
    def _parse_correction_response(self, response: str) -> List[Correction]:
        """Parse AI correction response"""
        corrections = []
        
        try:
            # Try to extract JSON from response
            import json
            
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                corrections_data = json.loads(json_match.group(0))
                
                for i, correction_data in enumerate(corrections_data):
                    corrections.append(Correction(
                        original=correction_data.get("original", ""),
                        corrected=correction_data.get("corrected", ""),
                        confidence=correction_data.get("confidence", 0.8),
                        reason=correction_data.get("reason", ""),
                        position=i
                    ))
        except Exception as e:
            self.logger.warning(f"Failed to parse AI correction response: {e}")
        
        return corrections
    
    def _apply_corrections(self, text: str, corrections: List[Correction]) -> str:
        """Apply corrections to text"""
        corrected_text = text
        
        # Sort corrections by position (reverse order to maintain indices)
        corrections.sort(key=lambda c: c.position, reverse=True)
        
        for correction in corrections:
            # Only apply high-confidence corrections
            if correction.confidence > 0.8:
                corrected_text = corrected_text.replace(
                    correction.original,
                    correction.corrected,
                    1  # Replace only first occurrence
                )
        
        return corrected_text
    
    def _simple_corrections(self, text: str, error_candidates: List[ErrorCandidate]) -> CorrectionResult:
        """Apply simple corrections without AI"""
        corrections = []
        corrected_text = text
        
        for error in error_candidates:
            if error.alternatives:
                # Use the first alternative if it's significantly better
                best_alternative = error.alternatives[0]
                
                # Simple heuristic: prefer alternatives that are in common words
                if best_alternative in self.common_words:
                    corrections.append(Correction(
                        original=error.word,
                        corrected=best_alternative,
                        confidence=0.7,
                        reason="Common word alternative",
                        position=error.position
                    ))
                    
                    corrected_text = corrected_text.replace(error.word, best_alternative, 1)
        
        return CorrectionResult(
            text=corrected_text,
            corrections=corrections,
            original_text=text,
            confidence=0.6
        )
    
    def _normalize_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Fix common spacing issues
        text = re.sub(r' +', ' ', text)  # Multiple spaces → single space
        text = re.sub(r'\n\n+', '\n\n', text)  # Multiple newlines → double newline
        text = re.sub(r' ?\n ?', '\n', text)  # Spaces around newlines
        
        # Fix punctuation spacing
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)  # Add space after punctuation
        text = re.sub(r'([.,!?;:])\s+\n', r'\1\n', text)  # Remove space before newline
        
        # Fix hyphenation at line breaks
        text = re.sub(r'-\s*\n\s*', '', text)  # Remove hyphens at line break
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def _format_markdown(self, text: str) -> str:
        """Generate clean formatted version with markdown"""
        formatted_lines = []
        lines = text.split('\n')
        
        for line in lines:
            # Check for title patterns
            if re.match(r'##.*?##', line):
                formatted_lines.append(line)
                continue
            
            # Check for bullet points
            if re.match(r'^\s*[•●○◦▪▫■□\-\*\+]\s+', line):
                # Normalize bullet character
                formatted_lines.append(re.sub(r'^\s*[•●○◦▪▫■□\-\*\+]\s+', '• ', line))
                continue
            
            # Check for numbered lists
            if re.match(r'^\s*\d+[\.\)]\s+', line):
                formatted_lines.append(line)
                continue
            
            # Check for checkboxes
            if re.match(r'^\s*\[[\s\?xX✓✔]\].*', line):
                # Normalize checkbox
                if '[x]' in line.lower() or '[✓]' in line or '[✔]' in line:
                    formatted_lines.append(re.sub(r'^\s*\[[\s\?xX✓✔]\]', '☑', line))
                else:
                    formatted_lines.append(re.sub(r'^\s*\[[\s\?xX✓✔]\]', '☐', line))
                continue
            
            # Regular line
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
