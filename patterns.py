"""
Pre-compiled Regex Patterns for Flashcard Generator

Centralizes and pre-compiles all regex patterns used throughout the application
for improved performance and maintainability.
"""

import re
from typing import Pattern


class TextPatterns:
    """Pre-compiled regex patterns for text processing."""
    
    # Text cleaning patterns
    HTML_TAGS: Pattern[str] = re.compile(r'<.*?>')
    WHITESPACE: Pattern[str] = re.compile(r'\s+')
    NON_WORD_CHARS: Pattern[str] = re.compile(r'[^\w\s.,!?-]')
    
    # Content filtering patterns
    PROCEDURAL: Pattern[str] = re.compile(
        r'^\s*(First|Next|Then|Click|Select|Enter|Type)\s*,\s*.*', 
        re.IGNORECASE
    )
    BOILERPLATE: Pattern[str] = re.compile(
        r'Copyright|All rights reserved|Privacy Policy', 
        re.IGNORECASE
    )
    PAGE_NUMBER: Pattern[str] = re.compile(r'^Page \d+$')
    STANDALONE_NUMBER: Pattern[str] = re.compile(r'^\d+$')
    
    # Sentence segmentation patterns
    SENTENCE_BOUNDARY: Pattern[str] = re.compile(r'(?<=[.!?])\s+')
    
    # AI generation patterns
    JSON_ARRAY: Pattern[str] = re.compile(r'\[.*?\]', re.DOTALL)
    GENERIC_QUESTION: Pattern[str] = re.compile(r'^question\s*\d+\?$', re.IGNORECASE)
    
    # File extension patterns
    PDF_EXTENSION: Pattern[str] = re.compile(r'\.pdf$', re.IGNORECASE)
    IMAGE_EXTENSIONS: Pattern[str] = re.compile(
        r'\.(jpg|jpeg|png|bmp|tiff|webp)$', 
        re.IGNORECASE
    )
    TEXT_EXTENSIONS: Pattern[str] = re.compile(r'\.(txt|md)$', re.IGNORECASE)


class TextCleaner:
    """Optimized text cleaning using pre-compiled patterns."""
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        return TextPatterns.HTML_TAGS.sub('', text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text."""
        return TextPatterns.WHITESPACE.sub(' ', text).strip()
    
    @staticmethod
    def remove_non_word_chars(text: str) -> str:
        """Remove non-word characters except basic punctuation."""
        return TextPatterns.NON_WORD_CHARS.sub('', text)
    
    @staticmethod
    def is_procedural_content(text: str) -> bool:
        """Check if text contains procedural content."""
        return bool(TextPatterns.PROCEDURAL.search(text))
    
    @staticmethod
    def is_boilerplate_content(text: str) -> bool:
        """Check if text contains boilerplate content."""
        return bool(TextPatterns.BOILERPLATE.search(text))
    
    @staticmethod
    def is_page_number(text: str) -> bool:
        """Check if text is a page number."""
        return bool(TextPatterns.PAGE_NUMBER.match(text.strip()))
    
    @staticmethod
    def is_standalone_number(text: str) -> bool:
        """Check if text is just a standalone number."""
        return bool(TextPatterns.STANDALONE_NUMBER.match(text.strip()))
    
    @staticmethod
    def split_sentences(text: str) -> list[str]:
        """Split text into sentences using regex."""
        return [s.strip() for s in TextPatterns.SENTENCE_BOUNDARY.split(text) if s.strip()]


class AIPatterns:
    """Patterns for AI generation processing."""
    
    @staticmethod
    def extract_json_array(text: str) -> list:
        """Extract JSON array from AI-generated text."""
        import json
        
        # Try direct JSON parsing first
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
        
        # Fallback to regex extraction
        match = TextPatterns.JSON_ARRAY.search(text)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
        
        return []
    
    @staticmethod
    def is_generic_question(question: str) -> bool:
        """Check if question is generic/template-like."""
        return bool(TextPatterns.GENERIC_QUESTION.match(question))


class FilePatterns:
    """Patterns for file type detection."""
    
    @staticmethod
    def is_pdf_file(filename: str) -> bool:
        """Check if filename indicates a PDF file."""
        return bool(TextPatterns.PDF_EXTENSION.search(filename))
    
    @staticmethod
    def is_image_file(filename: str) -> bool:
        """Check if filename indicates an image file."""
        return bool(TextPatterns.IMAGE_EXTENSIONS.search(filename))
    
    @staticmethod
    def is_text_file(filename: str) -> bool:
        """Check if filename indicates a text file."""
        return bool(TextPatterns.TEXT_EXTENSIONS.search(filename))
