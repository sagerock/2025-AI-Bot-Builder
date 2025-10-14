# Usage Guide

Quick guide to creating and deploying your AI bots.

## Getting Started

### 1. Start the Server

**Option A: Quick Start Script**
```bash
./start.sh
```

**Option B: Manual Start**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Option C: Docker**
```bash
docker-compose up -d
```

### 2. Access Admin Dashboard

Open your browser and go to: **http://localhost:8000/admin**

## Creating Your First Bot

### Step 1: Click "Create New Bot"

### Step 2: Fill in Basic Information

- **Bot Name**: Give your bot a descriptive name (e.g., "Customer Support Bot")
- **Description**: Optional description for your reference
- **AI Provider**: Choose between Anthropic (Claude) or OpenAI (GPT)
- **Model**: Select the AI model
  - Anthropic: claude-3-5-sonnet-20241022 (recommended), claude-3-opus, etc.
  - OpenAI: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
- **API Key**: Enter your Anthropic or OpenAI API key

### Step 3: Configure Bot Behavior

- **System Prompt**: Define how your bot should behave
  - Example: "You are a helpful customer support assistant for Acme Corp. Be friendly and professional."
- **Temperature** (0-100): Controls randomness
  - 0 = Very focused and deterministic
  - 100 = More creative and varied
  - Recommended: 70
- **Max Tokens**: Maximum response length (1024 is a good default)

### Step 4: Optional - Enable RAG (Qdrant)

If you want your bot to access a knowledge base:

1. Check "Use Qdrant (RAG)"
2. Enter your Qdrant collection name
3. Set "Top K Results" (how many relevant documents to retrieve)

**Note**: You need to have Qdrant running and your documents already indexed in a collection.

### Step 5: Configure Widget Appearance

- **Widget Title**: What appears in the chat header
- **Widget Color**: Choose your brand color
- **Widget Greeting**: Optional welcome message

### Step 6: Save Your Bot

Click "Save Bot" - your bot is now ready!

## Deploying Your Bot

After creating a bot, click "Get Code" to see deployment options:

### Option 1: Standalone Chat Page

You'll get a URL like:
```
https://yourdomain.com/chat/abc123
```

Share this URL with anyone - they can chat with your bot directly in their browser.

### Option 2: Embed Widget

Copy the embed code:
```html
<script src="https://yourdomain.com/static/widget.js" data-bot-id="abc123"></script>
```

Paste this into any website, just before the closing `</body>` tag. A chat widget will appear in the bottom-right corner.

## Real-World Examples

### Example 1: Simple Customer Support Bot

```
Name: Customer Support
Provider: Anthropic
Model: claude-3-5-sonnet-20241022
System Prompt: You are a customer support agent for Acme Corp. Help customers with:
- Order status inquiries
- Product information
- Return policies
- General questions
Be helpful, friendly, and professional.
Temperature: 70
Memory: Enabled
RAG: Disabled
```

### Example 2: Product Knowledge Bot with RAG

```
Name: Product Expert
Provider: Anthropic
Model: claude-3-5-sonnet-20241022
System Prompt: You are a product expert. Use the provided documentation to answer questions accurately. If you don't find relevant information, say so.
Temperature: 50
Memory: Enabled
RAG: Enabled
Qdrant Collection: product-docs
Top K: 5
```

### Example 3: Creative Writing Assistant

```
Name: Writing Helper
Provider: OpenAI
Model: gpt-4
System Prompt: You are a creative writing assistant. Help users with:
- Story ideas
- Character development
- Plot suggestions
- Writing tips
Be creative and encouraging!
Temperature: 85
Memory: Enabled
RAG: Disabled
```

## Managing Bots

### Edit a Bot
1. Click "Edit" on any bot card
2. Make your changes
3. Click "Save Bot"

### Delete a Bot
1. Click "Delete" on any bot card
2. Confirm deletion
3. Bot and all its conversations are removed

### Get Deployment Code
1. Click "Get Code" on any bot card
2. Copy the standalone URL or embed code
3. Share or embed on your website

## API Usage (Advanced)

### Chat with a Bot via API

```bash
curl -X POST https://yourdomain.com/api/chat/{bot_id} \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "session_id": "optional-session-id"
  }'
```

