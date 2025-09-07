#!/usr/bin/env python3
"""
Integration test for Phase 1 PDF & OCR implementation
"""

from flashcard_generator.processing.input_processor import process_input
from flashcard_generator.core.text_processor import text_normalization, segment_into_chunks, filter_segments, filter

def test_integration():
    """Test the complete integration from file input to text processing"""
    
    print("🧪 Testing Phase 1 Integration")
    
    # Test with our sample document
    file_path = "./examples/sample_document.txt"
    
    try:
        # Phase 0: Input Processing  
        print(f"\n📄 Processing file: {file_path}")
        raw_text = process_input(file_path)
        print(f"✅ Successfully extracted {len(raw_text)} characters")
        
        # Phase 1.1: Text Cleaning & Normalization
        print("\n🧹 Text normalization and cleaning...")
        normalized_text = text_normalization(raw_text)
        cleaned_text = filter(normalized_text)
        print(f"✅ Cleaned text: {len(cleaned_text)} characters")
        
        # Phase 1.2: Segmentation
        print("\n✂️ Segmenting text into chunks...")
        chunks = segment_into_chunks(cleaned_text, target_words=220, overlap_ratio=0.2)
        filtered_segments = filter_segments(chunks, min_length=50)
        print(f"✅ Created {len(filtered_segments)} text segments")
        
        # Show sample segments
        print("\n📋 Sample segments:")
        for i, segment in enumerate(filtered_segments[:2], 1):
            print(f"{i}. {segment[:100]}...")
        
        print(f"\n🎯 Ready for flashcard generation with {len(filtered_segments)} segments")
        print("✅ Phase 1 integration test successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n🚀 Phase 1 is ready for flashcard generation!")
    else:
        print("\n💥 Phase 1 needs fixes before proceeding")
