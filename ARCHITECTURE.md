# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Your Clients                         │
│  (Website visitors, customers, users)                        │
└────────────────┬──────────────────┬─────────────────────────┘
                 │                  │
                 │                  │
        ┌────────▼────────┐  ┌─────▼──────┐
        │ Embed Widget    │  │ Chat Page  │
        │ (widget.js)     │  │ (chat.html)│
        └────────┬────────┘  └─────┬──────┘
                 │                  │
                 └──────────┬───────┘
                            │
                    ┌───────▼────────┐
                    │   FastAPI      │
                    │  (app/main.py) │
                    └───────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐
        │ Bot API   │ │ Chat API │ │  Admin   │
        │ (bots.py) │ │(chat.py) │ │(admin UI)│
        └─────┬─────┘ └────┬─────┘ └──────────┘
              │             │
              └──────┬──────┘
                     │
           ┌─────────▼──────────┐
           │   Service Layer    │
           │  - Bot Service     │
           │  - Chat Service    │
           │  - Memory Service  │
           │  - Qdrant Service  │
           └─────────┬──────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼────┐  ┌───▼─────┐
   │Database │  │ AI API │  │ Qdrant  │
   │(SQLite/ │  │Anthropic│  │(Vector  │
   │Postgres)│  │ OpenAI │  │  DB)    │
   └─────────┘  └────────┘  └─────────┘
```

## Request Flow

### 1. Creating a Bot

```
Admin Dashboard (admin.html)
    │
    │ POST /api/bots
    │ {name, provider, api_key, prompt, ...}
    ▼
Bot API (api/bots.py)
    │
    │ validate request
    ▼
Bot Service (services/bot_service.py)
    │
    │ create bot record
    ▼
Database
    │
    │ return bot_id & config
    ▼
Admin Dashboard
    │
    │ show deployment codes
    │ - URL: /chat/{bot_id}
    │ - Embed: <script data-bot-id=...>
    └── Ready to use!
```

### 2. User Chatting with Bot

```
User (via widget or chat page)
    │
    │ "Hello, I need help"
    │
    │ POST /api/chat/{bot_id}
    │ {message: "Hello", session_id: "abc123"}
    ▼
Chat API (api/chat.py)
    │
    │ 1. Get bot config
    ▼
Bot Service
    │ get_bot(bot_id)
    ▼
Database
    │ return bot config
    │
    ▼
Memory Service
    │ 2. Get/create conversation
    │ 3. Get history (last N messages)
    ▼
Database
    │ return message history
    │
    ▼
Qdrant Service (if RAG enabled)
    │ 4. Search relevant documents
    ▼
Qdrant
    │ return top K results
    │
    ▼
Chat Service
    │ 5. Build context
    │    - System prompt
    │    - History
    │    - RAG context
    │    - User message
    │
    │ 6. Call AI provider
    ▼
Anthropic/OpenAI API
    │ AI generates response
    │
    ▼
Memory Service
    │ 7. Save user message
    │ 8. Save AI response
    ▼
Database
    │
    ▼
User
    └── Display response
```

## Component Details

### Frontend Layer

#### Admin Dashboard (admin.html)
- Pure JavaScript SPA
- Bot CRUD operations
- Code generation
- No external dependencies

#### Chat Interface (chat.html)
- Standalone chat page
- WebSocket-like feel with AJAX
- Session management
- Mobile responsive

#### Embed Widget (widget.js)
- Self-contained script
- Iframe isolation
- Customizable appearance
- Zero conflict with host page

### API Layer

#### Bot Endpoints
```python
POST   /api/bots           # Create bot
GET    /api/bots           # List bots
GET    /api/bots/{id}      # Get bot
PUT    /api/bots/{id}      # Update bot
DELETE /api/bots/{id}      # Delete bot
```

#### Chat Endpoints
```python
POST   /api/chat/{bot_id}                    # Send message
DELETE /api/chat/{bot_id}/session/{session}  # Clear history
```

### Service Layer

#### Bot Service
- Bot lifecycle management
- CRUD operations
- Data validation

#### Chat Service
- AI provider abstraction
- Message preparation
- Context building
- Response handling

#### Memory Service
- Conversation tracking
- Session management
- History retrieval
- Message persistence

#### Qdrant Service
- Vector search
- Context retrieval
- Collection management

### Data Layer

#### Database Models

**Bot**
- Configuration
- AI settings
- RAG settings
- Widget settings

**Conversation**
- Session tracking
- Bot relationship

**Message**
- User/assistant messages
- Timestamps
- RAG context

### External Services

#### AI Providers
- **Anthropic**: Claude models
- **OpenAI**: GPT models

#### Vector Database
- **Qdrant**: Document retrieval

## Data Flow Examples

### Simple Chat (No RAG, No History)

```
User: "What is Python?"
    ↓
API receives message
    ↓
