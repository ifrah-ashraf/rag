# chunking.py

from datetime import datetime, timezone
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.config_var import CHUNK_SIZE, CHUNK_OVERLAP


def build_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )


def chunk_docs(docs: list[dict]) -> list[dict]:
    splitter = build_splitter()
    all_chunks = []
    chunk_serial = 0

    for doc in docs:

        splits = splitter.create_documents(
            texts=[doc["content"]],
            metadatas=[{
                "doc_id": doc["doc_id"],
                "section": doc["section"],
                "source": doc["source"],
                "quality_score": doc.get("quality_score"),
                "page_start": doc.get("page_start"),
                "page_end": doc.get("page_end"),
                "language": doc.get("language"),
                "ingestion_version": doc.get("ingestion_version"),
            }]
        )

        for chunk_idx, lc_doc in enumerate(splits):

            chunk = {
                # ───────── Identity ─────────
                "chunk_id": f"{doc['doc_id']}_chunk_{chunk_serial:05d}",
                "chunk_index": chunk_idx,
                "doc_id": doc["doc_id"],

                # ───────── Content ─────────
                "content": lc_doc.page_content,
                "char_start": lc_doc.metadata.get("start_index", 0),
                "word_count": len(lc_doc.page_content.split()),

                # ───────── Provenance ─────────
                "section": lc_doc.metadata["section"],
                "page_start": lc_doc.metadata["page_start"],
                "page_end": lc_doc.metadata["page_end"],
                "source": lc_doc.metadata["source"],
                "language": lc_doc.metadata["language"],
                "ingestion_version": lc_doc.metadata["ingestion_version"],
                "source_quality_score": lc_doc.metadata["quality_score"],

                # ───────── Tracking ─────────
                "chunked_at": datetime.now(timezone.utc).isoformat(),

                # Placeholder for next stage
                "embedding": None,
            }

            all_chunks.append(chunk)
            chunk_serial += 1

    return all_chunks
