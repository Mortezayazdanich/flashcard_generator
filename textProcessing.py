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
    Filters out segments that are shorter than min_length characters.
    """

    # Rule for procedural content (starts with a common command verb)
    procedural_pattern = r'^\s*(First|Next|Then|Click|Select|Enter|Type)\s*,\s*.*'
    # Rule for common boilerplate
    boilerplate_pattern = r'Copyright|All rights reserved|Privacy Policy'

    lines = text.split('\n')
    filtered_lines = []
    for line in lines:
        # If the line doesn't match either pattern, keep it
        if not re.search(procedural_pattern, line, re.IGNORECASE) and not re.search(boilerplate_pattern, line, re.IGNORECASE):
            filtered_lines.append(line)

    filtered_text = '\n'.join(filtered_lines).strip()
    # Result: 'The main concept is photosynthesis, which is a critical process for plants.'
    return [seg for seg in text if len(seg) >= min_length]