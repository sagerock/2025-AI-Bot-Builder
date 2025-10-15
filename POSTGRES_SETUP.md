# PostgreSQL Setup Guide - Keep Your Bots Permanent! 🚀

This guide will help you switch from SQLite to PostgreSQL so your bots are NEVER lost.

## Why PostgreSQL?

- ✅ **Permanent Storage** - Your bots survive restarts/redeployments
- ✅ **Better Performance** - Faster queries for multiple users
- ✅ **Railway Free Tier** - Free PostgreSQL database included
- ✅ **Production Ready** - Used by millions of apps

## Step-by-Step Process

### Option 1: Railway (Recommended - Easiest)

#### Step 1: Deploy to Railway with SQLite First

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit with bots"

# Deploy to Railway
railway login
railway init
railway up
```

Your app is now online with SQLite! Your 5 bots are working, but they'll disappear if Railway restarts.

#### Step 2: Add PostgreSQL Database

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Select your project**
3. **Click "+ New"** → **"Database"** → **"Add PostgreSQL"**
4. Railway will automatically:
   - Create a PostgreSQL database
   - Add `DATABASE_URL` environment variable
   - Restart your app

#### Step 3: Copy the PostgreSQL Connection String

1. Click on your **PostgreSQL service** in Railway dashboard
2. Go to **"Connect"** tab
3. Copy the **"Postgres Connection URL"** (looks like this):
   ```
   postgresql://postgres:password@hostname.railway.app:5432/railway
   ```

#### Step 4: Migrate Your Bots from SQLite to PostgreSQL

**On your local computer**, run the migration:

```bash
# Make sure you're in the project directory
cd "/Volumes/T7/Scripts/AI Bot Builder"

# Run the migration script with your PostgreSQL URL
python3 migrate_to_postgres.py "postgresql://postgres:password@hostname.railway.app:5432/railway"
```

Replace the URL with the one you copied from Railway!

You'll see output like:
```
Migrating API Keys...
  ✓ Migrated API Key: Anthropic Main
Migrating Bots...
  ✓ Migrated Bot: Personal Jurisdiction Bot
  ✓ Migrated Bot: ALWD Citation Assistant
  ... (all 5 bots)
✅ Migration completed successfully!
```

#### Step 5: Verify Everything Works

1. Go to your Railway app URL: `https://your-app.up.railway.app`
2. Login with your credentials
3. Check the admin panel - all 5 bots should be there!
4. Test chatting with a bot

**🎉 DONE! Your bots are now permanent!**

---

### Option 2: Local PostgreSQL Testing (Optional)

If you want to test PostgreSQL locally first:

#### Install PostgreSQL

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Create Local Database:**
```bash
createdb botbuilder
```

#### Migrate Locally

```bash
python3 migrate_to_postgres.py "postgresql://localhost:5432/botbuilder"
```

#### Update .env File

Create `.env` file:
```bash
DATABASE_URL=postgresql://localhost:5432/botbuilder
```

#### Run the App

```bash
uvicorn app.main:app --reload
```

Your app now uses PostgreSQL locally!

---

## Troubleshooting

### "Connection refused" Error

Make sure the PostgreSQL URL is correct. Check Railway dashboard for the exact URL.

### "Table already exists" Error

This is okay! It means tables were created. The script will skip existing data.

### Bots Disappeared After Migration

Check Railway logs:
```bash
railway logs
```

Make sure `DATABASE_URL` environment variable is set in Railway.

### Migration Script Errors

Check that:
1. Your `data/botbuilder.db` file exists locally
2. You have internet connection
3. The PostgreSQL URL is correct (copy it exactly from Railway)

---

## What Gets Migrated?

✅ All 5 Bots (configurations, prompts, settings)
✅ API Keys (encrypted)
✅ Conversation History
✅ All Messages

**Total migration time: ~10 seconds**

---

## After Migration

### Creating New Bots
New bots created online will be **permanent** in PostgreSQL!

### Updating Bots
All bot updates are saved to PostgreSQL automatically.

### Backups
Railway automatically backs up your PostgreSQL database!

### Going Back to SQLite
You can always switch back by removing the `DATABASE_URL` environment variable in Railway. But why would you? 😄

---

## Cost

**Railway Free Tier:**
- ✅ PostgreSQL Database: FREE
- ✅ Up to $5/month usage: FREE
- ✅ 512MB RAM: FREE
- ✅ Shared CPU: FREE

Your bot builder will likely stay **100% FREE** on Railway!

---

## Quick Reference

**Migration Command:**
```bash
python3 migrate_to_postgres.py "YOUR_POSTGRES_URL_HERE"
```

**Check Railway Environment:**
```bash
railway variables
```

**View Railway Logs:**
```bash
railway logs
```

**Redeploy on Railway:**
```bash
railway up
```

---

## Summary of Steps

1. ✅ Deploy to Railway with SQLite
2. ✅ Add PostgreSQL database in Railway dashboard
3. ✅ Copy PostgreSQL connection URL
4. ✅ Run migration script locally: `python3 migrate_to_postgres.py "URL"`
5. ✅ Verify bots in admin panel
6. 🎉 Your bots are now PERMANENT!

---

Need help? Check Railway docs or ask me!
