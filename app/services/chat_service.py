from typing import Optional, List
from anthropic import Anthropic
from openai import OpenAI
from app.models.bot import Bot
from app.schemas.chat import ChatMessage
from app.services.qdrant_service import qdrant_service


class ChatService:
    @staticmethod
    def get_bot_api_key(bot: Bot) -> str:
        """Get the bot's API key from either the relationship or legacy field"""
        # Try to get from API key relationship first (new system)
        if bot.api_key_id and bot.api_key_ref:
            return bot.api_key_ref.api_key
        # Fall back to legacy field
        elif bot.api_key:
            return bot.api_key
        else:
            raise ValueError("No API key configured for this bot")

    @staticmethod
    def build_messages_with_context(
        user_message: str,
        history: List[ChatMessage],
        rag_contexts: Optional[List[str]] = None
    ) -> List[dict]:
        """Build message array with optional RAG context"""
        messages = []

        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Build user message with RAG context if available
        if rag_contexts and len(rag_contexts) > 0:
            context_text = "\n\n".join([f"[Context {i+1}]: {ctx}" for i, ctx in enumerate(rag_contexts)])
            enhanced_message = f"""Use the following context to help answer the question:

{context_text}

User question: {user_message}"""
            messages.append({
                "role": "user",
                "content": enhanced_message
            })
        else:
            messages.append({
                "role": "user",
                "content": user_message
            })

        return messages

    @staticmethod
    def chat_with_anthropic(
        bot: Bot,
        user_message: str,
        history: List[ChatMessage],
        rag_contexts: Optional[List[str]] = None
    ) -> str:
        """Send chat request to Anthropic"""
        api_key = ChatService.get_bot_api_key(bot)
        client = Anthropic(api_key=api_key)

        messages = ChatService.build_messages_with_context(
            user_message, history, rag_contexts
        )

        response = client.messages.create(
            model=bot.model,
            max_tokens=bot.max_tokens,
            temperature=bot.temperature / 100.0,  # Convert 0-100 to 0.0-1.0
            system=bot.system_prompt,
            messages=messages
        )

        return response.content[0].text

    @staticmethod
    def is_gpt5_model(model: str) -> bool:
        """Check if model is a GPT-5 variant"""
        gpt5_models = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-thinking',
                       'gpt-5-thinking-mini', 'gpt-5-thinking-nano', 'gpt-5-chat-latest']
        return any(model.startswith(gpt5_model) for gpt5_model in gpt5_models)

    @staticmethod
    def chat_with_openai_gpt5(
        bot: Bot,
        user_message: str,
        history: List[ChatMessage],
        rag_contexts: Optional[List[str]] = None
    ) -> str:
        """Send chat request to OpenAI using Responses API for GPT-5"""
        api_key = ChatService.get_bot_api_key(bot)
        client = OpenAI(api_key=api_key)

        # Build input with context and history
        input_parts = []

        # Add system prompt as context
        if bot.system_prompt:
            input_parts.append(f"System instructions: {bot.system_prompt}\n")

        # Add conversation history
        if history:
            input_parts.append("Previous conversation:")
            for msg in history:
                input_parts.append(f"{msg.role.capitalize()}: {msg.content}")
            input_parts.append("")

        # Add RAG context if available
        if rag_contexts and len(rag_contexts) > 0:
            input_parts.append("Relevant context:")
            for i, ctx in enumerate(rag_contexts):
                input_parts.append(f"[{i+1}]: {ctx}")
            input_parts.append("")

        # Add current user message
        input_parts.append(f"User: {user_message}")

        full_input = "\n".join(input_parts)

        # Build request params for Responses API
        request_params = {
            "model": bot.model,
            "input": full_input,
        }

        # Add GPT-5 specific parameters (with defaults)
        reasoning_effort = getattr(bot, 'reasoning_effort', 'medium')
        if reasoning_effort:
            request_params["reasoning"] = {"effort": reasoning_effort}

        text_verbosity = getattr(bot, 'text_verbosity', 'medium')
        if text_verbosity:
            request_params["text"] = {"verbosity": text_verbosity}

        # Note: max_output_tokens instead of max_tokens for GPT-5
        if bot.max_tokens:
            request_params["max_output_tokens"] = bot.max_tokens

        # Call the Responses API
        response = client.responses.create(**request_params)

        return response.output_text

    @staticmethod
    def chat_with_openai(
        bot: Bot,
        user_message: str,
        history: List[ChatMessage],
        rag_contexts: Optional[List[str]] = None
    ) -> str:
        """Send chat request to OpenAI (routes to appropriate API)"""
        # Check if using GPT-5 model - use Responses API
        if ChatService.is_gpt5_model(bot.model):
            return ChatService.chat_with_openai_gpt5(bot, user_message, history, rag_contexts)

        # Otherwise use Chat Completions API
        api_key = ChatService.get_bot_api_key(bot)
        client = OpenAI(api_key=api_key)

        messages = ChatService.build_messages_with_context(
            user_message, history, rag_contexts
        )

        # Add system message at the beginning for OpenAI
        messages.insert(0, {
            "role": "system",
            "content": bot.system_prompt
        })

        response = client.chat.completions.create(
            model=bot.model,
            max_tokens=bot.max_tokens,
            temperature=bot.temperature / 100.0,
            messages=messages
        )

        return response.choices[0].message.content

    @staticmethod
    def get_rag_contexts(
        bot: Bot,
        query: str,
        embedding_function=None
    ) -> Optional[List[str]]:
        """
        Get RAG contexts from Qdrant if configured
        Note: This is a placeholder - you'll need to implement embedding generation
        based on your specific use case
        """
        if not bot.use_qdrant or not bot.qdrant_collection:
            return None

        # For now, return empty list - in production you'd implement proper embeddings
        # You can use OpenAI embeddings, sentence transformers, etc.
        return qdrant_service.search_with_text(
            collection_name=bot.qdrant_collection,
            query_text=query,
            top_k=bot.qdrant_top_k,
            embedding_function=embedding_function
        )

    @staticmethod
    def chat(
        bot: Bot,
        user_message: str,
        history: List[ChatMessage] = None,
        rag_contexts: Optional[List[str]] = None
    ) -> str:
        """Main chat function that routes to appropriate provider"""
        if history is None:
            history = []

        # Get RAG contexts if enabled
        if bot.use_qdrant and not rag_contexts:
            rag_contexts = ChatService.get_rag_contexts(bot, user_message)

        # Route to appropriate provider
        if bot.provider == "anthropic":
            return ChatService.chat_with_anthropic(bot, user_message, history, rag_contexts)
        elif bot.provider == "openai":
            return ChatService.chat_with_openai(bot, user_message, history, rag_contexts)
        else:
            raise ValueError(f"Unsupported provider: {bot.provider}")
