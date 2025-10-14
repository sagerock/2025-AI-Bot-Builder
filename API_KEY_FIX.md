# API Key Preservation Fix

## Problem Solved

The issue where editing a bot caused 500 errors has been fixed! The problem was:

1. When editing a bot, the API returned a **masked** API key (e.g., `sk-ant-a...bQAA`)
2. This masked value was populated into the edit form
3. When you saved the bot, the masked value overwrote the real API key
4. Next chat attempt failed with: `401 - authentication_error: invalid x-api-key`

## The Fix

### Changes Made

**File: `app/static/admin.html`**

#### Change 1: Edit Form (Lines 568-570)
```javascript
// OLD CODE (BROKEN):
document.getElementById('bot-api-key').value = bot.api_key || '';

// NEW CODE (FIXED):
// Don't populate API key field - leave blank to preserve existing key
document.getElementById('bot-api-key').value = '';
document.getElementById('bot-api-key').placeholder = 'Leave blank to keep current API key';
```

#### Change 2: Form Submission (Lines 509-532)
```javascript
// OLD CODE (BROKEN):
const botData = {
    name: document.getElementById('bot-name').value,
    // ... other fields ...
    api_key: document.getElementById('bot-api-key').value,  // Always sent masked value!
};

// NEW CODE (FIXED):
const apiKeyValue = document.getElementById('bot-api-key').value.trim();

const botData = {
    name: document.getElementById('bot-name').value,
    // ... other fields ...
    // api_key NOT included by default
};

// Only include api_key if user entered a new value (not blank)
if (apiKeyValue) {
    botData.api_key = apiKeyValue;
}
```

## What This Means

✅ **When editing a bot:**
- API key field will be **blank** with placeholder text: "Leave blank to keep current API key"
- If you don't enter anything, your existing API key is **preserved**
- If you enter a new API key, it will **update** to the new one

✅ **No more corrupted API keys!**

## Action Required

⚠️ **Your existing bot's API key was already corrupted by the previous bug**

You need to **re-enter your API key** for affected bots:

### Steps to Fix Your Bot:

1. **Go to admin dashboard**: http://localhost:8000/admin

2. **Click "Edit" on your bot** (Genghis Khan Expert)

3. **Re-enter your API key**:
   - For Anthropic: Enter your full `sk-ant-api03-...` key
   - For OpenAI: Enter your full `sk-...` key

4. **Click "Save Bot"**

5. **Test the chat** - it should work now!

### Where to Find Your API Keys:

- **Anthropic API Key**: https://console.anthropic.com/settings/keys
- **OpenAI API Key**: https://platform.openai.com/api-keys

## Testing the Fix

### Test 1: Edit Without Changing API Key

1. Edit a bot
2. Change only the name or description
3. **Leave API key field blank**
4. Save
5. ✅ Chat should still work (API key preserved)

### Test 2: Update API Key

1. Edit a bot
2. Enter a new API key
3. Save
4. ✅ New API key should be used

### Test 3: Create New Bot

1. Create a new bot
2. Fill in all fields including API key
3. Save
4. ✅ Should work normally

## Backend Support

The backend already supports this properly:

**File: `app/services/bot_service.py` (Line 37)**
```python
update_data = bot_data.model_dump(exclude_unset=True)
```

The `exclude_unset=True` means:
- If a field is not included in the update request, it won't be changed
- This allows us to omit `api_key` from updates when not changing it

## Security Note

The API key masking in `BotResponse` is still in place for security:

**File: `app/schemas/bot.py`**
```python
def model_post_init(self, __context):
    # Mask API key for security (only show first 8 and last 4 chars)
    if self.api_key and len(self.api_key) > 12:
        self.api_key = f"{self.api_key[:8]}...{self.api_key[-4:]}"
```

This is **good** - it prevents API keys from being exposed in API responses. But now the frontend handles it correctly by not sending the masked value back.

## Summary

| Scenario | Old Behavior | New Behavior |
|----------|-------------|--------------|
| Edit bot, leave API key blank | ❌ Corrupted with masked value | ✅ Preserved unchanged |
| Edit bot, enter new API key | ❌ Sometimes corrupted | ✅ Updated correctly |
| Create new bot | ✅ Worked fine | ✅ Still works fine |

## Files Modified

1. `app/static/admin.html` - Fixed editBot() and form submission
2. This documentation file

## No Server Restart Needed

Since this was a frontend-only fix, you don't need to restart the server. Just:
1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Re-enter your API key in the affected bot
3. Start chatting!

---

**The fix is complete! Your bots will no longer lose their API keys when edited.** 🎉
