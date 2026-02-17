import os
import re
from datetime import datetime
import json

with open("data/processed/silver_output.json", "r") as f:
    raw_data = json.load(f)
# ---------- DOC ID ----------
def generate_doc_id(source_path):
    filename = os.path.basename(source_path)
    name_without_ext = os.path.splitext(filename)[0]
    doc_id = re.sub(r'[^a-zA-Z0-9]+', '_', name_without_ext.lower())
    return doc_id


# ---------- PAGE NORMALIZATION ----------
def normalize_page(page):
    """
    Converts:
    6       -> (6, 6)
    "6"     -> (6, 6)
    "6-7"   -> (6, 7)
    """
    if isinstance(page, int):
        return page, page

    if isinstance(page, str):
        page = page.strip()
        if "-" in page:
            start, end = page.split("-")
            return int(start.strip()), int(end.strip())
        return int(page), int(page)

    raise ValueError(f"Invalid page format: {page}")


# ---------- CLEAN TEXT ----------
def clean_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'•\s*', '- ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ---------- MAIN NORMALIZER ----------
def normalize_record(record, ingestion_version="v1"):
    doc_id = generate_doc_id(record["source"])
    page_start, page_end = normalize_page(record["page"])

    normalized = {
        "doc_id": doc_id,
        "page_start": page_start,
        "page_end": page_end,
        "section": record.get("section", "").strip(),
        "content": clean_text(record["content"]),
        "source": record["source"],
        "language": "en",  # default — change if multilingual
        "ingestion_version": ingestion_version,
        "created_at": datetime.utcnow().isoformat()
    }

    return normalized

normalized_data = []

for r in raw_data:
    normalized = normalize_record(r)
    normalized_data.append(normalized)

output_path = "data/processed/gold_normalized_output.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(normalized_data, f, indent=2, ensure_ascii=False)

print(f"Normalized data written to {output_path}")
