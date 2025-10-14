from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from app.config import settings


class QdrantService:
    def __init__(self):
        self.client = None
        if settings.qdrant_url:
            try:
                self.client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key
                )
            except Exception as e:
                print(f"Warning: Could not connect to Qdrant: {e}")

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5
    ) -> List[ScoredPoint]:
        """Search for similar vectors in Qdrant"""
        if not self.client:
            return []

        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k
            )
            return results
        except Exception as e:
            print(f"Qdrant search error: {e}")
            return []

    def search_with_text(
        self,
        collection_name: str,
        query_text: str,
        top_k: int = 5,
        embedding_function=None
    ) -> List[str]:
        """
        Search with text query (requires embedding function)
        Returns list of text snippets
        """
        if not self.client or not embedding_function:
            return []

        try:
            # Convert text to embedding
            query_vector = embedding_function(query_text)

            # Search
            results = self.search(collection_name, query_vector, top_k)

            # Extract text from results
            contexts = []
            for result in results:
                if hasattr(result, 'payload') and result.payload:
                    # Try common payload fields
                    text = (
                        result.payload.get('text') or
                        result.payload.get('content') or
                        result.payload.get('page_content') or
                        str(result.payload)
                    )
                    contexts.append(text)

            return contexts
        except Exception as e:
            print(f"Qdrant text search error: {e}")
            return []

    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        if not self.client:
            return False

        try:
            collections = self.client.get_collections()
            return any(c.name == collection_name for c in collections.collections)
        except Exception:
            return False


# Singleton instance
qdrant_service = QdrantService()
