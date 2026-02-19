import voyageai
import time 
import dotenv

voyage_api_key = dotenv.load_dotenv("voyage_api_key")
client = voyageai.Client(api_key=voyage_api_key)

# ── Test 1: Document embedding (as you'd use during indexing) ──
doc_result = client.embed(
    texts=["Our Vision: To make life more connected, entertaining, personalized and productive."],
     model="voyage-3.5",
    input_type="document"
)

print("=== voyage-context-3 (document) ===")
print(f"Status        : SUCCESS")
print(f"Dimensions    : {len(doc_result.embeddings[0])}")
print(f"First 5 values: {doc_result.embeddings[0][:5]}")
print(f"Total tokens  : {doc_result.total_tokens}")


time.sleep(25)
# ── Test 2: Query embedding (as you'd use at retrieval time) ──
query_result = client.embed(
    texts=["What is the vision of Harman?"],
    model="voyage-4",
    input_type="query"
)

print("\n=== voyage-4 (query) ===")
print(f"Status        : SUCCESS")
print(f"Dimensions    : {len(query_result.embeddings[0])}")
print(f"First 5 values: {query_result.embeddings[0][:5]}")
print(f"Total tokens  : {query_result.total_tokens}")


time.sleep(25)
# ── Test 3: Similarity check (the real sanity test) ──
import numpy as np

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Embed both doc and query with same model to compare
doc_vec = client.embed(
    texts=["Our Vision: To make life more connected and productive."],
    model="voyage-4",
    input_type="document"
).embeddings[0]


time.sleep(25)

related_query_vec = client.embed(
    texts=["What is Harman's vision?"],
    model="voyage-4",
    input_type="query"
).embeddings[0]


time.sleep(25)

unrelated_query_vec = client.embed(
    texts=["What is the recipe for pasta?"],
    model="voyage-4",
    input_type="query"
).embeddings[0]

print("\n=== Similarity Sanity Check ===")
print(f"Related query similarity  : {cosine_similarity(doc_vec, related_query_vec):.4f}  ← should be HIGH (0.7+)")
print(f"Unrelated query similarity: {cosine_similarity(doc_vec, unrelated_query_vec):.4f}  ← should be LOW (0.3-)")