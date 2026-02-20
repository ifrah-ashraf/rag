from flask import Flask, request, jsonify
from flask_cors import CORS
from llm.rag_query import (
    rag_query,
    embed_query,
    retrieve_chunks, 
    ask_llm
)

app = Flask(__name__)
CORS(app)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("question", "").strip()

    if not query:
        return jsonify({"error": "No question provided"}), 400

    query_vector = embed_query(query)
    chunks       = retrieve_chunks(query_vector)
    answer       = ask_llm(query, chunks)

    references = [
        {
            "section":   c["section"],
            "page":      c["page"],
            "relevance": c["score"],
        }
        for c in chunks
    ]

    return jsonify({
        "question":   query,
        "answer":     answer,
        "references": references,
    })



if __name__ =="__main__":
    app.run(debug=True, port=5000)
