# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Option 1: Automatic Setup (Recommended)

```bash
./start.sh
```

That's it! The script will:
- Create virtual environment
- Install dependencies
- Start the server

### Option 2: Docker (Easiest for Production)

```bash
docker-compose up -d
```

### Option 3: Manual Setup

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Run
uvicorn app.main:app --reload --port 8000
```

## 🎯 Access Points

Once running:

- **Admin Dashboard**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api

## 📝 Create Your First Bot

1. Open http://localhost:8000/admin
2. Click "Create New Bot"
3. Fill in:
   - Name: "My First Bot"
   - Provider: Anthropic or OpenAI
   - Model:
     - Anthropic: claude-sonnet-4-5-20250929 (latest) or claude-3-5-haiku (fastest)
     - OpenAI: gpt-5 (latest) or gpt-4
   - API Key: Your API key
   - System Prompt: "You are a helpful assistant"
   - (For GPT-5: Set reasoning effort and verbosity)
4. Click "Save Bot"
5. Click "Get Code" to get your bot URL!

## 🌐 Deploy Your Bot

### Standalone URL
```
https://yourdomain.com/chat/{bot_id}
```
Share this URL with anyone!

### Embed Widget
```html
<script src="https://yourdomain.com/static/widget.js"
        data-bot-id="{bot_id}"></script>
```
Add to any website before `</body>` tag!

## 🔑 Get API Keys

**Anthropic (Claude)**
- Go to: https://console.anthropic.com
- Create API key

**OpenAI (GPT)**
- Go to: https://platform.openai.com
- Create API key

## 📚 Documentation

- **Usage Guide**: See USAGE_GUIDE.md
- **Deployment**: See DEPLOYMENT.md
- **API Docs**: http://localhost:8000/docs

## 🆘 Quick Troubleshooting

**Port already in use?**
```bash
# Change port
uvicorn app.main:app --reload --port 8080
```

**Database error?**
```bash
# Delete and recreate
rm -rf data/
mkdir data
```

**Dependencies issue?**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## ⚙️ Configuration

Edit `.env` file to change:
- Database location
- Secret key
- Admin password
- Qdrant settings
- Default API keys

## 🎨 Features

✅ **Latest Models**: Claude 4 (Sonnet 4.5, Opus 4.1) & OpenAI GPT-5
✅ Claude Sonnet 4.5 - Best for agents & coding
✅ GPT-5 reasoning models with configurable effort & verbosity
✅ RAG with Qdrant vector database
✅ Conversation memory
✅ Customizable chat widget
✅ Standalone chat pages
✅ Embeddable widget
✅ Simple admin dashboard
✅ REST API
✅ Docker support

## 💡 Example Bots

**Customer Support**
```
System Prompt: You are a customer support agent. Help with orders, products, and policies.
Temperature: 70
Memory: Enabled
```

**Knowledge Base (with RAG)**
```
System Prompt: Answer questions using the provided documentation.
Temperature: 50
Memory: Enabled
RAG: Enabled (with Qdrant collection)
```

**Creative Assistant**
```
System Prompt: You are a creative writing assistant. Help with stories and ideas.
Temperature: 85
Memory: Enabled
```

## 🚢 Deploy to Production

**Railway** (Easiest)
```bash
railway up
```

**DigitalOcean** (Affordable)
- Use App Platform
- Connect GitHub repo
- Deploy!

**Docker** (Flexible)
```bash
docker-compose up -d
```

See DEPLOYMENT.md for detailed instructions!

---

**That's it!** You now have a fully functional AI bot platform. 🎉

For more details, see:
- USAGE_GUIDE.md - Detailed usage instructions
- CLAUDE_MODELS_GUIDE.md - Claude models guide (NEW!)
- GPT5_GUIDE.md - GPT-5 integration guide
- DEPLOYMENT.md - Production deployment guide
- README.md - Project overview
