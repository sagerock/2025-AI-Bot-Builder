"""
Sync Qdrant collections from Cloud to Railway

This script will:
1. Connect to both cloud and railway Qdrant instances
2. List all collections from cloud
3. Create matching collections on railway
4. Copy all points (vectors + metadata) from cloud to railway
"""

import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class QdrantSyncer:
    def __init__(
        self,
        source_url: str,
        source_api_key: str,
        target_url: str,
        target_api_key: str
    ):
        """Initialize connections to source and target Qdrant instances"""
        # Clean up URLs (remove trailing slashes)
        source_url = source_url.rstrip('/')
        target_url = target_url.rstrip('/')

        print(f"Connecting to source Qdrant: {source_url}")
        self.source_client = QdrantClient(
            url=source_url,
            api_key=source_api_key,
            timeout=60,
            prefer_grpc=False
        )

        print(f"Connecting to target Qdrant: {target_url}")

        # For Railway, we need to use HTTPS with proper settings
        import httpx
        self.target_client = QdrantClient(
            url=target_url,
            api_key=target_api_key,
            timeout=120,
            prefer_grpc=False,
            https=True,
            verify=True
        )

        # Test connections
        try:
            source_collections = self.source_client.get_collections()
            print(f"[OK] Source connection successful ({len(source_collections.collections)} collections)")
        except Exception as e:
            print(f"[ERROR] Source connection failed: {e}")
            raise

        try:
            target_collections = self.target_client.get_collections()
            print(f"[OK] Target connection successful ({len(target_collections.collections)} collections)")
        except Exception as e:
            print(f"[ERROR] Target connection failed: {e}")
            raise

    def get_collection_config(self, collection_name: str) -> Dict[str, Any]:
        """Get configuration of a collection from source"""
        info = self.source_client.get_collection(collection_name)

        # Extract vector configuration
        vectors_config = info.config.params.vectors

        return {
            "name": collection_name,
            "vector_size": vectors_config.size,
            "distance": vectors_config.distance,
            "points_count": info.points_count
        }

    def create_collection_on_target(self, config: Dict[str, Any]) -> bool:
        """Create a collection on target with matching configuration"""
        collection_name = config["name"]

        # Check if collection already exists
        try:
            existing_collections = self.target_client.get_collections()
            if any(c.name == collection_name for c in existing_collections.collections):
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
                vectors_config=VectorParams(
                    size=config["vector_size"],
                    distance=config["distance"]
                )
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
                        "id": point.id,
                        "vector": point.vector,
                        "payload": point.payload
                    })

                # Upload to target
                if points:
                    self.target_client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
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
                    "error": "Collection creation skipped or failed"
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
    print("Qdrant Cloud -> Railway Sync Tool")
    print("="*60)

    # Get connection details from environment variables
    print("\nLoading connection details from environment variables...")
    source_url = os.getenv("CLOUD_QDRANT_URL")
    source_api_key = os.getenv("CLOUD_QDRANT_API_KEY")
    target_url = os.getenv("QDRANT_URL")
    target_api_key = os.getenv("QDRANT_API_KEY")

    if not all([source_url, source_api_key, target_url, target_api_key]):
        print("\n[ERROR] Error: Missing required connection details")
        print("\nYou can also set these environment variables:")
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
