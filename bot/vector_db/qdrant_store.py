import json
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from config.config_var import OUTPUT_EMBEDDING_PATH

def store_embeddings_in_qdrant():
    """Store embeddings from JSON file to Qdrant vector database."""
    try:
        # 1. Connect to Qdrant
        client = QdrantClient(host="localhost", port=6333)

        # 2. Load embeddings
        with open(OUTPUT_EMBEDDING_PATH, "r") as f:
            points_data = json.load(f)

        # 3. Get vector dimension dynamically
        vector_size = len(points_data[0]["vector"])

        collection_name = "harman_docs"

        # 4. Create collection (if not exists)
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        # 5. Convert to Qdrant PointStruct format
        points = []

        for item in points_data:
            points.append(
                PointStruct(
                    id=item["id"],
                    vector=item["vector"],
                    payload=item["payload"]
                )
            )

        # 6. Upload to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        print("Successfully stored embeddings in Qdrant.")

    except FileNotFoundError as e:
        print(f"Error: Embedding file not found - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Error: Failed to store embeddings in Qdrant - {e}")
