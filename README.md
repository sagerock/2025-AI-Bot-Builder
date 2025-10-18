# AI Bot Builder Platform

A streamlined platform for creating and deploying AI chatbots with ease. Build bots connected to Anthropic Claude or OpenAI, optionally integrate with Qdrant for RAG capabilities, and deploy with a simple URL or embed code.

## Features

- **Latest AI Models**: Full support for Claude 4.x (Sonnet 4.5, Haiku 4.5, Opus 4.1, Sonnet 4) and OpenAI GPT-5!
- **Anthropic Claude 4.x**: All latest models with 64K max output, extended thinking, and superior tool use
- **OpenAI GPT-5**: Complete integration with GPT-5 (128K output) and GPT-5 Mini with configurable reasoning
- **OCR Support**: Upload scanned documents (up to 25 MB) with automatic text extraction
- **RAG Integration**: Connect bots to Qdrant vector databases for knowledge retrieval with full document mode
- **Session Memory**: Optional conversation history tracking
- **Easy Deployment**: Each bot gets a unique URL and embeddable widget code
- **Simple Management**: Clean admin interface for bot CRUD operations
- **Lightweight**: No complex flow builders, just the essentials

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
```

### 2. Run the Application

```bash
# Start the API server
uvicorn app.main:app --reload --port 8000
```

Visit:
- Admin Dashboard: http://localhost:8000/admin
- API Docs: http://localhost:8000/docs

### 3. Create Your First Bot

1. Go to the admin dashboard
2. Click "Create New Bot"
3. Fill in:
   - Bot name
   - AI provider (Anthropic/OpenAI)
   - API key
   - System prompt
   - Optional: Qdrant collection for RAG
4. Get your bot URL and embed code!

## Project Structure

```
AI Bot Builder/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   └── static/              # Frontend files
├── requirements.txt
├── .env.example
├── README.md
├── GPT5_GUIDE.md            # GPT-5 integration guide
└── ...
```

## Deployment

### Docker (Recommended)

```bash
docker-compose up -d
```

### Manual Deployment

See `docs/deployment.md` for detailed deployment instructions for various platforms (DigitalOcean, Railway, Render, AWS).

## API Endpoints

- `GET /api/bots` - List all bots
- `POST /api/bots` - Create a new bot
- `GET /api/bots/{bot_id}` - Get bot details
- `PUT /api/bots/{bot_id}` - Update bot
- `DELETE /api/bots/{bot_id}` - Delete bot
- `POST /api/chat/{bot_id}` - Chat with a bot
- `GET /chat/{bot_id}` - Standalone chat interface

## Latest Model Support

### Anthropic Claude 4.x ⭐

The platform fully supports the latest Claude 4 generation models:

| Model | API Name | Context | Max Output | Output Price | Best For |
|-------|----------|---------|------------|--------------|----------|
| **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | 200K (1M beta) | 64K | $15/MTok | Complex agents, coding, autonomous tasks |
| **Haiku 4.5** | `claude-haiku-4-5-20250514` | 200K | 64K | $5/MTok | Fast, cost-efficient, high-volume tasks |
| **Opus 4.1** | `claude-opus-4-1-20250514` | 200K | 32K | $75/MTok | Specialized reasoning, exceptional tasks |
| **Sonnet 4** | `claude-sonnet-4-20250514` | 200K | 64K | $15/MTok | General purpose, balanced tasks |

**Key Features (All Claude 4.x):**
- ✅ Extended thinking capability
- ✅ Priority tier access
- ✅ Vision support
- ✅ Superior tool use
- ✅ Multilingual
- ✅ Knowledge cutoff: Jan 2025

**Plus support for:** Claude 3.7, 3.5, and 3 models

📖 See `CLAUDE_MODELS_GUIDE.md` for complete documentation

### OpenAI GPT-5 🚀

Full support for OpenAI's latest GPT-5 reasoning models:

| Model | API Name | Context | Max Output | Output Price | Best For |
|-------|----------|---------|------------|--------------|----------|
| **GPT-5** | `gpt-5` | 400K | 128K | $10/MTok | Advanced reasoning, complex tasks |
| **GPT-5 Mini** | `gpt-5-mini` | 400K | 128K | $2/MTok | Cost-efficient reasoning |

**Key Features:**
- ✅ Automatic Responses API routing
- ✅ Configurable reasoning effort (minimal, low, medium, high)
- ✅ Configurable text verbosity (low, medium, high)
- ✅ Extended reasoning capabilities
- ✅ Superior coding performance

📖 See `GPT5_GUIDE.md` for complete documentation

### Quick Model Selection Guide

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| **Autonomous coding agents** | Claude Sonnet 4.5 | Best coding, tool use, agents |
| **Complex analysis** | Claude Opus 4.1 | Exceptional reasoning |
| **General chatbot** | Claude Sonnet 4 | Balanced intelligence & speed |
| **High-volume tasks** | Claude Haiku 4.5 | Fast & affordable (64K output) |
| **Advanced reasoning** | GPT-5 | Superior reasoning with 128K output |
| **Cost-efficient reasoning** | GPT-5 Mini | Budget-friendly with full GPT-5 capabilities |

## License

MIT
