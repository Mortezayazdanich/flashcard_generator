from ai import generate_flashcards, generate_summary
from storage import clean_dataset, save_flashcards, load_flashcards
from textProcessing import text_normalization, segment_into_chunks, filter_segments, filter


def main():
    # Get input text
    # text = input("Enter text to generate flashcards: ")
    text = """
    Photosynthesis is a process used by plants, algae, and certain bacteria to convert light energy into 
    chemical energy, through a process that converts carbon dioxide and water into sugars (glucose) and oxygen. 
    This process is crucial for life on Earth as it produces most of the oxygen in the atmosphere and supplies 
    the chemical energy necessary for most living organisms. The process occurs in chloroplasts, which are 
    small organelles found in the cells of plants. Chlorophyll, the green pigment in chloroplasts, is responsible 
    for absorbing the light energy that drives photosynthesis.
    """

    # Process text efficiently using pipeline-aligned approach
    normalized_text = text_normalization(text)
    cleaned_text = filter(normalized_text)
    chunks = segment_into_chunks(cleaned_text, target_words=220, overlap_ratio=0.2)
    filtered_segments = filter_segments(chunks, min_length=50)
    
    print(f"Processing {len(filtered_segments)} text segments...")
    
    # Generate summary from cleaned text
    generate_summary(cleaned_text)
    
    # Generate flashcards for each segment
    all_flashcards = []
    for i, segment in enumerate(filtered_segments, 1):
        print(f"\n--- Processing segment {i}/{len(filtered_segments)} ---")
        flashcards = generate_flashcards(segment, num_questions=3)
        all_flashcards.extend(flashcards)
    
    # Save all flashcards at once
    if all_flashcards:
        save_flashcards(all_flashcards)
        clean_dataset()
        
        # Display results
        cards = load_flashcards()
        print(f"\n=== Generated {len(cards)} Total Flashcards ===")
        for i, card in enumerate(cards, 1):
            print(f"{i}. Q: {card['Question']}")
            print(f"   A: {card['Answer']}\n")
    else:
        print("No flashcards generated.")


if __name__ == "__main__":
    main()