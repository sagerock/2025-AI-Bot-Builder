# Deploy to Railway in 5 Minutes ⚡

## Prerequisites
- GitHub account
- Your code in a GitHub repository
- Railway account (sign up at railway.app)

## 🚀 One-Time Setup (2 minutes)

### Step 1: Prepare Your Repo

Make sure these files exist in your project root:

**Procfile** (tells Railway how to start your app):
```bash
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**runtime.txt** (specifies Python version):
```
python-3.12
```

**requirements.txt** (already exists, but verify):
```bash
# Make sure it's up to date
pip freeze > requirements.txt
```

Commit these files:
```bash
git add Procfile runtime.txt requirements.txt
git commit -m "Add Railway deployment files"
git push
```

### Step 2: Create Railway Project

**Option A: Web Dashboard (Easiest)**

1. Go to **railway.app**
2. Click **"Start a New Project"**
3. Click **"Deploy from GitHub repo"**
4. Select your **AI Bot Builder** repository
5. Railway auto-detects Python and deploys!

**Option B: CLI (Faster)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize in your project directory
cd "/Volumes/T7/Scripts/AI Bot Builder"
railway init

# Select "Create a new project"
# Name it: ai-bot-builder
```

## 📦 Add PostgreSQL (1 minute)

### Via Dashboard:
1. In your Railway project
2. Click **"+ New"**
3. Select **"Database"** → **"PostgreSQL"**
4. Done! Railway auto-connects it

### Via CLI:
```bash
railway add -d postgres
```

Railway automatically sets `DATABASE_URL` environment variable!

## 🔐 Set Environment Variables (2 minutes)

### Generate Encryption Key:
```bash
python3 -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"
```

Copy the output.

### Via Dashboard:
1. Go to your service
2. Click **"Variables"** tab
3. Add these:

```
ENCRYPTION_KEY=your-generated-key-here
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-set by Railway
QDRANT_HOST=your-qdrant-host (if using Qdrant)
QDRANT_API_KEY=your-qdrant-key (if using Qdrant)
ALLOWED_ORIGINS=https://your-domain.railway.app
API_BASE_URL=https://your-domain.railway.app
```

### Via CLI:
```bash
railway variables set ENCRYPTION_KEY=your-key-here
railway variables set QDRANT_HOST=your-qdrant-host
railway variables set QDRANT_API_KEY=your-qdrant-key
```

## 🚀 Deploy!

### Auto-Deploy (Recommended)
Railway automatically deploys when you push to GitHub:
```bash
git push
# Railway detects push and deploys automatically
```

### Manual Deploy via CLI:
```bash
railway up
```

## 🌐 Get Your URL

### Via Dashboard:
1. Go to your service
2. Click **"Settings"**
3. Scroll to **"Domains"**
4. Click **"Generate Domain"**
5. Your app is live at: `your-app-name.railway.app`

### Via CLI:
```bash
railway domain
# Creates: your-app-name.railway.app
```

## ✅ Verify It Works

### Test the API:
```bash
curl https://your-app-name.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

### Open Admin Dashboard:
```
https://your-app-name.railway.app/admin
```

### Test Bot Chat:
```
https://your-app-name.railway.app/chat/YOUR-BOT-ID
```

## 🎨 Add Custom Domain (Optional)

### Via Dashboard:
1. Go to **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Enter your domain: `botbuilder.yourdomain.com`
4. Add the CNAME record to your DNS:
   ```
   CNAME: botbuilder → your-app-name.railway.app
   ```
5. Railway automatically provisions SSL certificate (free!)

### Via CLI:
```bash
railway domain add botbuilder.yourdomain.com
```

## 📊 Monitor Your App

### View Logs:
```bash
# Via CLI
railway logs

# Via Dashboard
Click "Deployments" → Select deployment → View logs
```

### Check Metrics:
Dashboard shows:
- CPU usage
- Memory usage
- Request count
- Response times

## 🔄 Continuous Deployment

**Already set up!** Railway automatically:
1. Watches your GitHub repo
2. Detects new commits
3. Builds and deploys
4. Zero downtime deployment

Just push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push
# Railway deploys automatically in ~2 minutes
```

## 💰 Cost Overview

You'll see costs in Railway dashboard:

**Free Trial**: $5 credit to start

**After trial**:
```
Web Service: ~$5/month (scales with usage)
PostgreSQL: ~$5/month
Total: ~$10/month
```

**Billing alerts**: Set in Settings → Team → Billing

## 🐛 Troubleshooting

### Build Failed?

Check Railway logs:
```bash
railway logs
```

Common issues:
- Missing dependencies in `requirements.txt`
- Wrong Python version in `runtime.txt`
- Database connection errors

### App Won't Start?

Check `Procfile` is correct:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Make sure `$PORT` is used (Railway assigns port dynamically).

### Database Connection Issues?

Verify `DATABASE_URL` is set:
```bash
railway variables
```

Should show:
```
DATABASE_URL=postgresql://...
```

### Environment Variable Not Working?

1. Check spelling (case-sensitive!)
2. Redeploy after adding variables:
   ```bash
   railway up --force
   ```

## 🔧 Advanced: Multiple Environments

### Create Staging Environment:

```bash
# Create staging branch
git checkout -b staging
git push origin staging

# In Railway dashboard:
# 1. Create new service from same repo
# 2. Select "staging" branch
# 3. Add same environment variables
# 4. Generate new domain: staging-botbuilder.railway.app
```

Now you have:
- **Production**: main branch → botbuilder.railway.app
- **Staging**: staging branch → staging-botbuilder.railway.app

## 📋 Quick Command Reference

```bash
# Login
railway login

# Check status
railway status

# View logs
railway logs

# Open dashboard
railway open

# Add database
railway add -d postgres

# Set variable
railway variables set KEY=value

# Deploy
railway up

# Generate domain
railway domain

# Link to existing project
railway link

# Unlink project
railway unlink
```

## 🎯 Post-Deployment Checklist

After deploying:

- [ ] Visit `/health` endpoint - should return healthy
- [ ] Open `/admin` - admin dashboard loads
- [ ] Create a test bot
- [ ] Add an API key
- [ ] Test chat functionality
- [ ] Check database is persisting data
- [ ] Verify SSL certificate (padlock in browser)
- [ ] Set up custom domain (optional)
- [ ] Configure billing alerts
- [ ] Share with first users!

## 🚀 You're Live!

Your AI Bot Builder is now deployed and accessible at:
```
https://your-app-name.railway.app
```

**Next steps**:
1. Create some bots
2. Share with clients
3. Monitor usage in Railway dashboard
4. Scale up as needed

---

## 💡 Pro Tips

1. **Enable notifications**: Railway → Settings → Notifications
   - Get alerts for deployment failures
   - Monitor for downtime

2. **Database backups**: Railway automatically backs up PostgreSQL
   - Can restore to any point in last 7 days

3. **View costs**: Railway → Settings → Usage
   - Real-time usage monitoring
   - Set budget alerts

4. **Team collaboration**: Railway → Settings → Members
   - Invite team members
   - Manage permissions

5. **Environment variables per branch**:
   - Different configs for staging/prod
   - Railway supports per-environment variables

---

## 🎉 That's It!

Your AI Bot Builder is now live on Railway in less than 10 minutes!

**What you got:**
- ✅ Live production app
- ✅ PostgreSQL database
- ✅ Auto-deployments from GitHub
- ✅ Free SSL certificate
- ✅ Automatic scaling
- ✅ Built-in monitoring
- ✅ ~$10/month cost

**Focus on building your product, not managing servers!**
