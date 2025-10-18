# Claude Models Guide

Complete guide to using Anthropic's latest Claude models in the AI Bot Builder platform.

## Available Claude Models

The platform now supports all current Anthropic Claude models, including the latest Claude 4 generation.

### Claude 4.x (Latest Generation) ⭐ **Current Recommended**

| Model | API Name | Best For | Context | Max Output | Input Price | Output Price |
|-------|----------|----------|---------|------------|-------------|--------------|
| **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | Complex agents, coding, autonomous tasks | 200K (1M beta) | **64K** | $3/MTok | $15/MTok |
| **Haiku 4.5** | `claude-haiku-4-5-20250514` | Fast, cost-efficient, high-volume tasks | 200K | **64K** | $0.80/MTok | $5/MTok |
| **Opus 4.1** | `claude-opus-4-1-20250514` | Specialized reasoning, exceptional tasks | 200K | **32K** | $15/MTok | $75/MTok |
| **Sonnet 4** | `claude-sonnet-4-20250514` | General purpose, balanced tasks | 200K | **64K** | $3/MTok | $15/MTok |

**Knowledge Cutoffs:**
- Sonnet 4.5: Jan 2025
- Haiku 4.5: Feb 2025
- Opus 4.1: Jan 2025
- Sonnet 4: Jan 2025

**Key Features (All Claude 4.x):**
- ✅ Extended thinking capability
- ✅ Priority tier access
- ✅ Vision support
- ✅ Superior tool use
- ✅ Multilingual
- ✅ Up to 1M context (beta, Sonnet models)

### Claude 3.7 (Extended Thinking)

| Model | Best For | Context | Max Output | Knowledge Cutoff |
|-------|----------|---------|------------|------------------|
| **Claude Sonnet 3.7** | High intelligence with toggleable extended thinking | 200K | 128K tokens (with beta) | Oct 2024 |

### Claude 3.5 (Previous Generation)

| Model | Best For | Context | Max Output | Knowledge Cutoff |
|-------|----------|---------|------------|------------------|
| **Claude 3.5 Sonnet** | High-performance general tasks | 200K | 8K tokens | Jul 2024 |
| **Claude 3.5 Haiku** | Fast responses at lower cost | 200K | 8K tokens | Jul 2024 |

### Claude 3 (Legacy)

| Model | Best For | Context | Max Output |
|-------|----------|---------|------------|
| **Claude 3 Opus** | Complex tasks (legacy) | 200K | 4K tokens |
| **Claude 3 Sonnet** | Balanced performance (legacy) | 200K | 4K tokens |
| **Claude 3 Haiku** | Fast and compact (legacy) | 200K | 4K tokens |

## Model Selection Guide

### When to Use Each Model

#### Claude Sonnet 4.5 ⭐ **Recommended for most use cases**
```yaml
Best for:
- Autonomous coding agents
- Complex multi-agent frameworks
- Cybersecurity automation
- Long-running autonomous tasks
- Advanced tool orchestration
- Complex financial analysis
- Multi-hour research tasks

Strengths:
- Highest intelligence across most tasks
- Exceptional agent capabilities
- Best coding performance
- Superior tool use
```

**Example Bot Configuration:**
```yaml
Name: Advanced Coding Agent
Model: claude-sonnet-4-5-20250929
Temperature: 70
Max Tokens: 4096
System Prompt: |
  You are an expert coding agent specializing in:
  - Autonomous code generation and refactoring
  - Bug detection and fixes
  - Architecture design
  - Code reviews

  Use tools when needed. Think through problems systematically.
```

#### Claude Opus 4.1
```yaml
Best for:
- Highly complex codebase refactoring
- Nuanced creative writing
- Specialized scientific analysis
- Tasks requiring exceptional reasoning

Strengths:
- Superior reasoning capabilities
- Exceptional for specialized tasks
- Nuanced understanding
```

**Example Bot Configuration:**
```yaml
Name: Research Analyst
Model: claude-opus-4-1-20250514
Temperature: 60
Max Tokens: 4096
System Prompt: |
  You are a specialized research analyst. Provide:
  - Deep, thorough analysis
  - Nuanced interpretations
  - Evidence-based conclusions
  - Multiple perspectives on complex topics
```

