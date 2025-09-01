import fitz  # PyMuPDF
import easyocr
import io
import logging
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional, Tuple
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFTextExtractor:
    """Enhanced PDF text extractor with OCR capabilities."""
    
    def __init__(self, languages=['en'], confidence_threshold=0.5):
        """
        Initialize the PDF text extractor.
        
        Args:
            languages: List of language codes for OCR (e.g., ['en', 'fr'])
            confidence_threshold: Minimum confidence for OCR text (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self._ocr_reader = None
        self.languages = languages
        
    @property
    def ocr_reader(self):
        """Lazy initialization of EasyOCR reader to avoid loading on import."""
        if self._ocr_reader is None:
            logger.info(f"Initializing EasyOCR reader for languages: {self.languages}")
            try:
                self._ocr_reader = easyocr.Reader(self.languages, gpu=True)
                logger.info("EasyOCR reader initialized successfully")
            except Exception as e:
                logger.warning(f"GPU initialization failed, falling back to CPU: {e}")
                self._ocr_reader = easyocr.Reader(self.languages, gpu=False)
        return self._ocr_reader

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts selectable text from a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF cannot be opened or processed
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    logger.warning("PDF is encrypted, attempting to decrypt with empty password")
                    doc.authenticate("")
                
                text_parts = []
                for page_num, page in enumerate(doc):
                    try:
                        page_text = page.get_text().strip()
                        if page_text:
                            text_parts.append(page_text)
                        else:
                            logger.info(f"Page {page_num + 1} has no selectable text, might need OCR")
                    except Exception as e:
                        logger.error(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
                
                full_text = "\n\n".join(text_parts)
                logger.info(f"Extracted {len(full_text)} characters from {len(text_parts)} pages")
                return full_text
                
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            raise

    def enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Enhance image quality for better OCR results.
        
        Args:
            image: PIL Image object
            
        Returns:
            Enhanced PIL Image object
        """
        try:
            # Convert to grayscale if not already
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
        except Exception as e:
            logger.warning(f"Image enhancement failed, using original: {e}")
            return image

    def extract_text_with_ocr(self, pdf_path: str, enhance_images: bool = True) -> str:
        """
        Extracts text from a PDF using OCR, suitable for scanned documents.
        
        Args:
            pdf_path: Path to the PDF file
            enhance_images: Whether to enhance images before OCR
            
        Returns:
            Extracted text as string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF cannot be processed
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            logger.info(f"Extracting text from PDF using OCR: {pdf_path}")
            full_text = ''
            total_confidence = 0
            total_words = 0
            
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    logger.warning("PDF is encrypted, attempting to decrypt with empty password")
                    doc.authenticate("")
                
                for page_num in range(len(doc)):
                    try:
                        page = doc.load_page(page_num)
                        
                        # Render page to high-resolution image
                        pix = page.get_pixmap(dpi=300)
                        
                        # Convert pixmap to PIL Image
                        img_bytes = pix.tobytes("png")
                        image = Image.open(io.BytesIO(img_bytes))
                        
                        # Enhance image if requested
                        if enhance_images:
                            image = self.enhance_image_for_ocr(image)
                        
                        # Convert back to bytes for EasyOCR
                        img_buffer = io.BytesIO()
                        image.save(img_buffer, format='PNG')
                        img_bytes = img_buffer.getvalue()
                        
                        # Perform OCR
                        results = self.ocr_reader.readtext(img_bytes)
                        
                        # Filter by confidence and extract text
                        page_texts = []
                        for bbox, text, confidence in results:
                            if confidence >= self.confidence_threshold:
                                page_texts.append(text)
                                total_confidence += confidence
                                total_words += 1
                            else:
                                logger.debug(f"Skipping low-confidence text: '{text}' (confidence: {confidence:.2f})")
                        
                        page_text = " ".join(page_texts)
                        if page_text.strip():
                            full_text += page_text + '\n\n'
                        
                        logger.info(f"Page {page_num + 1}: Extracted {len(page_texts)} text segments")
                        
                        # Clean up
                        pix = None
                        image.close()
                        img_buffer.close()
                        
                    except Exception as e:
                        logger.error(f"Error processing page {page_num + 1}: {e}")
                        continue
            
            # Log overall quality metrics
            avg_confidence = total_confidence / total_words if total_words > 0 else 0
            logger.info(f"OCR completed. Average confidence: {avg_confidence:.2f}, Total words: {total_words}")
            
            return full_text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text with OCR from PDF {pdf_path}: {e}")
            raise

    def extract_text_hybrid(self, pdf_path: str) -> Tuple[str, str]:
        """
        Attempts text extraction first, falls back to OCR if needed.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted_text, method_used)
            method_used is either 'text_extraction' or 'ocr'
        """
        try:
            # First, try regular text extraction
            text = self.extract_text_from_pdf(pdf_path)
            
            # Check if we got meaningful text (more than just whitespace and page numbers)
            meaningful_text = ' '.join([line.strip() for line in text.split('\n') 
                                     if line.strip() and not line.strip().isdigit()])
            
            if len(meaningful_text) > 100:  # Threshold for meaningful content
                logger.info("Using text extraction method")
                return text, 'text_extraction'
            else:
                logger.info("Text extraction yielded minimal content, falling back to OCR")
                ocr_text = self.extract_text_with_ocr(pdf_path)
                return ocr_text, 'ocr'
                
        except Exception as e:
            logger.warning(f"Text extraction failed, trying OCR: {e}")
            try:
                ocr_text = self.extract_text_with_ocr(pdf_path)
                return ocr_text, 'ocr'
            except Exception as ocr_error:
                logger.error(f"Both text extraction and OCR failed: {ocr_error}")
                raise

# Convenience functions for backward compatibility
def extract_text_from_pdf(pdf_path: str) -> str:
    """Convenience function for basic PDF text extraction."""
    extractor = PDFTextExtractor()
    return extractor.extract_text_from_pdf(pdf_path)

def extract_text_with_ocr(pdf_path: str) -> str:
    """Convenience function for OCR-based text extraction."""
    extractor = PDFTextExtractor()
    return extractor.extract_text_with_ocr(pdf_path)

# Example usage
if __name__ == "__main__":
    # Example usage
    pdf_file = "sample.pdf"  # Replace with your PDF path
    
    extractor = PDFTextExtractor(confidence_threshold=0.6)
    
    try:
        # Try hybrid approach (automatic fallback)
        text, method = extractor.extract_text_hybrid(pdf_file)
        print(f"Extraction method used: {method}")
        print(f"Extracted text length: {len(text)} characters")
        print("\nFirst 500 characters:")
        print(text[:500])
        
    except FileNotFoundError:
        print(f"PDF file '{pdf_file}' not found. Please update the path.")
    except Exception as e:
        print(f"Error processing PDF: {e}")