import os, json, time
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from config.config_var import OUTPUT_EMBEDDING_PATH

QDRANT_HOST     = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT     = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "harman_docs"

_client = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def _collection_has_data() -> bool:
    try:
        return get_client().get_collection(COLLECTION_NAME).points_count > 0
    except Exception:
        return False


def store_embeddings_in_qdrant():
    """Load embeddings JSON into Qdrant (recreates the collection)."""
    with open(OUTPUT_EMBEDDING_PATH) as f:
        data = json.load(f)

    client = get_client()
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=len(data[0]["vector"]), distance=Distance.COSINE),
    )
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=d["id"], vector=d["vector"], payload=d["payload"]) for d in data],
    )
    print(f"[qdrant] Stored {len(data)} embeddings.")


def ensure_collection_loaded(max_retries=10, delay=3):
    """Wait for Qdrant, then load embeddings if the collection is empty."""
    # wait for qdrant to be reachable
    for attempt in range(1, max_retries + 1):
        try:
            get_client().get_collections()
            break
        except Exception as e:
            print(f"[startup] Qdrant not ready ({attempt}/{max_retries}): {e}")
            time.sleep(delay)
    else:
        raise RuntimeError(f"Qdrant unreachable after {max_retries} attempts")

    # skip if already populated
    if _collection_has_data():
        cnt = get_client().get_collection(COLLECTION_NAME).points_count
        print(f"[startup] '{COLLECTION_NAME}' has {cnt} points — skipping load.")
        return

    print(f"[startup] Loading embeddings into '{COLLECTION_NAME}' ...")
    store_embeddings_in_qdrant()
