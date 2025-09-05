from ai import generate_flashcards, generate_summary
from storage import clean_dataset, save_flashcards, load_flashcards
from textProcessing import text_normalization, segment_into_chunks, filter_segments, filter
from input_processor import process_input
import os


def get_input():
    """Get input from user - either file path or manual text entry."""
    print("\n=== Flashcard Generator - Phase 0: Input Processing ===")
    print("Choose your input method:")
    print("1. Upload a file (PDF, image, or text file)")
    print("2. Enter text manually")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == '1':
        file_path = input("Enter the file path: ").strip()
        if not file_path:
            print("No file path provided. Switching to manual text entry.")
            return input("Enter text to generate flashcards: ") # Return the manual text entry
        
        # Expand user path if needed
        file_path = os.path.expanduser(file_path)
        
        try:
            print(f"\nProcessing file: {file_path}")
            return process_input(file_path)
        except Exception as e:
            print(f"Error processing file: {e}")
            print("Switching to manual text entry.")
            return input("Enter text to generate flashcards: ") # Return the manual text entry
    
    elif choice == '2':
        return input("\nEnter text to generate flashcards: ")
    
    else:
        print("Invalid choice. Defaulting to manual text entry.")
        return input("Enter text to generate flashcards: ") # Return the manual text entry


def main():
    """Main function with enhanced input processing."""
    
    # Phase 0: Input Processing (NEW)
    try:
        raw_text = get_input() # Get the input from the user
        
        if not raw_text or not raw_text.strip():
            print("No text provided. Exiting.")
            return # Exit the function if no text was provided  
            
        print(f"\n✅ Successfully extracted {len(raw_text)} characters of text")
        print("\n=== Proceeding to flashcard generation pipeline ===")
        
    except Exception as e:
        print(f"Error during input processing: {e}")
        return # Exit the function if there was an error during the input processing
    
    # Phase 1.1: Text Cleaning & Normalization (existing pipeline)
    try:
        normalized_text = text_normalization(raw_text)
        cleaned_text = filter(normalized_text)
        chunks = segment_into_chunks(cleaned_text, target_words=220, overlap_ratio=0.2)
        filtered_segments = filter_segments(chunks, min_length=50)
        
        print(f"Processing {len(filtered_segments)} text segments...")
        
        # Generate summary from cleaned text
        generate_summary(cleaned_text)
        
        # Generate flashcards for each segment
        all_flashcards = []
        for i, segment in enumerate(filtered_segments, 1): # Starting from 1 to match the enumerate syntax for the print statements
            print(f"\n--- Processing segment {i}/{len(filtered_segments)} ---")
            flashcards = generate_flashcards(segment, num_questions=3)
            all_flashcards.extend(flashcards) # Extend the list with the new flashcards list
        
        # Save all flashcards at once
        if all_flashcards:
            save_flashcards(all_flashcards) # Save the all_flashcards list to the flashcards.json file
            clean_dataset()
            
            # Display results
            cards = load_flashcards() # Load the flashcards.json file into a list
            print(f"\n=== Generated {len(cards)} Total Flashcards ===")
            for i, card in enumerate(cards, 1):
                print(f"{i}. Q: {card['Question']}") # Print the question
                print(f"   A: {card['Answer']}\n") # Print the answer
        else:
            print("No flashcards generated.") # Print a message if no flashcards were generated
            
    except Exception as e:
        print(f"Error during flashcard generation: {e}") # Print an error message if there was an error during the flashcard generation


if __name__ == "__main__":
    main() # Run the main function