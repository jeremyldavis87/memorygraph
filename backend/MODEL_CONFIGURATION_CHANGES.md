# Model Configuration Changes

## Summary
Updated all hardcoded model references to use `settings.AGENT_VISION_MODEL` from `.env.development` as the primary source.

## Files Updated

### 1. `backend/app/services/agents/extraction_agent.py`
- ✅ Added `from app.core.config import settings`
- ✅ Changed hardcoded `"gpt-5-mini"` to `settings.AGENT_VISION_MODEL`
- ✅ Updated default fallback in raw_data to use `settings.AGENT_VISION_MODEL`

### 2. `backend/app/services/agents/separation_agent.py`
- ✅ Added `from app.core.config import settings`
- ✅ Changed hardcoded `"gpt-5-mini"` to `settings.AGENT_VISION_MODEL`

### 3. `backend/app/services/agents/orchestrator_agent.py`
- ✅ Added `from app.core.config import settings`
- ✅ Changed hardcoded `"gpt-5-mini"` to use config with fallback: `config.get("vision_model_preference", settings.AGENT_VISION_MODEL)`

### 4. `backend/app/services/agent_service.py`
- ✅ Changed default parameter from `model_name: str = "gpt-5-mini"` to `model_name: str = None`
- ✅ Added fallback: `self.model_name = model_name or settings.AGENT_VISION_MODEL`

### 5. `backend/app/services/ai_service.py`
- ✅ Updated `process_with_vision_llm()` default from `"gpt-5-mini"` to `None` with fallback to `settings.AGENT_VISION_MODEL`
- ✅ Updated `extract_text_from_note_region()` default from `"gpt-5-mini"` to `None` with fallback to `settings.AGENT_VISION_MODEL`
- ✅ Updated `detect_note_regions_with_vision()` default from `"gpt-5-mini"` to `None` with fallback to `settings.AGENT_VISION_MODEL`

### 6. `backend/app/api/api_v1/endpoints/notes.py`
- ✅ Added `from app.core.config import settings`
- ✅ Added fallback: `user_model = current_user.vision_model_preference or settings.AGENT_VISION_MODEL`
- ✅ Uses `settings.AGENT_VISION_MODEL` if user preference is None

### 7. `backend/app/schemas/agent_schemas.py`
- ✅ Added `from app.core.config import settings`
- ✅ Changed `llm_model: str = "gpt-5-mini"` to `llm_model: str = Field(default_factory=lambda: settings.AGENT_VISION_MODEL)`

### 8. `backend/test_agent_processing.py`
- ✅ Updated test to use `NoteProcessingAgent()` without hardcoded model
- ✅ Updated config to use `settings.AGENT_VISION_MODEL`

## Configuration Priority

The model selection now follows this priority order:

1. **User Preference** (`current_user.vision_model_preference`) - if set
2. **Environment Variable** (`AGENT_VISION_MODEL` from `.env.development`) - default fallback
3. **Hardcoded Default** (`"gpt-5-mini"`) - only in config.py as ultimate fallback

## How to Change the Model

Simply update `.env.development`:
```bash
AGENT_VISION_MODEL=gpt-5
# or
AGENT_VISION_MODEL=gpt-4-vision-preview
# or any other OpenAI vision model
```

Then restart the backend container.

## Note on User Model Default

The `User.vision_model_preference` database column still has a default of `"gpt-5-mini"` for new users, but the code now falls back to `settings.AGENT_VISION_MODEL` if the user preference is `None`. This means:
- Existing users: Keep their preference
- New users: Get `settings.AGENT_VISION_MODEL` value
- Users with None preference: Get `settings.AGENT_VISION_MODEL` value

This is the desired behavior.

