from bs4 import BeautifulSoup
import ftfy
from typing import List, Optional
import logging
from ..utils.model_manager import get_nlp_model
from ..utils.patterns import TextCleaner, TextPatterns
from ..config.settings import get_config
from ..utils.exceptions import TextProcessingError

logger = logging.getLogger(__name__)


def text_normalization(text: str) -> str:
    """Normalize and clean input text efficiently."""
    try:
        # Remove HTML, non-word chars, normalize whitespace
        text = TextCleaner.remove_html_tags(text)
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text()
        text = TextCleaner.remove_non_word_chars(text)
        text = TextCleaner.normalize_whitespace(text)

        # Normalize quotes and fix encoding
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")
        text = ftfy.fix_text(text)

        # Remove headers/footers
        text = remove_headers_footers(text)
        return text.lower().strip()
    except Exception as e:
        raise TextProcessingError("text_normalization", len(text), e)


def remove_headers_footers(text: str) -> str:
    """Remove page numbers and standalone numbers often present in headers/footers."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if TextCleaner.is_page_number(line):
            continue
        if TextCleaner.is_standalone_number(line):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def segment_text(text: str, max_length: Optional[int] = None) -> List[str]:
    """Segment text into chunks ending at sentence boundaries by character length."""
    config = get_config()
    if max_length is None:
        max_length = config.MAX_CHUNK_LENGTH

    try:
        nlp = get_nlp_model()
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    except Exception:
        # Regex fallback
        sentences = TextCleaner.split_sentences(text)

    chunks: List[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_length:
            current += (" " if current else "") + sentence
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)

    return chunks if chunks else [text]


def filter_segments(segments: List[str], min_length: Optional[int] = None) -> List[str]:
    """Filter out too-short and low-value segments."""
    config = get_config()
    if min_length is None:
        min_length = config.MIN_SEGMENT_LENGTH

    filtered: List[str] = []
    for segment in segments:
        s = segment.strip()
        if (len(s) >= min_length and
            not TextCleaner.is_procedural_content(s) and
            not TextCleaner.is_boilerplate_content(s)):
            filtered.append(s)
    return filtered


def segment_into_chunks(text: str, target_words: Optional[int] = None, overlap_ratio: Optional[float] = None) -> List[str]:
    """Segment text into overlapping chunks by word count while preserving sentence boundaries."""
    config = get_config()
    if target_words is None:
        target_words = config.TARGET_WORDS_PER_CHUNK
    if overlap_ratio is None:
        overlap_ratio = config.CHUNK_OVERLAP_RATIO

    try:
        nlp = get_nlp_model()
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    except Exception:
        sentences = TextCleaner.split_sentences(text)

    chunks: List[str] = []
    idx = 0
    num_sentences = len(sentences)
    if num_sentences == 0:
        return []

    while idx < num_sentences:
        current_chunk: List[str] = []
        word_count = 0
        while idx < num_sentences and word_count < target_words:
            sent = sentences[idx]
            current_chunk.append(sent)
            word_count += len(sent.split())
            idx += 1

        if not current_chunk:
            break

        chunks.append(' '.join(current_chunk).strip())

        # Compute overlap in sentences for next chunk start
        overlap_sentence_count = max(1, int(len(current_chunk) * overlap_ratio))
        idx = max(0, idx - overlap_sentence_count)

        # Ensure progress to avoid infinite loop when chunk is a single sentence
        if overlap_sentence_count >= len(current_chunk):
            idx += 1

    return chunks


def filter(text: str, min_length: Optional[int] = None) -> str:
    """Backward-compatible filter for a raw text string."""
    config = get_config()
    if min_length is None:
        min_length = config.MIN_SEGMENT_LENGTH

    lines = text.split('\n')
    filtered_lines: List[str] = []
    for line in lines:
        if not TextCleaner.is_procedural_content(line) and not TextCleaner.is_boilerplate_content(line):
            filtered_lines.append(line)
    return '\n'.join(filtered_lines).strip()
