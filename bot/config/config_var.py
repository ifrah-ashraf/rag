# config.py

INPUT_PATH = "data/chunks/chunks_ready.json"
OUTPUT_CHUNKS_PATH = "data/chunks/chunking.json"
OUTPUT_DISCARDED_PATH = "data/chunks/discarded_chunks.json"

# Chunking
CHUNK_SIZE = 450
CHUNK_OVERLAP = 50

# Quality filtering
MIN_WORD_COUNT = 20
QUALITY_PASS_SCORE = 40
SECTION_MAX_WORDS = 8
