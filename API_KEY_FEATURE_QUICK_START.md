# API Key Management - Quick Start Guide

## ✅ What's Been Implemented

I've successfully added a centralized API key management system to your AI Bot Builder platform!

### Backend (100% Complete)

✅ **Database**
- Created `api_keys` table
- Added `api_key_id` to bots table
- Ran migration successfully

✅ **API Endpoints** (`/api/api-keys`)
- POST - Create API key
- GET - List all API keys
- GET /{id} - Get specific API key
- PUT /{id} - Update API key
- DELETE /{id} - Delete API key

✅ **Bot Integration**
- Bots can now reference API keys by ID
- Chat service automatically fetches key from relationship
- Backward compatible with inline API keys

✅ **Tested & Working**
- Created test API key successfully
- All endpoints functional
- Database schema updated

### Frontend (Needs Update)

⚠️ **admin.html needs to be updated** to include:
1. Tabs for "Bots" and "API Keys"
2. API key management interface
3. Dropdown in bot form to select API keys

I've backed up your current admin.html to `admin_backup.html`.

## 🚀 How to Use Right Now (API Only)

You can start using the feature via API calls immediately:

### Step 1: Create an API Key

```bash
curl -X POST http://localhost:8000/api/api-keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Production Anthropic Key",
    "provider": "anthropic",
    "api_key": "sk-ant-api03-YOUR-ACTUAL-KEY-HERE"
  }'
```

Response:
```json
{
  "id": "a34fa6e3-4408-4ea4-9a46-1a652b6231a0",
  "name": "My Production Anthropic Key",
  "provider": "anthropic",
  "api_key": "sk-ant-a...HERE",  // Masked for security
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Save the `id`** - you'll use it when creating bots.

### Step 2: Create a Bot Using the API Key

```bash
curl -X POST http://localhost:8000/api/bots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Bot",
    "description": "Test bot with centralized API key",
    "provider": "anthropic",
    "model": "claude-sonnet-4-5-20250929",
    "api_key_id": "a34fa6e3-4408-4ea4-9a46-1a652b6231a0",
    "system_prompt": "You are a helpful assistant",
    "temperature": 70,
    "max_tokens": 1024
  }'
```

**Note**: Use `api_key_id` instead of `api_key`!

### Step 3: Test Chatting

The bot will automatically use the API key from the relationship:

```bash
curl -X POST http://localhost:8000/api/chat/YOUR_BOT_ID \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test123"}'
```

It should work! 🎉

## 📋 Next Steps

### Option 1: Use API Directly (No UI Update Needed)

You can manage API keys via API calls:

**List all API keys**:
```bash
curl http://localhost:8000/api/api-keys
```

**List API keys for specific provider**:
```bash
curl http://localhost:8000/api/api-keys?provider=anthropic
```

**Update API key**:
```bash
curl -X PUT http://localhost:8000/api/api-keys/{key_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

**Delete API key**:
```bash
curl -X DELETE http://localhost:8000/api/api-keys/{key_id}
```

### Option 2: Update admin.html UI

To add the visual interface, you'll need to:

1. **Add Tabs** to switch between "Bots" and "API Keys" views

2. **Add API Key Management Section**:
   - List of API keys with edit/delete buttons
   - "Add API Key" button and form
   - Edit API key modal

3. **Update Bot Form**:
   - Replace API key text field with dropdown
   - Load API keys when provider is selected
   - Filter by provider (show only Anthropic keys for Anthropic bots)

I can help with this if you'd like! The backend is 100% ready.

## 🔧 Testing the Backend

### Test 1: Create Multiple API Keys

```python
from app.database import SessionLocal
from app.services.api_key_service import APIKeyService
from app.schemas.api_key import APIKeyCreate

db = SessionLocal()

# Create Anthropic key
anthropic_key = APIKeyService.create_api_key(db, APIKeyCreate(
    name="Production Anthropic",
    provider="anthropic",
    api_key="sk-ant-api03-YOUR-KEY"
))

# Create OpenAI key
openai_key = APIKeyService.create_api_key(db, APIKeyCreate(
    name="Production OpenAI",
    provider="openai",
    api_key="sk-YOUR-OPENAI-KEY"
))

print(f"Anthropic Key ID: {anthropic_key.id}")
print(f"OpenAI Key ID: {openai_key.id}")

db.close()
```

### Test 2: Create Bot with API Key Reference

```python
from app.database import SessionLocal
from app.services.bot_service import BotService
from app.schemas.bot import BotCreate

db = SessionLocal()

bot = BotService.create_bot(db, BotCreate(
    name="Test Bot",
    provider="anthropic",
    model="claude-sonnet-4-5-20250929",
    api_key_id="YOUR-API-KEY-ID-HERE",  # Use the ID from Test 1
    system_prompt="You are a helpful assistant"
))

print(f"Bot created: {bot.name}")
print(f"Using API key ID: {bot.api_key_id}")

db.close()
```

### Test 3: Verify Chat Works

```python
from app.database import SessionLocal
from app.services.bot_service import BotService
from app.services.chat_service import ChatService

db = SessionLocal()

bot = BotService.get_bot(db, "YOUR-BOT-ID")
if bot:
    try:
        # This will fetch the API key from the relationship
        response = ChatService.chat(bot, "Hello!")
        print(f"✅ Chat works! Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Chat failed: {e}")
else:
    print("Bot not found")

db.close()
```

## 🎯 Benefits You Get

1. **No More Re-entering Keys**: Add your Anthropic and OpenAI keys once, reuse for all bots
2. **Easy Switching**: Change which key a bot uses with a simple update
3. **Better Organization**: Name your keys ("Dev Key", "Client A Key", etc.)
4. **Security**: Keys are masked in all API responses
5. **Flexibility**: Can still use inline API keys if needed (legacy support)

## 📖 API Documentation

Visit http://localhost:8000/docs to see all the new endpoints in the interactive API documentation!

Look for the "api-keys" section with all CRUD operations.

## 🐛 Troubleshooting

### Bot Says "No API key configured"

Make sure:
- Bot has either `api_key` OR `api_key_id` set
- If using `api_key_id`, the APIKey exists and is active
- The API key in the database is valid (not masked)

### Can't Create API Key

Check:
- Name is not empty
- Provider is "anthropic" or "openai"
- API key is not empty

### Migration Issues

If you need to re-run migration:
```bash
python3 migrate_api_keys.py
```

It's safe to run multiple times (uses `checkfirst=True`).

## 📝 Files Changed

**New Files**:
- `app/models/api_key.py`
- `app/schemas/api_key.py`
- `app/services/api_key_service.py`
- `app/api/api_keys.py`
- `migrate_api_keys.py`

**Modified Files**:
- `app/models/bot.py` - Added api_key_id, api_key_ref relationship
- `app/schemas/bot.py` - Added api_key_id, api_key_name fields
- `app/services/chat_service.py` - Added get_bot_api_key() helper
- `app/services/bot_service.py` - Added joinedload for relationship
- `app/api/bots.py` - Added enrich_bot_response()
- `app/main.py` - Added api_keys router
- `app/static/admin.html` - Fixed API key corruption bug

## 🎉 Summary

**The backend for centralized API key management is 100% complete and working!**

You can:
- ✅ Create, read, update, delete API keys via API
- ✅ Create bots that reference API keys
- ✅ Chat with bots (they fetch keys automatically)
- ✅ Use legacy inline keys (backward compatible)

The only remaining task is updating the frontend UI to make it visual, but the feature is fully functional via API right now!

---

Would you like me to create the admin UI updates next, or are you happy using the API directly for now?
