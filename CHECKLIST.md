# Setup Checklist

Use this checklist to get your AI Bot Builder platform up and running.

## ✅ Initial Setup

### 1. Prerequisites
- [ ] Python 3.11+ installed
- [ ] pip installed
- [ ] (Optional) Docker & Docker Compose installed
- [ ] Git installed (for version control)

### 2. Get API Keys
- [ ] Anthropic API key (from https://console.anthropic.com)
- [ ] OpenAI API key (from https://platform.openai.com)
- [ ] (Optional) Qdrant Cloud account (from https://cloud.qdrant.io)

### 3. Project Setup

#### Quick Method
- [ ] Run `./start.sh`
- [ ] Wait for installation to complete
- [ ] Open http://localhost:8000/admin

#### Manual Method
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy env file: `cp .env.example .env`
- [ ] Edit `.env` with your settings
- [ ] Run server: `uvicorn app.main:app --reload --port 8000`

#### Docker Method
- [ ] Review `docker-compose.yml`
- [ ] Create `.env` file
- [ ] Run: `docker-compose up -d`
- [ ] Check logs: `docker-compose logs -f app`

## ✅ Configuration

### Required Settings (.env)
- [ ] Set `SECRET_KEY` to a random string
- [ ] Set `ADMIN_PASSWORD` (if you want admin protection)
- [ ] Review `DATABASE_URL` (SQLite default is fine for testing)

### Optional Settings
- [ ] Set `DEFAULT_ANTHROPIC_API_KEY` (or set per-bot)
- [ ] Set `DEFAULT_OPENAI_API_KEY` (or set per-bot)
- [ ] Configure `QDRANT_URL` if using Qdrant
- [ ] Configure `QDRANT_API_KEY` if using Qdrant Cloud
- [ ] Set `API_BASE_URL` to your production URL
- [ ] Update `ALLOWED_ORIGINS` for CORS

## ✅ Testing Locally

### Verify Installation
- [ ] Server starts without errors
- [ ] Navigate to http://localhost:8000
- [ ] See welcome JSON response
- [ ] Navigate to http://localhost:8000/docs
- [ ] See API documentation (Swagger UI)
- [ ] Navigate to http://localhost:8000/admin
- [ ] See admin dashboard

### Create Test Bot
- [ ] Click "Create New Bot"
- [ ] Fill in required fields:
  - [ ] Name: "Test Bot"
  - [ ] Provider: Anthropic or OpenAI
  - [ ] Model: Select a model
  - [ ] API Key: Enter your API key
  - [ ] System Prompt: "You are a helpful test assistant"
- [ ] Click "Save Bot"
- [ ] Bot appears in dashboard

### Test Chat
- [ ] Click "Get Code" on your test bot
- [ ] Copy the standalone URL
- [ ] Open URL in new tab
- [ ] See chat interface
- [ ] Type a message: "Hello, are you working?"
- [ ] Receive response from AI
- [ ] Verify conversation continues (memory works)

### Test Widget
- [ ] Create a test HTML file:
  ```html
  <!DOCTYPE html>
  <html>
  <head><title>Test</title></head>
  <body>
    <h1>Test Page</h1>
    <script src="http://localhost:8000/static/widget.js"
            data-bot-id="YOUR_BOT_ID"></script>
  </body>
  </html>
  ```
- [ ] Open in browser
- [ ] See widget button in bottom-right
- [ ] Click to open chat
- [ ] Send test message
- [ ] Receive response

## ✅ Optional: Qdrant Setup (for RAG)

### Local Qdrant
- [ ] Run: `docker run -p 6333:6333 qdrant/qdrant:latest`
- [ ] Verify: http://localhost:6333/dashboard
- [ ] Update `.env`: `QDRANT_URL=http://localhost:6333`

### Qdrant Cloud
- [ ] Sign up at https://cloud.qdrant.io
- [ ] Create cluster
- [ ] Get cluster URL
- [ ] Get API key
- [ ] Update `.env`:
  - [ ] `QDRANT_URL=https://xyz.cloud.qdrant.io`
  - [ ] `QDRANT_API_KEY=your-key`

### Index Test Documents
- [ ] Create test collection in Qdrant
- [ ] Index some sample documents
- [ ] Create bot with RAG enabled
- [ ] Set collection name
- [ ] Test retrieval with relevant question

## ✅ Production Deployment

### Choose Platform
- [ ] Select deployment platform:
  - [ ] Railway (easiest)
  - [ ] DigitalOcean App Platform
  - [ ] Render
  - [ ] AWS EC2
  - [ ] Heroku
  - [ ] Other VPS with Docker

### Platform-Specific Setup
Follow the appropriate section in DEPLOYMENT.md:
- [ ] Create account on chosen platform
- [ ] Connect GitHub repository (or upload code)
- [ ] Configure build settings
- [ ] Set environment variables
- [ ] Deploy application

### Production Database
- [ ] Set up PostgreSQL:
  - [ ] Use platform's managed database, OR
  - [ ] Set up external PostgreSQL
- [ ] Update `DATABASE_URL` in production environment
- [ ] Verify connection

### Domain & SSL
- [ ] Point domain to deployment
- [ ] Configure SSL certificate:
  - [ ] Platform auto-SSL (Railway, Render, etc.), OR
  - [ ] Let's Encrypt with Certbot, OR
  - [ ] CloudFlare SSL
- [ ] Update `API_BASE_URL` to production domain
- [ ] Test HTTPS access

### Security Checklist
- [ ] Change `SECRET_KEY` to strong random string
- [ ] Change `ADMIN_PASSWORD` to strong password
- [ ] Verify HTTPS is working
- [ ] Update `ALLOWED_ORIGINS` to production domains only
- [ ] Review API keys are not exposed
- [ ] Set up firewall rules (if applicable)
- [ ] Enable rate limiting (if needed)

## ✅ Post-Deployment

### Verification
- [ ] Access production admin dashboard
- [ ] Create production bot
- [ ] Test chat interface
- [ ] Test widget embed
- [ ] Verify memory/sessions work
- [ ] Test RAG if enabled
- [ ] Check response times
- [ ] Review logs for errors

### Monitoring Setup
- [ ] Set up log aggregation
- [ ] Monitor response times
- [ ] Track API costs
- [ ] Set up error alerts
- [ ] Monitor database size
- [ ] Track active users/sessions

### Documentation
- [ ] Document your deployment URL
- [ ] Document bot configurations
- [ ] Document API keys storage
- [ ] Create runbook for common issues
- [ ] Document backup procedures

## ✅ Client Onboarding

### For Each Client
- [ ] Create dedicated bot
- [ ] Configure with client requirements
- [ ] Test thoroughly
- [ ] Generate deployment code
- [ ] Provide to client:
  - [ ] Standalone URL
  - [ ] Embed code
  - [ ] Integration instructions
- [ ] Verify deployment on client site
- [ ] Test from client's environment

## ✅ Maintenance

### Regular Tasks
- [ ] Monitor API costs (daily/weekly)
- [ ] Review error logs (weekly)
- [ ] Check database size (weekly)
- [ ] Update dependencies (monthly)
- [ ] Review and optimize prompts (monthly)
- [ ] Backup database (weekly/daily)
- [ ] Test all bots (monthly)

### Updates
- [ ] Pull latest code
- [ ] Review CHANGELOG
- [ ] Test in staging
- [ ] Deploy to production
- [ ] Verify all bots still work

## ✅ Troubleshooting

If something goes wrong, check:

### Server Won't Start
- [ ] Check Python version (3.11+)
- [ ] Verify all dependencies installed
- [ ] Check `.env` file exists and is valid
- [ ] Review error messages in terminal
- [ ] Check port 8000 is not in use

### Bot Not Responding
- [ ] Verify API key is valid
- [ ] Check AI provider status page
- [ ] Review server logs
- [ ] Test with simple message
- [ ] Verify bot is active in database

### Widget Not Loading
- [ ] Check browser console for errors
- [ ] Verify widget.js is accessible
- [ ] Confirm bot_id is correct
- [ ] Test CORS settings
- [ ] Check network tab in browser

### RAG Not Working
- [ ] Verify Qdrant is accessible
- [ ] Check collection exists
- [ ] Verify collection has documents
- [ ] Test Qdrant API directly
- [ ] Review embedding configuration

### Database Issues
- [ ] Check file permissions (SQLite)
- [ ] Verify connection string (PostgreSQL)
- [ ] Check disk space
- [ ] Review migration status
- [ ] Try database backup/restore

## 🎉 Success Criteria

You're fully set up when:

✅ Server runs without errors
✅ Admin dashboard is accessible
✅ Can create bots successfully
✅ Bots respond to messages
✅ Memory/sessions work correctly
✅ Widget loads on test page
✅ Production deployment is live
✅ SSL certificate is active
✅ Clients can access their bots
✅ Monitoring is in place

## 📚 Need Help?

Refer to:
- **QUICK_START.md** - Getting started
- **USAGE_GUIDE.md** - Using the platform
- **DEPLOYMENT.md** - Deploying to production
- **ARCHITECTURE.md** - Understanding the system
- **API Docs** - http://localhost:8000/docs

---

**Ready to build?** Start with: `./start.sh` 🚀
