import json
import re
from collections import Counter

# Normalize Bullet Points
def normalize_bullets(text: str) -> str:
    """
    - Converts isolated bullets into proper inline bullets
    - Ensures space after bullet symbols
    """

    # Fix broken bullet lines
    text = re.sub(r"[•✓]\s*\n\s*", r"\g<0> ", text)

    # Ensure space after bullet symbol
    text = re.sub(r"([•✓-])([^\s])", r"\1 \2", text)

    return text


# Detect Section Heading
def detect_section(text: str) -> str:
    """
    Extract section title from first meaningful line.
    Assumes headings are uppercase or short phrases.
    """

    lines = text.split("\n")

    for line in lines:
        clean = line.strip()

        # Skip bullet lines
        if clean.startswith(("•", "✓", "-")):
            continue

        # Heuristic: heading likely short and uppercase-heavy
        if len(clean) < 80 and clean.isupper():
            return clean.title()

        # Fallback: first non-bullet line
        if clean:
            return clean

    return "Unknown Section"

# Remove Repeated Headers Across Pages
def remove_repeated_headers(pages):
    """
    Detect repeated first-line headers across pages
    and remove them.
    """

    first_lines = []

    for page in pages:
        lines = page["content"].split("\n")
        if lines:
            first_lines.append(lines[0].strip())

    freq = Counter(first_lines)

    for page in pages:
        lines = page["content"].split("\n")
        if lines and freq[lines[0].strip()] > 2:
            page["content"] = "\n".join(lines[1:]).strip()

    return pages

#  Convert Flattened Tables (Option pattern example)
def convert_flattened_tables(text: str) -> str:
    """
    Detect patterns like:
    Option 1: 100000 INR 4540 Option 2: 200000 INR 5676

    And insert line breaks properly.
    """

    # Insert newline before each Option
    text = re.sub(r"(Option\s+\d+:)", r"\n\1", text)

    # Normalize spacing inside table row
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()

#  Merge Small Pages
def merge_small_pages(pages, min_length=60):
    """
    Merge pages with very small content into next page.
    """

    merged_pages = []
    skip_next = False

    for i in range(len(pages)):
        if skip_next:
            skip_next = False
            continue

        page = pages[i]

        if len(page["content"]) < min_length and i + 1 < len(pages):
            next_page = pages[i + 1]
            combined_content = page["content"] + "\n" + next_page["content"]

            merged_pages.append({
                "page": f"{page['page']}-{next_page['page']}",
                "content": combined_content,
                "source": page["source"]
            })

            skip_next = True
        else:
            merged_pages.append(page)

    return merged_pages


# Main Silver Processing Function
def process_bronze_to_silver(input_json: str, output_json: str):

    with open(input_json, "r", encoding="utf-8") as f:
        pages = json.load(f)

    # Remove repeated headers
    pages = remove_repeated_headers(pages)

    processed_pages = []

    for page in pages:
        text = page["content"]

        text = normalize_bullets(text)
        text = convert_flattened_tables(text)

        section = detect_section(text)

        processed_pages.append({
            "page": page["page"],
            "section": section,
            "content": text,
            "source": page["source"]
        })

    # Merge small pages at the end
    processed_pages = merge_small_pages(processed_pages)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(processed_pages, f, indent=2, ensure_ascii=False)

    print(f"Silver layer created → {output_json}")


    
    