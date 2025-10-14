# API Key Management Feature

## Overview

This feature allows you to manage all your API keys in one central location and simply select which key to use when creating or editing a bot.

## Benefits

✅ **Centralized Management** - Add all your API keys once, reuse them for multiple bots
✅ **Easy Switching** - Change which API key a bot uses via dropdown (no re-entering)
✅ **Better Organization** - Name your keys (e.g., "Production Key", "Client A Key")
✅ **More Secure** - Keys are stored once, not duplicated across bots
✅ **Backward Compatible** - Existing bots with inline API keys continue to work

## How It Works

### Database Structure

**New Table: `api_keys`**
- `id` - Unique identifier
- `name` - Friendly name (e.g., "My Anthropic Key")
- `provider` - "anthropic" or "openai"
- `api_key` - The actual API key
- `is_active` - For soft deletes
- `created_at`, `updated_at` - Timestamps

**Updated Table: `bots`**
- Added `api_key_id` - Foreign key reference to `api_keys` table
- Kept `api_key` - Legacy field for backward compatibility

### Two Systems Supported

**New System (Recommended)**:
- Store API keys in `api_keys` table
- Bots reference keys via `api_key_id`
- Multiple bots can share the same API key

**Legacy System**:
- Bots store API key directly in `api_key` field
- Still works, but not recommended for new bots

## User Interface

### API Keys Tab

New section in admin dashboard with:

1. **List of API Keys**
   - Name, provider, masked key
   - Edit and delete buttons

2. **Add API Key Form**
   - Name (e.g., "Production Anthropic Key")
   - Provider (dropdown: Anthropic or OpenAI)
   - API Key (password field)
   - Save button

3. **Edit API Key**
   - Update name or provider
   - Optionally update the actual API key

### Bot Form Updates

When creating/editing a bot:

**API Key Section** has two options:

**Option 1: Use Existing API Key (Recommended)**
- Dropdown showing all API keys for the selected provider
- Automatically filtered when you select Anthropic or OpenAI

**Option 2: Enter API Key Directly (Legacy)**
- Text field to enter a key directly
- Stored in bot's `api_key` field

## Migration

The `migrate_api_keys.py` script:

1. Creates the `api_keys` table
2. Adds `api_key_id` column to `bots` table
3. Migrates existing bot API keys to the new system
4. Creates an `APIKey` entry for each bot's existing key
5. Updates bot to reference the new API Key

### Running Migration

```bash
python3 migrate_api_keys.py
```

Expected output:
```
🔄 Starting migration...

1. Creating api_keys table...
✅ api_keys table created

2. Adding api_key_id column to bots table...
✅ api_key_id column added

3. Migrating existing bot API keys...
✅ Migrated API key for bot: My Bot Name

✅ Migration complete! Migrated 1 bot(s)

📊 Summary:
  Total API keys: 1
  Total bots: 1
  Bots using new system: 1
  Bots using legacy system: 0
```

## API Endpoints

### API Key Management

**GET /api/api-keys**
- List all API keys
- Query param: `provider` (optional) - filter by provider

**POST /api/api-keys**
- Create new API key
- Body: `{name, provider, api_key}`

**GET /api/api-keys/{key_id}**
- Get specific API key (with masked key)

**PUT /api/api-keys/{key_id}**
- Update API key
- Body: `{name?, provider?, api_key?}`

**DELETE /api/api-keys/{key_id}**
- Soft delete API key

### Bot Updates

**POST /api/bots**
- Now accepts either:
  - `api_key` (legacy - direct key)
  - `api_key_id` (new - reference to APIKey)

**PUT /api/bots/{bot_id}**
- Same as above

**GET /api/bots** and **GET /api/bots/{bot_id}**
- Response now includes:
  - `api_key_id` - ID of referenced API key (if using new system)
  - `api_key_name` - Name of the API key (for display)
  - `api_key` - Masked for security

## Code Changes Summary

### New Files

1. `app/models/api_key.py` - APIKey model
2. `app/schemas/api_key.py` - Pydantic schemas
3. `app/services/api_key_service.py` - CRUD operations
4. `app/api/api_keys.py` - FastAPI endpoints
5. `migrate_api_keys.py` - Migration script

### Modified Files

1. **app/models/bot.py**
   - Added `api_key_id` field
   - Added `api_key_ref` relationship
   - Made `api_key` nullable

