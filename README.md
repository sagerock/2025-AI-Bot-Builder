# AI Bot Builder Platform

A streamlined platform for creating and deploying AI chatbots with ease. Build bots connected to Anthropic Claude or OpenAI, optionally integrate with Qdrant for RAG capabilities, and deploy with a simple URL or embed code.

## Features

- **Latest AI Models**: Full support for Claude 4 (Sonnet 4.5, Opus 4.1, Sonnet 4, Opus 4) and OpenAI GPT-5!
- **Anthropic Claude**: All Claude models including latest Claude 4 generation with superior coding and reasoning
- **OpenAI GPT-5**: Complete integration with GPT-5 reasoning models with configurable effort and verbosity
- **RAG Integration**: Connect bots to Qdrant vector databases for knowledge retrieval
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

### Anthropic Claude 4
The platform fully supports the latest Claude 4 models:
- **Claude Sonnet 4.5** - Best for complex agents and coding
- **Claude Opus 4.1** - Exceptional for specialized complex tasks
- **Claude Sonnet 4** - High intelligence and speed balance
- **Plus all Claude 3.7, 3.5, and 3 models**

See `CLAUDE_MODELS_GUIDE.md` for detailed documentation.

### OpenAI GPT-5
Full support for OpenAI's GPT-5 reasoning models:
- Automatic Responses API routing
- Configurable reasoning effort (minimal, low, medium, high)
- Configurable text verbosity (low, medium, high)
- All GPT-5 variants: gpt-5, gpt-5-mini, gpt-5-nano

See `GPT5_GUIDE.md` for detailed documentation.

## License

MIT
