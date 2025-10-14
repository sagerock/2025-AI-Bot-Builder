# Fixing the 500 Error - Complete Guide

## The Problem

You're getting a 500 error when trying to chat with your bot. This is happening because:

1. **Your existing bot has a corrupted API key** (from the previous bug - only 15 characters instead of ~100)
2. **SQLAlchemy needs to know about the APIKey model** to load the relationship

## The Fix

I've made two changes:

### 1. Updated `app/database.py`

Added imports so SQLAlchemy knows about all models:

```python
def init_db():
    """Initialize database tables"""
    # Import all models so they are registered with SQLAlchemy
    from app.models.bot import Bot
    from app.models.conversation import Conversation, Message
    from app.models.api_key import APIKey  # NEW!

    Base.metadata.create_all(bind=engine)
```

### 2. Created Fix Script

Created `fix_bot_api_key.py` to help you:
- Add a valid API key to the system
- Update your existing bot to use it

## How to Fix

### Option 1: Use the Fix Script (Easiest)

1. **Stop your server** (Ctrl+C if it's running)

2. **Run the fix script**:
```bash
python3 fix_bot_api_key.py
```

3. **Enter your Anthropic API key** when prompted

4. **Restart your server**:
```bash
./start.sh
```

5. **Hard refresh your browser** (Ctrl+Shift+R or Cmd+Shift+R)

6. **Try chatting** - should work now!

### Option 2: Use the Admin UI

1. **Restart your server first** (so it picks up the database.py fix):
```bash
# Stop server (Ctrl+C)
./start.sh
```

2. **Go to admin**: http://localhost:8000/admin

3. **Click "API Keys" tab**

4. **Click "+ Add API Key"**:
   - Name: "Production Anthropic Key"
   - Provider: Anthropic
   - API Key: [Your actual key from https://console.anthropic.com/settings/keys]
   - Click "Save API Key"

5. **Click "Bots" tab**

6. **Click "Edit"** on your "Genghis Khan Expert" bot

7. **In API Key section**:
   - Select "Use existing API key" (radio button)
   - Select your new key from dropdown
   - Click "Save Bot"

8. **Hard refresh browser** (Ctrl+Shift+R)

9. **Try chatting** - should work!

### Option 3: Direct Database Fix (Advanced)

```bash
python3 << 'EOF'
from app.database import SessionLocal
from app.services.api_key_service import APIKeyService
from app.services.bot_service import BotService
from app.schemas.api_key import APIKeyCreate
from app.schemas.bot import BotUpdate

db = SessionLocal()

# Create API key
api_key = APIKeyService.create_api_key(db, APIKeyCreate(
    name="My Anthropic Key",
    provider="anthropic",
    api_key="sk-ant-api03-YOUR-ACTUAL-KEY-HERE"
))

# Update bot
BotService.update_bot(db, "eef34087-2222-4c6d-a9ab-1ccba4bb93e5", BotUpdate(
    api_key_id=api_key.id
))

db.close()
print(f"✅ Fixed! Bot now uses API key: {api_key.name}")
EOF
```

Then restart server.

## Why This Happened

### The Original Bug

When you edited your bot earlier, the API key field was populated with a **masked** value (e.g., `sk-ant-a...xyz`). When you saved, this masked value overwrote your real API key.

**This bug is now fixed** - the edit form no longer populates the API key field.

### The Current Error

Your bot now has:
- `api_key`: `sk-ant-a...bQAA` (corrupted - only 15 characters)
- `api_key_id`: NULL (not using new system yet)

So when the chat service tries to get the API key:
```python
def get_bot_api_key(bot: Bot) -> str:
    if bot.api_key_id and bot.api_key_ref:
        return bot.api_key_ref.api_key  # Not set
    elif bot.api_key:
        return bot.api_key  # Corrupted!
    else:
        raise ValueError("No API key configured")
```

It returns the corrupted key, which fails authentication with Anthropic.

## Verification

After applying the fix, verify it works:

```bash
python3 << 'EOF'
from app.database import SessionLocal
from app.services.bot_service import BotService

db = SessionLocal()
bot = BotService.get_bot(db, "eef34087-2222-4c6d-a9ab-1ccba4bb93e5")

print(f"Bot: {bot.name}")
print(f"API Key ID: {bot.api_key_id}")

if bot.api_key_id and bot.api_key_ref:
    print(f"✅ Using centralized API key: {bot.api_key_ref.name}")
    print(f"   Key length: {len(bot.api_key_ref.api_key)} chars")
else:
    print(f"❌ Still using inline key (or no key)")

db.close()
EOF
```

Should output:
```
Bot: Genghis Khan Expert
API Key ID: [some UUID]
✅ Using centralized API key: [Your key name]
   Key length: ~100 chars
```

## Testing the Fix

### Test 1: API Call

```bash
curl -X POST http://localhost:8000/api/chat/eef34087-2222-4c6d-a9ab-1ccba4bb93e5 \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "session_id": "test123"}'
```

Should return a response (not 500 error).

### Test 2: Browser

1. Go to: http://localhost:8000/chat/eef34087-2222-4c6d-a9ab-1ccba4bb93e5
2. Send message: "Hello"
3. Should get response from Claude

### Test 3: Create New Bot

1. Admin → API Keys tab → Add your key
2. Bots tab → Create new bot
3. Select your key from dropdown
4. Save and test chat

## Common Issues

### Issue: "ImportError: cannot import name 'APIKey'"

**Solution**: Restart your server. The database.py fix needs to load.

### Issue: "KeyError: 'APIKey'" in SQLAlchemy

**Solution**:
1. Stop server
2. Restart with `./start.sh`
3. This ensures init_db() imports the APIKey model

### Issue: Dropdown shows "No API keys found"

**Solution**: You haven't created any API keys yet.
1. Go to API Keys tab
2. Click "+ Add API Key"
3. Create one first

### Issue: Bot still fails after fix

**Possible causes**:
1. **Didn't restart server** - Changes to database.py require restart
2. **Wrong API key** - Make sure you entered valid key
3. **API key for wrong provider** - Anthropic bot needs Anthropic key

**Debug**:
```bash
# Check what bot is using
python3 << 'EOF'
from app.database import SessionLocal
from app.services.bot_service import BotService
from app.services.chat_service import ChatService

db = SessionLocal()
bot = BotService.get_bot(db, "eef34087-2222-4c6d-a9ab-1ccba4bb93e5")

try:
    api_key = ChatService.get_bot_api_key(bot)
    print(f"✅ Bot has API key (length: {len(api_key)})")
    print(f"   Starts with: {api_key[:15]}")
except Exception as e:
    print(f"❌ Error: {e}")

db.close()
EOF
```

## Prevention

To prevent this in the future:

1. ✅ **Use centralized API keys** - Add keys in API Keys tab, select from dropdown
2. ✅ **Never paste masked keys** - The UI now prevents this
3. ✅ **Test after edits** - Always test chat after editing a bot
4. ✅ **Check server logs** - Watch for errors in console

## Quick Fix Checklist

- [ ] Server is running
- [ ] Ran `python3 fix_bot_api_key.py` OR added key via admin UI
- [ ] Restarted server after fix
- [ ] Hard refreshed browser (Ctrl+Shift+R)
- [ ] Verified bot has valid API key (see Verification section)
- [ ] Tested chat - should work now!

## Summary

**Root cause**: Your bot had a corrupted API key from the previous bug.

**The fix**:
1. Updated database.py to import APIKey model
2. Add a valid API key via admin UI or fix script
3. Update your bot to use the new key
4. Restart server
5. Test chat

**Status**: The original corruption bug is fixed. This is just cleanup of the damaged data.

---

**Run `python3 fix_bot_api_key.py` and follow the prompts - easiest way to fix!**