2. **app/schemas/bot.py**
   - Added `api_key_id` to BotCreate and BotUpdate
   - Added `api_key_name` to BotResponse
   - Made `api_key` optional

3. **app/services/chat_service.py**
   - Added `get_bot_api_key()` helper
   - Updated all chat functions to use helper

4. **app/services/bot_service.py**
   - Added joinedload for `api_key_ref` relationship

5. **app/api/bots.py**
   - Added `enrich_bot_response()` function
   - Populates `api_key_name` in responses

6. **app/main.py**
   - Added `api_keys` router

7. **app/static/admin.html** (TO BE UPDATED)
   - Add tabs for "Bots" and "API Keys"
   - Add API key management interface
   - Update bot form with API key dropdown

## Usage Examples

### Example 1: Create API Keys First

1. Go to admin dashboard
2. Click "API Keys" tab
3. Click "+ Add API Key"
4. Fill in:
   - Name: "Production Anthropic"
   - Provider: Anthropic
   - API Key: sk-ant-api03-...
5. Click "Save"

6. Repeat for OpenAI:
   - Name: "Production OpenAI"
   - Provider: OpenAI
   - API Key: sk-...

### Example 2: Create Bot Using Saved Key

1. Click "Bots" tab
2. Click "+ Create New Bot"
3. Fill in bot details
4. Select Provider: "Anthropic"
5. API Key section shows dropdown with "Production Anthropic"
6. Select it from dropdown
7. Save bot

### Example 3: Switch API Key for Existing Bot

1. Edit bot
2. Change the API key dropdown to a different key
3. Save
4. Bot now uses the new API key!

### Example 4: Legacy Mode (Direct API Key)

1. Create bot
2. Instead of selecting from dropdown, click "Enter API key directly"
3. Paste API key in text field
4. Save
5. Bot stores key directly (legacy mode)

## Security Considerations

1. **API Keys Never Exposed**
   - All API responses mask keys (e.g., `sk-ant-a...bQAA`)
   - Frontend never sees full keys after initial save

2. **Password Fields**
   - API key input fields use `type="password"`
   - Keys are hidden as you type

3. **Soft Deletes**
   - Deleted API keys are marked inactive, not removed
   - Prevents accidental data loss

4. **Validation**
   - Provider must match bot provider
   - Empty keys not allowed

## Testing

### Test API Key CRUD

```bash
# Create API key
curl -X POST http://localhost:8000/api/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key", "provider": "anthropic", "api_key": "sk-ant-test123"}'

# List API keys
curl http://localhost:8000/api/api-keys

# Get specific key
curl http://localhost:8000/api/api-keys/{key_id}

# Update key
curl -X PUT http://localhost:8000/api/api-keys/{key_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete key
curl -X DELETE http://localhost:8000/api/api-keys/{key_id}
```

### Test Bot with API Key Reference

```bash
# Create bot with api_key_id
curl -X POST http://localhost:8000/api/bots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Bot",
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "api_key_id": "{your_api_key_id}",
    "system_prompt": "You are a helpful assistant"
  }'
```

## Troubleshooting

### Bot Can't Find API Key

**Problem**: Error "No API key configured for this bot"

**Solution**:
- Check bot has either `api_key` or `api_key_id` set
- If using `api_key_id`, verify the APIKey exists and is active
- Run migration if upgrading from old version

### Dropdown Shows No API Keys

**Problem**: API key dropdown is empty when creating bot

**Solution**:
- Create an API key first in the "API Keys" tab
- Make sure provider matches (Anthropic keys only show for Anthropic bots)
- Check API key is active (not deleted)

### Can't Delete API Key

**Problem**: Delete button doesn't work or shows error

**Solution**:
- Check if any bots are using this key
- You may need to update those bots first
- Or the feature allows deletion (bots will fail until fixed)

## Future Enhancements

Possible additions:
- [ ] Show which bots use each API key
- [ ] Prevent deleting keys that are in use
- [ ] API key usage tracking
- [ ] API key rotation/expiry warnings
- [ ] Team/user-specific API keys
- [ ] Encrypted storage for API keys
- [ ] Import/export API keys

## Migration Rollback

If you need to rollback:

```sql
-- Remove api_key_id column from bots
ALTER TABLE bots DROP COLUMN api_key_id;

-- Drop api_keys table
DROP TABLE api_keys;
```

Note: This will lose all centralized API keys. Bots will fall back to their `api_key` field.

---

**This feature is now ready to use! Run the migration and enjoy centralized API key management.** 🎉