Get bot config (system prompt, model, etc.)
    ↓
Send to AI:
    System: "You are a helpful assistant"
    User: "What is Python?"
    ↓
AI responds: "Python is a programming language..."
    ↓
Save to database
    ↓
Return to user
```

### Chat with Memory

```
User: "What is Python?"
    ↓
[Get history: empty]
    ↓
AI: "Python is a programming language..."
    ↓
Save both messages
    ↓
---
User: "What are its benefits?"
    ↓
[Get history: previous Q&A]
    ↓
Send to AI:
    History: Q&A about Python
    User: "What are its benefits?"
    ↓
AI: "Python's benefits include..." (context-aware)
```

### Chat with RAG

```
User: "What is your refund policy?"
    ↓
Search Qdrant for "refund policy"
    ↓
Get relevant docs:
    1. "We offer 30-day refunds..."
    2. "To request a refund..."
    ↓
Send to AI:
    System: "Use docs to answer"
    Context: [refund policy docs]
    User: "What is your refund policy?"
    ↓
AI: "Based on our policy, we offer..." (accurate)
```

### Chat with RAG + Memory

```
User: "What is your refund policy?"
    ↓
[History: empty]
[RAG: Get refund docs]
    ↓
AI: "We offer 30-day refunds..."
    ↓
Save messages
    ↓
---
User: "How do I request one?"
    ↓
[History: Previous Q&A]
[RAG: Get refund request docs]
    ↓
AI: "To request a refund from our 30-day policy..." (context + history)
```

## Security Architecture

```
┌─────────────────────────────────────┐
│         Security Layers             │
├─────────────────────────────────────┤
│ 1. CORS                             │
│    - Allowed origins only           │
├─────────────────────────────────────┤
│ 2. Input Validation                 │
│    - Pydantic schemas               │
├─────────────────────────────────────┤
│ 3. API Key Storage                  │
│    - Per-bot keys                   │
│    - Hidden in responses            │
├─────────────────────────────────────┤
│ 4. Environment Variables            │
│    - Secret keys                    │
│    - Database credentials           │
├─────────────────────────────────────┤
│ 5. Session Isolation                │
│    - UUID-based sessions            │
│    - No cross-contamination         │
└─────────────────────────────────────┘
```

## Scaling Architecture

### Current (Single Container)
```
Internet → Load Balancer → Container → Database
                              ↓
                           Qdrant
```

### Scaled (Multiple Containers)
```
                    ┌→ Container 1 ┐
Internet → Load     ├→ Container 2 ├→ PostgreSQL
           Balancer ├→ Container 3 ├→ Redis
                    └→ Container N ┘
                           ↓
                    Qdrant Cluster
```

## Technology Choices Explained

### Why FastAPI?
- Modern Python framework
- Async support (better performance)
- Auto-generated API docs
- Type hints & validation
- Easy to learn

### Why SQLAlchemy?
- ORM abstraction
- Multiple database support
- Migration support
- Pythonic queries

### Why Pydantic?
- Data validation
- Type safety
- Auto-documentation
- Integration with FastAPI

### Why Vanilla JS?
- No build step
- Zero dependencies
- Fast loading
- Easy maintenance
- No framework lock-in

### Why Qdrant?
- Purpose-built for vectors
- Better than Flowise integration
- Fast similarity search
- Cloud option available
- Good Python client

## Deployment Architecture

### Development
```
localhost:8000 → SQLite
```

### Production (Simple)
```
Domain → SSL → Container → PostgreSQL
                   ↓
                Qdrant Cloud
```

### Production (Advanced)
```
Domain → CDN (static files)
    ↓
  SSL/Load Balancer
    ↓
  ┌───────────────┐
  │ Container 1-N │ → PostgreSQL (managed)
  └───────────────┘ → Redis (managed)
         ↓
    Qdrant (managed)
```

## Monitoring Points

```
┌─────────────────────────────────┐
│      What to Monitor            │
├─────────────────────────────────┤
│ • Response times                │
│ • Error rates                   │
│ • API costs (Anthropic/OpenAI)  │
│ • Database size                 │
│ • Active sessions               │
│ • Bot usage (per bot)           │
│ • Message volume                │
│ • RAG retrieval quality         │
└─────────────────────────────────┘
```

## Summary

This architecture provides:

✅ **Simplicity** - Easy to understand and modify
✅ **Scalability** - Can handle growth
✅ **Maintainability** - Clean separation of concerns
✅ **Flexibility** - Easy to extend
✅ **Security** - Multiple protection layers
✅ **Performance** - Async operations, caching-ready
✅ **Reliability** - Error handling, logging

The design follows best practices:
- **Separation of concerns** - API, Service, Data layers
- **Dependency injection** - Easy testing
- **Single responsibility** - Each component has one job
- **DRY** - Don't repeat yourself
- **Configuration over code** - Environment variables
