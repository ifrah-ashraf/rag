# RAG HR Assistant

A minimal RAG (Retrieval-Augmented Generation) system with a Flask backend, React frontend, and Qdrant vector database — all containerized with Docker Compose.

## Architecture

```
rag-ui (React + nginx)  :5173
   ↓ API calls
bot (Flask)             :5000
   ↓ vector search
qdrant (vector DB)      :6333
```

## Prerequisites

- Docker & Docker Compose
- API keys for [Voyage AI](https://www.voyageai.com/) and [Groq](https://console.groq.com/)

## Setup

### 1. Add your API keys

Create `bot/.env`:

```
VOYAGE_API_KEY=your-voyage-api-key
GROQ_API_KEY=your-groq-api-key
```

### 2. Add your data

The `bot/data/` directory is **git-ignored** for privacy. You need to provide it yourself.

Expected structure:

```
bot/data/
  └── chunks/
      ├── chunking.json           # chunked text from your PDF
      ├── embeddings.json         # pre-computed Voyage embeddings
      ├── discarded_chunks.json
      └── gold_output.json
```

The `embeddings.json` file is loaded into Qdrant automatically on first startup. Without it, the bot has no data to search.

### 3. Run

```bash
docker compose up --build -d
```

- UI: http://localhost:5173
- API: http://localhost:5000/ask
- Qdrant dashboard: http://localhost:6333/dashboard

### 4. Stop

```bash
docker compose down
```

Qdrant data persists in a Docker named volume (`qdrant_data`). To wipe it: `docker volume rm rag_qdrant_data`.

## Running without Docker

```bash
# Backend
cd bot
python -m venv bot-env && source bot-env/bin/activate
pip install -r requirements.txt
python src/main.py            # requires Qdrant running on localhost:6333

# Frontend
cd rag-ui
npm install && npm run dev
```
