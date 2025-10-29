# LLM-Only Mode Configuration

## Summary
Changed the default OCR processing mode from `traditional` (OCR only) to `llm` (Vision LLM only) to get much better results from handwritten notes.

## What Changed

### Backend API (notes.py)
**Before:**
```python
ocr_mode: str = Form("traditional"),
```

**After:**
```python
ocr_mode: str = Form("llm"),  # Default to LLM only for better results
```

### Configuration (config.py)
**Before:**
```python
OCR_MODE: str = os.getenv("OCR_MODE", "traditional")
```

**After:**
```python
OCR_MODE: str = os.getenv("OCR_MODE", "llm")  # traditional, llm, or auto - default to LLM for better results
```

### Frontend (CapturePage.tsx)
**Before:**
```typescript
const [ocrMode, setOcrMode] = useState('traditional');
```

**After:**
```typescript
const [ocrMode, setOcrMode] = useState('llm');  // Default to LLM for better results
```

## How It Works Now

### LLM Mode (`ocr_mode = "llm"`)
- **Uses**: Vision LLM (GPT-4o-mini) ONLY
- **Skips**: Traditional Tesseract OCR completely
- **Pros**: 
  - Much better at reading handwritten text
  - Better at understanding context and structure
  - Handles messy handwriting gracefully
- **Cons**: 
  - Requires OpenAI API key with quota
  - Slower than OCR
  - Costs money per request

### Flow with LLM Mode
1. Image uploaded → Agent processing
2. Note separation (QR codes, contours, or Vision LLM)
3. For each note region:
   - **ExtractionAgent** calls Vision LLM to extract text (NO OCR)
   - **StructureRecognitionAgent** identifies titles, sections, lists
   - **PostProcessAgent** corrects any errors
   - **MetadataAgent** extracts QR codes, EXIF data
4. Returns clean, readable text

## Testing
To verify it's working:
1. Go to http://localhost:3001/capture
2. Upload an image with handwritten notes
3. The processed text should be readable (not gibberish like with OCR)
4. Check logs: Should see "Using LLM mode (Vision LLM only)" messages

## Requirements
- OpenAI API key with available quota must be in `.env.development`
- Without quota, it will fail and return empty results

## Rollback
If you want to use OCR again, change the defaults back to `"traditional"` in:
- `backend/app/api/api_v1/endpoints/notes.py` line 193
- `backend/app/core/config.py` line 37
- `frontend/src/pages/CapturePage.tsx` line 12

Or change the mode in the UI dropdown before uploading.

