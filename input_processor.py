import fitz  # PyMuPDF
import easyocr
import io, os, logging
from logging import getLogger
from PIL import Image
import mimetypes
from pathlib import Path


def detect_file_type(file_path):
    """Auto-detect file type based on extension and MIME type."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    file_ext = Path(file_path).suffix.lower()
    
    # Get MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Determine file type
    if file_ext == '.pdf' or (mime_type and 'pdf' in mime_type):
        return 'pdf'
    elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'] or (mime_type and mime_type.startswith('image/')):
        return 'image'
    elif file_ext in ['.txt', '.md'] or (mime_type and mime_type.startswith('text/')):
        return 'text'
    else:
        return 'unknown'


def extract_text_from_pdf(pdf_path):
    """Extracts selectable text from a PDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    try:
        with fitz.open(pdf_path) as doc:
            text_parts = [page.get_text("text") for page in doc]  # type: ignore
            return "".join(text_parts)
    except Exception as e:
        logger = getLogger(__name__)
        logger.error(f"Failed to process PDF: {e}")
        raise


def extract_text_from_image(image_path, languages=['en']):
    """Extract text from image using OCR."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        reader = easyocr.Reader(languages)
        results = reader.readtext(image_path)
        
        # Extract text from OCR results
        text_parts = []
        for (bbox, text, confidence) in results:
            if float(confidence) > 0.5:  # Filter low-confidence results
                text_parts.append(text)
        
        return " ".join(text_parts)
    except Exception as e:
        logger = getLogger(__name__)
        logger.error(f"Failed to process image with OCR: {e}")
        raise


def read_text_file(file_path):
    """Read content from a text file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()
    except Exception as e:
        logger = getLogger(__name__)
        logger.error(f"Failed to read text file: {e}")
        raise


class PDFTextExtractor:
    """Advanced PDF text extractor with OCR fallback capabilities."""
    
    def __init__(self, languages=['en']):
        self.languages = languages
        self._ocr_reader = None
        self.logger = getLogger(__name__)
    
    @property
    def ocr_reader(self):
        """Lazy loading of OCR reader to avoid unnecessary initialization."""
        if self._ocr_reader is None:
            self._ocr_reader = easyocr.Reader(self.languages)
        return self._ocr_reader
    
    def extract_text(self, pdf_path, use_ocr_fallback=True):
        """Extract text from PDF with OCR fallback for scanned documents."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # First, try extracting selectable text
            text = extract_text_from_pdf(pdf_path)
            
            # Check if text extraction was successful
            if text.strip() and len(text.strip()) > 50:
                self.logger.info("Successfully extracted selectable text from PDF")
                return text
            
            # If text is minimal or empty, use OCR fallback
            if use_ocr_fallback:
                self.logger.info("Minimal text found, using OCR fallback")
                return self._extract_with_ocr(pdf_path)
            else:
                return text
                
        except Exception as e:
            if use_ocr_fallback:
                self.logger.warning(f"Text extraction failed, trying OCR: {e}")
                return self._extract_with_ocr(pdf_path)
            else:
                raise
    
    def _extract_with_ocr(self, pdf_path):
        """Extract text using OCR by converting PDF pages to images."""
        try:
            text_parts = []
            
            with fitz.open(pdf_path) as doc:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    
                    # Convert page to image
                    pix = page.get_pixmap()  # type: ignore
                    img_data = pix.tobytes("png")
                    
                    # Use OCR on the image
                    results = self.ocr_reader.readtext(img_data)
                    
                    # Extract text from OCR results
                    page_text = []
                    for (bbox, text, confidence) in results:
                        if float(confidence) > 0.5:  # Filter low-confidence results 
                            page_text.append(text)
                    
                    if page_text:
                        text_parts.append(" ".join(page_text))
            
            return "\n".join(text_parts)
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            raise


def process_input(input_source, languages=['en']):
    """Unified interface for processing different input types.
    
    Args:
        input_source (str): Can be a file path or raw text
        languages (list): Languages for OCR (default: ['en'])
    
    Returns:
        str: Extracted text ready for the flashcard generation pipeline
    """
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
            raise ValueError(f"Unsupported file type: {file_type}")
    
    else:
        # Treat as raw text input
        logger.info("Processing raw text input")
        return input_source
