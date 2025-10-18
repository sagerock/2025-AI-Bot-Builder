from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    ScoredPoint,
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
import uuid
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

    def list_collections(self) -> List[dict]:
        """List all available collections with their details"""
        if not self.client:
            return []

        try:
            collections_response = self.client.get_collections()
            collections = []

            for collection in collections_response.collections:
                try:
                    # Get collection info
                    info = self.client.get_collection(collection.name)
                    collections.append({
                        "name": collection.name,
                        "vectors_count": info.vectors_count if (hasattr(info, 'vectors_count') and info.vectors_count is not None) else 0,
                        "points_count": info.points_count if (hasattr(info, 'points_count') and info.points_count is not None) else 0,
                        "status": str(info.status) if hasattr(info, 'status') else "unknown",
                    })
                except Exception as e:
                    # If we can't get details, just add the name
                    collections.append({
                        "name": collection.name,
                        "vectors_count": 0,
                        "points_count": 0,
                        "status": "unknown",
                        "error": str(e)
                    })

            return collections
        except Exception as e:
            print(f"Error listing Qdrant collections: {e}")
            return []

    def get_collection_info(self, collection_name: str) -> Optional[dict]:
        """Get detailed information about a specific collection"""
        if not self.client:
            return None

        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count if (hasattr(info, 'vectors_count') and info.vectors_count is not None) else 0,
                "points_count": info.points_count if (hasattr(info, 'points_count') and info.points_count is not None) else 0,
                "status": str(info.status) if hasattr(info, 'status') else "unknown",
                "config": {
                    "vector_size": info.config.params.vectors.size if hasattr(info, 'config') else None,
                    "distance": str(info.config.params.vectors.distance) if hasattr(info, 'config') else None,
                }
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return None

    def test_connection(self) -> dict:
        """Test Qdrant connection and return status"""
        if not self.client:
            return {
                "connected": False,
                "error": "Qdrant client not initialized. Check QDRANT_URL in settings."
            }

        try:
            # Try to list collections as a connection test
            self.client.get_collections()
            collections = self.list_collections()
            return {
                "connected": True,
                "collections_count": len(collections),
                "url": settings.qdrant_url
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "url": settings.qdrant_url
            }

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,  # Default for OpenAI text-embedding-3-small
        distance: str = "Cosine"
    ) -> bool:
        """Create a new Qdrant collection"""
        if not self.client:
            raise Exception("Qdrant client not initialized")

        try:
            # Map distance string to Distance enum
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclidean": Distance.EUCLID,
                "Dot": Distance.DOT
            }

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, Distance.COSINE)
                )
            )
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise

    def upload_points(
        self,
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Upload points (vectors) to a Qdrant collection

        Args:
            collection_name: Name of the collection
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts for each point

        Returns:
            List of point IDs that were uploaded
        """
        if not self.client:
            raise Exception("Qdrant client not initialized")

        if len(texts) != len(embeddings):
            raise ValueError("Number of texts and embeddings must match")

        if metadatas and len(metadatas) != len(texts):
            raise ValueError("Number of metadatas must match number of texts")

        try:
            points = []
            point_ids = []

            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                point_id = str(uuid.uuid4())
                point_ids.append(point_id)

                payload = {
                    "text": text,
                    "content": text,  # Alias for compatibility
                }

                # Add metadata if provided
                if metadatas and i < len(metadatas):
                    payload.update(metadatas[i])

                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                ))

            # Upload in batches of 100
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )

            return point_ids
        except Exception as e:
            print(f"Error uploading points: {e}")
            raise

    def delete_points(
        self,
        collection_name: str,
        point_ids: List[str]
    ) -> bool:
        """Delete specific points from a collection"""
        if not self.client:
            raise Exception("Qdrant client not initialized")

        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids
            )
            return True
        except Exception as e:
            print(f"Error deleting points: {e}")
            raise

    def delete_collection(self, collection_name: str) -> bool:
        """Delete an entire collection"""
        if not self.client:
            raise Exception("Qdrant client not initialized")

        try:
            self.client.delete_collection(collection_name=collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            raise

    def scroll_points(
        self,
        collection_name: str,
        limit: int = 100,
        offset: Optional[str] = None,
        with_vectors: bool = False
    ) -> Dict[str, Any]:
        """
        Scroll through points in a collection (pagination)

        Args:
            collection_name: Name of the collection
            limit: Maximum number of points to return
            offset: Point ID to start from (for pagination)
            with_vectors: Whether to include vectors in response

        Returns:
            Dict with 'points' list and 'next_offset' for pagination
        """
        if not self.client:
            return {"points": [], "next_offset": None}

        try:
            result = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_vectors=with_vectors,
                with_payload=True
            )

            points = []
            for point in result[0]:
                points.append({
                    "id": point.id,
                    "payload": point.payload,
                    "vector": point.vector if with_vectors else None
                })

            return {
                "points": points,
                "next_offset": result[1]  # Next page offset
            }
        except Exception as e:
            print(f"Error scrolling points: {e}")
            return {"points": [], "next_offset": None}

    def search_points_by_metadata(
        self,
        collection_name: str,
        metadata_key: str,
        metadata_value: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for points by metadata field"""
        if not self.client:
            return []

        try:
            results = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key=metadata_key,
                            match=MatchValue(value=metadata_value)
                        )
                    ]
                ),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            points = []
            for point in results[0]:
                points.append({
                    "id": point.id,
                    "payload": point.payload
                })

            return points
        except Exception as e:
            print(f"Error searching points: {e}")
            return []

    def get_all_chunks_for_document(
        self,
        collection_name: str,
        filename: str
    ) -> str:
        """
        Retrieve ALL chunks for a specific document and return as concatenated text

        Args:
            collection_name: Name of the Qdrant collection
            filename: Source filename to retrieve chunks for

        Returns:
            Full document text with all chunks concatenated in order
        """
        if not self.client:
            return ""

        try:
            # Get all points for this document (high limit to get all chunks)
            points = self.search_points_by_metadata(
                collection_name=collection_name,
                metadata_key="source",
                metadata_value=filename,
                limit=10000  # High limit to ensure we get all chunks
            )

            if not points:
                return ""

            # Sort chunks by chunk_index to maintain document order
            sorted_chunks = sorted(
                points,
                key=lambda x: x["payload"].get("chunk_index", 0)
            )

            # Extract text from each chunk
            texts = []
            for chunk in sorted_chunks:
                text = chunk["payload"].get("text") or chunk["payload"].get("content", "")
                if text:
                    texts.append(text)

            # Join all chunks with double newline
            full_text = "\n\n".join(texts)

            print(f"Retrieved {len(sorted_chunks)} chunks for document '{filename}'")
            return full_text

        except Exception as e:
            print(f"Error retrieving full document: {e}")
            return ""


# Singleton instance
qdrant_service = QdrantService()
