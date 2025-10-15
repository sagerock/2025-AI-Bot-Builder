# 🚀 Deploy to Railway NOW - Step by Step

## ✅ What We've Done

Your app is now **ready for deployment**! Here's what I just prepared:

- ✅ Created `Procfile` (tells Railway how to start your app)
- ✅ Created `runtime.txt` (specifies Python 3.12)
- ✅ Updated `requirements.txt` (all dependencies)
- ✅ Updated `.gitignore` (protects sensitive files)
- ✅ Initialized git repository
- ✅ Created initial commit

## 🎯 Next Steps - You Do These

### Option A: Deploy via Railway Website (Easiest - No CLI needed)

**Step 1: Create Railway Account**
1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (recommended) or email

**Step 2: Deploy Your Code**

Since your code is local (not on GitHub yet), you need to push it first:

```bash
# 1. Create a new repository on GitHub
# Go to github.com → New Repository
# Name it: ai-bot-builder
# Don't initialize with README (we already have files)

# 2. Push your code to GitHub
cd "/Volumes/T7/Scripts/AI Bot Builder"

git remote add origin https://github.com/YOUR-USERNAME/ai-bot-builder.git
git branch -M main
git push -u origin main
```

**Step 3: Connect to Railway**
1. Back in Railway, click **"Deploy from GitHub repo"**
2. Select **"ai-bot-builder"** repository
3. Railway detects Python and starts deploying!
4. Wait 2-3 minutes for build

**Step 4: Add PostgreSQL**
1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Done! Railway auto-connects it

**Step 5: Set Environment Variables**

Generate encryption key first:
```bash
python3 -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"
```

Copy the output, then in Railway:
1. Click your **web service**
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these one by one:

```
ENCRYPTION_KEY=paste-your-generated-key-here
DATABASE_URL=${{Postgres.DATABASE_URL}}
API_BASE_URL=${{RAILWAY_PUBLIC_DOMAIN}}
ALLOWED_ORIGINS=${{RAILWAY_PUBLIC_DOMAIN}}
```

**Step 6: Generate Domain**
1. Go to **"Settings"** tab
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. Your app is live! Copy the URL (e.g., `https://ai-bot-builder-production.up.railway.app`)

**Step 7: Test It!**
```bash
# Visit your app
https://your-app-name.up.railway.app/admin

# Test health endpoint
curl https://your-app-name.up.railway.app/health
```

---

### Option B: Deploy via Railway CLI (For Tech-Savvy Users)

**Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

**Step 2: Login**
```bash
railway login
```

This opens your browser to authenticate.

**Step 3: Initialize Project**
```bash
cd "/Volumes/T7/Scripts/AI Bot Builder"
railway init
```

- Select **"Create a new project"**
- Name it: **ai-bot-builder**

**Step 4: Add PostgreSQL**
```bash
railway add -d postgres
```

**Step 5: Set Environment Variables**
```bash
# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set it
railway variables set ENCRYPTION_KEY=your-generated-key-here

# Railway auto-sets DATABASE_URL, but you can verify:
railway variables
```

**Step 6: Deploy**
```bash
railway up
```

Wait 2-3 minutes for deployment.

**Step 7: Get Your URL**
```bash
railway domain
```

Generates a URL like: `https://ai-bot-builder-production.up.railway.app`

**Step 8: Open Your App**
```bash
railway open
# Or manually visit the URL
```

---

## 🔍 Verify Deployment

### Check 1: Health Endpoint
```bash
curl https://your-app-name.up.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

### Check 2: Admin Dashboard
Open in browser:
```
https://your-app-name.up.railway.app/admin
```

Should see the admin interface!

### Check 3: Check Logs
```bash
# Via CLI
railway logs

# Or in Railway dashboard → Deployments → View logs
```

---

## 🐛 Troubleshooting

### Issue: Build Failed

**Check logs**:
```bash
railway logs
```

**Common causes**:
- Missing dependencies in requirements.txt
- Python version mismatch
- Database connection issues

**Fix**: Check the specific error in logs and address it.

### Issue: App Won't Start

**Check Procfile**:
```bash
cat Procfile
# Should show: web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Check runtime.txt**:
```bash
cat runtime.txt
# Should show: python-3.12
```

