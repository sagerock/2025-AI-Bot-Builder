# GPT-5 Integration Guide

This guide covers how to use OpenAI's GPT-5 models in the AI Bot Builder platform.

## What is GPT-5?

GPT-5 is OpenAI's most intelligent model yet, specifically trained to excel at:
- **Code generation, bug fixing, and refactoring**
- **Instruction following**
- **Long context and tool calling**
- **Complex reasoning and agentic tasks**

## GPT-5 Models Available

The platform supports all GPT-5 variants:

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| **gpt-5** | Complex reasoning, broad world knowledge, code-heavy tasks | Slower | Higher |
| **gpt-5-mini** | Balanced speed, cost, and capability | Medium | Medium |
| **gpt-5-nano** | High-throughput, simple tasks, classification | Fast | Lower |
| **gpt-5-chat-latest** | Latest chat-optimized version | Medium | Medium |

## Key Differences from GPT-4

### 1. Reasoning Models
GPT-5 models are **reasoning models** - they generate an internal "chain of thought" before responding. This makes them:
- More accurate for complex problems
- Better at multi-step reasoning
- More reliable for code generation

### 2. New API (Responses API)
GPT-5 uses OpenAI's new **Responses API** instead of Chat Completions. The platform automatically handles this for you - just select a GPT-5 model and everything works seamlessly.

### 3. No Temperature Setting
GPT-5 models **do not support** the `temperature`, `top_p`, or `logprobs` parameters. Instead, you control output through:
- **Reasoning Effort** - How much the model "thinks"
- **Text Verbosity** - How detailed the responses are

## GPT-5 Settings

### Reasoning Effort

Controls how many reasoning tokens the model generates before producing a response.

| Setting | Use Case | Speed | Quality |
|---------|----------|-------|---------|
| **Minimal** | Fastest time-to-first-token, simple tasks | ⚡️⚡️⚡️⚡️ | ⭐️⭐️ |
| **Low** | Quick responses with basic reasoning | ⚡️⚡️⚡️ | ⭐️⭐️⭐️ |
| **Medium** | Balanced (default) | ⚡️⚡️ | ⭐️⭐️⭐️⭐️ |
| **High** | Most thorough reasoning, complex problems | ⚡️ | ⭐️⭐️⭐️⭐️⭐️ |

**When to use each:**
- **Minimal**: Code generation, instruction following, SQL queries, simple Q&A
- **Low**: General chatbots, quick customer support
- **Medium**: Most use cases (default)
- **High**: Complex reasoning, research, debugging, architecture design

### Text Verbosity

Controls how many output tokens are generated (response length).

| Setting | Use Case | Response Length |
|---------|----------|-----------------|
| **Low** | Concise answers, simple code | Short |
| **Medium** | Balanced explanations (default) | Medium |
| **High** | Detailed explanations, extensive refactoring | Long |

**When to use each:**
- **Low**: SQL queries, simple Q&A, concise code snippets
- **Medium**: Most use cases, general chatbots
- **High**: Documentation, code reviews, detailed tutorials

## Creating a GPT-5 Bot

### Step 1: Select OpenAI Provider
In the admin dashboard, select "OpenAI (GPT)" as the provider.

### Step 2: Choose GPT-5 Model
Select one of the GPT-5 models:
- **gpt-5** for most intelligent responses
- **gpt-5-mini** for balanced performance
- **gpt-5-nano** for speed

### Step 3: Configure GPT-5 Settings

**For Fast, Concise Responses:**
```
Reasoning Effort: Minimal
Text Verbosity: Low
```

**For Balanced Performance (Recommended):**
```
Reasoning Effort: Medium
Text Verbosity: Medium
```

**For Complex Tasks:**
```
Reasoning Effort: High
Text Verbosity: High
```

### Step 4: Write Your Prompt

GPT-5 works best with clear, specific prompts:

**Good GPT-5 Prompt:**
```
You are a code assistant specializing in Python. Help users with:
- Writing clean, efficient code
- Debugging errors
- Refactoring for better performance

Before calling tools, explain why you're calling them.
Think step-by-step through complex problems.
```

