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


# Global spaCy model to avoid repeated loading
_nlp = None

def get_nlp():
    """Get spaCy model, loading it once if needed."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

def segment_text(text, max_length=2000):
    """
    Segments the input text into chunks of approximately max_length characters,
    ensuring that segments end at sentence boundaries.
    """
    nlp = get_nlp()
    doc = nlp(text)
    
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    # Group sentences into chunks under max_length
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks if chunks else [text]

def filter_segments(segments, min_length=50):
    """
    Filters out segments that are shorter than min_length characters
    or contain procedural/boilerplate content.
    """
    # Rule for procedural content (starts with a common command verb)
    procedural_pattern = r'^\s*(First|Next|Then|Click|Select|Enter|Type)\s*,\s*.*'
    # Rule for common boilerplate
    boilerplate_pattern = r'Copyright|All rights reserved|Privacy Policy'
    
    filtered = []
    for segment in segments:
        if (len(segment) >= min_length and 
            not re.search(procedural_pattern, segment, re.IGNORECASE) and 
            not re.search(boilerplate_pattern, segment, re.IGNORECASE)):
            filtered.append(segment)
    
    return filtered