### Issue: Database Connection Failed

**Verify DATABASE_URL is set**:
```bash
railway variables | grep DATABASE_URL
```

If missing, add PostgreSQL:
```bash
railway add -d postgres
```

### Issue: 500 Error on /admin

**Check environment variables**:
```bash
railway variables
```

Make sure ENCRYPTION_KEY is set.

**Check logs for detailed error**:
```bash
railway logs --tail
```

---

## 📊 Post-Deployment Checklist

After deploying, verify:

- [ ] App is accessible at Railway URL
- [ ] `/health` endpoint returns healthy
- [ ] `/admin` dashboard loads
- [ ] Can create an API key in admin
- [ ] Can create a bot
- [ ] Bot chat works
- [ ] Database persists data (refresh page, data still there)
- [ ] SSL certificate is active (padlock in browser)

---

## 🎯 What to Do Next

### 1. Fix Your Local Bot's API Key

Remember your existing bot has a corrupted key. Let's fix it now that we're deploying:

```bash
# Run the fix script locally BEFORE deploying your database
python3 fix_bot_api_key.py
```

This will:
- Prompt for your Anthropic API key
- Create an APIKey entry
- Update your bot to use it

Then commit and push:
```bash
git add -A
git commit -m "Fix bot API key"
git push
```

Railway will auto-deploy the update!

### 2. Set Up Qdrant (If Using RAG)

**Option 1: Qdrant Cloud (Recommended)**
1. Go to **https://cloud.qdrant.io**
2. Create free account
3. Create a cluster (1GB free)
4. Get your API URL and key
5. Add to Railway variables:
```bash
railway variables set QDRANT_URL=your-qdrant-url
railway variables set QDRANT_API_KEY=your-qdrant-key
```

**Option 2: Self-Host on Railway**
```bash
# Add Qdrant service
railway add
# Select "Empty Service"
# Deploy Qdrant Docker image
```

### 3. Add Custom Domain (Optional)

**In Railway Dashboard**:
1. Settings → Networking → Domains
2. Click **"Custom Domain"**
3. Enter: `botbuilder.yourdomain.com`
4. Add CNAME record to your DNS:
   ```
   CNAME: botbuilder → your-app.up.railway.app
   ```
5. Railway auto-provisions SSL (free!)

### 4. Monitor Your App

**Set up notifications**:
- Railway → Settings → Notifications
- Get alerts for deployments and errors

**View metrics**:
- Railway Dashboard shows CPU, memory, requests

### 5. Set Budget Alerts

**Prevent surprise bills**:
- Railway → Team Settings → Usage
- Set spending limit
- Get alerts at 50%, 80%, 100%

---

## 💰 What You'll Pay

**First Month**: ~$0-5 (Railway gives $5 credit)

**Ongoing**:
```
Web Service: ~$5/month
PostgreSQL: ~$5/month
━━━━━━━━━━━━━━━━━━━━
Total: ~$10/month
```

Plus Qdrant if you use it:
```
Qdrant Cloud Free: $0
Or
Qdrant Cloud Starter: $25/month
```

---

## 🚀 Summary

**You're ready to deploy!** Here's what you need to do:

1. **Push to GitHub** (if using Option A)
2. **Connect to Railway** (via website or CLI)
3. **Add PostgreSQL** (one click)
4. **Set ENCRYPTION_KEY** (generate and add to variables)
5. **Deploy!** (automatic)
6. **Test** (visit /admin, create bots)

**Total time: 10-15 minutes** ⚡

---

## 🆘 Need Help?

If you get stuck:

1. **Check Railway logs** - Most errors are explained there
2. **Railway Discord** - Very responsive community
3. **Railway Docs** - https://docs.railway.app

Or we can troubleshoot together!

---

## 🎉 Ready to Deploy?

Choose your path:
- **Option A**: Via Railway website (no CLI)
- **Option B**: Via Railway CLI (faster)

Let me know when you're ready to start, or if you have any questions!

**Your app is 10 minutes away from being live!** 🚀