#### Claude Sonnet 4
```yaml
Best for:
- Complex customer chatbot inquiries
- General code generation
- Data analysis
- General agentic tasks

Strengths:
- High intelligence
- Fast response times
- Balanced performance
```

**Example Bot Configuration:**
```yaml
Name: Customer Support Agent
Model: claude-sonnet-4-20250514
Temperature: 70
Max Tokens: 2048
System Prompt: |
  You are a helpful customer support agent for [Company].
  Handle complex inquiries with:
  - Clear explanations
  - Empathy and professionalism
  - Problem-solving approach
```

#### Claude Haiku 4.5 (Fastest & Most Affordable)
```yaml
Best for:
- Basic customer support
- High volume formulaic content
- Straightforward data extraction
- Quick responses needed
- Cost-sensitive applications
- Long-form content generation

Strengths:
- Blazing fast responses
- Low cost ($5/MTok output)
- 64K max output (8x more than 3.5 Haiku)
- Extended thinking capability
- Better intelligence than 3.5
```

**Example Bot Configuration:**
```yaml
Name: Quick FAQ Bot
Model: claude-haiku-4-5-20250514
Temperature: 50
Max Tokens: 4096
System Prompt: |
  You are a quick-response FAQ assistant.
  Answer questions concisely and accurately.
  Stick to known information.
```

## Choosing the Right Model

### Option 1: Start with Fast & Cost-Effective (Recommended for most)

**Start here if:**
- Initial prototyping
- Tight latency requirements
- Cost-sensitive
- High-volume straightforward tasks

**Path:**
```
1. Start: Claude Haiku 4.5
2. Test thoroughly
3. Upgrade only if needed (Sonnet 4 or 4.5)
```

### Option 2: Start with Most Capable

**Start here if:**
- Complex reasoning required
- Scientific/mathematical applications
- Accuracy outweighs cost
- Advanced coding needs
- Autonomous agents

**Path:**
```
1. Start: Claude Sonnet 4.5
2. Optimize prompts
3. Consider downgrading if simpler model works
```

## Decision Matrix

| Your Need | Recommended Model | Why |
|-----------|------------------|-----|
| **Autonomous coding agent** | Claude Sonnet 4.5 | Best coding, tool use, agents |
| **Complex analysis** | Claude Opus 4.1 | Exceptional reasoning |
| **General chatbot** | Claude Sonnet 4 | Balanced intelligence & speed |
| **Customer support** | Claude Haiku 4.5 | Fast & affordable with 64K output |
| **Content generation (high volume)** | Claude Haiku 4.5 | Cost-effective with large output |
| **Scientific research** | Claude Opus 4.1 | Deep reasoning |
| **Code generation** | Claude Sonnet 4.5 | Best for coding |
| **Quick Q&A** | Claude Haiku 4.5 | Fastest responses, better than 3.5 |
| **Multi-agent frameworks** | Claude Sonnet 4.5 | Superior orchestration |

## Feature Support

| Feature | Sonnet 4.5 | Haiku 4.5 | Opus 4.1 | Sonnet 4 | Haiku 3.5 |
|---------|------------|-----------|----------|----------|-----------|
| **Vision** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Extended Thinking** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Tool Use** | ✅ Best | ✅ | ✅ | ✅ | ✅ |
| **Max Output** | 64K | 64K | 32K | 64K | 8K |
| **200K Context** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **1M Context (beta)** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Multilingual** | ✅ | ✅ | ✅ | ✅ | ✅ |

## Creating Bots with Latest Models

### Example 1: Autonomous Coding Agent (Claude Sonnet 4.5)

```yaml
Bot Configuration:
  Name: "Code Assistant Pro"
  Provider: Anthropic
  Model: claude-sonnet-4-5-20250929
  Temperature: 70
  Max Tokens: 8192

System Prompt: |
  You are an expert autonomous coding agent. Your capabilities:

  1. Code Generation: Write clean, efficient, well-documented code
  2. Debugging: Identify and fix bugs systematically
  3. Refactoring: Improve code structure and performance
  4. Architecture: Design scalable systems
  5. Reviews: Provide constructive code reviews

  Approach:
  - Break down complex problems
  - Think through solutions step-by-step
  - Consider edge cases
  - Write tests when appropriate
  - Explain your reasoning

  Use tools when needed for file operations, searches, etc.
```

