# Troubleshooting Upload Issue - CORS and Braintrust Error

## Issue Summary
When processing notes from the CapturePage.tsx, there was a network error. The backend showed "internal server error" and the frontend showed:

```
Access to XMLHttpRequest at 'http://localhost:8001/api/v1/notes/upload' from origin 'http://localhost:3001' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Root Cause
The actual issue was **NOT** a CORS configuration problem. The CORS middleware was configured correctly to allow requests from `http://localhost:3001`.

The real problem was a bug in the `agent_service.py` file where `braintrust.log()` was being called with positional arguments (a dictionary) instead of keyword arguments.

### Error Location
The error occurred in `backend/app/services/agent_service.py` when processing notes with multi-note detection enabled.

### Specific Error
```python
# INCORRECT - This caused the error:
braintrust.log({"error": str(e)})

# CORRECT - Fixed version:
braintrust.log(error=str(e))
```

The Braintrust library requires keyword arguments, not a positional dictionary argument.

## Solution
Fixed all `braintrust.log()` calls throughout `agent_service.py` to use keyword arguments instead of positional dictionaries.

### Changes Made
1. Fixed `braintrust.log()` calls in `_process_with_braintrust()` method
2. Fixed `span.log()` calls in `_process_single_note_with_braintrust()` method
3. Changed all dictionary-style calls to keyword argument calls

## Why It Appeared as a CORS Error
When the backend crashed with the Braintrust TypeError, the CORS headers weren't being sent in the error response. This made the browser report a CORS error even though CORS was configured correctly.

## Verification
After the fix:
- Backend starts successfully without errors
- CORS headers are properly returned in responses
- Upload functionality works correctly

## Testing
To verify the fix works:
1. Upload a note from the CapturePage
2. Check that it processes without errors
3. Verify the note appears in the notes list

## Files Modified
- `backend/app/services/agent_service.py` - Fixed all Braintrust logging calls
