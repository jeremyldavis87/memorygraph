# MemoryGraph - Product Requirements Document
## AI Agent Architecture Edition

**Version:** 2.0  
**Date:** October 27, 2025  
**Status:** Draft  
**Product Type:** AI Agent-Powered Visual Content Intelligence Platform  
**Architecture:** Multi-Agent Processing System

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [AI Agent Architecture Overview](#ai-agent-architecture-overview)
3. [Agent Core System Design](#agent-core-system-design)
4. [Technical Requirements](#technical-requirements)
5. [Image Processing Pipeline](#image-processing-pipeline)
6. [Vision LLM Integration](#vision-llm-integration)
7. [Output Schema & JSON Structure](#output-schema--json-structure)
8. [Content Recognition Patterns](#content-recognition-patterns)
9. [Post-Processing Intelligence](#post-processing-intelligence)
10. [Multi-Note Separation Engine](#multi-note-separation-engine)
11. [Metadata Extraction System](#metadata-extraction-system)
12. [Error Handling & Confidence Scoring](#error-handling--confidence-scoring)
13. [Performance Requirements](#performance-requirements)
14. [Integration Architecture](#integration-architecture)
15. [Success Metrics](#success-metrics)
16. [Implementation Phases](#implementation-phases)
17. [Risk & Mitigation](#risk--mitigation)

---

# Executive Summary

## Product Name: MemoryGraph AI Agent

**Tagline:** "Intelligent visual content extraction through coordinated AI agents"

## What We're Building

MemoryGraph AI Agent is an intelligent multi-agent system that processes handwritten and visual content through coordinated orchestration of computer vision tools, OCR engines, QR code scanners, and vision language models. The agent architecture enables sophisticated image understanding by combining specialized tools with generative AI for superior accuracy, context awareness, and structured data extraction.

Unlike traditional OCR systems that apply single-pass recognition, MemoryGraph AI Agent employs a multi-stage processing pipeline where specialized agents handle detection, separation, extraction, validation, and post-processing tasks. The system returns comprehensive JSON output containing not just recognized text, but rich metadata, formatting preservation, semantic structure, and contextual corrections.

## Core Architecture Principles

**Agent Orchestration**
The central orchestrator agent coordinates specialized sub-agents for image processing, text extraction, QR scanning, validation, and post-processing. Each agent operates independently but communicates through a shared context and decision framework.

**Tool-Augmented Intelligence**
Agents leverage traditional computer vision libraries (OpenCV, pytesseract, pyzbar) alongside modern vision LLMs (GPT-4-Vision/GPT-5-mini) to achieve accuracy beyond either approach alone.

**Structured Output Protocol**
All processing results flow through a standardized JSON schema that captures raw data, processed data, metadata, confidence scores, and extracted semantic structures.

**Progressive Enhancement**
The system applies multiple passes of increasing sophistication, starting with fast traditional methods and escalating to expensive LLM calls only when needed or for validation.

## Key Differentiators

1. **Multi-Agent Coordination:** Specialized agents work together rather than monolithic processing
2. **Hybrid Tool + AI Approach:** Combines deterministic CV tools with probabilistic LLM understanding
3. **Multi-Note Intelligence:** Automatically detects and separates multiple sticky notes or content regions
4. **Semantic Structure Extraction:** Identifies titles, lists, tasks, tags, and key-value metadata
5. **Context-Aware Post-Processing:** Uses LLM to correct OCR errors based on content understanding
6. **Comprehensive Metadata:** Extracts color, QR codes, handwriting style, confidence scores
7. **Format Preservation:** Maintains document structure including indentation, bullets, numbering

## Initial Release Scope

Launch with a production-ready AI agent system capable of:
- Separating and processing multiple sticky notes from a single image
- High-accuracy handwriting OCR using hybrid tool + LLM approach
- QR code detection and decoding
- Semantic structure recognition (titles, lists, tasks, tags)
- Contextual typo correction and text normalization
- Rich JSON output with full metadata

---

# AI Agent Architecture Overview

## System Architecture Philosophy

MemoryGraph employs a **hierarchical multi-agent system** where a central Orchestrator Agent coordinates specialized sub-agents, each responsible for a specific aspect of visual content processing. This architecture provides:

**Modularity:** Each agent can be upgraded or replaced independently  
**Scalability:** Agents can process in parallel when appropriate  
**Reliability:** Agent failures are isolated and recoverable  
**Observability:** Each agent reports confidence and decision rationale  
**Extensibility:** New agents can be added without system redesign

## Agent Hierarchy

```
┌─────────────────────────────────────────┐
│     Orchestrator Agent (Core)           │
│  - Task planning and coordination       │
│  - Agent selection and sequencing       │
│  - Result aggregation and validation    │
│  - Quality assessment and routing       │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼──────┐ ┌──▼────────┐ ┌▼──────────────┐
│ Image        │ │ Separation │ │ QR/Metadata   │
│ Processing   │ │ Agent      │ │ Agent         │
│ Agent        │ │            │ │               │
└──────┬───────┘ └──┬─────────┘ └┬──────────────┘
       │            │             │
┌──────▼──────┐ ┌──▼─────────┐ ┌▼──────────────┐
│ Text        │ │ Structure  │ │ Post-Process  │
│ Extraction  │ │ Recognition│ │ Agent         │
│ Agent       │ │ Agent      │ │               │
└─────────────┘ └────────────┘ └───────────────┘
```

## Agent Responsibilities

### Orchestrator Agent
**Role:** Central coordinator and decision maker  
**Responsibilities:**
- Receives raw image input and user parameters
- Analyzes image characteristics to determine processing strategy
- Dispatches tasks to appropriate sub-agents
- Manages agent dependencies and sequencing
- Aggregates results from all agents
- Performs final validation and quality checks
- Generates structured JSON output
- Handles errors and fallback strategies

**Decision Framework:**
```python
if image_contains_multiple_notes():
    invoke(SeparationAgent)
    for each_separated_note:
        invoke(ImageProcessingAgent)
        invoke(TextExtractionAgent)
        invoke(StructureRecognitionAgent)
else:
    invoke(ImageProcessingAgent)
    invoke(TextExtractionAgent)
    invoke(StructureRecognitionAgent)

invoke(QRMetadataAgent)
invoke(PostProcessAgent)
return aggregate_and_validate()
```

### Image Processing Agent
**Role:** Prepares images for optimal extraction  
**Tools Used:**
- opencv-python
- PIL/Pillow
- numpy
- scikit-image

**Responsibilities:**
- Image quality assessment
- Noise reduction and denoising
- Contrast enhancement
- Perspective correction
- Deskewing and rotation correction
- Background normalization
- Border detection and cropping

**Output:** Optimized image ready for text extraction

### Separation Agent
**Role:** Detects and isolates multiple content regions  
**Tools Used:**
- opencv-python (contour detection)
- numpy
- scikit-learn (clustering)

**Responsibilities:**
- Detect multiple sticky notes or content regions in single image
- Apply contour detection and connected component analysis
- Separate overlapping or touching notes using edge detection
- Extract individual note boundaries with bounding boxes
- Assign unique identifiers to each separated region
- Determine spatial relationships (top-left, bottom-right, etc.)
- Handle edge cases (partial notes, shadows, skewed angles)

**Output:** Array of separated image regions with bounding box metadata

### Text Extraction Agent
**Role:** Primary handwriting recognition using hybrid approach  
**Tools Used:**
- pytesseract (traditional OCR)
- GPT-4-Vision/GPT-5-mini (vision LLM)
- Custom handwriting models (optional)

**Responsibilities:**
- Run traditional OCR (pytesseract) as first pass
- Send image to vision LLM for AI-based text extraction
- Compare results from both approaches
- Use LLM output as ground truth for difficult cases
- Maintain character-level confidence scores from both sources
- Handle multiple languages and handwriting styles
- Preserve line breaks, spacing, and formatting

**Processing Strategy:**
1. Quick OCR pass with pytesseract (fast, lower accuracy)
2. Vision LLM pass with GPT-4-Vision (slower, higher accuracy)
3. Confidence comparison and result selection
4. Hybrid result generation using best elements from each

**Output:** Raw text with confidence scores and source attribution

### Structure Recognition Agent
**Role:** Identifies semantic patterns and document structure  
**Tools Used:**
- regex pattern matching
- GPT-4-Vision/GPT-5-mini for visual structure
- Custom parsing logic

**Responsibilities:**
- Identify titles marked with double hash marks (## TITLE ##)
- Detect bulleted lists (visual bullets or text markers)
- Detect numbered lists with sequential numbering
- Recognize to-do items (open box □ or visual checkboxes)
- Extract key-value tags formatted as ::key:value
- Extract simple tags with @ symbol (@tag)
- Preserve indentation and hierarchy
- Identify headers, subheaders, and sections
- Detect tables or structured data layouts

**Pattern Recognition:**
```
Title Pattern: /##\s*(.+?)\s*##/
Bullet Pattern: /^[\s]*[•\-\*]\s+/
Numbered Pattern: /^[\s]*\d+[\.\)]\s+/
ToDo Pattern: /^[\s]*\[[\s\?x]\]\s+/ or visual checkbox
KeyValue Pattern: /::([a-zA-Z0-9_]+):([^\s]+)/
SimpleTag Pattern: /@([a-zA-Z0-9_]+)/
```

**Output:** Structured representation of document organization

### QR/Metadata Agent
**Role:** Extracts non-textual information  
**Tools Used:**
- pyzbar (QR/barcode scanning)
- opencv-python (color analysis)
- exif readers

**Responsibilities:**
- Scan for QR codes using pyzbar
- Decode QR content and validate format
- Extract color information (dominant colors, background color)
- Detect physical note color (yellow, blue, pink, etc.)
- Read EXIF metadata from image
- Extract timestamp, device info, GPS if available
- Identify special markers or symbols

**Output:** Metadata dictionary with QR results, colors, and image properties

### Post-Process Agent
**Role:** Intelligent text correction and enhancement  
**Tools Used:**
- GPT-4/GPT-5-mini for contextual understanding
- Language models for spell checking
- Custom correction logic

**Responsibilities:**
- Analyze raw text for likely OCR errors
- Use contextual understanding to identify improbable words
- Correct common OCR mistakes (l vs I, 0 vs O, etc.)
- Fix spacing and punctuation errors
- Normalize formatting inconsistencies
- Validate and correct proper nouns
- Maintain original meaning while improving readability
- Generate both raw and formatted versions of text

**Correction Strategy:**
```
1. Identify low-confidence words from extraction phase
2. Build context window around each uncertain word
3. Query LLM: "Given context X, is word Y correct?"
4. Apply corrections with annotation
5. Generate clean formatted version
6. Preserve raw version for user reference
```

**Output:** Raw text, formatted text, and correction annotations

---

# Agent Core System Design

## Orchestrator Agent Implementation

### Core Responsibilities

The Orchestrator Agent serves as the central intelligence coordinating all processing activities. It makes high-level decisions about:

**Processing Strategy Selection**
- Single note vs multiple notes
- Simple vs complex content
- High-quality vs low-quality images
- Text-heavy vs diagram-heavy content

**Agent Invocation Sequencing**
```python
class OrchestratorAgent:
    def process(self, image_path: str, options: dict) -> dict:
        # Phase 1: Initial analysis
        image_analysis = self.analyze_image(image_path)
        
        # Phase 2: Separation if needed
        if image_analysis.contains_multiple_notes:
            separated_notes = self.separation_agent.separate(image_path)
        else:
            separated_notes = [image_path]
        
        # Phase 3: Process each note
        results = []
        for note_image in separated_notes:
            # Preprocessing
            processed_img = self.image_processing_agent.process(note_image)
            
            # Parallel extraction
            ocr_result = self.text_extraction_agent.extract_ocr(processed_img)
            llm_result = self.text_extraction_agent.extract_llm(processed_img)
            qr_metadata = self.qr_metadata_agent.extract(processed_img)
            
            # Merge text results
            merged_text = self.merge_extraction_results(ocr_result, llm_result)
            
            # Structure recognition
            structure = self.structure_recognition_agent.analyze(
                merged_text, 
                processed_img
            )
            
            # Post-processing
            final_text = self.post_process_agent.correct(
                merged_text, 
                structure
            )
            
            # Compile note result
            note_result = {
                "note_id": note_image.id,
                "raw_text": merged_text,
                "formatted_text": final_text,
                "structure": structure,
                "metadata": qr_metadata,
                "confidence": self.calculate_confidence(ocr_result, llm_result)
            }
            results.append(note_result)
        
        # Phase 4: Aggregation
        return self.compile_final_output(results, image_analysis)
```

### Decision Logic

**When to use expensive LLM calls:**
- Low OCR confidence scores (< 0.7)
- Handwriting detected (vs printed text)
- Complex layouts or diagrams
- User explicitly requests high-accuracy mode
- Initial pass identifies uncertain regions

**When to use traditional tools:**
- High-quality printed text
- Simple layouts
- QR codes and barcodes
- Color and metadata extraction
- Quick preview mode

**Parallel vs Sequential Processing:**
- Parallel: OCR + QR scanning (independent tasks)
- Sequential: Image processing → text extraction (dependent tasks)
- Parallel: Multiple separated notes (independent)
- Sequential: Raw text → structure recognition → post-processing (dependent)

### Error Handling Strategy

```python
class OrchestratorAgent:
    def handle_agent_error(self, agent_name: str, error: Exception):
        if agent_name == "TextExtractionAgent":
            # Fallback to LLM-only mode
            return self.fallback_to_llm_extraction()
        elif agent_name == "SeparationAgent":
            # Process as single image
            return self.process_as_single_image()
        elif agent_name == "PostProcessAgent":
            # Return unprocessed text with warning
            return self.return_raw_with_warning()
        else:
            # Log and continue with partial results
            self.log_error(agent_name, error)
            return self.partial_success_response()
```

---

# Technical Requirements

## Core Dependencies

### Computer Vision & Image Processing
```python
opencv-python>=4.8.0
opencv-contrib-python>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0
scikit-image>=0.21.0
```

### OCR & Text Recognition
```python
pytesseract>=0.3.10
# Requires Tesseract binary installation
# Tesseract 5.0+ recommended for best results
```

### QR Code & Barcode Processing
```python
pyzbar>=0.1.9
# Requires libzbar
# On Ubuntu: apt-get install libzbar0
# On macOS: brew install zbar
```

### Vision LLM Integration
```python
openai>=1.3.0  # For GPT-4-Vision / GPT-5-mini
anthropic>=0.5.0  # Alternative: Claude with vision
```

### Supporting Libraries
```python
requests>=2.31.0
aiohttp>=3.9.0  # For async LLM calls
pydantic>=2.4.0  # Schema validation
jsonschema>=4.19.0  # JSON output validation
```

## System Requirements

**Minimum Specifications**
- CPU: 2+ cores, 2.0 GHz+
- RAM: 4GB minimum, 8GB recommended
- Storage: 500MB for libraries, 2GB for models
- Python: 3.9+

**Optimal Specifications**
- CPU: 4+ cores, 3.0 GHz+
- RAM: 16GB+
- GPU: Optional but beneficial for CV operations
- Storage: 5GB+ for caching and models

## Environment Configuration

```yaml
# config.yaml
orchestrator:
  max_concurrent_agents: 4
  timeout_seconds: 60
  retry_attempts: 3

image_processing:
  max_image_size: 4096x4096
  min_image_size: 100x100
  supported_formats: [jpg, jpeg, png, webp, tiff]
  preprocessing:
    denoise: true
    enhance_contrast: true
    auto_rotate: true

text_extraction:
  ocr_engine: tesseract
  tesseract_config: "--psm 6 --oem 3"
  llm_model: gpt-4-vision-preview
  llm_temperature: 0.0
  hybrid_mode: true
  confidence_threshold: 0.7

separation:
  min_note_size: 50x50
  max_notes_per_image: 20
  overlap_threshold: 0.1
  contour_method: external

qr_scanning:
  enabled: true
  scanner: pyzbar
  try_rotation: true
  max_qr_per_image: 10

post_processing:
  enabled: true
  llm_model: gpt-4-turbo
  correction_mode: contextual
  preserve_raw: true
```

---

# Image Processing Pipeline

## Stage 1: Image Ingestion & Validation

**Input Validation**
```python
def validate_image(image_path: str) -> ImageValidation:
    """Validate image meets processing requirements"""
    checks = {
        "format": check_supported_format(image_path),
        "size": check_image_dimensions(image_path),
        "corruption": check_image_integrity(image_path),
        "file_size": check_reasonable_file_size(image_path)
    }
    return ImageValidation(**checks)
```

**Validation Criteria**
- Format: Must be JPEG, PNG, WEBP, or TIFF
- Dimensions: Minimum 100x100, maximum 4096x4096 pixels
- File size: Maximum 25MB
- Integrity: Must be valid, non-corrupted image file
- Color space: RGB or grayscale (convert CMYK if needed)

## Stage 2: Preprocessing

**Noise Reduction**
```python
def denoise_image(image: np.ndarray) -> np.ndarray:
    """Apply non-local means denoising"""
    if is_color(image):
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    else:
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
```

**Contrast Enhancement**
```python
def enhance_contrast(image: np.ndarray) -> np.ndarray:
    """Apply CLAHE for adaptive contrast enhancement"""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    if is_color(image):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    else:
        return clahe.apply(image)
```

**Deskewing**
```python
def deskew_image(image: np.ndarray) -> tuple[np.ndarray, float]:
    """Detect and correct image skew/rotation"""
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                            flags=cv2.INTER_CUBIC,
                            borderMode=cv2.BORDER_REPLICATE)
    
    return rotated, angle
```

**Binarization**
```python
def binarize_for_ocr(image: np.ndarray) -> np.ndarray:
    """Convert to optimal binary image for OCR"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if is_color(image) else image
    
    # Adaptive thresholding works best for varied lighting
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    
    return binary
```

## Stage 3: Quality Assessment

```python
def assess_image_quality(image: np.ndarray) -> QualityMetrics:
    """Evaluate image quality for OCR readiness"""
    
    # Blur detection using Laplacian variance
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if is_color(image) else image
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = laplacian_var / 100.0  # Normalize
    
    # Contrast measurement
    contrast = gray.std()
    
    # Brightness check
    brightness = gray.mean()
    
    # Resolution adequacy
    height, width = gray.shape
    resolution_score = min(1.0, (height * width) / (1000 * 1000))
    
    return QualityMetrics(
        blur_score=blur_score,
        contrast_score=contrast / 127.5,  # Normalize to 0-2
        brightness_score=brightness / 255.0,
        resolution_score=resolution_score,
        overall_quality=calculate_overall_quality(
            blur_score, contrast, brightness, resolution_score
        )
    )
```

---

# Vision LLM Integration

## GPT-4-Vision / GPT-5-mini Configuration

### API Integration

```python
from openai import OpenAI

class VisionLLMAgent:
    def __init__(self, api_key: str, model: str = "gpt-4-vision-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def extract_text(self, image_path: str, prompt_type: str = "standard") -> dict:
        """Extract text from image using vision LLM"""
        
        # Convert image to base64
        base64_image = self.encode_image(image_path)
        
        # Select appropriate prompt
        prompt = self.get_prompt(prompt_type)
        
        # Make API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            temperature=0.0,
            max_tokens=4096
        )
        
        return self.parse_llm_response(response)
```

### Prompt Engineering

**Standard Text Extraction Prompt**
```python
STANDARD_EXTRACTION_PROMPT = """
You are an expert at reading handwritten notes from images. 

Task: Extract ALL text from this image with perfect accuracy.

Requirements:
1. Preserve exact spelling, even if words seem misspelled
2. Maintain original line breaks and spacing
3. Keep all punctuation marks
4. Preserve capitalization as written
5. If text is unclear, provide your best interpretation
6. Note any regions where text is illegible

Format your response as:
TEXT: <extracted text here>
CONFIDENCE: <high/medium/low>
ILLEGIBLE_REGIONS: <descriptions of any unclear areas>
"""
```

**Structure-Aware Extraction Prompt**
```python
STRUCTURE_EXTRACTION_PROMPT = """
You are an expert at reading and understanding structured handwritten notes.

Task: Extract text AND identify the document structure.

Look for and mark:
1. Titles enclosed in ## TITLE ## markers
2. Bulleted lists (any bullet style)
3. Numbered lists (1. 2. 3. or 1) 2) 3) etc.)
4. Checkboxes or to-do items (empty boxes that indicate tasks)
5. Tags starting with @ symbol
6. Key-value pairs formatted as ::key:value
7. Headers, subheaders, sections

Provide response as structured JSON:
{
  "raw_text": "complete text as written",
  "title": "detected title if any",
  "has_lists": true/false,
  "has_todos": true/false,
  "has_tags": true/false,
  "structure_notes": "description of document organization"
}
"""
```

**Correction-Focused Prompt**
```python
CORRECTION_PROMPT = """
You are an expert at identifying and correcting OCR errors while preserving meaning.

Original OCR text:
{ocr_text}

Task: Identify likely OCR errors and provide corrections.

Common OCR mistakes to look for:
- "l" (lowercase L) vs "I" (uppercase i) vs "1" (one)
- "O" (letter) vs "0" (zero)
- "rn" vs "m"
- "vv" vs "w"
- Missing or extra spaces
- Punctuation errors

Provide response as:
{
  "corrected_text": "text with corrections applied",
  "corrections": [
    {"original": "word", "corrected": "word", "reason": "explanation"}
  ],
  "confidence": "high/medium/low"
}

Only make corrections you are confident about. When uncertain, preserve original.
"""
```

### Response Parsing

```python
def parse_llm_response(self, response) -> ExtractionResult:
    """Parse and structure LLM response"""
    
    content = response.choices[0].message.content
    
    # Extract text content
    text_match = re.search(r'TEXT:\s*(.+?)(?=CONFIDENCE:|$)', 
                          content, re.DOTALL)
    text = text_match.group(1).strip() if text_match else content
    
    # Extract confidence
    conf_match = re.search(r'CONFIDENCE:\s*(high|medium|low)', 
                          content, re.IGNORECASE)
    confidence = conf_match.group(1).lower() if conf_match else "medium"
    
    # Extract illegible regions
    illegible_match = re.search(r'ILLEGIBLE_REGIONS:\s*(.+?)$', 
                               content, re.DOTALL)
    illegible = illegible_match.group(1).strip() if illegible_match else None
    
    return ExtractionResult(
        text=text,
        confidence=confidence,
        illegible_regions=illegible,
        model=self.model,
        tokens_used=response.usage.total_tokens
    )
```

## Hybrid OCR + LLM Strategy

### Decision Framework

```python
def select_extraction_strategy(self, 
                               image_quality: QualityMetrics,
                               user_settings: dict) -> str:
    """Determine optimal extraction approach"""
    
    # Force LLM if user requests high accuracy
    if user_settings.get('accuracy_mode') == 'high':
        return 'llm_only'
    
    # Use hybrid for handwriting
    if self.detect_handwriting(image):
        return 'hybrid'
    
    # Use OCR only for high-quality printed text
    if (image_quality.overall_quality > 0.8 and 
        not self.detect_handwriting(image)):
        return 'ocr_only'
    
    # Default to hybrid
    return 'hybrid'
```

### Hybrid Processing Implementation

```python
async def extract_hybrid(self, image_path: str) -> HybridResult:
    """Run OCR and LLM extraction in parallel, merge results"""
    
    # Launch both extractions simultaneously
    ocr_task = asyncio.create_task(self.extract_with_ocr(image_path))
    llm_task = asyncio.create_task(self.extract_with_llm(image_path))
    
    # Wait for both to complete
    ocr_result, llm_result = await asyncio.gather(ocr_task, llm_task)
    
    # Merge results with LLM as ground truth
    merged = self.merge_extraction_results(ocr_result, llm_result)
    
    return HybridResult(
        text=merged.text,
        confidence=self.calculate_hybrid_confidence(ocr_result, llm_result),
        ocr_version=ocr_result.text,
        llm_version=llm_result.text,
        differences=self.identify_differences(ocr_result, llm_result),
        extraction_method='hybrid'
    )

def merge_extraction_results(self, 
                            ocr: ExtractionResult, 
                            llm: ExtractionResult) -> str:
    """Merge OCR and LLM results, preferring LLM for conflicts"""
    
    # Use sequence matcher to align texts
    matcher = SequenceMatcher(None, ocr.text, llm.text)
    
    merged_text = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Both agree, use either
            merged_text.append(ocr.text[i1:i2])
        elif tag == 'replace':
            # Conflict: prefer LLM
            merged_text.append(llm.text[j1:j2])
        elif tag == 'delete':
            # OCR has extra text: check if it's noise
            if self.looks_like_noise(ocr.text[i1:i2]):
                continue  # Skip it
            else:
                merged_text.append(ocr.text[i1:i2])  # Keep it
        elif tag == 'insert':
            # LLM has extra text: trust it
            merged_text.append(llm.text[j1:j2])
    
    return ''.join(merged_text)
```

---

# Output Schema & JSON Structure

## Primary Output Schema

```json
{
  "version": "2.0",
  "processed_at": "2025-10-27T10:30:45Z",
  "processing_time_ms": 2847,
  "image_metadata": {
    "filename": "sticky_notes_scan.jpg",
    "original_dimensions": {
      "width": 3024,
      "height": 4032
    },
    "file_size_bytes": 2458624,
    "format": "JPEG",
    "color_space": "RGB"
  },
  "notes": [
    {
      "note_id": "note_001",
      "spatial_position": {
        "bounding_box": {
          "x": 120,
          "y": 340,
          "width": 800,
          "height": 600
        },
        "relative_position": "top_left",
        "rotation_angle": -2.3
      },
      "visual_metadata": {
        "dominant_color": {
          "rgb": [255, 248, 153],
          "hex": "#FFF899",
          "name": "yellow"
        },
        "background_color": {
          "rgb": [255, 253, 208],
          "hex": "#FFFDD0",
          "name": "light_yellow"
        },
        "estimated_note_type": "sticky_note",
        "physical_size_estimate": "3x3_inches"
      },
      "qr_codes": [
        {
          "data": "https://memorygraph.app/n/abc123",
          "type": "QR_CODE",
          "position": {
            "x": 700,
            "y": 500
          },
          "confidence": 1.0
        }
      ],
      "text_content": {
        "raw_text": "## Project Alpha ##\n\nObjectives:\n• Launch beta by Q1\n• Acquire 1000 users\n• Achieve $50K MRR\n\n[] Schedule team meeting\n[] Review budget\n[] Update roadmap\n\n@urgent @marketing\n::project:alpha\n::priority:high",
        "formatted_text": "## Project Alpha ##\n\nObjectives:\n• Launch beta by Q1\n• Acquire 1000 users  \n• Achieve $50K MRR\n\n☐ Schedule team meeting\n☐ Review budget\n☐ Update roadmap\n\n@urgent @marketing\nProject: alpha\nPriority: high",
        "extraction_method": "hybrid",
        "confidence_score": 0.92
      },
      "structure": {
        "title": {
          "text": "Project Alpha",
          "format": "double_hash",
          "position": "top"
        },
        "sections": [
          {
            "type": "paragraph",
            "content": "Objectives:",
            "line_start": 3
          },
          {
            "type": "bulleted_list",
            "items": [
              "Launch beta by Q1",
              "Acquire 1000 users",
              "Achieve $50K MRR"
            ],
            "line_start": 4,
            "line_end": 6
          },
          {
            "type": "todo_list",
            "items": [
              {
                "text": "Schedule team meeting",
                "completed": false,
                "line": 8
              },
              {
                "text": "Review budget",
                "completed": false,
                "line": 9
              },
              {
                "text": "Update roadmap",
                "completed": false,
                "line": 10
              }
            ]
          }
        ],
        "has_title": true,
        "has_lists": true,
        "has_todos": true,
        "has_tags": true
      },
      "tags": {
        "simple_tags": [
          "urgent",
          "marketing"
        ],
        "key_value_tags": {
          "project": "alpha",
          "priority": "high"
        }
      },
      "entities": {
        "dates": ["Q1"],
        "numbers": ["1000", "50K"],
        "monetary_values": ["$50K"],
        "people": [],
        "organizations": []
      },
      "quality_metrics": {
        "image_quality": 0.87,
        "text_clarity": 0.92,
        "ocr_confidence": 0.89,
        "llm_confidence": 0.95,
        "overall_confidence": 0.92
      },
      "processing_details": {
        "preprocessing_applied": [
          "denoise",
          "contrast_enhancement",
          "deskew"
        ],
        "ocr_engine": "tesseract_5.0",
        "llm_model": "gpt-4-vision-preview",
        "llm_tokens_used": 1247,
        "post_processing_corrections": 3
      }
    }
  ],
  "summary": {
    "total_notes": 1,
    "total_todos": 3,
    "total_tags": 4,
    "total_qr_codes": 1,
    "average_confidence": 0.92,
    "processing_status": "success"
  },
  "errors": [],
  "warnings": [
    "Note rotation detected and corrected: -2.3 degrees"
  ]
}
```

## Schema Validation

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class SpatialPosition(BaseModel):
    bounding_box: BoundingBox
    relative_position: str
    rotation_angle: float

class RGBColor(BaseModel):
    rgb: List[int]
    hex: str
    name: str

class VisualMetadata(BaseModel):
    dominant_color: RGBColor
    background_color: RGBColor
    estimated_note_type: str
    physical_size_estimate: Optional[str]

class QRCode(BaseModel):
    data: str
    type: str
    position: Dict[str, int]
    confidence: float

class TextContent(BaseModel):
    raw_text: str
    formatted_text: str
    extraction_method: str
    confidence_score: float

class Title(BaseModel):
    text: str
    format: str
    position: str

class TodoItem(BaseModel):
    text: str
    completed: bool
    line: int

class Section(BaseModel):
    type: str
    content: Optional[str] = None
    items: Optional[List] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None

class Structure(BaseModel):
    title: Optional[Title]
    sections: List[Section]
    has_title: bool
    has_lists: bool
    has_todos: bool
    has_tags: bool

class Tags(BaseModel):
    simple_tags: List[str]
    key_value_tags: Dict[str, str]

class Entities(BaseModel):
    dates: List[str]
    numbers: List[str]
    monetary_values: List[str]
    people: List[str]
    organizations: List[str]

class QualityMetrics(BaseModel):
    image_quality: float
    text_clarity: float
    ocr_confidence: float
    llm_confidence: float
    overall_confidence: float

class ProcessingDetails(BaseModel):
    preprocessing_applied: List[str]
    ocr_engine: str
    llm_model: str
    llm_tokens_used: int
    post_processing_corrections: int

class Note(BaseModel):
    note_id: str
    spatial_position: SpatialPosition
    visual_metadata: VisualMetadata
    qr_codes: List[QRCode]
    text_content: TextContent
    structure: Structure
    tags: Tags
    entities: Entities
    quality_metrics: QualityMetrics
    processing_details: ProcessingDetails

class ImageMetadata(BaseModel):
    filename: str
    original_dimensions: Dict[str, int]
    file_size_bytes: int
    format: str
    color_space: str

class Summary(BaseModel):
    total_notes: int
    total_todos: int
    total_tags: int
    total_qr_codes: int
    average_confidence: float
    processing_status: str

class ProcessingOutput(BaseModel):
    version: str = "2.0"
    processed_at: datetime
    processing_time_ms: int
    image_metadata: ImageMetadata
    notes: List[Note]
    summary: Summary
    errors: List[str] = []
    warnings: List[str] = []
```

---

# Content Recognition Patterns

## Title Detection

### Double Hash Pattern

**Visual Recognition:**
```python
def detect_title_visual(self, image: np.ndarray, text_regions: List) -> Optional[Title]:
    """Detect titles using visual patterns in image"""
    
    # Look for text surrounded by hash marks
    for region in text_regions:
        # Extract region
        roi = image[region.y:region.y+region.height, 
                   region.x:region.x+region.width]
        
        # Look for hash mark patterns on both sides
        left_hashes = self.detect_hash_marks(roi, 'left')
        right_hashes = self.detect_hash_marks(roi, 'right')
        
        if left_hashes and right_hashes:
            title_text = self.extract_text_between_marks(roi)
            return Title(
                text=title_text,
                format='double_hash',
                position=self.determine_position(region)
            )
    
    return None

def detect_hash_marks(self, roi: np.ndarray, side: str) -> bool:
    """Detect ## pattern visually"""
    # Look for two parallel vertical segments (hash marks)
    # This is more reliable than OCR for detecting the pattern
    
    if side == 'left':
        search_region = roi[:, :20]  # Left edge
    else:
        search_region = roi[:, -20:]  # Right edge
    
    edges = cv2.Canny(search_region, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 15, 
                           minLineLength=10, maxLineGap=5)
    
    if lines is not None and len(lines) >= 2:
        # Found multiple vertical lines (hash marks)
        return True
    
    return False
```

**Text Pattern Matching:**
```python
import re

TITLE_PATTERNS = [
    r'##\s*(.+?)\s*##',  # Standard: ## Title ##
    r'#\s*(.+?)\s*#',     # Alternative: # Title #
    r'=+\s*(.+?)\s*=+',   # Alternative: ==Title==
]

def extract_titles_from_text(text: str) -> List[str]:
    """Extract titles using regex patterns"""
    titles = []
    
    for pattern in TITLE_PATTERNS:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            title_text = match.group(1).strip()
            titles.append(title_text)
    
    return titles
```

**LLM-Assisted Detection:**
```python
def identify_title_with_llm(self, text: str) -> Optional[str]:
    """Use LLM to identify which line is likely the title"""
    
    prompt = f"""
    Analyze this text and identify which line is the title/heading:
    
    {text}
    
    Return ONLY the title text, or "NONE" if no clear title exists.
    """
    
    response = self.llm_client.query(prompt)
    title = response.strip()
    
    return title if title != "NONE" else None
```

## List Detection

### Bulleted Lists

**Pattern Recognition:**
```python
BULLET_PATTERNS = [
    r'^\s*[•●○◦▪▫■□]\s+(.+)$',  # Unicode bullets
    r'^\s*[-\*\+]\s+(.+)$',      # ASCII bullets
    r'^\s*>\s+(.+)$',             # Quote-style bullets
]

def extract_bulleted_lists(text: str) -> List[Dict]:
    """Extract all bulleted lists from text"""
    lists = []
    current_list = None
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        is_bullet = False
        bullet_text = None
        
        for pattern in BULLET_PATTERNS:
            match = re.match(pattern, line)
            if match:
                is_bullet = True
                bullet_text = match.group(1).strip()
                break
        
        if is_bullet:
            if current_list is None:
                current_list = {
                    'type': 'bulleted_list',
                    'items': [],
                    'line_start': i + 1
                }
            current_list['items'].append(bullet_text)
        else:
            if current_list:
                current_list['line_end'] = i
                lists.append(current_list)
                current_list = None
    
    # Catch list that continues to end of text
    if current_list:
        current_list['line_end'] = len(lines)
        lists.append(current_list)
    
    return lists
```

**Visual Detection:**
```python
def detect_bullets_visually(self, image: np.ndarray) -> List[BulletPoint]:
    """Detect bullet points using image analysis"""
    
    # Convert to binary
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find small circular or square contours (likely bullets)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bullets = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Bullets are small (5-50 pixels area)
        if 5 < area < 50:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Bullets are roughly square/circular
            if 0.7 < aspect_ratio < 1.3:
                # Check if there's text to the right
                text_region = image[y:y+h, x+w:x+w+500]
                if self.has_text(text_region):
                    bullets.append(BulletPoint(x=x, y=y, width=w, height=h))
    
    return bullets
```

### Numbered Lists

**Sequential Number Detection:**
```python
NUMBERED_PATTERNS = [
    r'^\s*(\d+)[\.)\]]\s+(.+)$',  # 1. Item or 1) Item or 1] Item
    r'^\s*\((\d+)\)\s+(.+)$',      # (1) Item
    r'^\s*(\d+)\s*[-–—]\s*(.+)$',  # 1 - Item
]

def extract_numbered_lists(text: str) -> List[Dict]:
    """Extract numbered lists and validate sequence"""
    lists = []
    current_list = None
    expected_number = 1
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        is_numbered = False
        number = None
        item_text = None
        
        for pattern in NUMBERED_PATTERNS:
            match = re.match(pattern, line)
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
                
                current_list['items'].append({
                    'number': number,
                    'text': item_text
                })
                expected_number = number + 1
            else:
                # Sequence broken, start new list
                if current_list:
                    current_list['line_end'] = i
                    lists.append(current_list)
                
                current_list = {
                    'type': 'numbered_list',
                    'items': [{'number': number, 'text': item_text}],
                    'line_start': i + 1
                }
                expected_number = number + 1
        else:
            if current_list:
                current_list['line_end'] = i
                lists.append(current_list)
                current_list = None
                expected_number = 1
    
    if current_list:
        current_list['line_end'] = len(lines)
        lists.append(current_list)
    
    return lists
```

## To-Do Item Detection

### Checkbox Pattern Recognition

**Text Patterns:**
```python
TODO_PATTERNS = [
    r'^\s*\[\s*\]\s+(.+)$',      # [ ] Task
    r'^\s*\[[\s?]\]\s+(.+)$',    # [?] Task (uncertain)
    r'^\s*\[[xX✓✔]\]\s+(.+)$',   # [x] Task (completed)
    r'^\s*☐\s+(.+)$',             # ☐ Task (Unicode checkbox)
    r'^\s*☑\s+(.+)$',             # ☑ Task (Unicode checked)
    r'^\s*○\s+(.+)$',             # ○ Task (circle)
    r'^\s*◉\s+(.+)$',             # ◉ Task (filled circle)
]

def extract_todos(text: str) -> List[TodoItem]:
    """Extract all to-do items from text"""
    todos = []
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for pattern in TODO_PATTERNS:
            match = re.match(pattern, line)
            if match:
                task_text = match.group(1).strip()
                
                # Determine if completed
                completed = any(marker in line for marker in ['[x]', '[X]', '[✓]', '[✔]', '☑', '◉'])
                
                todos.append(TodoItem(
                    text=task_text,
                    completed=completed,
                    line=i + 1
                ))
                break
    
    return todos
```

**Visual Checkbox Detection:**
```python
def detect_checkboxes_visually(self, image: np.ndarray) -> List[Checkbox]:
    """Detect checkboxes using computer vision"""
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find square contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    checkboxes = []
    for contour in contours:
        # Approximate contour to polygon
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        
        # Checkboxes are roughly square with 4 sides
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / h
            
            # Should be square-ish and small-medium size
            if 0.8 < aspect_ratio < 1.2 and 15 < w < 50:
                # Check if there's text to the right
                text_region = image[y:y+h, x+w:x+w+400]
                if self.has_text(text_region):
                    # Check if checkbox is filled (completed)
                    roi = binary[y:y+h, x:x+w]
                    fill_ratio = cv2.countNonZero(roi) / (w * h)
                    completed = fill_ratio > 0.3  # >30% filled = checked
                    
                    checkboxes.append(Checkbox(
                        x=x, y=y,
                        width=w, height=h,
                        completed=completed
                    ))
    
    return checkboxes
```

## Tag Extraction

### Simple Tags (@tag)

```python
def extract_simple_tags(text: str) -> List[str]:
    """Extract all @tag style tags"""
    
    # Pattern: @ followed by alphanumeric/underscore, word boundary after
    pattern = r'@([a-zA-Z0-9_]+)\b'
    
    matches = re.findall(pattern, text)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in matches:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique_tags.append(tag)
    
    return unique_tags
```

### Key-Value Tags (::key:value)

```python
def extract_keyvalue_tags(text: str) -> Dict[str, str]:
    """Extract all ::key:value style metadata tags"""
    
    # Pattern: :: followed by key, then :, then value (no spaces in value)
    pattern = r'::([a-zA-Z0-9_]+):([^\s:]+)'
    
    matches = re.findall(pattern, text)
    
    # Convert to dictionary (last value wins for duplicate keys)
    tags = {}
    for key, value in matches:
        tags[key.lower()] = value
    
    return tags
```

### Combined Tag Extraction

```python
def extract_all_tags(text: str) -> Tags:
    """Extract both simple and key-value tags"""
    
    simple_tags = extract_simple_tags(text)
    keyvalue_tags = extract_keyvalue_tags(text)
    
    return Tags(
        simple_tags=simple_tags,
        key_value_tags=keyvalue_tags
    )
```

---

# Post-Processing Intelligence

## Error Correction Strategy

### Common OCR Errors

```python
OCR_COMMON_MISTAKES = {
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

def identify_likely_errors(self, text: str, ocr_confidence: Dict) -> List[ErrorCandidate]:
    """Identify words that are likely OCR errors"""
    
    error_candidates = []
    words = text.split()
    
    for i, word in enumerate(words):
        # Check if word is in dictionary
        if not self.is_valid_word(word):
            # Low confidence + not in dictionary = likely error
            word_confidence = ocr_confidence.get(i, 0.5)
            
            if word_confidence < 0.8:
                # Find alternative interpretations
                alternatives = self.generate_alternatives(word)
                
                error_candidates.append(ErrorCandidate(
                    word=word,
                    position=i,
                    confidence=word_confidence,
                    alternatives=alternatives
                ))
    
    return error_candidates

def generate_alternatives(self, word: str) -> List[str]:
    """Generate alternative spellings based on OCR confusion matrix"""
    
    alternatives = set()
    
    # Try replacing each character with common confusions
    for i, char in enumerate(word):
        if char in OCR_COMMON_MISTAKES:
            for replacement in OCR_COMMON_MISTAKES[char]:
                alt_word = word[:i] + replacement + word[i+1:]
                if self.is_valid_word(alt_word):
                    alternatives.add(alt_word)
    
    # Try replacing character pairs
    for i in range(len(word) - 1):
        pair = word[i:i+2]
        if pair in OCR_COMMON_MISTAKES:
            for replacement in OCR_COMMON_MISTAKES[pair]:
                alt_word = word[:i] + replacement + word[i+2:]
                if self.is_valid_word(alt_word):
                    alternatives.add(alt_word)
    
    return list(alternatives)
```

### Contextual Correction with LLM

```python
def correct_with_context(self, text: str, error_candidates: List[ErrorCandidate]) -> CorrectionResult:
    """Use LLM to contextually correct identified errors"""
    
    if not error_candidates:
        return CorrectionResult(text=text, corrections=[])
    
    # Build correction prompt
    prompt = self.build_correction_prompt(text, error_candidates)
    
    # Query LLM
    response = self.llm_client.query(prompt, temperature=0.0)
    
    # Parse corrections
    corrections = self.parse_correction_response(response)
    
    # Apply corrections to text
    corrected_text = self.apply_corrections(text, corrections)
    
    return CorrectionResult(
        text=corrected_text,
        corrections=corrections,
        original_text=text
    )

def build_correction_prompt(self, text: str, errors: List[ErrorCandidate]) -> str:
    """Build prompt for LLM correction"""
    
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
```

### Correction Application

```python
def apply_corrections(self, text: str, corrections: List[Correction]) -> str:
    """Apply corrections to text"""
    
    # Sort corrections by position (reverse order to maintain indices)
    corrections.sort(key=lambda c: c.position, reverse=True)
    
    corrected_text = text
    for correction in corrections:
        # Only apply high-confidence corrections
        if correction.confidence > 0.8:
            corrected_text = corrected_text.replace(
                correction.original,
                correction.corrected,
                1  # Replace only first occurrence
            )
    
    return corrected_text
```

## Formatting Enhancement

### Text Normalization

```python
def normalize_text(self, raw_text: str) -> str:
    """Clean and normalize extracted text"""
    
    text = raw_text
    
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
```

### Markdown Formatting

```python
def generate_formatted_version(self, 
                                raw_text: str,
                                structure: Structure,
                                todos: List[TodoItem]) -> str:
    """Generate clean formatted version with markdown"""
    
    formatted_lines = []
    lines = raw_text.split('\n')
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Check if this line is a title
        if structure.title and structure.title.position == line_num:
            formatted_lines.append(f"## {structure.title.text} ##")
            continue
        
        # Check if this line is a to-do
        is_todo = False
        for todo in todos:
            if todo.line == line_num:
                checkbox = "☑" if todo.completed else "☐"
                formatted_lines.append(f"{checkbox} {todo.text}")
                is_todo = True
                break
        
        if is_todo:
            continue
        
        # Check if this line is part of a list
        if self.is_bullet_line(line):
            # Normalize bullet character
            formatted_lines.append(re.sub(r'^\s*[•●○◦▪▫■□\-\*\+]\s+', '• ', line))
            continue
        
        if self.is_numbered_line(line):
            # Keep numbered format
            formatted_lines.append(line)
            continue
        
        # Regular line
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)
```

---

# Multi-Note Separation Engine

## Detection Algorithm

### Primary Approach: Contour Detection

```python
def separate_notes(self, image_path: str) -> List[SeparatedNote]:
    """Detect and separate multiple sticky notes in image"""
    
    # Load image
    image = cv2.imread(image_path)
    original = image.copy()
    
    # Preprocess for separation
    preprocessed = self.preprocess_for_separation(image)
    
    # Find contours
    contours = self.find_note_contours(preprocessed)
    
    # Filter and validate contours
    valid_contours = self.filter_contours(contours, image.shape)
    
    # Handle overlapping notes
    separated_contours = self.handle_overlaps(valid_contours)
    
    # Extract individual notes
    notes = []
    for i, contour in enumerate(separated_contours):
        note_image = self.extract_note_region(original, contour)
        
        notes.append(SeparatedNote(
            note_id=f"note_{i+1:03d}",
            image=note_image,
            bounding_box=cv2.boundingRect(contour),
            contour=contour,
            spatial_position=self.determine_spatial_position(contour, image.shape)
        ))
    
    return notes

def preprocess_for_separation(self, image: np.ndarray) -> np.ndarray:
    """Prepare image for note detection"""
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Adaptive thresholding to handle lighting variations
    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )
    
    # Morphological operations to connect note regions
    kernel = np.ones((3, 3), np.uint8)
    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    return morph

def find_note_contours(self, binary_image: np.ndarray) -> List:
    """Find contours that likely represent notes"""
    
    # Find all contours
    contours, hierarchy = cv2.findContours(
        binary_image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    return contours
```

### Contour Filtering

```python
def filter_contours(self, contours: List, image_shape: tuple) -> List:
    """Filter contours to identify valid notes"""
    
    height, width = image_shape[:2]
    image_area = height * width
    
    valid_contours = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Size filters
        min_area = image_area * 0.01  # At least 1% of image
        max_area = image_area * 0.95  # At most 95% of image
        
        if not (min_area < area < max_area):
            continue
        
        # Aspect ratio filter (notes are generally rectangular)
        aspect_ratio = w / h
        if not (0.3 < aspect_ratio < 3.0):
            continue
        
        # Minimum dimensions
        if w < 50 or h < 50:
            continue
        
        # Shape approximation (notes should be roughly rectangular)
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        # Should have 4-8 corners (rectangular-ish)
        if not (4 <= len(approx) <= 8):
            continue
        
        valid_contours.append(contour)
    
    return valid_contours
```

### Overlap Handling

```python
def handle_overlaps(self, contours: List) -> List:
    """Separate overlapping notes using watershed or splitting"""
    
    # Check for overlaps
    overlapping_groups = self.find_overlapping_contours(contours)
    
    separated = []
    processed = set()
    
    for i, contour in enumerate(contours):
        if i in processed:
            continue
        
        # Check if this contour overlaps with others
        overlaps_with = overlapping_groups.get(i, [])
        
        if not overlaps_with:
            # No overlap, keep as-is
            separated.append(contour)
            processed.add(i)
        else:
            # Multiple notes overlapping, attempt separation
            group = [contour] + [contours[j] for j in overlaps_with]
            split_contours = self.split_overlapping_notes(group)
            separated.extend(split_contours)
            processed.add(i)
            processed.update(overlaps_with)
    
    return separated

def split_overlapping_notes(self, contours: List) -> List:
    """Use watershed or other techniques to split overlapping notes"""
    
    # Create combined mask
    mask = np.zeros(self.image_shape[:2], dtype=np.uint8)
    for contour in contours:
        cv2.drawContours(mask, [contour], -1, 255, -1)
    
    # Distance transform
    dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    
    # Find peaks (likely centers of notes)
    _, sure_fg = cv2.threshold(
        dist_transform,
        0.5 * dist_transform.max(),
        255, 0
    )
    
    # Find markers for watershed
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(mask, sure_fg)
    
    # Label markers
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    
    # Apply watershed
    if len(self.image_shape) == 3:
        markers = cv2.watershed(self.original_image, markers)
    
    # Extract separated contours from markers
    separated_contours = []
    for label in range(2, markers.max() + 1):
        mask = np.zeros(self.image_shape[:2], dtype=np.uint8)
        mask[markers == label] = 255
        
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if contours:
            separated_contours.append(contours[0])
    
    return separated_contours
```

### Spatial Positioning

```python
def determine_spatial_position(self, contour, image_shape: tuple) -> str:
    """Determine relative position of note in image"""
    
    height, width = image_shape[:2]
    x, y, w, h = cv2.boundingRect(contour)
    
    # Calculate center point
    center_x = x + w // 2
    center_y = y + h // 2
    
    # Divide image into 9 regions (3x3 grid)
    col = "left" if center_x < width / 3 else "center" if center_x < 2 * width / 3 else "right"
    row = "top" if center_y < height / 3 else "middle" if center_y < 2 * height / 3 else "bottom"
    
    if row == "middle" and col == "center":
        return "center"
    elif row == "middle":
        return col
    elif col == "center":
        return row
    else:
        return f"{row}_{col}"
```

---

# Metadata Extraction System

## QR Code Detection & Decoding

```python
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol

class QRCodeAgent:
    def scan_qr_codes(self, image_path: str) -> List[QRCode]:
        """Scan image for QR codes and barcodes"""
        
        image = cv2.imread(image_path)
        
        # Try multiple orientations if initial scan fails
        qr_codes = []
        
        for rotation in [0, 90, 180, 270]:
            rotated = self.rotate_image(image, rotation)
            detected = decode(rotated, symbols=[ZBarSymbol.QRCODE])
            
            for qr in detected:
                qr_codes.append(QRCode(
                    data=qr.data.decode('utf-8'),
                    type=qr.type,
                    position={'x': qr.rect.left, 'y': qr.rect.top},
                    confidence=1.0  # pyzbar doesn't provide confidence
                ))
        
        # Remove duplicates
        unique_qr_codes = self.deduplicate_qr_codes(qr_codes)
        
        return unique_qr_codes
    
    def rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by specified angle"""
        if angle == 0:
            return image
        
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        return rotated
```

## Color Analysis

```python
from sklearn.cluster import KMeans
from collections import Counter

class ColorAnalysisAgent:
    def extract_color_metadata(self, image_path: str) -> VisualMetadata:
        """Extract color information from note"""
        
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get dominant color
        dominant_color = self.get_dominant_color(image_rgb)
        
        # Get background color (likely the note color)
        background_color = self.get_background_color(image_rgb)
        
        # Estimate physical note type
        note_type = self.estimate_note_type(background_color)
        
        return VisualMetadata(
            dominant_color=dominant_color,
            background_color=background_color,
            estimated_note_type=note_type,
            physical_size_estimate=self.estimate_size(image.shape)
        )
    
    def get_dominant_color(self, image_rgb: np.ndarray, k: int = 5) -> RGBColor:
        """Find dominant color using k-means clustering"""
        
        # Reshape image to list of pixels
        pixels = image_rgb.reshape(-1, 3)
        
        # Cluster colors
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(pixels)
        
        # Find most common cluster
        labels = kmeans.labels_
        counts = Counter(labels)
        dominant_cluster = counts.most_common(1)[0][0]
        
        # Get RGB values
        dominant_rgb = kmeans.cluster_centers_[dominant_cluster].astype(int)
        
        return RGBColor(
            rgb=dominant_rgb.tolist(),
            hex=self.rgb_to_hex(dominant_rgb),
            name=self.rgb_to_name(dominant_rgb)
        )
    
    def get_background_color(self, image_rgb: np.ndarray) -> RGBColor:
        """Estimate background/note color by sampling edges"""
        
        h, w = image_rgb.shape[:2]
        
        # Sample pixels from edges (likely background)
        edge_pixels = []
        edge_pixels.extend(image_rgb[0, :, :].reshape(-1, 3))  # Top
        edge_pixels.extend(image_rgb[-1, :, :].reshape(-1, 3))  # Bottom
        edge_pixels.extend(image_rgb[:, 0, :].reshape(-1, 3))  # Left
        edge_pixels.extend(image_rgb[:, -1, :].reshape(-1, 3))  # Right
        
        edge_pixels = np.array(edge_pixels)
        
        # Get median color (more robust than mean)
        median_color = np.median(edge_pixels, axis=0).astype(int)
        
        return RGBColor(
            rgb=median_color.tolist(),
            hex=self.rgb_to_hex(median_color),
            name=self.rgb_to_name(median_color)
        )
    
    def rgb_to_hex(self, rgb: np.ndarray) -> str:
        """Convert RGB to hex"""
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    def rgb_to_name(self, rgb: np.ndarray) -> str:
        """Map RGB to common color name"""
        
        COLOR_NAMES = {
            'yellow': ([200, 200, 0], [255, 255, 180]),
            'pink': ([255, 150, 150], [255, 220, 220]),
            'blue': ([100, 150, 200], [180, 220, 255]),
            'green': ([150, 200, 150], [200, 255, 200]),
            'orange': ([255, 150, 50], [255, 220, 150]),
            'white': ([240, 240, 240], [255, 255, 255]),
            'gray': ([150, 150, 150], [200, 200, 200]),
        }
        
        for name, (lower, upper) in COLOR_NAMES.items():
            if all(lower[i] <= rgb[i] <= upper[i] for i in range(3)):
                return name
        
        return 'unknown'
    
    def estimate_note_type(self, background_color: RGBColor) -> str:
        """Estimate physical note type based on color"""
        
        color_name = background_color.name
        
        if color_name in ['yellow', 'pink', 'blue', 'green', 'orange']:
            return 'sticky_note'
        elif color_name in ['white']:
            return 'paper'
        else:
            return 'unknown'
```

---

# Error Handling & Confidence Scoring

## Confidence Calculation

```python
class ConfidenceScorer:
    def calculate_overall_confidence(self,
                                    image_quality: float,
                                    ocr_confidence: float,
                                    llm_confidence: float,
                                    structure_clarity: float) -> float:
        """Calculate weighted overall confidence score"""
        
        weights = {
            'image_quality': 0.20,
            'ocr_confidence': 0.30,
            'llm_confidence': 0.35,
            'structure_clarity': 0.15
        }
        
        overall = (
            image_quality * weights['image_quality'] +
            ocr_confidence * weights['ocr_confidence'] +
            llm_confidence * weights['llm_confidence'] +
            structure_clarity * weights['structure_clarity']
        )
        
        return round(overall, 3)
    
    def assess_structure_clarity(self, structure: Structure) -> float:
        """Assess how clear the document structure is"""
        
        clarity_score = 0.5  # Base score
        
        # Clear title increases confidence
        if structure.has_title:
            clarity_score += 0.15
        
        # Presence of lists indicates structure
        if structure.has_lists:
            clarity_score += 0.15
        
        # Tags indicate intentional formatting
        if structure.has_tags:
            clarity_score += 0.10
        
        # To-dos show clear intent
        if structure.has_todos:
            clarity_score += 0.10
        
        return min(1.0, clarity_score)
```

## Error Handling

```python
class AgentErrorHandler:
    def handle_processing_error(self, 
                               error: Exception,
                               stage: str,
                               context: Dict) -> ErrorResponse:
        """Handle errors gracefully and determine recovery strategy"""
        
        error_info = {
            'stage': stage,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Determine severity
        severity = self.assess_error_severity(error, stage)
        
        # Determine if processing can continue
        can_continue = severity in ['low', 'medium']
        
        # Generate fallback strategy
        fallback = self.generate_fallback_strategy(stage, error)
        
        return ErrorResponse(
            error_info=error_info,
            severity=severity,
            can_continue=can_continue,
            fallback_strategy=fallback
        )
    
    def assess_error_severity(self, error: Exception, stage: str) -> str:
        """Assess how critical the error is"""
        
        critical_stages = ['image_loading', 'orchestration']
        high_priority_stages = ['text_extraction', 'separation']
        
        if stage in critical_stages:
            return 'critical'
        elif stage in high_priority_stages:
            return 'high'
        elif isinstance(error, (ValueError, TypeError)):
            return 'high'
        elif isinstance(error, (IOError, FileNotFoundError)):
            return 'critical'
        else:
            return 'medium'
    
    def generate_fallback_strategy(self, stage: str, error: Exception) -> Dict:
        """Generate recovery strategy for failed stage"""
        
        fallbacks = {
            'text_extraction': {
                'action': 'use_llm_only',
                'description': 'Skip OCR, use vision LLM exclusively'
            },
            'separation': {
                'action': 'process_as_single',
                'description': 'Treat entire image as single note'
            },
            'qr_scanning': {
                'action': 'skip',
                'description': 'Continue without QR code data'
            },
            'post_processing': {
                'action': 'use_raw',
                'description': 'Return unprocessed text'
            }
        }
        
        return fallbacks.get(stage, {
            'action': 'abort',
            'description': 'Cannot recover, abort processing'
        })
```

## Partial Success Handling

```python
def compile_partial_results(self, 
                           completed_stages: List[str],
                           failed_stages: List[str],
                           partial_data: Dict) -> PartialResult:
    """Compile results when some stages fail"""
    
    # Build result with available data
    result = {
        'status': 'partial_success',
        'completed_stages': completed_stages,
        'failed_stages': failed_stages,
        'warnings': []
    }
    
    # Add available data
    if 'text_extraction' in completed_stages:
        result['text_content'] = partial_data.get('text_content')
        result['warnings'].append('Text extracted successfully')
    else:
        result['warnings'].append('Text extraction failed')
    
    if 'structure_recognition' in completed_stages:
        result['structure'] = partial_data.get('structure')
    else:
        result['warnings'].append('Structure recognition unavailable')
    
    if 'qr_scanning' in failed_stages:
        result['warnings'].append('QR code scanning failed, no QR data available')
    
    # Calculate partial confidence
    result['confidence'] = self.calculate_partial_confidence(
        completed_stages,
        partial_data
    )
    
    return PartialResult(**result)
```

---

# Performance Requirements

## Speed Targets

**Processing Time Goals**

- **Single Note (Simple):** < 2 seconds
  - Image preprocessing: < 200ms
  - OCR pass: < 500ms
  - LLM extraction: < 1000ms
  - Post-processing: < 300ms

- **Single Note (Complex):** < 5 seconds
  - With full hybrid extraction and correction

- **Multiple Notes (2-3):** < 8 seconds
  - Separation: < 1 second
  - Parallel processing of notes

- **Multiple Notes (4-6):** < 15 seconds
  - With parallel agent execution

**Throughput Targets**

- **Minimum:** 10 images per minute (single threaded)
- **Target:** 30-50 images per minute (with parallelization)
- **Maximum:** 100+ images per minute (batch processing, multiple workers)

## Resource Requirements

**Memory**

- **Per Image Processing:** 100-500MB RAM
- **With LLM Loaded:** 2-4GB RAM (depends on model)
- **Concurrent Processing:** Scale linearly with number of parallel tasks

**CPU Utilization**

- **Preprocessing:** CPU intensive (OpenCV operations)
- **OCR:** CPU intensive (Tesseract)
- **LLM API Calls:** Network I/O bound
- **Ideal:** 4+ cores for parallel note processing

**API Rate Limits**

- **OpenAI GPT-4-Vision:**
  - Tier 1: 500 RPM (requests per minute)
  - Tier 2: 5000 RPM
  - Consider rate limiting and queuing

- **Cost Optimization:**
  - Use OCR first, LLM only when needed
  - Batch similar images
  - Cache results when possible

## Optimization Strategies

```python
class PerformanceOptimizer:
    def optimize_processing(self, notes: List[SeparatedNote]) -> List[Note]:
        """Optimize processing based on note characteristics"""
        
        # Classify notes by complexity
        simple_notes = []
        complex_notes = []
        
        for note in notes:
            if self.is_simple_note(note):
                simple_notes.append(note)
            else:
                complex_notes.append(note)
        
        # Process simple notes with fast path (OCR only)
        simple_results = self.process_simple_batch(simple_notes)
        
        # Process complex notes with full pipeline
        complex_results = self.process_complex_batch(complex_notes)
        
        return simple_results + complex_results
    
    def is_simple_note(self, note: SeparatedNote) -> bool:
        """Determine if note can use fast processing path"""
        
        # Check image quality
        quality = self.assess_image_quality(note.image)
        
        # Simple if high quality and appears to be printed text
        if quality.overall_quality > 0.85 and not self.detect_handwriting(note.image):
            return True
        
        return False
    
    async def process_parallel(self, notes: List[SeparatedNote]) -> List[Note]:
        """Process multiple notes in parallel"""
        
        # Create processing tasks
        tasks = [
            self.process_single_note(note)
            for note in notes
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any failures
        successful_results = [
            r for r in results
            if not isinstance(r, Exception)
        ]
        
        return successful_results
```

---

# Implementation Phases

## Phase 1: Core Agent System (Months 1-2)

**Goals:**
- Build orchestrator agent framework
- Implement basic image processing pipeline
- Deploy OCR + LLM hybrid extraction
- Create JSON output schema

**Deliverables:**

1. **Orchestrator Agent**
   - Task planning and coordination
   - Agent lifecycle management
   - Result aggregation

2. **Image Processing Agent**
   - Noise reduction
   - Contrast enhancement
   - Deskewing

3. **Text Extraction Agent**
   - Tesseract OCR integration
   - GPT-4-Vision integration
   - Hybrid result merging

4. **Output Generator**
   - JSON schema definition
   - Pydantic models
   - Validation system

**Success Metrics:**
- 80%+ accuracy on clean handwriting
- < 3 second processing for single notes
- Valid JSON output 100% of time

## Phase 2: Multi-Note & Structure (Months 2-3)

**Goals:**
- Implement note separation
- Add structure recognition
- Deploy QR code scanning
- Enhance metadata extraction

**Deliverables:**

1. **Separation Agent**
   - Contour detection
   - Overlap handling
   - Spatial positioning

2. **Structure Recognition Agent**
   - Title detection (## TITLE ##)
   - List identification
   - To-do extraction
   - Tag parsing

3. **QR/Metadata Agent**
   - pyzbar integration
   - Color analysis
   - EXIF extraction

**Success Metrics:**
- 90%+ correct note separation (2-4 notes)
- 85%+ structure recognition accuracy
- 95%+ QR code detection rate

## Phase 3: Intelligence & Correction (Month 4)

**Goals:**
- Implement post-processing agent
- Add contextual correction
- Enhance confidence scoring
- Optimize performance

**Deliverables:**

1. **Post-Process Agent**
   - Error identification
   - LLM-based correction
   - Text normalization
   - Formatted output generation

2. **Confidence System**
   - Multi-factor scoring
   - Granular confidence per field
   - Quality metrics

3. **Performance Optimization**
   - Parallel processing
   - Fast path for simple notes
   - API call optimization

**Success Metrics:**
- 50%+ reduction in OCR errors
- 90%+ overall accuracy
- < 8 seconds for 3-note images

## Phase 4: Production Hardening (Month 5)

**Goals:**
- Comprehensive error handling
- Monitoring and observability
- Scale testing
- Documentation

**Deliverables:**

1. **Error Handling**
   - Graceful degradation
   - Partial result handling
   - Retry logic

2. **Observability**
   - Agent performance metrics
   - Processing pipeline visibility
   - Error tracking

3. **Documentation**
   - API documentation
   - Agent architecture guide
   - Configuration guide
   - Troubleshooting guide

**Success Metrics:**
- 99%+ uptime
- < 0.1% unhandled errors
- Complete documentation

---

# Risk & Mitigation

## Technical Risks

### High-Priority Risks

**Risk 1: LLM API Costs Exceed Budget**

**Likelihood:** High  
**Impact:** High  
**Mitigation:**
- Implement smart routing (OCR first, LLM only when needed)
- Use cheaper models (GPT-4-turbo) for post-processing
- Cache results aggressively
- Consider local LLM options for simpler tasks
- Implement strict per-user quotas

**Risk 2: OCR Accuracy Insufficient for Handwriting**

**Likelihood:** Medium  
**Impact:** High  
**Mitigation:**
- Hybrid approach using both OCR and vision LLM
- Extensive preprocessing to improve image quality
- Use LLM as ground truth validator
- Allow manual correction feedback loop
- Consider fine-tuning OCR models

**Risk 3: Note Separation Fails on Complex Images**

**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:**
- Multiple separation algorithms (contour, watershed, ML-based)
- Fallback to processing as single note if separation uncertain
- Manual separation tool for difficult cases
- User feedback to improve algorithm
- Clear confidence scores on separation quality

### Medium-Priority Risks

**Risk 4: Processing Time Too Slow for Real-Time Use**

**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:**
- Aggressive parallelization of independent tasks
- Fast path for simple/high-quality images
- Progressive result delivery (quick preview, then full results)
- Edge processing for preprocessing steps
- Async API design

**Risk 5: JSON Output Schema Too Rigid**

**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Version the schema from day one
- Include extension points for custom fields
- Maintain backward compatibility
- Allow optional fields
- Provide schema migration tools

## Integration Risks

**Risk 6: Vision LLM API Changes or Deprecation**

**Likelihood:** Low  
**Impact:** High  
**Mitigation:**
- Abstract LLM interface, support multiple providers
- Can switch between OpenAI, Anthropic, local models
- Monitor provider announcements
- Maintain fallback processing path
- Keep OCR as always-available baseline

## Operational Risks

**Risk 7: User Privacy Concerns with Cloud Processing**

**Likelihood:** Medium  
**Impact:** High  
**Mitigation:**
- Transparent privacy policy
- Option for local processing (OCR only mode)
- End-to-end encryption
- No data retention beyond processing
- GDPR compliance
- User data deletion on request

---

*This PRD is a living document and will evolve as we develop the AI agent system.*

**Last Updated:** October 27, 2025  
**Version:** 2.0  
**Status:** Ready for Implementation
