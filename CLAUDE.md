# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Local development with hot reload
uvicorn app.main:app --reload --port 8000

# Or use the start script
./start.sh
```

### Database Operations
```bash
# Run migrations (adds new columns to existing tables)
python migrate_db.py

# Initialize fresh database (creates all tables)
# This happens automatically on startup via app.main:startup_event

# Import/export bots (for backup or migration)
python export_bots.py          # Creates my_bots_backup.json
python import_bots.py backup.json
```

### System Dependencies for OCR
The platform supports OCR for scanned documents. System requirements:
```bash
# macOS
brew install tesseract poppler

# Ubuntu/Debian (for Railway deployment, see Aptfile)
sudo apt-get install tesseract-ocr poppler-utils
```

## Architecture Overview

### Request Flow

**Chat Request Flow:**
```
User → /api/chat/{bot_id} (chat.py)
  ↓
ChatService.chat() (chat_service.py)
  ↓
├─→ MemoryService.get_conversation_history() [if memory enabled]
├─→ QdrantService.search_with_text() [if RAG enabled]
│   └─→ EmbeddingService.embed_text() (OpenAI embeddings)
├─→ OCRService.extract_text() [if file uploaded]
└─→ AI Provider API (Anthropic/OpenAI)
  ↓
Response → MemoryService.add_message()
        → WebhookService.trigger_event()
```

### Multi-Provider AI Integration

The platform routes to different AI APIs based on model:

**Anthropic Claude:**
- Uses `anthropic` SDK
- All Claude models go through standard Messages API
- Supports vision (base64 image in message content array)

**OpenAI GPT-5:**
- GPT-5 models auto-detect and route to **Responses API** (not Chat Completions)
- Uses special parameters: `reasoning_effort`, `text_verbosity`
- Other models use standard Chat Completions API
- Detection logic in `chat_service.py:is_gpt5_model()`

### API Key Management System

The platform has **two API key systems**:

1. **Legacy (bot.api_key):** Direct API key stored per bot
2. **New (bot.api_key_id → APIKey):** Centralized API key management

**Fallback Chain in `ChatService.get_bot_api_key()`:**
```python
bot.api_key_ref.api_key          # New system (relationship)
→ bot.api_key                     # Legacy field
→ settings.default_<provider>_api_key  # Environment default
→ ValueError                      # No key available
```

When creating/updating bots, prefer using `api_key_id` to reference centralized keys.

### RAG (Retrieval Augmented Generation)

**Two RAG Modes:**

1. **Normal RAG (top_k chunks):**
   - Uses `bot.qdrant_top_k` (default: 5)
   - Searches for most relevant chunks via semantic similarity
   - Efficient for Q&A

2. **Full Document Mode:**
   - Triggered by `?full_document=filename.pdf` query parameter
   - Retrieves **ALL chunks** for that document (sorted by chunk_index)
   - Used for creating comprehensive outlines of large documents
   - See `OCR_QDRANT_GUIDE.md` for token recommendations

**Document Upload Flow:**
```
POST /api/documents/upload
  ↓
OCRService.detect_if_scanned()
  ↓ [if scanned]
OCRService.ocr_pdf() (Tesseract)
  ↓
DocumentService.chunk_text() (LangChain text splitter)
  ↓
EmbeddingService.embed_text() (for each chunk)
  ↓
