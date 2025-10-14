# Troubleshooting 500 Error After Bot Update

## Problem

After editing a bot, the chat stops working with a 500 Internal Server Error.

## What Was Fixed

### 1. Added Bot Refresh
**File:** `app/api/chat.py`

Added `db.refresh(bot)` after fetching the bot to ensure we have the latest data from the database:

```python
# Get bot
bot = BotService.get_bot(db, bot_id)
if not bot:
    raise HTTPException(status_code=404, detail="Bot not found")

# Refresh bot from database to get latest data
db.refresh(bot)
```

**Why:** SQLAlchemy caches objects. After an update, the cached object might be stale.

### 2. Better Error Logging
**File:** `app/api/chat.py`

Added detailed error logging:

```python
except Exception as e:
    import traceback
    error_detail = f"AI provider error: {str(e)}\n{traceback.format_exc()}"
    print(f"ERROR in chat: {error_detail}")
    raise HTTPException(status_code=500, detail=f"AI provider error: {str(e)}")
```

**Why:** Now you can see the exact error in the server console.

### 3. Safer Field Access
**File:** `app/services/chat_service.py`

Changed from `hasattr` to `getattr` with defaults:

```python
# Before
if hasattr(bot, 'reasoning_effort') and bot.reasoning_effort:
    request_params["reasoning"] = {"effort": bot.reasoning_effort}

# After
reasoning_effort = getattr(bot, 'reasoning_effort', 'medium')
if reasoning_effort:
    request_params["reasoning"] = {"effort": reasoning_effort}
```

**Why:** Safer and provides default values if fields are missing.

## How to Debug

### Step 1: Check Server Console

When the error occurs, look at your server console output. You should now see detailed error messages like:

```
ERROR in chat: AI provider error: [specific error]
```

### Step 2: Run Test Script

```bash
python test_bot_update.py
```

This will:
- Find your first bot
- Show its current settings
- Try updating it
- Verify fields are preserved

### Step 3: Check Database

```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('data/botbuilder.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name, reasoning_effort, text_verbosity FROM bots")
for row in cursor.fetchall():
    print(f"{row[1]}: reasoning={row[2]}, verbosity={row[3]}")
conn.close()
EOF
```

### Step 4: Restart Server

Sometimes a fresh restart helps:

```bash
# Stop server (Ctrl+C)
./start.sh
```

## Common Causes

### 1. NULL Values After Update

**Problem:** Fields become NULL when updating bot.

**Check:**
```python
python test_bot_update.py
```

**Fix:** Make sure the update includes all fields or doesn't overwrite them.

### 2. Missing API Key

**Problem:** Bot's API key became empty.

**Check in admin UI:** Edit the bot and verify API key is present.

**Fix:** Re-enter the API key and save.

### 3. Invalid Model Name

**Problem:** Model name changed to something invalid.

**Check:** Make sure the model name matches exactly:
- Claude: `claude-sonnet-4-5-20250929`
- GPT-5: `gpt-5`

### 4. Cached Bot Object

**Problem:** SQLAlchemy returning stale data.

**Fix:** Already added `db.refresh(bot)` - should be fixed now!

## Testing the Fix

### Test 1: Update Bot Name

1. Go to admin dashboard
2. Edit a bot
3. Change just the name
4. Save
5. Try chatting
6. ✅ Should work

### Test 2: Update Bot Model

1. Edit a bot
2. Change provider (e.g., Anthropic to OpenAI)
3. Change model
4. Update API key
5. Save
6. Try chatting
7. ✅ Should work

### Test 3: Update GPT-5 Settings

1. Edit a bot with GPT-5 model
2. Change reasoning effort
3. Change verbosity
4. Save
5. Try chatting
6. ✅ Should work

## If Still Broken

### Collect Debug Info

1. **Check server console** - What's the exact error?

2. **Check browser console** - Click on the 500 error to see details

3. **Test API directly:**
```bash
curl -X POST http://localhost:8000/api/chat/YOUR_BOT_ID \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test123"}'
```

4. **Check bot in database:**
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('data/botbuilder.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM bots WHERE id='YOUR_BOT_ID'")
print(cursor.fetchone())
conn.close()
EOF
```

### Nuclear Option

If all else fails, recreate the bot:

1. Note down all bot settings
2. Delete the broken bot
3. Create new bot with same settings
4. Test - should work

## Prevention

To avoid this issue:

1. **Don't partially update** - When updating via API, include all fields
2. **Always test after update** - Send a test message after editing
3. **Keep backups** - Regularly backup `data/botbuilder.db`
4. **Monitor logs** - Watch server console for errors

## Quick Fix Checklist

- [ ] Server is running
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Check server console for errors
- [ ] Run `python test_bot_update.py`
- [ ] Verify bot has valid API key
- [ ] Verify bot has valid model name
- [ ] Try creating a new test bot
- [ ] If new bot works, recreate broken bot

## What the Fixes Do

1. **`db.refresh(bot)`** - Ensures fresh data from database
2. **Better error logging** - Shows exactly what went wrong
3. **`getattr` with defaults** - Handles missing/NULL fields gracefully

These three changes should prevent the 500 error from happening again!

## Still Need Help?

1. Copy the full error from server console
2. Check which line number the error is on
3. Look at that file and line
4. The error message should now be much clearer

The fixes are already in place - just restart your server and it should work! 🎉
