# Deployment Guide

Your AI Bot Builder is ready to deploy! All 5 of your bots will go online with the app.

## What Gets Deployed

✅ **Your bots** - All 5 bots in `data/botbuilder.db` (184KB)
- test 1
- Genghis Khan Expert
- SGWS
- Personal Jurisdiction Bot
- ALWD Citation Assistant

✅ **API Keys** - Your stored API keys (encrypted in database)
✅ **Conversation History** - All existing chat sessions
✅ **All Settings** - Bot configurations, prompts, colors, etc.

## Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. **Create a Railway account**: https://railway.app
2. **Install Railway CLI** (optional but helpful):
   ```bash
   npm install -g railway
   ```
3. **Deploy from GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit with bots"
   git push origin main
   ```
   Then connect your GitHub repo in Railway dashboard

4. **Or deploy directly with CLI**:
   ```bash
   railway login
   railway init
   railway up
   ```

5. **Environment Variables to Set** (in Railway dashboard):
   - `DATABASE_URL`: Will be auto-set to SQLite (your bots will be there!)
   - `QDRANT_URL`: Your Qdrant instance URL (if using)
   - `QDRANT_API_KEY`: Your Qdrant API key (if needed)

### Option 2: Heroku

1. Create Heroku app
2. Add buildpack: `heroku/python`
3. Push code: `git push heroku main`
4. Your database file will be deployed with the app

### Option 3: VPS (DigitalOcean, AWS, etc.)

1. SSH into your server
2. Clone your repository
3. Install Python 3.10+
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Important Notes

### Database Persistence
⚠️ **SQLite on ephemeral filesystems**: Some platforms (like Railway/Heroku) have ephemeral filesystems, meaning your database changes (new bots, conversations) may be lost on restart.

**Solutions:**
1. **For production**: Switch to PostgreSQL (Railway provides free PostgreSQL)
2. **For personal use**: SQLite is fine if you don't mind recreating bots after restarts

### Switching to PostgreSQL (Recommended for Production)

If you want persistence on Railway:

1. **Add PostgreSQL in Railway dashboard**
2. **Update your `.env` or Railway environment variables**:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```
3. **Install psycopg2**:
   ```bash
   pip install psycopg2-binary
   ```
4. **Add to requirements.txt**:
   ```
   psycopg2-binary==2.9.9
   ```

Your bots won't automatically migrate - you'll need to recreate them in the admin panel (one-time setup).

## Security Checklist Before Deploying

✅ **Authentication** - Already set up! (username: sagelewis, password: SageLewis1971)
✅ **API Keys** - Stored in database (but consider using Railway secrets)
⚠️ **Change admin password** - Update `app/auth.py` lines 10-11 with a stronger password
⚠️ **Update secret_key** - Set a random string in `.env` file:
   ```
   SECRET_KEY=your-random-64-character-string-here
   ```

## After Deployment

1. **Get your URL**: Railway will give you something like `https://your-app.up.railway.app`
2. **Login**: Go to `https://your-app.up.railway.app/login`
3. **Use your bots**: `https://your-app.up.railway.app/chat/{bot_id}`

## Updating the Online Version

When you make changes locally:
```bash
git add .
git commit -m "Description of changes"
git push
```

Railway will automatically redeploy!

## Backup Your Bots

Before deploying, create a backup:
```bash
cp data/botbuilder.db data/botbuilder.db.backup
```

## Need Help?

- Railway Docs: https://docs.railway.app
- This app uses: FastAPI, SQLAlchemy, Anthropic API, OpenAI API
