"""
Sync Qdrant collections from Cloud to Railway using direct HTTP requests

This version uses the qdrant-client for the source (cloud) but uses
direct HTTP requests for the target (Railway) to work around connection issues.
"""

import os
import requests
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RailwayQdrantHTTP:
    """Direct HTTP client for Railway Qdrant to bypass connection issues"""

    def __init__(self, url: str, api_key: str):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }

    def get_collections(self):
        """Get all collections"""
        response = requests.get(
            f"{self.url}/collections",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['result']

    def get_collection(self, collection_name: str):
        """Get collection info"""
        response = requests.get(
            f"{self.url}/collections/{collection_name}",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['result']

    def create_collection(self, collection_name: str, vector_size: int, distance: str):
        """Create a collection"""
        # Map Qdrant Distance enum to string
        distance_str_map = {
            Distance.COSINE: "Cosine",
            Distance.EUCLID: "Euclidean",
            Distance.DOT: "Dot"
        }
        distance_str = distance_str_map.get(distance, "Cosine")

        payload = {
            "vectors": {
                "size": vector_size,
                "distance": distance_str
            }
        }
        response = requests.put(
            f"{self.url}/collections/{collection_name}",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        response = requests.delete(
            f"{self.url}/collections/{collection_name}",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def upsert(self, collection_name: str, points: List[Dict]):
        """Upsert points to a collection"""
        payload = {"points": points}
        response = requests.put(
            f"{self.url}/collections/{collection_name}/points",
            headers=self.headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()


class QdrantSyncer:
    def __init__(
        self,
        source_url: str,
        source_api_key: str,
        target_url: str,
        target_api_key: str
    ):
        """Initialize connections to source and target Qdrant instances"""
        # Clean up URLs
        source_url = source_url.rstrip('/')
        target_url = target_url.rstrip('/')

        print(f"Connecting to source Qdrant: {source_url}")
        self.source_client = QdrantClient(
            url=source_url,
            api_key=source_api_key,
            timeout=60,
            prefer_grpc=False
        )

        print(f"Connecting to target Qdrant (HTTP): {target_url}")
        self.target_client = RailwayQdrantHTTP(target_url, target_api_key)

        # Test connections
        try:
            source_collections = self.source_client.get_collections()
            print(f"[OK] Source connection successful ({len(source_collections.collections)} collections)")
        except Exception as e:
            print(f"[ERROR] Source connection failed: {e}")
            raise

        try:
            target_collections = self.target_client.get_collections()
            print(f"[OK] Target connection successful ({len(target_collections.get('collections', []))} collections)")
        except Exception as e:
            print(f"[ERROR] Target connection failed: {e}")
            raise

    def get_collection_config(self, collection_name: str) -> Dict[str, Any]:
        """Get configuration of a collection from source"""
        info = self.source_client.get_collection(collection_name)

        # Extract vector configuration (handle both object and dict formats)
        vectors_config = info.config.params.vectors

        # Check if it's a dict or object
        if isinstance(vectors_config, dict):
            # Named vectors configuration
            # Get the first/default vector config
            vector_name = list(vectors_config.keys())[0]
            vector_cfg = vectors_config[vector_name]
            vector_size = vector_cfg.size if hasattr(vector_cfg, 'size') else vector_cfg['size']
            distance = vector_cfg.distance if hasattr(vector_cfg, 'distance') else vector_cfg['distance']
        else:
            # Single vector configuration
            vector_size = vectors_config.size
            distance = vectors_config.distance

        return {
            "name": collection_name,
            "vector_size": vector_size,
            "distance": distance,
            "points_count": info.points_count
        }

    def create_collection_on_target(self, config: Dict[str, Any]) -> bool:
        """Create a collection on target with matching configuration"""
        collection_name = config["name"]

        # Check if collection already exists
        try:
            existing_collections = self.target_client.get_collections()
            existing_names = [c['name'] for c in existing_collections.get('collections', [])]
            if collection_name in existing_names:
                print(f"  Collection '{collection_name}' already exists on target")
                print(f"  Deleting existing collection '{collection_name}'...")
                self.target_client.delete_collection(collection_name)
        except Exception as e:
            print(f"  Error checking existing collections: {e}")

        # Create collection
        try:
            print(f"  Creating collection '{collection_name}' (size: {config['vector_size']}, distance: {config['distance']})")
            self.target_client.create_collection(
                collection_name=collection_name,
                vector_size=config["vector_size"],
                distance=config["distance"]
            )
            print(f"  [OK] Collection created")
            return True
        except Exception as e:
            print(f"  [ERROR] Error creating collection: {e}")
            return False

    def sync_collection_data(self, collection_name: str, batch_size: int = 100):
        """Sync all points from source collection to target collection"""
        print(f"\n  Syncing data for collection '{collection_name}'...")

        total_points = 0
        offset = None

        try:
            while True:
                # Scroll through source collection
                result, next_offset = self.source_client.scroll(
                    collection_name=collection_name,
                    limit=batch_size,
                    offset=offset,
                    with_vectors=True,
                    with_payload=True
                )

                if not result:
                    break

                # Prepare points for upload
                points = []
                for point in result:
                    points.append({
                        "id": str(point.id),  # Ensure ID is string
                        "vector": point.vector,
                        "payload": point.payload if point.payload else {}
                    })

                # Upload to target
                if points:
                    self.target_client.upsert(collection_name, points)
                    total_points += len(points)
                    print(f"    Synced {total_points} points...", end='\r')

                # Check if there are more points
                if not next_offset:
                    break

                offset = next_offset

            print(f"    [OK] Synced {total_points} points total")
            return total_points

        except Exception as e:
            print(f"    [ERROR] Error syncing data: {e}")
            import traceback
            traceback.print_exc()
            return total_points

    def sync_all_collections(self):
        """Sync all collections from source to target"""
        print("\n" + "="*60)
        print("STARTING QDRANT SYNC")
        print("="*60)

        # Get all collections from source
        collections_response = self.source_client.get_collections()
        collections = collections_response.collections

        print(f"\nFound {len(collections)} collections to sync:")
        for collection in collections:
            print(f"  - {collection.name}")

        print("\n" + "-"*60)

        # Sync each collection
        results = {}
        for collection in collections:
            collection_name = collection.name
            print(f"\nSyncing collection: {collection_name}")
            print("-"*60)

            # Get source collection config
            config = self.get_collection_config(collection_name)
            print(f"  Source: {config['points_count']} points")

            # Create collection on target
            created = self.create_collection_on_target(config)

            if created:
                # Sync data
                synced_count = self.sync_collection_data(collection_name)
                results[collection_name] = {
                    "success": True,
                    "points_synced": synced_count,
                    "source_count": config['points_count']
                }
            else:
                results[collection_name] = {
                    "success": False,
                    "error": "Collection creation failed"
                }

        # Print summary
        print("\n" + "="*60)
        print("SYNC SUMMARY")
        print("="*60)

        for collection_name, result in results.items():
            if result["success"]:
                print(f"[OK] {collection_name}: {result['points_synced']}/{result['source_count']} points")
            else:
                print(f"[ERROR] {collection_name}: {result.get('error', 'Failed')}")

        print("\n" + "="*60)
        print("SYNC COMPLETE")
        print("="*60)


def main():
    print("Qdrant Cloud -> Railway Sync Tool (HTTP Mode)")
    print("="*60)

    # Get connection details from environment variables
    print("\nLoading connection details from environment variables...")
    source_url = os.getenv("CLOUD_QDRANT_URL")
    source_api_key = os.getenv("CLOUD_QDRANT_API_KEY")
    target_url = os.getenv("QDRANT_URL")
    target_api_key = os.getenv("QDRANT_API_KEY")

    if not all([source_url, source_api_key, target_url, target_api_key]):
        print("\n[ERROR] Error: Missing required connection details")
        print("\nYou need these environment variables:")
        print("  CLOUD_QDRANT_URL")
        print("  CLOUD_QDRANT_API_KEY")
        print("  QDRANT_URL (Railway)")
        print("  QDRANT_API_KEY (Railway)")
        return

    print("\n" + "-"*60)

    # Create syncer and run
    try:
        syncer = QdrantSyncer(
            source_url=source_url,
            source_api_key=source_api_key,
            target_url=target_url,
            target_api_key=target_api_key
        )

        syncer.sync_all_collections()

    except Exception as e:
        print(f"\n[ERROR] Sync failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
