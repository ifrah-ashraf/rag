import fitz  # PyMuPDF
import json
import re


def clean_text(text: str) -> str:
    """
    Advanced text cleanup for RAG:
    - Remove standalone page numbers
    - Preserve bullets
    - Fix broken line wraps
    - Normalize whitespace
    - Keep paragraph separation
    """

    lines = text.split("\n")
    cleaned_lines = []

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Remove standalone page numbers (e.g., "2", "7")
        if re.fullmatch(r"\d+", line):
            continue

        # Fix bullet formatting (• and ✓)
        if line.startswith(("•", "✓", "-")):
            cleaned_lines.append(line)
            continue

        # Join broken lines:
        # If previous line does NOT end with punctuation,
        # and current line is not bullet → merge with previous
        if cleaned_lines:
            prev = cleaned_lines[-1]
            if (
                not prev.endswith((".", ":", "?", "!", "•", "✓"))
                and not line.startswith(("•", "✓", "-"))
            ):
                cleaned_lines[-1] = prev + " " + line
                continue

        cleaned_lines.append(line)

    # Join paragraphs properly
    text = "\n".join(cleaned_lines)

    # Normalize multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    return text.strip()


def extract_pdf_to_json(pdf_path: str, output_json: str):
    """
    Extract text page-by-page using PyMuPDF
    and apply structured cleaning.
    """

    doc = fitz.open(pdf_path)
    extracted_data = []

    for page_num, page in enumerate(doc, start=1):
        raw_text = page.get_text("text")  # explicit mode

        cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            continue

        page_data = {
            "page": page_num,
            "content": cleaned_text,
            "source": pdf_path
        }

        extracted_data.append(page_data)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)

    print(f"Extraction completed. Saved to: {output_json}")


