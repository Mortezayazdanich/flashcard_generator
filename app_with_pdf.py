from ai import generate_flashcards, generate_summary
from storage import clean_dataset, save_flashcards, load_flashcards
from textProcessing import text_normalization, segment_into_chunks, filter_segments, filter
from pdf_ocr_processor import PDFTextExtractor
import os
import sys

def get_input_source():
    """Get input from user - either direct text or file path."""
    print("\n=== Flashcard Generator ===")
    print("Choose input method:")
    print("1. Enter text directly")
    print("2. Upload PDF file")
    print("3. Upload image file (OCR)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        text = input("\nEnter text to generate flashcards: ")
        return text, "text"
    
    elif choice == "2":
        file_path = input("\nEnter PDF file path: ").strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return file_path, "pdf"
    
    elif choice == "3":
        file_path = input("\nEnter image file path: ").strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return file_path, "image"
    
    else:
        raise ValueError("Invalid choice. Please select 1, 2, or 3.")

def process_input(input_source, input_type):
    """Process different input types and return raw text."""
    
    if input_type == "text":
        return input_source
    
    elif input_type == "pdf":
        print(f"\n📄 Processing PDF file: {input_source}")
        extractor = PDFTextExtractor(confidence_threshold=0.6)
        
        try:
            # Use hybrid approach for best results
            text, method = extractor.extract_text_hybrid(input_source)
            print(f"✅ Text extracted using: {method}")
            print(f"📊 Extracted {len(text)} characters")
            
            if len(text) < 100:
                print("⚠️  Warning: Very little text extracted. Check if PDF is readable.")
                return text
            
            return text
            
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            raise
    
    elif input_type == "image":
        print(f"\n🖼️  Processing image file: {input_source}")
        extractor = PDFTextExtractor(confidence_threshold=0.6)
        
        try:
            # For images, we need to create a temporary PDF or handle directly
            # For now, let's assume it's handled by the OCR function
            # You might need to modify the extractor to handle single images
            print("⚠️  Direct image processing not yet implemented.")
            print("Please convert your image to PDF first, or add image handling to the extractor.")
            raise NotImplementedError("Direct image processing not implemented yet")
            
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            raise
    
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

def main():
    try:
        # Phase 0: Input Processing
        input_source, input_type = get_input_source()
        print(f"\n🔄 Processing {input_type} input...")
        
        raw_text = process_input(input_source, input_type)
        
        if not raw_text or len(raw_text.strip()) < 50:
            print("❌ Insufficient text extracted. Please check your input.")
            return
        
        print(f"\n✅ Successfully extracted text. Preview:")
        print("-" * 50)
        print(raw_text[:300] + "..." if len(raw_text) > 300 else raw_text)
        print("-" * 50)
        
        # Existing pipeline (unchanged)
        print("\n🔄 Processing text through pipeline...")
        normalized_text = text_normalization(raw_text)
        cleaned_text = filter(normalized_text)
        chunks = segment_into_chunks(cleaned_text, target_words=220, overlap_ratio=0.2)
        filtered_segments = filter_segments(chunks, min_length=50)
        
        print(f"📊 Processing {len(filtered_segments)} text segments...")
        
        # Generate summary from cleaned text
        generate_summary(cleaned_text)
        
        # Generate flashcards for each segment
        all_flashcards = []
        for i, segment in enumerate(filtered_segments, 1):
            print(f"\n--- Processing segment {i}/{len(filtered_segments)} ---")
            try:
                flashcards = generate_flashcards(segment, num_questions=3)
                all_flashcards.extend(flashcards)
                print(f"✅ Generated {len(flashcards)} flashcards from this segment")
            except Exception as e:
                print(f"⚠️  Error generating flashcards for segment {i}: {e}")
                continue
        
        # Save all flashcards at once
        if all_flashcards:
            save_flashcards(all_flashcards)
            clean_dataset()
            
            # Display results
            cards = load_flashcards()
            print(f"\n🎉 === Generated {len(cards)} Total Flashcards ===")
            for i, card in enumerate(cards, 1):
                print(f"{i}. Q: {card['Question']}")
                print(f"   A: {card['Answer']}\n")
        else:
            print("❌ No flashcards generated. Please check your input text quality.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
    except FileNotFoundError as e:
        print(f"\n❌ File error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()