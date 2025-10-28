"""
Structure Recognition Agent

Handles content structure recognition including titles, lists, todos, and tags.
Detects patterns like ##TITLE##, bullet points, numbered lists, checkboxes,
@tags, and ::key:value pairs.
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass

from .base_agent import BaseAgent, PartialResult


@dataclass
class Title:
    """Container for title information"""
    text: str
    format: str
    position: int
    confidence: float = 1.0


@dataclass
class ListItem:
    """Container for list item information"""
    text: str
    number: Optional[int] = None
    bullet_type: Optional[str] = None
    line: int = 0


@dataclass
class TodoItem:
    """Container for todo item information"""
    text: str
    completed: bool
    line: int
    checkbox_type: str = "box"


@dataclass
class Tag:
    """Container for tag information"""
    name: str
    value: Optional[str] = None
    type: str = "simple"  # simple or key_value
    line: int = 0


@dataclass
class DocumentStructure:
    """Container for complete document structure"""
    title: Optional[Title] = None
    sections: List[Dict[str, Any]] = None
    bulleted_lists: List[List[ListItem]] = None
    numbered_lists: List[List[ListItem]] = None
    todos: List[TodoItem] = None
    simple_tags: List[Tag] = None
    key_value_tags: List[Tag] = None
    has_title: bool = False
    has_lists: bool = False
    has_todos: bool = False
    has_tags: bool = False


class StructureRecognitionAgent(BaseAgent):
    """
    Agent responsible for recognizing document structure and semantic patterns.
    
    Capabilities:
    - Title detection (##TITLE## pattern)
    - Bulleted list recognition
    - Numbered list recognition with sequence validation
    - To-do item detection with checkbox patterns
    - Simple tag extraction (@tag)
    - Key-value tag extraction (::key:value)
    - Document structure analysis
    """
    
    def __init__(self):
        super().__init__("StructureRecognitionAgent")
        
        # Compile regex patterns for efficiency
        self.title_patterns = [
            re.compile(r'##\s*(.+?)\s*##', re.MULTILINE),  # ## Title ##
            re.compile(r'#\s*(.+?)\s*#', re.MULTILINE),     # # Title #
            re.compile(r'=+\s*(.+?)\s*=+', re.MULTILINE),   # ==Title==
        ]
        
        self.bullet_patterns = [
            re.compile(r'^\s*[•●○◦▪▫■□]\s+(.+)$', re.MULTILINE),  # Unicode bullets
            re.compile(r'^\s*[-\*\+]\s+(.+)$', re.MULTILINE),      # ASCII bullets
            re.compile(r'^\s*>\s+(.+)$', re.MULTILINE),             # Quote-style bullets
        ]
        
        self.numbered_patterns = [
            re.compile(r'^\s*(\d+)[\.\)]\s+(.+)$', re.MULTILINE),  # 1. Item or 1) Item
            re.compile(r'^\s*\((\d+)\)\s+(.+)$', re.MULTILINE),      # (1) Item
            re.compile(r'^\s*(\d+)\s*[-–—]\s*(.+)$', re.MULTILINE),  # 1 - Item
        ]
        
        self.todo_patterns = [
            re.compile(r'^\s*\[\s*\]\s+(.+)$', re.MULTILINE),      # [ ] Task
            re.compile(r'^\s*\[[\s?]\]\s+(.+)$', re.MULTILINE),    # [?] Task (uncertain)
            re.compile(r'^\s*\[[xX✓✔]\]\s+(.+)$', re.MULTILINE),   # [x] Task (completed)
            re.compile(r'^\s*☐\s+(.+)$', re.MULTILINE),             # ☐ Task (Unicode checkbox)
            re.compile(r'^\s*☑\s+(.+)$', re.MULTILINE),             # ☑ Task (Unicode checked)
            re.compile(r'^\s*○\s+(.+)$', re.MULTILINE),             # ○ Task (circle)
            re.compile(r'^\s*◉\s+(.+)$', re.MULTILINE),             # ◉ Task (filled circle)
        ]
        
        self.simple_tag_pattern = re.compile(r'@([a-zA-Z0-9_]+)\b')
        self.keyvalue_tag_pattern = re.compile(r'::([a-zA-Z0-9_]+):([^\s:]+)')
    
    async def process(self, text: str) -> Union[DocumentStructure, PartialResult]:
        """
        Main processing method for structure recognition.
        
        Args:
            text: Input text to analyze
            
        Returns:
            DocumentStructure object or PartialResult if processing fails
        """
        return await self.execute_with_retry(self._recognize_structure, text)
    
    async def _recognize_structure(self, text: str) -> DocumentStructure:
        """Internal method to recognize document structure"""
        # Extract title
        title = self._extract_title(text)
        
        # Extract lists
        bulleted_lists = self._extract_bulleted_lists(text)
        numbered_lists = self._extract_numbered_lists(text)
        
        # Extract todos
        todos = self._extract_todos(text)
        
        # Extract tags
        simple_tags, key_value_tags = self._extract_tags(text)
        
        # Create sections
        sections = self._create_sections(text, title, bulleted_lists, numbered_lists, todos)
        
        # Create structure object
        structure = DocumentStructure(
            title=title,
            sections=sections,
            bulleted_lists=bulleted_lists,
            numbered_lists=numbered_lists,
            todos=todos,
            simple_tags=simple_tags,
            key_value_tags=key_value_tags,
            has_title=title is not None,
            has_lists=len(bulleted_lists) > 0 or len(numbered_lists) > 0,
            has_todos=len(todos) > 0,
            has_tags=len(simple_tags) > 0 or len(key_value_tags) > 0
        )
        
        # Log metrics
        self.log_metric("has_title", 1 if structure.has_title else 0)
        self.log_metric("has_lists", 1 if structure.has_lists else 0)
        self.log_metric("has_todos", 1 if structure.has_todos else 0)
        self.log_metric("has_tags", 1 if structure.has_tags else 0)
        self.log_metric("total_todos", len(todos))
        self.log_metric("total_tags", len(simple_tags) + len(key_value_tags))
        
        return structure
    
    def _extract_title(self, text: str) -> Optional[Title]:
        """Extract title using various patterns"""
        lines = text.split('\n')
        
        # Try regex patterns first
        for pattern in self.title_patterns:
            matches = pattern.findall(text)
            if matches:
                title_text = matches[0].strip()
                # Find line number
                for i, line in enumerate(lines):
                    if title_text in line:
                        return Title(
                            text=title_text,
                            format=pattern.pattern,
                            position=i + 1,
                            confidence=1.0
                        )
        
        # Fallback to heuristic detection
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for underlined text (common in handwritten notes)
            if line.startswith('_') and line.endswith('_'):
                return Title(
                    text=line[1:-1].strip(),
                    format="underlined",
                    position=i + 1,
                    confidence=0.8
                )
            
            # Check for all caps (common for titles)
            if line.isupper() and len(line) > 3:
                return Title(
                    text=line.title(),
                    format="all_caps",
                    position=i + 1,
                    confidence=0.7
                )
            
            # Check for text in brackets or parentheses
            if (line.startswith('[') and line.endswith(']')) or \
               (line.startswith('(') and line.endswith(')')):
                return Title(
                    text=line[1:-1].strip(),
                    format="brackets",
                    position=i + 1,
                    confidence=0.6
                )
            
            # First non-empty line as fallback
            if len(line) > 3 and i < 3:  # Only consider first few lines
                return Title(
                    text=line,
                    format="first_line",
                    position=i + 1,
                    confidence=0.5
                )
        
        return None
    
    def _extract_bulleted_lists(self, text: str) -> List[List[ListItem]]:
        """Extract all bulleted lists from text"""
        lists = []
        current_list = None
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            is_bullet = False
            bullet_text = None
            bullet_type = None
            
            for pattern in self.bullet_patterns:
                match = pattern.match(line)
                if match:
                    is_bullet = True
                    bullet_text = match.group(1).strip()
                    bullet_type = pattern.pattern
                    break
            
            if is_bullet:
                if current_list is None:
                    current_list = {
                        'type': 'bulleted_list',
                        'items': [],
                        'line_start': i + 1
                    }
                
                current_list['items'].append(ListItem(
                    text=bullet_text,
                    bullet_type=bullet_type,
                    line=i + 1
                ))
            else:
                if current_list:
                    current_list['line_end'] = i
                    lists.append(current_list['items'])
                    current_list = None
        
        # Catch list that continues to end of text
        if current_list:
            current_list['line_end'] = len(lines)
            lists.append(current_list['items'])
        
        return lists
    
    def _extract_numbered_lists(self, text: str) -> List[List[ListItem]]:
        """Extract numbered lists and validate sequence"""
        lists = []
        current_list = None
        expected_number = 1
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            is_numbered = False
            number = None
            item_text = None
            
            for pattern in self.numbered_patterns:
                match = pattern.match(line)
                if match:
                    number = int(match.group(1))
                    item_text = match.group(2).strip()
                    is_numbered = True
                    break
            
            if is_numbered:
                # Check if this continues current list
                if current_list is None or number == expected_number:
                    if current_list is None:
                        current_list = {
                            'type': 'numbered_list',
                            'items': [],
                            'line_start': i + 1
                        }
                        expected_number = 1
                    
                    current_list['items'].append(ListItem(
                        text=item_text,
                        number=number,
                        line=i + 1
                    ))
                    expected_number = number + 1
                else:
                    # Sequence broken, start new list
                    if current_list:
                        current_list['line_end'] = i
                        lists.append(current_list['items'])
                    
                    current_list = {
                        'type': 'numbered_list',
                        'items': [ListItem(
                            text=item_text,
                            number=number,
                            line=i + 1
                        )],
                        'line_start': i + 1
                    }
                    expected_number = number + 1
            else:
                if current_list:
                    current_list['line_end'] = i
                    lists.append(current_list['items'])
                    current_list = None
                    expected_number = 1
        
        if current_list:
            current_list['line_end'] = len(lines)
            lists.append(current_list['items'])
        
        return lists
    
    def _extract_todos(self, text: str) -> List[TodoItem]:
        """Extract all to-do items from text"""
        todos = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.todo_patterns:
                match = pattern.match(line)
                if match:
                    task_text = match.group(1).strip()
                    
                    # Determine if completed
                    completed = any(marker in line for marker in ['[x]', '[X]', '[✓]', '[✔]', '☑', '◉'])
                    
                    # Determine checkbox type
                    if '☐' in line or '☑' in line:
                        checkbox_type = "unicode"
                    elif '○' in line or '◉' in line:
                        checkbox_type = "circle"
                    else:
                        checkbox_type = "box"
                    
                    todos.append(TodoItem(
                        text=task_text,
                        completed=completed,
                        line=i + 1,
                        checkbox_type=checkbox_type
                    ))
                    break
        
        return todos
    
    def _extract_tags(self, text: str) -> Tuple[List[Tag], List[Tag]]:
        """Extract both simple and key-value tags"""
        simple_tags = []
        key_value_tags = []
        lines = text.split('\n')
        
        # Extract simple tags
        simple_matches = self.simple_tag_pattern.findall(text)
        for i, tag_name in enumerate(simple_matches):
            # Find line number
            line_num = 0
            for j, line in enumerate(lines):
                if f"@{tag_name}" in line:
                    line_num = j + 1
                    break
            
            simple_tags.append(Tag(
                name=tag_name,
                type="simple",
                line=line_num
            ))
        
        # Extract key-value tags
        keyvalue_matches = self.keyvalue_tag_pattern.findall(text)
        for key, value in keyvalue_matches:
            # Find line number
            line_num = 0
            for j, line in enumerate(lines):
                if f"::{key}:{value}" in line:
                    line_num = j + 1
                    break
            
            key_value_tags.append(Tag(
                name=key,
                value=value,
                type="key_value",
                line=line_num
            ))
        
        return simple_tags, key_value_tags
    
    def _create_sections(self, text: str, title: Optional[Title], 
                        bulleted_lists: List[List[ListItem]], 
                        numbered_lists: List[List[ListItem]], 
                        todos: List[TodoItem]) -> List[Dict[str, Any]]:
        """Create structured sections from the document"""
        sections = []
        lines = text.split('\n')
        
        # Add title section if exists
        if title:
            sections.append({
                "type": "title",
                "content": title.text,
                "line_start": title.position,
                "line_end": title.position,
                "format": title.format
            })
        
        # Add list sections
        for bulleted_list in bulleted_lists:
            if bulleted_list:
                sections.append({
                    "type": "bulleted_list",
                    "items": [{"text": item.text, "line": item.line} for item in bulleted_list],
                    "line_start": bulleted_list[0].line,
                    "line_end": bulleted_list[-1].line
                })
        
        for numbered_list in numbered_lists:
            if numbered_list:
                sections.append({
                    "type": "numbered_list",
                    "items": [{"text": item.text, "number": item.number, "line": item.line} for item in numbered_list],
                    "line_start": numbered_list[0].line,
                    "line_end": numbered_list[-1].line
                })
        
        # Add todo section
        if todos:
            sections.append({
                "type": "todo_list",
                "items": [{"text": todo.text, "completed": todo.completed, "line": todo.line} for todo in todos],
                "line_start": todos[0].line,
                "line_end": todos[-1].line
            })
        
        # Add paragraph sections for remaining text
        used_lines = set()
        for section in sections:
            for line_num in range(section["line_start"], section["line_end"] + 1):
                used_lines.add(line_num)
        
        # Find paragraph sections
        paragraph_start = None
        for i, line in enumerate(lines):
            line_num = i + 1
            if line_num not in used_lines and line.strip():
                if paragraph_start is None:
                    paragraph_start = line_num
            elif paragraph_start is not None:
                sections.append({
                    "type": "paragraph",
                    "content": "\n".join(lines[paragraph_start-1:i]),
                    "line_start": paragraph_start,
                    "line_end": i
                })
                paragraph_start = None
        
        # Handle paragraph that continues to end
        if paragraph_start is not None:
            sections.append({
                "type": "paragraph",
                "content": "\n".join(lines[paragraph_start-1:]),
                "line_start": paragraph_start,
                "line_end": len(lines)
            })
        
        return sections