Response:
```json
{
  "response": "Hi! How can I help you today?",
  "session_id": "abc123",
  "rag_context": null
}
```

### List All Bots

```bash
curl https://yourdomain.com/api/bots
```

### Get Bot Details

```bash
curl https://yourdomain.com/api/bots/{bot_id}
```

### Update Bot

```bash
curl -X PUT https://yourdomain.com/api/bots/{bot_id} \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "New system prompt"
  }'
```

## Setting up Qdrant for RAG

### 1. Start Qdrant (if using Docker Compose)

Qdrant is already included in docker-compose.yml

### 2. Index Your Documents

You'll need to write a script to index your documents. Here's a simple example:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Connect to Qdrant
client = QdrantClient(url="http://localhost:6333")

# Create collection
client.create_collection(
    collection_name="my-docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# Add documents (you need to generate embeddings first)
points = [
    PointStruct(
        id=1,
        vector=[0.1, 0.2, ...],  # Your embedding vector
        payload={
            "text": "Your document content here",
            "metadata": "any additional info"
        }
    )
]

client.upsert(collection_name="my-docs", points=points)
```

### 3. Use in Bot

When creating your bot:
1. Check "Use Qdrant"
2. Set collection name to "my-docs"
3. Set Top K to 5 (or however many relevant docs you want)

Now your bot will automatically retrieve relevant documents when answering questions!

## Tips and Best Practices

### System Prompts
- Be specific about the bot's role and capabilities
- Include examples if helpful
- Set boundaries (what the bot should NOT do)
- Define the tone (professional, casual, friendly, etc.)

### Temperature Settings
- **0-30**: Very focused, good for factual Q&A
- **40-70**: Balanced, good for general chatbots
- **70-100**: Creative, good for brainstorming

### Conversation Memory
- Enable for multi-turn conversations
- Disable for simple single-question bots
- Adjust max messages based on context window needs

### RAG Best Practices
- Use clear, well-structured documents
- Keep document chunks reasonably sized (200-500 words)
- Use good metadata for filtering
- Test retrieval quality before deployment

### API Keys
- Never commit API keys to version control
- Use environment variables or .env file
- Consider using separate keys per bot for cost tracking
- Monitor API usage regularly

### Performance
- Start with SQLite for testing
- Switch to PostgreSQL for production
- Enable Redis for better session management
- Monitor response times

### Security
- Change default SECRET_KEY and ADMIN_PASSWORD
- Use HTTPS in production
- Implement rate limiting if needed
- Monitor for abuse

## Troubleshooting

### Bot Not Responding
1. Check API key is valid
2. Check API provider status (Anthropic/OpenAI)
3. Check logs for errors
4. Verify bot is active

### RAG Not Working
1. Check Qdrant is running: `curl http://localhost:6333/collections`
2. Verify collection exists and has data
3. Check collection name matches exactly
4. Ensure embeddings are generated correctly

### Widget Not Appearing
1. Check embed code is correct
2. Verify bot_id is correct
3. Check browser console for errors
4. Ensure server is accessible from your website

### Database Errors
1. Check database file permissions
2. Verify DATABASE_URL is correct
3. Try deleting and recreating database
4. Check disk space

## Getting API Keys

### Anthropic (Claude)
1. Go to https://console.anthropic.com
2. Sign up / Log in
3. Go to API Keys section
4. Create a new API key
5. Copy and save it securely

### OpenAI (GPT)
1. Go to https://platform.openai.com
2. Sign up / Log in
3. Go to API Keys section
4. Create a new API key
5. Copy and save it securely

## Next Steps

1. **Create your first bot** - Start simple with a basic chatbot
2. **Test it out** - Use the standalone URL to test functionality
3. **Embed on your site** - Add the widget code to your website
4. **Monitor usage** - Check logs and adjust settings as needed
5. **Add more bots** - Create specialized bots for different use cases

## Support Resources

- **API Documentation**: http://localhost:8000/docs
- **Deployment Guide**: See DEPLOYMENT.md
- **Anthropic Docs**: https://docs.anthropic.com
- **OpenAI Docs**: https://platform.openai.com/docs
- **Qdrant Docs**: https://qdrant.tech/documentation

Enjoy building your AI bots! 🤖
