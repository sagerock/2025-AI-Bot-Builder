# Testing Admin Dashboard

## Quick Test Steps

### 1. Clear Browser Cache
**This is important!** The browser may have cached the old broken JavaScript.

**Chrome/Edge:**
- Press `Ctrl+Shift+Del` (Windows) or `Cmd+Shift+Del` (Mac)
- Select "Cached images and files"
- Click "Clear data"

**OR use hard refresh:**
- `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)

### 2. Restart Server

```bash
# Stop if running (Ctrl+C)
# Then restart:
./start.sh
# or
uvicorn app.main:app --reload --port 8000
```

### 3. Open Admin Dashboard

```
http://localhost:8000/admin
```

### 4. Check Browser Console

1. Open Developer Tools: `F12` or `Right-click → Inspect`
2. Go to "Console" tab
3. You should see:
   - `Admin dashboard loaded` (if page loaded)
   - NO red errors
   - NO "Uncaught" errors

### 5. Test Functions

**Test 1: Create Button**
- Click "+ Create New Bot" button
- Should see: `openCreateModal called` in console
- Modal should open

**Test 2: Load Bots**
- If you have no bots: Should see "No bots yet. Create your first bot!"
- If you have bots: Should see bot cards

**Test 3: Create a Bot**
- Fill in all required fields:
  - Name: "Test Bot"
  - Provider: Anthropic or OpenAI
  - Model: Choose any
  - API Key: (your key)
  - System Prompt: "You are helpful"
- Click "Save Bot"
- Bot should appear in list

**Test 4: Edit Button**
- Click "Edit" on a bot
- Modal should open with all fields filled
- Check console for any errors

**Test 5: Get Code**
- Click "Get Code" on a bot
- Should show URL and embed code
- Copy buttons should work

## Expected Console Output

```
Admin dashboard loaded
(no errors)
```

When you click "Create New Bot":
```
openCreateModal called
```

## If Still Having Issues

### Check these:

1. **Server is running?**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

2. **Admin page loads?**
   ```bash
   curl http://localhost:8000/admin
   # Should return HTML
   ```

3. **JavaScript file is correct?**
   ```bash
   grep -n "function openCreateModal" app/static/admin.html
   # Should show line number where function is defined
   ```

4. **Check exact error:**
   - Open browser console
   - Take screenshot of error
   - Note the line number

### Common Issues

**Issue: "openCreateModal is not defined"**
- **Cause:** Browser cache
- **Fix:** Hard refresh (Ctrl+F5 or Cmd+Shift+R)

**Issue: "Unexpected end of input"**
- **Cause:** JavaScript syntax error
- **Fix:** Already fixed - just refresh

**Issue: Favicon 404**
- **Cause:** Missing favicon
- **Fix:** Already fixed - just refresh

## Verification Checklist

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000
- [ ] Can access http://localhost:8000/admin
- [ ] No errors in browser console
- [ ] "Create New Bot" button works
- [ ] Can fill form and create bot
- [ ] Can edit existing bot
- [ ] Can get embed code
- [ ] Can delete bot

If all checkboxes are ticked, everything is working! ✅

## Still Not Working?

Try this nuclear option:

```bash
# 1. Stop server
# 2. Clear browser completely
# 3. Delete database (if you don't need existing bots)
rm data/botbuilder.db
# 4. Restart server
./start.sh
# 5. Open in incognito/private window
# 6. Go to http://localhost:8000/admin
```

This ensures absolutely no caching and fresh database.