**Use Cases:**
- Building new features autonomously
- Refactoring large codebases
- Debug complex issues
- Architectural planning

### Example 2: Research & Analysis Bot (Claude Opus 4.1)

```yaml
Bot Configuration:
  Name: "Deep Research Assistant"
  Provider: Anthropic
  Model: claude-opus-4-1-20250514
  Temperature: 60
  Max Tokens: 4096
  RAG: Enabled
  Qdrant Collection: research-papers

System Prompt: |
  You are a specialized research analyst with deep expertise in:
  - Scientific analysis
  - Data interpretation
  - Critical thinking
  - Evidence synthesis

  For each query:
  1. Analyze available evidence thoroughly
  2. Consider multiple perspectives
  3. Identify gaps or limitations
  4. Provide reasoned conclusions
  5. Cite specific sources when available

  Be nuanced and thorough. Quality over speed.
```

**Use Cases:**
- Scientific literature review
- Complex data analysis
- Strategic planning
- Market research

### Example 3: Customer Support Bot (Claude Sonnet 4)

```yaml
Bot Configuration:
  Name: "Customer Care AI"
  Provider: Anthropic
  Model: claude-sonnet-4-20250514
  Temperature: 70
  Max Tokens: 2048
  Memory: Enabled
  Memory Max Messages: 15

System Prompt: |
  You are a customer support agent for Acme Corp.

  Your role:
  - Answer product questions
  - Help with troubleshooting
  - Process order inquiries
  - Provide policy information

  Style:
  - Friendly and professional
  - Patient and empathetic
  - Clear and concise
  - Solution-oriented

  If you can't help, offer to escalate to a human agent.
```

**Use Cases:**
- Complex customer inquiries
- Multi-step troubleshooting
- Product recommendations
- Order support

### Example 4: High-Volume FAQ Bot (Claude Haiku 4.5)

```yaml
Bot Configuration:
  Name: "Quick FAQ Assistant"
  Provider: Anthropic
  Model: claude-haiku-4-5-20250514
  Temperature: 50
  Max Tokens: 2048
  Memory: Disabled

System Prompt: |
  You are a FAQ assistant. Answer questions quickly and accurately.

  Topics you cover:
  - Hours and location
  - Pricing and plans
  - Basic product features
  - Contact information

  Keep responses brief and to the point.
  If question is complex, suggest contacting support.
```

**Use Cases:**
- Basic FAQ responses
- Quick information lookup
- High-volume simple queries
- Cost-sensitive deployments
- Long-form responses when needed (64K max output)

## Model-Specific Tips

### Claude Sonnet 4.5
- **Best for:** Autonomous agents, complex coding
- **Prompt tip:** Give it space to think and use tools
- **Temperature:** 60-80 for balanced creativity
- **Max tokens:** 4096+ for complex responses

### Claude Haiku 4.5
- **Best for:** Speed and volume with intelligence
- **Prompt tip:** Keep prompts focused but can handle complexity
- **Temperature:** 40-60 for consistency
- **Max tokens:** 1024-4096 (64K max available!)
- **Note:** Much better than 3.5 Haiku - can handle more nuanced tasks

### Claude Opus 4.1
- **Best for:** Deep analysis, specialized tasks
- **Prompt tip:** Encourage thorough reasoning
- **Temperature:** 50-70 for focused analysis
- **Max tokens:** 2048-4096 for detailed outputs

### Claude Sonnet 4
- **Best for:** General purpose, balanced tasks
- **Prompt tip:** Clear instructions work best
- **Temperature:** 60-80 for most uses
- **Max tokens:** 1024-2048 typical

### Claude 3.5 Haiku (Legacy)
- **Best for:** Speed and volume (consider upgrading to Haiku 4.5)
- **Prompt tip:** Keep prompts focused and simple
- **Temperature:** 40-60 for consistency
- **Max tokens:** 512-1024 for quick responses

## Cost Optimization