**Tips:**
- Be explicit about the bot's role
- Encourage step-by-step thinking for complex tasks
- For minimal reasoning, prompt it to "think" or outline steps

## Example Bots

### 1. Code Generation Bot (Fast)

```yaml
Name: Quick Code Generator
Model: gpt-5-nano
Reasoning Effort: Minimal
Text Verbosity: Low
System Prompt: |
  You are a Python code generator. Generate clean, working code.
  Be concise. Include brief comments only when necessary.
```

**Best for:** Quick code snippets, SQL queries, simple functions

### 2. Coding Assistant (Balanced)

```yaml
Name: Coding Assistant
Model: gpt-5
Reasoning Effort: Medium
Text Verbosity: Medium
System Prompt: |
  You are an expert coding assistant. Help with:
  - Writing clean, maintainable code
  - Debugging and fixing errors
  - Code reviews and suggestions

  Think through problems step by step.
  Explain your reasoning when helpful.
```

**Best for:** General development assistance, debugging, code reviews

### 3. Architecture Advisor (Complex)

```yaml
Name: Software Architect
Model: gpt-5
Reasoning Effort: High
Text Verbosity: High
System Prompt: |
  You are a senior software architect. Help users with:
  - System design and architecture decisions
  - Scalability and performance optimization
  - Best practices and design patterns

  Analyze problems thoroughly.
  Consider multiple approaches.
  Provide detailed explanations and trade-offs.
```

**Best for:** Complex architectural decisions, design reviews, refactoring

### 4. Customer Support Bot (Fast & Friendly)

```yaml
Name: Support Assistant
Model: gpt-5-mini
Reasoning Effort: Low
Text Verbosity: Low
System Prompt: |
  You are a helpful customer support agent for Acme Corp.
  Be friendly, concise, and professional.
  Answer questions about products, orders, and policies.
```

**Best for:** Quick customer inquiries, FAQ responses

### 5. RAG-Enhanced Knowledge Bot

```yaml
Name: Documentation Assistant
Model: gpt-5
Reasoning Effort: Medium
Text Verbosity: Medium
RAG: Enabled
Qdrant Collection: docs-collection
System Prompt: |
  You are a documentation expert. Use the provided context to answer questions.
  If context doesn't contain the answer, say so.
  Be accurate and cite specific details from the documentation.
```

**Best for:** Knowledge base queries, documentation Q&A

## Migration Guide

### From GPT-4 to GPT-5

If you have existing GPT-4 bots, here's how to migrate:

**GPT-4 Bot:**
```yaml
Model: gpt-4
Temperature: 70
Max Tokens: 1024
```

**→ GPT-5 Equivalent:**
```yaml
Model: gpt-5
Reasoning Effort: Minimal or Low
Text Verbosity: Low or Medium
Max Tokens: 1024
```

**Prompt Updates:**
- GPT-5 follows instructions better - you may need less prompting
- Test with `minimal` reasoning first
- Increase to `low` if quality isn't sufficient
- Consider using the prompt optimizer (see below)

### From o3 to GPT-5

If you used o3 (previous reasoning model):

**o3 Bot:**
```yaml
Model: o3
Reasoning: Medium
```

**→ GPT-5 Equivalent:**
```yaml
Model: gpt-5
Reasoning Effort: Medium or High
Text Verbosity: Medium
```

Start with `medium` reasoning and tune your prompts. Increase to `high` if needed.

## Best Practices

### 1. Start with Lower Settings
- Begin with `minimal` or `low` reasoning
- Use `low` or `medium` verbosity
- Only increase if quality isn't good enough

### 2. Match Settings to Task

| Task Type | Reasoning | Verbosity |
|-----------|-----------|-----------|
| SQL queries | Minimal | Low |
| Simple code | Minimal | Low |
| Chatbots | Low | Medium |
| Debugging | Medium | Medium |
| Architecture | High | High |
| Research | High | High |

### 3. Prompt for Reasoning (at Minimal)

