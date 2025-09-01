from ai import generate_flashcards, generate_summary
from storage import clean_dataset, save_flashcards, load_flashcards
from textProcessing import text_normalization, segment_text, filter_segments


def main():
    # Get input text
    text = input("Enter text to generate flashcards: ")
    # text = """
    # Photosynthesis is a process used by plants, algae, and certain bacteria to convert light energy into 
    # chemical energy, through a process that converts carbon dioxide and water into sugars (glucose) and oxygen. 
    # This process is crucial for life on Earth as it produces most of the oxygen in the atmosphere and supplies 
    # the chemical energy necessary for most living organisms. The process occurs in chloroplasts, which are 
    # small organelles found in the cells of plants. Chlorophyll, the green pigment in chloroplasts, is responsible 
    # for absorbing the light energy that drives photosynthesis.
    # """

<<<<<<< HEAD
    text = """
    Photosynthesis is a process used by plants, algae, and certain bacteria to convert light energy into 
    chemical energy, through a process that converts carbon dioxide and water into sugars (glucose) and oxygen. 
    This process is crucial for life on Earth as it produces most of the oxygen in the atmosphere and supplies 
    the chemical energy necessary for most living organisms. The process occurs in chloroplasts, which are 
    small organelles found in the cells of plants. Chlorophyll, the green pigment in chloroplasts, is responsible 
    for absorbing the light energy that drives photosynthesis.
    """

    # Normalize and segment into semantic chunks (per Pipeline Phase 1 & 2)
    normalized = text_normalization(text)
    cleaned = filter(normalized)
    chunks = segment_into_chunks(cleaned, target_words=220, overlap_ratio=0.2)
    segments = filter_segments(chunks, min_length=50)

    generate_summary(cleaned)

    for seg in segments:
        flashcards = generate_flashcards(seg)
        save_flashcards(flashcards)

    clean_dataset()
    cards = load_flashcards()
    for card in cards:
        print(f"Q: {card['Question']}\nA: {card['Answer']}\n")
=======
    # Process text efficiently
    normalized_text = text_normalization(text)
    segments = segment_text(normalized_text, max_length=1500)
    filtered_segments = filter_segments(segments, min_length=100)
    
    print(f"Processing {len(filtered_segments)} text segments...")
>>>>>>> main
    
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