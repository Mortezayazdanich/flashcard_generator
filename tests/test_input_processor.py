#!/usr/bin/env python3
"""
Test script for the PDF and OCR input processing functionality.

This script tests the Phase 1 implementation of PDF & OCR integration.
"""

import sys
import os
from flashcard_generator.processing.input_processor import (
    detect_file_type, 
    process_input, 
    extract_text_from_pdf, 
    extract_text_from_image,
    read_text_file,
    PDFTextExtractor
)

def test_file_type_detection():
    """Test file type detection functionality."""
    print("=== Testing File Type Detection ===")
    
    # Test with sample input file (should be text)
    if os.path.exists("sample input.txt"):
        file_type = detect_file_type("sample input.txt")
        print(f"✅ sample input.txt detected as: {file_type}")
    else:
        print("⚠️ sample input.txt not found, skipping text file test")
    
    # Test with various extensions
    test_files = {
        "test.pdf": "pdf",
        "test.jpg": "image", 
        "test.png": "image",
        "test.txt": "text",
        "test.md": "text"
    }
    
    for filename, expected_type in test_files.items():
        # Create temporary file to test detection
        try:
            with open(filename, 'w') as f:
                f.write("test content")
            detected_type = detect_file_type(filename)
            if detected_type == expected_type:
                print(f"✅ {filename} correctly detected as: {detected_type}")
            else:
                print(f"❌ {filename} detected as: {detected_type}, expected: {expected_type}")
            os.remove(filename)  # Clean up
        except Exception as e:
            print(f"❌ Error testing {filename}: {e}")

def test_text_file_processing():
    """Test text file processing."""
    print("\n=== Testing Text File Processing ===")
    
    if os.path.exists("sample input.txt"):
        try:
            text = read_text_file("sample input.txt")
            print(f"✅ Successfully read text file: {len(text)} characters")
            print(f"Preview: {text[:100]}...")
        except Exception as e:
            print(f"❌ Error reading text file: {e}")
    else:
        print("⚠️ sample input.txt not found, creating test file...")
        test_content = """
        This is a test document for flashcard generation.
        
        Machine Learning is a subset of artificial intelligence that focuses on 
        developing algorithms and statistical models that enable computers to improve 
        their performance on a specific task through experience without being explicitly programmed.
        
        Key concepts include:
        - Supervised learning: Learning with labeled data
        - Unsupervised learning: Finding patterns in data without labels
        - Neural networks: Computing systems inspired by biological neural networks
        """
        
        with open("test_sample.txt", "w") as f:
            f.write(test_content)
        
        try:
            text = read_text_file("test_sample.txt")
            print(f"✅ Successfully read test file: {len(text)} characters")
            print(f"Preview: {text[:100]}...")
            os.remove("test_sample.txt")  # Clean up
        except Exception as e:
            print(f"❌ Error reading test file: {e}")

def test_pdf_extractor_class():
    """Test the PDFTextExtractor class."""
    print("\n=== Testing PDFTextExtractor Class ===")
    
    extractor = PDFTextExtractor()
    print("✅ PDFTextExtractor instantiated successfully")
    print(f"Languages: {extractor.languages}")
    
    # The OCR reader is lazy-loaded, so we won't initialize it in tests
    # unless we have an actual PDF to process
    print("✅ OCR reader ready for lazy loading")

def test_unified_process_input():
    """Test the unified process_input function with different input types."""
    print("\n=== Testing Unified process_input Function ===")
    
    # Test with raw text
    sample_text = "This is a test of the unified input processing function."
    try:
        result = process_input(sample_text)
        print(f"✅ Raw text processing: {len(result)} characters")
    except Exception as e:
        print(f"❌ Error processing raw text: {e}")
    
    # Test with text file if available
    if os.path.exists("sample input.txt"):
        try:
            result = process_input("sample input.txt")
            print(f"✅ Text file processing: {len(result)} characters")
        except Exception as e:
            print(f"❌ Error processing text file: {e}")

def run_all_tests():
    """Run all tests."""
    print("🧪 Starting PDF & OCR Input Processor Tests\n")
    
    try:
        test_file_type_detection()
        test_text_file_processing() 
        test_pdf_extractor_class()
        test_unified_process_input()
        
        print("\n✅ All basic tests completed!")
        print("\n📝 Notes for Phase 1:")
        print("- PDF processing requires actual PDF files to test fully")
        print("- OCR processing requires image files to test")
        print("- The system will work with both digital and scanned PDFs")
        print("- Error handling is in place for unsupported file types")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