### Model Pricing (per million tokens)

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| Claude Sonnet 4.5 | $3 | $15 | Complex tasks worth the cost |
| Claude Haiku 4.5 | $0.80 | $5 | High volume, cost-sensitive |
| Claude Opus 4.1 | $15 | $75 | Specialized high-value tasks |
| Claude Sonnet 4 | $3 | $15 | General purpose |
| Claude 3.5 Haiku | $0.80 | $4 | Legacy high-volume tasks |

### Cost Reduction Strategies

1. **Start with Haiku** for simple tasks
2. **Use prompt caching** for repeated context
3. **Enable conversation memory** to reduce context
4. **Optimize max_tokens** to actual needs
5. **Use RAG wisely** - only when needed

## Migration Guide

### From Claude 3.5 to Claude 4

**Simple migration:**
```yaml
Before:
  Model: claude-3-5-sonnet-20241022

After:
  Model: claude-sonnet-4-5-20250929
```

**What to expect:**
- ✅ Better reasoning
- ✅ Better coding
- ✅ Better tool use
- ✅ Same API structure
- ⚠️ Slightly higher latency (but still fast)

**Prompt adjustments:**
- Claude 4 is smarter - may need less hand-holding
- Better at following complex instructions
- More capable with tools
- Test and adjust as needed

## Best Practices

### 1. Choose Model by Task Complexity

```
Simple FAQ → Claude 3.5 Haiku
Standard chatbot → Claude Sonnet 4
Complex reasoning → Claude Opus 4.1
Autonomous agents → Claude Sonnet 4.5
```

### 2. Optimize Prompts for Each Model

**For Haiku:**
- Short, focused instructions
- Clear, simple language
- Avoid complexity

**For Sonnet 4.5:**
- Detailed context okay
- Encourage tool use
- Multi-step reasoning welcome

**For Opus 4.1:**
- Thorough instructions
- Request deep analysis
- Multiple perspectives

### 3. Use RAG Appropriately

- **Sonnet 4.5**: Excellent with RAG, complex retrieval
- **Opus 4.1**: Deep analysis of retrieved content
- **Sonnet 4**: Good balance for RAG applications
- **Haiku 3.5**: Works but keep context simple

### 4. Enable Memory Strategically

- **Agents (Sonnet 4.5)**: High memory (20+ messages)
- **Support (Sonnet 4)**: Medium memory (10-15 messages)
- **FAQ (Haiku)**: Low/no memory (5 or disabled)

## Troubleshooting

### Responses Too Slow
- Switch to Haiku for speed
- Reduce max_tokens
- Simplify prompt

### Not Smart Enough
- Upgrade to Sonnet 4 or 4.5
- Add more context
- Be more specific in prompts

### Too Expensive
- Use Haiku for high-volume tasks
- Implement prompt caching
- Optimize token usage

### Tool Use Not Working Well
- Use Sonnet 4.5 (best tool use)
- Provide clear tool descriptions
- Test with simpler examples first

## Summary

The platform now supports all latest Claude models:

✅ **Claude 4.x Generation** - Latest and greatest
- **Sonnet 4.5** (`claude-sonnet-4-5-20250929`) - Best for agents & coding - 64K output, $15/MTok
- **Haiku 4.5** (`claude-haiku-4-5-20250514`) - Fast & cost-efficient - 64K output, $5/MTok
- **Opus 4.1** (`claude-opus-4-1-20250514`) - Exceptional reasoning - 32K output, $75/MTok
- **Sonnet 4** (`claude-sonnet-4-20250514`) - Balanced performance - 64K output, $15/MTok

✅ **Claude 3.7** - Extended thinking
- Sonnet 3.7 (128K output with beta)

✅ **Claude 3.5** - Previous generation
- Sonnet 3.5 (8K output)
- Haiku 3.5 (8K output, fastest)

✅ **Claude 3** - Legacy support

**Quick Start:**
1. Go to admin dashboard
2. Select Anthropic provider
3. Choose your Claude model (use exact API name)
4. Configure and deploy!

**Recommended Defaults:**
- **General use:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Agents/coding:** Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- **High volume:** Claude Haiku 4.5 (`claude-haiku-4-5-20250514`)
- **Deep analysis:** Claude Opus 4.1 (`claude-opus-4-1-20250514`)

All models work seamlessly with the platform's features: RAG, memory, widgets, OCR, and deployment options!
