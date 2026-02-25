import json
import os
import time
from typing import List, Dict, Any
from config.config_var import INPUT_PATH, OUTPUT_EMBEDDING_PATH

import voyageai
from dotenv import load_dotenv


# CONFIG
VOYAGE_MODEL = "voyage-3.5"
BATCH_SIZE = 64
SAFE_MAX_BATCH = 24        # Safe upper limit
RATE_LIMIT_SLEEP = 1.5
FAILED_LOG_PATH = "failed_embeddings.json"


# STEP 1 — Load Chunks
def load_chunks(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    pending = [c for c in chunks if c.get("embedding") is None]

    if not pending:
        print("✔ All chunks already embedded. No API calls required.")
        return []

    return pending


# STEP 2 — Initialize Voyage
def init_voyage():
    load_dotenv()
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise ValueError("VOYAGE_API_KEY not found")

    return voyageai.Client(api_key=api_key)


# STEP 3 — Embed Chunks Safely
def embed_chunks(voyage, chunks: List[Dict[str, Any]]):

    if not chunks:
        return []

    effective_batch = min(BATCH_SIZE, SAFE_MAX_BATCH)

    print(f"Using batch size: {effective_batch}")

    embedded_chunks = []
    failed_chunks = []

    for i in range(0, len(chunks), effective_batch):
        batch = chunks[i:i+effective_batch]
        texts = [c["content"] for c in batch]

        try:
            result = voyage.embed(
                texts=texts,
                model=VOYAGE_MODEL,
                input_type="document"
            )

            for chunk, vector in zip(batch, result.embeddings):
                chunk["embedding"] = vector
                embedded_chunks.append(chunk)

        except Exception as e:
            print(f"⚠ Batch {i}-{i+effective_batch} failed: {str(e)}")

            for chunk in batch:
                failed_chunks.append({
                    "chunk_id": chunk["chunk_id"],
                    "error": str(e),
                    "content_preview": chunk["content"][:200]
                })

        time.sleep(RATE_LIMIT_SLEEP)

    # Save failed chunks if any
    if failed_chunks:
        with open(FAILED_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(failed_chunks, f, indent=2)
        print(f"⚠ Failed chunks saved to {FAILED_LOG_PATH}")

    print(f"✔ Successfully embedded {len(embedded_chunks)} chunks")

    return embedded_chunks


# STEP 4 — Build Qdrant-Ready Structure
def build_qdrant_points(chunks: List[Dict[str, Any]]):

    points = []

    for idx, chunk in enumerate(chunks):

        if not chunk.get("embedding"):
            continue

        point = {
            "id": idx,
            "vector": chunk["embedding"],
            "payload": {
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "content": chunk["content"],
                "section": chunk.get("section"),
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "source": chunk.get("source"),
                "language": chunk.get("language")
            }
        }

        points.append(point)

    return points


# EXECUTE IN MAIN
def execute_embeddings():

    print("Step 1: Loading chunks...")
    chunks = load_chunks(INPUT_PATH)

    if not chunks:
        return

    print(f"Pending chunks: {len(chunks)}")

    print("Step 2: Initializing Voyage...")
    voyage = init_voyage()

    print("Step 3: Generating embeddings...")
    embedded = embed_chunks(voyage, chunks)

    if not embedded:
        print("No embeddings generated.")
        return

    print("Step 4: Building Qdrant-ready objects...")
    points = build_qdrant_points(embedded)

    with open(OUTPUT_EMBEDDING_PATH, "w", encoding="utf-8") as f:
        json.dump(points, f)

    print(f"✔ Saved embeddings to {OUTPUT_EMBEDDING_PATH}")

    print("\nSample Output Preview:\n")
    print(json.dumps(points[0], indent=2)[:800])


