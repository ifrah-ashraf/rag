import json

from config.config_var import (
    INPUT_PATH,
    OUTPUT_CHUNKS_PATH,
)

from process.chunk import (
    chunk_docs
)


def main():
    print("Loading input JSON...")

    # ───────── Load cleaned JSON ─────────
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)

    print(f"Loaded {len(docs)} documents")

    # ───────── Run Chunking ─────────
    print("Running chunking...")
    chunks = chunk_docs(docs)

    print(f"Created {len(chunks)} chunks")

    # ───────── Save Output ─────────
    print("Saving chunked output...")

    with open(OUTPUT_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print("Chunking completed successfully.")


if __name__ == "__main__":
    main()
