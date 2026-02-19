"""
RAG Query Pipeline
==================
Voyage AI (voyage-3.5)  →  Qdrant (harman_docs)  →  Groq (llama-3.3-70b)
"""

import os
from dotenv import load_dotenv
import voyageai
from qdrant_client import QdrantClient
from groq import Groq

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG — matches your embedding setup exactly
# ─────────────────────────────────────────────
VOYAGE_MODEL      = "voyage-3.5"
COLLECTION_NAME   = "harman_docs"
GROQ_MODEL        = "llama-3.3-70b-versatile"
TOP_K             = 5

# ─────────────────────────────────────────────
# CLIENTS
# ─────────────────────────────────────────────
voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
qdrant = QdrantClient(host="localhost", port=6333)
groq   = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ─────────────────────────────────────────────
# STEP 1 — Embed the user query
# ─────────────────────────────────────────────
def embed_query(query: str) -> list:
    result = voyage.embed(
        texts=[query],
        model=VOYAGE_MODEL,
        input_type="query",      
    )
    return result.embeddings[0]


# ─────────────────────────────────────────────
# STEP 2 — Search Qdrant for relevant chunks
# ─────────────────────────────────────────────
def retrieve_chunks(query_vector: list, top_k: int = TOP_K) -> list:
    hits = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    chunks = []
    for hit in hits:
        chunks.append({
            "score":   round(hit.score, 4),
            "content": hit.payload.get("content", ""),
            "section": hit.payload.get("section", "N/A"),
            "page":    hit.payload.get("page_start", "?"),
        })
    return chunks


# ─────────────────────────────────────────────
# STEP 3 — Build context + call Groq LLM
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a helpful HR assistant for HARMAN DTS.
Answer using ONLY the context provided.
If the answer isn't in the context, say "I don't have that information in the handbook."
Be concise and cite the section name when relevant."""


def ask_llm(query: str, chunks: list) -> str:
    # Build context block from retrieved chunks
    context_parts = []
    for i, c in enumerate(chunks, 1):
        context_parts.append(
            f"[{i}] Section: {c['section']} | Page: {c['page']} | Relevance: {c['score']}\n"
            f"{c['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    response = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        temperature=0.2,
        max_tokens=512,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────
# FULL PIPELINE
# ─────────────────────────────────────────────
def rag_query(query: str, verbose: bool = True) -> str:
    print(f"\n{'='*55}")
    print(f"  Query: {query}")
    print(f"{'='*55}")

    # Step 1: Embed query
    query_vector = embed_query(query)
    print(f"Query embedded ({len(query_vector)} dims)")

    # Step 2: Retrieve
    chunks = retrieve_chunks(query_vector)
    print(f"Retrieved {len(chunks)} chunks from Qdrant")

    if verbose:
        print("\n Retrieved context:")
        for c in chunks:
            print(f"   [{c['score']}] {c['section']} — p.{c['page']}")
            print(f"   {c['content'][:80]}...")

    # Step 3: LLM answer
    answer = ask_llm(query, chunks)
    print(f"\n Answer:\n{answer}")
    return answer

