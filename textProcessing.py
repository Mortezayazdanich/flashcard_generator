from bs4 import BeautifulSoup
import re
import ftfy 
import spacy


def text_normalization(text):
    """
    Normalize the input text by converting it to lowercase and stripping leading/trailing whitespace.
    """
    html_text = re.sub(r'<.*?>', '', text)
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text()    
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = ftfy.fix_text(text)
    text = remove_headers_footers(text)
    return text.lower().strip()

def remove_headers_footers(text):
    lines = text.split('\n')
    # Example rule: Remove lines that look like "Page [number]"
    cleaned_lines = [line for line in lines if not re.match(r'^Page \d+$', line.strip())]
    # Example rule: Remove lines that are just a number (common page number format)
    cleaned_lines = [line for line in cleaned_lines if not line.strip().isdigit()]
    return '\n'.join(cleaned_lines)


def segment_text(text, max_length=2000):
    """
    Segments the input text into chunks of approximately max_length characters,
    ensuring that segments end at sentence boundaries.
    """
    # Load the pre-trained English model
    nlp = spacy.load("en_core_web_sm")

    paragraph = "Dr. Eva Smith works for the W.H.O. in Geneva. She is a leading expert. What is her specialty?"

    # Process the text with spaCy   
    doc = nlp(text)

    # Iterate over sentences
    sentences = [sent.text for sent in doc.sents]

    return sentences

def filter(text, min_length=50):
    """
    Backward-compatible filter that accepts a string, removes boilerplate/procedural lines,
    and returns the cleaned string. Prefer using filter_segments for lists of segments.
    """

    # Rule for procedural content (starts with a common command verb)
    procedural_pattern = r'^\s*(First|Next|Then|Click|Select|Enter|Type)\s*,\s*.*'
    # Rule for common boilerplate
    boilerplate_pattern = r'Copyright|All rights reserved|Privacy Policy'

    lines = text.split('\n')
    filtered_lines = []
    for line in lines:
        if not re.search(procedural_pattern, line, re.IGNORECASE) and not re.search(boilerplate_pattern, line, re.IGNORECASE):
            filtered_lines.append(line)

    return '\n'.join(filtered_lines).strip()


def filter_segments(segments, min_length=50):
    """
    Filters out text segments shorter than min_length characters.
    """
    return [seg for seg in segments if isinstance(seg, str) and len(seg.strip()) >= min_length]


def segment_into_chunks(text, target_words=220, overlap_ratio=0.2):
    """
    Segments text into chunks of approximately target_words, preserving sentence boundaries.
    Overlaps consecutive chunks by overlap_ratio of the chunk size (by sentence count).

    Fallbacks to a regex-based sentence splitter if spaCy model is unavailable.
    """
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    except Exception:
        # Regex-based sentence splitting fallback
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    chunks = []
    idx = 0
    num_sentences = len(sentences)
    if num_sentences == 0:
        return []

    while idx < num_sentences:
        current_chunk = []
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