When using `minimal` reasoning, encourage the model to think:

```
Before answering, think through:
1. What is the user asking?
2. What information do I need?
3. What's the best approach?

Then provide your answer.
```

### 4. Use Preambles for Tools

If using tools/functions, ask the model to explain before calling:

```
Before calling any tool, briefly explain why you're calling it.
```

This improves tool-calling accuracy.

### 5. Test and Iterate

GPT-5 is different from GPT-4. Test your bots and adjust:
- Try different reasoning levels
- Adjust verbosity based on response length
- Refine prompts based on output quality

## Common Issues

### Responses Too Slow
**Solution:** Lower reasoning effort to `minimal` or `low`

### Responses Too Short
**Solution:** Increase verbosity to `medium` or `high`, or prompt for more detail

### Not Following Instructions
**Solution:** Increase reasoning to `low` or `medium`, make prompts more explicit

### Too Verbose
**Solution:** Lower verbosity to `low`, or prompt for conciseness

### Code Not Detailed Enough
**Solution:** Increase verbosity to `high` for detailed code with explanations

## Prompt Optimizer

OpenAI provides a prompt optimizer that automatically updates prompts for GPT-5 best practices. Consider using it to optimize your existing prompts.

## Cost Optimization

GPT-5 pricing depends on:
- **Model variant** (gpt-5 > gpt-5-mini > gpt-5-nano)
- **Reasoning tokens** (higher effort = more tokens)
- **Output tokens** (higher verbosity = more tokens)

**To reduce costs:**
1. Use `gpt-5-mini` or `gpt-5-nano` when possible
2. Use `minimal` or `low` reasoning for simple tasks
3. Use `low` verbosity for concise responses
4. Enable conversation memory to reduce re-reasoning

## Technical Details

### API Routing

The platform automatically detects GPT-5 models and routes to the correct API:

- **GPT-5 models** → OpenAI Responses API
- **GPT-4/GPT-3.5 models** → OpenAI Chat Completions API
- **Claude models** → Anthropic Messages API

You don't need to do anything - just select the model!

### Conversation History

For GPT-5, the platform passes conversation history as part of the input string, formatted clearly for the model to understand context.

### RAG Integration

RAG works seamlessly with GPT-5. Relevant context is included in the input, and the reasoning model determines how to use it.

## Example API Usage

If you're using the API directly:

```bash
# Chat with GPT-5 bot
curl -X POST https://yourdomain.com/api/chat/BOT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function to calculate Fibonacci",
    "session_id": "user123"
  }'
```

The platform handles all GPT-5 specifics internally!

## Troubleshooting

### Error: "temperature not supported"
**Cause:** GPT-5 doesn't use temperature
**Solution:** This is normal - the platform handles it automatically

### Error: "responses.create not found"
**Cause:** OpenAI Python SDK version too old
**Solution:** Update SDK: `pip install --upgrade openai`

### Slow responses
**Cause:** High reasoning effort
**Solution:** Lower to `minimal` or `low` in bot settings

### Unexpected response format
**Cause:** GPT-5 processes input differently
**Solution:** Update your system prompt for GPT-5, be more explicit

## Further Reading

- [OpenAI GPT-5 Documentation](https://platform.openai.com/docs/models/gpt-5)
- [Responses API Guide](https://platform.openai.com/docs/api-reference/responses)
- [GPT-5 Prompting Guide](https://platform.openai.com/docs/guides/prompting-gpt5)
- [Migration from GPT-4](https://platform.openai.com/docs/guides/migration)

## Summary

GPT-5 is now fully integrated into the AI Bot Builder platform:

✅ All GPT-5 models supported (gpt-5, gpt-5-mini, gpt-5-nano)
✅ Automatic Responses API routing
✅ Reasoning effort control (minimal, low, medium, high)
✅ Text verbosity control (low, medium, high)
✅ Works with RAG and conversation memory
✅ Backward compatible with GPT-4/3.5

**To get started:** Create a new bot, select a GPT-5 model, configure reasoning/verbosity, and deploy!
