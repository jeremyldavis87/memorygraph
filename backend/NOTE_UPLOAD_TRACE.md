# Note Upload Trace Analysis

## Test Image
- File: `backend/tests/test-files/26372.jpg`
- Size: 1,664,650 bytes
- Expected: 3x3 grid (9 notes)

## Issues Found

### 1. OpenAI API Key Not Configured
- **Location**: Local script execution
- **Impact**: Vision LLM calls fail immediately
- **Evidence**: `OPENAI_API_KEY configured: False`
- **Fix**: Ensure API key is loaded in container environment

### 2. Vision LLM Extraction Fails Silently
- **Location**: `extraction_agent.py` - `_extract_with_vision()`
- **Problem**: When Vision LLM fails in LLM-only mode, it returns empty text but doesn't fail hard
- **Impact**: Processing continues with empty/gibberish text
- **Current Behavior**:
  ```python
  if not vision_result.get("success"):
      return ExtractionResult(text="", confidence=0.0, ...)
  ```
- **Fix**: In LLM-only mode, return PartialResult on failure instead of empty ExtractionResult

### 3. Note Separation Issues
- **Detected**: Only 4 regions instead of 9
- **Method Used**: Contour detection (Vision LLM failed)
- **Root Cause**: Vision LLM detection failed due to missing API key
- **Fix**: Ensure Vision LLM detection works, or improve contour detection for 3x3 grids

### 4. OCR Mode Not Being Respected
- **UI Shows**: "OCR Mode: traditional"
- **Expected**: "OCR Mode: llm"
- **Root Cause**: `ocr_mode` from form may not be passed correctly, or falls back to OCR when LLM fails
- **Fix**: Ensure ocr_mode is passed through correctly and fail hard in LLM-only mode

## Flow Trace

1. **Upload Endpoint** (`notes.py:upload_note`)
   - Receives `ocr_mode="llm"` from form
   - Creates `NoteProcessingAgent` with user model
   - Config: `{"ocr_mode": "llm", ...}`

2. **Agent Service** (`agent_service.py:process_multi_note_image`)
   - Passes config to orchestrator
   - Config includes `ocr_mode: "llm"`

3. **Orchestrator** (`orchestrator_agent.py:process`)
   - Phase 1: Image preprocessing ✓
   - Phase 2: Note separation
     - QR detection: Disabled (pyzbar not available)
     - Contour detection: Found 4 regions ❌ (should be 9)
     - Vision LLM detection: Failed (API key not configured) ❌
   - Phase 3: Process each region
     - Extraction agent called with `ocr_mode="llm"`
     - Vision LLM extraction fails
     - Returns empty text
     - Processing continues with empty text ❌

4. **Extraction Agent** (`extraction_agent.py:_extract_parallel`)
   - Checks `ocr_mode == "llm"`
   - Calls `_extract_with_vision()`
   - Vision LLM fails
   - Returns `ExtractionResult(text="", confidence=0.0)`
   - Should return `PartialResult` in LLM-only mode on failure ❌

## Recommended Fixes

1. **Fail hard in LLM-only mode**: If Vision LLM fails when `ocr_mode="llm"`, return PartialResult
2. **Improve Vision LLM detection**: Ensure API key is configured and detection works
3. **Better contour detection**: For Rocketbook images, assume 3x3 grid if 9 QR codes detected
4. **Logging**: Add more detailed logging at each step