QdrantService.upload_points() (stores vectors + metadata)
```

### Session Memory

Controlled per bot:
- `bot.enable_memory`: Enable/disable conversation history
- `bot.memory_max_messages`: Number of messages to include in context

Storage:
- Conversation → session_id (UUID)
- Message → role (user/assistant), content, rag_context

### Model-Specific Validation

`app/schemas/bot.py` contains `MODEL_MAX_TOKENS` dictionary mapping models to their max output limits:
- Claude Sonnet 4.5: 64,000 tokens
- GPT-5: 128,000 tokens
- Claude Opus 4.1: 32,000 tokens
- etc.

The `@field_validator('max_tokens')` enforces these limits to prevent API errors.

## Database Schema

**Core Tables:**
- `bots`: Bot configurations (provider, model, prompts, settings)
- `api_keys`: Centralized API key storage with encryption
- `conversations`: Chat sessions (linked to bot_id)
- `messages`: Individual messages (role, content, rag_context)
- `webhooks`: Webhook configurations for bot events

**Important Relationships:**
- `Bot.api_key_id` → `APIKey.id` (many-to-one)
- `Bot.id` → `Conversation.bot_id` (one-to-many)
- `Conversation.id` → `Message.conversation_id` (one-to-many)
- `Bot.id` → `Webhook.bot_id` (one-to-many)

**Migrations:**
The app uses a simple migration system in `migrate_db.py`:
- Checks for missing columns/tables
- Adds them with ALTER TABLE statements
- Runs automatically on startup via `app.main:startup_event()`

## Configuration

Environment variables (see `.env.example`):

**Required:**
- `DATABASE_URL`: SQLite (local) or PostgreSQL (production)
- Admin credentials: `ADMIN_PASSWORD`, `SECRET_KEY`

**Optional API Keys (can be set per bot instead):**
- `DEFAULT_ANTHROPIC_API_KEY`
- `DEFAULT_OPENAI_API_KEY`

**Qdrant (for RAG):**
- `QDRANT_URL`: Vector database endpoint
- `QDRANT_API_KEY`: If using hosted Qdrant

**Security:**
- `JWT_SECRET_KEY`: For API token generation
- `FIREBASE_PROJECT_ID`, `FIREBASE_CREDENTIALS_PATH`: For external auth integration

## Frontend Architecture

### Admin Dashboard (`app/static/admin.html`)
Single-page admin interface with vanilla JavaScript:
- Bot CRUD operations
- API key management (separate tab)
- Webhook configuration
- Analytics dashboard (Tier 1: basic metrics)
- Max tokens field has interactive help tooltip showing model limits

### Chat Interface (`app/static/chat.html`)
Embeddable chat widget:
- Full document mode toggle (when bot has Qdrant enabled)
- Auto-loads available documents from collection
- File upload support (images + documents)
- Markdown rendering with table support
- Suggestion chips (if enabled on bot)

## Special Features

### OCR for Scanned Documents
- Max upload: 25 MB (configured in `documents.py`)
- Auto-detects if PDF is scanned (<50 words/page threshold)
- Uses Tesseract OCR via `pytesseract`
- Processes at 300 DPI for quality
- See `OCR_QDRANT_GUIDE.md` for usage

### Full Document Mode for Outlines
When creating outlines from 50+ page documents:
- Use `?full_document=filename.pdf` parameter
- Recommended max_tokens: 16,384 (detailed) or 32,000 (comprehensive)
- Input cost: ~25-37K tokens for 50 pages
- See tooltip in admin UI for guidance

### Webhooks
Bots can trigger webhooks on events:
- `conversation_started`
- `message_sent`
- `message_received`
- `conversation_ended`

Payload includes: bot_id, bot_name, session_id, user_id, event data

### Analytics (Tier 1)
Basic metrics tracked per bot:
- Total conversations
- Total messages
- Average conversation length
- Usage over time

## Testing

No formal test suite currently. To test manually:

```bash
# Test bot creation/update
python test_bot_update.py

# Test database migration
python migrate_db.py

# Test import/export
python export_bots.py
python import_bots.py my_bots_backup.json
```

## Deployment

**Railway (Current Production):**
```bash
./push_to_railway.sh   # Uses Railway CLI
```

**Railway Configuration:**
- Procfile: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Aptfile: System dependencies (tesseract, poppler)
- Automatic migrations run on startup
- PostgreSQL database (via Railway add-on)

**Environment Variables for Production:**
- Set `DATABASE_URL` (Railway provides automatically)
- Set `API_BASE_URL` to your Railway domain
- Update `ALLOWED_ORIGINS` for CORS
- Set secure `SECRET_KEY` and `ADMIN_PASSWORD`

See `RAILWAY_DEPLOY.md` for detailed deployment guide.

## Key Files

**Service Layer (Business Logic):**
- `chat_service.py`: AI provider routing, message building, RAG integration
- `qdrant_service.py`: Vector search, document upload, full document retrieval
- `embedding_service.py`: OpenAI embeddings (text-embedding-3-small)
- `ocr_service.py`: Tesseract OCR, scanned PDF detection
- `document_service.py`: Text extraction, chunking (LangChain)
- `webhook_service.py`: Webhook dispatch with retries

**API Endpoints:**
- `chat.py`: Chat endpoint with file upload, RAG, full document mode
- `bots.py`: Bot CRUD operations
- `documents.py`: Document upload/management for RAG
- `api_keys.py`: Centralized API key management
- `webhooks.py`: Webhook CRUD
- `analytics.py`: Usage metrics

**Models & Schemas:**
- `models/bot.py`: SQLAlchemy Bot model with relationships
- `schemas/bot.py`: Pydantic validation with model-specific max_tokens limits
- `models/conversation.py`: Session and message storage

## Documentation

- `README.md`: Quick start and feature overview
- `CLAUDE_MODELS_GUIDE.md`: Complete Claude model specs, pricing, usage guide
- `GPT5_GUIDE.md`: GPT-5 integration details and Responses API
- `OCR_QDRANT_GUIDE.md`: Document upload workflow and token recommendations
- `RAILWAY_DEPLOY.md`: Production deployment guide

## Common Pitfalls

1. **LangChain Import Changes:** Use `langchain_core.documents` not `langchain.docstore.document` (post-0.3.0)

2. **GPT-5 Detection:** Must check model name contains "gpt-5" to route to Responses API vs Chat Completions API

3. **Max Tokens Validation:** Platform validates per-model limits in schema. Don't set higher than model supports.

4. **API Key Priority:** Understand the fallback chain. New `api_key_id` system preferred over legacy `api_key` field.

5. **Full Document Mode:** Requires proper `filename` parameter matching exact document name in Qdrant metadata.

6. **OCR System Dependencies:** Tesseract and poppler must be installed system-wide, not just Python packages.
