from typing import List, Optional
from openai import OpenAI
from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings for RAG"""

    DEFAULT_MODEL = "text-embedding-3-small"  # OpenAI's latest small model

    @staticmethod
    def generate_embedding(
        text: str,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL
    ) -> List[float]:
        """
        Generate embedding vector for a text string

        Args:
            text: The text to embed
            api_key: OpenAI API key (uses DEFAULT_OPENAI_API_KEY if not provided)
            model: Embedding model to use (default: text-embedding-3-small)

        Returns:
            List of floats representing the embedding vector
        """
        # Use provided API key or fall back to default
        key = api_key or settings.default_openai_api_key

        if not key:
            raise ValueError(
                "No OpenAI API key available for embeddings. "
                "Set DEFAULT_OPENAI_API_KEY in environment or provide api_key parameter."
            )

        try:
            client = OpenAI(api_key=key)
            response = client.embeddings.create(
                input=text,
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    @staticmethod
    def generate_embeddings_batch(
        texts: List[str],
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call

        Args:
            texts: List of texts to embed
            api_key: OpenAI API key (uses DEFAULT_OPENAI_API_KEY if not provided)
            model: Embedding model to use

        Returns:
            List of embedding vectors
        """
        key = api_key or settings.default_openai_api_key

        if not key:
            raise ValueError("No OpenAI API key available for embeddings")

        try:
            client = OpenAI(api_key=key)
            response = client.embeddings.create(
                input=texts,
                model=model
            )
            # Sort by index to ensure order matches input
            sorted_embeddings = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_embeddings]
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            raise


# Singleton instance
embedding_service = EmbeddingService()
