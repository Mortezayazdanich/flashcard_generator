import fitz  # PyMuPDF
import os
import logging
import mimetypes
from pathlib import Path
from typing import List, Union, Optional
from logging import getLogger
from model_manager import get_ocr_reader
from patterns import FilePatterns
from config import get_config
from exceptions import InputProcessingError, FileTypeError, OCRError


def detect_file_type(file_path: Union[str, Path]) -> str:
    """Auto-detect file type based on extension and MIME type."""
    file_path_str = str(file_path)
    if not os.path.exists(file_path_str):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Use optimized patterns for file type detection
    if FilePatterns.is_pdf_file(file_path_str):
        return 'pdf'
    elif FilePatterns.is_image_file(file_path_str):
        return 'image'
    elif FilePatterns.is_text_file(file_path_str):
        return 'text'
    
    # Fallback to MIME type detection
    mime_type, _ = mimetypes.guess_type(file_path_str)
    if mime_type:
        if 'pdf' in mime_type:
            return 'pdf'
        elif mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('text/'):
            return 'text'
    
    return 'unknown'


def extract_text_from_pdf(pdf_path: Union[str, Path]) -> str:
    """Extract selectable text from a PDF efficiently."""
    pdf_path_str = str(pdf_path)
    if not os.path.exists(pdf_path_str):
        raise InputProcessingError(pdf_path_str, "PDF file not found")
    
    try:
        with fitz.open(pdf_path_str) as doc:
            text_parts = [page.get_text() for page in doc] # type: ignore
            return "".join(text_parts)
    except Exception as e:
        raise InputProcessingError(pdf_path_str, "Failed to extract PDF text", e)


def extract_text_from_image(image_path: Union[str, Path], languages: Optional[List[str]] = None) -> str:
    """Extract text from image using optimized OCR."""
    config = get_config()
    if languages is None:
        languages = config.OCR_DEFAULT_LANGUAGES
        
    image_path_str = str(image_path)
    if not os.path.exists(image_path_str):
        raise InputProcessingError(image_path_str, "Image file not found")
    
    try:
        # Use ModelManager for OCR reader
        reader = get_ocr_reader(languages)
        results = reader.readtext(image_path_str)
        
        # Extract text using config threshold
        text_parts = []
        for (bbox, text, confidence) in results:
            if float(confidence) > config.OCR_CONFIDENCE_THRESHOLD:
                text_parts.append(text)
        
        return " ".join(text_parts)
    except Exception as e:
        raise OCRError(image_path_str, languages, e)


def read_text_file(file_path: Union[str, Path]) -> str:
    """Read content from a text file with encoding fallback."""
    file_path_str = str(file_path)
    if not os.path.exists(file_path_str):
        raise InputProcessingError(file_path_str, "Text file not found")
    
    encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']
    for encoding in encodings:
        try:
            with open(file_path_str, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise InputProcessingError(file_path_str, f"Failed to read with encoding {encoding}", e)
    
    raise InputProcessingError(file_path_str, "Unable to read file with any supported encoding")


class PDFTextExtractor:
    """Advanced PDF text extractor with OCR fallback using optimized ModelManager."""
    
    def __init__(self, languages: Optional[List[str]] = None):
        config = get_config()
        self.languages = languages or config.OCR_DEFAULT_LANGUAGES
        self.logger = getLogger(__name__)
        self.config = config
    
    def extract_text(self, pdf_path: Union[str, Path], use_ocr_fallback: bool = True) -> str:
        """Extract text from PDF with OCR fallback for scanned documents."""
        pdf_path_str = str(pdf_path)
        if not os.path.exists(pdf_path_str):
            raise InputProcessingError(pdf_path_str, "PDF file not found")
        
        try:
            # First, try extracting selectable text
            text = extract_text_from_pdf(pdf_path_str)
            
            # Check if text extraction was successful
            if text.strip() and len(text.strip()) > 50:
                self.logger.info("Successfully extracted selectable text from PDF")
                return text
            
            # If text is minimal or empty, use OCR fallback
            if use_ocr_fallback:
                self.logger.info("Minimal text found, using OCR fallback")
                return self._extract_with_ocr(pdf_path_str)
            else:
                return text
                
        except Exception as e:
            if use_ocr_fallback:
                self.logger.warning(f"Text extraction failed, trying OCR: {e}")
                try:
                    return self._extract_with_ocr(pdf_path_str)
                except Exception as ocr_e:
                    raise InputProcessingError(pdf_path_str, "Both text and OCR extraction failed", ocr_e)
            else:
                raise
    
    def _extract_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR by converting PDF pages to images."""
        try:
            text_parts: List[str] = []
            
            # Use ModelManager for OCR reader
            ocr_reader = get_ocr_reader(self.languages)
            
            with fitz.open(pdf_path) as doc:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    
                    # Convert page to image
                    pix = page.get_pixmap() # type: ignore
                    img_data = pix.tobytes("png")
                    
                    # Use OCR on the image
                    results = ocr_reader.readtext(img_data)
                    
                    # Extract text using config threshold
                    page_text: List[str] = []
                    for (bbox, text, confidence) in results:
                        if float(confidence) > self.config.OCR_CONFIDENCE_THRESHOLD:
                            page_text.append(text)
                    
                    if page_text:
                        text_parts.append(" ".join(page_text))
            
            return "\n".join(text_parts)
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            raise OCRError(pdf_path, self.languages, e)


def process_input(input_source: str, languages: Optional[List[str]] = None) -> str:
    """Unified interface for processing different input types.
    
    Args:
        input_source: Can be a file path or raw text
        languages: Languages for OCR (uses config default if None)
    
    Returns:
        Extracted text ready for the flashcard generation pipeline
    """
    config = get_config()
    if languages is None:
        languages = config.OCR_DEFAULT_LANGUAGES
        
    logger = getLogger(__name__)
    
    # Check if input_source is a file path
    if os.path.exists(input_source):
        file_type = detect_file_type(input_source)
        
        logger.info(f"Processing file: {input_source} (type: {file_type})")
        
        if file_type == 'pdf':
            # Use advanced PDF extractor with OCR fallback
            extractor = PDFTextExtractor(languages=languages)
            return extractor.extract_text(input_source)
        
        elif file_type == 'image':
            # Use OCR for image files
            return extract_text_from_image(input_source, languages=languages)
        
        elif file_type == 'text':
            # Read text file directly
            return read_text_file(input_source)
        
        else:
            raise FileTypeError(input_source, file_type)
    
    else:
        # Treat as raw text input
        logger.info("Processing raw text input")
        return input_source
