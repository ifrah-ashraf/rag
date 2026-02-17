# This is extra cleaning process required due to missing values neglected in the JSON output

import re
from config.config_var import MIN_WORD_COUNT, QUALITY_PASS_SCORE, SECTION_MAX_WORDS


# SECTION EXTRACTION
def extract_section_from_content(content: str, max_words: int = SECTION_MAX_WORDS) -> str:
    content = content.strip()
    if not content:
        return "general"

    caps_match = re.match(r'^([A-Z][A-Z\s&\'\/]+?)(?=[a-z]|\d\s|\s[-–]\s|\n|$)', content)
    if caps_match:
        phrase = caps_match.group(1).strip()
        words = phrase.split()[:max_words]
        return title_case_clean(" ".join(words))

    first_line = content.split("\n")[0].strip()
    if first_line and not first_line.endswith(".") and len(first_line) < 80:
        return title_case_clean(first_line)

    words = content.split()[:max_words]
    return title_case_clean(" ".join(words))


def title_case_clean(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip(" -–—•✓▪"))
    return text.title()


def fix_sections(docs: list[dict]) -> list[dict]:
    for doc in docs:
        if not doc.get("section", "").strip():
            doc["section"] = extract_section_from_content(doc["content"])
            doc["section_auto_extracted"] = True
        else:
            doc["section_auto_extracted"] = False
    return docs


# QUALITY SCORING
def score_content(content: str) -> dict:
    words = content.split()
    word_count = len(words)
    unique_words = set(w.lower().strip(".,;:!?") for w in words)

    # Length score
    if word_count >= 80:
        length_score = 25
    elif word_count >= 40:
        length_score = 20
    elif word_count >= MIN_WORD_COUNT:
        length_score = 10
    else:
        length_score = int((word_count / MIN_WORD_COUNT) * 10)

    # Lexical density
    lex_density = len(unique_words) / max(word_count, 1)
    lex_score = int(min(lex_density * 40, 25))

    # Sentence structure
    has_sentence = bool(re.search(r'[.!?]', content))
    sentence_score = 12 if has_sentence else 0

    # Info density
    has_numbers = bool(re.search(r'\d', content))
    info_score = 8 if has_numbers else 0

    total = length_score + lex_score + sentence_score + info_score

    return {
        "quality_score": total,
        "word_count": word_count
    }

# FILTERING
def evaluate_short_content(docs: list[dict]):
    kept = []
    discarded = []

    for doc in docs:
        quality = score_content(doc["content"])
        doc.update(quality)

        if quality["word_count"] == 0:
            doc["discard_reason"] = "empty"
            discarded.append(doc)
            continue

        if quality["word_count"] < MIN_WORD_COUNT and quality["quality_score"] < QUALITY_PASS_SCORE:
            doc["discard_reason"] = "too short and low quality"
            discarded.append(doc)
            continue

        if quality["quality_score"] < QUALITY_PASS_SCORE:
            doc["discard_reason"] = "low quality"
            discarded.append(doc)
            continue

        kept.append(doc)

    return kept, discarded
